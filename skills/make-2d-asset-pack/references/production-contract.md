# Production Contract

This contract is based on a discovery run and a human-approved 44-PNG pilot spanning Furniture, Sports, and Flowers. It is a starting contract, not a claim that every family will behave identically.

## Generation

- Use Codex built-in image generation.
- Attach one creator-owned canonical style anchor to every call.
- Attach one identity template when exact items, order, or view semantics matter.
- Use multi-item sheets as the primary efficiency path.
- Cap a sheet at 16 slots.
- Pair large and small variants by default only when every slot has an explicit payload contract.
- Large assets are detailed, dimensional, and perspective-aware where appropriate.
- Small assets are purpose-designed icons with strict front or pure side orthographic views, broad shapes, few details, and raw `64x64` readability.
- Require a uniform solid matte outside every silhouette.
- Forbid exterior cast shadows, contact shadows, floor blobs, ambient shadows outside the silhouette, reflections, glow, texture, gradients, floor planes, text, labels, frames, and clipping.
- Allow lighting and form shading only inside silhouettes.

## Splitting

- Generated image dimensions may differ from the supplied template. Scale all nominal geometry to the actual source dimensions.
- Model output can drift across nominal cell boundaries. Equal-grid crops are diagnostic only.
- Use matte-gap adaptive row and column boundaries.
- Save a split overlay for every source before accepting crops.

## Matte And Extraction

- Select mattes from the expected subject palette, not from a universal family default.
- Use the requested matte color as the chroma removal key. Measure the real matte for diagnostics and adaptive splitting, but do not silently replace the requested key with a generated median.
- Derive soft thresholds from measured border distances and record them.
- Prefer native soft chroma when the matte is absent from the subject.
- Keep despill disabled by default. It can destroy valid red, purple, green, or blue subject colors.
- Select `rembg` explicitly when chroma extraction is incompatible with the subject or generated matte.
- Use hard color key only when the matte is flat and safely absent from the subject.
- AI background edits are new generations, not pixel-paired mattes. Never combine two AI generations as if the subjects were pixel-identical.
- Do not accept fragile manual painting or broad cleanup as production extraction. Regenerate instead.

## Validation

Validation proceeds in this order:

1. Code checks count, dimensions, alpha occupancy, edge contact, disconnected fragments, matte residue, output hashes, and provenance.
2. Codex checks identity, requested payload, large perspective, small orientation and simplification, style coherence, exterior shadows, residue, clipping, and edge integrity.
3. A human gives the final family approval or rejection with an optional comment.

Generate checker, white, purple, and black review boards. Also inspect every small PNG at raw `64x64`. Review boards support inspection but do not replace it.

Raw `64x64` inspection is the mandatory small-asset gate. A real-game board is optional rather than mandatory by owner decision on 2026-07-13 because the target card UI displays item labels; use an in-game board whenever labels may be absent or ambiguity would affect play.

Codex review remains calibrated work. Preserve human-found defects and use them to tighten later checks. A previous pilot caught that a readable small icon can still be wrong when it copies the large payload instead of the original small payload.

## Retry And Retention

- Keep at most two distinct full-sheet AI sources per family and mode. Re-extractions of the same source do not consume another generation.
- Keep at most two distinct item-specific repair sources per asset and variant.
- Enforce both limits in code. An owner-directed `--override-limit` is allowed only when it is retained in round history.
- Never overwrite a prompt, source, crop, extraction, metric file, board, or review decision.
- A rejected small set must not replace approved large assets.
- Preserve the selected source and extraction method per asset in `family-status.json`.

## Approval And Publication

- `code`, `codex`, and `human` are separate approval fields.
- Default every family to unapproved.
- Promote assets only after code and Codex pass and the human approves the family.
- Accept human decisions only through the local review server; the Codex review CLI cannot set the human gate.
- Regenerate and verify the approved manifest after every human approval.
- Exclude third-party references and private templates from the distributable pack.
- Block public release whenever reference or conditioning rights are unresolved.
