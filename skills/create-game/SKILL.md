---
name: create-game
description: "Create a new PlayDrop game from a worker task or direct creator request using PlayDrop templates and runtime contracts."
---

# Create Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use the agent-chosen reporting vocabulary in `../../references/phases/new-game.md`.

Choose the workflow that best fits the game. When the core interaction is uncertain or nonstandard, prove a small playable version before production polish. A visually led or familiar game may start with art or move art and implementation forward together. `../../references/greybox-report.md` is optional working evidence, not an upload gate.

## Non-Negotiables

- Do not create a project by hand. Claim the slug if the task requires it, then scaffold with `playdrop project create app <slug> --template <allowed-template-key>`.
- Record the engine decision before scaffolding, then load exactly one engine skill: `phaser-2d-game` or `three-js-game`. Continuous motion, physics, a moving camera, or spatial 2D gameplay requires `phaser-2d`; 3D requires `three-js`; the single-file HTML template is only for turn-based or static-screen UI games such as word, quiz, card, and board games. Never choose the HTML template merely because it is faster. Never read both engine skills for one game.
- Choose `primarySurface` for the requested game's interaction and composition. Task `surfaceContext` describes the device that submitted the prompt, not a game-design requirement, and must not determine `primarySurface` unless the prompt itself explicitly requests that surface. One-thumb continuous arcade games normally use `MOBILE_PORTRAIT`; wide platformers and racers normally use `MOBILE_LANDSCAPE`; pointer-heavy, keyboard-heavy, or information-dense games normally use `DESKTOP`. Inside the app entry in `catalogue.json`, enable only honestly supported `surfaceTargets`, set `primarySurface`, and add one complete `playtestTapes` entry per enabled surface. These fields are required for every newly created game even though old catalogue content remains compatible without them.
- Use `catalogue.json` for the upload contract and its optional seven-field design classification. Keep richer decisions in working notes or concise `GAME.md`, `ART_DIRECTION.md`, and `AGENTS.md` files when that context will help continued work. These prose files are encouraged, never upload gates; preserve and update existing files instead of overwriting them.
- Before scaffolding, choose the template and any core pack refs, but do not write a nonempty root `catalogue.json`. After scaffolding, keep the scaffold structure, write the scaffolded app catalogue, and replace the sample loop with the game.
- Before committing to a starting point, search PlayDrop for strong existing games, packs, assets, and proven systems. Reuse what materially improves the result and declare reuse honestly.
- Keep scope small enough to be fun and shippable as a first draft. Scope cuts become next-step suggestions.
- A merely functional prototype is not shippable. The final loop needs player agency, feedback, pressure or challenge, visible progress or payoff, and reliable restart behavior appropriate to the game.
- Do not ship basic SVG shapes, emoji, plain CSS shapes, or default engine primitives as the game's visual identity. Deliberately simple art is valid when it is coherent and uses finished assets.
- If the request names an existing game, infer only the genre and functional loop. Create original expression: do not copy its name, characters, art, audio, text, story, level layouts, UI composition, or distinctive presentation.
- Run the deterministic final `project check` flow from `../playtest-game/SKILL.md` before upload. An earlier check is recommended when it will reduce risk or rework.
- Follow `../make-listing/SKILL.md` before upload, including its capture rules for your task type.
- macOS PlayDrop Cloud and Local Agent worker tasks use the native listing recorder for real gameplay video and source stills, then include `listing.captureReport`. Windows Local Agent and other direct-creator tasks use `project check` for source still evidence and omit `listing.captureReport` until a supported recorder is available. In every case, final listing screenshots come from `make-marketing-screenshots` as fully AI-generated marketing artwork, never from recorder posters or `project check` captures.

## Read when needed

- Before choosing scope and judging the result: `../../references/dimensions.md` and `../../references/quality-bars.md`. They are outcome targets, not an ordered build checklist.
- Before scaffolding and catalogue edits: `../../references/catalogue-json.md` and `../../references/tech/playdrop-sdk.md`.
- When selecting the implementation: exactly one matching engine skill.
- When sourcing or creating art: the relevant asset skill and art-direction reference.
- Before the first gameplay check: `../playtest-game/SKILL.md`.
- Before producing store media: `../make-listing/SKILL.md`.
