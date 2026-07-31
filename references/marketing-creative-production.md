# PlayDrop marketing creative production standard

Use this standard for marketing screenshots, gameplay videos, paid creatives,
and social-media derivatives. The channel-specific skill still owns its
technical export requirements.

## 1. Start from approved precedent and a locked brief

Before creating assets:

1. Inspect the playable game, listing, real captures, positioning brief, and
   approved copy.
2. Inventory the canonical icon, game title, subtitle, hero art, and end card.
3. Mark each input as either `protected` or `editable`.
4. Record the exact headline for every frame or video beat.
5. Record explicitly forbidden treatments, objects, claims, and motifs.

When the operator names a previous campaign such as Starfold or Nuts & Bolts,
inspect its final exports, handoff, source assets, and render scripts before
working. Treat that package as production precedent. Reuse its established
interaction assets and motion system when requested. Do not replace a cited
process with a generic workflow from memory.

Use category research and the game's differentiator to choose the message
before making art. Keep one marketing job per frame or video beat. Marketing
screenshot headlines use two to four words. Video caption plates normally use
three to five words. The visual must prove the message without explanatory body
copy.

When no other PlayDrop precedent is named and the intended listing treatment is
unclear, find the approved Starfold listing package in the available workspace.
Inspect its current screenshot story, final exports, marketing README,
catalogue, sources, and handoff before proceeding.

## 2. Protect identity assets

Protected identity assets are immutable unless the operator explicitly asks to
edit that specific asset.

- Do not regenerate, retouch, recolor, retype, redraw, extend, or decorate a
  protected icon, title, subtitle, hero, or end card.
- Do not add marketing copy to a protected hero.
- Use a protected hero only at an aspect ratio where the exact asset fits
  without cropping, stretching, padding, or generative extension.
- When no protected hero exists for a destination ratio, open video on real
  gameplay. For a still, generate a separate ratio-native marketing composition
  instead of modifying the protected hero.
- When the network uses a separate end card, supply the designated canonical
  hero or end-card file unchanged. Let the network render its own CTA and app
  metadata.

## 3. Apply the correct truth contract to each medium

Video and still images have different responsibilities.

### Gameplay video

- Use only real footage from the shipped game.
- Keep the real board, world, HUD, controls, score, rewards, obstacles, and
  results accurate.
- Use editing, captions, touch guidance, pacing, and effects only when they do
  not change what the player can actually encounter.
- Keep the complete action envelope visible: source, destination, moving
  object, important HUD, and resulting payoff.

### Marketing screenshots

- Generate the complete final image with AI image generation, including game
  content, composition, effects, and the two-to-four-word headline.
- Use the playable game, accurate gameplay video, source stills, hero, icon,
  palette, and positioning brief as references and truth evidence.
- Do not require captured gameplay pixels or exact runtime geometry in the
  final still.
- Allow idealized lighting, camera, scale, staging, and effects when they make
  the selling point clearer.
- Never advertise a mechanic, character, environment, control, progression
  system, reward, score behavior, obstacle, or outcome that the shipped game
  does not contain.
- For rules-dense games, verify that the image communicates the real mechanic
  even when the board is idealized. Do not show an action that contradicts the
  actual rules.

Fail with `marketing_gameplay_truth_invalid` when a video is not real gameplay
or a still advertises unsupported game content.

## 4. Build finished marketing typography

Use the game's approved visual language. Do not ship placeholder typography,
plain debug text, or generic lettering that looks unrelated to the game.

For marketing screenshots, generate the exact headline as part of the complete
AI-generated image. Regenerate any candidate with missing, duplicated,
misspelled, malformed, or unreadable words. Do not repair it with generic
script-drawn or HTML typography.

For premium raster caption plates used in video:

1. Inspect the approved screenshot typography and any cited campaign plates.
2. Define exact copy, line breaks, game-specific materials, palette,
   silhouette, and forbidden effects.
3. Generate each distinct plate separately with the exact text on a flat chroma
   background.
4. Remove the chroma background with the standard ImageGen helper.
5. Verify spelling, punctuation, alpha channel, transparent corners, subject
   coverage, and clean edges on the actual video frame.
6. Save the chroma source, production alpha asset, and prompt notes with the
   editable project.

Prefer a compact transparent silhouette. Do not add an opaque panel or an outer
frame unless the approved art direction requires it. Assume storefront and
social surfaces may apply their own rounded mask, so decorative borders around
the canvas are normally invalid.

For video, use a fast readable entrance and exit. A practical PlayDrop default
is a 200 ms fade on each edge plus a subtle settle from 103.5 percent to 100
percent scale. Hold short three-to-five-word plates for roughly 2 to 2.6
seconds. Hold an opening hook or final call to action for roughly 3 to 4 seconds
when the edit permits.

Place copy in the nearest genuinely quiet region:

- For a centered board, prefer clear space above it.
- For a top-aligned board with empty lower scenery, use the lower quiet region.
- Never cover the player action, hand cue, goal, moving object, platform
  controls, or important HUD.

## 5. Capture real interaction for video

Record the game externally at the destination surface dimensions. Capture a
complete clean take when the creative needs a late-game payoff or victory, then
select the strongest truthful sections in the edit.

- Hide browser, host, debug, and recording chrome.
- Keep the full board or playfield visible edge to edge.
- Preserve source proportions with one uniform scale.
- Never use side bars, blurred gutters, duplicated footage, decorative fill,
  nonuniform scaling, or stretching.
- Crop only when a complete-clip review proves that the removed region is
  genuine empty margin. Never crop the board, action, touch cue, HUD that
  matters, or payoff.
- For board and puzzle games that fill the width, prefer a separate native
  capture for 3:4 and 2:3 instead of assuming a 9:16 crop is safe.

Use an approved transparent hand asset when input is not otherwise obvious.
Anchor the fingertip to the real contact point, compress the hand slightly into
the screen plane for a tap, and place radial feedback at the same point. Show
the complete gesture for long presses and drags. Derive every cue timestamp
from the exact raw take used in the edit.

## 6. Edit by semantic phase

Split the source at meaningful boundaries:

1. identity or opening hook,
2. readable player input,
3. automatic or repetitive payoff,
4. result or victory celebration.

Do not apply one speed to the entire video merely to reach a target duration.
Keep player input slow enough to understand. Accelerate only a repetitive
automatic phase when that improves momentum. Return to a readable speed for the
result or victory unless the operator requests otherwise. Keep audio
synchronized per segment and record every phase speed in the edit manifest.

When an exact protected hero exists at the output ratio and the campaign uses a
hero opening, use that file unchanged for a short identity beat before real
gameplay. Do not fabricate a hero opening for ratios without one.

## 7. Adapt each destination deliberately

The normal cross-channel video package is:

- 1080 x 1920 shared social short, roughly 10 to 15 seconds,
- 1080 x 1920 focused paid cut, roughly 8 to 15 seconds when requested,
- 1080 x 1440 Instagram feed cut,
- 1000 x 1500 Pinterest video Pin,
- 1920 x 1080 landscape trailer, roughly 20 to 30 seconds.

These are separate compositions or verified derivatives, not permission to
crop blindly. Reuse one file only when its dimensions, safe areas, timing, and
complete action envelope are already correct for every mapped destination.

## 8. Produce review evidence

Keep `source-captures/`, `project/`, `review/`, and final exports separate.

For every video, produce:

- first-frame and final-frame checks,
- a complete contact sheet,
- frames at each interaction cue,
- frames before and after every speed boundary,
- a poster-frame candidate.

For every still, produce:

- a full-size check,
- a thumbnail-size check,
- a comparison with its closest approved reference,
- a comparison with its canonical master when it is a derivative,
- the two-to-four-word headline and truthful selling point,
- the game or video evidence supporting the promise.

For a multi-format package, create one composite showing every final in
delivery order. Record sources, dimensions, crop policy, copy, cue timestamps,
phase speeds, codec, duration, and validation results in the handoff.

Do not approve from metadata alone. Review the actual pixels, the complete
motion, and the muted viewing experience.
