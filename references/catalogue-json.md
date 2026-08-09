# catalogue.json Reference

Use `catalogue.json` as the upload contract and compact high-level game plan. Keep detailed creative and implementation context in normal project prose when it helps future work:

- `GAME.md`: core loop, rules, scope, progression, controls, and feel.
- `ART_DIRECTION.md`: visual identity, subjects, setting, palette, UI material, lighting, asset needs, and visual no-gos.
- `AGENTS.md`: concise commands, code map, important assets, current validation status, and facts a future agent should preserve.

These files are encouraged working memory, never CLI, API, upload, or phase gates. Preserve existing files and edit them in place instead of replacing creator notes. Do not create them merely to satisfy a checklist.

## Allowed Values

- Template keys: `playdrop/template/html_single_file_template`, `playdrop/template/phaser_2d_template`, `playdrop/template/three_js_template`.
- `authMode`: use `NONE` when the game has no account features, `OPTIONAL` when sign-in is offered from an explicit user action, and `REQUIRED` only when the game cannot function without an account, such as a multiplayer-only game.
- Surface targets in `catalogue.json`: `desktop`, `mobileLandscape`, `mobilePortrait`.
- `primarySurface`: `DESKTOP`, `MOBILE_LANDSCAPE`, or `MOBILE_PORTRAIT`. It must also be enabled in `surfaceTargets`.
- `playtestTapes`: the only scripted-input contract, with one version-1 tape keyed by uppercase surface for every enabled surface. Each tape declares `primaryVerb` as `tap`, `swipe`, `drag`, or `key`. Event `type` must be exactly `tap`, `pointerDown`, `pointerMove`, `pointerUp`, `keyDown`, or `keyUp`. Represent a swipe or drag with a complete `pointerDown` → `pointerMove` → `pointerUp` sequence. Keyboard events are desktop-only.
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
- `tweaks` is optional and declares one flat creator-tunable document. It requires `basedOn`, `schema`, and complete `defaults`. Supported field types are `number`, `string`, `boolean`, and string `enum`. Use `basedOn: null` only when the previous version has no tweak state. To intentionally remove an existing tweak declaration, use `{ "basedOn": "twk_...", "removed": true }` without `schema` or `defaults`.

## Copy-Paste Shape

Replace names, refs, paths, and notes. Keep the shape.

```json
{
  "apps": [
    {
      "name": "sky-orchard-glider",
      "version": "1.0.0",
      "displayName": "Sky Orchard Glider",
      "description": "Thread a nimble glider through shifting orchard wind rings, collect orchard stars, and master precise one-thumb landings before the storm closes in.",
      "type": "GAME",
      "authMode": "OPTIONAL",
      "controllerMode": "UNSUPPORTED",
      "previewable": true,
      "editorSupported": false,
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
        "heroLandscape": "assets/marketing/playdrop/hero/hero-landscape.png"
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
      "releaseNotes": "First playable with ring steering, scoring, restart, preview mode, and identity art."
    }
  ]
}
```

Rules:

- `releaseNotes` must contain one line with 1 to 240 characters.
- Game descriptions should be at least 20 words and about 120 characters, covering the player's action, objective, and distinctive hook. Short descriptions produce a CLI warning only and never block checks or upload.
- Each screenshot and video entry may remain a path string or use a structured object. Structured objects require `path` and may add `slug`, `title`, `alt`, `caption`, and `description`. Use lowercase hyphenated slugs. `alt` is primarily for screenshots; `description` is primarily for videos.
- A structured media `slug` becomes the filename in the published listing URL. Keep it stable after publication and unique within its orientation array.
- New games set `primarySurface` inside the app entry to exactly one enabled surface: `DESKTOP`, `MOBILE_LANDSCAPE`, or `MOBILE_PORTRAIT`. Existing catalogue content may omit it until updated.
- New games provide exactly one `playtestTapes` entry for every enabled surface. Each tape declares `primaryVerb` as `tap`, `swipe`, `drag`, or `key`, and must demonstrate that verb at least once after startup; secondary controls are allowed. Event `type` must be exactly `tap`, `pointerDown`, `pointerMove`, `pointerUp`, `keyDown`, or `keyUp`; a swipe or drag is a complete pointer-down, move, and up sequence. Use normalized `x` and `y` coordinates from `0` to `1`, ordered millisecond timestamps, at least one success signal, and no pointer or key left down. Keyboard events are valid only in `DESKTOP` tapes. When a game has a title screen, put its complete start action first and set `startOnlyEventCount` to the number of startup events so later reviewers can distinguish startup from gameplay; otherwise it may be `0`. The startup prefix must not leave a pointer or key held. Existing catalogue content may omit tapes until updated.
- Aim for about 10 seconds and 3 to 6 representative gameplay actions, plus a start action when needed. Highlight the core gameplay and declared primary verb. These are recommendations, not validation limits.
- Run the deterministic check in `skills/playtest-game` for every enabled surface before upload.
- Every `design` field is optional. Omit `design`, use `{}`, or supply only the primary classifications that are useful and honest.
- Each populated field is one string tag ref, never a `{ "value": ... }`, `{ "values": [...] }`, free-form label, or list. Secondary values may be expressed as normal explicit `tags` until the contract grows secondary fields.
- The platform automatically adds populated design refs to the game's effective tags. You do not need to repeat them in `tags`, but doing so is accepted and deduplicated.
- Clearing a design field removes its derived tag. An explicitly listed copy remains an explicit tag.
- Rich game design and art direction do not belong in extra `design` keys. Use concise project prose when that context is worth retaining.
- Every declared runtime pack or asset must be loaded and rendered or played in the game.
- A Cloud `NEW_GAME` requires `listing.icon`, `listing.heroPortrait`, and `listing.heroLandscape`. Keep the database fields optional for legacy and direct-publish compatibility.
- Screenshots, videos, social packages, and capture reports are optional. Do not create them unless the creator requests them or the task specifically changes existing media.
- `editorSupported` is optional and defaults to `false`. Set it to `true` only when a hosted game boots a focused owner-only Editor and calls `sdk.host.editorReady()` after that UI mounts. External apps cannot enable it.
- For updates that do not request listing changes, keep the existing listing fields and files unchanged.
- When present, final screenshot arrays contain AI-generated marketing artwork from `skills/make-marketing-screenshots`, never recorder posters or raw gameplay captures.
- Listing video is literal gameplay footage. Keep recorder posters in the capture directory as source evidence and image-generation references. Reference requested video through `listing.videosPortrait` or `listing.videosLandscape`. A native `listing.captureReport` is optional and is not a completion requirement.
- Audio SFX and listing art are non-blocking at runtime (warn, keep play unblocked). Gameplay-required images, sprites, and 3D models should fail loudly if missing.
