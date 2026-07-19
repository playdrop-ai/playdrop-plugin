# catalogue.json Reference

Use `catalogue.json` as the upload contract and compact high-level game plan. Keep detailed creative and implementation context in normal project prose when it helps future work:

- `GAME.md`: core loop, rules, scope, progression, controls, and feel.
- `ART_DIRECTION.md`: visual identity, subjects, setting, palette, UI material, lighting, asset needs, and visual no-gos.
- `AGENTS.md`: concise commands, code map, important assets, current validation status, and facts a future agent should preserve.

These files are encouraged working memory, never CLI, API, upload, or phase gates. Preserve existing files and edit them in place instead of replacing creator notes. Do not create them merely to satisfy a checklist.

## Allowed Values

- Template keys: `playdrop/template/html_single_file_template`, `playdrop/template/phaser_2d_template`, `playdrop/template/three_js_template`.
- Surface targets in `catalogue.json`: `desktop`, `mobileLandscape`, `mobilePortrait`.
- `primarySurface`: `DESKTOP`, `MOBILE_LANDSCAPE`, or `MOBILE_PORTRAIT`. It must also be enabled in `surfaceTargets`.
- `playtestTapes`: one version-1 tape keyed by uppercase surface for every enabled surface. Each tape declares `primaryVerb` as `tap`, `swipe`, `drag`, or `key`. Mobile tapes use pointer or tap events. Desktop tapes may also use key events.
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
      "primarySurface": "MOBILE_PORTRAIT",
      "playtestTapes": {
        "MOBILE_PORTRAIT": {
          "version": 1,
          "primaryVerb": "tap",
          "durationMs": 5000,
          "startOnlyEventCount": 1,
          "successSignals": [
            {
              "kind": "VISIBLE_PROGRESS",
              "description": "The glider visibly clears the first wind ring while idle does not."
            }
          ],
          "events": [
            { "type": "tap", "atMs": 0, "x": 0.5, "y": 0.5, "durationMs": 80 },
            { "type": "tap", "atMs": 500, "x": 0.75, "y": 0.65, "durationMs": 80 },
            { "type": "tap", "atMs": 1800, "x": 0.25, "y": 0.65, "durationMs": 80 }
          ]
        }
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

- New games set top-level `primarySurface` to exactly one enabled surface: `DESKTOP`, `MOBILE_LANDSCAPE`, or `MOBILE_PORTRAIT`. Existing catalogue content may omit it until updated.
- New games provide exactly one `playtestTapes` entry for every enabled surface. Each tape declares `primaryVerb` as `tap`, `swipe`, `drag`, or `key`; all post-start events must use that family. The game must visibly teach the same verb. Use normalized `x` and `y` coordinates from `0` to `1`, ordered millisecond timestamps, at least one success signal, and a complete input sequence with no pointer or key left down. `startOnlyEventCount` must include an explicit startup action, the first startup event must use `atMs: 0`, and the startup prefix must leave no pointer or key down. Keyboard events are valid only in `DESKTOP` tapes. Existing catalogue content may omit tapes until updated.
- A tape is evidence only when its full run meaningfully beats matched zero-input and start-only runs by surviving longer, scoring above zero and above both controls, making visible progress, or reaching a state neither control reaches. Run `playdrop project check . --tape <surface>` for every enabled surface and inspect all three captures before upload.
- Every `design` field is optional. Omit `design`, use `{}`, or supply only the primary classifications that are useful and honest.
- Each populated field is one string tag ref, never a `{ "value": ... }`, `{ "values": [...] }`, free-form label, or list. Secondary values may be expressed as normal explicit `tags` until the contract grows secondary fields.
- The platform automatically adds populated design refs to the game's effective tags. You do not need to repeat them in `tags`, but doing so is accepted and deduplicated.
- Clearing a design field removes its derived tag. An explicitly listed copy remains an explicit tag.
- Rich game design and art direction do not belong in extra `design` keys. Use concise project prose when that context is worth retaining.
- Every declared runtime pack or asset must be loaded and rendered or played in the game.
- Listing screenshots are required for new games and live under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/` (production validates these paths; on cloud tasks, copy recorder posters into them per `skills/make-listing`).
- Audio SFX and listing art are non-blocking at runtime (warn, keep play unblocked). Gameplay-required images, sprites, and 3D models should fail loudly if missing.
