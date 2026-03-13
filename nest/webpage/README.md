# webpage — harnest Chick

A website creation team for building single-page React Vite TypeScript sites. A strategist interviews the customer, an artist generates visual assets, a builder constructs the site, and a UX tester validates the result.

## Team Roles

| Agent       | Model | Count | Description |
|-------------|-------|-------|-------------|
| `strategist` | opus  | 1 | Interviews the customer, distills a website brief. Runs before all other agents. |
| `artist`     | sonnet | 1 | Generates images with Nano Banana MCP. Places assets in `public/`. |
| `builder`    | sonnet | 1 | Builds the React Vite TypeScript site. Uses frontend-design plugin. |
| `ux-tester`  | sonnet | 1 | Simulates users with Playwright, verifies image integration, signs off. |

## Workflow

```
User Request
    │
    ▼
Strategist (customer interview → brief)
    │
    ├──► Artist (generate images → public/)
    │
    ├──► Builder (skeleton → integrate images → revise)
    │        ▲                         │
    │        └─── UX tester feedback ──┘
    │
    └──► UX Tester (simulate users, verify images, sign off)
              │
              ▼
         Website Complete
```

1. **Brief** — Strategist asks clarifying questions and writes `.harnest/brief.md`
2. **Parallel creation** — Artist generates images; builder constructs the site skeleton
3. **Integration** — Builder replaces placeholder images with artist assets
4. **Validate** — UX tester simulates real user flows and verifies all images are in use
5. **Revise** — Builder fixes any issues reported by the UX tester
6. **Sign-off** — UX tester confirms everything looks good; website is done

## Configuration

All team configuration lives in `harnest.yaml`:

```yaml
agents:
  strategist:
    model: opus       # Change to sonnet for faster/cheaper interviews
    count: 1

  artist:
    model: sonnet
    count: 1

  builder:
    model: sonnet
    count: 1

  ux_tester:
    model: sonnet
    count: 1

workflow:
  strategist_first: true          # Strategist runs before artist/builder
  parallel_artist_builder: true   # Artist and builder run simultaneously
  ux_test_on_build: true          # UX tester waits for builder
  use_worktrees: false            # All agents share the project directory
  require_ux_approval: true       # Website done only when UX tester signs off
```

## Tmux Split-Pane Mode

In addition to the built-in Agent teams workflow, this chick supports running agents as separate `claude` processes in tmux split panes.

**Start a session:**
```bash
harnest fly "build a portfolio website for a freelance photographer"
```

This creates a tmux session with the following intended layout:

```
┌───────────────┬───────────────────────────────┬───────────────┐
│  strategist   │                               │    builder    │
├───────────────┤          monitor              ├───────────────┤
│    artist     │                               │   ux-tester   │
└───────────────┴───────────────────────────────┴───────────────┘
```

- **Strategist** (top-left): Runs first, interviews you interactively
- **Monitor** (center, double width): Live dashboard — task status, agent states, git log
- **Builder** (top-right): Builds the website skeleton, integrates assets
- **Artist** (bottom-left): Generates and saves images to `public/`
- **UX Tester** (bottom-right): Validates the completed site

Each agent pane runs a separate `claude -p` process with a generated prompt that includes the coordination protocol and agent instructions. Agents coordinate through the `.harnest/` directory using file-based messaging.

> **Layout note**: The full-height spanning center monitor column is the intended design. Current harnest uses a tiled layout approximation — a future enhancement will support the exact spanning layout.

**Stop the session:**
```bash
harnest land
```

**Configure the layout** in `harnest.yaml`:
```yaml
tmux:
  session_name: webpage
  layout:
    - [strategist, monitor, builder]
    - [artist, ux-tester]
  monitor:
    refresh_interval: 2
    show: [tasks, git, agents]
```

**Requirements:** `tmux` and `claude` CLI must be installed.

## Supplementary Tools

All supplementary tools are optional but strongly recommended. Disable any tool by setting `enabled: false` in `harnest.yaml` and `"disabled": true` in `.claude/settings.json`.

> **Note:** This chick ships with MCP servers pre-configured in `.claude/settings.json`. The instructions below are for obtaining API keys and installing the underlying tools.

### Nano Banana MCP (used by artist — highly recommended)

Provides the artist with AI image generation powered by Gemini.

**Setup:**
1. Get a free Gemini API key at [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Set your key in `.claude/settings.local.json`:
   ```json
   {
     "mcpServers": {
       "nanobanana": {
         "env": {
           "GEMINI_API_KEY": "your-key-here"
         }
       }
     }
   }
   ```
3. Requires `uv` installed (`brew install uv` or `pip install uv`)

The MCP server runs via `uvx nanobanana-mcp-server@latest` — no separate installation needed beyond `uv`.

**If unavailable:** The artist will use descriptive placeholder comments and CSS gradient backgrounds instead.

### Playwright MCP (used by ux-tester — highly recommended)

Enables the UX tester to drive a real browser, interact with the site, and capture screenshots.

See the [Playwright MCP documentation](https://github.com/microsoft/playwright-mcp) for full setup. No additional API keys required.

**If unavailable:** The UX tester will review source code and give static feedback without live browser interaction.

### Frontend Design Plugin (used by builder — highly recommended)

Provides the builder with UI implementation guidance. Enable in Claude Code settings.

See the [Claude Code frontend-design plugin](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design) for setup.

## Local Overrides

Create `.claude/settings.local.json` to override settings without modifying the tracked `settings.json`. See `.claude/settings.local.json.example` for a template. This file is gitignored and will not be committed.

## Output

The finished website is a standard React Vite TypeScript project. Build it with:

```bash
npm run build
```

The `dist/` directory contains the production output — a single compacted HTML file with inlined CSS and JavaScript, plus the image assets from `public/`.

## Limitations

- **Experimental feature**: Agent teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. This is an experimental Claude Code feature and may change.
- **Nano Banana API key**: Image generation requires a Gemini API key. Without it, the artist generates descriptive placeholders.
- **Single-page only**: This chick is designed for single-page static sites. Multi-page, server-side, or database-backed sites are out of scope — use the `fullstack` chick instead.
- **No worktrees**: All agents share the project directory. Parallel edits are possible but the agents are designed to work on complementary concerns (images vs. code) to minimize conflicts.
- **Session persistence**: Teams exist only within a single Claude Code session. They are not persisted across sessions.
