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

Known current refs can change. Always confirm with `detail` or `versions browse` before writing `uses.packs`.

## Design Rule

At design time, choose one of:

- `assetStrategy: "pack-first"` when a medium-matched pack supplies the core entities.
- `assetStrategy: "mixed"` when a pack supplies the world or entities and you add a few owned assets.
- `assetStrategy: "owned-assets"` when no suitable pack exists but you have a small coherent owned set.
- `assetStrategy: "procedural"` when simple procedural visuals are the honest scope call.

Do not declare a pack just to satisfy metadata. If it is in `uses.packs`, the game must load and render assets from it at runtime.
