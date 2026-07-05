---
name: update-game
description: "Update an existing PlayDrop game without breaking current behavior, using builder v2 update phases."
---

# Update Game

Follow `references/phases/update-game.md`. If this is a worker task, also read `skills/task-worker/SKILL.md`.

## Rules

- Update the staged project in place. Do not change the app slug unless the task explicitly says so.
- Preserve working gameplay before adding polish.
- Refresh `catalogue.json.design` so it describes the new version.
- Validate and self-playtest before upload or publish.

## Required References

- `references/phases/update-game.md`
- `references/dimensions.md`
- `references/quality-bars.md`
- `references/tech/playdrop-sdk.md`
