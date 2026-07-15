#!/usr/bin/env python3
"""Process one approved source job with per-asset extraction routing."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from asset_pack_common import (
    append_jsonl,
    color_hex,
    find_family,
    grid_for_slots,
    load_spec,
    now,
    parse_hex_color,
    parse_item_ids,
    read_json,
    retry_limits,
    sha256,
    slots_for_family,
    write_json,
)
from process_sheet import (
    adaptive_grid,
    crop_box,
    finish_chroma_edge,
    hard_key,
    image_metrics,
    make_board,
    make_raw_small_board,
    matte_profile,
    remove_tiny_components,
    rembg_extract,
    soft_chroma,
    supports_despill,
    split_overlay,
    trim_and_fit,
)


METHODS = ("soft-chroma", "hard-key", "rembg")
SYSTEMIC_REPAIR_RATIO = 0.5


def code_failures(metrics: dict[str, Any], size: tuple[int, int]) -> list[str]:
    minimum_visible = 500 if max(size) >= 256 else 35
    failures: list[str] = []
    if metrics["visiblePixels"] <= minimum_visible:
        failures.append("empty_or_too_small")
    if metrics["outputEdgeTouchPixels"] != 0:
        failures.append("output_edge_contact")
    if metrics["tinyComponentCount"] != 0:
        failures.append("tiny_disconnected_component")
    if metrics["residualMatteRatioWithin48"] > 0.002:
        failures.append("matte_residue_or_subject_overlap")
    if metrics["residualMatteHueRatio"] > 0.002:
        failures.append("matte_hue_fringe_or_subject_overlap")
    return failures


def source_crop_edge_pixels(image: Image.Image, key: tuple[int, int, int], threshold: float = 96.0) -> int:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    distance = np.linalg.norm(rgb - np.asarray(key, dtype=np.float32), axis=2)
    subject = distance > threshold
    edge = np.concatenate((subject[0], subject[-1], subject[:, 0], subject[:, -1]))
    return int(edge.sum())


def erode_mask(mask: np.ndarray, radius: int) -> np.ndarray:
    eroded = mask.copy()
    height, width = mask.shape
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            shifted = np.zeros_like(mask)
            source_y = slice(max(0, dy), min(height, height + dy))
            target_y = slice(max(0, -dy), min(height, height - dy))
            source_x = slice(max(0, dx), min(width, width + dx))
            target_x = slice(max(0, -dx), min(width, width - dx))
            shifted[target_y, target_x] = mask[source_y, source_x]
            eroded &= shifted
    return eroded


def source_matte_subject_overlap(
    image: Image.Image,
    key: tuple[int, int, int],
    opaque_threshold: float,
) -> dict[str, Any]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    key_rgb = np.asarray(key, dtype=np.float32)
    key_chroma = key_rgb - key_rgb.min()
    key_chroma_norm = float(np.linalg.norm(key_chroma))
    if key_chroma_norm <= 1.0:
        return {"interiorPixels": 0, "subjectPixels": 0, "ratio": 0.0, "detectable": False}
    distance = np.linalg.norm(rgb - key_rgb, axis=2)
    subject = distance > opaque_threshold
    pixel_chroma = rgb - rgb.min(axis=2, keepdims=True)
    pixel_chroma_norm = np.linalg.norm(pixel_chroma, axis=2)
    similarity = np.divide(
        np.sum(pixel_chroma * key_chroma, axis=2),
        pixel_chroma_norm * key_chroma_norm,
        out=np.zeros_like(pixel_chroma_norm),
        where=pixel_chroma_norm > 1.0,
    )
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    same_hue_subject = subject & (saturation >= 24.0) & (similarity >= 0.80)
    interior = erode_mask(same_hue_subject, 2)
    subject_pixels = int(subject.sum())
    interior_pixels = int(interior.sum())
    return {
        "interiorPixels": interior_pixels,
        "subjectPixels": subject_pixels,
        "ratio": round(interior_pixels / max(1, subject_pixels), 7),
        "detectable": True,
    }


def run_builder(script: Path, arguments: list[str]) -> None:
    result = subprocess.run([sys.executable, str(script), *arguments], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"builder_failed:{script.name}:{result.stderr.strip() or result.stdout.strip()}")


def record_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError as error:
        raise SystemExit(f"provenance_path_outside_pack_root:{path.resolve()}") from error


def write_review_boards(assets: list[dict[str, Any]], pack_root: Path, validation_root: Path) -> None:
    entries = []
    for asset in assets:
        path = pack_root / asset["output"]
        entries.append({"path": str(path), "label": f"{asset['item']} {asset['kind']}", "kind": asset["kind"]})
    for background in ("checker", "white", "purple", "black"):
        make_board(entries, validation_root / f"review-{background}.png", background)
    if any(entry["kind"] == "small" for entry in entries):
        make_raw_small_board(entries, validation_root / "small-raw-64.png")


def next_repair_number(family_root: Path, item_id: str, kind: str) -> int:
    prefix = f"repair-{item_id}-{kind}-v"
    numbers = []
    for path in (family_root / "jobs").glob(f"{prefix}*.json"):
        try:
            numbers.append(int(path.stem.removeprefix(prefix)))
        except ValueError:
            continue
    return max(numbers, default=0) + 1


def create_repair_job(
    pack_root: Path,
    spec_path: Path,
    spec: dict[str, Any],
    family: dict[str, Any],
    family_root: Path,
    source_job: dict[str, Any],
    item_id: str,
    kind: str,
    reasons: list[str],
) -> dict[str, Any] | None:
    for path in sorted((family_root / "jobs").glob(f"repair-{item_id}-{kind}-v*.json")):
        existing = read_json(path)
        if existing.get("state") in {"ready", "running", "source-approved", "awaiting-source-review"}:
            return existing
    version = next_repair_number(family_root, item_id, kind)
    maximum = retry_limits(spec)["individualRepairsPerAssetMaximum"]
    prior_jobs = [
        read_json(path)
        for path in sorted((family_root / "jobs").glob(f"repair-{item_id}-{kind}-v*.json"))
    ]
    generated_sources = sum(
        (pack_root / candidate["output"]).is_file()
        for candidate in prior_jobs
        if candidate.get("output")
    )
    if generated_sources >= maximum:
        return None
    production = family.get("production", {})
    mattes = list(source_job.get("fallbackMattes") or production.get("fallbackMattes") or [])
    if not mattes:
        return None
    matte = mattes[min(generated_sources, len(mattes) - 1)]
    job_id = f"repair-{item_id}-{kind}-v{version}"
    template_dir = family_root / "private-templates" / job_id
    prompt = family_root / "prompts" / f"{job_id}.txt"
    scripts = Path(__file__).resolve().parent
    style = spec.get("styleAnchor", {})
    style_references = [
        value
        for value in [style.get("path"), *style.get("additionalReferences", [])]
        if value
    ]
    style_references.extend(
        reference["path"] if isinstance(reference, dict) else reference
        for reference in family.get("continuityStyleReferences", [])
    )
    source_output = source_job.get("output")
    if source_output and (pack_root / source_output).is_file():
        style_references.append(source_output)
    style_references = list(dict.fromkeys(style_references))
    run_builder(
        scripts / "build_template.py",
        [
            "--spec", str(spec_path),
            "--family", family["id"],
            "--mode", kind,
            "--items", item_id,
            "--columns", "1",
            "--output-dir", str(template_dir),
        ],
    )
    template = template_dir / f"{family['id']}-{kind}-identity-template.png"
    run_builder(
        scripts / "build_prompt.py",
        [
            "--spec", str(spec_path),
            "--family", family["id"],
            "--mode", kind,
            "--items", item_id,
            "--columns", "1",
            "--matte", matte,
            "--style-reference-count", str(len(style_references)),
            "--output", str(prompt),
        ],
    )
    created_at = now()
    job = {
        "schemaVersion": 1,
        "jobId": job_id,
        "type": "generation",
        "familyId": family["id"],
        "mode": kind,
        "items": [item_id],
        "attempt": version,
        "columns": 1,
        "matte": matte,
        "fallbackMattes": mattes[generated_sources + 1:],
        "state": "ready" if style_references else "blocked-style-anchor",
        "bootstrapStyle": False,
        "prompt": record_path(prompt, pack_root),
        "identityTemplate": record_path(template, pack_root),
        "styleReferences": style_references,
        "output": record_path(family_root / "generated" / f"{job_id}.png", pack_root),
        "repairFor": {"itemId": item_id, "kind": kind, "reasons": reasons},
        "timing": {"queuedAt": created_at},
        "errors": [],
    }
    write_json(family_root / "jobs" / f"{job_id}.json", job)
    append_jsonl(
        family_root / "events.jsonl",
        {
            "at": created_at,
            "event": "repair-job-prepared",
            "jobId": job_id,
            "itemId": item_id,
            "kind": kind,
            "reasons": reasons,
            "styleReferences": style_references,
        },
    )
    return job


def supersede_pending_repairs(
    family_root: Path,
    current_job_id: str,
    superseded_at: str,
) -> list[str]:
    """Retire unstarted repairs once a complete family round makes them obsolete."""
    superseded: list[str] = []
    for path in sorted((family_root / "jobs").glob("repair-*.json")):
        candidate = read_json(path)
        job_id = candidate.get("jobId", path.stem)
        if job_id == current_job_id or candidate.get("state") not in {"ready", "blocked-style-anchor"}:
            continue
        candidate["state"] = "superseded"
        candidate["supersededBy"] = current_job_id
        candidate["supersededAt"] = superseded_at
        write_json(path, candidate)
        superseded.append(job_id)
    return superseded


def merge_assets(
    previous: list[dict[str, Any]],
    replacements: list[dict[str, Any]],
    family: dict[str, Any],
) -> list[dict[str, Any]]:
    merged = {(asset["itemId"], asset["kind"]): asset for asset in previous}
    for asset in replacements:
        merged[(asset["itemId"], asset["kind"])] = asset
    order = {
        (slot["itemId"], slot["kind"]): index
        for index, slot in enumerate(slots_for_family(family, "paired"))
    }
    return sorted(merged.values(), key=lambda asset: order.get((asset["itemId"], asset["kind"]), 100000))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--job", default="generation-v1")
    parser.add_argument(
        "--methods",
        default="soft-chroma,hard-key,rembg",
        help="Comma-separated per-asset priority. rembg is attempted only after chroma methods fail.",
    )
    parser.add_argument(
        "--allow-source-hue-overlap-items",
        help="Comma-separated visually inspected item ids allowed to retain legitimate matte-like subject hues.",
    )
    parser.add_argument(
        "--allow-matte-warning-items",
        help="Comma-separated visually inspected item ids allowed to bypass output matte residue/hue warnings.",
    )
    parser.add_argument(
        "--allow-source-crop-edge-items",
        help="Comma-separated visually inspected item ids allowed to bypass source crop-edge contact warnings.",
    )
    parser.add_argument(
        "--force-hue-cleanup-items",
        help="Comma-separated visually inspected item ids allowed to force chroma hue cleanup despite source hue overlap.",
    )
    parser.add_argument(
        "--skip-hue-cleanup-items",
        help="Comma-separated visually inspected item ids that must skip the final chroma edge hue cleanup.",
    )
    args = parser.parse_args()

    methods = [value.strip() for value in args.methods.split(",") if value.strip()]
    if not methods or any(method not in METHODS for method in methods) or len(methods) != len(set(methods)):
        raise SystemExit(f"invalid_method_priority:{args.methods}")
    pack_root = args.pack_root.resolve()
    spec_path = pack_root / "pack-spec.json"
    spec = load_spec(spec_path)
    family = find_family(spec, args.family)
    family_item_ids = {item["id"] for item in family["items"]}
    source_hue_override_items = set(parse_item_ids(args.allow_source_hue_overlap_items) or [])
    matte_warning_override_items = set(parse_item_ids(args.allow_matte_warning_items) or [])
    crop_edge_override_items = set(parse_item_ids(args.allow_source_crop_edge_items) or [])
    forced_hue_cleanup_items = set(parse_item_ids(args.force_hue_cleanup_items) or [])
    skipped_hue_cleanup_items = set(parse_item_ids(args.skip_hue_cleanup_items) or [])
    unknown_override_items = (
        source_hue_override_items
        | matte_warning_override_items
        | crop_edge_override_items
        | forced_hue_cleanup_items
        | skipped_hue_cleanup_items
    ) - family_item_ids
    if unknown_override_items:
        raise SystemExit(f"unknown_override_items:{','.join(sorted(unknown_override_items))}")
    visual_override_items = {
        "sourceHueOverlap": sorted(source_hue_override_items),
        "outputMatteWarnings": sorted(matte_warning_override_items),
        "sourceCropEdge": sorted(crop_edge_override_items),
        "forcedHueCleanup": sorted(forced_hue_cleanup_items),
        "skippedHueCleanup": sorted(skipped_hue_cleanup_items),
    }
    family_root = pack_root / "families" / family["id"]
    job_path = family_root / "jobs" / f"{args.job}.json"
    job = read_json(job_path)
    if job.get("state") == "processed":
        print(f"already_processed:{family['id']}:{args.job}")
        return
    if job.get("state") != "source-approved":
        raise SystemExit(f"source_job_not_approved:{family['id']}:{args.job}:{job.get('state')}")
    lock_path = family_root / ".process.lock"
    try:
        lock_descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise SystemExit(f"family_process_locked:{family['id']}") from error
    os.close(lock_descriptor)
    started_at = now()
    try:
        status_path = family_root / "family-status.json"
        previous = read_json(status_path)
        previous_assets = list(previous.get("assets", []))
        was_approved = previous.get("status") == "approved"
        previous_approved = previous.get("approvedAssets") or previous.get("lastApprovedAssets")
        previous["status"] = "extracting"
        previous.setdefault("pipeline", {})["stage"] = "extraction"
        previous["pipeline"].setdefault("timing", {})["extractionStartedAt"] = started_at
        previous["updatedAt"] = started_at
        write_json(status_path, previous)
        append_jsonl(family_root / "events.jsonl", {"at": started_at, "event": "extraction-started", "jobId": args.job})

        source = pack_root / job["output"]
        prompt = pack_root / job["prompt"]
        identity_template = pack_root / job["identityTemplate"]
        for label, path in (("source", source), ("prompt", prompt), ("identity_template", identity_template)):
            if not path.is_file():
                raise SystemExit(f"job_input_not_found:{label}:{path}")
        item_ids = list(job.get("items") or []) or None
        slots = slots_for_family(family, job["mode"], item_ids)
        rows, columns = grid_for_slots(len(slots), int(job["columns"]))
        key = parse_hex_color(job["matte"])
        despill_enabled = supports_despill(key)
        source_image = Image.open(source).convert("RGB")
        profile = matte_profile(source_image, rows, columns, key)
        if profile["medianDistanceFromRequested"] > 96:
            raise SystemExit(f"matte_median_too_far_from_requested:{profile['medianDistanceFromRequested']}")
        round_name = f"{args.job}-routed"
        round_root = family_root / "extraction-rounds" / round_name
        validation_root = family_root / "validation" / round_name
        if round_root.exists() or validation_root.exists():
            raise SystemExit(f"round_already_exists:{round_name}")
        crop_root = round_root / "crops"
        attempts_root = round_root / "attempts"
        selected_root = round_root / "extracted"
        crop_root.mkdir(parents=True)
        attempts_root.mkdir(parents=True)
        selected_root.mkdir(parents=True)
        validation_root.mkdir(parents=True)
        layout = adaptive_grid(source_image, rows, columns, profile)
        split_overlay(source_image, rows, columns, layout, validation_root / "split-overlay.png")
        transparent = max(12.0, min(80.0, math.ceil(profile["distanceFromRequestedP99"] + 3.0)))
        opaque = max(115.0, transparent + 64.0)
        hard_tolerance = max(64.0, min(112.0, transparent + 48.0))
        style_path_value = spec.get("styleAnchor", {}).get("path")
        style_path = pack_root / style_path_value if style_path_value else None
        attempts: list[dict[str, Any]] = []
        replacements: list[dict[str, Any]] = []
        unresolved: list[dict[str, Any]] = []

        for slot, box in zip(slots, layout["boxes"]):
            filename = f"{slot['itemId']}-{slot['kind']}.png"
            crop = crop_box(source_image, box)
            crop_path = crop_root / filename
            crop.save(crop_path)
            crop_edge_pixels = source_crop_edge_pixels(crop, key)
            matte_overlap = source_matte_subject_overlap(crop, key, opaque)
            variant = spec["variants"][slot["kind"]]
            chosen: dict[str, Any] | None = None
            soft_visible: int | None = None
            slot_attempts: list[dict[str, Any]] = []
            for method in methods:
                attempt_path = attempts_root / method / filename
                attempt_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    if method == "soft-chroma":
                        extracted = soft_chroma(crop, key, transparent, opaque, despill_enabled, True)
                    elif method == "hard-key":
                        extracted = hard_key(crop, key, hard_tolerance)
                    else:
                        extracted = rembg_extract(crop)
                except SystemExit as error:
                    if str(error) == "rembg_not_installed":
                        slot_attempts.append({"method": method, "skipped": "rembg_not_installed"})
                        continue
                    raise
                fitted = trim_and_fit(
                    extracted,
                    int(variant["width"]),
                    int(variant["height"]),
                    int(variant["padding"]),
                )
                final_hue_cleanup = method == "soft-chroma" and slot["itemId"] not in skipped_hue_cleanup_items and (
                    matte_overlap["ratio"] <= 0.005 or slot["itemId"] in forced_hue_cleanup_items
                )
                if final_hue_cleanup:
                    fitted = finish_chroma_edge(fitted, key)
                fitted = remove_tiny_components(fitted)
                fitted.save(attempt_path)
                measured = image_metrics(fitted, key)
                measured["sourceCropEdgePixels"] = crop_edge_pixels
                measured["sourceMatteSubjectOverlap"] = matte_overlap
                failures = code_failures(measured, fitted.size)
                if slot["itemId"] in matte_warning_override_items:
                    failures = [
                        failure for failure in failures
                        if failure not in {
                            "matte_residue_or_subject_overlap",
                            "matte_hue_fringe_or_subject_overlap",
                        }
                    ]
                if crop_edge_pixels > 2 and slot["itemId"] not in crop_edge_override_items:
                    failures.append("source_crop_edge_contact")
                if (
                    matte_overlap["ratio"] > 0.005
                    and slot["itemId"] not in source_hue_override_items
                ):
                    failures.append("source_matte_hue_inside_subject")
                if method == "soft-chroma":
                    soft_visible = int(measured["visiblePixels"])
                elif method == "hard-key" and soft_visible:
                    retained = measured["visiblePixels"] / max(1, soft_visible)
                    measured["visibleRatioVsSoftChroma"] = round(retained, 6)
                    if retained < 0.96:
                        failures.append("possible_subject_loss_vs_soft_chroma")
                elif method == "rembg" and soft_visible:
                    retained = measured["visiblePixels"] / max(1, soft_visible)
                    measured["visibleRatioVsSoftChroma"] = round(retained, 6)
                    if retained < 0.82 or retained > 1.18:
                        failures.append("possible_silhouette_drift_vs_soft_chroma")
                record = {
                    "item": slot["item"],
                    "itemId": slot["itemId"],
                    "kind": slot["kind"],
                    "method": method,
                    "file": record_path(attempt_path, pack_root),
                    "finalHueCleanupApplied": final_hue_cleanup,
                    **measured,
                    "codeFailures": failures,
                    "codePass": not failures,
                }
                attempts.append(record)
                slot_attempts.append(record)
                if not failures:
                    chosen = record
                    break
            if chosen:
                selected_path = selected_root / filename
                shutil.copy2(pack_root / chosen["file"], selected_path)
                asset = {
                    "item": slot["item"],
                    "itemId": slot["itemId"],
                    "kind": slot["kind"],
                    "payload": slot["payload"],
                    "source": record_path(source, pack_root),
                    "sourceSha256": sha256(source),
                    "prompt": record_path(prompt, pack_root),
                    "promptSha256": sha256(prompt),
                    "styleAnchor": record_path(style_path, pack_root) if style_path else None,
                    "styleAnchorSha256": sha256(style_path) if style_path else None,
                    "identityTemplate": record_path(identity_template, pack_root),
                    "identityTemplateSha256": sha256(identity_template),
                    "adaptiveBox": box,
                    "crop": record_path(crop_path, pack_root),
                    "cropSha256": sha256(crop_path),
                    "extractor": chosen["method"],
                    "requestedKeyRgb": list(key),
                    "transparentThreshold": transparent if chosen["method"] == "soft-chroma" else None,
                    "opaqueThreshold": opaque if chosen["method"] == "soft-chroma" else None,
                    "hardTolerance": hard_tolerance if chosen["method"] == "hard-key" else None,
                    "despill": chosen["method"] == "soft-chroma" and despill_enabled,
                    "hueCleanup": chosen["method"] == "soft-chroma",
                    "forcedHueCleanup": slot["itemId"] in forced_hue_cleanup_items,
                    "skippedHueCleanup": slot["itemId"] in skipped_hue_cleanup_items,
                    "finalHueCleanupApplied": bool(chosen.get("finalHueCleanupApplied")),
                    "tinyComponentCleanupThreshold": 10,
                    "output": record_path(selected_path, pack_root),
                    "outputSha256": sha256(selected_path),
                }
                replacements.append(asset)
            else:
                failures = sorted({failure for attempt in slot_attempts for failure in attempt.get("codeFailures", [])})
                if not failures:
                    failures = [attempt.get("skipped", "no_compatible_extractor") for attempt in slot_attempts]
                unresolved.append({"item": slot["item"], "itemId": slot["itemId"], "kind": slot["kind"], "failures": failures})

        if item_ids and unresolved and was_approved:
            replacements = []
        selected_assets = merge_assets(previous_assets, replacements, family)
        expected = int(previous.get("expectedAssetCount") or len(family["items"]) * 2)
        complete = len(selected_assets) == expected and not unresolved
        repair_jobs = []
        systemic_repair = bool(
            unresolved
            and len(unresolved) >= max(2, math.ceil(len(slots) * SYSTEMIC_REPAIR_RATIO))
        )
        if not systemic_repair:
            unresolved_by_item: dict[str, list[dict[str, Any]]] = {}
            for asset in unresolved:
                unresolved_by_item.setdefault(asset["itemId"], []).append(asset)
            repair_requests: list[tuple[str, str, list[str]]] = []
            for item_id, item_failures in unresolved_by_item.items():
                kinds = {asset["kind"] for asset in item_failures}
                reasons = sorted({reason for asset in item_failures for reason in asset["failures"]})
                if kinds == {"large", "small"}:
                    repair_requests.append((item_id, "paired", reasons))
                else:
                    repair_requests.extend(
                        (item_id, asset["kind"], asset["failures"])
                        for asset in item_failures
                    )
            for item_id, kind, reasons in repair_requests:
                repair = create_repair_job(
                    pack_root,
                    spec_path,
                    spec,
                    family,
                    family_root,
                    job,
                    item_id,
                    kind,
                    reasons,
                )
                if repair:
                    repair_jobs.append(repair["jobId"])

        write_json(round_root / "source-preflight.json", profile)
        write_json(
            round_root / "metrics.json",
            {
                "codePass": complete,
                "selectedAssetCount": len(replacements),
                "unresolved": unresolved,
                "repairStrategy": "full-sheet" if systemic_repair else "targeted",
                "visualReviewOverrideItems": visual_override_items,
                "attempts": attempts,
            },
        )
        write_json(
            round_root / "provenance.json",
            {
                "schemaVersion": 1,
                "createdAt": now(),
                "family": family["name"],
                "familyId": family["id"],
                "mode": job["mode"],
                "round": round_name,
                "jobId": args.job,
                "methodPriority": methods,
                "source": record_path(source, pack_root),
                "sourceSha256": sha256(source),
                "prompt": record_path(prompt, pack_root),
                "promptSha256": sha256(prompt),
                "identityTemplate": record_path(identity_template, pack_root),
                "identityTemplateSha256": sha256(identity_template),
                "matteProfile": profile,
                "splitting": layout,
                "assets": replacements,
                "unresolved": unresolved,
                "repairStrategy": "full-sheet" if systemic_repair else "targeted",
                "visualReviewOverrideItems": visual_override_items,
            },
        )
        if selected_assets:
            write_review_boards(selected_assets, pack_root, validation_root)
        finished_at = now()
        superseded_jobs = supersede_pending_repairs(family_root, args.job, finished_at) if complete else []
        history = list(previous.get("roundHistory", []))
        history.append(
            {
                "round": round_name,
                "jobId": args.job,
                "mode": job["mode"],
                "repairItems": item_ids or [],
                "sourceSha256": sha256(source),
                "method": "per-asset-routing",
                "methodPriority": methods,
                "visualReviewOverrideItems": visual_override_items,
                "code": "approved" if complete else "incomplete",
                "createdAt": finished_at,
            }
        )
        if complete:
            status_value = "awaiting-codex-review"
            validation = {"code": "approved", "codex": "pending", "human": "pending", "codeFailures": []}
            selected_round = round_name
            pipeline_stage = "codex-review"
        elif was_approved:
            status_value = "approved"
            validation = previous["validation"]
            selected_assets = previous_assets
            selected_round = previous.get("selectedRound")
            pipeline_stage = "full-sheet-retry" if systemic_repair else ("repair-generation" if repair_jobs else "blocked-repair")
        else:
            status_value = "needs-retry" if systemic_repair else ("needs-repair" if repair_jobs else "blocked-repair")
            validation = {
                "code": "incomplete",
                "codex": "pending",
                "human": "pending",
                "codeFailures": [
                    f"{asset['itemId']}-{asset['kind']}:{failure}"
                    for asset in unresolved
                    for failure in asset["failures"]
                ],
            }
            selected_round = round_name
            pipeline_stage = "full-sheet-retry" if systemic_repair else ("repair-generation" if repair_jobs else "blocked-repair")
        status = {
            **previous,
            "status": status_value,
            "selectedRound": selected_round,
            "source": {
                "path": record_path(source, pack_root),
                "sha256": sha256(source),
                "jobId": args.job,
                "mode": job["mode"],
                "repairItems": item_ids or [],
                "matte": color_hex(key),
                "preflight": profile,
                "prompt": record_path(prompt, pack_root),
                "promptSha256": sha256(prompt),
                "identityTemplate": record_path(identity_template, pack_root),
                "identityTemplateSha256": sha256(identity_template),
            },
            "extraction": {
                "method": "per-asset-routing",
                "priority": methods,
                "visualReviewOverrideItems": visual_override_items,
            },
            "lastAttempt": {
                "round": round_name,
                "jobId": args.job,
                "code": "approved" if complete else "incomplete",
                "unresolved": unresolved,
                "repairJobs": repair_jobs,
                "repairStrategy": "full-sheet" if systemic_repair else "targeted",
                "supersededJobs": superseded_jobs,
                "visualReviewOverrideItems": visual_override_items,
            },
            "validation": validation,
            "selectedAssetCount": len(selected_assets),
            "assets": selected_assets,
            "roundHistory": history,
            "pipeline": {
                **dict(previous.get("pipeline") or {}),
                "stage": pipeline_stage,
                "activeJob": None if complete else (repair_jobs[0] if repair_jobs else None),
                "timing": {
                    **dict((previous.get("pipeline") or {}).get("timing") or {}),
                    "extractionStartedAt": started_at,
                    "extractionFinishedAt": finished_at,
                },
                "lastError": None if complete else f"{len(unresolved)} unresolved assets",
            },
            "updatedAt": finished_at,
        }
        if previous_approved:
            status["lastApprovedAssets"] = previous_approved
        write_json(status_path, status)
        job["state"] = "processed" if complete else "needs-repair"
        job.setdefault("timing", {})["processedAt"] = finished_at
        job["result"] = {
            "round": round_name,
            "selectedAssets": len(replacements),
            "unresolvedAssets": len(unresolved),
            "repairJobs": repair_jobs,
            "repairStrategy": "full-sheet" if systemic_repair else "targeted",
            "supersededJobs": superseded_jobs,
            "visualReviewOverrideItems": visual_override_items,
        }
        write_json(job_path, job)
        append_jsonl(
            family_root / "events.jsonl",
            {
                "at": finished_at,
                "event": "extraction-finished",
                "jobId": args.job,
                "selectedAssets": len(replacements),
                "unresolvedAssets": len(unresolved),
                "repairJobs": repair_jobs,
                "supersededJobs": superseded_jobs,
                "visualReviewOverrideItems": visual_override_items,
            },
        )
        print(f"family:{family['id']}")
        print(f"job:{args.job}")
        print(f"selected:{len(replacements)}")
        print(f"unresolved:{len(unresolved)}")
        print(f"family_status:{status_value}")
        for repair_job in repair_jobs:
            print(f"repair_job:{repair_job}")
        if superseded_jobs:
            print(f"superseded_jobs:{len(superseded_jobs)}")
        if systemic_repair:
            print("repair_strategy:full-sheet")
            print(
                "next_command:prepare_retry.py --pack-root "
                f"{pack_root} --family {family['id']} --reason 'Systemic extraction failure in {len(unresolved)}/{len(slots)} slots.'"
            )
        if unresolved:
            raise SystemExit("family_requires_repair")
    finally:
        lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
