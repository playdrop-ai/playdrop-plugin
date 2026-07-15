# catalogue.json Reference

Use `catalogue.json` as the only design and metadata source of truth. Do not create GDD, PLAN, README-like task notes, or other metadata files for game design decisions.

## Allowed Values

- Template keys: `playdrop/template/html_single_file_template`, `playdrop/template/phaser_2d_template`, `playdrop/template/three_js_template`.
- Surface targets in `catalogue.json`: `desktop`, `mobileLandscape`, `mobilePortrait`.
- Design `render`: `2d`, `3d`.
- Design `engine`: `plain-html`, `phaser-2d`, `three-js`.
- Design `assetStrategy`: `pack-first`, `owned-assets`, `mixed`, `procedural`.
- Design `camera`: `top-down`, `side`, `isometric`, `third-person`, `first-person`, `fixed-screen`.
- Design `input`: `one-thumb`, `tap`, `drag`, `keyboard`, `pointer`, `virtual-stick`, `gamepad`.
- Design `progression`: `endless`, `levels`, `waves`, `rounds`, `story`.

## Copy-Paste Shape

Replace names, refs, paths, and notes. Keep the shape.

```json
{
  "apps": [
    {
      "name": "sky-orchard-glider",
      "version": "1.0.0",
      "displayName": "Sky Orchard Glider",
      "description": "A one-thumb glider game about threading orchard wind rings and landing safely.",
      "type": "GAME",
      "authMode": "REQUIRED",
      "controllerMode": "UNSUPPORTED",
      "previewable": true,
      "file": "dist/index.html",
      "surfaceTargets": {
        "desktop": false,
        "mobileLandscape": false,
        "mobilePortrait": true
      },
      "uses": {
        "packs": [
          "pack:playdrop/platformer-art-deluxe-repack@1.0.0"
        ],
        "assets": [
          {
            "ref": "asset:playdrop/wind-chime-sfx@r1",
            "runtimeKey": "sfx-wind-chime"
          }
        ]
      },
      "ownedAssets": [
        {
          "name": "glider-sprite",
          "runtimeKey": "player-glider",
          "displayName": "Player Glider Sprite",
          "description": "Runtime player sprite used in the game.",
          "category": "IMAGE",
          "subcategory": "generic",
          "format": "PNG",
          "files": {
            "primary": "assets/sprites/player-glider.png"
          },
          "license": "PLAYDROP"
        },
        {
          "name": "boost-sfx",
          "runtimeKey": "sfx-boost",
          "displayName": "Boost SFX",
          "description": "Optional tap feedback sound. Missing audio must not block boot.",
          "category": "AUDIO",
          "subcategory": "sfx",
          "format": "MP3",
          "files": {
            "primary": "assets/audio/boost.mp3"
          },
          "license": "PLAYDROP"
        },
        {
          "name": "listing-hero-source",
          "runtimeKey": "listing-hero-source",
          "displayName": "Listing Hero Source",
          "description": "Reusable source image for listing art, not gameplay-critical.",
          "category": "IMAGE",
          "subcategory": "generic",
          "format": "PNG",
          "files": {
            "primary": "assets/marketing/playdrop/hero/hero-landscape.png"
          },
          "license": "PLAYDROP"
        }
      ],
      "listing": {
        "icon": "assets/marketing/playdrop/icon.png",
        "heroPortrait": "assets/marketing/playdrop/hero/hero-portrait.png",
        "heroLandscape": "assets/marketing/playdrop/hero/hero-landscape.png",
        "screenshotsPortrait": [
          "assets/marketing/playdrop/screenshots/portrait/01-start.png",
          "assets/marketing/playdrop/screenshots/portrait/02-core.png"
        ],
        "screenshotsLandscape": []
      },
      "design": {
        "genre": { "value": "arcade flight" },
        "coreGameplay": { "value": "steer through rings, collect fruit, land before stamina runs out" },
        "render": { "value": "2d" },
        "camera": { "value": "side" },
        "input": { "values": ["one-thumb", "tap", "drag"] },
        "progression": { "value": "levels" },
        "artStyle": { "value": "bright orchard cartoon" },
        "fantasy": { "value": "glide a fruit-orchard courier between floating sky islands" },
        "mascot": { "value": "round teal glider-fox", "note": "Locked traits: teal scarf, brass goggles, cream belly." },
        "setting": { "value": "sunny floating orchards, late afternoon light" },
        "palette": { "values": ["#F4A93B amber", "#2E8C6A orchard green", "#7FD1E8 sky blue", "#4A3325 bark"] },
        "uiMaterial": { "value": "rounded wooden panels, soft shadows, chunky friendly type" },
        "assetStrategy": { "value": "mixed", "note": "Pack art for scenery, one owned player sprite, optional SFX." },
        "engine": { "value": "phaser-2d" },
        "coreAssets": { "values": ["pack:playdrop/platformer-art-deluxe-repack@1.0.0"] },
        "features": { "values": ["achievements"] },
        "references": { "values": ["playdrop/template/phaser_2d_template"] }
      },
      "releaseNotes": "First playable with ring steering, scoring, restart, screenshots, and truthful asset declarations."
    }
  ]
}
```

Rules:

- `design.coreAssets.values` must be a subset of `uses.packs`.
- The art-direction concept block lives in `design.fantasy`, `design.mascot`, `design.setting`, `design.palette`, and `design.uiMaterial`, written at the start of the art-direction phase (see `references/art-direction-board.md`).
- `assetStrategy: "procedural"` is allowed only when you deliberately render procedural visuals and do not declare fake packs/assets.
- Every declared runtime pack or asset must be loaded and rendered or played in the game.
- Listing screenshots are required for new games. Put them under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/`.
- Audio SFX and listing art are non-blocking assets. Gameplay-required images, sprites, and 3D models should fail loudly if missing.
