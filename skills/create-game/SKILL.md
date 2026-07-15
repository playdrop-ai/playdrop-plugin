---
name: create-game
description: "Create a new PlayDrop game from a worker task or direct creator request using builder v2 phases and official templates."
---

# Create Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Follow `references/phases/new-game.md`.

## Non-Negotiables

- Do not create a project by hand. Claim the slug if the task requires it, then scaffold with `playdrop project create app <slug> --template <allowed-template-key>`.
- Use the creator surface as the primary surface when the prompt gives one, unless it is a terrible fit for the requested game. State the chosen primary surface in `catalogue.json.design`.
- Put all game design decisions in the scaffolded app's `catalogue.json` under the app entry. Do not create GDD, PLAN, NEXT, or metadata files outside `catalogue.json` except `next-steps.json` for task completion.
- Before scaffolding, choose the template, `design.assetStrategy`, and any core pack refs, but do not write a nonempty root `catalogue.json`. After scaffolding, keep the scaffold structure, write the scaffolded app catalogue, and replace the sample loop with the game.
- Keep scope small enough to be fun and shippable as a first draft. Scope cuts become next-step suggestions.
- Run the deterministic `project check` flow from `skills/playtest-game/SKILL.md` before upload.
- Follow `skills/make-listing/SKILL.md` before upload. PlayDrop Cloud tasks run native capture and include `listing.captureReport`. Local Agent and other direct-creator tasks implement real preview support, use `project check` screenshots, never run `project capture` in the worker, and omit `listing.captureReport`.

## Required References

- `references/phases/new-game.md`
- `references/catalogue-json.md`
- `references/asset-pack-index.md`
- `references/dimensions.md`
- `references/quality-bars.md`
- `references/tech/playdrop-sdk.md`
- `skills/playtest-game/SKILL.md`
- `skills/make-listing/SKILL.md`
