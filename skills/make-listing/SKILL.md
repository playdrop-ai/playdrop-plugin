---
name: make-listing
description: "Create or refresh a complete PlayDrop game listing with accurate metadata, icon and hero art, preview mode, and real gameplay video. Use for PlayDrop catalogue and game-detail listing work, including external games."
---

# Make Listing

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

## Non-negotiable media model

- **Listing video is literal gameplay evidence.** It must show the shipped game running and playing accurately.
- **Promotional screenshots are optional and never part of the default listing workflow.** Create them only when the creator explicitly requests screenshots, store images, promotional stills, or a broader marketing package.
- When explicitly requested, use `../make-marketing-screenshots/SKILL.md`. Source stills and recorder posters remain references and must not be published as promotional screenshots.

## Required for new games

- Dedicated square app icon PNG.
- Portrait and landscape hero PNG.
- A playable runtime with `previewable: true` and an implemented real-gameplay preview scene.
- At least one clean real-gameplay video, using the primary surface when only one is produced.
- Accurate title, subtitle, description, tags, surfaces, `previewable`, `uses`, and any populated optional `design` refs in `catalogue.json` (description bar in `../../references/catalogue-json.md`).

This is the complete default media set. Do not recommend or create promotional screenshots unless the creator explicitly asks for them.

Begin listing work when it is efficient for the game. Early identity art can guide production. Create gameplay video only after the shipped runtime and player promises are known.

## Identity art

- When art-direction heroes exist, use them as references for final hero art and refine them against real source stills and runtime assets. Otherwise derive truthful heroes from the finished game.
- Create or edit hero art with AI image generation. Never create hero art with code, SVG, canvas, CSS, or a raw gameplay composition. If AI generation cannot produce acceptable hero art, fail clearly instead of substituting code-drawn art.
- Both portrait and landscape hero art must show the exact game name front and center as large, readable title or logo text. Inspect at full size and thumbnail size, and reject misspelled, malformed, clipped, obscured, or unreadable titles.
- Save final identity PNGs under `assets/marketing/playdrop/` and reference them through `listing.heroPortrait` and `listing.heroLandscape`. Each hero and screenshot must remain within the CLI size limits.
- Never use a mockup board, a raw gameplay capture, or a crop of either as hero art.
- The app icon is required. It must be a square 1:1 PNG, preferably 512x512. Create it as a separate composition with a bold small-size silhouette and no text. Never copy, crop, resize, or reuse the hero as the icon.
- Hero art may be more polished than gameplay, but it must express the actual game fantasy and key entities.
- For icon and hero art, follow the Plan A Codex CLI with Terra high, Plan B agent-native, then Plan C PlayDrop CLI generation order and media failure policy in `../make-assets/SKILL.md`.
- When a local image inspection or transform needs Python, use the standard PlayDrop creator image runtime. Never install Pillow or create another Python environment during a game task. Fail with `creator_image_runtime_missing` when the standard runtime is unavailable.

## Optional promotional screenshots

- Skip this section unless the creator explicitly requested promotional screenshots or a marketing package.
- Use `../make-marketing-screenshots/SKILL.md` for production. Do not substitute recorder posters or ordinary runtime screenshots.
- Save final files under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/` and reference only those marketing images in `catalogue.json`.
- Prefer the structured media object with `path`, a stable lowercase `slug`, `title`, accurate `alt`, and concise `caption` so search engines and assistive technology receive useful context.

## Gameplay capture

Before recording, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, run a deterministic showcase of real gameplay for each declared surface. It must actively perform the core verb, survive long enough to show a satisfying moment, and never settle on a menu, game-over screen, score-zero state, or idle opening.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after active gameplay is ready for recording.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and make `stopAudioCapture()` resolve `{ mimeType, base64 }` with recorded audio.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

When the native recorder is available, finish every runtime change, then run the native recorder once for all supported surfaces:

```sh
playdrop project capture . --output-dir assets/marketing/playdrop/capture
```

- Keep each recorder poster in the capture directory as a source still and review artifact. Do not copy it into the final screenshot directories.
- Keep each recorder video in the capture directory and reference it through `listing.videosPortrait` or `listing.videosLandscape`.
- Prefer the structured video object with `path`, a stable lowercase `slug`, `title`, `caption`, and `description`. These fields become the durable media URL and search metadata.
- Reference `assets/marketing/playdrop/capture/capture-report.json` through `listing.captureReport` when the task requires native capture proof.
- Inspect the poster and the beginning, middle, and end of every video. A report does not replace pixel review.
- The capture report is bound to the runtime bundle. A runtime or capture-hook change invalidates the recording, so finish the runtime change, validate it, and capture again.

When the native recorder is unavailable, use the supported external capture workflow. Omit `listing.captureReport` when no supported native recorder produced one. Keep source stills as evidence and publish only real gameplay video as footage. If promotional screenshots were explicitly requested, use AI-generated artwork for those arrays.

## Completion bar

- The video accurately represents real gameplay.
- The runtime is playable and preview mode shows real active gameplay.
- Icon, heroes, video, metadata, and supported surfaces are wired correctly in `catalogue.json`.
- When promotional screenshots were explicitly requested, their arrays contain marketing artwork, never raw captures or recorder posters, and every claim is supported by the shipped game and gameplay video.
- Every final image and representative video frame has been inspected at full size and thumbnail size.
