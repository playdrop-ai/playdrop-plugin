# Prompt Contract

Use the generated prompt from `scripts/build_prompt.py` as the base. Add family-specific art direction only when it makes a requirement more concrete. Do not weaken any constraint below.

## Inputs

- Image 1 is the canonical style anchor. It controls rendering, color balance, silhouette language, internal shading, and overall polish. Ignore its subject identity and background.
- Image 2 is the identity template. It controls the exact item list, slot order, pairing, required payload, and target view. Ignore its original visual style.
- For semantic-only items, the written per-slot payload is authoritative.

## Style

Use polished top-tier casual mobile game rendering with friendly rounded construction, clean silhouettes, balanced saturated color, and controlled internal form shading. Match the supplied creator-owned style anchor closely. Do not invent a generic matte illustration style. Avoid hard glossy plastic-toy material.

## Large Variant

Large assets must be detailed, dimensional, and perspective-aware when the object benefits from depth. Keep every silhouette complete and readable. Use sturdy geometry for thin parts.

## Small Variant

Small assets must be purpose-designed for `64x64`, not resized or cropped large assets. Use strict front or pure side orthographic views, a bold silhouette, few broad color regions, minimal internal lines, and no material grain or tiny texture. Follow the small payload literally even when it contains fewer objects than the large payload.

## Matte

Name the exact matte color and hex value. State that it is absent from every subject. Require every exterior pixel to be that uniform solid color. Do not ask for a transparent background in the generation call because extraction needs a controlled matte.

## Forbidden Content

Forbid all exterior cast shadow, contact shadow, floor blob, ambient shadow outside the silhouette, reflection, glow, gradient, texture, floor plane, clipping, watermark, logo, text, label, number, divider, frame, people, overlap, and extra prop.

## Sheet Contract

- State the exact rows, columns, slot count, order, item, variant, and payload.
- Ask for one complete asset composition per slot with generous padding.
- Require stable, equal invisible cells without visible dividers.
- Do not require exact output pixels from the image model. The extraction script scales template geometry to the actual output.
- Reject the source if any slot is missing, duplicated, swapped, clipped, or assigned the wrong size role.

## Repair Prompt

For a repair, name what stays approved and what failed. Generate a template and prompt containing only the failed item ids and variants. Include the original authoritative references when the payload is unchanged. When owner feedback changes the content contract, replace the stale payload structurally, suppress conflicting old visual references for that slot, and state that the correction overrides generic constraints. Include the latest code-approved full-family source as a style-only continuity input when available. Do not ask the model to redraw approved assets merely to preserve sheet shape. Do not ask the model to edit a prior matte while preserving pixels; background edits redraw subjects.
