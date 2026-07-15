# Art Direction

Every new game produces its art direction as an ordered chain of artifacts, each derived from the previous:

1. Hero art (always): the game fantasy as key art, generated first; reused by the store listing.
2. Art mockup board (always): the game's real screens.
3. Asset sheet (when packs and catalogue assets cannot cover a need): `references/asset-sheet.md`.
4. Game background (always for 2D games; 3D backdrops come from the environment): produced in art-production, step 5 below.

Hero art and the mockup board come before any gameplay code. Do not skip them, including for simple UI games. Every generation follows the `skills/make-assets` preference order.

Identity is carried by image conditioning, not prose: `hero-portrait.png` is the canonical identity image, and every downstream generation (landscape hero, board, asset sheets, backgrounds, icon, listing art) passes it as a reference image (native reference editing, or CLI `--image1`). Never regenerate the mascot's identity from text alone.

## Step 1: concept block

Expand the creator prompt into a concept block recorded as `catalogue.json.design` fields (`fantasy`, `mascot`, `setting`, `palette`, `uiMaterial`; see `references/catalogue-json.md`) before prompting the image model. catalogue.json is the only design source of truth and always ships with the upload. Creator prompts are often one line; the concept block is where you make the game specific. Write:

- Fantasy: one sentence, what the player gets to be or do.
- Mascot or hero identity: species/object, 2-3 locked visual traits (colors, accessory, expression), personality in 3 words.
- Setting and mood: place, time, weather, lighting.
- Palette: 4-6 named colors with hex values.
- UI material language: surface texture, corner rounding, button feel, typography mood.

## Step 2: hero art

Hero art is one illustration that sells the fantasy: the mascot/hero with locked traits, mid-action at the most exciting moment of the core loop, in the setting, with the game name front and center as a polished logo painted into the illustration by the image model, never overlaid programmatically. The logo must stay legible at thumbnail size and clear of the edges so common listing crops cannot clip it. It is key art, not a screenshot: no other text, no UI, no HUD, no phone frames, no watermark.

Generate `assets/art-direction/hero-portrait.png` (9:16) first from the template below; it becomes the canonical identity image. Then derive `assets/art-direction/hero-landscape.png` (16:9) from it with reference conditioning (native reference editing, or CLI `--source-mode IMAGE --image1 assets/art-direction/hero-portrait.png`), recomposing for landscape rather than regenerating.

Template: "Create high-resolution key art for an original premium casual mobile game. <fantasy sentence>. <Mascot with locked traits> <doing the core action> in <setting and mood>, dynamic composition, <palette colors by name>, polished stylized illustration, high production value, not photorealistic. A polished game-logo title reading '<NAME>' integrated front and center, legible at small sizes, away from the edges. No other text, no user interface, no phone frames, no watermark."

The store listing reuses these files as the base of the listing hero art. Never use the mockup board, or any crop of it, as hero art.

## Step 3: mockup board

The board shows ONLY in-game screens, visually consistent with the hero art: generate it with `hero-portrait.png` as the reference image so mascot, palette, and materials carry over. No branding area, no app icon, no logo lockup: branding belongs to the hero art and app icon, not the mockup. DESKTOP-primary games: use desktop browser-window mockups instead of phone mockups, same four screens. Mockup orientation MUST match the game's primary surface (portrait phones for portrait games, landscape for landscape/desktop). Screens are ONLY the ones scoped v1 will actually ship: title, core gameplay, success state, failure/mistake state. Never invent meta-game screens the build will not include.

Template: "Create one single high-resolution landscape art-direction sheet for an original premium casual mobile game called '<NAME>'. One cohesive presentation board, not separate files. Exactly 4 accurate iPhone 15 <portrait|landscape> mockups arranged <in a row | in a 2x2 grid>, correct proportions, visible Dynamic Island, undistorted. Overall concept: <fantasy, mascot, setting from the concept block>. Overall visual style: premium casual mobile game quality, polished stylized illustration, <palette colors by name>, consistent mascot, consistent UI materials across all screens, high production value, not photorealistic. Phone 1: title screen with logo, mascot, large button labeled 'Play'. Phone 2: core gameplay screen showing <the real core loop, HUD, controls>, clearly playable and uncluttered. Phone 3: success state '<success headline>' with mascot celebrating and rewards. Phone 4: <failure/mistake state> that is encouraging, not punishing. Under the phones, four feature captions: <4 short real features>. Constraints: readable game name and button labels, no distorted phones, no extra screens, no photorealism, no cluttered UI, no inconsistent mascot, no game logo, branding area, or app icon anywhere outside the phone screens, every phone mockup in the <portrait|landscape> orientation of the primary surface."

After generating, verify the board yourself before proceeding: correct orientation on every phone, no branding area outside the screens. One violation = regenerate once with the violation named in the prompt; record the outcome either way.

## Step 4: generate and register

Generate hero art first, then the board, with your built-in image generation capability FIRST, then persist each file: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`), so copy the newest produced file to its target path and verify it with `file`. Board target: `assets/art-direction/board.png`. Retry native generation once on failure. Native generation is the normal path: fast and free of PlayDrop credits.

If native generation is unavailable or failed after the retry, use the PlayDrop CLI path (ratio 9:16 for hero-portrait, 16:9 for hero-landscape and the board):

playdrop ai create image "<prompt>" --ratio <ratio> --source-mode IMAGE --image1 <reference image> --asset-name <slug>-<artifact> --visibility private --timeout 600 --output <target path>

Omit `--source-mode IMAGE --image1` only for the canonical hero-portrait itself; every other artifact passes its reference.

If the CLI path also fails (including `insufficient_funds`), do NOT fail the game. The concept block becomes the visual source of truth: record `art_direction_generation_unavailable` with the artifact name and exact error in your working notes, and build with packs, CC0, or deliberately designed owned assets that follow the concept block. Record which path you used for every artifact.

## Step 5: game background (in art-production)

Every 2D game has a background image, always: gameplay happens on real background art, never on a code-drawn gradient, flat fill, or primitives; `assetStrategy: procedural` prototypes are the only exception. 3D games are different: the backdrop comes from the 3D environment (skybox or horizon, lighting, environment geometry), no 2D background image required, but it must match the direction.

Choose the treatment from the camera; all of them are real image art, sourced per the `skills/make-assets` preference order (a pack or CC0 backdrop that fits the direction beats generating one; generated files go under `assets/generated/`). Backgrounds never contain text or logos:

- Fixed screen: one flattened background image per distinct scene or room type, in the aspect of the primary surface (`background-<scene>.png`).
- Scrolling camera: a seamlessly tiling background image sized for the engine's tiling object (for example Phaser TileSprite); verify the seam by scrolling at least two full widths.
- Parallax or depth, only when the direction calls for it: 2-4 full-canvas alpha layers with identical dimensions, generated individually with the hero art as reference, named `background-<scene>-layer<N>.png` back to front, seamless horizontally when scrolling, composed at runtime. Never produce layers through the chroma-key sheet pipeline; component extraction splits and misaligns them.

Verify every treatment visually during playtest: take a screenshot, check alignment, full coverage, no seams, and readable gameplay on top.

## Step 6: extract into the design

The concept block already lives in `catalogue.json.design`; keep `design.artStyle` consistent with `design.palette`. The image artifacts live at the canonical paths above; do not invent catalogue fields for them. They are project files and MUST ship with the uploaded app, never excluded: the judge and reviewer audit them in the shipped files. Every later visual decision (assets, UI, backgrounds, listing art) must match the hero art and concept block. If the shipped game would not be recognizable as phone 2 of that direction, the build is not done.
