---
name: make-2d-asset-pack
description: "Build, extract, validate, repair, and approve consistent transparent 2D asset packs made from multi-item AI image sheets. Use for sprite or icon families, paired large and small variants, repeated sheets, chroma-key or rembg extraction, and human-reviewed pack production."
---

# Make 2D Asset Pack

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Build coherent PNG asset packs with Codex image generation, deterministic extraction, and explicit code, Codex, and human gates. Use this workflow for production sets, not for six or fewer unrelated images.

The scripts require Python 3.10 or newer, Pillow, and NumPy. The `rembg` package is optional and required only when `--method rembg` is selected.

## Non-Negotiable Rules

- Freeze a `pack-spec.json` before generation. Validate it against `references/pack-spec.schema.json`.
- Use one creator-owned canonical style anchor in every generation call.
- Treat identity references and the style anchor as different inputs. The identity template controls items, order, and views. The style anchor controls rendering.
- Keep private or third-party reference pixels out of published packs, plugin artifacts, review bundles, and public repositories. Block publication until rights are documented.
- Generate every source matte with the image model. Never create an alternate AI source by script-swapping its background.
- Preserve every generation, prompt, extraction attempt, measurement, and review decision. Never overwrite prior rounds.
- Select the matte and extraction method explicitly per family or per asset. Never silently switch methods.
- Require final human approval for each family. Code and Codex approval cannot substitute for it.

Read `references/production-contract.md` before starting. Read `references/prompt-contract.md` before generating the first sheet or any repair.

## Output Layout

Use this structure unless the project already has an equivalent documented layout:

```text
asset-pack/
  pack-spec.json
  generation-ledger.csv
  approved-manifest.json
  human-review-log.jsonl
  style-anchor/
  families/<family>/
    private-templates/
    prompts/
    generated/
    extraction-rounds/<round>/
      crops/
      extracted/
      metrics.json
      provenance.json
    validation/<round>/
    approved/
    family-status.json
```

Keep only approved outputs in `approved/`. Keep rejected evidence in its round directory.

## Workflow

### 1. Freeze Scope And Rights

1. List every family, item, large payload, small payload, output size, and reference path in `pack-spec.json`.
2. Mark each item `visual-reference` or `semantic-only`.
3. Record ownership and publication permission for the style anchor, references, and generated output.
4. Stop publication when any required right is unresolved. Private experimentation may continue in a clearly private directory.

Validate scope and local reference coverage before making a template:

```bash
python3 scripts/validate_spec.py \
  --spec /absolute/path/pack-spec.json \
  --report /absolute/path/spec-validation.json
```

Add `--for-publication` before packaging. It hard-fails unless `pack.publicationRights` is `cleared`; ordinary private production emits a warning instead.

### 2. Build The Private Identity Template

Create a layout-only identity sheet from the spec:

```bash
python3 scripts/build_template.py \
  --spec /absolute/path/pack-spec.json \
  --family furniture \
  --mode paired \
  --output-dir /absolute/path/families/furniture/private-templates
```

The script composes provided references; it does not create art. For semantic-only items it creates a text placeholder. Do not publish the resulting template when it embeds restricted references.

Use paired large/small sheets by default, with at most 16 slots. Use a separate large-only or small-only sheet when paired generations repeatedly confuse roles, simplify the wrong payload, or lose effective cell resolution.

For a targeted repair, add `--items chair,desk` to both `build_template.py` and `build_prompt.py`. This creates only the requested slots while preserving authoritative family order.

### 3. Choose A Subject-Safe Matte

Inspect the expected subject palette before generating. Pick a matte absent from every subject in that sheet. Prefer saturated magenta, green, blue, red, cyan, yellow, violet, white, or black only when that color is safely absent.

Do not assume green is universal. White animals, green plants, red flowers, and magenta sports equipment all require different choices. Generate a new source when the selected matte overlaps valid subject color.

### 4. Build And Record The Prompt

Generate a reproducible prompt from the spec:

```bash
python3 scripts/build_prompt.py \
  --spec /absolute/path/pack-spec.json \
  --family furniture \
  --mode paired \
  --matte '#ff00ff' \
  --output /absolute/path/families/furniture/prompts/paired-v1.txt
```

Attach the canonical style anchor as Image 1 and the private identity template as Image 2. Use Codex built-in image generation. Persist the exact output and append the call, input hashes, prompt hash, elapsed time, success, and error to `generation-ledger.csv`.

Copy the style anchor, identity template, prompt, and generated source into the pack root before recording them. The ledger rejects out-of-root paths so provenance stays portable and does not leak local usernames.

```bash
python3 scripts/record_generation.py \
  --ledger /absolute/path/generation-ledger.csv \
  --family furniture \
  --mode paired \
  --attempt 1 \
  --status success \
  --prompt /absolute/path/prompts/paired-v1.txt \
  --style-anchor /absolute/path/style-anchor.png \
  --identity-template /absolute/path/private-templates/furniture-paired-identity-template.png \
  --output /absolute/path/generated/paired-v1.png
```

Record provider failures too, with `--status failed --error '<exact error>'` and no output. Do not keep a success-only ledger.

Reject the source before extraction when it has the wrong slot count, identity, order, size role, matte, clipping, text, exterior shadow, floor contact, glow, or unreadable small icons.

### 5. Split And Extract Explicitly

Run one selected method at a time:

```bash
python3 scripts/process_sheet.py \
  --spec /absolute/path/pack-spec.json \
  --family furniture \
  --mode paired \
  --source /absolute/path/families/furniture/generated/paired-v1.png \
  --prompt /absolute/path/families/furniture/prompts/paired-v1.txt \
  --identity-template /absolute/path/families/furniture/private-templates/furniture-paired-identity-template.png \
  --matte '#ff00ff' \
  --method soft-chroma \
  --round paired-v1 \
  --output-root /absolute/path/asset-pack
```

Use the same `--items` list for item-specific extraction. The processor merges successful requested variants with prior selected assets and leaves every unrequested variant byte-identical.

Available methods are `soft-chroma`, `hard-key`, and `rembg`. `soft-chroma` is primary when the matte is absent from subjects. Keep despill off unless a visible fringe is proven and the cleanup cannot remove valid subject color. `rembg` must be explicitly selected and requires the optional `rembg` package.

The processor measures the real matte, finds adaptive row and column gaps, scales to the generated image dimensions, writes every crop and PNG, creates review boards, and records provenance. It never chooses another extraction method automatically.

If the selected method fails, inspect the evidence and deliberately start a new round in this order:

1. Re-extract the same AI source with another explicit method.
2. Generate a new source with a subject-safe matte.
3. Generate an item-specific or variant-specific repair source.

The processor enforces at most two distinct full-sheet AI sources per family and mode and two distinct item-repair sources per asset. Re-extracting the same AI source with another explicit method does not consume another generation. A deliberate owner exception requires `--override-limit`; the override is recorded in `roundHistory` and `lastAttempt`.

### 6. Gate In Order

Run the manifest and image checks first:

```bash
python3 scripts/verify_pack.py \
  --spec /absolute/path/pack-spec.json \
  --pack-root /absolute/path/asset-pack \
  --family furniture
```

The code gate checks expected count, dimensions, hashes, alpha occupancy, edge contact, disconnected fragments, matte residue, and provenance. A code failure blocks Codex review.

Then inspect split overlays, raw 64x64 small assets, transparent assets, and checker, white, purple, and black boards. Compare every small asset with its small payload reference, not with the large asset. Record identity, view, simplification, style, shadow, residue, clipping, and edge-integrity findings.

Record the Codex decision:

```bash
python3 scripts/record_review.py \
  --status /absolute/path/families/furniture/family-status.json \
  --reviewer codex \
  --decision approve \
  --comment "All required checks passed."
```

Only after Codex approval, present the family to the human reviewer. Human decisions cannot be recorded by `record_review.py`; they are exclusive to the local review server. A family is approved only when all three gates pass.

For a local visual review queue, run:

```bash
python3 scripts/review_server.py \
  --pack-root /absolute/path/asset-pack \
  --port 4177
```

Open the printed URL. The page displays every validation board, accepts approve or reject plus an optional comment, writes a local JSONL audit log, updates `family-status.json`, and promotes assets only after all gates pass.

Human review POSTs are same-origin only. Every approval regenerates `approved-manifest.json`; the manifest rejects missing or unexpected PNGs in an approved directory.

### 7. Repair Without Regression

- Repair only rejected variants or items. Preserve approved large assets when small assets fail.
- Build repair templates from the authoritative payload references, especially for small variants.
- Keep repaired assets in a new round. Promote individual files into `approved/` only after all gates pass.
- Re-run family boards after any promotion so mixed-version families are reviewed together.
- Re-run cross-family boards at each production wave to detect style drift from the canonical anchor.

### 8. Package For PlayDrop

Before publishing:

1. Verify every approved file and provenance entry.
2. Remove private templates and restricted references from the distributable pack.
3. Add only approved transparent PNGs and public metadata to the pack catalogue.
4. Run local `playdrop project validate`.
5. Keep publication blocked until rights and human approvals are complete.

Run the hard publication gates before catalogue work:

```bash
python3 scripts/validate_spec.py --spec /absolute/path/asset-pack/pack-spec.json --for-publication
python3 scripts/verify_pack.py \
  --spec /absolute/path/asset-pack/pack-spec.json \
  --pack-root /absolute/path/asset-pack \
  --family furniture \
  --for-publication
```

Generate the current approved manifest after any manual status migration:

```bash
python3 scripts/build_approved_manifest.py \
  --spec /absolute/path/asset-pack/pack-spec.json \
  --pack-root /absolute/path/asset-pack
```

## Regression Check

Use `verify_approved_manifest.py` to prove an existing approved set has not changed:

```bash
python3 scripts/verify_approved_manifest.py \
  --manifest /absolute/path/pilot-approved-manifest.json \
  --root /absolute/path/pilot-root \
  --large-size 256x256 \
  --small-size 64x64 \
  --approved-glob 'families/*/04-approved/*.png' \
  --expected-count 44
```

For current packs, pass `--spec` instead of explicit sizes. The verifier checks hashes, PNG format, RGBA transparency, spec-driven dimensions, and unexpected approved files without copying private fixtures into the plugin.

## Development Regression

The exported synthetic end-to-end suite exercises extraction, all three review gates, promotion, repair merge, failed-repair preservation, manifests, retry limits, rights, and audit controls:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```
