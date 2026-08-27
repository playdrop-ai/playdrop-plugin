# Asset Pack Index

Search before choosing to make assets. Use medium filters so the result is usable in the selected engine.

## Commands

2D or sprite games:

```sh
playdrop search "<genre or theme>" --kind asset-pack --creator playdrop --pack-contains-category IMAGE --limit 10
```

3D games:

```sh
playdrop search "<genre or theme>" --kind asset-pack --creator playdrop --pack-contains-category MODEL_3D --limit 10
```

Procedural Three.js assets and packs:

```sh
playdrop search "<object, effect, or character>" --kind asset --creator playdrop --asset-category MODEL_3D --asset-subcategory procedural --limit 10
playdrop search "<object, effect, or character>" --kind asset-pack --creator playdrop --pack-contains-subcategory procedural --limit 10
```

Inspect a candidate before copying its ref:

```sh
playdrop detail playdrop/asset-pack/<pack-name>
playdrop versions browse playdrop/asset-pack/<pack-name> --json
```

## Starting Points

- Platformer or side-view arcade: `platformer-art-deluxe`, 2D IMAGE pack, seed catalogue says about 930 assets.
- Top-down city, courier, grid, or roguelike: `roguelike-modern-city`, 2D IMAGE pack, seed catalogue says about 1036 assets.
- Robot, factory, courier, or sci-fi entity set: `robot-pack` or `robot-pack-repack`, 2D IMAGE pack, seed catalogue says about 50 assets.
- Racing or vehicle games: `racing-kit` or `racing-kit-repack`, 3D MODEL_3D pack, seed catalogue says about 110 assets.
- Tower defense or wave defense: `tower-defense-kit` or `tower-defense-kit-repack`, 3D MODEL_3D pack, seed catalogue says about 160 assets.
- Configurable weapons and handheld props: `procedural-handheld`, procedural Three.js pack with typed controls, named parts, and sockets.

Known current refs can change. Always confirm with `detail` or `versions browse` before writing `uses.packs`.

## Asset Plan

At design time, make one honest scope call:

- Use a medium-matched pack when it supplies the core entities.
- Mix a pack with a few owned assets when it supplies only part of the visual set.
- Use a small coherent owned set when no suitable pack exists.
- Use hand-authored primitive geometry only when a deliberately abstract prototype is the honest scope call. Catalogue procedural Three.js assets are finished reusable assets, not prototype primitives.

Record the choice only when it will help continued work. Do not declare a pack just to satisfy metadata. If it is in `uses.packs`, the game must load and render assets from it at runtime.
