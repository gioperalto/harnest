#!/usr/bin/env python3
"""Parse gmux.yaml and output JSON to stdout.

Usage: python3 gmux-parse-yaml.py <path-to-gmux.yaml>

Uses PyYAML if available, otherwise falls back to a built-in parser
that handles the subset of YAML used by gmux.yaml (maps, lists,
scalars, block sequences, flow sequences).
"""

import json
import re
import sys


def parse_yaml_fallback(text):
    """Minimal YAML parser for gmux.yaml format."""
    lines = text.splitlines()
    return _parse_block(lines, 0, 0)[0]


def _current_indent(line):
    return len(line) - len(line.lstrip())


def _strip_comment(value):
    """Remove trailing # comments that aren't inside quotes."""
    in_single = False
    in_double = False
    for i, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return value[:i].rstrip()
    return value


def _parse_scalar(raw):
    """Convert a raw YAML scalar string to a Python value."""
    raw = raw.strip()
    if not raw:
        return ""
    # Quoted strings
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    # Booleans
    if raw.lower() in ("true", "yes", "on"):
        return True
    if raw.lower() in ("false", "no", "off"):
        return False
    # Null
    if raw.lower() in ("null", "~"):
        return None
    # Numbers
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def _parse_flow_sequence(raw):
    """Parse a YAML flow sequence like [a, b, c] or [[a, b], [c, d]]."""
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        return None
    inner = raw[1:-1].strip()
    if not inner:
        return []

    # Handle nested arrays like [[a, b], [c, d]]
    items = []
    depth = 0
    current = ""
    for ch in inner:
        if ch == "[":
            depth += 1
            current += ch
        elif ch == "]":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())

    result = []
    for item in items:
        item = item.strip()
        if item.startswith("["):
            result.append(_parse_flow_sequence(item))
        else:
            result.append(_parse_scalar(item))
    return result


def _parse_block(lines, start, base_indent):
    """Parse a YAML block (mapping or sequence) starting at the given line."""
    result = {}
    i = start

    while i < len(lines):
        line = lines[i]

        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        indent = _current_indent(line)
        if indent < base_indent:
            break

        stripped = line.strip()

        # Block sequence item: "- value" or "- key: value"
        if stripped.startswith("- "):
            # This is a list — parse it
            lst, i = _parse_sequence(lines, i, indent)
            return lst, i

        # Mapping key: value
        match = re.match(r"^(\s*)([^#:]+?)\s*:\s*(.*?)\s*$", line)
        if not match:
            i += 1
            continue

        key = match.group(2).strip()
        value_str = _strip_comment(match.group(3))
        key_indent = _current_indent(line)

        if key_indent > base_indent and i > start:
            break

        if value_str == ">" or value_str == "|":
            # Folded/literal scalar — collect indented lines
            i += 1
            parts = []
            while i < len(lines):
                if not lines[i].strip():
                    parts.append("")
                    i += 1
                    continue
                if _current_indent(lines[i]) > key_indent:
                    parts.append(lines[i].strip())
                    i += 1
                else:
                    break
            joiner = " " if value_str == ">" else "\n"
            result[key] = joiner.join(parts).strip()
        elif value_str.startswith("["):
            result[key] = _parse_flow_sequence(value_str)
            i += 1
        elif value_str:
            result[key] = _parse_scalar(value_str)
            i += 1
        else:
            # Value is a nested block
            i += 1
            # Find the indent of the next non-empty line
            next_indent = None
            for j in range(i, len(lines)):
                if lines[j].strip() and not lines[j].strip().startswith("#"):
                    next_indent = _current_indent(lines[j])
                    break
            if next_indent is not None and next_indent > key_indent:
                child, i = _parse_block(lines, i, next_indent)
                result[key] = child
            else:
                result[key] = None

    return result, i


def _parse_sequence(lines, start, base_indent):
    """Parse a YAML block sequence starting at the given line."""
    result = []
    i = start

    while i < len(lines):
        line = lines[i]

        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        indent = _current_indent(line)
        if indent < base_indent:
            break

        stripped = line.strip()
        if not stripped.startswith("- "):
            break

        item_value = stripped[2:].strip()

        if item_value.startswith("["):
            result.append(_parse_flow_sequence(item_value))
            i += 1
        elif ":" in item_value and not item_value.startswith('"'):
            # Inline mapping like "- key: value"
            # Check for nested block under this item
            item_indent = indent + 2
            # Parse the first key:value
            m = re.match(r"^([^:]+):\s*(.*?)\s*$", item_value)
            if m:
                obj = {}
                k = m.group(1).strip()
                v = _strip_comment(m.group(2))
                obj[k] = _parse_scalar(v) if v else None
                i += 1
                # Check for more keys at item_indent
                while i < len(lines):
                    nl = lines[i]
                    if not nl.strip() or nl.strip().startswith("#"):
                        i += 1
                        continue
                    ni = _current_indent(nl)
                    if ni < item_indent:
                        break
                    nm = re.match(r"^(\s*)([^#:]+?)\s*:\s*(.*?)\s*$", nl)
                    if nm and _current_indent(nl) == item_indent:
                        nk = nm.group(2).strip()
                        nv = _strip_comment(nm.group(3))
                        obj[nk] = _parse_scalar(nv) if nv else None
                        i += 1
                    else:
                        break
                result.append(obj)
            else:
                result.append(_parse_scalar(item_value))
                i += 1
        else:
            result.append(_parse_scalar(item_value))
            i += 1

    return result, i


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <gmux.yaml>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Try PyYAML first
    try:
        import yaml

        data = yaml.safe_load(content)
    except ImportError:
        data, _ = parse_yaml_fallback(content)

    json.dump(data, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
