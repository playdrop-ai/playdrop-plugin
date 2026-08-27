#!/usr/bin/env python3
"""Build a PlayDrop asset-pack catalogue from human-approved family assets."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from asset_pack_common import load_spec, now, read_json, write_json


TAG_REF_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*$")


def canonical_tag_refs(values: object) -> list[str]:
    """Require unique canonical PlayDrop taxonomy refs."""
    if not isinstance(values, list):
        raise SystemExit("pack_tags_array_required")
    retained: list[str] = []
    for value in values:
        if not isinstance(value, str) or not TAG_REF_PATTERN.fullmatch(value):
            raise SystemExit(f"noncanonical_tag:{value}")
        if value in retained:
            raise SystemExit(f"duplicate_tag:{value}")
        retained.append(value)
    return retained


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--validate", action="store_true", help="Run local `playdrop project validate` after writing catalogue.json")
    parser.add_argument("--playdrop-command", default="playdrop")
    args = parser.parse_args()
    pack_root = args.pack_root.resolve()
    spec = load_spec(pack_root / "pack-spec.json")
    pack = spec["pack"]
    if str(pack.get("visibility") or "PRIVATE").upper() == "PUBLIC" and pack.get("publicationRights") != "cleared":
        raise SystemExit(f"publication_rights_not_cleared:{pack.get('publicationRights')}")
    pack_tags = canonical_tag_refs(pack.get("tags", []))
    owned_assets = []
    for family in spec["families"]:
        family_root = pack_root / "families" / family["id"]
        status = read_json(family_root / "family-status.json")
        if status.get("status") != "approved" or status.get("validation", {}).get("human") != "approved":
            raise SystemExit(f"family_not_human_approved:{family['id']}:{status.get('status')}")
        selected = {asset["itemId"]: asset for asset in status.get("assets", [])}
        for item in family["items"]:
            asset = selected.get(item["id"])
            if not asset:
                continue
            approved = family_root / "approved" / Path(asset["output"]).name
            if not approved.is_file():
                raise SystemExit(f"approved_asset_not_found:{approved}")
            owned_assets.append(
                {
                    "name": f"{family['id']}-{item['id']}",
                    "displayName": item["name"],
                    "description": item["payload"],
                    "category": "IMAGE",
                    "subcategory": "generic",
                    "format": "PNG",
                    "visibility": str(pack.get("visibility") or "PRIVATE"),
                    "license": str(pack.get("license") or "PLAYDROP"),
                    "tags": pack_tags,
                    "files": {"primary": str(approved.relative_to(pack_root))},
                }
            )
    if not owned_assets:
        raise SystemExit("approved_assets_required")
    catalogue = {
        "assetPacks": [
            {
                "name": pack["id"],
                "displayName": pack["name"],
                "version": str(pack.get("version") or "1.0.0"),
                "license": str(pack.get("license") or "PLAYDROP"),
                "visibility": str(pack.get("visibility") or "PRIVATE"),
                "tags": pack_tags,
                "releaseNotes": "Initial validated 2D asset-pack release.",
                "ownedAssets": owned_assets,
            }
        ]
    }
    catalogue_path = pack_root / "catalogue.json"
    write_json(catalogue_path, catalogue)
    print(f"catalogue:{catalogue_path}")
    print(f"owned_assets:{len(owned_assets)}")
    if args.validate:
        result = subprocess.run(
            [args.playdrop_command, "project", "validate"],
            cwd=pack_root,
            text=True,
            capture_output=True,
            check=False,
        )
        print(result.stdout, end="")
        if result.returncode != 0:
            print(result.stderr, end="")
            raise SystemExit(result.returncode)
    finalized_at = now()
    status_path = pack_root / "pack-status.json"
    pack_status = read_json(status_path)
    pack_status["status"] = "finalized"
    pack_status["catalogue"] = {
        "path": str(catalogue_path.relative_to(pack_root)),
        "ownedAssetCount": len(owned_assets),
        "playdropValidation": "passed" if args.validate else "not-run",
    }
    pack_status.setdefault("timing", {})["finalizedAt"] = finalized_at
    pack_status["updatedAt"] = finalized_at
    write_json(status_path, pack_status)
    print(f"pack_status:{pack_status['status']}")


if __name__ == "__main__":
    main()
