# Prompt Contract

Use `scripts/build_prompt.py` as the base. Add art direction only when it makes a requirement more concrete.

## Inputs

- Style references control rendering, palette, silhouette language, internal shading, and polish. Ignore their subjects and backgrounds.
- The identity template controls the exact asset list, order, payloads, and output contracts. Ignore its visual style.
- A written item payload is authoritative.

## Matte

- Name the exact matte color and hex value.
- Require every exterior pixel to use that uniform solid color.
- Forbid the matte color inside every subject.
- Ask for a solid matte, not transparency, because extraction needs a controlled background.

## Sheet

- State exact rows, columns, count, order, item name, payload, and output contract.
- Ask for one complete independent asset per slot with generous padding and stable invisible cells.
- Forbid overlaps, visible dividers, text, labels, numbers, frames, people, unrequested props, exterior shadows, floor effects, reflection, glow, clipping, watermarks, and logos.
- Reject any missing, duplicated, swapped, or clipped asset.

## Repair

- Include only failed item ids.
- Preserve approved assets outside the repair.
- When owner feedback changes content, replace that item's payload structurally and suppress its conflicting identity reference.
- Include the latest approved family source as style-only continuity when available.
- Do not ask the model to edit a prior matte while preserving pixels. Treat every generated image as a new source.
