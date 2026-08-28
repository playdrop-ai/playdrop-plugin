---
name: discover-assets
description: "Search PlayDrop for reusable games, assets, packs, and remix sources before building."
---

# Discover Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use `playdrop search`, `browse`, `detail`, and `versions browse`.

## Workflow

1. For every new game, run three searches limited to games or demos before scaffolding. Use materially different mechanic, genre, or theme keywords and relevant tags so asset-only searches cannot satisfy this requirement.
2. Inspect the strongest game and demo results with `playdrop detail`. Download the two best sources with `playdrop app source app:<creator>/<name>@<version>`. The command prints the temporary folder containing the source; add a directory argument when you need a specific location. Study their mechanics, structure, SDK integration, and reusable patterns; never edit the references or copy their identity.
3. Separately run three searches limited to assets or asset packs. For 2D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category IMAGE --limit 10`. For 3D gameplay, start with `playdrop search "<genre>" --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --limit 10`.
4. Strongly prefer suitable procedural 3D assets. Search with `playdrop search "<object, effect, or character>" --kind asset --asset-category MODEL_3D --asset-subcategory procedural --limit 10`. Download their exact immutable source with `playdrop asset source asset:<creator>/<name>@r<revision> <directory>` and bundle it locally. Read `../../references/tech/three-js.md` for the official demo download example and SDK contract; never substitute a runtime catalogue import.
5. Inspect details before downloading or declaring anything. Asset-pack detail includes every member's exact `assetRef`, category, format, and file roles. Reference non-procedural assets and packs by exact ref; download their source only when the game genuinely needs editable source.
6. Copy exact current version refs into `catalogue.json` only after `detail` or `versions browse` confirms the version. At runtime, select a pack member by its exact `assetRef`; pack members do not have a `runtimeKey`.
7. Reject packs that match the theme but not the runtime file type.

Do not guess pack versions. Do not list pack members in `uses.assets` to represent a pack. Declare the pack once in `uses.packs`, then use the chosen member's exact `assetRef` from `playdrop detail` in game code.
Read `../../references/asset-pack-index.md` before deciding that no useful pack exists.

Cloud agents can read any Cloud game's Git repository, including its history and drafts. `app source` checks out the requested version and restores its separately stored files, without a writable remote. For uploaded games, assets, and packs, Cloud agents can download published source licensed MIT, CC0, or PLAYDROP. These archives contain what the author uploaded; downloading does not repair them or guarantee that they build. Ordinary creator and public permissions are unchanged. Download an editable pack with `playdrop pack source pack:<creator>/<name>@<version> <directory>`. If a download is denied or source is missing, report the error and choose an accessible reference; do not claim to have studied unavailable code.

Before copying code or assets, check the exact version's license and `canReuseOnPlaydrop` permission, and preserve required attribution. Download access and attribution alone do not grant reuse permission, including for another creator's CLOSED Cloud source. Select a permitted reference instead; never bypass source or reuse restrictions.
