---
name: asset-extraction-2d
description: "Use when extracting 2D game assets, sprites, mascot poses, props, icons, decorations, tile sheets, or packaged bitmap asset sets from PlayDrop art direction, screenshots, or mockups."
---

# Asset Extraction 2D

Use this skill when the user provides an image, mockup, screenshot, or approved art direction and asks to extract one or more non-UI 2D game assets into game-ready bitmap files.

This skill does the extraction. Do not stop at an extraction plan.

## Workflow

1. Identify every requested 2D asset and classify its game-asset role: `Sprite`, `Mascot`, `Character Pose`, `Prop`, `Pickup`, `Icon`, `Tile`, `Decoration`, `VFX Frame`, `Background Layer`, `Portrait`, or a tighter role that fits the game.
2. Decide output shape:
   - use one transparent PNG per asset when assets differ in size, purpose, or framing
   - use a single grid/sprite-sheet PNG when several related assets should share the same size, style, pivot, and padding, such as tile variants, collectible icons, mascot poses, animation frames, or matching props
3. Create a run folder under `tmp/asset-extraction-2d/<slug>/` for prompts, generated matte images, validation previews, reports, and experiments.
4. Ensure transient files are not committed or uploaded: add `tmp/` to `.gitignore` and `.playdropignore` when those files exist or when creating them is appropriate for the game repo.
5. For each single asset or grid sheet, use AI image generation/editing to isolate the requested art onto one flat-background matte image:
   - use pure black `#000000` when the asset does not contain black
   - otherwise use pure white `#ffffff` when the asset does not contain white
   - otherwise use bright green `#00ff00`, bright purple `#ff00ff`, or bright red `#ff0000`, choosing the color least present in the asset
6. Pass that same generated matte image back to AI image generation/editing and strongly request that only the background changes to the second matte color:
   - default second matte is bright green `#00ff00`
   - if the first matte is bright green, use bright purple `#ff00ff` when safe, otherwise bright red `#ff0000`
   - require identical asset pixels, crop, grid, padding, scale, antialiasing, lighting, shadows, and color
7. Run the shared background-swap alpha extractor from the PlayDrop plugin root. If the current working directory is the game repo, use the absolute path to the plugin script or copy the command path from the active skill cache; do not assume the game repo has this script:
   ```bash
   node <playdrop-plugin>/scripts/extract-alpha-background-swap.ts \
     --base tmp/asset-extraction-2d/<slug>/<asset>-matte-a.png \
     --swap tmp/asset-extraction-2d/<slug>/<asset>-matte-b.png \
     --out assets/2d/<asset>.png \
     --base-bg '#000000' \
     --swap-bg '#00ff00' \
     --background-threshold 40 \
     --same-threshold 8 \
     --preview-bg '#ff00ff' \
     --preview-out tmp/asset-extraction-2d/<slug>/<asset>-preview.png \
     --contact-sheet-out tmp/asset-extraction-2d/<slug>/<asset>-contact-sheet.png \
     --report tmp/asset-extraction-2d/<slug>/<asset>-report.json
   ```
8. Validate the transparent PNG visually on bright contact-sheet backgrounds not used by the asset. Check for bleeding, holes, unwanted matte color, clipped shadows, lost interior details, incorrect padding, inconsistent scale, and broken grid alignment. Do not reject only because the report has many matte or semi-transparent pixels; antialiasing, fur, glow, shadows, soft VFX, and AI matte drift can legitimately create them.
9. If the visual cut is not precise, retry in this order: adjust extractor thresholds, regenerate the second matte with stronger "change background only" instructions, then regenerate both isolated matte images. Threshold sweeps such as `--background-threshold 40`, `50`, and `60` are usually faster than regenerating and should be judged by the contact sheet.
10. For each accepted asset, define metadata: name, role, image, size, anchor/pivot, logical bounds, animation frame info if any, tags, source, prompt files, and validation report.
11. Move only accepted transparent PNGs into `assets/2d/`.
12. Add or update `images.json` in the game root.

## Grid Extraction

Use grid extraction when the user asks for multiple related same-size assets or when it will clearly save time and tokens without lowering quality.

Grid rules:

- every cell must have the same width, height, padding, camera, scale, and visual style
- use a clear row/column count in the prompt
- require consistent shadows and baseline alignment
- leave enough transparent padding inside each cell for animation or runtime placement
- do not mix unrelated roles in one sheet
- after extraction, validate the full sheet and at least one cell from each row on harsh backgrounds

Grid prompt addition:

```text
Arrange the assets in a clean <columns>x<rows> grid.
Every cell must be exactly the same size with consistent padding, scale, camera angle, shadow direction, and baseline.
Do not overlap cells. Do not add labels, numbers, dividers, or background decorations.
The final image should function as a sprite sheet / tile sheet.
```

## Prompt Pattern

For the first matte image:

```text
From the supplied image, isolate only the 2D game asset or asset set named "<asset>".
Role: <role>.
Reconstruct occluded or repeated parts only when necessary to make the asset usable as standalone game art.
Put the isolated asset on a perfectly flat solid <matte-a> background.
Do not include surrounding UI, text, screenshots, mockup frames, or unrelated objects.
Preserve the original style, lighting, texture, proportions, silhouette, and production quality.
Output a tightly cropped PNG with clean padding.
```

For the second matte image:

```text
Take the previous isolated asset image and change ONLY the flat background color to <matte-b>.
The asset must remain pixel-identical: same crop, same size, same grid, same padding, same antialiasing, same shadows, same colors, same texture, same edges.
Do not redraw, enhance, simplify, sharpen, blur, recolor, relight, move, resize, or recompose the asset.
```

## Metadata

Register accepted outputs in `images.json`:

```json
{
  "version": 1,
  "images": [
    {
      "name": "fox-chef-idle",
      "role": "Character Pose",
      "image": "assets/2d/fox-chef-idle.png",
      "size": { "width": 512, "height": 512 },
      "anchor": { "x": 0.5, "y": 0.9 },
      "bounds": { "x": 72, "y": 36, "width": 368, "height": 440 },
      "tags": ["mascot", "chef", "idle"],
      "source": "tmp/asset-extraction-2d/<slug>/source.png",
      "extraction": {
        "matteA": "#ffffff",
        "matteB": "#00ff00",
        "contactSheet": "tmp/asset-extraction-2d/<slug>/fox-chef-idle-contact-sheet.png",
        "report": "tmp/asset-extraction-2d/<slug>/fox-chef-idle-report.json",
        "validationStatus": "accepted"
      }
    },
    {
      "name": "garden-props",
      "role": "Prop Sheet",
      "image": "assets/2d/garden-props.png",
      "sheet": {
        "columns": 4,
        "rows": 2,
        "cellWidth": 256,
        "cellHeight": 256,
        "items": [
          { "name": "stone-lantern", "index": 0, "anchor": { "x": 0.5, "y": 0.9 } },
          { "name": "small-shrine", "index": 1, "anchor": { "x": 0.5, "y": 0.9 } }
        ]
      },
      "source": "tmp/asset-extraction-2d/<slug>/source.png"
    }
  ]
}
```
