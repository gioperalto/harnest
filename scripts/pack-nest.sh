#!/usr/bin/env bash
set -euo pipefail

# pack-nest.sh — Serialize the nest/ directory into lib/nest-registry.json
#
# Run this at release/build time (e.g., from the Homebrew formula or CI).
# The registry embeds all chick data so users don't need the nest/ directory.
#
# Usage: ./scripts/pack-nest.sh [nest-dir] [output-file]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

NEST_DIR="${1:-$PROJECT_ROOT/nest}"
OUTPUT="${2:-$PROJECT_ROOT/lib/nest-registry.json}"

if [ ! -d "$NEST_DIR" ]; then
  echo "Error: nest directory not found at $NEST_DIR" >&2
  exit 1
fi

echo "Packing nest from $NEST_DIR → $OUTPUT"

python3 -c "
import json
import os
import sys

nest_dir = sys.argv[1]
registry = {'version': 1, 'chicks': {}}

for chick_name in sorted(os.listdir(nest_dir)):
    chick_path = os.path.join(nest_dir, chick_name)
    if not os.path.isdir(chick_path):
        continue

    chick = {'files': {}}

    # Walk all files in the chick directory and embed their contents
    for root, dirs, files in os.walk(chick_path):
        for fname in sorted(files):
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, chick_path)

            # Skip hidden files and __pycache__
            if any(part.startswith('.') or part == '__pycache__' for part in rel_path.split(os.sep)):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                chick['files'][rel_path] = content
            except (UnicodeDecodeError, PermissionError):
                # Skip binary or unreadable files
                continue

    # Extract description from harnest.yaml if present
    if 'harnest.yaml' in chick['files']:
        yaml_lines = chick['files']['harnest.yaml'].splitlines()
        for i, line in enumerate(yaml_lines):
            stripped = line.strip()
            if stripped.startswith('description:'):
                desc = stripped.split(':', 1)[1].strip().strip('\"').strip(\"'\")
                if desc and desc not in ('>', '|', '>-', '|-'):
                    chick['description'] = desc
                else:
                    # Multi-line: grab the next non-empty, non-comment line
                    for next_line in yaml_lines[i+1:]:
                        s = next_line.strip()
                        if s and not s.startswith('#') and not s.endswith(':'):
                            chick['description'] = s.strip('\"').strip(\"'\")
                            break
                break

    # Extract agent list from claude/agents/
    agents = []
    for fpath in sorted(chick['files'].keys()):
        if fpath.startswith('claude/agents/') and fpath.endswith('.md'):
            agents.append(os.path.basename(fpath).removesuffix('.md'))
    if agents:
        chick['agents'] = agents

    registry['chicks'][chick_name] = chick

print(json.dumps(registry, indent=2, ensure_ascii=False))
" "$NEST_DIR" > "$OUTPUT"

echo "Packed $(python3 -c "import json; d=json.load(open('$OUTPUT')); print(len(d['chicks']))" ) chicks into $OUTPUT"
