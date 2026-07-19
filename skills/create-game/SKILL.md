---
name: create-game
description: "Create a new PlayDrop game from a worker task or direct creator request using builder v2 phases and official templates."
---

# Create Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Follow `../../references/phases/new-game.md`.

Start with the smallest plain-shape playable loop and follow `../../references/greybox-report.md`. Prove ordinary start, causal player agency against a zero-input or opposite-input control, and restart before art or listing work. Retry a failed verb once, then simplify it. Repeat the checks against the final build before upload.

## Non-Negotiables

- Do not create a project by hand. Claim the slug if the task requires it, then scaffold with `playdrop project create app <slug> --template <allowed-template-key>`.
- Record the engine decision before scaffolding, then load exactly one engine skill: `phaser-2d-game` or `three-js-game`. Never read both for one game.
- Use the creator surface as the primary surface when the prompt gives one, unless it is a terrible fit for the requested game. In `catalogue.json`, enable every honestly supported `surfaceTargets` surface, set the top-level `primarySurface`, and add one complete `playtestTapes` entry per enabled surface. These fields are required for every newly created game even though old catalogue content remains compatible without them.
- Use `catalogue.json` for the upload contract and its optional seven-field design classification. Keep richer decisions in working notes or concise `GAME.md`, `ART_DIRECTION.md`, and `AGENTS.md` files when that context will help continued work. These prose files are encouraged, never upload gates; preserve and update existing files instead of overwriting them.
- Before scaffolding, choose the template and any core pack refs, but do not write a nonempty root `catalogue.json`. After scaffolding, keep the scaffold structure, write the scaffolded app catalogue, and replace the sample loop with the game.
- Keep scope small enough to be fun and shippable as a first draft. Scope cuts become next-step suggestions.
- If the request names an existing game, infer only the genre and functional loop. Create original expression: do not copy its name, characters, art, audio, text, story, level layouts, UI composition, or distinctive presentation.
- Run the deterministic `project check` flow from `../playtest-game/SKILL.md` before upload, including the zero-input, start-only, and full-tape comparison on every enabled surface plus the counterfactual, replay, challenge, and applicable 3D-readability checks. Do not upload until the full tape meaningfully beats both controls and every causal check passes.
- Follow `../make-listing/SKILL.md` before upload, including its capture rules for your task type.
- Local Agent and other direct-creator tasks use `project check` screenshots and omit `listing.captureReport`; the native listing recorder is only for the FIRST_PARTY PlayDrop Cloud path.

## Required References

- `../../references/phases/new-game.md`
- `../../references/catalogue-json.md`
- `../../references/asset-pack-index.md`
- `../../references/dimensions.md`
- `../../references/quality-bars.md`
- `../../references/greybox-report.md`
- `../../references/tech/playdrop-sdk.md`
- `../playtest-game/SKILL.md`
- `../make-listing/SKILL.md`
