#!/usr/bin/env python3
"""Record a generation result, retain its source, and update family jobs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from asset_pack_common import append_jsonl, now, read_json, sha256, write_json


def elapsed_between(start: str | None, end: str) -> float | None:
    if not start:
        return None
    try:
        return round((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds(), 3)
    except ValueError:
        return None


def portable_copy(source: Path, destination: Path) -> None:
    if destination.exists():
        if sha256(destination) != sha256(source):
            raise SystemExit(f"generation_output_conflict:{destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def record_ledger(
    pack_root: Path,
    job: dict,
    status: str,
    output: Path | None,
    elapsed_seconds: float | None,
    error: str,
) -> None:
    command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "record_generation.py"),
        "--ledger", str(pack_root / "generation-ledger.csv"),
        "--family", job["familyId"],
        "--attempt", str(job["attempt"]),
        "--status", status,
        "--prompt", str(pack_root / job["prompt"]),
        "--identity-template", str(pack_root / job["identityTemplate"]),
    ]
    references = job.get("styleReferences", [])
    if references:
        command.extend(["--style-anchor", str(pack_root / references[0])])
    if output:
        command.extend(["--output", str(output)])
    if elapsed_seconds is not None:
        command.extend(["--elapsed-seconds", str(elapsed_seconds)])
    if error:
        command.extend(["--error", error])
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"generation_ledger_failed:{result.stderr.strip() or result.stdout.strip()}")


def promote_bootstrap(pack_root: Path, family_id: str, source: Path) -> str:
    destination = pack_root / "style-anchor" / f"generated-bootstrap-{family_id}.png"
    portable_copy(source, destination)
    spec_path = pack_root / "pack-spec.json"
    spec = read_json(spec_path)
    relative = str(destination.relative_to(pack_root))
    spec["styleAnchor"]["path"] = relative
    spec["styleAnchor"]["origin"] = "generated-bootstrap"
    spec["styleAnchor"]["ownership"] = "creator-owned"
    write_json(spec_path, spec)
    for family in spec["families"]:
        other_root = pack_root / "families" / family["id"]
        for job_path in sorted((other_root / "jobs").glob("*.json")):
            job = read_json(job_path)
            if job.get("state") != "blocked-style-anchor":
                continue
            job["styleReferences"] = list(dict.fromkeys([relative, *job.get("styleReferences", [])]))
            job["state"] = "ready"
            job.setdefault("timing", {})["unblockedAt"] = now()
            write_json(job_path, job)
            status_path = other_root / "family-status.json"
            status = read_json(status_path)
            status["status"] = "queued-generation"
            status.setdefault("pipeline", {})["stage"] = "generation"
            status["updatedAt"] = now()
            write_json(status_path, status)
            append_jsonl(
                other_root / "events.jsonl",
                {"at": now(), "event": "style-anchor-unblocked", "jobId": job["jobId"], "styleReference": relative},
            )
    return relative


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--job", default="generation-v1")
    parser.add_argument("--status", choices=("success", "failed"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--elapsed-seconds", type=float)
    parser.add_argument("--error", default="")
    parser.add_argument("--source-review", choices=("approve", "reject"))
    parser.add_argument("--comment", default="")
    args = parser.parse_args()

    pack_root = args.pack_root.resolve()
    family_root = pack_root / "families" / args.family
    job_path = family_root / "jobs" / f"{args.job}.json"
    job = read_json(job_path)
    if job.get("state") not in {"ready", "running"}:
        raise SystemExit(f"job_not_ingestable:{args.family}:{args.job}:{job.get('state')}")
    if args.status == "success" and (not args.output or not args.output.is_file()):
        raise SystemExit(f"generation_output_not_found:{args.output}")
    if args.status == "success" and not args.source_review:
        raise SystemExit("successful_generation_requires_source_review")
    if args.status == "failed" and not args.error.strip():
        raise SystemExit("failed_generation_requires_error")

    recorded_at = now()
    destination: Path | None = None
    if args.output:
        destination = pack_root / job["output"]
        portable_copy(args.output.resolve(), destination)
    record_ledger(pack_root, job, args.status, destination, args.elapsed_seconds, args.error)
    timing = job.setdefault("timing", {})
    timing["finishedAt"] = recorded_at
    wall_seconds = elapsed_between(timing.get("startedAt"), recorded_at)
    if wall_seconds is not None:
        timing["wallSeconds"] = wall_seconds
    if args.elapsed_seconds is not None:
        timing["providerSeconds"] = args.elapsed_seconds
    status_path = family_root / "family-status.json"
    family_status = read_json(status_path)
    family_status.setdefault("pipeline", {}).setdefault("timing", {})
    if args.status == "failed":
        job["state"] = "failed"
        job.setdefault("errors", []).append(args.error.strip())
        family_status["status"] = "generation-failed"
        family_status["pipeline"]["stage"] = "generation-failed"
        family_status["pipeline"]["lastError"] = args.error.strip()
        event = {"at": recorded_at, "event": "generation-failed", "jobId": args.job, "error": args.error.strip()}
    else:
        approved = args.source_review == "approve"
        job["state"] = "source-approved" if approved else "source-rejected"
        job["sourceReview"] = {"decision": args.source_review, "comment": args.comment, "recordedAt": recorded_at}
        family_status["status"] = "awaiting-extraction" if approved else "source-rejected"
        family_status["pipeline"]["stage"] = "extraction" if approved else "source-rejected"
        family_status["pipeline"]["lastError"] = None if approved else (args.comment or "source review rejected")
        family_status["pipeline"]["timing"]["sourceApprovedAt" if approved else "sourceRejectedAt"] = recorded_at
        if approved and job.get("bootstrapStyle"):
            relative = promote_bootstrap(pack_root, args.family, destination)
            job["styleReferences"] = [relative]
        event = {
            "at": recorded_at,
            "event": "source-reviewed",
            "jobId": args.job,
            "decision": args.source_review,
            "comment": args.comment,
            "outputSha256": sha256(destination),
        }
    family_status["pipeline"]["timing"]["generationFinishedAt"] = recorded_at
    family_status["updatedAt"] = recorded_at
    write_json(job_path, job)
    write_json(status_path, family_status)
    append_jsonl(family_root / "events.jsonl", event)
    print(f"ingested:{args.family}:{args.job}:{job['state']}")
    if destination:
        print(f"output:{destination}")
    if wall_seconds is not None:
        print(f"wall_seconds:{wall_seconds}")


if __name__ == "__main__":
    main()
