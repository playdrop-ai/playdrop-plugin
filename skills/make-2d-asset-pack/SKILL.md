---
name: make-2d-asset-pack
description: "Create, extract, validate, repair, and optionally package transparent 2D game assets from AI-generated matte-backed images. Use for one game-owned asset, a multi-item sheet, or a reusable PlayDrop asset pack."
---

# Make 2D Asset Pack

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this workflow whenever generated gameplay art needs real transparency. It supports individual assets, multi-item sheets, extraction, validation, repair, and reusable packs. A pack is only a container of independent assets. Each request item produces one independent asset with its own payload, optional identity reference, and output contract.

Read `references/production-contract.md` before processing art and `references/prompt-contract.md` before changing prompts.

Use a supplied `runtime_python:` path. Otherwise install the shared pinned runtime once:

```bash
python3 scripts/setup_runtime.py
```

Use the printed path as `ASSET_PACK_PY` below.

## Request

- One asset or game-owned set: one family with one item per asset.
- Sheet: one family with at most 16 independent assets. Start from `references/sheet-request.template.json`.
- Pack: one or more families. Start from `references/pack-request.template.json`.
- Each object item requires a non-empty `name`; `id` and `payload` do not replace it. The author supplies display names for assets it chose.
- `output` defines the default width, height, padding, and visual contract. An item may override it.
- `style.description` is required. Style references and `sourceFolder` are optional.
- `metadata.tags` must be existing PlayDrop taxonomy refs. Use `playdrop tags browse --json`.
- Use `matte: "auto"` unless the owner specifies a subject-safe matte.
- Preserve explicit item payloads. Do not invent a relationship between separately named assets.

Freeze the request:

```bash
$ASSET_PACK_PY scripts/prepare_request.py \
  --request /absolute/path/request.json \
  --output-root /absolute/path/asset-pack
```

Successful preparation writes the frozen request, normalized spec, prompts, templates, status, and claimable family jobs. If preparation rejects a locally authored raw request, correct the named input defect and rerun preparation before generating art. A rejected raw request is not frozen output or missing creator input. Preserve successfully prepared state; `--resume` accepts only the same frozen request.

Without a style reference, the first family bootstraps the canonical style and later families wait for it. With a style reference, all families can start immediately.

## Production owner

Use exactly one owner for the whole image job:

- Active Codex agent: use Codex image generation and own generation, transforms, validation, visual inspection, retries, and manifest.
- Active Grok agent: use Grok's own image generation and own generation, transforms, validation, visual inspection, retries, and manifest. Never delegate image generation to Codex.
- Active Claude agent: delegate the complete job to one Codex CLI run as defined in `../make-assets/SKILL.md`; Claude only integrates accepted outputs.

Do not split one job between owners or switch owners after failure. Retain the exact failure and stop after the allowed evidence-based correction.

## Workflow

### 1. Claim and generate

```bash
$ASSET_PACK_PY scripts/status.py --pack-root /absolute/path/asset-pack --json
$ASSET_PACK_PY scripts/claim_job.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1 \
  --worker agent-1
```

The claim prints the prompt, style references, identity template, and output path. Supply style references first and the identity template last. Generate the art on the requested solid matte. Do not synthesize it with code.

Inspect the source immediately. Reject wrong count, order, identity, payload, clipping, text, exterior shadows, floor effects, or subject use of the matte color. Record every provider failure, rejected source, and accepted source:

```bash
$ASSET_PACK_PY scripts/ingest_generation.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1 \
  --status success \
  --output /absolute/path/generated.png \
  --source-review approve \
  --comment "Count, payloads, matte, silhouettes, and shadows pass."
```

### 2. Extract and validate

```bash
$ASSET_PACK_PY scripts/process_family.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1
```

The processor adaptively splits the source, routes each asset through the configured extraction methods, validates dimensions, alpha, edges, fragments, matte residue, hashes, and provenance, then creates checker, white, purple, black, and split-overlay review boards. It retains every attempt.

When fewer than half the requested assets fail, it prepares independent item repair jobs. When at least half fail, prepare one full-sheet retry. Run at most three generation jobs and two extraction jobs concurrently.

### 3. Repair without regression

Full-sheet retry:

```bash
$ASSET_PACK_PY scripts/prepare_retry.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --reason "Source has exterior cast shadows."
```

Targeted retry: add `--items chair`. A payload correction file is a JSON object keyed directly by item id:

```json
{
  "chair": "One complete wooden dining chair with four visible legs."
}
```

Pass it with `--payload-overrides /absolute/path/payload-overrides.json`. The repair replaces only the named independent assets and preserves accepted hashes for everything else. Two generated full sheets per family and two repair sources per asset are allowed unless the owner explicitly uses `--override-limit`.

To reprocess a retained source after a deterministic extractor improvement:

```bash
$ASSET_PACK_PY scripts/prepare_reextract.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --from-job generation-v1 \
  --reason "Extraction method improved."
```

For a proven false-positive code warning, use only the narrow item-scoped `process_family.py` override that matches the evidence. Never use an override for clipped art, lost subject color, real matte residue, or shadow remnants.

### 4. Review

After code approval, the production agent inspects the source, split overlay, and every extracted asset on all four backgrounds. Check identity, payload, visual contract, style, silhouette, shadows, residue, clipping, and disconnected detail.

```bash
$ASSET_PACK_PY scripts/record_review.py \
  --status /absolute/path/asset-pack/families/furniture/family-status.json \
  --reviewer <codex|grok> \
  --decision approve \
  --comment "All source and extracted-asset checks pass."
```

Use `codex` or `grok` for the actual image-production owner. For game-owned assets, copy accepted PNGs into the game after code and agent review. For a standalone reusable pack, explicit human approval is also required:

```bash
$ASSET_PACK_PY scripts/review_server.py --pack-root /absolute/path/asset-pack --port 4177
```

Never infer human approval.

### 5. Finalize a reusable pack

```bash
$ASSET_PACK_PY scripts/finalize_pack.py \
  --pack-root /absolute/path/asset-pack \
  --validate
```

This writes `catalogue.json` from approved transparent PNGs. Public release requires `publicationRights: "cleared"`. Reference pixels and private templates never enter the distributable pack.

## State

- JSON files are authoritative. Never overwrite prompts, generations, extraction rounds, reviews, or approved assets.
- Keep one canonical style anchor in every non-bootstrap generation call.
- Keep internal form shading. Reject exterior cast, contact, floor shadows, and glows.
- `process_family.py` is the only extraction command. `process_sheet.py` is its internal image-processing library and must not be invoked directly.
- Do not bypass code gates or fabricate a human decision.

## Development check

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```
