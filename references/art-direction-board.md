# Art Direction

After the greybox core interaction works, every new game produces its art direction as an ordered chain of artifacts, each derived from the previous:

1. Hero art (always): the game fantasy as key art, generated first; reused by the store listing.
2. Art mockup board (always): the game's real screens.
3. Generated assets (when packs and catalogue assets cannot cover a need): `references/asset-sheet.md`.
4. Game background (always for 2D games; 3D backdrops come from the environment): produced in art-production, step 5 below.

Hero art and the mockup board come before final gameplay visuals and production assets, not before the greybox loop. Do not skip them, including for simple UI games. Greybox visuals exist only to tune gameplay and cannot ship. Every generation follows the `skills/make-assets` preference order.

Identity is carried by image conditioning, not prose: `hero-portrait.png` is the canonical identity image, and every downstream generation (landscape hero, board, generated assets, backgrounds, icon, listing art) passes it as a reference image (native reference editing, or CLI `--image1`). Never regenerate the identity from text alone.

## Step 1: art concept

The art concept was decided during `game-design`. Use the working notes or the project's existing `ART_DIRECTION.md`; create or update that file only when retaining the direction will help continued work. It is working memory, not an upload gate. Verify the concept is clear before prompting the image model; every prompt below fills from it. Its contents:

- Fantasy: one sentence, what the player gets to be or do.
- Identity: the game's primary visual subject: a character, creature, vehicle, object, or motif, with 2-3 locked visual traits (colors, accessory, expression) and personality in 3 words.
- Setting and mood: place, time, weather, lighting.
- Palette: 4-6 named colors with hex values.
- UI material language: surface texture, corner rounding, button feel, typography mood.

## Step 2: hero art

Hero art is one illustration that sells the fantasy: the identity subject with locked traits, mid-action at the most exciting moment of the core loop, in the setting, with the game name front and center as a polished logo painted into the illustration by the image model, never overlaid programmatically. The logo must stay legible at thumbnail size and clear of the edges so common listing crops cannot clip it. It is key art, not a screenshot: no other text, no UI, no HUD, no device frames, no watermark.

Generate `assets/art-direction/hero-portrait.png` (9:16) first from the template below; it becomes the canonical identity image. Then derive `assets/art-direction/hero-landscape.png` (16:9) from it with reference conditioning (native reference editing, or CLI `--source-mode IMAGE --image1 assets/art-direction/hero-portrait.png`), recomposing for landscape rather than regenerating and restating the logo text in the prompt. Self-check both hero files: the game name reads exactly '<NAME>' and stays legible at thumbnail size; a misspelled or illegible logo = regenerate that file once with the problem named.

Template: "Create high-resolution key art for an original premium casual game. <fantasy sentence>. <Identity subject with locked traits> <doing the core action> in <setting and mood>, dynamic composition, <palette colors by name>, polished stylized illustration, high production value, not photorealistic. A polished game-logo title reading '<NAME>' integrated front and center, legible at small sizes, away from the edges. No other text, no user interface, no device frames, no watermark."

The store listing reuses these files as the base of the listing hero art. Never use the mockup board, or any crop of it, as hero art.

## Step 3: mockup board

The board shows ONLY in-game screens, visually consistent with the hero art: generate it with `hero-portrait.png` as the reference image so identity, palette, and materials carry over. No branding area, app icon, or logo lockup outside the screens (the title screen's in-game logo is the only branding on the board): branding belongs to the hero art and app icon, not the mockup. Frames match the primary surface: portrait phones for portrait games, landscape phones for landscape games, browser windows for desktop games. Screens are ONLY the ones scoped v1 will actually ship: title, core gameplay, and the loop's real end or pressure states (success and failure for win/loss games; milestone and pressure moments for endless or story loops). Never invent meta-game screens the build will not include.

Template: "Create one single high-resolution landscape art-direction sheet for an original premium casual game called '<NAME>'. One cohesive presentation board, not separate files. Exactly 4 accurate <iPhone 15 portrait | iPhone 15 landscape | desktop browser-window> mockups matching the primary surface, arranged <in a row | in a 2x2 grid>, correct proportions, undistorted<, visible Dynamic Island for phone frames>. Overall concept: <fantasy, identity, and setting from the art concept>. Overall visual style: premium casual game quality, polished stylized illustration, <palette colors by name>, consistent identity subject, consistent UI materials across all screens, high production value, not photorealistic. Screen 1: title screen with logo, identity subject, large button labeled 'Play'. Screen 2: core gameplay screen showing <the real core loop, HUD, controls>, clearly playable and uncluttered. Screen 3: <the loop's success or milestone state '<headline>'> with the identity subject celebrating. Screen 4: <the loop's failure or pressure state> that is encouraging, not punishing. Under the screens, four feature captions: <4 short real features>. Constraints: readable game name and button labels, no distorted frames, no extra screens, no photorealism, no cluttered UI, no inconsistent identity, no game logo, branding area, or app icon anywhere outside the screens, every frame in the orientation of the primary surface."

After generating, verify the board yourself before proceeding: correct device frame and orientation on every mockup, no branding area outside the screens, game name spelled exactly right. One violation = regenerate once with the violation named in the prompt. If the retry still violates, record the violation and mark the board ADVISORY in your notes. THE DIRECTION CONTRACT, which every screen and consistency check in this plugin compares against, is: the valid board; when the board is advisory or deferred, the HERO DIRECTION (hero art plus art concept); when the heroes are also deferred (direct creators), the art concept. Do not loop.

## Step 4: generate and register

Generate hero art first, then the board, with your built-in image generation capability FIRST (persistence mechanics per `skills/make-assets`). Board target: `assets/art-direction/board.png`. Retry native generation once on failure. Native generation is the normal path: fast and free of PlayDrop credits.

If native generation is unavailable or failed after the retry, use the PlayDrop CLI path (ratio 9:16 for hero-portrait, 16:9 for hero-landscape and the board):

playdrop ai create image "<prompt>" --ratio <ratio> --source-mode IMAGE --image1 <reference image> --asset-name <slug>-<artifact> --visibility private --timeout 600 --output <target path>

Omit `--source-mode IMAGE --image1` only for the canonical hero-portrait itself; every other artifact passes its reference.

If the CLI path also fails (including `insufficient_funds`), apply the media failure policy in `skills/make-assets`: in a PlayDrop Cloud task fail this phase clearly with `art_direction_generation_unavailable` and the exact error; direct creators continue with the art concept as the visual source of truth per Plan C and add the missing artifacts later.

## Step 5: game background (in art-production)

Every 2D game has a background image, always: gameplay happens on real background art, never on a code-drawn gradient, flat fill, or primitives; a deliberately abstract prototype is the only exception. 3D games are different: the backdrop comes from the 3D environment (skybox or horizon, lighting, environment geometry), no 2D background image required, but it must match the direction.

Choose the treatment from the camera; all of them are real image art, sourced per the `skills/make-assets` preference order (a pack or CC0 backdrop that fits the direction beats generating one; generated files go under `assets/generated/`). Backgrounds never contain text or logos:

- Fixed screen: one flattened background per distinct scene or room type (`background-<scene>.png`), in the primary surface's full aspect. The background IS the board's gameplay-screen environment with the identity subject, interactive items, and HUD absent. A reliable way to get it: image-edit the board (`--image1 board.png`) asking for exactly that.
- Scrolling camera: a seamlessly tiling background image sized for the engine's tiling object; verify the seam by scrolling at least two full widths.
- Parallax or depth, only when the direction calls for it: 2-4 full-canvas alpha layers with identical dimensions, seamless horizontally when scrolling, matching the direction, composed at runtime; sourced per the preference order like the other treatments (a matching pack's layers qualify). When generating, generate each layer individually with the hero art as reference and name them `background-<scene>-layer<N>.png` back to front. Never produce layers through sprite-extraction pipelines; they split and misalign full-canvas layers.

Verify every treatment visually during playtest: take a screenshot, check alignment, full coverage, no seams, readable gameplay on top, and that entities sit ON the background's structures (ledges, openings, surfaces) rather than floating over them, matching its light.

## Step 6: consistency

Keep the chosen visual style and palette coherent. The image artifacts live at the canonical paths above; do not invent catalogue fields for them. They are project files that ship with the upload; production enforces `board.png` and the listing hero pair, and the judge and reviewer audit the full chain in the shipped files. Every later visual decision (assets, UI, backgrounds, listing art) must match the hero direction. If the shipped game would not be recognizable as the board's gameplay screen (or, for an advisory board, as the hero direction), the build is not done.
