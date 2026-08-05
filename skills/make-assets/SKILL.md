---
name: make-assets
description: "Choose, create, and declare PlayDrop gameplay assets with the PlayDrop asset preference order."
---

# Make Assets

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Create assets when they best support the game. For risky mechanics, an optional early playable check can avoid polishing the wrong interaction; familiar or visually led games may benefit from earlier art.

For every generated gameplay image that requires a transparent background, use the staged `make-2d-asset-pack` skill, even for one sprite. It owns controlled-matte generation, extraction, and alpha validation because image providers do not reliably return structural transparency. Also use it for coherent packs, multiple families or sheets, paired size variants, and approval rounds. Return here after extraction and review to declare the accepted files in the game.

## Sourcing And Image Generation Order

Before generating an image, prefer a PlayDrop pack or exact asset that already matches the style and runtime need, then a suitable CC0 web asset that can be converted and attributed correctly. Bespoke identity art usually needs generation instead.

When generating any image, first check whether the `codex` CLI is available, including when the active agent is Claude. Then use these plans in order:

1. **Plan A: Codex CLI image generation.** When Codex CLI is available, ask it to generate the image with Terra at high reasoning. Run `codex exec --ephemeral --skip-git-repo-check --model gpt-5.6-terra --config 'model_reasoning_effort="high"' --sandbox workspace-write --cd <workspace> --image <path> -- "<image request>"` when attaching a visual reference, or omit `--image <path> --` when there is no reference. The `--` before the prompt is required because `--image` accepts multiple paths. Tell Codex to use its built-in image-generation tool, name the exact absolute output path, and forbid unrelated file changes. Repeat `--image <path>` before `--` for each useful visual reference. Make one corrected retry when appropriate.
2. **Plan B: agent-native image generation.** When Codex CLI is unavailable or still fails, use the current agent's built-in image-generation tool when it supports the requested image type. Make one corrected retry when the first result or provider call fails.
3. **Plan C: PlayDrop CLI AI generation.** When Plan B is unavailable or still fails, use `playdrop ai create ...` and follow the matching command help.

Use this generation order for hero art, optional direction artifacts, gameplay assets, backgrounds, listing art, and promotional images. Audio generation keeps the same source preference but uses the available audio-specific tools. When an approved identity reference exists, pass it to related generations when that improves consistency. Built-in tools and Codex CLI may save generated files outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`); copy the accepted file into the exact workspace target, verify it with `file`, and inspect it before use.

Media failure policy: after all three plans fail, do not invent another generation route. For direct creator game work, record the reason, deliberately reduce the asset scope or use honestly designed owned vector/canvas assets, and surface "add credits to regenerate art" as a creator next step. In a PlayDrop Cloud game task, required listing media must fail clearly after the documented attempts instead of continuing toward an upload that will reject it. Optional art-direction media may be skipped, and gameplay-required media must follow the clear-failure rule below.

## Rules

- Declare reused packs in `uses.packs` as exact version refs such as `pack:playdrop/forest-kit@1.0.0`.
- If the game needs only a small subset of a pack, declare those exact asset version refs in `uses.assets` instead of the whole pack.
- Declare a whole pack only when the runtime genuinely uses the pack. Never add a pack merely to satisfy validation or an asset-use requirement.
- For 3D, prove selected assets expose GLB/GLTF runtime files before choosing them.
- Temporary primitives and plain shapes are useful when a rough playable will reduce risk, but replace them before upload unless the game is deliberately abstract.
- Use a real background when the game benefits from one; `../../references/art-direction-board.md` describes useful treatments.
- For a small set of game-owned foreground assets, use one `make-2d-asset-pack` family with one slot per asset. Never ask an image provider for a transparent background, ship a painted checkerboard, or write an ad hoc background-removal script. Request the workflow's controlled matte, extract it, validate every silhouette, and keep one transparent PNG per accepted asset. The standalone pack publication human gate does not apply when the files remain owned assets inside this one game; code and agent visual review still do.
- Before committing to generation, briefly consider whether an existing pack or asset already fits. Record the decision only when it will help continued work.
- Register every generated gameplay file per `../../references/asset-sheet.md`.
- When running as a hosted worker, report useful accepted transparent gameplay assets only when the worker material protocol is available. Reporting is best-effort and must never block delivery.
- Gameplay-required images, sprites, and models must fail clearly if missing. Audio SFX and listing-only assets should warn and keep play unblocked.
- If a declared pack or asset is not loaded and rendered or played at runtime, remove the declaration or fix the runtime.
- Keep the visual set coherent. A small matching set beats a large mismatched set.
