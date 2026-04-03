# Godot Porting

Use this when porting a Godot demo, starter kit, or template into a Playdrop web project.

Start with:
- `playdrop detail playdrop/app/starter-kit-racing --json`
- `playdrop detail playdrop/app/starter-kit-3d-platformer --json`
- `playdrop detail playdrop/app/starter-kit-fps --json`
- `playdrop search starter kit --kind app --app-type demo --json`
- `playdrop browse --kind app --app-type template --json`

Default rule:
- freeze one exact upstream revision and keep attribution exact
- convert scene and resource data into checked-in TS or JSON modules instead of parsing Godot files in the browser at runtime
- port gameplay systems natively for web instead of embedding the engine
- add `window.advanceTime(ms)` and `window.render_game_to_text()` early
- validate on the real Playdrop `/play` route, not only on a local harness

Critical checks:
- transforms : verify Godot `Transform3D` basis mapping before tuning camera or physics
- collisions : confirm Godot collider semantics match the target runtime, especially capsule shapes and concave static colliders
- grounding : if you add custom floor probes, measure from the collider center to the collider bottom plus margin only
- cameras : preserve the authored rig structure first, then tune feel
- first-person viewmodels : if the source uses a separate weapon camera or subviewport, preserve that structure instead of attaching weapons to the world scene
- runtime init : initialize WASM or engine-backed libraries such as Rapier before constructing worlds or controllers, then verify on the real hosted route
- touch orientation : if the gameplay depends on dual-stick or wide look zones, explicitly gate mobile to landscape instead of inventing a portrait fallback
- invisible helpers : distinguish engine helpers such as `RayCast3D` from visible effects before adding tracers, beams, or debug lines to the player-facing game
- mobile : add touch parity only after desktop behavior matches

Good workflow:
- freeze source and attribution first
- write deterministic converters with a `--check` mode
- rebuild gameplay with Playdrop-compatible libraries
- add physics vs render debug views, camera gizmos, and topdown inspection
- prove key transitions with short scripted runs such as spawn, jump, land, camera rotate, collect, and trigger
- publish and capture proof from Playdrop

Compare:
- authored scene transforms versus runtime transforms
- collider bottoms versus visible feet after jump and land
- camera target state versus visible camera state
- viewmodel state versus camera state for first-person games
- hosted `/play` behavior versus harness behavior for SDK bootstrap and runtime initialization
- keyboard, gamepad, and touch parity

Suggested results:
- `Starter Kit Racing Demo` is a strong first reference for content conversion, hosted packaging, and mobile controls
- `Starter Kit 3D Platformer Demo` is a strong first reference for character controller, camera rig, jump and land validation, and physics debug
- `Starter Kit FPS Demo` is a strong first reference for first-person viewmodels, hitscan semantics, pointer-lock input, and landscape-only mobile FPS controls
