#!/usr/bin/env python3
"""Append one successful or failed image-generation attempt to a CSV ledger."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from asset_pack_common import exclusive_file_lock, sha256


FIELDS = [
    "recorded_at",
    "family",
    "attempt",
    "status",
    "prompt",
    "prompt_sha256",
    "style_anchor",
    "style_anchor_sha256",
    "identity_template",
    "identity_template_sha256",
    "output",
    "output_sha256",
    "output_width",
    "output_height",
    "elapsed_seconds",
    "error",
]


def file_hash(path: Path | None) -> str:
    return sha256(path) if path else ""


def portable_path(path: Path | None, root: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError as error:
        raise SystemExit(f"generation_path_outside_pack_root:{path.resolve()}") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--status", choices=("success", "failed"), required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--style-anchor", type=Path)
    parser.add_argument("--identity-template", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--elapsed-seconds", type=float)
    parser.add_argument("--error", default="")
    args = parser.parse_args()
    ledger_root = args.ledger.resolve().parent

    for label, path in (("prompt", args.prompt), ("identity_template", args.identity_template)):
        if not path.is_file():
            raise SystemExit(f"generation_input_not_found:{label}:{path}")
    if args.style_anchor and not args.style_anchor.is_file():
        raise SystemExit(f"generation_input_not_found:style_anchor:{args.style_anchor}")
    if args.attempt < 1:
        raise SystemExit("generation_attempt_must_be_positive")
    if args.status == "success" and (not args.output or not args.output.is_file()):
        raise SystemExit(f"successful_generation_output_not_found:{args.output}")
    if args.status == "failed" and not args.error.strip():
        raise SystemExit("failed_generation_requires_error")

    width = height = ""
    output_hash = ""
    if args.output and args.output.is_file():
        with Image.open(args.output) as image:
            width, height = image.size
        output_hash = sha256(args.output)
    row = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "family": args.family,
        "attempt": args.attempt,
        "status": args.status,
        "prompt": portable_path(args.prompt, ledger_root),
        "prompt_sha256": sha256(args.prompt),
        "style_anchor": portable_path(args.style_anchor, ledger_root),
        "style_anchor_sha256": file_hash(args.style_anchor),
        "identity_template": portable_path(args.identity_template, ledger_root),
        "identity_template_sha256": file_hash(args.identity_template),
        "output": portable_path(args.output, ledger_root),
        "output_sha256": output_hash,
        "output_width": width,
        "output_height": height,
        "elapsed_seconds": "" if args.elapsed_seconds is None else args.elapsed_seconds,
        "error": args.error,
    }
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(args.ledger.with_suffix(f"{args.ledger.suffix}.lock")):
        exists = args.ledger.exists()
        with args.ledger.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow(row)
    print(f"ledger:{args.ledger}")
    print(f"attempt:{args.attempt}:{args.status}")


if __name__ == "__main__":
    main()
