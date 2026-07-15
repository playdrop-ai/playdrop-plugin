---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the builder v2 asset preference order."
---

# Make Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

## Preference Order

1. PlayDrop packs or exact assets that match style and runtime needs.
2. CC0 assets from the web, converted and attributed correctly.
3. Agent-native asset/image generation when available for the asset type.
4. PlayDrop CLI AI generation (`playdrop ai create ...`) when native generation is unavailable for the asset type or failed after one retry.
5. Plan C, only after BOTH generation paths failed (including `insufficient_funds` on the CLI path): deliberately designed owned vector/canvas assets or a reduced asset scope, recorded honestly in `design.assetStrategy` and your notes. Never as a first resort.

This order is BINDING for every image or audio generation anywhere in the build, including hero art, art-direction boards, asset sheets, game backgrounds, and listing art; a reference or phase doc that names one command does not override it. Steps 1-2 do not apply to bespoke identity artifacts (hero art, mockup board): those start at native generation. Every generation downstream of the canonical hero passes `assets/art-direction/hero-portrait.png` (and the board when relevant) as reference images. Native generation mechanics: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`); after generating, copy the newest produced file into the workspace target and verify it with `file`. Native counts as failed only when generation or that copy fails. A media generation failure, including running out of PlayDrop credits, must never fail a game creation, update, or remix: record the reason, apply plan C, and surface "add credits to regenerate art" as a creator next step.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- `catalogue.json.design.coreAssets.values` must be a subset of `uses.packs`.
- Set `catalogue.json.design.assetStrategy` honestly: `pack-first`, `mixed`, `owned-assets`, or `procedural`.
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Never render primitives, emoji, or plain CSS/canvas shapes as the player character, mascot, or primary interactive objects in a real game. `assetStrategy: procedural` is only acceptable for deliberately abstract prototypes.
- Every 2D game uses a real background image asset per `references/art-direction-board.md` step 5: one flattened image per scene by default, aligned full-canvas alpha layers composed at runtime only for parallax/depth, visually verified in playtest. Never a code-drawn gradient or primitives as a 2D game's backdrop. 3D backdrops come from the 3D environment instead.
- Before generating anything, name in your notes at least 2 candidate packs and 2 individual catalogue assets you searched, and why each was used or rejected.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and listing-only assets should warn and keep play unblocked.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
