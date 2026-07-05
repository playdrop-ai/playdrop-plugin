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
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Do not render primitives as the main identity when the request calls for real assets.
- If an asset fails to load, throw a clear error. Do not silently show placeholders.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
