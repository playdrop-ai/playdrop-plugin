---
name: asset-extraction-iso
description: "Use when extracting classic 2:1 square-footprint isometric 2D game assets, tiles, buildings, terrain, roads, props, or packaged iso asset sets from approved PlayDrop art direction."
---

# Asset Extraction ISO

Use this skill when the user provides an image or approved art direction and asks to extract an isometric 2D asset into a game-ready bitmap plus grid metadata.

This skill only supports classic 2:1 isometric projection. A logical square grid tile is rendered as a diamond where `tileWidth = 2 * tileHeight`, such as `128x64` or `256x128`. Do not use dimetric, trimetric, perspective, cabinet, or arbitrary angled projections in this skill.

Current v1 limitation: only square footprints are supported reliably. Use `1x1`, `2x2`, `3x3`, or `4x4`. Do not attempt rectangular footprints such as `2x3` or `3x2`; current image-generation models do not follow the template precisely enough and the output should be rejected before spending more extraction time.

This skill does the extraction. Do not stop at an extraction plan. If a requested asset cannot pass visual validation, leave it rejected in the run folder and do not register it as accepted.

## Package Contract

- Keep all intermediary prompts, source crops, AI generations, template masks, previews, overlays, reports, and rejected attempts under `tmp/asset-extraction-iso/<slug>/`.
- Ensure `tmp/` is ignored by both `.gitignore` and `.playdropignore` when working inside a game repo.
- Move only accepted transparent PNGs into `assets/iso/`.
- Register only accepted assets in `iso.json`; rejected attempts stay in `tmp/` with notes or reports.
- Use the same metadata vocabulary across extraction skills: `name`, `role`, `image`, `source`, `extraction`, `contactSheet`, `report`, `validationStatus`, and `notes` when useful.

## Inputs

Require or infer:

- source art image to extract from
- item to extract from that image
- optional already-successful reference extraction from the same game to match style, scale, matte handling, and grid placement; prefer a non-transparent colorful-template-background version, not a transparent PNG
- square footprint size from `1x1` to `4x4`, such as `1x1`, `2x2`, `3x3`, or `4x4`

The footprint is the ground/base footprint, not the full roof or vertical height.

## Workflow

1. Identify the requested iso asset and classify its role: `Building`, `Terrain Tile`, `Road Tile`, `Water Tile`, `Prop`, `Decoration`, `Resource`, `Landmark`, or a tighter role that fits the game.
2. Choose a square footprint from `1x1` to `4x4`. Use the visible ground/base contact area, not the full roof or vertical height. If the asset appears to need a rectangular footprint, either reinterpret it into the nearest square footprint or reject/defer it; do not run a rectangular template attempt in this v1 skill.
3. Create a run folder under `tmp/asset-extraction-iso/<slug>/` for prompts, generated matte images, validation overlays, reports, and experiments.
4. Ensure transient files are not committed or uploaded: add `tmp/` to `.gitignore` and `.playdropignore` when those files exist or when creating them is appropriate for the game repo.
5. Generate a 3-color template mask for the square footprint. This is the primary iso extraction control surface. Do not generate rectangular templates in this v1 workflow.
   ```bash
   node <playdrop-plugin>/scripts/render-iso-template-mask.ts \
     --out tmp/asset-extraction-iso/<slug>/<asset>-template.png \
     --size 1024 \
     --tile-width 280 \
     --tile-height 140 \
     --footprint-width 2 \
     --footprint-height 2 \
     --origin-x 512 \
     --origin-y 720 \
     --report tmp/asset-extraction-iso/<slug>/<asset>-template.json
   ```
6. Use AI image generation/editing with three images when a same-game reference extraction exists:
   - source art image containing the item to extract
   - approved same-game reference extraction, kept on its colorful template/background, to lock style, scale, asset polish, and successful placement behavior
   - exact template mask for this generation

   If there is no approved same-game reference yet, use only source art and template mask.

   Template rules:
   - red `#ff0000` means locked/non-touchable background
   - green `#00ff00` means the full floor/base footprint, which must be covered by floor/base art
   - purple `#ff00ff` means the only vertical editable region where the body of the asset may appear
   - request the same template composition back with the item painted only into green/purple areas, aligned to this exact template shape, not to the reference extraction's template shape
   - explicitly state that no pure green pixels should remain visible in the final constrained output; green is an instruction area to replace with floor/base art, not a background color
   - remove unwanted transient elements requested by the user, such as smoke, steam, labels, neighboring buildings, roads, vehicles, people, or UI
7. Visually validate the constrained output before matte extraction. The template is a placement contract, not a same-pixel-size contract. Accept the output if the asset is in the intended footprint and the red/purple/green template regions clearly controlled placement, even if the AI image generator returns a different native resolution or slightly repaints flat template colors. Do not fail solely because the output is `1254x1254` instead of the `1024x1024` template. Fail if the item spills into locked red space in a way that changes the usable silhouette, if the floor does not cover the footprint, if requested removals such as smoke/steam are still present, or if the projection is not classic 2:1.
8. Ask AI image generation/editing to convert all leftover red and purple background/template regions to pure white `#ffffff` while keeping the asset and floor pixel-identical.
9. Ask AI image generation/editing to convert only the white/off-white background to bright green `#00ff00` while keeping the asset and floor pixel-identical.
10. Run the shared background-swap alpha extractor from the PlayDrop plugin root when the white/green matte pair stayed visually aligned:
   ```bash
   node <playdrop-plugin>/scripts/extract-alpha-background-swap.ts \
     --base tmp/asset-extraction-iso/<slug>/<asset>-white-matte.png \
     --swap tmp/asset-extraction-iso/<slug>/<asset>-green-matte.png \
     --out assets/iso/<asset>.png \
     --base-bg '#ffffff' \
     --swap-bg '#00ff00' \
     --background-threshold 70 \
     --same-threshold 45 \
     --opaque-distance-threshold 20 \
     --preview-bg '#ff00ff' \
     --preview-out tmp/asset-extraction-iso/<slug>/<asset>-preview.png \
     --contact-sheet-out tmp/asset-extraction-iso/<slug>/<asset>-contact-sheet.png \
     --report tmp/asset-extraction-iso/<slug>/<asset>-report.json
   ```
11. If the AI white/green pair visibly drifts, creates ghost silhouettes, or damages details, do not package that output. Use connected template-background extraction from the constrained template image instead:
   ```bash
   node <playdrop-plugin>/scripts/extract-template-background.ts \
     --input tmp/asset-extraction-iso/<slug>/<asset>-constrained.png \
     --out assets/iso/<asset>.png \
     --keys '#ff0000,#ff00ff' \
     --distance-threshold 90 \
     --hue-threshold 18 \
     --remove-guide-lines \
     --line-hue-threshold 45 \
     --line-min-run 256 \
     --preview-bg '#ff00ff' \
     --preview-out tmp/asset-extraction-iso/<slug>/<asset>-preview.png \
     --contact-sheet-out tmp/asset-extraction-iso/<slug>/<asset>-contact-sheet.png \
     --report tmp/asset-extraction-iso/<slug>/<asset>-report.json
   ```
   This is valid because the template-constrained output already contains known red/purple background guides. The script only removes guide-colored pixels connected to the image border plus long leftover guide lines; it avoids deleting similar brick, copper, or window colors inside the asset.
   Use `--keep-largest-component` when tiny disconnected guide specks remain after removal. Long guide-line cleanup must catch both horizontal and vertical leftovers from AI-generated template edges.
12. Validate the transparent PNG visually on bright contact-sheet backgrounds. Visual acceptance is authoritative here. Check for bleeding, holes, unwanted matte color, clipped roof/height, lost ground contact, interior transparency tint, broken footprint shape, and any requested removals such as smoke/steam. Tiny matte ticks on highlights can be accepted if the asset is visually strong and the contact sheet does not show obvious holes, halos, color blocks, or remaining forbidden elements. Do not reject only because a report has many matte, semi-transparent, or removed pixels; AI matte drift and template antialiasing can legitimately create them.
13. Render the classic 2:1 iso grid overlay using the square footprint metadata from the template, scaled to the generated output if the native image resolution differs:
    ```bash
    node <playdrop-plugin>/scripts/render-iso-grid-overlay.ts \
      --image assets/iso/<asset>.png \
      --out tmp/asset-extraction-iso/<slug>/<asset>-iso-overlay.png \
      --report tmp/asset-extraction-iso/<slug>/<asset>-iso-overlay.json \
      --tile-width 280 \
      --tile-height 140 \
      --footprint-width 2 \
      --footprint-height 2 \
      --origin-x 512 \
      --origin-y 720 \
      --background '#ff00ff'
    ```
14. Register accepted outputs in `iso.json` in the game root and move only accepted transparent PNGs into `assets/iso/`.

## Exploration Fallback

When a square-footprint template-constrained output fails but the source still looks promising, try up to three direct image-generation approaches before giving up:

1. Source art plus approved same-game reference plus exact square template. If the generation tool only supports two image inputs, combine source and reference into one labeled reference sheet and use the exact template as the second input.
2. Source art plus exact square template, without the same-game reference.
3. Source art only, with a strong prompt requiring a classic 2:1 square-footprint asset on a plain extraction background.

For each approach, record the prompt and direct output in `tmp/asset-extraction-iso/<slug>/`. Do not continue to matte extraction unless the direct output already satisfies the footprint and red/green/purple contract visually.

## Rectangular Footprints

Rectangular footprints are future work. A Steam City `2x3` factory extraction was tested with source+reference+template, source+template, and source-only prompts, including stronger instructions to reinterpret the art, preserve red pixels, fully consume green floor pixels, avoid streets/sidewalks, and adjust perspective. The model still failed the placement contract often enough that rectangular support is not reliable. Reject or defer `2x3`, `3x2`, and other non-square footprints until PlayDrop has a more template-faithful generation path.

## Prompt Pattern

For the template-constrained image:

```text
Use the provided images:
1. Source art: <source art image containing the requested item>.
2. Same-game reference extraction: <approved extracted asset on colorful template/background>. Use this only for style, polish, scale discipline, and successful extraction behavior.
3. Template mask: the exact image for this generation with red locked pixels, purple editable vertical area, and green floor footprint.

Return the same composition as image 3, allowing for the image generator's native output resolution.

Role: <role>.
Footprint: <size>x<size> square footprint on a classic 2:1 isometric grid.

Red region: locked background. Keep it as background; do not put asset art there.
Green region: floor footprint. Fully cover it with the asset's floor/base.
Purple region: vertical editable region. Put the asset body only there. Leave unused purple as background.

Do not copy the reference extraction's subject. The reference image is not the target item.
Do not reuse the reference extraction's footprint if it differs from this template. Align to image 3 exactly.
Do not leave any pure green visible. The green area is not background; it must become painted floor/base art.
Use classic 2:1 isometric projection only. Remove <unwanted elements such as smoke/steam>. Preserve the source style and production quality.
```

For the white matte:

```text
Take the template-constrained asset image and change ONLY the red and purple background/template areas to pure white #ffffff.
Keep the asset and complete isometric floor/base pixel-identical. Do not redraw, recolor, relight, resize, move, crop, or improve the asset.
```

For the green matte:

```text
Take the white-matte asset image and change ONLY the white/off-white background to pure bright green #00ff00.
Keep the asset and complete isometric floor/base pixel-identical. Treat this as a paint-bucket fill of background pixels only.
```

## Metadata

Register each accepted asset in `iso.json`:

```json
{
  "version": 1,
  "projection": "isometric-2:1",
  "assets": [
    {
      "name": "steam-city-civic-hall",
      "role": "Building",
      "image": "assets/iso/steam-city-civic-hall.png",
      "size": { "width": 1024, "height": 1024 },
      "tile": { "width": 280, "height": 140 },
      "footprint": { "width": 2, "height": 2 },
      "origin": { "x": 512, "y": 720 },
      "anchor": { "x": 0.5, "y": 0.703 },
      "sortPoint": { "x": 0.5, "y": 0.875 },
      "bounds": { "x": 196, "y": 64, "width": 632, "height": 780 },
      "source": "tmp/asset-extraction-iso/<slug>/source.png",
      "extraction": {
        "template": "tmp/asset-extraction-iso/<slug>/<asset>-template.png",
        "templateReport": "tmp/asset-extraction-iso/<slug>/<asset>-template.json",
        "whiteMatte": "#ffffff",
        "greenMatte": "#00ff00",
        "templatePrompt": "tmp/asset-extraction-iso/<slug>/<asset>-template-prompt.txt",
        "whitePrompt": "tmp/asset-extraction-iso/<slug>/<asset>-white-prompt.txt",
        "greenPrompt": "tmp/asset-extraction-iso/<slug>/<asset>-green-prompt.txt",
        "contactSheet": "tmp/asset-extraction-iso/<slug>/<asset>-contact-sheet.png",
        "overlay": "tmp/asset-extraction-iso/<slug>/<asset>-iso-overlay.png",
        "report": "tmp/asset-extraction-iso/<slug>/<asset>-report.json",
        "validationStatus": "accepted"
      }
    }
  ]
}
```

`origin` is the screen-space center of the footprint diamond in the PNG. `anchor` is `origin / imageSize`. `sortPoint` is normally the bottom center of the footprint and should be used for render sorting.
