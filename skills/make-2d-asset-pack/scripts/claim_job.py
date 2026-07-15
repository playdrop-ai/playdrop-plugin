#!/usr/bin/env python3
"""Atomically claim one ready family generation job."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from asset_pack_common import append_jsonl, now, read_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--job", default="generation-v1")
    parser.add_argument("--worker", default="codex-parent")
    args = parser.parse_args()

    pack_root = args.pack_root.resolve()
    family_root = pack_root / "families" / args.family
    job_path = family_root / "jobs" / f"{args.job}.json"
    lock_path = job_path.with_suffix(".lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise SystemExit(f"job_claim_locked:{args.family}:{args.job}") from error
    try:
        os.close(descriptor)
        job = read_json(job_path)
        if job.get("state") != "ready":
            raise SystemExit(f"job_not_ready:{args.family}:{args.job}:{job.get('state')}")
        claimed_at = now()
        job["state"] = "running"
        job["worker"] = args.worker
        job.setdefault("timing", {})["startedAt"] = claimed_at
        write_json(job_path, job)
        status_path = family_root / "family-status.json"
        status = read_json(status_path)
        status["status"] = "generating"
        status.setdefault("pipeline", {})["stage"] = "generation"
        status["pipeline"]["activeJob"] = str(job_path.relative_to(pack_root))
        status["pipeline"].setdefault("timing", {})["generationStartedAt"] = claimed_at
        status["updatedAt"] = claimed_at
        write_json(status_path, status)
        append_jsonl(
            family_root / "events.jsonl",
            {"at": claimed_at, "event": "job-claimed", "jobId": args.job, "worker": args.worker},
        )
    finally:
        lock_path.unlink(missing_ok=True)
    print(f"claimed:{args.family}:{args.job}:{args.worker}")
    print(f"prompt:{pack_root / job['prompt']}")
    print(f"identity_template:{pack_root / job['identityTemplate']}")
    for reference in job.get("styleReferences", []):
        print(f"style_reference:{pack_root / reference}")
    print(f"output:{pack_root / job['output']}")


if __name__ == "__main__":
    main()
