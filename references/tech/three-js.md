# Three.js

Use the official Three.js template for lightweight 3D games.

- Load Three from `sdk.libs.three.load()`.
- Load GLB/GLTF assets with Three loaders when using 3D packs.
- Normalize loaded models by bounding box and verify the first playable camera frame shows the complete player plus level/arena/board.
- Do not declare a 3D pack while rendering only primitives.
- If required models fail, throw a clear error instead of substituting primitive shapes.
- Keep the primary 3D scene edge-to-edge, not framed in a UI card.
