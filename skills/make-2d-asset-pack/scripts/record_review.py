#!/usr/bin/env python3
"""Record a Codex decision; human decisions are exclusive to review_server.py."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

from asset_pack_common import append_jsonl, read_json, sha256, write_json


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_recorded(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def promote(status_path: Path, status: dict) -> list[dict[str, str]]:
    family_root = status_path.parent
    pack_root = family_root.parents[1]
    approved_root = family_root / "approved"
    approved_root.mkdir(parents=True, exist_ok=True)
    approved: list[dict[str, str]] = []
    for asset in status["assets"]:
        source = resolve_recorded(pack_root, asset["output"])
        destination = approved_root / source.name
        if destination.exists() and sha256(destination) != asset["outputSha256"]:
            previous_hash = sha256(destination)
            archive = family_root / "approval-history" / previous_hash[:12] / destination.name
            archive.parent.mkdir(parents=True, exist_ok=True)
            if archive.exists() and sha256(archive) != previous_hash:
                raise SystemExit(f"approval_history_conflict:{archive}")
            if not archive.exists():
                shutil.copy2(destination, archive)
        if not destination.exists() or sha256(destination) != asset["outputSha256"]:
            shutil.copy2(source, destination)
        approved.append(
            {
                "file": str(destination.relative_to(pack_root)),
                "sha256": sha256(destination),
                "selectedFrom": asset["output"],
            }
        )
    return approved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, required=True)
    parser.add_argument("--reviewer", choices=("codex",), required=True)
    parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    parser.add_argument("--comment", default="")
    args = parser.parse_args()

    status_path = args.status.resolve()
    status = read_json(status_path)
    validation = status.get("validation")
    if not isinstance(validation, dict):
        raise SystemExit("family_status_validation_required")
    if validation.get("code") != "approved":
        raise SystemExit("codex_review_requires_code_approval")
    normalized = "approved" if args.decision == "approve" else "rejected"
    validation["codex"] = normalized
    status["status"] = "awaiting-human-review" if normalized == "approved" else "codex-rejected"
    if normalized == "rejected":
        validation["human"] = "pending"
    recorded_at = now()
    history = list(status.get("reviewHistory", []))
    history.append(
        {
            "reviewer": "codex",
            "decision": args.decision,
            "comment": args.comment,
            "recordedAt": recorded_at,
            "selectedRound": status.get("selectedRound"),
        }
    )
    status["reviewHistory"] = history
    pipeline = status.setdefault("pipeline", {})
    pipeline["stage"] = "human-review" if normalized == "approved" else "codex-rejected"
    pipeline.setdefault("timing", {})["codexReviewedAt"] = recorded_at
    pipeline["lastError"] = None if normalized == "approved" else (args.comment or "Codex review rejected")
    status["updatedAt"] = recorded_at
    write_json(status_path, status)
    append_jsonl(
        status_path.parent / "events.jsonl",
        {"at": recorded_at, "event": "codex-reviewed", "decision": args.decision, "comment": args.comment},
    )
    print(f"status:{status_path}")
    print(f"family_status:{status['status']}")


if __name__ == "__main__":
    main()
