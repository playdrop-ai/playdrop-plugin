# Art Direction Board

Every new game generates ONE art-direction board image before any gameplay code. The board is the visual north star: mascot identity, palette, UI material language, and the look of each core screen. Do not skip it, including for simple UI games.

## Step 1: concept block

Expand the creator prompt into a concept block inside your working notes before prompting the image model. Creator prompts are often one line; the concept block is where you make the game specific. Write:

- Fantasy: one sentence, what the player gets to be or do.
- Mascot or hero identity: species/object, 2-3 locked visual traits (colors, accessory, expression), personality in 3 words.
- Setting and mood: place, time, weather, lighting.
- Palette: 4-6 named colors with hex values.
- UI material language: surface texture, corner rounding, button feel, typography mood.

## Step 2: board prompt

Write one image prompt following this template, filled from the concept block. Mockup orientation MUST match the game's primary surface (portrait phones for portrait games, landscape for landscape/desktop). Screens are ONLY the ones scoped v1 will actually ship: title, core gameplay, success state, failure/mistake state. Never invent meta-game screens the build will not include.

Template: "Create one single high-resolution landscape art-direction sheet for an original premium casual mobile game called '<NAME>'. One cohesive presentation board, not separate files. Exactly 4 accurate iPhone 15 <portrait|landscape> mockups arranged <in a row | in a 2x2 grid>, correct proportions, visible Dynamic Island, undistorted. Overall concept: <fantasy, mascot, setting from the concept block>. Overall visual style: premium casual mobile game quality, polished stylized illustration, <palette colors by name>, consistent mascot, consistent UI materials across all screens, high production value, not photorealistic. Top-left branding area: polished app icon, refined logo lockup reading '<NAME>', prominent mascot illustration with <locked traits>. Phone 1: title screen with logo, mascot, large button labeled 'Play'. Phone 2: core gameplay screen showing <the real core loop, HUD, controls>, clearly playable and uncluttered. Phone 3: success state '<success headline>' with mascot celebrating and rewards. Phone 4: <failure/mistake state> that is encouraging, not punishing. Under the phones, four feature captions: <4 short real features>. Constraints: readable game name and button labels, no distorted phones, no extra screens, no photorealism, no cluttered UI, no inconsistent mascot."

## Step 3: generate and register

Generate the board with your built-in image generation capability FIRST, then persist it: built-in tools may save outside the workspace (Codex saves under `$CODEX_HOME/generated_images`, default `~/.codex/generated_images`), so copy the newest produced file to `assets/art-direction/board.png` and verify it with `file`. Retry native generation once on failure. Native generation is the normal path: fast and free of PlayDrop credits.

If native generation is unavailable or failed after the retry, use the PlayDrop CLI path:

./bin/playdrop ai create image "<board prompt>" --ratio 16:9 --asset-name <slug>-art-direction --visibility private --timeout 600 --output assets/art-direction/board.png

If the CLI path also fails (including `insufficient_funds`), do NOT fail the game. The concept block becomes the visual source of truth: record `art_board_generation_unavailable` with the exact error in your working notes, and build with packs, CC0, or deliberately designed owned assets that follow the concept block. Record which path you used in every case.

## Step 4: extract into the design

Record in catalogue.json design: the palette (design.artStyle should name the colors), and reference the board file only when it exists. Every later visual decision (assets, UI, hero art) must match the concept block or board. If the shipped game would not be recognizable as phone 2 of that direction, the build is not done.
