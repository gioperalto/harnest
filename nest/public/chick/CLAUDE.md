# Harnest — Meta Chick Creator (chick)

This chick creates new harnest chicks. Given a concept (e.g., "data pipeline", "mobile app", "ML training"), it researches the domain, synthesizes findings with user input, then scaffolds a complete chick following harnest conventions. The output is a new `nest/<chick-name>/` directory ready to be hatched.

## Configuration

All team settings live in `harnest.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, workflow rules, and supplementary tool availability.

## Team Structure

| Role        | Model  | Count | Purpose                                                         |
|-------------|--------|-------|-----------------------------------------------------------------|
| Researcher  | haiku  | 2     | Parallel web research — tooling/ecosystem and team/workflow     |
| Synthesizer | opus   | 1     | Merges research, interviews user, writes chick design brief     |
| Builder     | sonnet | 1     | Scaffolds all chick files following harnest conventions         |
| Reviewer    | sonnet | 1     | Audits convention compliance, approves or requests revisions    |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read harnest.yaml
```
Parse team settings, agent definitions, tool availability, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "chick", description: "Meta chick creator team")
```

### Step 3 — Spawn Researchers (Parallel)

Spawn both researchers simultaneously. They investigate the concept from two angles in parallel:

- **researcher-1** — domain tooling and ecosystem (what tools, frameworks, platforms exist)
- **researcher-2** — team structures and workflow patterns (how professionals divide work)

Each researcher writes a report to `.harnest/research-<N>.md` and signals the synthesizer when done.

### Step 4 — Spawn Synthesizer

After both researchers complete, spawn the synthesizer. The synthesizer:
1. Reads both research reports
2. Asks the user 3–5 targeted clarifying questions via `AskUserQuestion`
3. Drafts and confirms the chick design (agents, tools, workflow)
4. Writes `.harnest/brief.md` — the design brief for the builder

**The builder must wait for the synthesizer to complete before starting.**

### Step 5 — Spawn Builder

After the synthesizer produces the brief, spawn the builder. The builder:
1. Reads `.harnest/brief.md`
2. Studies reference chicks (`nest/fullstack/`, `nest/webpage/`) for convention patterns
3. Creates all files in `nest/<chick-name>/`
4. Signals the reviewer when done

### Step 6 — Spawn Reviewer

After the builder signals completion, spawn the reviewer. The reviewer:
1. Audits every generated file against the harnest convention checklist
2. Writes `.harnest/review.md` with verdict (APPROVED or REVISIONS REQUIRED)
3. If revisions are needed, signals the builder with specific issues
4. Builder fixes issues and signals reviewer again
5. Reviewer signs off

### Step 7 — Cleanup

When the reviewer approves:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

The new chick is now available at `nest/<chick-name>/` and can be installed with:
```bash
harnest hatch --chick <chick-name>
```

## Important Notes

- **Tavily MCP credentials**: The researchers use `TAVILY_API_KEY` when Tavily is enabled. Pass as a shell env var — never store in settings files. Without Tavily, researchers fall back to built-in `WebSearch`/`WebFetch` (no key required).
  ```bash
  export TAVILY_API_KEY=tvly-your-key-here
  ```
  Enable by copying the example and setting `"disabled": false`:
  ```bash
  cp claude/settings.local.json.example claude/settings.local.json
  ```
- **Output location**: The builder creates `nest/<chick-name>/` in the current directory (the harnest repo). Run this chick from the harnest repo root.
- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json`).
- **No worktrees**: All agents share the project directory. Researchers, synthesizer, builder, and reviewer all write to `.harnest/` and `nest/` within the same working tree.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
