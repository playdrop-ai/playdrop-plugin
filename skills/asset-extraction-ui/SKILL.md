---
name: asset-extraction-ui
description: "Use when extracting UI components, tokens, states, HUD elements, icons, or implementation-ready UI assets from approved PlayDrop art direction or screen mockups."
---

# Asset Extraction UI

Use this skill when the user provides an image or mockup and asks to extract one or more UI elements into game-ready UI assets.

This skill does the extraction. Do not stop at an extraction plan.

## Workflow

1. Identify every requested element and classify its design-system role: `Card`, `Container`, `Button`, `Custom Button`, `Progress Bar`, `Badge`, `HUD Panel`, `Icon`, `Input`, `Dialog`, or a tighter role that fits the image.
2. Create a run folder under `tmp/asset-extraction-ui/<slug>/` for prompts, generated matte images, validation previews, reports, and experiments.
3. Ensure transient files are not committed or uploaded: add `tmp/` to `.gitignore` and `.playdropignore` when those files exist or when creating them is appropriate for the game repo.
4. For each element, use AI image generation/editing to isolate only that element into one flat-background image:
   - use pure black `#000000` when the element does not contain black
   - otherwise use pure white `#ffffff` when the element does not contain white
   - otherwise use bright green `#00ff00`, bright purple `#ff00ff`, or bright red `#ff0000`, choosing the color least present in the element
5. Pass that same generated image back to AI image generation/editing and strongly request that only the background changes to the second matte color:
   - default second matte is bright green `#00ff00`
   - if the first matte is bright green, use bright purple `#ff00ff` when safe, otherwise bright red `#ff0000`
   - require identical element pixels, identical crop, identical scale, no redraw, no cleanup, no antialiasing changes, no lighting changes
6. Run the shared background-swap alpha extractor from the PlayDrop plugin root. If the current working directory is the game repo, use the absolute path to the plugin script or copy the command path from the active skill cache; do not assume the game repo has this script:
   ```bash
   node <playdrop-plugin>/scripts/extract-alpha-background-swap.ts \
     --base tmp/asset-extraction-ui/<slug>/<element>-matte-a.png \
     --swap tmp/asset-extraction-ui/<slug>/<element>-matte-b.png \
     --out assets/ui/<element>.png \
     --base-bg '#000000' \
     --swap-bg '#00ff00' \
     --background-threshold 40 \
     --same-threshold 8 \
     --preview-bg '#ff00ff' \
     --preview-out tmp/asset-extraction-ui/<slug>/<element>-preview.png \
     --contact-sheet-out tmp/asset-extraction-ui/<slug>/<element>-contact-sheet.png \
     --report tmp/asset-extraction-ui/<slug>/<element>-report.json
   ```
7. Validate the transparent PNG visually on bright contact-sheet backgrounds not used by the element. Check for bleeding, holes, unwanted matte color, clipped shadows, distorted corners, and missing internal transparency. Do not reject only because the report has many matte or semi-transparent pixels; bevels, antialiasing, glow, shadows, and AI matte drift can legitimately create them.
8. If the visual cut is not precise, retry in this order: adjust extractor thresholds, regenerate the second matte with stronger "change background only" instructions, then regenerate both isolated matte images. Threshold sweeps such as `--background-threshold 40`, `50`, and `60` are usually faster than regenerating and should be judged by the contact sheet.
9. For scalable UI, define and debug 9-slice metadata. Render stretch previews at small, normal, and large sizes before accepting the values.
10. Define the content area when applicable by overlaying a bright 50% opacity rectangle or circle on the element and iterating until label/content placement is correct.
11. Move only accepted transparent PNGs into `assets/ui/`.
12. Add or update `ui-kit.json` in the game root with the element name, role, image path, scale mode, 9-slice values, content area, source image, and extraction notes.

## Prompt Pattern

For the first matte image:

```text
From the supplied image, isolate only the UI element named "<element>".
Reconstruct occluded or repeated decorative parts only when necessary to make the element usable as a standalone game UI asset.
Put the isolated element on a perfectly flat solid <matte-a> background.
Do not add a shadow unless it belongs to the element. Do not include surrounding UI, text, icons, characters, or other components unless they are part of this exact element.
Keep the original style, border treatment, lighting, texture, scale, and proportions.
Output a tightly cropped PNG with clean padding.
```

For the second matte image:

```text
Take the previous isolated UI element image and change ONLY the flat background color to <matte-b>.
The UI element must remain pixel-identical: same crop, same size, same antialiasing, same shadows, same colors, same texture, same edges.
Do not redraw, enhance, simplify, sharpen, blur, recolor, relight, or move the element.
```

## UI Metadata

Register each accepted asset in `ui-kit.json`:

```json
{
  "elements": [
    {
      "name": "advisor-panel",
      "role": "Container",
      "image": "assets/ui/advisor-panel.png",
      "scaleMode": "nine-slice",
      "nineSlice": { "left": 18, "right": 18, "top": 18, "bottom": 18 },
      "contentArea": { "x": 28, "y": 24, "width": 188, "height": 96 },
      "states": ["default"],
      "source": "tmp/asset-extraction-ui/<slug>/source.png"
    }
  ]
}
```

Use `scaleMode: "fixed"` for hardcoded or non-scalable controls such as close buttons.
