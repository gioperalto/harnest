# webgame — Harnest Chick

Creates responsive, deployable web games from a rough concept. Interviews you to nail down the vision, picks the right tech stack, builds the full game, and wires up GitHub Actions for one-click GitHub Pages deployment.

## Team Roles

| Agent         | Model  | Count | Description                                                                 |
|---------------|--------|-------|-----------------------------------------------------------------------------|
| Game Designer | opus   | 1     | Interviews user, selects tech stack, writes game design document            |
| Builder       | sonnet | 1     | Implements complete playable game + GitHub Actions deployment workflow      |
| Playtester    | sonnet | 1     | Reviews code for bugs and GDD conformance, validates deployment config      |

## Workflow

```
User prompt: "I want to build a [game idea]"
         │
         ▼
  Game Designer (opus)
  ├─ Interviews user (genre, controls, visuals, platform, audio)
  ├─ Selects tech stack
  └─ Writes .harnest/game-design.md
         │
         ▼
    Builder (sonnet)
  ├─ Scaffolds chosen stack
  ├─ Implements full playable game
  ├─ Generates .github/workflows/deploy.yml
  └─ Writes README in game directory
         │
         ▼
  Playtester (sonnet)
  ├─ Reviews GDD conformance
  ├─ Checks for common bugs
  ├─ Validates GH Pages deployment config
  └─ Signs off (or sends builder specific fixes)
         │
         ▼
  <game-slug>/ ready to push → GitHub Pages
```

## Tech Stack Options

The game designer selects the right stack based on your game's complexity:

| Stack | When Used | Bundle Size |
|---|---|---|
| `vanilla` | Simple classics (Pong, Snake, Breakout) | ~0 KB overhead |
| `vite-vanilla` | Medium games, animation, no physics | ~5 KB (Vite runtime) |
| `vite-phaser` | Platformers, shooters, physics, audio | ~1.2 MB |
| `vite-three` | Explicit 3D browser games | ~650 KB |

## Configuration

```yaml
# harnest.yaml (excerpt)
team:
  name: webgame

agents:
  game_designer:
    model: opus
  builder:
    model: sonnet
    supplementary_tool: frontend_design
  playtester:
    model: sonnet

workflow:
  game_designer_first: true
  playtester_on_build: true
  require_playtester_approval: true
  max_review_cycles: 3
```

## Supplementary Tools

### frontend-design (built-in plugin)
Used by the builder for UI and visual implementation guidance. No setup required — enabled by default.

## Local Overrides

Copy `claude/settings.local.json.example` to `claude/settings.local.json` (not committed) to enable optional tools:

```bash
cp claude/settings.local.json.example claude/settings.local.json
```

**Playwright MCP** (optional): Enables browser-based playtesting in addition to static code review. Set `"disabled": false` in `settings.local.json`.

## Output

The chick produces a self-contained game directory:

```
<game-slug>/
├── index.html          (or src/ for Vite projects)
├── game.js / src/      (game implementation)
├── style.css
├── public/assets/      (images, audio — if needed)
├── vite.config.js      (Vite projects only)
├── package.json        (Vite projects only)
├── .github/
│   └── workflows/
│       └── deploy.yml  (push to main → GitHub Pages)
└── README.md           (dev setup + deployment guide)
```

To deploy: push to GitHub, then go to **Settings → Pages → Source: Deploy from branch → gh-pages**.

## Limitations

- **Client-side only**: No backend, database, or real-time multiplayer.
- **2D primary**: Phaser 3 covers the vast majority of 2D use cases. 3D (Three.js) is supported but less guided.
- **Audio assets**: The builder generates procedural audio (Web Audio API tones) when no audio files are provided, or uses Phaser's built-in audio with placeholder assets.
- **Teams feature**: Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `claude/settings.json`).
- **Session persistence**: Teams exist only within a single Claude Code session.
