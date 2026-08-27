#!/usr/bin/env python3
"""Build a portable manifest for every fully approved family in an asset pack."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from asset_pack_common import load_spec, read_json, sha256, write_json


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_manifest(pack_root: Path, spec_path: Path) -> dict[str, Any]:
    root = pack_root.resolve()
    spec = load_spec(spec_path.resolve())
    families: dict[str, Any] = {}
    total_pngs = 0
    for family in spec["families"]:
        status_path = root / "families" / family["id"] / "family-status.json"
        if not status_path.is_file():
            continue
        status = read_json(status_path)
        if status.get("status") != "approved":
            continue
        validation = status.get("validation", {})
        if any(validation.get(gate) != "approved" for gate in ("code", "agent", "human")):
            raise SystemExit(f"approved_family_gate_mismatch:{family['id']}")
        approved = status.get("approvedAssets")
        selected = status.get("assets")
        if not isinstance(approved, list) or not isinstance(selected, list):
            raise SystemExit(f"approved_family_assets_required:{family['id']}")
        expected = len(family["items"])
        if len(approved) != expected or len(selected) != expected:
            raise SystemExit(f"approved_family_asset_count:{family['id']}:{len(approved)}:{expected}")
        selected_by_output = {str(asset.get("output")): asset for asset in selected}
        assets: list[dict[str, Any]] = []
        for entry in approved:
            relative = str(entry.get("file", ""))
            selected_from = str(entry.get("selectedFrom", ""))
            source = selected_by_output.get(selected_from)
            if not relative or source is None:
                raise SystemExit(f"approved_asset_provenance_missing:{family['id']}:{relative}")
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError as error:
                raise SystemExit(f"approved_asset_outside_pack_root:{path}") from error
            if not path.is_file() or sha256(path) != entry.get("sha256"):
                raise SystemExit(f"approved_asset_hash_mismatch:{relative}")
            with Image.open(path) as image:
                width, height = image.size
            item = next((item for item in family["items"] if item["id"] == source.get("itemId")), None)
            if item is None:
                raise SystemExit(f"approved_asset_item_missing:{family['id']}:{source.get('itemId')}")
            expected_size = (
                int(item["output"]["width"]),
                int(item["output"]["height"]),
            )
            if (width, height) != expected_size:
                raise SystemExit(f"approved_asset_size_mismatch:{relative}:{width}x{height}")
            assets.append(
                {
                    "item": source.get("item"),
                    "itemId": source.get("itemId"),
                    "file": relative,
                    "sha256": entry["sha256"],
                    "width": width,
                    "height": height,
                    "selectedFrom": selected_from,
                    "sourceSha256": source.get("sourceSha256"),
                    "promptSha256": source.get("promptSha256"),
                    "identityTemplateSha256": source.get("identityTemplateSha256"),
                    "extractor": source.get("extractor"),
                }
            )
        expected_files = {str(asset["file"]) for asset in assets}
        actual_files = {
            str(path.relative_to(root))
            for path in (root / "families" / family["id"] / "approved").glob("*.png")
            if path.is_file()
        }
        unexpected = sorted(actual_files - expected_files)
        missing = sorted(expected_files - actual_files)
        if unexpected:
            raise SystemExit(f"unexpected_approved_files:{family['id']}:{','.join(unexpected)}")
        if missing:
            raise SystemExit(f"missing_approved_files:{family['id']}:{','.join(missing)}")
        assets.sort(key=lambda asset: str(asset["itemId"]))
        families[family["id"]] = {
            "name": family["name"],
            "selectedRound": status.get("selectedRound"),
            "assets": assets,
        }
        total_pngs += len(assets)
    return {
        "schemaVersion": 1,
        "generatedAt": now(),
        "pack": {"id": spec["pack"]["id"], "name": spec["pack"]["name"]},
        "approvedFamilies": len(families),
        "totalPngs": total_pngs,
        "families": families,
    }


def write_approved_manifest(pack_root: Path, spec_path: Path, output: Path | None = None) -> Path:
    destination = output.resolve() if output else pack_root.resolve() / "approved-manifest.json"
    write_json(destination, build_manifest(pack_root, spec_path))
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    destination = write_approved_manifest(args.pack_root, args.spec, args.output)
    manifest = read_json(destination)
    print(f"manifest:{destination}")
    print(f"approved_families:{manifest['approvedFamilies']}")
    print(f"pngs:{manifest['totalPngs']}")


if __name__ == "__main__":
    main()
