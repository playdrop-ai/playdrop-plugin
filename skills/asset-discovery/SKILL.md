---
name: asset-discovery
description: "Find reusable code, assets, and packs from the public Playdrop catalogue. Use when the user wants reference games, catalog assets, starter content, remix candidates, or attribution guidance before building."
---

# Asset Discovery

Use this skill when the fastest path is to start from existing public Playdrop content.

## Code reuse workflow

1. Search for the closest public reference
2. Inspect details before downloading anything
3. decide whether to start from a template, align with a starter, or remix a nearly matching app
4. remix or inspect locally only after confirming fit
5. extract the specific pattern needed

## Asset workflow

1. Browse packs and assets
2. Search by keyword or style
3. Compare a few strong candidates
4. Keep runtime style coherent
5. For packs, use CLI refs from search/browse output, for example `playdrop/asset-pack/graveyard-kit-repack`, when calling `./bin/playdrop detail <cli-ref>` and `./bin/playdrop versions browse <cli-ref>`. Convert to a catalogue ref only after copying the exact current version from CLI output, for example `pack:playdrop/graveyard-kit-repack@5.0.1`. Never guess pack versions or assume `1.0.0`.
6. For materially 3D gameplay that uses PlayDrop packs, start from the model-compatible pack list: `./bin/playdrop search --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --json`. Choose from those results before keyword searching. For a monster-themed 3D game, for example, prefer a compatible pack from that list such as `playdrop/asset-pack/ultimate-monsters-repack` over an image-only pack with a tempting name.
7. Verify runtime file compatibility before choosing a pack or asset. For 3D gameplay objects, the selected PlayDrop pack or assets must expose `model/gltf-binary` or `model/gltf+json` files that can be loaded in the game. Do not infer 3D compatibility from pack names, descriptions, release notes, or words like "model" in listing copy; the only acceptable proof is runtime files with contentType `model/gltf-binary` or `model/gltf+json`. Image-only packs are valid for 2D sprites, UI, textures, decals, cards, or secondary decoration, but not as the primary asset pack for a materially 3D game.
8. If no catalogue pack matches both the theme and required runtime file type, choose a compatible pack with a nearby theme or generate owned assets through the appropriate asset-extraction skill instead of declaring an incompatible pack.

## Shared references

- `code-reuse.md`
- `asset-reuse.md`
- `credits.md`
- `create-and-remix.md`
- `assets-and-generation.md`

## Handoff

- new project direction after reference research -> `game-planning`
- integrating a found pattern into an existing project -> `game-improvement`
- heavy engine migration or porting work -> `engine-porting`
