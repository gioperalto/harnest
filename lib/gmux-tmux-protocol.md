# gmux Coordination Protocol

You are running in **gmux tmux mode** — a split-pane tmux session where each agent is a separate `claude` process. You coordinate with other agents through the `.gmux/` filesystem directory, NOT through built-in `TeamCreate`, `SendMessage`, `TaskCreate`, `TaskUpdate`, `TaskList`, or `TaskGet` tools.

## Directory Structure

```
.gmux/
├── config.json              # Session metadata (read-only for agents)
├── tasks/
│   └── task-NNN.json        # One file per task
├── messages/
│   └── <ts>-<from>-<to>.json   # Inter-agent messages
├── status/
│   └── <agent-name>.json    # Your heartbeat and state
├── worktrees/
│   ├── jr-engineer-1/       # Git worktree (jr engineers only)
│   └── jr-engineer-2/       # Git worktree (jr engineers only)
├── prompts/
│   └── <agent-name>.txt     # Initial prompts (read-only)
└── log.jsonl                # Append-only activity log
```

## Reading Configuration

```bash
cat .gmux/config.json
```

Returns: `{"session_name": "gmux", "started_at": "<ISO timestamp>", "task": "<user's task description>", "agents": [...]}`

## Task Management

### List tasks
```bash
ls .gmux/tasks/task-*.json 2>/dev/null
for f in .gmux/tasks/task-*.json; do cat "$f"; echo; done
```

### Read a task
```bash
cat .gmux/tasks/task-001.json
```

Task file format:
```json
{
  "id": 1,
  "subject": "Implement login form",
  "description": "Build the login form component with email/password fields...",
  "status": "pending",
  "owner": "",
  "blockedBy": [],
  "blocks": [3, 4]
}
```

Status values: `"pending"`, `"in_progress"`, `"completed"`

### Create a task (architect only)
```bash
TASK_ID=$(ls .gmux/tasks/task-*.json 2>/dev/null | wc -l)
TASK_ID=$((TASK_ID + 1))
TASK_FILE=$(printf ".gmux/tasks/task-%03d.json" "$TASK_ID")
TMP=$(mktemp)
cat > "$TMP" << 'TASKEOF'
{
  "id": TASK_ID_HERE,
  "subject": "...",
  "description": "...",
  "status": "pending",
  "owner": "",
  "blockedBy": [],
  "blocks": []
}
TASKEOF
sed -i '' "s/TASK_ID_HERE/$TASK_ID/" "$TMP"
mv "$TMP" "$TASK_FILE"
```

### Update a task
```bash
# Read current, modify, write atomically
TMP=$(mktemp)
# Use python3 or jq to update fields
python3 -c "
import json
with open('.gmux/tasks/task-001.json') as f:
    t = json.load(f)
t['status'] = 'in_progress'
t['owner'] = 'jr-engineer-1'
with open('$TMP', 'w') as f:
    json.dump(t, f, indent=2)
" && mv "$TMP" .gmux/tasks/task-001.json
```

## Messaging

### Send a message
```bash
TS=$(date +%s%N)
FROM="your-agent-name"
TO="target-agent-name"
TMP=$(mktemp)
cat > "$TMP" << MSGEOF
{
  "from": "$FROM",
  "to": "$TO",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "subject": "Review request for task 3",
  "body": "I've completed the login form implementation. Please review."
}
MSGEOF
mv "$TMP" ".gmux/messages/${TS}-${FROM}-${TO}.json"
```

### Check for messages
```bash
# List messages addressed to you
ls .gmux/messages/*-*-your-agent-name.json 2>/dev/null
# Read latest message
ls -t .gmux/messages/*-*-your-agent-name.json 2>/dev/null | head -1 | xargs cat
```

## Status Updates

Update your status file periodically (at least when starting/finishing tasks):

```bash
TMP=$(mktemp)
cat > "$TMP" << STATUSEOF
{
  "agent": "your-agent-name",
  "state": "working",
  "current_task": 3,
  "last_heartbeat": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
STATUSEOF
mv "$TMP" .gmux/status/your-agent-name.json
```

State values: `"idle"`, `"working"`, `"reviewing"`, `"waiting"`, `"done"`

## Activity Log

Append to the shared activity log for monitor visibility:

```bash
echo '{"ts":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","agent":"your-agent-name","action":"task_started","message":"Starting task 3: Implement login form"}' >> .gmux/log.jsonl
```

## Atomic Writes

**Always use atomic writes** to avoid read/write conflicts between agents:

1. Write to a temp file: `TMP=$(mktemp)`
2. Write content to `$TMP`
3. Move atomically: `mv "$TMP" <destination>`

The `mv` command is atomic on the same filesystem, preventing partial reads.

**Exception**: `log.jsonl` uses append (`>>`), which is safe for single-line writes on local filesystems.

## Polling for Changes

Check for new messages and task updates periodically:

```bash
# Poll loop (run between work units, not continuously)
ls -t .gmux/messages/*-*-your-agent-name.json 2>/dev/null | head -5
ls .gmux/tasks/task-*.json 2>/dev/null | while read f; do
  python3 -c "import json; t=json.load(open('$f')); print(t['id'], t['status'], t['owner'])"
done
```

Check for messages after completing each task or major work unit. Do not spin in a tight loop.

## Important Rules

1. **Do NOT use built-in Claude Code team tools** — no `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, `SendMessage`, `TeamCreate`, or `TeamDelete`.
2. **Use filesystem operations only** — `cat`, `echo`, `mv`, `ls`, `python3` for JSON manipulation.
3. **Atomic writes always** — write to temp file, then `mv`.
4. **Update your status** — keep `.gmux/status/<your-name>.json` current.
5. **Log your activity** — append to `.gmux/log.jsonl` for monitor visibility.
6. **Respect task ownership** — only work on tasks assigned to you or unassigned tasks you claim.
7. **Respect dependencies** — don't start a task if its `blockedBy` list contains incomplete tasks.
