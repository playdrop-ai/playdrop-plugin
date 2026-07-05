---
name: create-game
description: "Create a new PlayDrop game from a worker task or direct creator request using builder v2 phases and official templates."
---

# Create Game

Follow `references/phases/new-game.md`. If this is a worker task, also read `skills/task-worker/SKILL.md`.

## Non-Negotiables

- Do not create a project by hand. Claim the slug if the task requires it, then scaffold with `./bin/playdrop project create app <slug> --template <allowed-template-key>`.
- Use the creator surface as the primary surface when the prompt gives one, unless it is a terrible fit for the requested game. State the chosen primary surface in `catalogue.json.design`.
- Put all game design decisions in `catalogue.json` under the app entry. Do not create GDD, PLAN, NEXT, or metadata files outside `catalogue.json` except `next-steps.json` for task completion.
- Keep scope small enough to be fun and shippable as a first draft. Scope cuts become next-step suggestions.
- Run the self-playtest from `skills/playtest-game/SKILL.md` before upload.

## Required References

- `references/phases/new-game.md`
- `references/dimensions.md`
- `references/quality-bars.md`
- `references/tech/playdrop-sdk.md`
