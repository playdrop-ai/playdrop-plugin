---
name: update-game
description: "Update an existing PlayDrop game without breaking current behavior, using builder v2 update phases."
---

# Update Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Follow `references/phases/update-game.md`.

## Rules

- Update the staged project in place. Do not change the app slug unless the task explicitly says so.
- Preserve working gameplay before adding polish.
- Refresh `catalogue.json.design` so it describes the new version.
- Validate and run the deterministic `project check` playtest before upload or publish.

## Required References

- `references/phases/update-game.md`
- `references/catalogue-json.md`
- `references/asset-pack-index.md`
- `references/dimensions.md`
- `references/quality-bars.md`
- `references/art-direction-board.md`
- `references/asset-sheet.md`
- `references/tech/playdrop-sdk.md`
