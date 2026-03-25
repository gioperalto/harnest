#!/usr/bin/env python3
"""
Flock YAML validator for harnest.

Validates flock.yaml files without external dependencies (stdlib only, Python 3.9+).
Parses the simple YAML subset used by flock.yaml via line-by-line string parsing.

Usage: python3 validate-flock.py <flock-file> <nest-dir>
Exit codes: 0 = valid, 1 = invalid, 2 = usage error
"""

import os
import re
import sys
from collections import defaultdict

# ── ANSI helpers (match bin/harnest output style) ───────────────────────────

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


def info(msg):
    print(f"  {GREEN}\u2713{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}!{RESET} {msg}")


def error(msg):
    print(f"  {RED}\u2717{RESET} {msg}")


# ── Minimal YAML subset parser ──────────────────────────────────────────────
#
# Handles the flat structure of flock.yaml:
#   top_key:
#     alias:
#       key: value
#       key:
#         - item
#
# Does NOT handle: anchors, multi-line strings, flow mappings, etc.
# This is intentional — flock.yaml is a simple, predictable format.

def parse_flock_yaml(filepath):
    """Parse flock.yaml into a nested dict. Returns (data, error_msg).

    Uses an indent-stack approach: each entry is (indent_level, dict_at_that_level).
    The root dict is at indent -1. When a key opens a new mapping (empty value),
    we push the NEW dict at the key's indent + 1 (child level). When we encounter
    a line, we pop back to find the dict that owns this indent level.
    """
    data = {}

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None, f"File not found: {filepath}"
    except PermissionError:
        return None, f"Permission denied: {filepath}"

    if not lines or all(line.strip() == "" or line.strip().startswith("#") for line in lines):
        return None, "File is empty"

    # Stack of (indent_level, dict_ref) — the dict that OWNS keys at >= indent_level
    # Root owns indent 0
    stack = [(-1, data)]
    list_key = None  # key currently accumulating list items
    list_owner = None  # dict that owns the list

    for raw_line in lines:
        stripped = raw_line.rstrip("\n")
        if stripped.strip() == "" or stripped.strip().startswith("#"):
            continue

        indent = len(stripped) - len(stripped.lstrip(" "))

        # Handle list items (  - value)
        list_match = re.match(r"^(\s*)- (.+)$", stripped)
        if list_match:
            if list_key and list_owner and list_key in list_owner:
                val = list_match.group(2).strip()
                if val and val[0] in ('"', "'") and val[-1] == val[0]:
                    val = val[1:-1]
                list_owner[list_key].append(val)
            continue

        # Handle key: value or key:
        kv_match = re.match(r"^(\s*)([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", stripped)
        if not kv_match:
            continue

        key = kv_match.group(2)
        value = kv_match.group(3).strip()

        # Remove quotes
        if value and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]

        # Remove YAML block scalar indicators
        if value in (">", "|", ">-", "|-"):
            value = ""

        # Pop stack to find the parent dict for this indent level
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        current = stack[-1][1]

        if value == "":
            # Key opens a new mapping — create child dict and push it
            new_dict = {}
            current[key] = new_dict
            stack.append((indent, new_dict))
            list_key = None
            list_owner = None
        else:
            # Convert booleans and numbers
            if value.lower() == "true":
                current[key] = True
            elif value.lower() == "false":
                current[key] = False
            elif re.match(r"^\d+$", value):
                current[key] = int(value)
            elif re.match(r"^\d+\.\d+$", value):
                current[key] = float(value)
            else:
                current[key] = value
            list_key = None
            list_owner = None

        # Check if the NEXT lines might be list items for this key
        # We set list_key so that subsequent "- item" lines append here
        if value == "" or value == "[]":
            # Could be a list — we'll detect on first "- item"
            # For now, leave it as a dict; if we see "- item" we need to convert
            pass
        # For depends_on specifically, pre-initialize as list
        if key == "depends_on" and value == "":
            current[key] = []
            list_key = key
            list_owner = current
            # Remove from stack since it's a list not a dict
            if stack and stack[-1][1] is not current.get(key):
                pass  # stack top is the parent, that's fine
            # Actually we pushed a new_dict for depends_on but it should be a list
            # Pop the dict we just pushed and replace with list
            if stack and isinstance(stack[-1][1], dict) and not stack[-1][1]:
                stack.pop()
                current[key] = []
                list_key = key
                list_owner = current

    return data, None


# ── Dependency graph utilities ───────────────────────────────────────────────

def detect_cycles(aliases, depends_on_map):
    """Detect circular dependencies using DFS. Returns (has_cycle, cycle_path)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {a: WHITE for a in aliases}
    parent = {}

    def dfs(node, path):
        color[node] = GRAY
        for dep in depends_on_map.get(node, []):
            if dep not in color:
                continue  # invalid ref, caught elsewhere
            if color[dep] == GRAY:
                # Found cycle — reconstruct path
                cycle = [dep, node]
                cur = node
                while cur != dep and cur in parent:
                    cur = parent[cur]
                    cycle.append(cur)
                cycle.reverse()
                return True, cycle
            if color[dep] == WHITE:
                parent[dep] = node
                result = dfs(dep, path + [dep])
                if result[0]:
                    return result
        color[node] = BLACK
        return False, []

    for alias in aliases:
        if color[alias] == WHITE:
            result = dfs(alias, [alias])
            if result[0]:
                return result
    return False, []


def topological_sort(aliases, depends_on_map):
    """Return aliases in execution order (topological sort). Assumes no cycles."""
    in_degree = {a: 0 for a in aliases}
    for alias, deps in depends_on_map.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[alias] = in_degree.get(alias, 0) + 1

    # Kahn's algorithm
    queue = sorted([a for a in aliases if in_degree[a] == 0])
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for alias in aliases:
            if node in depends_on_map.get(alias, []):
                in_degree[alias] -= 1
                if in_degree[alias] == 0:
                    queue.append(alias)
        queue.sort()  # deterministic order

    return order


# ── Main validation logic ────────────────────────────────────────────────────

def validate(flock_file, nest_dir):
    """Validate a flock.yaml file. Returns (success, messages)."""
    errors = []
    warnings = []

    # 1. Parse YAML
    data, parse_err = parse_flock_yaml(flock_file)
    if parse_err:
        return False, [("error", parse_err)]

    # 2. Check required top-level key: chicks
    if "chicks" not in data or not isinstance(data["chicks"], dict):
        errors.append("Missing required top-level key: chicks")
        return False, [("error", e) for e in errors]

    chicks = data["chicks"]
    if not chicks:
        errors.append("chicks section is empty — define at least one chick")
        return False, [("error", e) for e in errors]

    # 3. Get available nest chicks
    available_chicks = set()
    if os.path.isdir(nest_dir):
        for entry in os.listdir(nest_dir):
            if os.path.isdir(os.path.join(nest_dir, entry)):
                available_chicks.add(entry)

    # 4. Validate each chick entry
    aliases = list(chicks.keys())
    depends_on_map = {}
    messages = []

    for alias, config in chicks.items():
        if not isinstance(config, dict):
            errors.append(f'chick "{alias}": entry must be a mapping')
            continue

        # Validate alias name
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", alias):
            errors.append(
                f'chick "{alias}": alias must start with a letter and contain only '
                f"alphanumeric characters, hyphens, or underscores"
            )

        # Validate chick reference
        chick_name = config.get("chick")
        if not chick_name:
            errors.append(f'chick "{alias}": missing required field "chick"')
        elif chick_name not in available_chicks:
            errors.append(
                f'chick "{alias}": references "{chick_name}" which does not exist in nest. '
                f"Available: {', '.join(sorted(available_chicks))}"
            )
        else:
            messages.append(("info", f'chick "{alias}" \u2192 {chick_name} (exists in nest)'))

        # Validate prompt / prompt_file (exactly one required)
        has_prompt = "prompt" in config and config["prompt"]
        has_prompt_file = "prompt_file" in config and config["prompt_file"]

        if has_prompt and has_prompt_file:
            errors.append(
                f'chick "{alias}": cannot have both "prompt" and "prompt_file" — choose one'
            )
        elif not has_prompt and not has_prompt_file:
            errors.append(f'chick "{alias}": missing required field "prompt" or "prompt_file"')
        elif has_prompt_file:
            prompt_path = config["prompt_file"]
            # Resolve relative to flock.yaml directory
            flock_dir = os.path.dirname(os.path.abspath(flock_file))
            abs_prompt_path = os.path.join(flock_dir, prompt_path)
            if not os.path.isfile(abs_prompt_path):
                errors.append(
                    f'chick "{alias}": prompt_file "{prompt_path}" not found'
                )

        # Validate depends_on
        deps = config.get("depends_on", [])
        if isinstance(deps, str):
            deps = [deps]
        if not isinstance(deps, list):
            errors.append(f'chick "{alias}": depends_on must be a list')
            deps = []

        valid_deps = []
        for dep in deps:
            if dep not in aliases:
                errors.append(
                    f'chick "{alias}": depends_on references "{dep}" which is not defined'
                )
            elif dep == alias:
                errors.append(f'chick "{alias}": cannot depend on itself')
            else:
                valid_deps.append(dep)
        depends_on_map[alias] = valid_deps

        # Validate continue_on_failure (if present)
        if "continue_on_failure" in config:
            val = config["continue_on_failure"]
            if not isinstance(val, bool):
                errors.append(
                    f'chick "{alias}": continue_on_failure must be true or false'
                )

        # Validate timeout (if present)
        if "timeout" in config:
            val = config["timeout"]
            if not isinstance(val, (int, float)) or val <= 0:
                errors.append(
                    f'chick "{alias}": timeout must be a positive number (minutes)'
                )

    # 5. Validate settings section (if present)
    settings = data.get("settings", {})
    if settings and isinstance(settings, dict):
        if "continue_on_failure" in settings:
            val = settings["continue_on_failure"]
            if not isinstance(val, bool):
                errors.append("settings.continue_on_failure must be true or false")
        if "timeout" in settings:
            val = settings["timeout"]
            if not isinstance(val, (int, float)) or val <= 0:
                errors.append("settings.timeout must be a positive number (minutes)")

    # 6. Check for circular dependencies
    has_cycle, cycle_path = detect_cycles(aliases, depends_on_map)
    if has_cycle:
        cycle_str = " \u2192 ".join(cycle_path)
        errors.append(f"circular dependency detected: {cycle_str}")
    else:
        messages.append(("info", "dependency graph: no cycles"))

    # 7. Compute execution order
    if not has_cycle:
        order = topological_sort(aliases, depends_on_map)
        arrow = " \u2192 "
        messages.append(("info", f"execution order: {arrow.join(order)}"))

    # 8. Prompt resolution summary
    if not any("prompt" in e for e in errors):
        messages.append(("info", "all prompts resolved"))

    # Combine all messages
    all_messages = messages + [("error", e) for e in errors]
    return len(errors) == 0, all_messages


# ── CLI entry point ──────────────────────────────────────────────────────────

def main():
    import json as json_mod

    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <flock-file> <nest-dir> [--parse]", file=sys.stderr)
        sys.exit(2)

    flock_file = sys.argv[1]
    nest_dir = sys.argv[2]
    parse_mode = "--parse" in sys.argv

    if parse_mode:
        # Output parsed data as JSON for consumption by other tools
        data, parse_err = parse_flock_yaml(flock_file)
        if parse_err:
            print(json_mod.dumps({"error": parse_err}))
            sys.exit(1)
        print(json_mod.dumps(data, default=str))
        sys.exit(0)

    print("Validating flock.yaml...\n")

    success, messages = validate(flock_file, nest_dir)

    for msg_type, msg in messages:
        if msg_type == "info":
            info(msg)
        elif msg_type == "warn":
            warn(msg)
        elif msg_type == "error":
            error(msg)

    print()
    if success:
        print("Flock is valid!")
        sys.exit(0)
    else:
        print("Flock validation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
