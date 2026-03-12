# gmux — Composable Claude Code Agent Harness

gmux is a drop-in agent team configuration for Claude Code. It provides a structured workflow where an architect plans, a senior engineer sets conventions and reviews, junior engineers implement in parallel, and a test engineer validates before merge.

## Configuration

All team settings live in `gmux.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, counts, workflow rules, and supplementary tool availability.

## Team Structure

| Role           | Model  | Count | Purpose                                       |
|----------------|--------|-------|-----------------------------------------------|
| Architect      | opus   | 1     | Plans, decomposes tasks, coordinates the team  |
| Sr Engineer    | sonnet | 1     | Broad-stroke code, conventions, code review    |
| Jr Engineer    | sonnet | 2     | Implements tasks in isolated worktrees          |
| Test Engineer  | sonnet | 1     | Unit tests, integration tests, Playwright tests |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read gmux.yaml
```
Parse team settings, agent definitions, tool availability, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "gmux", description: "gmux agent team")
```

### Step 3 — Spawn Architect
Spawn the architect agent first. The architect:
1. Analyzes the user's request
2. Creates a plan with diagrams (if Mermaid MCP is available)
3. Populates the task list with ordered, dependency-aware subtasks

### Step 4 — Spawn Implementation Agents
After the architect creates the task list, spawn:
- 1x sr-engineer
- 2x jr-engineer (jr-engineer-1, jr-engineer-2)
- 1x test-engineer

The sr engineer picks up foundational tasks first. Jr engineers pick up implementation tasks once sr engineer work unblocks them.

### Step 5 — Review Loop
1. Jr engineer completes a task and notifies sr engineer
2. Sr engineer reviews the work
3. **Approve** → proceed to testing (Step 6)
4. **Reject** → jr engineer revises and resubmits
5. After `max_review_cycles` (default: 3) rejections, escalate to architect

### Step 6 — Test Validation
When `auto_test_on_approval` is enabled (default: true):
- After sr engineer approval, the test engineer is automatically assigned to validate
- Test engineer writes and runs tests
- **Pass** → task is complete
- **Fail** → bug task created and assigned back to the implementer

### Step 7 — Cleanup
When all tasks are complete:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

## Branch Naming Convention

Jr engineers use the prefix from `workflow.branch_prefix` (default: `gmux/`):
```
gmux/<task-id>-<short-description>
```

## Tmux Mode

gmux also supports a **tmux split-pane mode** where each agent runs as a separate `claude` CLI process in its own tmux pane. Use `gmux start "<task>"` to launch and `gmux stop` to tear down.

In tmux mode, agents coordinate through the `.gmux/` filesystem directory instead of built-in Claude Code team tools. Each agent's prompt includes a coordination protocol that explains how to read/write task files, send messages, and update status through the filesystem. The layout includes a monitor pane with a live dashboard.

This is an alternative to the built-in Agent teams workflow above — use whichever fits your needs.

## Important Notes

- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json`)
- **MCP servers**: Defined globally in `.claude/settings.json`. Agent frontmatter `mcpServers` documents intent but the global config is the runtime source.
- **Worktree isolation**: Jr engineers use `isolation: worktree` for parallel-safe implementation. No manual EnterWorktree calls needed.
- **Team lead**: The main Claude Code session acts as team lead — it spawns the team, monitors progress, and reports back to the user.
- **Supplementary tools are optional**: Set `enabled: false` in `gmux.yaml` and `"disabled": true` in `settings.json` to turn off any MCP server.
