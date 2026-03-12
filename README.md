# gmux

A composable agent team configuration for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Drop gmux into any project to enable structured, multi-agent development workflows — powered by configurable templates.

## Prerequisites

### Required

**Claude Code CLI**

Install via Homebrew (macOS/Linux) or npm:

```bash
# Homebrew
brew install claude-code

# npm
npm install -g @anthropic-ai/claude-code
```

You need an active Anthropic API key or Claude Pro/Team subscription. See [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) for setup.

**Experimental Teams Flag**

Agent teams require the experimental teams feature. `gmux init` configures this automatically in `.claude/settings.json`.

## Quick Start

1. **Install gmux:**
   ```bash
   brew install gmux
   ```
   Or install from a local clone:
   ```bash
   brew install --formula Formula/gmux.rb
   ```

2. **Initialize in your project:**
   ```bash
   cd your-project
   gmux init
   ```
   This scaffolds the default template (`fullstack`) into your project — copying `gmux.yaml`, agent definitions, and merging Claude Code settings.

3. **Start Claude Code:**
   ```bash
   claude
   ```

4. **Give it a task.** Claude reads the config on startup and bootstraps a gmux team.

## Templates

gmux ships with pre-built team configurations called templates. Each template defines a set of agent roles, workflow rules, and supplementary tools tailored for a specific development style.

**Set a global default template:**
```bash
gmux --template fullstack
```

**List available templates:**
```bash
gmux templates
```

**Initialize with a specific template (one-time override):**
```bash
gmux init --template fullstack
```

The global default is stored in `~/.config/gmux/config` and used by `gmux init` when no `--template` flag is given.

## Tmux Split-Pane Mode

Run agents as separate `claude` processes in a tmux split-pane layout with a live dashboard:

```bash
gmux start "build a hello world API with tests"
```

This creates a tmux session with one pane per agent (architect, sr-engineer, jr-engineers, test-engineer) plus a monitor dashboard. Agents coordinate through a `.gmux/` directory using file-based task management and messaging.

```
┌───────────────────┬───────────────────┐
│   architect       │   sr-engineer     │
├───────────────────┼───────────────────┤
│   jr-engineer-1   │   jr-engineer-2   │
├───────────────────┴───┬───────────────┤
│   test-engineer       │   monitor     │
└───────────────────────┴───────────────┘
```

**Stop the session:**
```bash
gmux stop
```

Tmux mode requires `tmux` and `claude` CLI to be installed. The layout and monitor settings are configurable in `gmux.yaml` under the `tmux:` section.

## Available Templates

| Template | Description |
|----------|-------------|
| [`fullstack`](templates/fullstack/) | Architect + Sr Engineer + Jr Engineers + Test Engineer. Plan → implement → review → test workflow. |

See the [templates/](templates/) directory for full documentation on each template.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to gmux, including how to create new templates.

## License

MIT
