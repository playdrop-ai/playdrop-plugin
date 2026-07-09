# Generated Asset Sheet

Use this when catalogue packs and individual assets cannot cover an asset need (mascot, unique props, themed tiles). Derive everything from the approved art-direction board.

## Generation path

Use your built-in image generation capability for both individual assets and sheets only when it can save PNG files in the workspace. Builder tasks must never call PlayDrop CLI AI generation or spend PlayDrop credits. If native generation cannot write files, use packs, CC0 assets, or owned designed runtime assets. If the requested scope requires generated media and no native file output exists, fail loudly with `native_image_generation_artifact_missing`.

## Small needs: individual assets

For 6 or fewer needed images, generate them individually with native tooling, each conditioned on the board or concept block for style consistency. Save each PNG under `assets/generated/<asset-name>.png`. Use isolated centered assets with complete silhouettes, transparent or easily removable flat backgrounds, no text, no frame, and consistent lighting.

## Larger needs: one sheet

For more than 6 images, generate one grid sheet with native tooling and save it to `assets/generated/sheet.png` (more consistent). The sheet must be a clean grid on a removable flat background, equal invisible cells, consistent padding, lighting, and scale, no overlapping assets, no labels, numbers, dividers, frames, or captions. Every asset must be isolated, centered, complete, and readable at mobile size.

## Extraction

Slice the sheet yourself in the workspace (npm install pngjs, then a small script): chroma-key everything within distance ~120 of pure #00ff00 to alpha, despill remaining green fringes (g = min(g, max(r,b)) on semi-transparent edge pixels), find connected bounding boxes, expect one per requested asset, export trimmed alpha PNGs named from the asset list. HARD CHECK: if the count of extracted boxes does not match the requested list, regenerate the sheet exactly once with the count problem named in the prompt; if it still mismatches, fail the phase loudly and fall back to individual assets for the missing items only.

Load extracted assets in the game like any owned asset and register them in catalogue.json. The mascot and all primary interactive objects must come from the board, a pack, or this pipeline. Never primitives.
