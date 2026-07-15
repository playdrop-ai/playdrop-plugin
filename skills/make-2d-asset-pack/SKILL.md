---
name: make-2d-asset-pack
description: "Create, extract, validate, repair, and package consistent transparent 2D game assets from AI-generated multi-item sheets. Use when asked to make one asset sheet or a multi-family asset pack from item lists, an art-style description or reference image, and optional source references; supports paired large/small variants, parallel family jobs, PlayDrop metadata, and code/Codex/human approval."
---

# Make 2D Asset Pack

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Turn a natural-language sheet or pack request into retained AI source sheets, validated transparent PNGs, and a PlayDrop `catalogue.json`. Production must use this workflow; do not replace it with family-specific scripts.

Read `references/production-contract.md` before processing art. Read `references/prompt-contract.md` before changing prompt behavior.

Set up the shared pinned extraction runtime once, then use the printed Python path for all skill scripts:

```bash
python3 scripts/setup_runtime.py
```

Use the printed `runtime_python:` path as `ASSET_PACK_PY` in the commands below. Runtime installation time is setup overhead, not family throughput. The pinned runtime includes Pillow, NumPy, and `rembg==2.0.61`; rembg remains a third fallback, not the primary extractor.

## Request Contract

Translate the user's request into one small JSON file:

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

## Canonical Loop

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

The command prints the exact prompt, style references, identity template, and output path. Invoke Codex built-in image generation with style references first and the identity template last. Never use a script to synthesize the art or swap its background.

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

- Target median: at most 300 active seconds per family from first claim to code and Codex approval.
- Slow-family threshold: 600 seconds. Crossing it requires a recorded reason.
- Clean five-family wave target: 900 seconds wall time with generation concurrency 3 and extraction concurrency 2.
- Repair wave target: 1,500 seconds wall time.
- Human response time is reported separately and excluded from automation throughput.

Use `status.py --families animals,drinks,chess --json` after each wave. It reports idle queue latency and active production separately; report both, and use active time for the five-minute production target. Keep generation, extraction, review, and total wall timings in job/status files. Do not hide retries or count only retained successes.

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
