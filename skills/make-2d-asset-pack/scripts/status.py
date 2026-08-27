#!/usr/bin/env python3
"""Report pack jobs, gates, failures, and measured family timings."""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

from asset_pack_common import read_json


def duration(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        return round((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds(), 3)
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--families", help="Optional comma-separated family ids for a wave-specific report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    pack_root = args.pack_root.resolve()
    pack = read_json(pack_root / "pack-status.json")
    requested_families = {
        value.strip() for value in (args.families or "").split(",") if value.strip()
    }
    families: list[dict[str, Any]] = []
    code_seconds: list[float] = []
    agent_seconds: list[float] = []
    active_code_seconds: list[float] = []
    active_agent_seconds: list[float] = []
    for status_path in sorted((pack_root / "families").glob("*/family-status.json")):
        status = read_json(status_path)
        if requested_families and status.get("familyId") not in requested_families:
            continue
        pipeline = status.get("pipeline", {})
        timing = pipeline.get("timing", {})
        raw_jobs = [read_json(path) for path in sorted((status_path.parent / "jobs").glob("*.json"))]
        started_values = [job.get("timing", {}).get("startedAt") for job in raw_jobs]
        active_started_at = min((value for value in started_values if value), default=None)
        latest_endpoint = (
            timing.get("humanApprovedAt")
            or timing.get("agentReviewedAt")
            or timing.get("extractionFinishedAt")
            or status.get("updatedAt")
        )
        elapsed = duration(timing.get("queuedAt"), latest_endpoint)
        code_elapsed = duration(timing.get("queuedAt"), timing.get("extractionFinishedAt"))
        agent_elapsed = duration(timing.get("queuedAt"), timing.get("agentReviewedAt"))
        human_elapsed = duration(timing.get("queuedAt"), timing.get("humanApprovedAt"))
        queue_latency = duration(timing.get("queuedAt"), active_started_at)
        active_elapsed = duration(active_started_at, latest_endpoint)
        active_code_elapsed = duration(active_started_at, timing.get("extractionFinishedAt"))
        active_agent_elapsed = duration(active_started_at, timing.get("agentReviewedAt"))
        active_human_elapsed = duration(active_started_at, timing.get("humanApprovedAt"))
        validation = status.get("validation", {})
        if validation.get("code") == "approved" and code_elapsed is not None:
            code_seconds.append(code_elapsed)
        if validation.get("agent") == "approved" and agent_elapsed is not None:
            agent_seconds.append(agent_elapsed)
        if validation.get("code") == "approved" and active_code_elapsed is not None:
            active_code_seconds.append(active_code_elapsed)
        if validation.get("agent") == "approved" and active_agent_elapsed is not None:
            active_agent_seconds.append(active_agent_elapsed)
        jobs = []
        for job in raw_jobs:
            jobs.append(
                {
                    "jobId": job.get("jobId"),
                    "state": job.get("state"),
                    "items": job.get("items", []),
                    "wallSeconds": job.get("timing", {}).get("wallSeconds"),
                    "providerSeconds": job.get("timing", {}).get("providerSeconds"),
                }
            )
        families.append(
            {
                "familyId": status.get("familyId"),
                "status": status.get("status"),
                "stage": pipeline.get("stage"),
                "selectedAssets": status.get("selectedAssetCount", 0),
                "expectedAssets": status.get("expectedAssetCount", 0),
                "validation": validation,
                "elapsedSeconds": elapsed,
                "activeElapsedSeconds": active_elapsed,
                "timing": {
                    "queueLatencySeconds": queue_latency,
                    "toCodeApprovalSeconds": code_elapsed,
                    "toAgentApprovalSeconds": agent_elapsed,
                    "toHumanApprovalSeconds": human_elapsed,
                    "activeToCodeApprovalSeconds": active_code_elapsed,
                    "activeToAgentApprovalSeconds": active_agent_elapsed,
                    "activeToHumanApprovalSeconds": active_human_elapsed,
                },
                "jobs": jobs,
                "lastError": pipeline.get("lastError"),
            }
        )
    if requested_families:
        found = {family["familyId"] for family in families}
        missing = sorted(requested_families - found)
        if missing:
            raise SystemExit(f"status_family_not_found:{','.join(missing)}")
    result = {
        "packId": pack.get("packId"),
        "kind": pack.get("kind"),
        "families": families,
        "summary": {
            "familyCount": len(families),
            "approved": sum(family["status"] == "approved" for family in families),
            "readyForHuman": sum(family["status"] == "awaiting-human-review" for family in families),
            "needsRepair": sum(family["status"] in {"needs-repair", "blocked-repair"} for family in families),
            "medianSecondsToCodeApproval": round(statistics.median(code_seconds), 3) if code_seconds else None,
            "medianSecondsToAgentApproval": round(statistics.median(agent_seconds), 3) if agent_seconds else None,
            "medianActiveSecondsToCodeApproval": round(statistics.median(active_code_seconds), 3) if active_code_seconds else None,
            "medianActiveSecondsToAgentApproval": round(statistics.median(active_agent_seconds), 3) if active_agent_seconds else None,
            "targetMedianSeconds": 300,
            "slowFamilySeconds": 600,
        },
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return
    summary = result["summary"]
    print(
        f"pack:{result['packId']} families:{summary['familyCount']} approved:{summary['approved']} "
        f"human-ready:{summary['readyForHuman']} repairs:{summary['needsRepair']}"
    )
    if summary["medianSecondsToCodeApproval"] is not None:
        print(f"median_to_code_approval_seconds:{summary['medianSecondsToCodeApproval']}")
    if summary["medianSecondsToAgentApproval"] is not None:
        print(f"median_to_agent_approval_seconds:{summary['medianSecondsToAgentApproval']}")
    if summary["medianActiveSecondsToCodeApproval"] is not None:
        print(f"median_active_to_code_approval_seconds:{summary['medianActiveSecondsToCodeApproval']}")
    if summary["medianActiveSecondsToAgentApproval"] is not None:
        print(f"median_active_to_agent_approval_seconds:{summary['medianActiveSecondsToAgentApproval']}")
    for family in families:
        elapsed = "-" if family["elapsedSeconds"] is None else f"{family['elapsedSeconds']:.1f}s"
        active = "-" if family["activeElapsedSeconds"] is None else f"{family['activeElapsedSeconds']:.1f}s"
        print(
            f"{family['familyId']}: {family['status']} stage={family['stage']} "
            f"assets={family['selectedAssets']}/{family['expectedAssets']} elapsed={elapsed} active={active}"
        )
        for job in family["jobs"]:
            print(
                f"  {job['jobId']}: {job['state']} provider={job['providerSeconds'] or '-'} "
                f"wall={job['wallSeconds'] or '-'}"
            )


if __name__ == "__main__":
    main()
