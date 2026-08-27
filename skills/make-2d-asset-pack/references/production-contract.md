# Production Contract

## Model

- A pack is a container of independent assets.
- Each item produces exactly one asset with one payload, optional identity reference, and explicit output contract.
- Use a multi-item sheet only to generate independent assets efficiently.
- Cap each sheet at 16 assets.
- Use one production owner for generation, transforms, validation, visual review, repairs, and the accepted-file manifest.
- Codex uses Codex image generation. Grok uses Grok image generation. Claude delegates the complete image job to Codex as defined in `../../make-assets/SKILL.md`.

## Generation

- Attach one creator-authorized canonical style anchor to every non-bootstrap call.
- Attach the generated identity template when exact item order or payload matters.
- Require a uniform solid matte outside every silhouette.
- Forbid exterior cast and contact shadows, floor effects, reflections, glow, background texture, text, labels, frames, and clipping.
- Allow lighting and form shading only inside silhouettes.
- Retain all source attempts, including provider failures and visual rejections.

## Splitting and extraction

- Scale nominal grid geometry to actual generated dimensions.
- Use matte-gap adaptive boundaries and save a split overlay.
- Rank matte candidates against available reference pixels and keep the requested matte as the extraction key.
- Route each asset independently through soft chroma, hard key, then rembg when needed.
- Reject subject loss, silhouette drift, crop-edge contact, matte-colored subject overlap, residue, and disconnected fragments.
- Do not repair production assets with manual painting or broad cleanup.

## Validation

1. Code checks count, dimensions, alpha, edge contact, fragments, matte residue, hashes, and provenance.
2. The production agent checks identity, payload, output contract, style, shadows, residue, clipping, and edge integrity on the source, split overlay, and all review backgrounds.
3. A human approves only standalone reusable packs.

## Retry and retention

- Keep at most two generated full-sheet sources per family and two generated repair sources per asset.
- When at least half a sheet fails, use one full-sheet retry. Otherwise repair only failed assets.
- A targeted repair must preserve all accepted asset hashes outside its item list.
- A deterministic extractor update may create a new immutable extraction round without consuming a generation allowance.
- Never overwrite a prompt, source, crop, extraction, metric, board, or review decision.

## Publication

- Game-owned assets need code and production-agent approval.
- Standalone reusable packs also need explicit human approval.
- Exclude references and private templates from the distributable pack.
- Block public release unless publication rights are cleared.
