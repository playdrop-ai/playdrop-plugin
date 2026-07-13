# Generated Asset Sheet

Use this when catalogue packs and individual assets cannot cover a coherent gameplay need. Derive the visual language from the approved art-direction board or a creator-owned canonical style anchor.

## Choose The Workflow

- For six or fewer unrelated images, generate individual assets with native tooling.
- For a production pack, more than one sheet, repeated families, paired large/small variants, transparent PNG extraction, or repair and approval rounds, use the `make-2d-asset-pack` skill.
- For one lightweight game sheet with more than six assets, follow the same source and extraction rules below even when the full pack workflow would be excessive.

## Generation Path

Use built-in image generation when it can persist PNG files. Builder tasks must never spend PlayDrop credits. If the task requires generated media and native generation cannot produce a file, fail clearly with `native_image_generation_artifact_missing`.

Use an exact slot list and a clean invisible grid. Every asset must be isolated, centered, complete, and readable at its gameplay size. Forbid labels, numbers, dividers, frames, overlaps, clipping, floor planes, and every exterior cast or contact shadow. Internal form shading is allowed.

Pick a saturated solid matte that is absent from every subject in the sheet. Green is not a universal choice. Never ask the model to change only the background of an existing sheet and then treat both results as pixel-identical; AI edits redraw subjects.

## Extraction

Do not crop on nominal equal-grid boundaries. Generated sheets can drift across cell boundaries and can differ from template dimensions. Scale the intended layout to the actual source and find row and column gaps from the measured matte.

Select one extraction method explicitly:

- soft chroma when the requested matte is absent from every subject
- hard color key when the matte is flat and safely separated
- `rembg` when chroma extraction conflicts with valid subject color

Measure the matte and record thresholds. Use the requested matte as the removal key. Keep despill disabled unless a visible fringe is proven and cleanup cannot damage valid subject color.

Generate checker, white, purple, and black review boards. Check output count, dimensions, alpha occupancy, edge contact, disconnected fragments, matte residue, and provenance before visual review. When extraction or identity fails, preserve the evidence and create a new named round. Repair only failed assets or variants after two full-sheet attempts.
