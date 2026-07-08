---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the builder v2 asset preference order."
---

# Make Assets

## Preference Order

1. PlayDrop packs or exact assets that match style and runtime needs.
2. CC0 assets from the web, converted and attributed correctly.
3. Agent-native asset/image generation when available for the asset type.
4. PlayDrop CLI AI generation only when native generation is unavailable or unsuitable.
5. Deliberate simple shapes, icons, letters, or prototype assets only when that is the right scope call.

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
