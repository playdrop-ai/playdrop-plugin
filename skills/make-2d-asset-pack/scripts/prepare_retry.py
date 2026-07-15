#!/usr/bin/env python3
"""Prepare a bounded full-sheet or targeted generation retry job."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

from asset_pack_common import (
    append_jsonl,
    find_family,
    load_spec,
    now,
    normalize_payload_overrides,
    parse_hex_color,
    parse_item_ids,
    read_json,
    retry_limits,
    slots_for_family,
    write_json,
)


ACTIVE_STATES = {"ready", "running", "source-approved"}


def run_builder(script: Path, arguments: list[str]) -> None:
    result = subprocess.run([sys.executable, str(script), *arguments], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"builder_failed:{script.name}:{result.stderr.strip() or result.stdout.strip()}")


def version_for(family_root: Path, prefix: str) -> int:
    versions: list[int] = []
    for path in (family_root / "jobs").glob(f"{prefix}*.json"):
        try:
            versions.append(int(path.stem.removeprefix(prefix)))
        except ValueError:
            continue
    return max(versions, default=0) + 1


def generated(job: dict[str, Any], pack_root: Path) -> bool:
    output = job.get("output")
    return bool(output and (pack_root / output).is_file())


def mode_includes(mode: str, kind: str) -> bool:
    return mode == "paired" or mode == kind


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--mode", choices=("paired", "large", "small"))
    parser.add_argument("--items", help="Comma-separated item ids; omit for a full-sheet retry")
    parser.add_argument(
        "--payload-overrides",
        type=Path,
        help="JSON payload replacements keyed by item id and large/small variant",
    )
    parser.add_argument("--matte", help="Subject-safe matte; otherwise the next configured matte is used")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--override-limit", action="store_true")
    args = parser.parse_args()

    if not args.reason.strip():
        raise SystemExit("retry_reason_required")
    pack_root = args.pack_root.resolve()
    spec_path = pack_root / "pack-spec.json"
    spec = load_spec(spec_path)
    family = find_family(spec, args.family)
    family_root = pack_root / "families" / family["id"]
    status_path = family_root / "family-status.json"
    status = read_json(status_path)
    item_ids = parse_item_ids(args.items)
    production = family.get("production", {})
    mode = args.mode or production.get("mode", "paired")
    if item_ids and not args.mode:
        raise SystemExit("targeted_retry_requires_mode")
    if args.payload_overrides and not item_ids:
        raise SystemExit("payload_overrides_require_targeted_retry")
    payload_overrides = normalize_payload_overrides(
        read_json(args.payload_overrides.resolve()) if args.payload_overrides else None
    )
    slots_for_family(family, mode, item_ids, payload_overrides)
    jobs = [
        job for job in (
            read_json(path) for path in sorted((family_root / "jobs").glob("*.json"))
        )
        if job.get("type", "generation") == "generation"
    ]

    if item_ids:
        requested_kinds = ("large", "small") if mode == "paired" else (mode,)
        relevant = [
            job for job in jobs
            if set(item_ids).intersection(job.get("items") or [])
            and any(mode_includes(str(job.get("mode")), kind) for kind in requested_kinds)
        ]
        if any(job.get("state") in ACTIVE_STATES for job in relevant):
            raise SystemExit(f"targeted_retry_already_active:{family['id']}:{mode}")
        maximum = retry_limits(spec)["individualRepairsPerAssetMaximum"]
        for item_id in item_ids:
            for kind in requested_kinds:
                count = sum(
                    generated(job, pack_root)
                    for job in jobs
                    if item_id in (job.get("items") or []) and mode_includes(str(job.get("mode")), kind)
                )
                if count >= maximum and not args.override_limit:
                    raise SystemExit(f"item_repair_retry_limit_exceeded:{family['id']}:{item_id}:{kind}:{maximum}")
        prefix = f"repair-{item_ids[0]}-{mode}-v" if len(item_ids) == 1 else f"repair-batch-{mode}-v"
    else:
        relevant = [job for job in jobs if not job.get("items") and job.get("mode") == mode]
        if any(job.get("state") in ACTIVE_STATES for job in relevant):
            raise SystemExit(f"full_sheet_retry_already_active:{family['id']}:{mode}")
        maximum = retry_limits(spec)["fullSheetsPerFamilyMaximum"]
        count = sum(generated(job, pack_root) for job in relevant)
        if count >= maximum and not args.override_limit:
            raise SystemExit(f"full_sheet_retry_limit_exceeded:{family['id']}:{mode}:{maximum}")
        prefix = "generation-v"

    version = version_for(family_root, prefix)
    job_id = f"{prefix}{version}"
    prior_mattes = [str(job.get("matte")) for job in relevant if generated(job, pack_root)]
    latest = relevant[-1] if relevant else None
    candidates = [
        str(value).lower()
        for value in [production.get("matte", "#ff00ff"), *production.get("fallbackMattes", [])]
    ]
    if args.matte:
        matte = args.matte.lower()
    elif latest and latest.get("state") == "failed":
        matte = str(latest.get("matte") or candidates[0]).lower()
    else:
        matte = next((candidate for candidate in candidates if candidate not in prior_mattes), candidates[-1])
    parse_hex_color(matte)
    configured_columns = int(production.get("columns") or 2)
    columns = min(configured_columns, len(item_ids)) if item_ids else configured_columns
    template_dir = family_root / "private-templates" / job_id
    prompt_path = family_root / "prompts" / f"{job_id}.txt"
    scripts = Path(__file__).resolve().parent
    item_args = ["--items", ",".join(item_ids)] if item_ids else []
    payload_override_path = template_dir / "payload-overrides.json" if payload_overrides else None
    payload_override_args: list[str] = []
    if payload_override_path:
        write_json(payload_override_path, payload_overrides)
        payload_override_args = ["--payload-overrides", str(payload_override_path)]
    style = spec.get("styleAnchor", {})
    style_references = [value for value in [style.get("path"), *style.get("additionalReferences", [])] if value]
    style_references.extend(
        reference["path"] if isinstance(reference, dict) else reference
        for reference in family.get("continuityStyleReferences", [])
    )
    repair_continuity_source_job_id = None
    for round_record in reversed(status.get("roundHistory", [])):
        if round_record.get("code") != "approved" or round_record.get("repairItems"):
            continue
        candidate_job_id = round_record.get("jobId")
        candidate_path = family_root / "jobs" / f"{candidate_job_id}.json"
        if not candidate_job_id or not candidate_path.is_file():
            continue
        candidate = read_json(candidate_path)
        candidate_output = candidate.get("output")
        if candidate_output and (pack_root / candidate_output).is_file():
            style_references.append(candidate_output)
            repair_continuity_source_job_id = candidate_job_id
            break
    style_references = list(dict.fromkeys(style_references))
    run_builder(
        scripts / "build_template.py",
        [
            "--spec", str(spec_path), "--family", family["id"], "--mode", mode,
            "--columns", str(columns), *item_args, *payload_override_args,
            "--output-dir", str(template_dir),
        ],
    )
    template = template_dir / f"{family['id']}-{mode}-identity-template.png"
    run_builder(
        scripts / "build_prompt.py",
        [
            "--spec", str(spec_path), "--family", family["id"], "--mode", mode,
            "--columns", str(columns), *item_args, *payload_override_args,
            "--matte", matte,
            "--style-reference-count", str(len(style_references)),
            "--output", str(prompt_path),
        ],
    )
    retry_reason = args.reason.strip()
    prompt_path.write_text(
        prompt_path.read_text(encoding="utf-8").rstrip()
        + "\n\nAUTHORITATIVE RETRY CORRECTION: The previous source was rejected. This correction overrides "
        + "any conflicting earlier payload text or generic constraint for the requested slots: "
        + f"{retry_reason}\n",
        encoding="utf-8",
    )
    created_at = now()
    job = {
        "schemaVersion": 1,
        "jobId": job_id,
        "type": "generation",
        "familyId": family["id"],
        "mode": mode,
        "items": item_ids or [],
        "attempt": version,
        "columns": columns,
        "matte": matte,
        "fallbackMattes": [
            candidate
            for candidate in candidates
            if candidate != matte and candidate not in prior_mattes
        ],
        "state": "ready" if style_references else "blocked-style-anchor",
        "bootstrapStyle": False,
        "prompt": str(prompt_path.relative_to(pack_root)),
        "identityTemplate": str(template.relative_to(pack_root)),
        "styleReferences": style_references,
        "output": str((family_root / "generated" / f"{job_id}.png").relative_to(pack_root)),
        "retry": {
            "reason": retry_reason,
            "limitOverride": bool(args.override_limit),
            "payloadOverrides": (
                str(payload_override_path.relative_to(pack_root)) if payload_override_path else None
            ),
            "repairContinuitySourceJobId": repair_continuity_source_job_id,
        },
        "timing": {"queuedAt": created_at},
        "errors": [],
    }
    write_json(family_root / "jobs" / f"{job_id}.json", job)
    if status.get("status") != "approved":
        status["status"] = "queued-generation" if job["state"] == "ready" else "blocked-style-anchor"
    status.setdefault("pipeline", {})["stage"] = "repair-generation" if item_ids else "generation"
    status["pipeline"]["activeJob"] = str((family_root / "jobs" / f"{job_id}.json").relative_to(pack_root))
    status["updatedAt"] = created_at
    write_json(status_path, status)
    append_jsonl(
        family_root / "events.jsonl",
        {
            "at": created_at,
            "event": "retry-job-prepared",
            "jobId": job_id,
            "mode": mode,
            "items": item_ids or [],
            "matte": matte,
            "reason": args.reason.strip(),
            "limitOverride": bool(args.override_limit),
            "payloadOverrides": payload_overrides,
            "repairContinuitySourceJobId": repair_continuity_source_job_id,
            "styleReferences": style_references,
        },
    )
    print(f"retry_job:{job_id}")
    print(f"state:{job['state']}")
    print(f"matte:{matte}")


if __name__ == "__main__":
    main()
