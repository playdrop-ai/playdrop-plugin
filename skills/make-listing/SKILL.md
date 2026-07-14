---
name: make-listing
description: "Create PlayDrop listing assets and metadata that match the real game and upload cleanly."
---

# Make Listing

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

## Required For New Games

- App icon PNG when available.
- Portrait and landscape hero PNG.
- Screenshots for supported surfaces.
- Accurate title, description, tags, surfaces, `previewable`, `uses`, and `design` in `catalogue.json`.

## Rules

- Start listing hero art from the art-direction hero files (`assets/art-direction/hero-portrait.png`, `hero-landscape.png`); refine or recompose against real screenshots and runtime assets as needed. Never use the art mockup board, or any crop of it, as hero art.
- App icon: the mascot/hero from the hero art, close up, bold silhouette readable at small sizes, flat background from the palette, no text.
- Hero art may be more polished than gameplay, but it must depict the actual game fantasy and key entities.
- For icon art, or hero art when the art-direction hero files are missing (older games), prefer built-in agent image generation (copy the produced file from the generator's output directory, for Codex `$CODEX_HOME/generated_images`, into the workspace and verify with `file`). If native generation is unavailable or failed after one retry, use PlayDrop CLI AI generation. If both fail (including `insufficient_funds`), compose from recorder stills, runtime assets, packs, CC0, or owned designed assets and record the reason; never fail the work over listing art generation.
- Do not use misleading stock-like art, raw screenshots as hero art, or title text that gets clipped in common listing crops.
- Store listing work is not optional polish; it is part of the shipped draft.
- PlayDrop Cloud tasks: final listing media must come from the native recorder and include `listing.captureReport` (the work order enforces this). Direct creators: video recording is OPTIONAL; when you want it, use the PlayDrop desktop app for quality capture, take screenshots with `playdrop project check`, and never use a script-based or in-browser recording path.

## Listing Capture

Before capture, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, render one deterministic live gameplay scene for each declared surface.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after the preview scene is ready for recording.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and `window.__listingCapture.stopAudioCapture()` so the recorder can save synced audio.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

Run the native recorder once for the declared surface set:

```sh
playdrop project capture . --output-dir assets/marketing/playdrop/capture
```

Use gameplay stills, not loading screens. Add every recorder poster and video from the output directory to `catalogue.json`:

- `listing.screenshotsPortrait` or `listing.screenshotsLandscape`: every `*poster.png`
- `listing.videosPortrait` or `listing.videosLandscape`: every `*listing.mp4`
- `listing.captureReport`: `assets/marketing/playdrop/capture/capture-report.json`

Single-surface apps produce `poster.png` and `listing.mp4`. Multi-surface apps produce surface-prefixed files such as `desktop-poster.png`, `mobile-landscape-listing.mp4`, and `mobile-portrait-poster.png`.
