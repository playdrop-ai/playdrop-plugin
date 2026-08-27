#!/usr/bin/env python3
"""Verify the selected assets and provenance for one asset-pack family."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from PIL import Image

from asset_pack_common import find_family, load_spec, read_json, sha256, write_json


def resolve_recorded(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--for-publication", action="store_true")
    args = parser.parse_args()

    spec = load_spec(args.spec.resolve())
    family = find_family(spec, args.family)
    root = args.pack_root.resolve()
    status_path = root / "families" / family["id"] / "family-status.json"
    status = read_json(status_path)
    failures: list[str] = []
    rights = spec["pack"].get("publicationRights")
    if args.for_publication and rights != "cleared":
        failures.append(f"publication_rights_not_cleared:{rights}")
    assets = status.get("assets")
    if not isinstance(assets, list):
        raise SystemExit("family_status_assets_required")
    expected = len(family["items"])
    if len(assets) != expected:
        failures.append(f"asset_count:{len(assets)}:{expected}")
    seen: set[str] = set()
    items = {item["id"]: item for item in family["items"]}
    checks: list[dict[str, Any]] = []
    for asset in assets:
        item_id = str(asset.get("itemId", ""))
        if item_id in seen:
            failures.append(f"duplicate_asset:{item_id}")
        seen.add(item_id)
        item = items.get(item_id)
        if item is None:
            failures.append(f"invalid_item:{item_id}")
            continue
        path_value = str(asset.get("output", ""))
        path = resolve_recorded(root, path_value)
        item_failures: list[str] = []
        for label, path_field, hash_field in (
            ("source", "source", "sourceSha256"),
            ("prompt", "prompt", "promptSha256"),
            ("style_anchor", "styleAnchor", "styleAnchorSha256"),
            ("identity_template", "identityTemplate", "identityTemplateSha256"),
        ):
            recorded = str(asset.get(path_field, ""))
            recorded_hash = str(asset.get(hash_field, ""))
            if not recorded or not recorded_hash:
                item_failures.append(f"provenance_missing:{label}")
                continue
            if Path(recorded).is_absolute():
                item_failures.append(f"provenance_absolute_path:{label}")
            provenance_path = resolve_recorded(root, recorded)
            if not provenance_path.is_file():
                item_failures.append(f"provenance_file_missing:{label}")
            elif sha256(provenance_path) != recorded_hash:
                item_failures.append(f"provenance_hash_mismatch:{label}")
        if not str(asset.get("extractor", "")):
            item_failures.append("provenance_missing:extractor")
        if not path.is_file():
            item_failures.append("missing")
        else:
            digest = sha256(path)
            if digest != asset.get("outputSha256"):
                item_failures.append("hash_mismatch")
            try:
                with Image.open(path) as image:
                    image.load()
                    expected_size = (
                        int(item["output"]["width"]),
                        int(item["output"]["height"]),
                    )
                    if image.format != "PNG":
                        item_failures.append(f"format:{image.format}")
                    if image.size != expected_size:
                        item_failures.append(f"size:{image.width}x{image.height}:{expected_size[0]}x{expected_size[1]}")
                    if "A" not in image.getbands():
                        item_failures.append("alpha_missing")
                    elif image.convert("RGBA").getchannel("A").getextrema() == (255, 255):
                        item_failures.append("alpha_has_no_transparency")
            except OSError:
                item_failures.append("invalid_image")
        failures.extend(f"{item_id}:{failure}" for failure in item_failures)
        checks.append({"itemId": item_id, "file": path_value, "failures": item_failures})
    for item in family["items"]:
        if item["id"] not in seen:
            failures.append(f"missing_expected:{item['id']}")
    if status.get("validation", {}).get("code") != "approved":
        failures.append(f"family_code_status:{status.get('validation', {}).get('code')}")
    approved_root = status_path.parent / "approved"
    actual_approved = {
        str(path.relative_to(root))
        for path in approved_root.glob("*.png")
        if path.is_file()
    }
    expected_records = status.get("approvedAssets") or status.get("lastApprovedAssets") or []
    expected_approved = {str(record.get("file")) for record in expected_records if record.get("file")}
    for relative in sorted(actual_approved - expected_approved):
        failures.append(f"unexpected_approved_file:{relative}")
    for relative in sorted(expected_approved - actual_approved):
        failures.append(f"missing_approved_file:{relative}")
    report = {
        "family": family["name"],
        "familyId": family["id"],
        "passed": not failures,
        "expectedAssets": expected,
        "checkedAssets": len(assets),
        "failures": failures,
        "approvedDirectory": {
            "expected": sorted(expected_approved),
            "actual": sorted(actual_approved),
        },
        "assets": checks,
    }
    if args.report:
        write_json(args.report, report)
    print(f"family:{family['id']}")
    print(f"checked:{len(assets)}")
    print(f"result:{'passed' if not failures else 'failed'}")
    for failure in failures:
        print(f"failure:{failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
