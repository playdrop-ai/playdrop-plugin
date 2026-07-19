# Three.js

Use the official Three.js template for lightweight 3D games. Search PlayDrop for a relevant existing game first, use a relevant local GameBlock second, and scaffold from the template when neither provides a stronger start.

## Runtime and assets

- Load Three from `sdk.libs.three.load()`.
- Load GLB or GLTF assets with Three loaders when using 3D packs.
- Normalize loaded models by bounding box, then verify the first playable camera frame shows the complete player and immediate objective.
- Do not declare a 3D pack while rendering only primitives.
- Throw a clear error when a required model fails. Do not substitute primitive geometry.
- Keep the scene edge-to-edge. Apply safe areas to HUD placement, not to the renderer canvas.

Pack asset pattern:

```js
const assets = await sdk.assets.listAppAssets();
const model = assets.find((asset) => asset.runtimeKey === "player-model")
  ?? assets.find((asset) => asset.sourcePackRef === "pack:playdrop/racing-kit-repack@1.0.1");
const modelFile = model?.files?.find((file) => file.role === "primary" && /^model\/gltf/.test(file.contentType ?? ""));
if (!modelFile?.url) throw new Error("[game] Missing player model asset");
await new GLTFLoader().loadAsync(modelFile.url);
```

## Coordinate and camera contract

Choose one right, up, and forward world basis before implementing movement, physics, or camera behavior. Keep input, simulation, models, and cameras on that basis.

Design the camera and controls together for the primary surface. Frame the player and immediate objective, not the player alone. Recompute aspect and projection on every resize, then prove the important play area remains visible at the primary surface dimensions. For side-on gameplay, keep the play plane fixed and use an orthographic or fixed-azimuth perspective camera that cannot reveal or hide targets through depth drift.

The official Three.js template includes `src/side-on-camera-rig.ts`. Pass the controlled entity and immediate objective together to `frameObjects(...)`; copy the local GameBlocks follow-camera patterns only when the camera must move through the world.

Use the pinned local blocks in `three-js-gameblocks/INDEX.md` when a camera or gameplay helper fits. Adapt their source to the Three instance returned by the SDK instead of importing the full library or adding another Three package.

## Input and update order

Pointer, touch, and keyboard handlers update an input-intent object only. They do not mutate physics or game state directly. Normalize pointer coordinates against the current renderer bounds and use pointer capture for drags.

Use this order every frame:

1. Clamp elapsed frame time and accumulate it.
2. Consume input intent in fixed simulation steps.
3. Step physics and game rules.
4. Synchronize rendered objects from simulation state.
5. Update the camera after its target has moved.
6. Update the HUD from the resulting game state.
7. Render once.

Use a fixed timestep such as `1 / 60`, cap catch-up work, and never tie gameplay speed to render frame rate. Keep random state seeded when repeatable playtests or restarts matter.

## Physics selection

Use simple overlap, ray, or analytic collision checks when they fully express the mechanic. Load Rapier from `sdk.libs.rapier.load()` when the game needs rigid-body contacts, impulses, joints, stacks, rolling, or destruction. Follow `rapier.md` when selected.

Prefer simple colliders that match gameplay over detailed mesh colliders. Enable continuous collision detection for small fast bodies such as launched projectiles. Step Rapier at the fixed timestep and synchronize meshes after the physics step.

## Mobile rendering

- Cap renderer pixel ratio for performance even when the emulated device DPR is higher.
- Set renderer output color space deliberately and use a small mobile-safe light rig with visible fill plus one directional key when using standard materials.
- Resize from the actual canvas container, update the camera projection, and keep touch actions disabled on the canvas.
- Test the primary mobile dimensions with touch enabled. A desktop window narrowed by hand is not equivalent.

## Restart and cleanup

Restart from one explicit clean-state function. Reset timers, input intent, random state, game rules, physics bodies, camera state, HUD, and audio together.

Cancel animation frames and remove listeners when tearing down. Dispose owned geometry, materials, textures, render targets, mixers, and the renderer. The local `Object3DUtils` helper covers geometry and materials only; dispose owned texture maps separately.

## Playtest signals

Make progress, score change, failure, retry, and softlock absence visible through ordinary gameplay. Compare normal input against a zero-input or opposite-input control. Do not use state-forcing hooks as proof.
