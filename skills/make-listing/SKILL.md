---
name: make-listing
description: "Create or refresh a complete PlayDrop game listing with accurate metadata, icon and hero art, AI-generated marketing screenshots, and real gameplay video. Use for PlayDrop catalogue and game-detail listing work, including external games."
---

# Make Listing

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

## Non-negotiable media model

- **Listing video is literal gameplay evidence.** It must show the shipped game running and playing accurately.
- **Listing screenshots are promotional artwork.** Use `../make-marketing-screenshots/SKILL.md` to create the final images with AI image generation, including the complete composition and rendered headline.
- **Source stills and recorder posters are references, not final listing screenshots.** Keep them with capture evidence and never point `listing.screenshotsPortrait` or `listing.screenshotsLandscape` at them.
- Default to four final marketing screenshots per supported orientation. Give each image one truthful selling point and one headline of two to four words.
- Marketing screenshots may idealize composition, lighting, scale, camera, and effects. They must not advertise mechanics, characters, environments, progression, or outcomes that the shipped game does not contain.

When uncertain about the intended quality or structure, find the approved Starfold PlayDrop listing package in the available workspace. Inspect its current four-part screenshot story, marketing README, final exports, and catalogue wiring before proceeding.

## Required for new games

- App icon PNG when available.
- Portrait and landscape hero PNG.
- Four AI-generated marketing screenshots for each supported orientation, unless the game has fewer than four genuinely distinct truthful selling points.
- One clean real-gameplay video for each supported orientation when the recording surface is available.
- Accurate title, subtitle, description, tags, surfaces, `previewable`, `uses`, and any populated optional `design` refs in `catalogue.json`.

Begin listing work when it is efficient for the game. Early identity art can guide production. Create final marketing screenshots and gameplay video only after the shipped runtime and player promises are known.

## Identity art

- When art-direction heroes exist, use them as references for final hero art and refine them against real source stills and runtime assets. Otherwise derive truthful heroes from the finished game.
- Save final identity PNGs under `assets/marketing/playdrop/` and reference them through `listing.heroPortrait` and `listing.heroLandscape`. Each hero and screenshot must remain within the CLI size limits.
- Never use a mockup board, a raw gameplay capture, or a crop of either as hero art.
- App icon is optional. When provided, it must be a square 1:1 PNG, preferably 512x512. Create it as a separate composition with a bold small-size silhouette and no text. Never copy, crop, resize, or reuse the hero as the icon.
- Hero art may be more polished than gameplay, but it must express the actual game fantasy and key entities.
- For icon art, or hero art when art-direction heroes are missing, prefer built-in image generation. If native generation is unavailable or fails after one retry, use PlayDrop CLI AI generation. Follow the media failure policy in `../make-assets/SKILL.md`.
- When a local image inspection or transform needs Python, use the standard PlayDrop creator image runtime. Never install Pillow or create another Python environment during a game task. Fail with `creator_image_runtime_missing` when the standard runtime is unavailable.

## Final marketing screenshots

- Use `../make-marketing-screenshots/SKILL.md` for production. Do not substitute recorder posters or ordinary runtime screenshots.
- Each final image must communicate one key selling point in two to four words and remain understandable at listing-card size.
- Generate the complete image, including content and headline, with AI image generation. Regenerate misspelled, malformed, or unreadable text instead of repairing it with generic code-drawn typography.
- Use the playable game, accurate gameplay video, source stills, icon, hero, and approved positioning as truth references.
- Save final files under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/` and reference only those marketing images in `catalogue.json`.

## Gameplay capture

Before recording, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, run a deterministic showcase of real gameplay for each declared surface. It must actively perform the core verb, survive long enough to show a satisfying moment, and never settle on a menu, game-over screen, score-zero state, or idle opening.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after active gameplay is ready for recording.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and make `stopAudioCapture()` resolve `{ mimeType, base64 }` with recorded audio.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

For macOS PlayDrop Cloud and Local Agent worker tasks, finish every runtime change, then run the native recorder once for all supported surfaces:

```sh
playdrop project capture . --output-dir assets/marketing/playdrop/capture
```

- Keep each recorder poster in the capture directory as a source still and review artifact. Do not copy it into the final screenshot directories.
- Keep each recorder video in the capture directory and reference it through `listing.videosPortrait` or `listing.videosLandscape`.
- Reference `assets/marketing/playdrop/capture/capture-report.json` through `listing.captureReport` when the task requires native capture proof.
- Inspect the poster and the beginning, middle, and end of every video. A report does not replace pixel review.
- The capture report is bound to the runtime bundle. A runtime or capture-hook change invalidates the recording, so finish the runtime change, validate it, and capture again.

For Windows Local Agent worker tasks, external games, and direct-creator tasks, use the supported external capture workflow. Omit `listing.captureReport` when no supported native recorder produced one. Keep the source stills as evidence, publish only real gameplay video as footage, and use AI-generated artwork for the final screenshot arrays.

## Completion bar

- The video accurately represents real gameplay.
- Final screenshot arrays contain marketing artwork, never raw captures or recorder posters.
- The screenshot set normally contains four distinct messages per supported orientation.
- Every screenshot headline contains two to four correctly rendered words.
- Every screenshot claim is supported by the shipped game and gameplay video.
- Icon, heroes, screenshots, video, metadata, and supported surfaces are wired correctly in `catalogue.json`.
- Every final image and representative video frame has been inspected at full size and thumbnail size.
