# 3D Platformer

Use this for third-person or orbit-camera 3D platformers.

Start with:
- `playdrop detail playdrop/app/starter-kit-3d-platformer --json`
- `playdrop search platformer --kind app --app-type demo --json`
- `playdrop browse --kind app --app-type template --json`
- `playdrop search platformer --kind asset-pack --json`
- `playdrop search character --kind asset --json`

Default rule:
- inspect `playdrop/app/starter-kit-3d-platformer` early
- use it as the default reference for movement, orbit camera, jump and landing behavior, collectibles, falling platforms, debug hooks, and mobile controls unless a better fit exists
- if you choose not to use it, say why

Good searches:
- demos : `playdrop search platformer --kind app --app-type demo --json`, `playdrop search character controller --kind app --json`
- templates : `playdrop browse --kind app --app-type template --json`
- 3D assets : `playdrop search platform --kind asset --json`, `playdrop search coin --kind asset --json`, `playdrop search skybox --kind asset --json`
- asset packs : `playdrop search platformer --kind asset-pack --json`, `playdrop search low poly --kind asset-pack --json`

Compare:
- idle, walk, and jump transitions
- grounded persistence after landing
- jump height, airtime, and recovery
- camera orbit, zoom, and follow smoothing
- landing readability with shadow, audio, and particles
- mobile and gamepad parity
- deterministic debug hooks such as `advanceTime` and `render_game_to_text`

Suggested result:
- `Starter Kit 3D Platformer Demo` is a strong first reference when you want a small 3D character controller sample with authored camera behavior, collision-driven platforming, and Playdrop-ready host packaging
