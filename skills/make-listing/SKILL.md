---
name: make-listing
description: "Create or refresh a PlayDrop game listing with accurate metadata and optional creator-requested media. Use for PlayDrop catalogue and game-detail listing work, including external games."
---

# Make Listing

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

## Listing contract

- Accurate title, subtitle, description, tags, surfaces, `uses`, and any populated optional `design` refs are enough to complete the default listing workflow. See `../../references/catalogue-json.md`.
- A Cloud `NEW_GAME` must include a square app icon, portrait hero, and landscape hero. Screenshots, videos, social packages, and capture reports remain optional and must not be created unless the creator requests them.
- For an update that does not request listing changes, leave the existing listing fields and files unchanged.
- Every identity file must be PNG. The app icon must be strictly under 512 KB (524,288 bytes). Each portrait or landscape hero must be strictly under 2 MB (2,097,152 bytes). The upload service validates the declared files again.
- Listing video must be literal footage from the shipped game. Promotional screenshots must make only truthful claims about the shipped game.

## New-game identity art

- Complete this section for a Cloud `NEW_GAME`. For updates, preserve the existing trio unless the creator requested changes.
- When art-direction heroes exist, use them as references for final hero art and refine them against real source stills and runtime assets. Otherwise derive truthful heroes from the finished game.
- Create or edit hero art with AI image generation. Never create hero art with code, SVG, canvas, CSS, or a raw gameplay composition. If AI generation cannot produce acceptable hero art, fail clearly instead of substituting code-drawn art.
- Both portrait and landscape hero art must show the exact game name front and center as large, readable title or logo text. The title is part of the generated composition, not code-added typography. Reject extra wording and misspelled, malformed, clipped, obscured, or unreadable titles.
- Compose portrait and landscape heroes separately for their orientations. Keep the title readable at full size and thumbnail size, preserve the actual game fantasy and key entities, and exclude unrelated UI, device frames, watermarks, and raw gameplay framing.
- Save final identity PNGs under `assets/marketing/playdrop/` and reference them through `listing.icon`, `listing.heroPortrait`, and `listing.heroLandscape`.
- Never use a mockup board, a raw gameplay capture, or a crop of either as hero art.
- Create the app icon as a separate square 1:1 PNG composition, preferably 512x512, with one bold thumbnail-readable silhouette and no text. Never copy, crop, resize, or reuse a hero as the icon.
- Hero art may be more polished than gameplay, but it must express the actual game fantasy and key entities.

Use the production ownership contract in `../make-assets/SKILL.md`:

- **Active Codex agent:** create the complete identity trio directly with built-in image generation, then validate and review all three files.
- **Active Grok agent:** create the complete identity trio with Grok's own image generation, then validate and review all three files. Never delegate image generation to Codex.
- **Active Claude agent:** delegate the complete identity trio to one Codex CLI run. Codex owns all three generations, deterministic transforms, code checks, full-size and thumbnail review, one evidence-based corrected retry, and the final manifest. Claude only updates `catalogue.json` with files that Codex marks accepted.

The production owner must not trust a prompt to satisfy dimensions or byte limits. After generation, inspect all three images together, resize or optimize deterministically when needed, and recheck the final files. Return one compact manifest with path, dimensions, PNG format, byte size, and visual-review result for each file. Accept the trio only when:

- the icon is square, text-free, visually distinct from both heroes, and under 524,288 bytes;
- both heroes are under 2,097,152 bytes and show the exact game name front and center;
- both heroes pass full-size and thumbnail inspection for title spelling, legibility, clipping, composition, truthfulness, and unwanted UI or watermarks.

If any item fails, correct that item and rerun the complete three-file preflight. Do not substitute PlayDrop AI, code-drawn identity art, or an ad hoc processing route.

## Optional promotional screenshots

- Skip this section unless the creator explicitly requested promotional screenshots or a marketing package.
- Use `../make-marketing-screenshots/SKILL.md` for production. Do not substitute recorder posters or ordinary runtime screenshots.
- Save final files under `assets/marketing/playdrop/screenshots/portrait/` or `assets/marketing/playdrop/screenshots/landscape/` and reference only those marketing images in `catalogue.json`.
- Prefer the structured media object with `path`, a stable lowercase `slug`, `title`, accurate `alt`, and concise `caption` so search engines and assistive technology receive useful context.

## Optional gameplay capture

Skip this section unless the creator requested listing video.

Before recording, make the app preview-ready:

- Set `previewable: true` only when the game actually supports preview.
- In preview phase, run a deterministic showcase of real gameplay for each declared surface. It must actively perform the core verb, survive long enough to show a satisfying moment, and never settle on a menu, game-over screen, score-zero state, or idle opening.
- Expose `window.__listingCapture.prepare(sceneId)` and make it finish only after active gameplay is ready for recording.
- If the game has audio, expose `window.__listingCapture.startAudioCapture()` and make `stopAudioCapture()` resolve `{ mimeType, base64 }` with recorded audio.
- Call `sdk.host.ready()` after the preview scene and capture hooks are installed.
- Do not branch on validation, local routes, launch-check flags, or capture markers to change gameplay.

When the native recorder is available, finish every runtime change, then capture the requested surfaces:

```sh
playdrop project capture . --output-dir assets/marketing/playdrop/capture
```

- Keep each recorder poster in the capture directory as a source still and review artifact. Do not copy it into the final screenshot directories.
- Keep each recorder video in the capture directory and reference it through `listing.videosPortrait` or `listing.videosLandscape`.
- Prefer the structured video object with `path`, a stable lowercase `slug`, `title`, `caption`, and `description`. These fields become the durable media URL and search metadata.
- A native capture may produce `assets/marketing/playdrop/capture/capture-report.json`. It is a local report, not a task-completion requirement.
- Inspect the poster and the beginning, middle, and end of every video. A report does not replace pixel review.
- The capture report is bound to the runtime bundle. A runtime or capture-hook change invalidates the recording, so finish the runtime change, validate it, and capture again.

When the native recorder is unavailable, use the supported external capture workflow. Keep source stills as references and publish only real gameplay video as footage. If promotional screenshots were explicitly requested, use AI-generated artwork for those arrays.

## Completion bar

- The metadata and supported surfaces are accurate in `catalogue.json`.
- Every Cloud `NEW_GAME` has an app icon, portrait hero, and landscape hero.
- Screenshots, videos, capture reports, and social packages are absent unless explicitly requested or intentionally preserved from an existing listing.
- Any supplied video accurately represents real gameplay.
- Any supplied icon, heroes, screenshots, and videos are wired correctly in `catalogue.json`.
- When promotional screenshots were explicitly requested, their arrays contain marketing artwork, never raw captures or recorder posters, and every claim is supported by the shipped game and gameplay video.
- Every supplied final image and representative video frame has been inspected at full size and thumbnail size.
