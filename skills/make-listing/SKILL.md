---
name: make-listing
description: "Create PlayDrop listing assets and metadata that match the real game and upload cleanly."
---

# Make Listing

## Required For New Games

- App icon PNG when available.
- Portrait and landscape hero PNG.
- Screenshots for supported surfaces.
- Accurate title, description, tags, surfaces, `previewable`, `uses`, and `design` in `catalogue.json`.

## Rules

- Base hero art on real screenshots, runtime assets, and final art direction.
- Hero art may be more polished than gameplay, but it must depict the actual game fantasy and key entities.
- Prefer built-in agent image generation for hero/icon art when available. Use PlayDrop CLI AI generation only when the agent has no native capability for that asset type.
- Do not use misleading stock-like art, raw screenshots as hero art, or title text that gets clipped in common listing crops.
- Store listing work is not optional polish; it is part of the shipped draft.
- Final listing media for PlayDrop Cloud games must come from the native recorder and include `listing.captureReport`.

## Listing Capture

Before capture, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, render one deterministic live gameplay scene for each declared surface.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after the preview scene is ready for recording.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and `window.__listingCapture.stopAudioCapture()` so the recorder can save synced audio.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

First build the app and copy the `bundleHash=<sha256>` value from the output:

```sh
./bin/playdrop project build .
```

Then run the native recorder once for the declared surface set:

```sh
./bin/playdrop project capture . --output-dir assets/marketing/playdrop/capture --content-hash <bundle-sha256>
```

Use gameplay stills, not loading screens. Add every recorder poster and video from the output directory to `catalogue.json`:

- `listing.screenshotsPortrait` or `listing.screenshotsLandscape`: every `*poster.png`
- `listing.videosPortrait` or `listing.videosLandscape`: every `*listing.mp4`
- `listing.captureReport`: `assets/marketing/playdrop/capture/capture-report.json`

Single-surface apps produce `poster.png` and `listing.mp4`. Multi-surface apps produce surface-prefixed files such as `desktop-poster.png`, `mobile-landscape-listing.mp4`, and `mobile-portrait-poster.png`.
