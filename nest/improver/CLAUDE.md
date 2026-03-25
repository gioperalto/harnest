# Harnest — Self-Improvement Chick (improver)

This chick picks a single improvement for the harnest application, implements it on a `patch/` branch, validates the work, and submits a PR. The improvement type is randomly selected from three equally-weighted categories: rubric item, new feature, or tech debt elimination.

## Configuration

All team settings live in `harnest.yaml` at the project root. Read it at the start of every session — it is the source of truth for agent roles, models, workflow rules, and supplementary tool availability.

## Team Structure

| Role        | Model  | Count | Purpose                                                              |
|-------------|--------|-------|----------------------------------------------------------------------|
| Assessor    | opus   | 1     | Selects improvement target, writes critical plan to assessment.md    |
| Implementer | sonnet | 1     | Creates branch, implements the improvement, commits                  |
| Validator   | sonnet | 1     | Reviews implementation critically, revises score deltas, signs off   |
| Shipper     | sonnet | 1     | Updates rubric/version as needed, pushes branch, creates PR          |

## Workflow: How to Bootstrap a Team

### Step 1 — Read Configuration
```
Read harnest.yaml
```
Parse team settings, agent definitions, and workflow config.

### Step 2 — Create Team
```
TeamCreate(team_name: "improver", description: "Single-improvement engine")
```

### Step 3 — Spawn Assessor

Spawn the assessor first. The assessor:
1. Reads `nest/rubric.yaml` to understand priorities and current scores
2. Rolls a die to select an improvement category: `rubric_item`, `new_feature`, or `tech_debt`
3. Explores the harnest codebase to identify the highest-priority target in that category
4. Performs a critical evaluation of the target before committing
5. Writes `.harnest/assessment.md` with the target, analysis, proposed changes, and branch name
6. Signals the implementer

**All other agents must wait for the assessor to complete.**

### Step 4 — Spawn Implementer

After the assessor writes `.harnest/assessment.md`, spawn the implementer. The implementer:
1. Reads the assessment
2. Creates the `patch/<name>` branch
3. Implements the improvement precisely — no scope creep
4. Commits the changes with the appropriate prefix (`fix:` / `feat:` / `refactor:`)
5. Signals the validator

### Step 5 — Spawn Validator

After the implementer signals completion, spawn the validator. The validator:
1. Reads `.harnest/assessment.md` to understand what was planned
2. Reviews `git diff main...HEAD` and all modified files critically
3. Checks correctness, scope, code quality, and completeness
4. Revises the proposed rubric score deltas in `.harnest/validation.md` if warranted
5. **If approved**: writes `APPROVED` verdict, signals the shipper
6. **If revisions required**: writes specific, actionable issues, signals the implementer for one revision cycle

After a revision cycle, the validator re-reviews and either approves or reduces the scope delta — no third cycle.

### Step 6 — Spawn Shipper

After the validator signals approval, spawn the shipper. The shipper:
1. Reads `.harnest/assessment.md` and `.harnest/validation.md`
2. If category is `rubric_item` or `new_feature`: updates `nest/rubric.yaml` using the validator's final score deltas (max +2 per dimension), commits
3. If category is `new_feature` only: bumps the minor version in `VERSION` (e.g., `1.2.4` → `1.3.0`), commits
4. Pushes the branch to `origin`
5. Creates a PR against `main` using `gh pr create`

### Step 7 — Cleanup

When the shipper creates the PR:
1. Send `shutdown_request` to all teammates
2. Wait for confirmations
3. Call `TeamDelete` to clean up

## Important Notes

- **Run from the harnest repo root**: The assessor, implementer, validator, and shipper all operate directly in the harnest repository. This chick is designed to improve harnest itself.
- **GitHub CLI required**: The shipper uses `gh pr create`. Ensure `gh` is authenticated (`gh auth status`) before running.
- **Push access required**: The implementer creates a branch locally; the shipper pushes it. Ensure `git remote origin` has push access.
- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `claude/settings.json`).
- **No worktrees**: All agents share the project directory (`use_worktrees: false`).
- **Version bump scope**: Only `new_feature` improvements trigger a minor version bump. `rubric_item` and `tech_debt` improvements do not — those are handled by the standard patch release workflow.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
