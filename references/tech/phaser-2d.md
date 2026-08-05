# Phaser 2D

Use the official Phaser 2D template when the game needs sprites, tweens, tile-like scenes, collisions, or fast 2D iteration.

- Load Phaser from `sdk.libs.phaser.load()` instead of bundling a separate engine copy.
- Keep the scaffold's scale block exactly as the template ships it (`Phaser.Scale.EXPAND` + `CENTER_BOTH`, base size per primary surface). Never switch to `RESIZE` and never hand-roll viewport fitting with camera zoom or bounds; Phaser keeps pointer input aligned for you.
- Keep controls and dialogs inside Phaser display objects; DOM overlays on the canvas desync from the scaled scene and have caused unclickable games.
- Keep HUD small and safe-area aware.
- Pause the active scene on host pause and resume on host resume.
- For mobile, make the main verb work with one thumb unless the request needs more.
- Use Phaser primitives only as deliberate prototype visuals, not as the final identity for asset-driven requests.

Pack asset pattern:

`sdk.assets.listAppAssets()` returns the asset array directly. `await` is harmless, but never chain `.catch()` on it; use ordinary `try/catch` around the call when needed.

```js
const assets = await sdk.assets.listAppAssets();
const spriteAssetRef = "asset:playdrop/platformer-player-blue@r1"; // Copy from `playdrop detail`.
const sprite = assets.find((asset) => asset.assetRef === spriteAssetRef);
const spriteFile = sprite?.files?.find((file) => file.role === "primary" && file.contentType?.startsWith("image/"));
if (!spriteFile?.url) throw new Error(`[game] Missing player sprite ${spriteAssetRef}`);
this.load.image("player-sprite", spriteFile.url);
```

Pack members have no `runtimeKey`. Never select the first asset matching only `sourcePackRef`; select the intended member by its exact `assetRef`.
