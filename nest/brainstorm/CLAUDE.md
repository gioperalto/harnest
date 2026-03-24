# Harnest — Creative Brainstorming Chick (brainstorm)

This chick applies generalizable brainstorming frameworks to any creative challenge or novel idea. A facilitator interviews the user and selects methods. An explorer and a provocateur generate ideas in parallel — the provocateur routes to Gemini via claude-code-router for cross-model creative diversity. A synthesizer distills everything into a structured, actionable output.

## Prerequisites

This chick requires **claude-code-router (ccr)**. Install it before running:

```bash
npm install -g @musistudio/claude-code-router
```

Configure `~/.claude-code-router/config.json` to route `haiku` model calls to Gemini (used by the provocateur agent):

```json
{
  "providers": [
    {
      "name": "gemini",
      "api_base_url": "https://generativelanguage.googleapis.com/v1beta/models/",
      "api_key": "$GEMINI_API_KEY",
      "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
      "transformer": { "use": ["gemini"] }
    }
  ],
  "router": {
    "default": "anthropic,claude-sonnet-4-5",
    "background": "gemini,gemini-2.5-flash"
  }
}
```

Set your Gemini API key:
```bash
export GEMINI_API_KEY=your-key-here
```

Then launch with `ccr code` instead of `claude`:
```bash
ccr code
```

## Configuration

All team settings live in `harnest.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, workflow rules, and supplementary tool availability.

## Team Structure

| Role         | Model  | Count | Purpose                                                         |
|--------------|--------|-------|-----------------------------------------------------------------|
| Facilitator  | opus   | 1     | Interviews user, frames the challenge, selects frameworks       |
| Explorer     | sonnet | 1     | Generates ideas via structured methods (SCAMPER, 6 Hats, etc.) |
| Provocateur  | haiku  | 1     | Generates unconventional ideas via Gemini (CCR-routed)          |
| Synthesizer  | sonnet | 1     | Merges all ideas, clusters themes, writes final output          |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read harnest.yaml
```
Parse team settings, agent definitions, tool availability, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "brainstorm", description: "Creative brainstorming team")
```

### Step 3 — Spawn Facilitator First

Spawn the facilitator. The facilitator:
1. Asks the user targeted questions to understand the challenge via `AskUserQuestion`
2. Selects 2–3 structured frameworks for the explorer and 2–3 provocations for the provocateur
3. Writes a complete brief to `.brainstorm/brief.md`
4. Signals the explorer and provocateur to begin

**All ideation agents must wait for the facilitator to complete before starting.**

### Step 4 — Spawn Explorer and Provocateur Simultaneously

After the facilitator produces the brief, spawn both at the same time:
- **1x explorer** — generates structured, method-driven ideas using SCAMPER, Six Thinking Hats, reverse brainstorming, and other assigned frameworks; writes to `.brainstorm/ideas-explorer.md`
- **1x provocateur** — generates unconventional, contrarian ideas using assumption-busting, random input, worst-possible-idea inversion, and other lateral provocations; writes to `.brainstorm/ideas-provocateur.md`; routes to Gemini via CCR

These two agents run in parallel. Neither needs to wait for the other.

### Step 5 — Spawn Synthesizer

After both ideation agents signal completion, spawn:
- **1x synthesizer** — reads both idea sets alongside the original brief, clusters ideas by theme, evaluates against success criteria, and writes the final actionable output to `brainstorm-output.md` at the project root

### Step 6 — Cleanup

When the synthesizer writes `brainstorm-output.md`:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

## Branch Naming Convention

If git branching is used during brainstorming:
```
brainstorm/<session-id>-<topic-slug>
```

## Important Notes

- **CCR required**: The provocateur agent routes to Gemini via `claude-code-router`. Run `ccr code` instead of `claude`. Without CCR, the provocateur falls back to the standard haiku model.
- **Gemini API key**: Get a key from [Google AI Studio](https://aistudio.google.com). Pass as `GEMINI_API_KEY` env var — never store in config files.
- **CCR config location**: `~/.claude-code-router/config.json`. Run `ccr restart` after editing the config.
- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.json`).
- **No worktrees**: All agents share the project directory. Shared files are isolated by convention (`.brainstorm/` directory).
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
- **Output file**: The final result is always written to `brainstorm-output.md` at the project root.
