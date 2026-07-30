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
- Refresh any populated `catalogue.json.design` tag refs that no longer describe the version; all seven fields remain optional.
- Before the first validation, require `package-lock.json` and run `npm ci` from the directory containing `package.json`. Stop with a clear error if the lockfile is missing or `npm ci` fails. Do not substitute `npm install`.
- If `package.json` or `package-lock.json` changes during the update, run `npm ci` again before the final type-check, validation, build, playtest, and upload.
- Validate and run the deterministic `project check` playtest before upload or publish.

## Read when needed

- For catalogue or runtime changes: `../../references/catalogue-json.md` and `../../references/tech/playdrop-sdk.md`.
- For visual changes: the relevant asset skill and art-direction reference.
- Before gameplay validation or refreshed store media: the playtest and listing skills.
