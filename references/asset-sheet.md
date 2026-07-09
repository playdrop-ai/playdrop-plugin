# Generated Asset Sheet

Use this when catalogue packs and individual assets cannot cover an asset need (mascot, unique props, themed tiles). Derive everything from the approved art-direction board.

## Generation path

Use your built-in image generation capability FIRST for both individual assets and sheets, saving the PNGs to the paths below. Only if your agent has no built-in image generation, or it failed after one retry, use the PlayDrop CLI commands in this reference. Record which path you used.

## Small needs: individual assets

For 6 or fewer needed images, generate them individually, each conditioned on the board for style consistency:

./bin/playdrop ai create image "<one asset description, style matching the board: palette, rendering, mood>. Single isolated game asset, centered, complete silhouette, on a perfectly flat pure #00ff00 matte background, no text, no frame, soft shadow attached to the object only." --image1 assets/art-direction/board.png --ratio 1:1 --visibility private --timeout 600 --output assets/generated/<asset-name>.png

## Larger needs: one sheet

For more than 6 images, generate one grid sheet (more consistent):

./bin/playdrop ai create image "Create one high-resolution square 2D game asset sheet for <NAME>, derived exactly from the attached approved art direction: <palette, style, mascot traits>. Clean <C> columns x <R> rows grid on a perfectly flat pure #00ff00 matte background, equal invisible cells, consistent padding, lighting, and scale, no overlapping assets, no labels, numbers, dividers, frames, or captions. Every asset isolated, centered, complete, readable at mobile size. Assets, left to right, top to bottom: <numbered list>. Same mascot design in all mascot cells. Clean silhouettes, extraction-friendly edges, no text, no photorealism." --image1 assets/art-direction/board.png --ratio 1:1 --visibility private --timeout 600 --output assets/generated/sheet.png

## Extraction

Slice the sheet yourself in the workspace (npm install pngjs, then a small script): chroma-key everything within distance ~120 of pure #00ff00 to alpha, despill remaining green fringes (g = min(g, max(r,b)) on semi-transparent edge pixels), find connected bounding boxes, expect one per requested asset, export trimmed alpha PNGs named from the asset list. HARD CHECK: if the count of extracted boxes does not match the requested list, regenerate the sheet exactly once with the count problem named in the prompt; if it still mismatches, fail the phase loudly and fall back to individual assets for the missing items only.

Load extracted assets in the game like any owned asset and register them in catalogue.json. The mascot and all primary interactive objects must come from the board, a pack, or this pipeline. Never primitives.
