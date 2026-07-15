---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the builder v2 asset preference order."
---

# Make Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

For an original coherent 2D pack with more than six assets, multiple families or sheets, paired size variants, transparent-background extraction, or approval rounds, use the `make-2d-asset-pack` skill as its own job: it has its own review flow. Cloud game workers do not have it staged: use existing packs, reduce scope, and record bespoke pack creation as a suggested follow-up job. Return here after a pack is approved to declare it in the game.

## Preference Order

1. PlayDrop packs or exact assets that match style and runtime needs.
2. CC0 assets from the web, converted and attributed correctly.
3. Agent-native asset/image generation when available for the asset type.
4. PlayDrop CLI AI generation (`playdrop ai create ...`) when native generation is unavailable for the asset type or failed after one retry.
5. Plan C, only after BOTH generation paths failed (including `insufficient_funds` on the CLI path): deliberately designed owned vector/canvas assets or a reduced asset scope, recorded honestly in working notes or existing project prose. Never as a first resort.

This order is BINDING for every image or audio generation anywhere in the build, including hero art, art-direction boards, generated assets, game backgrounds, and listing art; a reference or phase doc that names one command does not override it. Steps 1-2 do not apply to bespoke identity artifacts (hero art, mockup board, app icon, and listing heroes derived from the canonical hero): those start at native generation. Every generation downstream of the canonical hero passes `assets/art-direction/hero-portrait.png` (and the board when relevant) as reference images. Native generation mechanics: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`); after generating, copy the newest produced file into the workspace target and verify it with `file`. Native counts as failed only when generation or that copy fails.

Media failure policy: for a direct creator's game work, a media generation failure, including running out of PlayDrop credits, must never fail the work: record the reason, apply Plan C, and surface "add credits to regenerate art" as a creator next step. In a PlayDrop Cloud game task, the artifacts production upload requires for your task type (new games: the board and listing hero pair; remixes and updates: their listing media; the canonical art-direction heroes are judged in shipped files, not gated at upload) are the exception: if one cannot be produced after the documented retries, fail the phase clearly instead of continuing toward an upload that will reject it.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- If the game needs only a small subset of a pack, declare those exact asset version refs in `uses.assets` instead of the whole pack.
- Declare a whole pack only when the runtime genuinely uses the pack. Never add a pack merely to satisfy validation or an asset-use requirement.
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Temporary primitives and plain shapes are allowed during the planned greybox phase to tune the loop, then must be replaced before upload. Never ship them as the player character, identity subject, or primary interactive objects in a real game. Procedural primary visuals are only acceptable for deliberately abstract prototypes.
- Backgrounds: `references/art-direction-board.md` step 5 owns the rule.
- Do not generate before your reuse notes exist: which packs and assets you considered and why each was used or rejected (for new games, the research phase owns this).
- Register every generated gameplay file per `references/asset-sheet.md`.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and listing-only assets should warn and keep play unblocked.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
