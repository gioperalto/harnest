# Harnest

> *Every flock needs a nest. Every nest needs its chicks.*

**Harnest** is a composable agent team harness for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Drop it into any project to enable structured, multi-agent development workflows — powered by configurable chicks.

## The Language of Harnest

Harnest speaks in birds.

- **The nest** is where your team lives. It's the configuration your project hatches from — a curated set of agent definitions, workflow rules, and supplementary tools. Think of it as the home base that every chick knows.
- **A chick** is a specific nest configuration, like `fullstack`. Chicks define who's on your team, how they work together, and what tools they have access to. Set one globally or pick one per session.
- **Hatch** your project once to scaffold the nest into place. From there, your team wakes up every time you open Claude.
- **Fly** to launch a full tmux split-pane session — each agent in its own pane, all of them coordinating in real time.
- **Land** to bring the session home, clean up worktrees, and archive the run.

## Commands

| Command | Description |
|---------|-------------|
| `harnest hatch` | Scaffold a chick into the current project |
| `harnest hatch --chick fullstack` | Hatch with a specific chick (one-time) |
| `harnest --chick fullstack` | Set the global default chick |
| `harnest nest` | List available chicks |
| `harnest fly "build a login system"` | Launch agents in tmux split panes |
| `harnest fly --chick fullstack "..."` | Fly with a specific chick |
| `harnest land` | Stop the tmux session and clean up |
| `harnest version` | Print version |
| `harnest help` | Show help |

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

Agent teams require the experimental teams feature. `harnest hatch` configures this automatically in `.claude/settings.json`.

## Quick Start

1. **Install Harnest:**
   ```bash
   brew tap gioperalto/harnest
   brew install harnest
   ```

2. **Hatch in your project:**
   ```bash
   cd your-project
   harnest hatch
   ```
   This scaffolds the default chick (`fullstack`) into your project — copying `harnest.yaml`, agent definitions, and merging Claude Code settings.

3. **Start Claude Code:**
   ```bash
   claude
   ```

4. **Give it a task.** Claude reads the config on startup and bootstraps a Harnest team.

## Chicks

Harnest ships with pre-built team configurations called chicks. Each chick defines a set of agent roles, workflow rules, and supplementary tools tailored for a specific development style.

**Set a global default chick:**
```bash
harnest --chick fullstack
```

**List available chicks:**
```bash
harnest nest
```

**Hatch with a specific chick (one-time override):**
```bash
harnest hatch --chick fullstack
```

The global default is stored in `~/.config/harnest/config` and used by `harnest hatch` when no `--chick` flag is given.

## Tmux Split-Pane Mode

Run agents as separate `claude` processes in a tmux split-pane layout with a live dashboard:

```bash
harnest fly "build a hello world API with tests"
```

This creates a tmux session with one pane per agent (architect, sr-engineer, jr-engineers, test-engineer) plus a monitor dashboard. Agents coordinate through a `.harnest/` directory using file-based task management and messaging.

```
┌───────────────────┬───────────────────┐
│   architect       │   sr-engineer     │
├───────────────────┼───────────────────┤
│   jr-engineer-1   │   jr-engineer-2   │
├───────────────────┴───┬───────────────┤
│   test-engineer       │   monitor     │
└───────────────────────┴───────────────┘
```

**Land the session:**
```bash
harnest land
```

Tmux mode requires `tmux` and `claude` CLI to be installed. The layout and monitor settings are configurable in `harnest.yaml` under the `tmux:` section.

## Available Chicks

| Chick | Description |
|-------|-------------|
| [`fullstack`](nest/fullstack/) | Architect + Sr Engineer + Jr Engineers + Test Engineer. Plan → implement → review → test workflow. |
| [`webpage`](nest/webpage/) | Strategist + Artist + Builder + UX Tester. Interview → generate assets → build → validate workflow for single-page React Vite TypeScript websites. |

See the [nest/](nest/) directory for full documentation on each chick.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to Harnest, including how to create new chicks.

## License

MIT
