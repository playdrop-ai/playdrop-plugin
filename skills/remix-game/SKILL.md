---
name: remix-game
description: "Create a new PlayDrop remix by scaffolding from the source app and transforming it into a distinct game."
---

# Remix Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use the agent-chosen reporting vocabulary in `../../references/phases/remix-game.md`.

## Rules

- Do not edit the source game in place.
- Scaffold with `playdrop project create app <slug> --remix <source-ref>` after claiming the new slug when the task requires it.
- Study the source mechanics, assets, and listing before changing them.
- Make a meaningful transformation: new loop, constraint, level structure, fantasy, or input feel.
- Keep source ancestry in `catalogue.json` and refresh any populated optional `design` tag refs that changed.
- Choose and declare one supported `primarySurface`; never carry an ambiguous legacy surface contract into the remix.
- Validate per `../playtest-game/SKILL.md` before upload.

## Read when needed

- Before scaffolding and catalogue edits: `../../references/catalogue-json.md` and `../../references/tech/playdrop-sdk.md`.
- For visual changes: the relevant asset skill and art-direction reference.
- Before gameplay validation or store media: the playtest and listing skills.
