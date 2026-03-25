# Harnest — Meta Flock Pipeline Creator (flock)

This chick creates flock.yaml pipelines. Given a multi-step workflow goal, it interviews the user to understand which chicks to chain together, how data flows between them, and what prompts each chick needs. The output is a `flock.yaml` file at the project root, ready to be executed by harnest.

## Configuration

All team settings live in `harnest.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, workflow rules, and supplementary tool availability.

## Team Structure

| Role         | Model  | Count | Purpose                                                          |
|--------------|--------|-------|------------------------------------------------------------------|
| Interviewer  | opus   | 1     | Gathers user requirements, lists available chicks, writes brief  |
| Composer     | sonnet | 1     | Reads brief and chick configs, generates valid flock.yaml        |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read harnest.yaml
```
Parse team settings, agent definitions, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "flock", description: "Meta flock pipeline creator team")
```

### Step 3 — Spawn Interviewer

Spawn the interviewer first. The interviewer:
1. Reads `harnest.yaml` to understand its role
2. Scans `nest/*/harnest.yaml` to discover available chicks and what each does
3. Asks the user about their multi-step workflow goals via `AskUserQuestion`
4. Identifies which chicks to chain and in what order
5. Identifies data flow between chicks (what each produces and what the next consumes)
6. Asks about per-chick prompts and configuration
7. Writes `.harnest/flock-brief.md` with the complete pipeline design

**The composer must wait for the interviewer to complete before starting.**

### Step 4 — Spawn Composer

After the interviewer produces the brief, spawn the composer. The composer:
1. Reads `.harnest/flock-brief.md`
2. Reads each referenced chick's `harnest.yaml` to understand inputs, outputs, and working directories
3. Generates a valid `flock.yaml` following the flock spec
4. Validates the pipeline: all chick references exist, no circular dependencies, prompts make sense for the data flow
5. Writes `flock.yaml` to the project root

### Step 5 — Cleanup

When the composer signals completion:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

The flock pipeline is now available at `flock.yaml` in the project root and can be executed by harnest.

## Important Notes

- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json`).
- **No worktrees**: All agents share the project directory. The interviewer writes to `.harnest/` and the composer writes to the project root.
- **Output location**: The composer creates `flock.yaml` in the current directory (the project root). Run this chick from the project where you want the pipeline.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
