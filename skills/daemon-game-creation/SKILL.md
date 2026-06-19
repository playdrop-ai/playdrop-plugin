---
name: daemon-game-creation
description: "Build a fast first playable PlayDrop Cloud game draft from a validated daemon task plan. Use when running inside the PlayDrop Cloud daemon or when a prompt mentions a cloud_game_plan, daemon task, private upload, or playdrop task report/complete."
---

# Daemon Game Creation

Use this skill only for PlayDrop Cloud daemon tasks. The goal is a complete private first playable draft with real gameplay assets and valid PlayDrop listing assets.

## Workflow

1. Read the creator request and the task instructions from the daemon prompt. Treat the creator request as authoritative for gameplay, style, camera, dimensionality, and requested PlayDrop assets.
2. Create the smallest PlayDrop project that proves the requested core loop and target surface without dropping requested mechanics.
3. Report progress with `./bin/playdrop task report --phase <phase> --pct <0-100> -m "<message>"`.
4. Report a catalogue preview as soon as `catalogue.json` describes the intended build.
5. Stop after the project is ready. The worker supervisor validates, uploads, and completes the task.

## Build Rules

- Build core gameplay, controls, HUD, restart, and basic UX.
- Initialize the PlayDrop SDK early, but call `await sdk.host.ready()` only after required runtime assets have loaded and the first playable frame is visibly populated with the board, player, enemies, props, or other primary gameplay objects. Do not call host.ready from a wrapper page before importing game code or before GLB/PNG assets are resolved; the hosted launch check treats ready-plus-blank-canvas as a failed build.
- When the creator requests physics, particles, 3D, an asset pack, or a specific visual subject, implement those as visible runtime features. Do not reduce them to static shapes, text labels, or background decoration.
- Requested mechanics must be reachable in normal play. If the game has hits, physics collisions, particle bursts, combos, pickups, reveals, or attacks, a normal tap/click/key input must visibly trigger that mechanic within the first few seconds. Do not ship impossible collision geometry, offscreen targets, unreachable hitboxes, or timing windows that make the requested mechanic effectively inaccessible.
- Do not add blood, gore, graphic violence, horror intensity, or adult tone unless the creator explicitly asks for it. When a compatible asset pack has darker assets, frame them as playful arcade monsters or hazards unless the creator requested otherwise.
- Default to mobile portrait as the primary surface unless the cloud game plan says otherwise.
- Treat the target surface as the primary surface, not necessarily the only supported surface.
- For mobile portrait primary games, add desktop compatibility when the controls can be mapped simply to mouse, click, space, arrows, or keyboard.
- Desktop compatibility means a larger desktop aspect playfield, desktop controls, and catalogue `surfaceTargets` with `desktop: true` as well as the supported mobile orientation booleans.
- Keep mobile-only only when the game truly depends on phone-only touch, multi-touch, device orientation, or a portrait-only layout that cannot be converted cheaply.
- Use licensed PlayDrop assets whenever the creator asks for PlayDrop assets, PlayDrop packs, or when a matching first-party pack exists. Discover packs with the staged CLI refs from `./bin/playdrop search` or `./bin/playdrop browse`, for example `playdrop/asset-pack/graveyard-kit-repack`. For materially 3D games, start with `./bin/playdrop search --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --json` and choose from those model-compatible first-party packs before doing keyword searches. Pass CLI refs to `./bin/playdrop detail <cli-ref>` and `./bin/playdrop versions browse <cli-ref>`, then copy the exact current version into the catalogue ref. Declare reused packs in `catalogue.json` as `uses.packs` string refs only, for example `"uses": {"packs": ["pack:playdrop/graveyard-kit-repack@5.0.1"]}`. Never guess pack versions or assume `1.0.0`. Do not put objects, `ref`/`runtimeKey` pairs, runtimeKey fields, or local paths inside `uses.packs`. Do not list pack member assets under `uses.assets` to represent that pack; `uses.assets` is only for exact standalone asset refs such as `asset:creator/name@r3`.
- Browse the PlayDrop catalogue with the staged worker CLI: `./bin/playdrop search <query>`, `./bin/playdrop browse`, `./bin/playdrop detail <ref>`, and `./bin/playdrop versions browse <ref>`. Do not rely on a global `playdrop` binary, because login shells may resolve an older CLI. Do not use nonexistent commands such as `./bin/playdrop catalogue search`, and do not run `./bin/playdrop --help` from inside the worker task.
- If no suitable PlayDrop asset exists for a requested primary character, toy, prop, obstacle, or collectible, generate real image assets with the available agent image generation tool or `./bin/playdrop ai create image`.
- For 2D runtime sprites, characters, toys, props, collectibles, particles, and UI-visible gameplay objects, do not declare direct PlayDrop AI JPEG image assets as runtime dependencies. Those catalogue images can have baked backgrounds or checkerboard previews. Use a PlayDrop asset pack when there is a suitable pack; otherwise open/read `.playdrop/plugin/skills/asset-extraction-2d/SKILL.md` and apply that skill to create accepted game-ready owned PNG assets, declare them in `ownedAssets`, and load those owned assets through `sdk.assets`.
- Open/read `.playdrop/plugin/skills/asset-extraction-2d/SKILL.md` before creating generated 2D runtime PNGs, then follow it exactly. That skill is the only source of truth for output shape, transparent PNG extraction, sprite-sheet acceptance, and validation; do not recreate that workflow from memory. For generated gameplay objects, prefer separate owned PNG files by runtimeKey. Do not create a sprite sheet unless the creator explicitly asked for a sprite sheet, tilemap, or frame animation, or the skill says a shared grid is truly required. Small collectible sets such as gems, candies, coins, cards, icons, and pickups should be separate accepted PNG assets by default.
- After creating generated owned runtime PNGs, inspect the extraction contact sheet and report before registering them in `catalogue.json`. If the report rejects the asset, or if the PNG/contact sheet still shows matte-color wash, checkerboard texture, visible grid/cell borders, colored seams, or empty-cell outlines, retry or split the sheet into simpler individual PNG assets. The worker upload validator rejects owned runtime PNGs with those artifacts.
- Do not use emoji, CSS primitives, SVG placeholders, Three.js primitives, or canvas-drawn blobs as the primary visual identity when the request calls for real assets.
- Do not use runtime image assets that visibly contain checkerboard transparency previews, watermarks, asset-card backgrounds, contact sheets, or preview grids. Choose a cleaner PlayDrop asset or create an owned asset through the `asset-extraction-2d` skill workflow.
- Load runtime assets through the PlayDrop SDK manifest. `sdk.assets.resolveAppAsset(runtimeKey)` and `sdk.assets.listAppAssets()` return entries shaped as `{ assetRef, runtimeKey, sourceType, sourcePackRef, files }`; each file is `{ role, url, contentType, sizeBytes, sha256 }`. For `uses.packs`, do not invent a pack runtimeKey; enumerate pack members with `sdk.assets.listAppAssets()` and match by `assetRef`, `sourcePackRef`, `sourceType`, and file metadata.
- PlayDrop runtime asset URLs are API URLs and may not end in `.png`, `.glb`, or `.gltf`. Choose files by `role` and `contentType`, not by URL suffix. For GLB/GLTF, use `model/gltf-binary` or `model/gltf+json` content types.
- Pack manifest entries do not expose `name`, `ref`, `assetName`, `key`, or `currentVersion`. Match pack members with `asset.assetRef`, `asset.sourcePackRef`, `asset.sourceType`, and file metadata.
- If a declared gameplay asset URL is missing or an asset image/model fails to load, throw a clear error and let the task fail. Do not render placeholder or fallback visuals instead.
- For materially 3D games, do not choose an image-only PlayDrop pack as the primary gameplay pack. Start asset-pack discovery with `./bin/playdrop search --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --json`; this is the authoritative shortlist of first-party packs that can expose GLB/GLTF runtime models. Inspect the chosen pack and choose one with `model/gltf-binary` or `model/gltf+json` files for the player, enemies, obstacles, collectibles, board pieces, or other main runtime objects. Do not infer 3D compatibility from pack names, descriptions, release notes, or words like "model" in listing copy; the only acceptable proof is runtime files with contentType `model/gltf-binary` or `model/gltf+json`. Image-only packs may be used only for secondary 2D surfaces such as decals, cards, UI, or billboards when the main 3D objects come from GLB/GLTF assets or owned generated assets.
- For 3D games using PlayDrop 3D packs, load the actual GLB/GLTF assets at runtime with Three.js `GLTFLoader` or an equivalent loader. Do not declare a 3D pack while rendering only primitive geometry.
- For 3D games using requested PlayDrop assets or packs, do not ship emergency, fallback, or placeholder model code that substitutes Three.js primitives when GLB/GLTF assets fail to load. If real PlayDrop models cannot be resolved and rendered, fail with a clear error instead of silently degrading.
- For 3D games, normalize loaded GLB/GLTF models by measured bounding boxes and verify the first playable camera frame shows the complete player plus the track, board, arena, or world at the intended scale. Do not ship a view that is mostly darkness, a clipped/underside view of one giant model, or a scene where requested PlayDrop assets are too small, offscreen, or hidden by primitive geometry.
- For 3D board, grid, puzzle, strategy, minesweeper, tile, arena, or level games, the first playable frame after any Start/Play button must visibly show the populated board, grid, arena, or level and multiple real gameplay models. Do not ship a first playable frame that is mostly empty background, sky, floor, fog, or a single flat ground plane. Covered tiles, player pieces, enemies, flags, pickups, obstacles, or other primary interactive objects must be visible immediately before the user makes a precise move.
- Create final listing hero art for every new game by opening and following `.playdrop/plugin/skills/listing-art/SKILL.md`. Save accepted final hero art under `assets/marketing/playdrop/`. The final portrait and landscape hero art must contain the exact game name front and center as readable title/logo text, and the exact game title must be the only readable text anywhere in the final image. Do not recreate the listing-art workflow from memory; use the staged skill and its title composition script so the exact title is deterministic.
- Do not copy proprietary games, proprietary code, or unlicensed assets.
- Do not read credentials, environment secrets, unrelated files, or task system internals.
- Do not publish publicly. The uploaded app version must stay private.

## Reporting

Use short progress events at real milestones:

```bash
./bin/playdrop task report --phase setup --pct 5 -m "Created project scaffold"
./bin/playdrop task report --phase build --pct 45 -m "Core loop is playable"
./bin/playdrop task report-catalogue --file catalogue.json -m "Planned the first version"
./bin/playdrop task report --phase build --pct 75 -m "Polishing gameplay and listing assets"
```

If the build cannot be completed, exit non-zero with a concise reason. The worker supervisor owns task failure.

## Output Requirements

- The task result is uploaded as a private draft by the worker supervisor.
- The catalogue must declare at least one real gameplay asset through `ownedAssets`, `uses.assets`, or `uses.packs`.
- New games must reference portrait and landscape hero PNG files under `assets/marketing/playdrop/` through `listing.heroPortrait` and `listing.heroLandscape`.
- Do not run `./bin/playdrop project validate`, `./bin/playdrop project publish`, `./bin/playdrop task complete`, or `./bin/playdrop task fail` unless the server prompt explicitly says otherwise. The worker supervisor owns validation, upload, billing, completion, and failure.
