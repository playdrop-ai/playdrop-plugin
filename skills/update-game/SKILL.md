---
name: update-game
description: "Update an existing PlayDrop game without breaking current behavior or PlayDrop integration."
---

# Update Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use the agent-chosen reporting vocabulary in `../../references/phases/update-game.md`.

## Rules

- Update the staged project in place. Do not change the app slug unless the task explicitly says so.
- Preserve working gameplay before adding polish.
- If the staged legacy catalogue has no `primarySurface`, choose one supported surface and declare it before validation. Every updated version must leave an explicit supported primary surface.
- Refresh any populated `catalogue.json.design` tag refs that no longer describe the version; all seven fields remain optional.
- Before the first validation, require `package-lock.json` and run `npm ci` from the directory containing `package.json`; run it again if either file changes during the update. Stop with a clear error if the lockfile is missing or `npm ci` fails. Never substitute `npm install`.
- Validate per `../playtest-game/SKILL.md` before upload or publish.
- When task context contains `metadata.playdrop.tweaks` or dev/validation reports stale tweaks: read `../tweaks/SKILL.md` and carry the creator's values forward.

## Read when needed

- For catalogue or runtime changes: `../../references/catalogue-json.md` and `../../references/tech/playdrop-sdk.md`.
- For visual changes: the relevant asset skill and art-direction reference.
- Before gameplay validation or refreshed store media: the playtest and listing skills.
