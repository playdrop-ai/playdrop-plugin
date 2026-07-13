#!/usr/bin/env python3
"""Verify an immutable approved asset manifest without copying its files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from PIL import Image

from asset_pack_common import load_spec, read_json, sha256, write_json


def assets_from_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    families = manifest.get("families")
    if not isinstance(families, dict):
        raise SystemExit("approved_manifest_families_required")
    assets: list[dict[str, Any]] = []
    for family_id, family in families.items():
        for asset in family.get("assets", []):
            assets.append({"family": family_id, **asset})
    return assets


def parse_size(value: str | None, label: str) -> tuple[int, int] | None:
    if not value:
        return None
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except (TypeError, ValueError) as error:
        raise SystemExit(f"invalid_{label}_size:{value}") from error
    if width < 1 or height < 1:
        raise SystemExit(f"invalid_{label}_size:{value}")
    return width, height


def asset_kind(asset: dict[str, Any], path: Path) -> str | None:
    kind = asset.get("kind")
    if kind in ("large", "small"):
        return str(kind)
    if path.stem.endswith("-large"):
        return "large"
    if path.stem.endswith("-small"):
        return "small"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--large-size")
    parser.add_argument("--small-size")
    parser.add_argument("--approved-glob", default="families/*/approved/*.png")
    args = parser.parse_args()

    manifest = read_json(args.manifest.resolve())
    root = args.root.resolve()
    spec = load_spec(args.spec.resolve()) if args.spec else None
    fallback_sizes = {
        "large": parse_size(args.large_size, "large"),
        "small": parse_size(args.small_size, "small"),
    }
    assets = assets_from_manifest(manifest)
    expected = args.expected_count if args.expected_count is not None else manifest.get("totalPngs")
    failures: list[str] = []
    if expected is not None and len(assets) != int(expected):
        failures.append(f"asset_count:{len(assets)}:{expected}")
    checks: list[dict[str, Any]] = []
    for asset in assets:
        relative = str(asset.get("file", ""))
        path = root / relative
        item_failures: list[str] = []
        if not path.is_file():
            item_failures.append("missing")
        else:
            if sha256(path) != asset.get("sha256"):
                item_failures.append("hash_mismatch")
            try:
                with Image.open(path) as image:
                    image.load()
                    kind = asset_kind(asset, path)
                    if asset.get("width") is not None and asset.get("height") is not None:
                        size = (int(asset["width"]), int(asset["height"]))
                    elif spec and kind:
                        size = (
                            int(spec["variants"][kind]["width"]),
                            int(spec["variants"][kind]["height"]),
                        )
                    else:
                        size = fallback_sizes.get(kind or "")
                    if image.format != "PNG":
                        item_failures.append(f"format:{image.format}")
                    if size is None:
                        item_failures.append("expected_size_missing")
                    elif image.size != size:
                        item_failures.append(f"size:{image.width}x{image.height}:{size[0]}x{size[1]}")
                    if "A" not in image.getbands():
                        item_failures.append("alpha_missing")
                    elif image.convert("RGBA").getchannel("A").getextrema() == (255, 255):
                        item_failures.append("alpha_has_no_transparency")
            except OSError:
                item_failures.append("invalid_png")
        failures.extend(f"{relative}:{failure}" for failure in item_failures)
        checks.append({"family": asset["family"], "file": relative, "failures": item_failures})
    expected_files = {str(asset.get("file", "")) for asset in assets}
    actual_files = {
        str(path.relative_to(root))
        for path in root.glob(args.approved_glob)
        if path.is_file()
    }
    for relative in sorted(actual_files - expected_files):
        failures.append(f"unexpected_approved_file:{relative}")
    for relative in sorted(expected_files - actual_files):
        failures.append(f"approved_glob_missing_manifest_file:{relative}")
    report = {
        "passed": not failures,
        "expectedCount": expected,
        "checkedCount": len(assets),
        "failures": failures,
        "approvedGlob": args.approved_glob,
        "approvedFiles": sorted(actual_files),
        "assets": checks,
    }
    if args.report:
        write_json(args.report, report)
    print(f"checked:{len(assets)}")
    print(f"result:{'passed' if not failures else 'failed'}")
    for failure in failures:
        print(f"failure:{failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
