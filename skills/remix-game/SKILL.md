---
name: remix-game
description: "Create a new PlayDrop remix by scaffolding from the source app and transforming it into a distinct game."
---

# Remix Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Follow `references/phases/remix-game.md`.

## Rules

- Do not edit the source game in place.
- Scaffold with `playdrop project create app <slug> --remix <source-ref>` after claiming the new slug when the task requires it.
- Study the source mechanics, assets, and listing before changing them.
- Make a meaningful transformation: new loop, constraint, level structure, fantasy, or input feel.
- Keep source ancestry in `catalogue.json` and refresh `catalogue.json.design`.
- Run the deterministic `project check` playtest before upload.

## Required References

- `references/phases/remix-game.md`
- `references/catalogue-json.md`
- `references/asset-pack-index.md`
- `references/dimensions.md`
- `references/quality-bars.md`
- `references/art-direction-board.md`
- `references/asset-sheet.md`
- `references/tech/playdrop-sdk.md`
