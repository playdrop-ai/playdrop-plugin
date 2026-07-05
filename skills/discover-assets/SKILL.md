---
name: discover-assets
description: "Search PlayDrop for reusable games, assets, packs, and remix sources before building."
---

# Discover Assets

Use `./bin/playdrop search`, `browse`, `detail`, and `versions browse`.

## Workflow

1. Search only when the creator request mentions style, subject, asset, pack, reference game, or remix source.
2. Inspect details before downloading or declaring anything.
3. Copy exact current version refs into `catalogue.json`.
4. For 3D gameplay, start with `./bin/playdrop search --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --json`.
5. Reject packs that match the theme but not the runtime file type.

Do not guess pack versions. Do not list all pack members in `uses.assets` to represent a pack.
