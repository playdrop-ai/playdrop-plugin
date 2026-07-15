# catalogue.json Reference

Use `catalogue.json` as the upload contract and compact high-level game plan. Keep detailed creative and implementation context in normal project prose when it helps future work:

- `GAME.md`: core loop, rules, scope, progression, controls, and feel.
- `ART_DIRECTION.md`: visual identity, subjects, setting, palette, UI material, lighting, asset needs, and visual no-gos.
- `AGENTS.md`: concise commands, code map, important assets, current validation status, and facts a future agent should preserve.

These files are encouraged working memory, never CLI, API, upload, or phase gates. Preserve existing files and edit them in place instead of replacing creator notes. Do not create them merely to satisfy a checklist.

## Allowed Values

- Template keys: `playdrop/template/html_single_file_template`, `playdrop/template/phaser_2d_template`, `playdrop/template/three_js_template`.
- Surface targets in `catalogue.json`: `desktop`, `mobileLandscape`, `mobilePortrait`.
- `design` is optional. When present, it accepts only the seven optional keys below, each containing one exact APP tag ref from its corresponding group:
  - `genre`: `game-genre`
  - `coreGameplay`: `core-gameplay`
  - `perspective`: `perspective`
  - `controls`: `game-controls`
  - `visualStyle`: `visual-style`
  - `progression`: `game-progression`
  - `feel`: `game-feel`
- Use only current platform tag refs. The CLI and API reject unknown keys, nonexistent tags, and tags from the wrong group with a clear error.
- Browse current values without copying the taxonomy into the plugin: `playdrop tags browse --group <group> --kind APP --json`.

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
          "assets/marketing/playdrop/screenshots/portrait/01-core.png",
          "assets/marketing/playdrop/screenshots/portrait/02-core.png"
        ],
        "screenshotsLandscape": []
      },
      "design": {
        "genre": "game-genre/arcade",
        "coreGameplay": "core-gameplay/fly",
        "perspective": "perspective/2d-side-view",
        "controls": "game-controls/drag",
        "visualStyle": "visual-style/stylized",
        "progression": "game-progression/levels",
        "feel": "game-feel/playful"
      },
      "releaseNotes": "First playable with ring steering, scoring, restart, screenshots, and truthful asset declarations."
    }
  ]
}
```

Rules:

- Every `design` field is optional. Omit `design`, use `{}`, or supply only the primary classifications that are useful and honest.
- Each populated field is one string tag ref, never a `{ "value": ... }`, `{ "values": [...] }`, free-form label, or list. Secondary values may be expressed as normal explicit `tags` until the contract grows secondary fields.
- The platform automatically adds populated design refs to the game's effective tags. You do not need to repeat them in `tags`, but doing so is accepted and deduplicated.
- Clearing a design field removes its derived tag. An explicitly listed copy remains an explicit tag.
- Rich game design and art direction do not belong in extra `design` keys. Use concise project prose when that context is worth retaining.
- Every declared runtime pack or asset must be loaded and rendered or played in the game.
- Listing screenshots are required for new games and live under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/` (production validates these paths; on cloud tasks, copy recorder posters into them per `skills/make-listing`).
- Audio SFX and listing art are non-blocking at runtime (warn, keep play unblocked). Gameplay-required images, sprites, and 3D models should fail loudly if missing.
