# Generated Asset Sheet

Use this when catalogue packs and individual assets cannot cover an asset need (mascot, unique props, themed tiles). Derive everything from the approved hero art and art-direction board. Generation follows the `skills/make-assets` preference order.

## Small needs: individual assets

For 6 or fewer needed images, generate them individually with native tooling, each conditioned on `assets/art-direction/hero-portrait.png` (and the board when helpful) for style consistency. Save each PNG under `assets/generated/<asset-name>.png`. Use isolated centered assets with complete silhouettes, transparent or easily removable flat backgrounds, no text, no frame, and consistent lighting.

## Larger needs: use make-2d-asset-pack

For more than 6 images, item families (characters, items, props, tiles), or paired large/small variants, use the staged `make-2d-asset-pack` skill instead of hand-rolling sheets or extraction scripts. Build its request JSON from the game's actual needs (families and items with payloads), put the concept palette and style words in `style.description`, and pass `assets/art-direction/hero-portrait.png` as the first style reference. Inside an autonomous task, run its code and Codex review gates and record in your notes that the human gate was skipped. Copy the approved transparent PNGs into the game and register them as `ownedAssets`; never publish a pack from inside a task.

Background parallax layers do NOT use sheets: they are full-canvas alpha layers per `references/art-direction-board.md` step 5.
