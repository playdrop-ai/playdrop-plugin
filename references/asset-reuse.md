# Asset Reuse

Use this when sourcing catalog assets or packs.

## Workflow

- search or browse first
- inspect asset quality and style fit
- check licensing or credit expectations
- test a few candidates in context before committing
- keep the final runtime style coherent

## Rule

Prefer fewer strong assets over a noisy mix of unrelated packs.

Declare reused packs in `catalogue.json` as `uses.packs` string refs only, for example `"uses": {"packs": ["pack:playdrop/graveyard-kit-repack@5.0.1"]}`. Discover packs with CLI refs from `./bin/playdrop search` or `./bin/playdrop browse`, for example `playdrop/asset-pack/graveyard-kit-repack`, pass those CLI refs to `./bin/playdrop detail <cli-ref>` and `./bin/playdrop versions browse <cli-ref>`, then copy the exact current version into the catalogue ref. Never guess pack versions or assume `1.0.0`. Do not put objects, `ref`/`runtimeKey` pairs, runtimeKey fields, or local paths inside `uses.packs`. Do not list pack member assets under `uses.assets` to represent that pack; `uses.assets` is only for exact standalone asset refs such as `asset:creator/name@r3`. At runtime, enumerate pack members with `sdk.assets.listAppAssets()` and match entries by `assetRef`, `sourcePackRef`, `sourceType`, and file metadata.
