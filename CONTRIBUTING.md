# Contributing to gmux

Thanks for your interest in contributing to gmux! This guide covers the fork workflow and how to add new templates.

## Fork Workflow

1. **Fork** the repository on GitHub: [gioperalto/gmux](https://github.com/gioperalto/gmux)
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/gmux.git
   cd gmux
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feature/my-change
   ```
4. **Make your changes**, commit, and push:
   ```bash
   git push -u origin feature/my-change
   ```
5. **Open a Pull Request** against `gioperalto/gmux:main`.

## Creating a New Template

Templates live in the `templates/` directory. Each template is a self-contained directory with everything `gmux init` needs to scaffold into a project.

### Template Structure

```
templates/<template-name>/
  gmux.yaml                         # Team config (required)
  CLAUDE.md                         # Claude Code instructions (required)
  README.md                         # Template documentation (required)
  claude/
    agents/*.md                     # Agent definitions (required)
    settings.json                   # Claude Code settings (required)
    settings.local.json.example     # Local overrides example (optional)
```

### Requirements

- **`gmux.yaml`**: Must define `team`, `agents`, `tools`, and `workflow` sections. See the `fullstack` template for the schema.
- **`CLAUDE.md`**: Instructions injected into the project's `CLAUDE.md` on init. Should describe the team structure, workflow, and how to bootstrap the team.
- **`README.md`**: Documentation for the template. Must include:
  - What the template is for
  - Team roles table
  - Workflow description
  - Configuration options
  - Supplementary tool requirements
  - Limitations
- **Agent files**: One `.md` file per agent role in `claude/agents/`. Each file uses frontmatter for agent metadata (name, model, tools, permissions) and markdown body for instructions.
- **`settings.json`**: Claude Code settings including the teams experimental flag, permissions, and MCP server configurations.

### Guidelines

- Keep templates focused — each template should serve a clear use case.
- Use the `fullstack` template as a reference for structure and conventions.
- Test your template by running `gmux init --template <name>` in a fresh directory.
- Document all supplementary tools and how to disable them.

## Code Style

- Shell scripts use `bash` with `set -euo pipefail`.
- Use the existing helper functions (`info`, `skip`, `warn`, `merge`) for user-facing output.
- Keep `bin/gmux` POSIX-friendly where possible.

## Reporting Issues

Open an issue at [github.com/gioperalto/gmux/issues](https://github.com/gioperalto/gmux/issues).
