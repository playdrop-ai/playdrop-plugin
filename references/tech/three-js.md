# Three.js

Use the official Three.js template for lightweight 3D games.

- Load Three from `sdk.libs.three.load()`.
- Load GLB/GLTF assets with Three loaders when using 3D packs.
- Normalize loaded models by bounding box and verify the first playable camera frame shows the complete player plus level/arena/board.
- Do not declare a 3D pack while rendering only primitives.
- If required models fail, throw a clear error instead of substituting primitive shapes.
- Keep the primary 3D scene edge-to-edge, not framed in a UI card.

Pack asset pattern:

```js
const assets = await sdk.assets.listAppAssets();
const model = assets.find((asset) => asset.runtimeKey === "player-model")
  ?? assets.find((asset) => asset.sourcePackRef === "pack:playdrop/racing-kit-repack@1.0.1");
const modelFile = model?.files?.find((file) => file.role === "primary" && /^model\/gltf/.test(file.contentType ?? ""));
if (!modelFile?.url) throw new Error("[game] Missing player model asset");
await new GLTFLoader().loadAsync(modelFile.url);
```

For Three.js gameplay structure, consider GameBlocks building blocks from `https://github.com/xt4d/GameBlocks`: camera rigs, vehicle controllers, race checkpoints, grid/path helpers, wave spawners, projectiles, and lightweight HUD helpers. Use them as proven implementation patterns for motion, camera, and world logic; do not add a large dependency when copying a small focused block is enough.
