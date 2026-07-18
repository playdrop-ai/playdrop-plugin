---
name: three-js-game
description: "Build the 3D implementation of a PlayDrop game after the create-game workflow has explicitly selected the Three.js engine. Use for spatial 3D rendering, 3D cameras, 3D assets, or 3D physics. Do not use for Phaser 2D games."
---

# Three.js Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this only after `create-game` records `three-js` as the engine decision. Do not load the Phaser engine skill for the same game.

Before searching or scaffolding, do these actions now:

1. Read and follow `../../references/tech/three-js.md` completely.
2. Read `../../references/tech/three-js-gameblocks/INDEX.md` and choose the smallest relevant local block set, or record why no listed block fits. Inspect only the selected local files.
3. When the mechanic needs rigid-body contacts, impulses, joints, stacks, rolling, launching, or destruction, read `../../references/tech/rapier.md` completely.
4. Record the template, GameBlocks, and physics choice in the existing engine-decision progress report or working notes, then continue directly with the normal creation flow.

Do not browse for engine guidance or GameBlocks during the task. Use the vendored local references.
