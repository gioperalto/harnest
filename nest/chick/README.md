# chick — Harnest Chick

A meta chick that creates new harnest chicks. Give it a concept and it researches the domain, designs a team with your input, and scaffolds a fully convention-compliant chick ready to hatch.

## Team Roles

| Agent         | Model  | Count | Description                                                                    |
|---------------|--------|-------|--------------------------------------------------------------------------------|
| `researcher`  | haiku  | 2     | Parallel research — tooling/ecosystem (r-1) and team/workflow patterns (r-2)  |
| `synthesizer` | opus   | 1     | Merges research, interviews user, writes design brief. Runs after researchers. |
| `builder`     | sonnet | 1     | Creates all chick files. Follows harnest conventions exactly.                  |
| `reviewer`    | sonnet | 1     | Audits convention compliance and signs off. Revisions loop until approved.     |

## Workflow

```
User Request ("create a <concept> chick")
    │
    ├──► researcher-1 (domain tooling & ecosystem)  ──┐
    │                                                  ├──► synthesizer (merge + interview user)
    └──► researcher-2 (team structures & workflows) ──┘         │
                                                                 ▼
                                                    .harnest/brief.md
                                                                 │
                                                                 ▼
                                                           builder
                                                     (scaffold chick files)
                                                                 │
                                                                 ▼
                                                           reviewer ◄─── (revisions loop)
                                                                 │
                                                                 ▼
                                                     nest/<chick-name>/ APPROVED
```

1. **Research** — Two researchers run in parallel. One maps the tooling ecosystem; the other maps team structures and workflow patterns. Each writes a report to `.harnest/research-<N>.md`.
2. **Synthesis** — Synthesizer reads both reports and asks you 3–5 targeted questions to clarify the chick design. Writes `.harnest/brief.md` with proposed agents, tools, and workflow.
3. **Build** — Builder reads the brief, studies reference chicks (`nest/fullstack/`, `nest/webpage/`), and creates all files in `nest/<chick-name>/`.
4. **Review** — Reviewer audits every file against the harnest convention checklist. Approves or returns specific issues to the builder.
5. **Done** — New chick is at `nest/<chick-name>/`, ready to install with `harnest hatch --chick <chick-name>`.

## Configuration

All team configuration lives in `harnest.yaml`:

```yaml
agents:
  researcher:
    model: haiku      # Fast and cheap for web research
    count: 2          # Parallel research from two angles

  synthesizer:
    model: opus       # Best model for synthesis and user interview
    count: 1

  builder:
    model: sonnet
    count: 1

  reviewer:
    model: sonnet
    count: 1

workflow:
  parallel_research: true      # Both researchers run simultaneously
  synthesizer_first: true      # Synthesizer must complete before builder starts
  review_on_build: true        # Reviewer validates after builder completes
  require_reviewer_approval: true  # Chick not done until reviewer signs off
  use_worktrees: false
  branch_prefix: "chick/"
```

## Supplementary Tools

All supplementary tools are optional. Disable any tool by setting `enabled: false` in `harnest.yaml` and `"disabled": true` in `.claude/settings.json`.

### Tavily Search MCP (used by researchers — recommended)

Provides richer web search results with source summaries. Falls back to built-in `WebSearch`/`WebFetch` when disabled — no functionality is lost, only result quality.

**Get a free API key at [tavily.com](https://tavily.com), then:**
```bash
export TAVILY_API_KEY=tvly-your-key-here
```

Enable by copying the example:
```bash
cp claude/settings.local.json.example claude/settings.local.json
```

Requires `node`/`npx` installed. The MCP server runs via `npx -y tavily-mcp@latest` — no separate installation needed.

**If unavailable:** Researchers use built-in `WebSearch` and `WebFetch`. Research quality is slightly reduced but the workflow is fully functional.

### Mermaid MCP (used by synthesizer — recommended)

Enables the synthesizer to generate workflow diagrams and embed them in the design brief.

No credentials required. Requires `node`/`npx` installed.

**If unavailable:** The synthesizer writes ASCII diagrams instead.

## Local Overrides

Create `claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `claude/settings.local.json.example` for a template. This file is gitignored and will not be committed.

**Important:** Do not store API keys in `settings.local.json`. Pass them as shell env vars (see Tavily setup above).

## Output

The finished chick is a directory at `nest/<chick-name>/` in the harnest repository containing:

```
nest/<chick-name>/
├── harnest.yaml                  # Team configuration
├── CLAUDE.md                     # Setup guide (injected into projects on hatch)
├── README.md                     # Chick documentation
└── claude/
    ├── settings.json             # Claude Code settings
    ├── settings.local.json.example
    └── agents/
        └── *.md                  # Agent definitions
```

Install it into any project:
```bash
harnest hatch --chick <chick-name>
```

## Limitations

- **Run from the harnest repo**: The builder creates `nest/<chick-name>/` relative to the current working directory. Run this chick from the root of the harnest repository.
- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **No worktrees**: All agents share the project directory. The workflow is designed so agents work on complementary concerns to minimize conflicts.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
