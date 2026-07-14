# Art Direction

Every new game produces its art direction as an ordered chain of artifacts, each derived from the previous:

1. Hero art (always): the game fantasy as key art, generated first; reused by the store listing.
2. Art mockup board (always): the game's real screens.
3. Asset sheet (when packs and catalogue assets cannot cover a need): `references/asset-sheet.md`.
4. Game background (when scenes have a visible backdrop): produced in art-production, step 5 below.

Hero art and the mockup board come before any gameplay code. Do not skip them, including for simple UI games. Every generation follows the `skills/make-assets` preference order.

## Step 1: concept block

Expand the creator prompt into a concept block inside your working notes before prompting the image model. Creator prompts are often one line; the concept block is where you make the game specific. Write:

- Fantasy: one sentence, what the player gets to be or do.
- Mascot or hero identity: species/object, 2-3 locked visual traits (colors, accessory, expression), personality in 3 words.
- Setting and mood: place, time, weather, lighting.
- Palette: 4-6 named colors with hex values.
- UI material language: surface texture, corner rounding, button feel, typography mood.

## Step 2: hero art

Hero art is one illustration that sells the fantasy: the mascot/hero with locked traits, mid-action at the most exciting moment of the core loop, in the setting. It is key art, not a screenshot: no UI, no HUD, no phone frames, no text, no logo, no watermark.

Generate two files: `assets/art-direction/hero-portrait.png` (9:16) and `assets/art-direction/hero-landscape.png` (16:9).

Template: "Create high-resolution key art for an original premium casual mobile game. <fantasy sentence>. <Mascot with locked traits> <doing the core action> in <setting and mood>, dynamic composition, <palette colors by name>, polished stylized illustration, high production value, not photorealistic. No text, no logo, no user interface, no phone frames, no watermark."

The store listing reuses these files as the base of the listing hero art. Never use the mockup board, or any crop of it, as hero art.

## Step 3: mockup board

The board shows ONLY in-game screens, visually consistent with the hero art (same mascot, palette, materials). No branding area, no app icon, no logo lockup: branding belongs to hero art and listing work, not the mockup. Mockup orientation MUST match the game's primary surface (portrait phones for portrait games, landscape for landscape/desktop). Screens are ONLY the ones scoped v1 will actually ship: title, core gameplay, success state, failure/mistake state. Never invent meta-game screens the build will not include.

Template: "Create one single high-resolution landscape art-direction sheet for an original premium casual mobile game called '<NAME>'. One cohesive presentation board, not separate files. Exactly 4 accurate iPhone 15 <portrait|landscape> mockups arranged <in a row | in a 2x2 grid>, correct proportions, visible Dynamic Island, undistorted. Overall concept: <fantasy, mascot, setting from the concept block>. Overall visual style: premium casual mobile game quality, polished stylized illustration, <palette colors by name>, consistent mascot, consistent UI materials across all screens, high production value, not photorealistic. Phone 1: title screen with logo, mascot, large button labeled 'Play'. Phone 2: core gameplay screen showing <the real core loop, HUD, controls>, clearly playable and uncluttered. Phone 3: success state '<success headline>' with mascot celebrating and rewards. Phone 4: <failure/mistake state> that is encouraging, not punishing. Under the phones, four feature captions: <4 short real features>. Constraints: readable game name and button labels, no distorted phones, no extra screens, no photorealism, no cluttered UI, no inconsistent mascot."

## Step 4: generate and register

Generate hero art first, then the board, with your built-in image generation capability FIRST, then persist each file: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`), so copy the newest produced file to its target path and verify it with `file`. Board target: `assets/art-direction/board.png`. Retry native generation once on failure. Native generation is the normal path: fast and free of PlayDrop credits.

If native generation is unavailable or failed after the retry, use the PlayDrop CLI path (ratio 9:16 for hero-portrait, 16:9 for hero-landscape and the board):

playdrop ai create image "<prompt>" --ratio <ratio> --asset-name <slug>-<artifact> --visibility private --timeout 600 --output <target path>

If the CLI path also fails (including `insufficient_funds`), do NOT fail the game. The concept block becomes the visual source of truth: record `art_direction_generation_unavailable` with the artifact name and exact error in your working notes, and build with packs, CC0, or deliberately designed owned assets that follow the concept block. Record which path you used for every artifact.

## Step 5: game background (in art-production)

Any scene with a visible backdrop uses a real background image asset. Never ship a code-drawn gradient, flat fill, or primitives as the backdrop of a real game; `assetStrategy: procedural` prototypes are the only exception.

- Default: one flattened background image per distinct scene or room type, matching the hero art and palette, in the aspect of the primary surface. Source it per the `skills/make-assets` preference order: a pack or CC0 backdrop that fits the direction beats generating one; generated backgrounds go under `assets/generated/background-<scene>.png`.
- Parallax or depth only when the direction calls for it: generate the layers as one sheet per `references/asset-sheet.md`, compose them at runtime, and verify the composition visually during playtest (take a screenshot; check alignment, full coverage, no seams, readable gameplay on top).

## Step 6: extract into the design

Record in catalogue.json design: the palette (design.artStyle should name the colors), and reference the hero art and board files only when they exist. Every later visual decision (assets, UI, backgrounds, listing art) must match the hero art and concept block. If the shipped game would not be recognizable as phone 2 of that direction, the build is not done.
