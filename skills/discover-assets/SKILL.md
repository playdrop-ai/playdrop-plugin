---
name: discover-assets
description: "Search PlayDrop for reusable games, assets, packs, and remix sources before building."
---

# Discover Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use `playdrop search`, `browse`, `detail`, and `versions browse`.

## Workflow

1. For every new game, run three searches limited to games or demos before scaffolding. Use materially different mechanic, genre, or theme keywords and relevant tags so asset-only searches cannot satisfy this requirement.
2. Inspect the strongest game and demo results with `playdrop detail`. Download and extract the two best source archives into a temporary reference directory. Study them for proven mechanics, structure, SDK integration, and reusable patterns; never edit the references or copy their identity.
3. Separately run three searches limited to assets or asset packs. For 2D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category IMAGE --limit 10`. For 3D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --limit 10`.
4. Strongly prefer suitable procedural 3D assets. Always download and bundle their exact immutable source with `playdrop asset source`; never substitute a runtime catalogue import.
5. Inspect details before downloading or declaring anything. Asset-pack detail includes every member's exact `assetRef`, category, format, and file roles. Reference non-procedural assets and packs by exact ref; download their source only when the game genuinely needs editable source.
6. Copy exact current version refs into `catalogue.json` only after `detail` or `versions browse` confirms the version. At runtime, select a pack member by its exact `assetRef`; pack members do not have a `runtimeKey`.
7. Reject packs that match the theme but not the runtime file type.

Do not guess pack versions. Do not list pack members in `uses.assets` to represent a pack. Declare the pack once in `uses.packs`, then use the chosen member's exact `assetRef` from `playdrop detail` in game code.
Read `../../references/asset-pack-index.md` before deciding that no useful pack exists.
