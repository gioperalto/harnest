# flock — Harnest Chick

A meta chick that creates flock.yaml pipeline files. Give it a multi-step workflow goal and it interviews you about which chicks to chain together, then generates a valid flock.yaml ready for execution — similar to Docker Compose, but for harnest chicks.

## Team Roles

| Agent          | Model  | Count | Description                                                                  |
|----------------|--------|-------|------------------------------------------------------------------------------|
| `interviewer`  | opus   | 1     | Gathers requirements, discovers available chicks, writes pipeline design brief |
| `composer`     | sonnet | 1     | Reads brief and chick configs, generates and validates flock.yaml            |

## Workflow

```
User Request ("create a pipeline for <workflow>")
    │
    ▼
interviewer
  (discover chicks, interview user, design pipeline)
    │
    ▼
.harnest/flock-brief.md
    │
    ▼
composer
  (read brief + chick configs, generate flock.yaml)
    │
    ▼
flock.yaml (project root)
```

1. **Interview** — The interviewer scans `nest/*/harnest.yaml` to discover available chicks and summarize what each does. It then asks you targeted questions about your workflow: which chicks to chain, in what order, how data flows between them, and what prompts each chick needs. Writes `.harnest/flock-brief.md` with the complete pipeline design.
2. **Compose** — The composer reads the brief and each referenced chick's configuration. It generates a valid `flock.yaml` with correct dependencies, prompts, and settings. Validates there are no circular dependencies and that all chick references exist.
3. **Done** — The pipeline file is at `flock.yaml` in the project root, ready for execution.

## What is flock.yaml?

A `flock.yaml` file defines a multi-chick pipeline — a sequence of harnest chicks that run in order, with dependencies and per-chick prompts. Think of it like Docker Compose for AI workflows.

Example:

```yaml
chicks:
  research:
    chick: researcher
    prompt: "Research the latest trends in serverless architecture"

  design:
    chick: architect
    prompt: "Design a serverless API based on the research findings"
    depends_on:
      - research

  build:
    chick: fullstack
    prompt: "Implement the serverless API from the architecture design"
    depends_on:
      - design

settings:
  continue_on_failure: false
  timeout: 30
```

## Configuration

All team configuration lives in `harnest.yaml`:

```yaml
agents:
  interviewer:
    model: opus       # Best model for user interview and pipeline design
    count: 1

  composer:
    model: sonnet     # Strong model for config generation and validation
    count: 1

workflow:
  interviewer_first: true      # Interviewer must complete before composer starts
  use_worktrees: false
  branch_prefix: "flock/"
```

## How to Use

```bash
harnest hatch --chick flock
claude
```

Then describe the multi-step workflow you want to build. The interviewer will guide you through the design process.

## Output

The finished pipeline is a single file at the project root:

```
<project-root>/
└── flock.yaml        # Pipeline configuration
```

Execute it with harnest to run the full multi-chick workflow.

## Limitations

- **Run from your project root**: The composer writes `flock.yaml` relative to the current working directory. Run this chick from the project where you want the pipeline.
- **Chick availability**: The pipeline can only reference chicks that exist in the harnest nest. The interviewer will show you what is available.
- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **No worktrees**: All agents share the project directory. The workflow is designed so agents work on complementary concerns to minimize conflicts.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
