---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the PlayDrop asset preference order."
---

# Make Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Create assets when they best support the game. For risky mechanics, an optional early playable check can avoid polishing the wrong interaction; familiar or visually led games may benefit from earlier art.

For every generated gameplay image that requires a transparent background, use the staged `make-2d-asset-pack` skill, even for one sprite. It owns controlled-matte generation, extraction, and alpha validation because image providers do not reliably return structural transparency. Also use it for coherent packs, multiple families or sheets, and approval rounds. A pack is a container of independent assets, not a special size relationship. Return here after extraction and review to declare the accepted files in the game.

## Sourcing And Image Generation Ownership

Before generating an image, prefer a PlayDrop pack or exact asset that already matches the style and runtime need, then a suitable CC0 web asset that can be converted and attributed correctly. Bespoke identity art usually needs generation instead.

Use exactly one production owner for each coherent image job:

- **Active Codex agent:** own the complete job directly. Use the built-in image-generation tool, then perform every required deterministic transform, code check, visual inspection, and corrected retry before returning accepted files.
- **Active Grok agent:** own the complete job directly. Use Grok's own image generation, then perform every required deterministic transform, code check, visual inspection, and corrected retry before returning accepted files. Never delegate image generation to Codex.
- **Active Claude agent:** delegate the complete job to one Codex CLI run with Terra at high reasoning. Do not ask Codex for one source image and resume processing in Claude. Codex owns generation, deterministic transforms, code validation, visual review, corrected retries, and the final accepted-file manifest. Claude only integrates the accepted outputs into the game.

For a Claude delegation, run this from the task workspace and put the full job contract in the prompt:

```bash
codex exec --ephemeral --skip-git-repo-check \
  --model gpt-5.6-terra \
  --config 'model_reasoning_effort="high"' \
  --dangerously-bypass-approvals-and-sandbox \
  --ignore-rules \
  --cd <workspace> \
  -- "You are a delegated image-production helper, not the lead game agent. Read the named PlayDrop skills and complete the full image job below. Write only the requested outputs. Return the accepted-file manifest or the exact error to the lead. Do not run PlayDrop task upload, completion, failure, or submission commands, even if you inherit a task context. <full image job contract>" < /dev/null
```

When visual references are required, add one `--image <absolute-path>` per reference before `--`. The separator is required because `--image` accepts multiple paths. Give Codex the exact absolute output directory, the applicable PlayDrop skill paths, the visual references, and the complete asset or listing contract. For transparent assets, first prepare the managed runtime as directed by `make-2d-asset-pack`, then include its printed `runtime_python` path in the delegation prompt.

Use this ownership rule for hero art, optional direction artifacts, gameplay assets, backgrounds, listing art, and promotional images. Audio generation uses the available audio-specific tools. When an approved identity reference exists, pass it to related generations when that improves consistency. Built-in image generation may initially save a result outside the workspace; the production owner must copy the accepted result into the exact workspace target, verify its type, and inspect it before use.

Do not switch to PlayDrop AI, an ad hoc keyer, or a second production owner when generation or validation fails. Make one corrected retry when the evidence identifies a correctable defect, then fail clearly with the retained reason. For a delegated image job, failure means returning the error to the lead, not failing the parent game task. Optional media may be skipped only when the governing skill says it is optional. Gameplay-required media and the new-game identity trio must fail clearly when they cannot be completed.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- If the game needs only a small subset of a pack, declare those exact asset version refs in `uses.assets` instead of the whole pack.
- Declare a whole pack only when the runtime genuinely uses the pack. Never add a pack merely to satisfy validation or an asset-use requirement.
- For static 3D, prove selected assets expose GLB/GLTF runtime files before choosing them. Procedural 3D assets instead use category `MODEL_3D`, subcategory `procedural`, format `CUSTOM`, and the standard `primary`, `manifest`, `preview`, `source`, and `license` roles. Download and bundle an exact procedural source revision; do not reject it for lacking GLB/GLTF files.
- Before creating or changing a procedural asset, read `../../references/tech/three-js.md`. Use the existing SDK types to check its contract and the official demo or avatar source when an example helps. Run the mandatory CLI preflight required by your workflow and fix every procedural validation error before upload. Do not replace the platform check with a mock Three.js test or a check of your own invented interface.
- Pair reusable procedural 3D code with compact typed custom assets when creators or players need persistent variations. Store the exact procedural asset reference plus validated parameters, following the same composition used by the shared PlayDrop avatar runtime and `asset-spec:playdrop/avatar-skin` skins. Do not duplicate procedural code, geometry, rigs, or animations in each custom asset.
- Temporary primitives and plain shapes are useful when a rough playable will reduce risk, but replace them before upload unless the game is deliberately abstract.
- Use a real background when the game benefits from one; `../../references/art-direction-board.md` describes useful treatments.
- For a small set of game-owned foreground assets, use one `make-2d-asset-pack` family with one slot per asset. Never ask an image provider for a transparent background, ship a painted checkerboard, or write an ad hoc background-removal script. Request the workflow's controlled matte, extract it, validate every silhouette, and keep one transparent PNG per accepted asset. The standalone pack publication human gate does not apply when the files remain owned assets inside this one game; code and agent visual review still do.
- Before committing to generation, briefly consider whether an existing pack or asset already fits. Record the decision only when it will help continued work.
- Register every generated gameplay file per `../../references/asset-sheet.md`.
- When running as a hosted worker, report useful accepted transparent gameplay assets only when the worker material protocol is available. Reporting is best-effort and must never block delivery.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and optional promotional listing media should warn and keep play unblocked; the required new-game identity trio follows `make-listing` and fails clearly.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
