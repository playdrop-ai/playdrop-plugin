---
name: make-listing
description: "Create PlayDrop listing assets and metadata that match the real game and upload cleanly."
---

# Make Listing

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Begin listing work when it is efficient for the game. Early identity art can guide production; final screenshots and video must come from the finished runtime.

## Required For New Games

- App icon PNG when available.
- Portrait and landscape hero PNG.
- Screenshots for supported surfaces.
- Accurate title, description, tags, surfaces, `previewable`, `uses`, and any populated optional `design` refs in `catalogue.json`.

## Rules

- When art-direction heroes exist, use them as references for final hero art and refine them against real screenshots and runtime assets. Otherwise derive truthful heroes from the finished game. Save final PNGs under `assets/marketing/playdrop/` and reference them via `listing.heroPortrait` / `listing.heroLandscape` (the CLI preflight enforces this path; each hero and screenshot max 2 MB, icon max 512 KB). Never use a mockup board, or any crop of one, as hero art.
- App icon is optional. When provided, it must be a square 1:1 PNG; generate it at 512x512 when possible. Create it as a separate composition using the hero art as a reference: identity subject close up, bold silhouette readable at small sizes, flat background from the palette, no text. Never copy, crop, resize, or reuse the hero image as the app icon.
- Hero art may be more polished than gameplay, but it must depict the actual game fantasy and key entities.
- For icon art, or hero art when the art-direction hero files are missing (older games), prefer built-in agent image generation (copy the produced file from the generator's output directory, for Codex `$CODEX_HOME/generated_images`, into the workspace and verify with `file`). If native generation is unavailable or failed after one retry, use PlayDrop CLI AI generation. Media failure policy: `../make-assets/SKILL.md`.
- When a local image inspection or transform needs Python, use `$HOME/.cache/playdrop/make-2d-asset-pack/venv-v1/bin/python`. The standard creator worker runtime already includes Pillow there. Never install Pillow or create another Python environment during a game task; fail clearly with `creator_image_runtime_missing` if that path is unavailable.
- Do not use misleading stock-like art, raw screenshots as hero art, or title text that gets clipped in common listing crops.
- Primary gameplay screenshots show active core play with the primary interactive entities visible (the player-controlled entity when one exists), never a game-over, pause, or menu overlay.
- Inspect every capture yourself: it must contain only the game canvas, no browser chrome or surrounding page. A clean capture report does not replace looking.
- Store listing work is not optional polish; it is part of the shipped draft.
- macOS PlayDrop Cloud and Local Agent worker tasks: final listing media must come from the native recorder and include `listing.captureReport` (the FIRST_PARTY task context enforces this).
- Windows Local Agent and other direct-creator tasks: do not run `playdrop project capture` from the worker, and omit `listing.captureReport`. Take listing screenshots with `playdrop project check`. Video is optional and can be added later; never substitute a script-based or in-browser recording path.
- For those local screenshots, capture to an unreferenced evidence path first, copy the validated image into `assets/marketing/playdrop/screenshots/portrait/` or `.../landscape/`, and only then add that path to `catalogue.json`. `playdrop project check` validates existing listing paths before it performs a new capture.

## Listing Capture

Before capture, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, run a deterministic showcase of real gameplay for each declared surface. It must actively perform the core verb for the full recording, survive long enough to show a satisfying high-pressure or high-progress moment, and never settle on a menu, game-over screen, score-zero state, or idle opening.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after the showcase is in active gameplay and ready for recording. Calling the ordinary start function without deterministic showcase control is insufficient.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and make `stopAudioCapture()` resolve `{ mimeType, base64 }` containing the recorded audio. Merely toggling runtime audio is not an export and capture rejects it before launching the native recorder.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

For macOS PlayDrop Cloud and Local Agent worker tasks, record after the last runtime change. A final tape is recommended first, and the optional capture-independent preflight is useful when early validation could avoid an expensive recording; then run the native recorder once for the declared surface set. Windows Local Agent and other direct-creator tasks skip the rest of this section.

```sh
playdrop project capture . --output-dir assets/marketing/playdrop/capture
```

The capture report is bound to the runtime bundle. Inspect the generated poster and beginning, middle, and end frames without relaunching the game. A later runtime or capture-hook change invalidates the recording: finish the change, validate the resulting runtime, and capture it again.

Worker captures use the canonical capture directory by default. Repeating the same command for the same runtime reuses its video; changing only `--poster-at` extracts a new poster from that video without relaunching the game. Other same-runtime recapture settings are rejected: fix the preview implementation and validate the changed runtime if the recording itself is not good enough.

Use gameplay stills, not loading screens. Copy each recorder `*poster.png` into `assets/marketing/playdrop/screenshots/portrait/` or `.../landscape/` per surface as a byte-identical copy (production validates screenshot paths there, and identical bytes keep the recorder-hash binding); videos stay in the capture directory. Then add the media to `catalogue.json`:

- `listing.screenshotsPortrait` or `listing.screenshotsLandscape`: the copied poster PNGs under `screenshots/portrait|landscape/`
- `listing.videosPortrait` or `listing.videosLandscape`: every `*listing.mp4`
- `listing.captureReport`: `assets/marketing/playdrop/capture/capture-report.json`

Single-surface apps produce `poster.png` and `listing.mp4`. Multi-surface apps produce surface-prefixed files such as `desktop-poster.png`, `mobile-landscape-listing.mp4`, and `mobile-portrait-poster.png`.
