#!/usr/bin/env python3
"""Create an immutable re-extraction job for an already retained AI source."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_pack_common import append_jsonl, find_family, load_spec, now, read_json, write_json


def next_version(jobs_root: Path) -> int:
    versions = []
    for path in jobs_root.glob("reextract-v*.json"):
        try:
            versions.append(int(path.stem.removeprefix("reextract-v")))
        except ValueError:
            continue
    return max(versions, default=0) + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--from-job", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument(
        "--override-source-review",
        action="store_true",
        help="Allow extraction-only evaluation of a retained source that failed visual source review.",
    )
    args = parser.parse_args()
    if not args.reason.strip():
        raise SystemExit("reextract_reason_required")

    pack_root = args.pack_root.resolve()
    spec = load_spec(pack_root / "pack-spec.json")
    family = find_family(spec, args.family)
    family_root = pack_root / "families" / family["id"]
    source_job = read_json(family_root / "jobs" / f"{args.from_job}.json")
    source = pack_root / source_job["output"]
    if not source.is_file():
        raise SystemExit(f"reextract_source_not_found:{source}")
    source_review_approved = source_job.get("sourceReview", {}).get("decision") == "approve"
    if not source_review_approved and not args.override_source_review:
        raise SystemExit(f"reextract_source_not_approved:{args.from_job}")

    version = next_version(family_root / "jobs")
    job_id = f"reextract-v{version}"
    created_at = now()
    job = {
        **source_job,
        "jobId": job_id,
        "type": "reextraction",
        "attempt": version,
        "state": "source-approved",
        "reextractOf": args.from_job,
        "reextractReason": args.reason.strip(),
        "timing": {"queuedAt": created_at, "finishedAt": created_at, "wallSeconds": 0.0},
        "errors": [],
    }
    if not source_review_approved:
        job["sourceReviewOverride"] = {
            "reason": args.reason.strip(),
            "recordedAt": created_at,
            "scope": "extraction-only",
            "originalDecision": source_job.get("sourceReview", {}).get("decision"),
        }
    job.pop("result", None)
    job.pop("worker", None)
    write_json(family_root / "jobs" / f"{job_id}.json", job)

    superseded_jobs = []
    for prior_job_id in source_job.get("result", {}).get("repairJobs", []):
        prior_path = family_root / "jobs" / f"{prior_job_id}.json"
        if not prior_path.is_file():
            continue
        prior = read_json(prior_path)
        if prior.get("state") not in {"ready", "blocked-style-anchor"}:
            continue
        prior["state"] = "superseded"
        prior["supersededBy"] = job_id
        prior["supersededAt"] = created_at
        write_json(prior_path, prior)
        superseded_jobs.append(prior_job_id)

    status_path = family_root / "family-status.json"
    status = read_json(status_path)
    if status.get("status") != "approved":
        status["status"] = "queued-extraction"
    status.setdefault("pipeline", {})["stage"] = "extraction"
    status["pipeline"]["activeJob"] = str((family_root / "jobs" / f"{job_id}.json").relative_to(pack_root))
    status["updatedAt"] = created_at
    write_json(status_path, status)
    append_jsonl(
        family_root / "events.jsonl",
        {
            "at": created_at,
            "event": "reextract-job-prepared",
            "jobId": job_id,
            "fromJob": args.from_job,
            "source": source_job["output"],
            "reason": args.reason.strip(),
            "sourceReviewOverride": not source_review_approved,
            "supersededJobs": superseded_jobs,
        },
    )
    print(f"reextract_job:{job_id}")
    print(f"source_job:{args.from_job}")
    print(f"state:{job['state']}")
    print(f"superseded_jobs:{len(superseded_jobs)}")


if __name__ == "__main__":
    main()
