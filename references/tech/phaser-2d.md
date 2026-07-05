# Phaser 2D

Use the official Phaser 2D template when the game needs sprites, tweens, tile-like scenes, collisions, or fast 2D iteration.

- Load Phaser from `sdk.libs.phaser.load()` instead of bundling a separate engine copy.
- Use `Phaser.Scale.RESIZE` and an edge-to-edge parent.
- Keep HUD small and safe-area aware.
- Pause the active scene on host pause and resume on host resume.
- For mobile, make the main verb work with one thumb unless the request needs more.
- Use Phaser primitives only as deliberate prototype visuals, not as the final identity for asset-driven requests.
