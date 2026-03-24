# brainstorm — Harnest Chick

A creative brainstorming team that applies generalizable ideation frameworks to any novel challenge or prompt. Give it a problem and it interviews you to frame it properly, then generates ideas from two angles in parallel — structured methods and unconventional provocations — before synthesizing everything into a prioritized, actionable output.

## Prerequisites

This chick uses **claude-code-router (ccr)** to route the provocateur agent to Gemini for cross-model creative diversity.

### Install CCR

```bash
npm install -g @musistudio/claude-code-router
```

### Configure CCR for Gemini

Edit `~/.claude-code-router/config.json`:

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

Set your Gemini API key (get one free at [Google AI Studio](https://aistudio.google.com)):

```bash
export GEMINI_API_KEY=your-key-here
```

Apply config changes:
```bash
ccr restart
```

### Launch with CCR

Run `ccr code` instead of `claude`:

```bash
ccr code
```

## Team Roles

| Agent         | Model  | Count | Description                                                                         |
|---------------|--------|-------|-------------------------------------------------------------------------------------|
| `facilitator` | opus   | 1     | Interviews user, frames the challenge, selects brainstorming frameworks             |
| `explorer`    | sonnet | 1     | Generates ideas using structured methods (SCAMPER, Six Hats, reverse brainstorm)    |
| `provocateur` | haiku  | 1     | Generates unconventional ideas via Gemini (CCR-routed) — runs parallel to explorer  |
| `synthesizer` | sonnet | 1     | Merges all ideas, clusters themes, writes prioritized output to brainstorm-output.md|

## Workflow

```
User Prompt
    │
    ▼
facilitator (interviews user → .brainstorm/brief.md)
    │
    ├──► explorer (structured methods → .brainstorm/ideas-explorer.md)
    │
    └──► provocateur [Gemini] (unconventional → .brainstorm/ideas-provocateur.md)
         [both run in parallel]
    │
    ▼
synthesizer (merges + clusters + evaluates → brainstorm-output.md)
```

1. **Frame** — The facilitator asks targeted questions to understand the challenge and selects applicable brainstorming frameworks for each ideation agent.
2. **Explore** — The explorer applies structured methods (SCAMPER, Six Thinking Hats, How Might We, etc.) to generate a high volume of ideas.
3. **Provoke** — In parallel, the provocateur uses lateral thinking and assumption-busting, with Gemini providing a distinct model perspective.
4. **Synthesize** — The synthesizer merges both idea sets, clusters by theme, evaluates against the brief's success criteria, and writes `brainstorm-output.md`.

## Configuration

All team configuration lives in `harnest.yaml`:

```yaml
agents:
  facilitator:
    model: opus       # Deep understanding of frameworks and user intent
    count: 1

  explorer:
    model: sonnet     # Structured method execution
    count: 1

  provocateur:
    model: haiku      # Routes to Gemini via CCR for cross-model diversity
    count: 1

  synthesizer:
    model: sonnet     # Evaluation and distillation
    count: 1

workflow:
  facilitator_first: true      # Facilitator must finish before ideation starts
  parallel_ideation: true      # Explorer and provocateur run simultaneously
  synthesize_on_ideation: true # Synthesizer runs after both ideation agents complete
  use_worktrees: false
```

## Supplementary Tools

### Mermaid MCP (used by synthesizer — optional)

Enables the synthesizer to generate mind maps and cluster diagrams in the final output.

No credentials required. Requires `node`/`npx` installed.

**If unavailable:** The synthesizer writes text-based cluster descriptions instead.

Enable by setting `"disabled": false` in `.claude/settings.json` (already enabled by default in this chick).

## Local Overrides

Create `claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `claude/settings.local.json.example` for a template. This file is gitignored and will not be committed.

**Important:** Do not store API keys in `settings.local.json` or any committed file. Pass them as shell env vars.

## Output

The final result is written to `brainstorm-output.md` at the project root. It contains:

- **Top Tier Ideas** — best ideas with development notes and risk assessment
- **Middle Tier Ideas** — promising ideas with conditions for promotion
- **Wild Cards** — speculative ideas too interesting to discard
- **Convergence Map** — ideas both agents independently arrived at (strong signal)
- **Recommended Next Steps** — concrete actions to move forward

Intermediate artifacts are written to `.brainstorm/`:
```
.brainstorm/
├── brief.md                   # Facilitator's problem framing
├── ideas-explorer.md          # Structured method ideas
├── ideas-provocateur.md       # Unconventional / Gemini-generated ideas
└── messages/                  # Agent coordination signals
```

## Limitations

- **CCR required for Gemini**: The provocateur routes to Gemini via `claude-code-router`. Without CCR, it falls back to standard haiku. The workflow is fully functional either way — CCR only affects which model powers the provocateur.
- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **No worktrees**: All agents share the project directory. The workflow is designed so agents work on complementary files to minimize conflicts.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
- **CCR config is global**: The `~/.claude-code-router/config.json` applies to all CCR sessions. Adjust routing per-session with `ccr model` or by editing the config directly.
