# improver — Harnest Chick

A self-improvement engine for harnest. The team randomly selects one of three improvement categories — rubric item, new feature, or tech debt — identifies the highest-priority target, implements it on a `patch/` branch, validates the work, and submits a PR.

## Team Roles

| Agent       | Model  | Count | Description                                                          |
|-------------|--------|-------|----------------------------------------------------------------------|
| Assessor    | opus   | 1     | Rolls the category die, explores the codebase, writes assessment.md  |
| Implementer | sonnet | 1     | Creates the patch branch, implements the improvement, commits        |
| Validator   | sonnet | 1     | Reviews critically, revises score deltas, signs off                  |
| Shipper     | sonnet | 1     | Updates rubric/version, pushes branch, creates PR                    |

## Workflow

```
User
 │
 ▼
Assessor ──────────────────────────────────► .harnest/assessment.md
 │                                            (category, target, plan, branch name)
 ▼
Implementer ──────────────────────────────► patch/<branch> commit(s)
 │
 ▼
Validator ─────────────────────────────────► .harnest/validation.md
 │   │                                        (verdict, revised score deltas)
 │   └─ REVISIONS REQUIRED ──► Implementer (max 1 cycle)
 │
 └─ APPROVED
     │
     ▼
Shipper ───────────────────────────────────► rubric.yaml update (if applicable)
                                             VERSION bump (new_feature only)
                                             git push + gh pr create
```

**Steps:**
1. **Assess** — assessor reads rubric.yaml, rolls die, explores codebase, writes plan
2. **Implement** — implementer creates branch, makes changes, commits
3. **Validate** — validator reviews diff, checks quality, adjusts score deltas
4. **Revise** (optional) — implementer addresses validator feedback (one cycle)
5. **Ship** — shipper updates rubric/version, pushes, opens PR

## Usage

```bash
# From the harnest repo root
harnest hatch --chick improver

# Ensure gh is authenticated
gh auth status

# Run
claude
```

## Prerequisites

- **`gh` CLI** — authenticated with push access to the harnest repo (`gh auth login`)
- **`git` remote `origin`** — must have push access
- **`python3`** — used by the assessor for random category selection
- **`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`** — set automatically by `claude/settings.json`

## Configuration

```yaml
workflow:
  assessor_first: true   # assessor runs before all other agents
  sequential: true       # strict ordering: assessor → implementer → validator → shipper
  use_worktrees: false   # all agents share the working directory
  branch_prefix: "patch/"
```

No supplementary MCP tools are required. All agents use built-in tools only.

## Output

- **`patch/<noun>-<description>` branch** with one or more commits implementing the improvement
- **`nest/rubric.yaml`** updated with new scores (for `rubric_item` and `new_feature` only, max +2 per dimension)
- **`VERSION`** bumped minor version (for `new_feature` only, e.g. `1.2.4` → `1.3.0`)
- **GitHub PR** targeting `main`, describing what was improved and why

## Improvement Categories

Each run randomly selects one of three equally-weighted categories:

| Category | Branch prefix | Rubric update | Version bump |
|----------|--------------|---------------|--------------|
| `rubric_item` | `patch/` | Yes (max +2) | No |
| `new_feature` | `patch/` | Yes (max +2) | Minor bump |
| `tech_debt` | `patch/` | No | No |

## Limitations

- **Experimental**: The teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) is experimental and requires a recent Claude Code version.
- **Single improvement per run**: The chick is intentionally scoped to one change. Run it again for additional improvements.
- **Harnest repo only**: This chick is designed to operate on the harnest repository itself, not general projects.
- **One revision cycle**: The validator may send the implementer back once. If issues remain after revision, the validator reduces the scope delta rather than blocking the PR.
- **Session persistence**: Teams exist only within a single Claude Code session and are not persisted across sessions.
