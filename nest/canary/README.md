# canary — Harnest Chick

A QA and dogfooding team that tests other harnest chicks end-to-end. The validator runs structural checkpoints against each target chick (file presence, YAML schema, agent frontmatter, CLAUDE.md section order, naming conventions, cross-references). The observer monitors OpenTelemetry telemetry in parallel to catch operational anomalies. The result is a structured pass/fail report with a link to the trace dashboard.

## Team Roles

| Agent       | Model  | Count | Description                                                                              |
|-------------|--------|-------|------------------------------------------------------------------------------------------|
| `validator` | sonnet | 1     | Runs 6-checkpoint validation checklist per target chick; writes final canary-report.md   |
| `observer`  | haiku  | 1     | Monitors OTel telemetry, detects anomalies, produces health summary with dashboard URL   |

## Workflow

```
┌─────────────┐
│  Validator   │──── reads harnest.yaml, identifies test targets
│  (setup)     │
└──────┬──────┘
       │ signals "test starting"
       ▼
┌─────────────┐     ┌─────────────┐
│  Validator   │────▶│  Observer    │
│  (execute)   │     │  (monitor)  │
│              │     │             │
│  runs checks │     │  watches    │
│  per chick   │     │  OTel data  │
└──────┬──────┘     └──────┬──────┘
       │                    │
       │◀───────────────────┘  Observer sends health summary
       ▼
┌─────────────┐
│  Validator   │──── writes .harnest/canary-report.md
│  (report)    │
└─────────────┘
```

1. **Setup** — Validator reads `harnest.yaml`, identifies target chicks (webpage, brainstorm), signals Observer to begin monitoring.
2. **Monitor** — Observer configures OTel environment, verifies backend reachability, and watches agent lifecycle events throughout the run.
3. **Validate** — Validator runs 6 structural checkpoints per target chick: file presence, YAML schema, agent frontmatter, CLAUDE.md section order, naming conventions, cross-references.
4. **Report** — Observer queries OTel backend and sends health summary. Validator merges validation results + health data + dashboard URL into `.harnest/canary-report.md`.

## Configuration

All team configuration lives in `harnest.yaml`:

```yaml
agents:
  validator:
    model: sonnet     # Orchestrates validation and writes the report
    count: 1

  observer:
    model: haiku      # Lightweight telemetry monitoring
    count: 1

workflow:
  observer_first: true       # Observer starts before Validator begins test execution
  parallel_execution: true   # Validator and Observer run simultaneously
  validator_reports: true    # Validator produces the final report
  use_worktrees: false
  branch_prefix: "canary/"
```

## Prerequisites

### OTel Telemetry (required for health monitoring)

Enable telemetry export from Claude Code:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
```

### Jaeger — Local OTel Backend (default)

Start Jaeger with Docker before running canary:

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Open the Jaeger UI at [http://localhost:16686](http://localhost:16686).

### Datadog — Cloud OTel Backend (optional)

If you prefer Datadog, pass your API key as an env var — never store it in config files:

```bash
export DD_API_KEY=your-datadog-api-key
export DD_SITE=datadoghq.com   # or datadoghq.eu, etc.
```

The Observer will automatically switch to the Datadog OTLP intake when `DD_API_KEY` is set.

## Local Overrides

Create `claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `claude/settings.local.json.example` for a template with OTel env var documentation. This file is gitignored and will not be committed.

**Important:** Do not store API keys in `settings.local.json` or any committed file. Pass them as shell env vars.

## Output

The final result is written to `.harnest/canary-report.md`. It contains:

- **Summary table** — per-chick checkpoint counts and overall PASS/FAIL verdict
- **Validation results** — per-checkpoint details for each target chick, with diagnostics for any failures
- **OTel health summary** — agent lifecycle table, anomaly list, span counts
- **Dashboard URL** — link to Jaeger or Datadog for trace drill-down

Intermediate artifacts are written to `.harnest/`:
```
.harnest/
└── canary-report.md   # Final pass/fail report with health summary
```

## Limitations

- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **OTel optional**: If no OTel backend is reachable, the Observer reports "Telemetry unavailable" but the Validator's structural checks still run and the report is still produced.
- **Nondeterministic outputs not checked**: Canary validates structural correctness (files, schema, conventions), not the content of agent-generated outputs — those are inherently nondeterministic.
- **No worktrees**: Both agents share the project directory. The workflow is designed so agents work on complementary concerns (validation vs. telemetry) to avoid conflicts.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
