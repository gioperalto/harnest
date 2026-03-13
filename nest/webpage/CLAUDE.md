# harnest — Single-Page Website Chick (webpage)

This chick creates single-page websites in React Vite TypeScript. The team is led by a strategist who interviews the customer and produces a brief, supported by an artist who generates images and a builder who constructs the site, validated by a UX tester who signs off before the website is done.

## Configuration

All team settings live in `harnest.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, workflow rules, and supplementary tool availability.

## Team Structure

| Role       | Model  | Count | Purpose                                                   |
|------------|--------|-------|-----------------------------------------------------------|
| Strategist | opus   | 1     | Interviews customer, distills brief, unblocks the team    |
| Artist     | sonnet | 1     | Generates images with Nano Banana MCP → `public/`         |
| Builder    | sonnet | 1     | Builds React Vite TypeScript single-page website          |
| UX Tester  | sonnet | 1     | Simulates users, verifies image integration, signs off    |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read harnest.yaml
```
Parse team settings, agent definitions, tool availability, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "webpage", description: "Single-page website creation team")
```

### Step 3 — Spawn Strategist First

Spawn the strategist. The strategist:
1. Asks the customer (user) targeted clarifying questions via `AskUserQuestion`
2. Writes a complete brief to `.harnest/brief.md`
3. Signals the team that the brief is ready

**All other agents must wait for the strategist to complete before starting their work.**

### Step 4 — Spawn Artist and Builder Simultaneously

After the strategist produces the brief, spawn both at the same time:
- **1x artist** — generates images per the brief, saves to `public/` with semantic names, documents assets in `.harnest/assets.md`
- **1x builder** — builds the site skeleton with placeholder images, integrates real images when artist is done

These two agents work in parallel. The builder starts immediately from the brief; the artist fills in real images as they become available.

### Step 5 — Spawn UX Tester

After the builder signals completion, spawn:
- **1x ux-tester** — runs Playwright simulations, cross-references artist asset manifest, gives actionable feedback to the builder

The UX tester:
- Confirms all artist images in `.harnest/assets.md` are referenced in the site source
- If images are missing or wrong, sends the builder a specific list of paths to fix
- Simulates real user flows at mobile, tablet, and desktop widths
- Signs off when all issues are resolved

### Step 6 — Cleanup

When the UX tester signs off:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

## Tech Stack

- **Framework**: React + Vite + TypeScript
- **Style**: Vanilla CSS — no component libraries (MUI, Chakra, Tailwind, etc.)
- **Target**: Single-page, compacted output (`npm run build` → `dist/`)
- **Images**: Placed in `public/`, referenced as root-relative paths (`/filename.ext`)

## Tmux Mode

Use `harnest fly "<task>"` to launch agents in split panes. Intended layout:

```
┌───────────────┬───────────────────────────────┬───────────────┐
│  strategist   │                               │    builder    │
├───────────────┤          monitor              ├───────────────┤
│    artist     │                               │   ux-tester   │
└───────────────┴───────────────────────────────┴───────────────┘
```

The monitor pane (center) displays a live dashboard of task status, agent state, and git activity.

> **Note**: The full-height spanning center monitor is the intended layout. Current harnest uses a tiled approximation.

Use `harnest land` to tear down the session.

## Important Notes

- **Nano Banana MCP**: Artist requires a `GEMINI_API_KEY`. Get a free key at [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey). Set it in `.claude/settings.local.json` under `mcpServers.nanobanana.env.GEMINI_API_KEY`.
- **frontend-design plugin**: Highly recommended for the builder. Enable it in Claude Code settings.
- **Playwright MCP**: Required for the UX tester browser simulation.
- **No worktrees**: All agents work in the same project directory (`use_worktrees: false`).
- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json`).
