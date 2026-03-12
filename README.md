# gmux

A composable agent team configuration for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Drop gmux into any project to enable structured, multi-agent development workflows.

## Overview

gmux provides a ready-made team of AI agents that collaborate on software tasks:

- **Architect** — plans work, breaks down tasks, creates diagrams, coordinates the team
- **Senior Engineer** — writes foundational code, sets conventions, reviews all work
- **Junior Engineers** (x2) — implement tasks in isolated worktrees, submit for review
- **Test Engineer** — writes and runs unit, integration, and browser tests

The team follows a structured workflow: plan → implement → review → test → merge.

## Prerequisites

### Required

**Claude Code CLI**

Install via Homebrew (macOS/Linux) or npm:

```bash
# Homebrew
brew install claude-code

# npm
npm install -g @anthropic-ai/claude-code
```

You need an active Anthropic API key or Claude Pro/Team subscription. See [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) for setup.

**Experimental Teams Flag**

Agent teams require the experimental teams feature. This is already configured in `.claude/settings.json` — no manual setup needed.

### Optional Supplementary Tools

All supplementary tools are optional. gmux works without them, but they enhance specific agent capabilities. Disable any tool by setting `enabled: false` in `gmux.yaml` and `"disabled": true` in `.claude/settings.json`.

> **Note:** gmux ships with MCP servers pre-configured in `.claude/settings.json`. The instructions below are for installing the underlying tools that those servers depend on. If you'd rather register MCP servers yourself (or add them to a different scope), use `claude mcp add`.

**Codex CLI** (used by sr-engineer)

```bash
# Homebrew
brew install codex

# npm
npm install -g @openai/codex
```

Provides the sr-engineer with Codex-powered code generation and analysis via MCP. Requires an OpenAI API key.

If not pre-configured in `settings.json`, register manually:

```bash
claude mcp add codex -s project -- codex mcp-server
```

**Mermaid MCP Server** (used by architect)

Enables the architect to generate architecture diagrams, flowcharts, and sequence diagrams.

If not pre-configured in `settings.json`, register manually:

```bash
claude mcp add mermaid -- npx -y @anthropic/mermaid-mcp-server
```

**Playwright MCP Server** (used by test-engineer)

Enables the test engineer to write and run browser-based end-to-end tests. See the [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp) for full setup options.

If not pre-configured in `settings.json`, register manually:

```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

**Frontend Design Plugin** (used by jr-engineers)

Enable in Claude Code settings. Used by jr engineers for UI implementation guidance. This is a Claude Code plugin, not an MCP server.

## Quick Start

1. **Copy gmux files into your project:**
   ```bash
   # Copy these files/directories into your project root:
   #   gmux.yaml
   #   CLAUDE.md
   #   .claude/settings.json
   #   .claude/agents/architect.md
   #   .claude/agents/sr-engineer.md
   #   .claude/agents/jr-engineer.md
   #   .claude/agents/test-engineer.md
   ```

2. **Customize `gmux.yaml`** (optional):
   - Adjust agent models and counts
   - Enable/disable supplementary tools
   - Modify workflow settings

3. **Merge `.claude/settings.json`** with your existing settings if you already have one.

4. **Start Claude Code:**
   ```bash
   claude
   ```

5. **Give it a task.** Claude reads `CLAUDE.md` on startup, which instructs it to bootstrap a gmux team for multi-agent work.

## Configuration

All team configuration lives in `gmux.yaml`:

```yaml
agents:
  sr_engineer:
    model: codex      # Change to opus, sonnet, or haiku
    count: 1
    agent_file: sr-engineer.md

workflow:
  max_review_cycles: 3          # Reviews before escalating to architect
  use_worktrees: true           # Jr engineers work in isolated worktrees
  branch_prefix: "gmux/"        # Branch naming: gmux/<task-id>-<desc>
  auto_test_on_approval: true   # Auto-run tests after sr engineer approval
  require_test_approval: true   # Require test engineer sign-off to merge
```

## Agent Roles

| Agent | Model | Description |
|-------|-------|-------------|
| `architect` | opus | Plans and coordinates. Read-only tools + diagram generation. Runs in plan mode. |
| `sr-engineer` | codex | Writes foundational code and reviews all work. Full tool access + Codex MCP. |
| `jr-engineer` | sonnet | Implements assigned tasks in worktree isolation. Full tool access. |
| `test-engineer` | sonnet | Writes and runs tests. Full tool access + Playwright MCP. |

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

## Local Overrides

Create `.claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `.claude/settings.local.json.example` for a template.

This file is gitignored and will not be committed.

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

## Limitations

- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **MCP server scoping**: MCP servers are defined globally in `settings.json`. Agent frontmatter `mcpServers` fields document intent but all agents can technically access all MCP servers.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
- **Codex dependency**: The sr-engineer role uses Codex as its primary model, which requires a separate OpenAI API key and the Codex CLI installed.

## License

MIT
