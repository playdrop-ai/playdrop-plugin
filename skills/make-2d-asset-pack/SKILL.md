---
name: make-2d-asset-pack
description: "Create, extract, validate, repair, and optionally package one or more transparent 2D game assets from AI-generated matte-backed images. Use for every generated sprite that requires real transparency, from one game-owned asset to multi-family reusable packs."
---

# Make 2D Asset Pack

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Turn a natural-language request for one sprite, a small game-owned set, a sheet, or a pack into retained AI source images and validated transparent PNGs. Create a PlayDrop `catalogue.json` only for a reusable pack. Production must use this workflow whenever generated gameplay art requires transparency; do not replace it with ad hoc background-removal scripts.

Read `references/production-contract.md` before processing art. Read `references/prompt-contract.md` before changing prompt behavior.

Use a supplied managed `runtime_python:` path when the execution environment provides one. Otherwise set up the shared pinned extraction runtime once:

```bash
python3 scripts/setup_runtime.py
```

Use the printed `runtime_python:` path as `ASSET_PACK_PY` in the commands below. Runtime installation time is setup overhead, not family throughput. The pinned runtime includes Pillow, NumPy, and `rembg==2.0.61`; rembg remains a third fallback, not the primary extractor.

## Request Contract

Translate the user's request into one small JSON file:

- **Single asset or small game-owned set:** one family with one slot per asset. The same matte extraction and validation gates apply even when there is only one slot.
- **Sheet:** one family, up to 16 slots. Start from `references/sheet-request.template.json`.
- **Pack:** several families. Start from `references/pack-request.template.json`.
- Paired large/small uses two slots per item, so one paired sheet supports at most eight items.
- `style.description` is required. `style.referenceImages` and `sourceFolder` are optional.
- For an extension family, set `families[].styleReferenceImages` to creator-owned approved family art. Jobs receive the canonical pack anchor first, then these family-continuity references, then the identity template.
- `metadata.tags`, when present, must be existing PlayDrop taxonomy refs in `group-slug/tag-slug` form. Use `playdrop tags browse --json` to choose them; never invent family, item, or variant tag groups.
- Use `matte: "auto"` or omit it. Preparation ranks saturated mattes against all available reference pixels and retains the scores; explicit mattes remain available for owner-directed cases.
- A source folder supplies identity references, not style, unless the user explicitly says otherwise.
- Preserve explicit item payloads. Otherwise derive a detailed large payload and a purpose-designed raw-64 small payload.

The request schema is `references/request.schema.json`. Freeze the request before generation:

```bash
$ASSET_PACK_PY scripts/prepare_request.py \
  --request /absolute/path/request.json \
  --output-root /absolute/path/asset-pack
```

This creates `request.json`, `pack-spec.json`, templates, prompts, family status, and claimable jobs. `--resume` verifies the frozen request and preserves all state byte-for-byte.

Review any `matte_review_required` warning before generation. It means even the safest candidate overlaps more than 0.2% of reference pixels; split the family or use item repairs instead of ignoring the warning.

If there is no style reference image, the first family is a bootstrap style job and the rest wait. Once its source is accepted, it becomes the canonical style anchor and all other families become ready. With a reference image, families are ready immediately.

## Production owner

- **Active Codex agent:** perform this complete workflow directly with built-in image generation.
- **Active Claude agent:** obtain the standard managed runtime path first, then delegate the complete transparent-asset job to one Codex CLI run as defined in `../make-assets/SKILL.md`. Provide the asset brief, exact output directory, this skill path, both reference contracts, and the runtime path. Codex must prepare the request, generate controlled-matte sources, ingest them, split and extract, run code validation, inspect every required board, make any allowed corrected retry, copy accepted game-owned PNGs into their final paths, and return a compact manifest containing path, dimensions, format, byte size, alpha result, and visual-review result. Claude only integrates files that the manifest marks accepted.

Do not split generation and extraction between Claude and Codex. Do not ask Codex merely for a transparent PNG. Do not replace this workflow with an ad hoc keyer. If the single Codex job fails after one evidence-based correction, retain the exact failure and stop clearly.

## Canonical Loop

For game-owned assets that remain embedded in one game, run the same generation, splitting, extraction, code validation, and Codex review steps below, then copy accepted transparent PNGs into the game and declare them in `ownedAssets`. The human approval and `finalize_pack.py` publication gates apply only when publishing a standalone reusable asset pack.

### 1. Claim And Generate

Inspect the queue:

```bash
$ASSET_PACK_PY scripts/status.py --pack-root /absolute/path/asset-pack --json
```

Claim one ready job per worker:

```bash
$ASSET_PACK_PY scripts/claim_job.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1 \
  --worker codex-1
```

The command prints the exact prompt, style references, identity template, and output path. Follow the production ownership rule in `../make-assets/SKILL.md`, with style references first and the identity template last. Never use a script to synthesize the art or swap its background.

For packs, run up to three independent generation jobs concurrently. Subagents may claim jobs when available, but the file queue is authoritative and the workflow must also work from one parent agent.

Immediately inspect every generated source sheet. Reject it before extraction for wrong count/order/identity, confused large/small roles, clipping, text, exterior shadow, floor/contact effects, or unreadable small icons. A mild value or hue gradient in an otherwise subject-safe matte is not sufficient reason to discard a source: retain it, run measured extraction, and decide from the extracted boards. Reject matte lighting that is tied to the object, such as a glow or grounding shadow.

Subject-safe means the generated subjects themselves do not reuse the matte color, even when the input references did not. The source hue detector is deliberately conservative and can confuse legitimate pink, blue, or green subject regions with a related matte hue. Keep that failure by default; after checker/white/purple/black inspection proves the subject is intact, use only the item-scoped extraction overrides documented below. Never apply a family-wide override to save one asset.

Record every success, rejection, and provider failure:

```bash
$ASSET_PACK_PY scripts/ingest_generation.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1 \
  --status success \
  --output /absolute/path/generated.png \
  --elapsed-seconds 31.2 \
  --source-review approve \
  --comment "Count, roles, matte, silhouettes, and shadows pass."
```

For a provider failure, omit the output and use `--status failed --error '<exact error>'`. For a bad source, ingest it with `--source-review reject`; rejected images remain evidence.

### 2. Split, Route Extraction, And Validate In Code

Process an accepted job once:

```bash
$ASSET_PACK_PY scripts/process_family.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --job generation-v1
```

The processor adaptively splits the actual generated dimensions, then routes each asset independently:

1. native hue-aware soft chroma and despill against the requested subject-safe matte;
2. hard color-key comparison when it does not remove subject pixels;
3. `rembg` only for assets still failing both chroma methods and only when its silhouette remains compatible.

It retains every attempt, selects the first code-passing result per asset, builds checker/white/purple/black/raw-64 boards, and writes provenance. It creates targeted repair jobs only when fewer than half the slots fail, combining a failed large/small pair for one item into one paired generation. Failure in at least half the sheet is classified as systemic and requests one full-sheet retry instead of fanning out into many item generations. `rembg` is an optional third fallback, never the family default.

Run at most two extraction processes concurrently. Family locks prevent duplicate processing, and writes are atomic.

### 3. Repair Without Regression

Generate only the listed repair jobs. A small-only repair must not redraw or replace approved large assets. Successful targeted extraction merges only requested variants and verifies prior hashes remain unchanged.

When a source itself fails, prepare one audited retry:

```bash
$ASSET_PACK_PY scripts/prepare_retry.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --reason "Source has an exterior cast shadow."
```

For a targeted retry, add `--mode small --items chair`. The code allows at most two generated full sheets per family/mode and two generated repair sources per asset/variant. Provider failures with no image do not consume a generated-source allowance. An owner exception requires `--override-limit` and is retained in the event log.

When human feedback changes the requested content rather than merely identifying a rendering defect, replace the stale slot payload structurally. Write a JSON file keyed by item id and variant, then pass it to the retry:

```json
{
  "baseball": {
    "large": "One complete baseball together with one complete readable baseball bat."
  }
}
```

```bash
$ASSET_PACK_PY scripts/prepare_retry.py \
  --pack-root /absolute/path/asset-pack \
  --family sports \
  --mode large \
  --items baseball \
  --payload-overrides /absolute/path/payload-overrides.json \
  --reason "Human review requires a bat in the large asset."
```

The override is copied into the immutable job, replaces the old payload in both the identity template and prompt, and suppresses any conflicting old visual reference for that slot. The retry correction is authoritative over generic constraints. Targeted repairs also receive the latest code-approved full-family source as an additional style-continuity image when one exists; the prompt image numbering and provenance must include it.

Regenerate instead of accepting manual painting, broad cleanup, unsafe matte overlap, broken thin details, or shadow remnants.

When a deterministic extractor improves, reprocess a retained approved source into a new immutable round without spending an AI-generation allowance:

```bash
$ASSET_PACK_PY scripts/prepare_reextract.py \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --from-job generation-v1 \
  --reason "Hue-aware chroma extraction added."
```

Then pass the printed `reextract-vN` job to `process_family.py`. Never overwrite the earlier extraction round.

If a retained source was rejected only for matte uniformity but a diagnostic extraction proves its sprites are clean, prepare an extraction-only audit round with `--override-source-review`. The original rejection remains linked and the override reason is recorded. For false-positive code warnings on visually inspected assets, use the narrowest applicable `process_family.py` option: `--allow-source-hue-overlap-items`, `--allow-matte-warning-items`, or `--allow-source-crop-edge-items`. If a subject-safe diagnostic proves that `finish_chroma_edge` removes a fringe without changing the subject, opt that item into `--force-hue-cleanup-items`; if it visibly punches holes into an otherwise clean extraction, opt only that item into `--skip-hue-cleanup-items`. Retain the before/after boards. Each option takes comma-separated item ids and is written to metrics, provenance, status, and events. Do not use these options for lost subject color from the base extractor, a visibly clipped silhouette, actual matte residue, or shadow remnants; regenerate that variant instead.

### 4. Review In Order

Code approval is automatic and blocks later gates on failure. Then Codex must visually inspect:

- the source sheet and split overlay;
- every transparent asset on checker, white, purple, and black;
- every small asset at raw `64x64`;
- identity, payload, view, simplification, style, shadow, residue, clipping, and disconnected detail.

Record Codex approval only after inspection:

```bash
$ASSET_PACK_PY scripts/record_review.py \
  --status /absolute/path/asset-pack/families/furniture/family-status.json \
  --reviewer codex \
  --decision approve \
  --comment "All source and extracted-asset checks pass."
```

Human approval is final. Start the local review server when a review page is useful:

```bash
$ASSET_PACK_PY scripts/review_server.py --pack-root /absolute/path/asset-pack --port 4177
```

If the owner approves or rejects explicitly in chat, do not send them back to the webpage. Relay their exact message to the same review server and audit log:

```bash
$ASSET_PACK_PY scripts/relay_human_review.py \
  --server http://127.0.0.1:4177 \
  --family furniture \
  --decision approve \
  --user-text "I approve furniture."
```

Never infer approval from silence or general praise. Every accepted family requires code, Codex, and explicit human approval.

### 5. Finalize For PlayDrop

After all families are human-approved:

```bash
$ASSET_PACK_PY scripts/finalize_pack.py \
  --pack-root /absolute/path/asset-pack \
  --validate
```

This creates a PlayDrop asset-pack `catalogue.json` from approved transparent PNGs and runs local validation. Public release remains blocked unless `publicationRights` is `cleared`; private templates and third-party reference pixels never enter the distributable pack.

## Performance Contract

Targets tracked by `status.py --json`: at most 300 active seconds per family to code and Codex approval (600 needs a recorded reason), 900 seconds wall time for a clean five-family wave, 1,500 for a repair wave. Human response time is excluded. Report idle latency and active time separately, keep timings in job/status files, and do not hide retries.

## State And Safety

```text
asset-pack/
  request.json
  pack-spec.json
  pack-status.json
  generation-ledger.csv
  human-review-log.jsonl
  catalogue.json
  style-anchor/
  private-reference-inputs/
  families/<family>/
    jobs/*.json
    events.jsonl
    family-status.json
    private-templates/
    prompts/
    generated/
    extraction-rounds/
    validation/
    approved/
```

- JSON files are the source of truth; agents and optional subagents are replaceable workers.
- Never overwrite prompts, generations, extraction rounds, reviews, or approved assets.
- Keep one canonical style anchor in every non-bootstrap generation call.
- Choose a matte color absent from every subject; there is no universal green or magenta. Judge generated matte gradients by extraction evidence, not by appearance alone.
- Keep internal form shading; reject every exterior cast/contact/floor shadow.
- Do not use `process_sheet.py` for normal production. It is retained for diagnostics and method experiments; `process_family.py` is canonical.
- Do not bypass code gates or fabricate a human decision.

## Development Check

The synthetic suite covers request preparation, text-only bootstrap, concurrent claims, failed-call logging, hue-aware chroma, generated-subject matte conflicts, systemic retry routing, immutable re-extraction, targeted repair merge, non-regression, hard retry limits, all review gates, manifests, rights, and catalogue output:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```
