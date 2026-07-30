---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the builder v2 asset preference order."
---

# Make Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Create assets when they best support the game. For risky mechanics, an optional early playable check can avoid polishing the wrong interaction; familiar or visually led games may benefit from earlier art.

For an original coherent 2D pack with more than six assets, multiple families or sheets, paired size variants, transparent-background extraction, or approval rounds, use the staged `make-2d-asset-pack` skill. Return here after extraction and review to declare the accepted files in the game.

## Preference Order

1. PlayDrop packs or exact assets that match style and runtime needs.
2. CC0 assets from the web, converted and attributed correctly.
3. Agent-native asset/image generation when available for the asset type.
4. PlayDrop CLI AI generation (`playdrop ai create ...`) when native generation is unavailable for the asset type or failed after one retry.
5. Plan C, only after BOTH generation paths failed (including `insufficient_funds` on the CLI path): deliberately designed owned vector/canvas assets or a reduced asset scope, recorded honestly in working notes or existing project prose. Never as a first resort.

Use this preference order for image and audio generation, including hero art, optional direction artifacts, generated assets, backgrounds, and listing art. Bespoke identity artifacts usually start at native generation. When an approved identity reference exists, pass it to related generations when that improves consistency. Native generation mechanics: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`); after generating, copy the newest produced file into the workspace target and verify it with `file`.

Media failure policy: for a direct creator's game work, a media generation failure, including running out of PlayDrop credits, must never fail the work: record the reason, apply Plan C, and surface "add credits to regenerate art" as a creator next step. In a PlayDrop Cloud game task, only media required by the listing contract is an exception: if it cannot be produced after the documented retries, fail clearly instead of continuing toward an upload that will reject it.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- If the game needs only a small subset of a pack, declare those exact asset version refs in `uses.assets` instead of the whole pack.
- Declare a whole pack only when the runtime genuinely uses the pack. Never add a pack merely to satisfy validation or an asset-use requirement.
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Temporary primitives and plain shapes are useful when a rough playable will reduce risk, but replace them before upload unless the game is deliberately abstract.
- Use a real background when the game benefits from one; `../../references/art-direction-board.md` describes useful treatments.
- Prefer individual generation for a small set of game-owned foreground assets. If generation returns a sheet, never ship or report the sheet: use `make-2d-asset-pack` to split it, remove the matte, validate every silhouette, and keep one transparent PNG per accepted asset. The standalone pack publication human gate does not apply when the files remain owned assets inside this one game; code and agent visual review still do.
- Before committing to generation, briefly consider whether an existing pack or asset already fits. Record the decision only when it will help continued work.
- Register every generated gameplay file per `../../references/asset-sheet.md`.
- When running as a hosted worker, report useful accepted transparent gameplay assets only when the worker material protocol is available. Reporting is best-effort and must never block delivery.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and listing-only assets should warn and keep play unblocked.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
