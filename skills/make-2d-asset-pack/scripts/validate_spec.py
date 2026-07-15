#!/usr/bin/env python3
"""Validate an asset-pack spec, rights state, and local reference coverage."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_pack_common import load_spec, resolve_input_path, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--for-publication", action="store_true")
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = load_spec(spec_path)
    failures: list[str] = []
    warnings: list[str] = []
    anchor = resolve_input_path(spec_path, spec["styleAnchor"].get("path"))
    if not anchor or not anchor.is_file():
        failures.append(f"style_anchor_not_found:{anchor}")
    if spec["styleAnchor"].get("ownership") == "unknown":
        failures.append("style_anchor_ownership_unknown")
    rights = spec["pack"].get("publicationRights")
    if rights != "cleared":
        if args.for_publication:
            failures.append(f"publication_rights_not_cleared:{rights}")
        else:
            warnings.append(f"publication_blocked:{rights}")
    visual = 0
    semantic = 0
    item_count = 0
    for family in spec["families"]:
        for item in family["items"]:
            item_count += 1
            if item.get("referenceType") == "visual-reference":
                visual += 1
                for kind in ("large", "small"):
                    path = resolve_input_path(spec_path, (item.get("references") or {}).get(kind))
                    if not path or not path.is_file():
                        failures.append(f"visual_reference_not_found:{family['id']}:{item['id']}:{kind}:{path}")
            else:
                semantic += 1
    report = {
        "passed": not failures,
        "pack": spec["pack"].get("name"),
        "families": len(spec["families"]),
        "items": item_count,
        "pngOutputs": item_count * 2,
        "visualReferenceItems": visual,
        "semanticOnlyItems": semantic,
        "failures": failures,
        "warnings": warnings,
    }
    if args.report:
        write_json(args.report, report)
    for key in ("families", "items", "pngOutputs", "visualReferenceItems", "semanticOnlyItems"):
        print(f"{key}:{report[key]}")
    for warning in warnings:
        print(f"warning:{warning}")
    for failure in failures:
        print(f"failure:{failure}")
    print(f"result:{'passed' if not failures else 'failed'}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
