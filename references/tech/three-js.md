# Three.js

Use the official Three.js template for lightweight 3D games. Prefer a relevant local GameBlock over bespoke systems when one fits; remixing a strong existing PlayDrop game is a separate decision made in `create-game`.

## Runtime and assets

- Load Three from `sdk.libs.three.load()`. Request GLTF support with
  `sdk.libs.three.load({ addons: ["loaders/GLTFLoader.js"] })`, then construct `new THREE.GLTFLoader()`.
- Load GLB or GLTF assets with Three loaders when using 3D packs.
- Normalize loaded models by bounding box, then verify the first playable camera frame shows the complete player and immediate objective.
- Do not declare a 3D pack while rendering only primitives.
- Throw a clear error when a required model fails. Do not substitute primitive geometry.
- Keep the scene edge-to-edge. Apply safe areas to HUD placement, not to the renderer canvas.
- When replacing `template.html`, preserve explicit `width: 100%` and `height: 100%` canvas CSS. The template calls
  `renderer.setSize(width, height, false)`, which deliberately leaves CSS sizing to the page.

Pack asset pattern:

`sdk.assets.listAppAssets()` returns the asset array directly. `await` is harmless, but never chain `.catch()` on it; use ordinary `try/catch` around the call when needed.

```js
const assets = await sdk.assets.listAppAssets();
const modelAssetRef = "asset:playdrop/racing-car-red@r2"; // Copy from `playdrop detail`.
const model = assets.find((asset) => asset.assetRef === modelAssetRef);
const modelFile = model?.files?.find((file) => file.role === "primary" && /^model\/gltf/.test(file.contentType ?? ""));
if (!modelFile?.url) throw new Error(`[game] Missing player model ${modelAssetRef}`);
await new GLTFLoader().loadAsync(modelFile.url);
```

Pack members have no `runtimeKey`. Never select the first asset matching only `sourcePackRef`; select the intended member by its exact `assetRef`.

## Procedural Three.js assets

Procedural assets are reusable `MODEL_3D` assets with subcategory `procedural` and format `CUSTOM`. They can expose typed controls, named parts and sockets, a timeline of animations, and a character rig. Prefer one when those capabilities fit instead of rebuilding the same configurable geometry or behavior inside the game.

Search for a suitable exact asset or pack, inspect it, then download its immutable source into the project:

```sh
playdrop search "<object, effect, or character>" --kind asset --asset-category MODEL_3D --asset-subcategory procedural --limit 10
playdrop asset source asset:<creator>/<name>@r<revision> <directory>
```

Import the downloaded local TypeScript entry and bundle it with the game. Keep its `playdrop-publication.json` provenance file. Games never dynamically import executable catalogue URLs. A procedural module creates one Three.js object and may expose `controls`, `selection`, `timeline`, and `character` capabilities. Add its object to the scene, call `update` when present, and call its idempotent `dispose` during teardown.

When creators or players need persistent variations, pair the shared procedural runtime with a typed custom asset rather than copying the runtime. The custom document should contain the exact procedural asset revision and validated parameter values. `asset-spec:playdrop/procedural-config` is the standard generic form:

```json
{
  "proceduralAsset": "asset:playdrop/pack-arming-sword@r1",
  "parameters": {
    "bladeLength": 1.1,
    "accentColor": "#2ec5eb"
  }
}
```

Declare the matching `assetSpecSupport` entry and only the capabilities the game actually uses. Load the document through `sdk.assets.custom.forSpec("asset-spec:playdrop/procedural-config")`, then pass its parameters to the already bundled exact procedural module. Custom data is persistent configuration, not executable code.

## Procedural avatars

PlayDrop avatars use the same composition: `sdk.libs.avatar` supplies one extensible procedural humanoid runtime with shared geometry, male and female templates, a 29-bone rig, sockets, and core, sword, rifle, and soccer animations. An exact `asset-spec:playdrop/avatar-skin` custom asset supplies the compact appearance and PBR materials. Declare read support for that asset-spec family in `catalogue.json`.

```js
const skinFamily = sdk.assets.custom.forSpec("asset-spec:playdrop/avatar-skin");
const skinBlob = await skinFamily.downloadFile({ assetRef: exactSkinRef, role: "primary" });
const avatarRuntime = await sdk.libs.avatar.load();
const avatar = await avatarRuntime.createAvatarFromSkinBlob(skinBlob, {
  renderMode: "voxel",
  joints: "on",
});
scene.add(avatar.object);
avatar.capabilities.timeline?.play("core_idle");
```

Use `renderMode: "voxel"` when outer-layer depth matters. Use `renderMode: "box"` for crowds or distance rendering, and disable optional joints when that tradeoff fits. Inspect `avatar.capabilities.timeline.animations` before choosing an animation, attach props through named sockets, call `avatar.update(...)` each frame, and dispose the instance during teardown. Do not copy the avatar geometry, rig, animations, or decoder into the game, and do not use legacy Boxel avatar code.

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
