---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the builder v2 asset preference order."
---

# Make Assets

## Preference Order

1. PlayDrop packs or exact assets that match style and runtime needs.
2. CC0 assets from the web, converted and attributed correctly.
3. Agent-native asset/image generation when available for the asset type.
4. Deliberate owned vector/canvas assets only when they are intentionally designed for the game, not placeholders.
5. Fail the phase loudly when the requested asset quality requires generated media and no native generator can save local files.

This order is BINDING for every image or audio generation anywhere in the build, including art-direction boards, asset sheets, and listing art. Builder tasks must never spend PlayDrop credits for media generation. Do not invoke PlayDrop-hosted AI media generation from NEW_GAME, GAME_UPDATE, or REMIX_GAME work. Native generation only counts when it writes a real file in the workspace. If native generation returns only an unpersisted preview, treat it as unavailable and choose packs, CC0, owned designed assets, or a clear phase failure.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- `catalogue.json.design.coreAssets.values` must be a subset of `uses.packs`.
- Set `catalogue.json.design.assetStrategy` honestly: `pack-first`, `mixed`, `owned-assets`, or `procedural`.
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Never render primitives, emoji, or plain CSS/canvas shapes as the player character, mascot, or primary interactive objects in a real game. `assetStrategy: procedural` is only acceptable for deliberately abstract prototypes.
- Before generating anything, name in your notes at least 2 candidate packs and 2 individual catalogue assets you searched, and why each was used or rejected.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and listing-only assets should warn and keep play unblocked.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
