# FPS

Use this for first-person shooters or first-person action games.

Start with:
- `playdrop detail playdrop/app/starter-kit-fps --json`
- `playdrop search fps --kind app --app-type demo --json`
- `playdrop browse --kind app --app-type template --json`
- `playdrop search weapon --kind asset --json`
- `playdrop search crosshair --kind asset --json`

Default rule:
- inspect `playdrop/app/starter-kit-fps` early
- use it as the default reference for pointer-lock controls, gamepad look, viewmodel camera setup, hitscan combat, enemy combat loops, HUD, and touch controls unless a better fit exists
- if mobile uses dual-stick FPS controls, prefer landscape-only support instead of a compromised portrait layout
- if you choose not to use it, say why

Good searches:
- demos : `playdrop search fps --kind app --app-type demo --json`, `playdrop search shooter --kind app --json`
- templates : `playdrop browse --kind app --app-type template --json`
- 3D assets : `playdrop search weapon --kind asset --json`, `playdrop search crosshair --kind asset --json`, `playdrop search sci fi --kind asset-pack --json`
- asset packs : `playdrop search shooter --kind asset-pack --json`, `playdrop search low poly --kind asset-pack --json`

Compare:
- viewmodel follows the camera exactly and uses its own camera or render pass if the source does
- viewmodel lighting stays readable and does not inherit broken world lighting
- desktop input parity for mouse look, pointer capture, jump, fire, and weapon swap
- mobile landscape parity for move stick, look zone, and action buttons
- hitscan semantics versus projectile semantics
- enemy line-of-sight, attack cadence, and health feedback
- HUD health and crosshair behavior
- hosted `/play` route versus local harness

Source parity notes:
- Godot `RayCast3D` in this starter kit is an invisible collision query, not a visible beam
- the original demo shows muzzle flash and impact effects, but not visible projectile bullets
- enemy hit feedback in the original is mostly health loss plus audio, not a heavy screen-space damage vignette
- viewmodel parity matters more than world weapon placement in first-person demos

Suggested result:
- `Starter Kit FPS Demo` is a strong first reference when you want a small first-person sample with hitscan weapons, separate weapon rendering, dual-stick mobile touch controls, and Playdrop-ready hosted validation
