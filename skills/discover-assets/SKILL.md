---
name: discover-assets
description: "Search PlayDrop for reusable games, assets, packs, and remix sources before building."
---

# Discover Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use `playdrop search`, `browse`, `detail`, and `versions browse`.

## Workflow

1. Search when the creator request mentions style, subject, asset, pack, reference game, remix source, or a known genre with existing pack coverage.
2. Inspect details before downloading or declaring anything. Asset-pack detail includes every member's exact `assetRef`, category, format, and file roles.
3. Copy exact current version refs into `catalogue.json` only after `detail` or `versions browse` confirms the version. At runtime, select a pack member by its exact `assetRef`; pack members do not have a `runtimeKey`.
4. For 2D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category IMAGE --limit 10`.
5. For 3D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --limit 10`.
6. Reject packs that match the theme but not the runtime file type.

Do not guess pack versions. Do not list pack members in `uses.assets` to represent a pack. Declare the pack once in `uses.packs`, then use the chosen member's exact `assetRef` from `playdrop detail` in game code.
Read `../../references/asset-pack-index.md` before deciding that no useful pack exists.
