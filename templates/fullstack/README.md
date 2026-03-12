# fullstack — gmux Template

A structured multi-agent team for full-stack development. An architect plans, a senior engineer sets conventions and reviews, junior engineers implement in parallel, and a test engineer validates before merge.

## Team Roles

| Agent | Model | Count | Description |
|-------|-------|-------|-------------|
| `architect` | opus | 1 | Plans and coordinates. Read-only tools + diagram generation. Runs in plan mode. |
| `sr-engineer` | sonnet | 1 | Writes foundational code and reviews all work. Full tool access + Codex MCP. |
| `jr-engineer` | sonnet | 2 | Implements assigned tasks in worktree isolation. Full tool access. |
| `test-engineer` | sonnet | 1 | Writes and runs tests. Full tool access + Playwright MCP. |

## Workflow

```
User Request
    │
    ▼
Architect (plan + task list)
    │
    ├──► Sr Engineer (broad strokes, conventions)
    │        │
    │        ▼
    ├──► Jr Engineer 1 ──► Sr Review ──┐
    ├──► Jr Engineer 2 ──► Sr Review ──┤
    │                                  │
    │    ┌─────────────────────────────┘
    │    ▼
    └──► Test Engineer (validate)
              │
              ▼
         Complete / Bug Report
```

1. **Plan** — Architect analyzes the request, creates subtasks with dependencies
2. **Scaffold** — Sr engineer writes foundational code and sets conventions
3. **Implement** — Jr engineers work in parallel on assigned tasks in isolated worktrees
4. **Review** — Sr engineer reviews jr engineer work (approve/reject cycle, max 3 rounds)
5. **Test** — Test engineer validates approved work with unit, integration, and browser tests
6. **Merge** — Approved and tested work is merged

## Configuration

All team configuration lives in `gmux.yaml`:

```yaml
agents:
  sr_engineer:
    model: sonnet     # Change to opus, sonnet, or haiku
    count: 1
    agent_file: sr-engineer.md

workflow:
  max_review_cycles: 3          # Reviews before escalating to architect
  use_worktrees: true           # Jr engineers work in isolated worktrees
  branch_prefix: "gmux/"        # Branch naming: gmux/<task-id>-<desc>
  auto_test_on_approval: true   # Auto-run tests after sr engineer approval
  require_test_approval: true   # Require test engineer sign-off to merge
```

## Tmux Split-Pane Mode

In addition to the built-in Agent teams workflow, this template supports running agents as separate `claude` processes in tmux split panes.

**Start a session:**
```bash
gmux start "build a user authentication system"
```

This creates a tmux session with the following layout:

```
┌───────────────────┬───────────────────┐
│   architect       │   sr-engineer     │
├───────────────────┼───────────────────┤
│   jr-engineer-1   │   jr-engineer-2   │
├───────────────────┴───┬───────────────┤
│   test-engineer       │   monitor     │
└───────────────────────┴───────────────┘
```

Each agent pane runs a separate `claude -p` process with an auto-generated prompt that includes the coordination protocol and agent instructions. The **monitor** pane displays a live dashboard showing task status, agent state, recent git commits, and activity logs.

**Coordination:** Agents coordinate through the `.gmux/` directory using JSON files for tasks, messages, and status updates — no built-in Claude Code team tools required.

**Stop a session:**
```bash
gmux stop
```

This kills the tmux session, removes git worktrees, prints a task summary, and optionally archives the `.gmux/` directory.

**Configure the layout** in `gmux.yaml`:
```yaml
tmux:
  session_name: gmux
  layout:
    - [architect, sr-engineer]
    - [jr-engineer-1, jr-engineer-2]
    - [test-engineer, monitor]
  monitor:
    refresh_interval: 2
    show: [tasks, git, agents]
```

**Requirements:** `tmux` and `claude` CLI must be installed.

## Supplementary Tools

All supplementary tools are optional. The template works without them, but they enhance specific agent capabilities. Disable any tool by setting `enabled: false` in `gmux.yaml` and `"disabled": true` in `.claude/settings.json`.

> **Note:** This template ships with MCP servers pre-configured in `.claude/settings.json`. The instructions below are for installing the underlying tools that those servers depend on. If you'd rather register MCP servers yourself (or add them to a different scope), use `claude mcp add`.

**Codex CLI** (used by sr-engineer)

```bash
brew install codex    # or: npm install -g @openai/codex
```

Provides the sr-engineer with Codex-powered code generation and analysis via MCP. Requires an OpenAI API key.

**Mermaid MCP Server** (used by architect)

Enables the architect to generate architecture diagrams, flowcharts, and sequence diagrams.

**Playwright MCP Server** (used by test-engineer)

Enables the test engineer to write and run browser-based end-to-end tests. See the [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp) for full setup options.

[**Frontend Design Plugin**](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design) (used by jr-engineers)

Enable in Claude Code settings. Used by jr engineers for UI implementation guidance. This is a Claude Code plugin, not an MCP server.

## Disabling Tools

To disable a supplementary tool:

1. In `gmux.yaml`, set `enabled: false`:
   ```yaml
   tools:
     codex:
       enabled: false
   ```

2. In `.claude/settings.json`, set `"disabled": true`:
   ```json
   "mcpServers": {
     "codex": {
       "disabled": true
     }
   }
   ```

## Local Overrides

Create `.claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `.claude/settings.local.json.example` for a template. This file is gitignored and will not be committed.

## Limitations

- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **MCP server scoping**: MCP servers are defined globally in `settings.json`. Agent frontmatter `mcpServers` fields document intent but all agents can technically access all MCP servers.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
- **Codex dependency**: The sr-engineer role uses the Codex MCP server for code generation and analysis, which requires a separate OpenAI API key and the Codex CLI installed.
