---
name: game-improvement
description: "Improve an existing Playdrop game's visuals, audio, controls, performance, and feel. Use when the user already has a project and wants iteration, polish, or stronger runtime quality before publishing or republishing."
---

# Game Improvement

Use this skill for focused iteration on an existing Playdrop project.

## Workflow

1. Log in, initialize, and validate the project
2. Inspect 2 to 3 strong references before making major changes
3. Update `catalogue.json` for the intended version and report a catalogue preview with `./bin/playdrop task report-catalogue --file catalogue.json --message "Planned the version"` before major code changes.
4. Improve visuals, animation, audio, controls, feel, or performance
5. Verify portrait, landscape, and desktop surfaces when the game supports them
6. Re-test locally with the staged CLI browser wrapper, for example `./bin/playdrop project capture . --surface mobile-portrait --dev-auth anonymous --timeout 20 --screenshot output/playwright/mobile-portrait.png`
7. Capture and validate before publish or marketing
8. Inside a server-assigned task workspace, upload the private updated version with `./bin/playdrop task upload` only after final local inspection and validation, then mark it done with `./bin/playdrop task done`. Task upload is final for this task; later edits cannot replace the uploaded draft.

## Rules

- do not polish around a broken or confusing core loop
- preserve the current PlayDrop CLI `catalogue.json` schema: a top-level JSON object with an `apps` array. Do not rewrite it into top-level `app`, top-level `displayName`, or a bare array. Update the existing `apps[]` entry for the game and keep its `name` stable unless the task explicitly says otherwise.
- preserve generated owned runtime assets as `ownedAssets[].files` role-to-path objects, for example `"files": {"primary": "assets/2d/player.png"}`. Do not rewrite them to `file`/`type` shorthand fields or a `files` array.
- if the strongest raw moment is still not worth clicking, step back before more surface polish
- use this skill to improve a viable game, not to rescue a concept that never worked
- keep the PlayDrop SDK loader and explicit SDK initialization in browser games; add them if missing before upload validation
- initialize the PlayDrop SDK early, but call `await sdk.host.ready()` only after required runtime assets have loaded and the first playable frame is visibly populated with the board, player, enemies, props, or other primary gameplay objects
- requested mechanics must be reachable in normal play; if an update adds or changes hits, physics collisions, particle bursts, combos, pickups, reveals, or attacks, a normal tap/click/key input must visibly trigger that mechanic within the first few seconds
- add or fix background music and SFX before marketing unless `preview.audioPolicy` intentionally declares `silent`
- make the first preview scene visually active enough for capture before generating assets
- when adding or replacing PlayDrop packs, declare reused packs as `uses.packs` string refs only, for example `"uses": {"packs": ["pack:playdrop/zombie-apocalypse-kit-repack@1.0.1"]}`. Do not put objects, `ref`/`runtimeKey` pairs, runtimeKey fields, or local paths inside `uses.packs`; enumerate pack members at runtime with `sdk.assets.listAppAssets()`
- when creating or replacing generated 2D runtime PNG assets, open/read `.playdrop/plugin/skills/asset-extraction-2d/SKILL.md` and follow that skill exactly; it is the only source of truth for output shape, transparent PNG extraction, sprite-sheet acceptance, and validation
- for browser testing inside a worker task, use `./bin/playdrop project capture` and the capture screenshots/logs it produces. Do not run raw Node scripts that `require("playwright")`; the isolated task workspace may not have local Node dependencies. Do not start ad hoc foreground servers such as `python -m http.server`, `npm run dev`, `vite`, or `next dev` from an agent command; a foreground server blocks the agent and leaves the task running without progress
- keep changes in the creator project; do not change PlayDrop platform code for game-specific polish
- inside server-assigned task workspaces, do not publish publicly and do not run `playdrop project publish`; use the task-scoped upload, done, and fail commands from the server prompt
- if an update cannot be completed, run `./bin/playdrop task fail --message "<creator-friendly reason>"` and exit non-zero

## Shared references

- `existing-projects.md`
- `assets-and-generation.md`
- `audio.md`
- `performance-debugging.md`
- `gameplay-review.md`
- `marketing-audio.md`
- `preview-guidelines.md`

## Handoff

- pre-listing desirability review -> `gameplay-review`
- visual direction rethink before polishing assets -> `art-direction`
- concept or scope rethink -> `game-planning`
- new listing assets or publish prep -> `store-listing`
- full marketing preparation -> `marketing-pack`
