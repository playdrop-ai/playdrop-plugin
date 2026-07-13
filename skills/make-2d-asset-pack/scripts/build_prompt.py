#!/usr/bin/env python3
"""Build a reproducible image-generation prompt from an asset-pack spec."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from asset_pack_common import (
    color_hex,
    find_family,
    grid_for_slots,
    load_spec,
    parse_hex_color,
    parse_item_ids,
    slots_for_family,
)


DEFAULT_STYLE = (
    "Match Image 1's polished top-tier casual mobile game rendering, friendly rounded construction, "
    "clean silhouettes, balanced saturated color, and controlled internal form shading. Avoid hard glossy "
    "plastic-toy material."
)


def build_prompt(args: argparse.Namespace) -> str:
    spec = load_spec(args.spec.resolve())
    family = find_family(spec, args.family)
    slots = slots_for_family(family, args.mode, parse_item_ids(args.items))
    rows, columns = grid_for_slots(len(slots), args.columns)
    matte = parse_hex_color(args.matte)
    matte_hex = color_hex(matte)
    style = str(spec.get("styleAnchor", {}).get("stylePrompt") or DEFAULT_STYLE).strip()
    variant_summary = {
        "paired": "large and small gameplay assets",
        "large": "large gameplay assets",
        "small": "small gameplay icons",
    }[args.mode]
    lines = [
        "Use case: style-transfer",
        f"Asset type: {family['name']} {variant_summary} on a removable matte",
        (
            "Input images: Image 1 is the mandatory creator-owned visual style anchor only; ignore its subjects "
            "and background. Image 2 is the authoritative identity, slot order, payload, and target-view template; "
            "ignore its original visual style."
        ),
        "",
        (
            f"Create one high-resolution source sheet with exactly {columns} columns by {rows} rows and exactly "
            f"{len(slots)} slots on a visually uniform solid {matte_hex} matte. Follow Image 2 exactly, left to "
            "right and top to bottom:"
        ),
    ]
    for index, slot in enumerate(slots, start=1):
        lines.append(f"{index}. {slot['item']} {slot['kind']}: {slot['payload']}")
    lines.extend(["", f"Style: {style}", ""])
    if args.mode in ("paired", "large"):
        lines.append(
            "LARGE VIEW CONTRACT: detailed, dimensional, and perspective-aware where appropriate. Preserve the "
            "complete silhouette, use sturdy readable geometry, and follow every large payload literally."
        )
    if args.mode in ("paired", "small"):
        lines.append(
            "SMALL VIEW CONTRACT: purpose-designed strict front or pure side orthographic 64x64 icon, never a "
            "scaled or cropped large asset. Use a bold silhouette, few broad color regions, minimal internal lines, "
            "no material grain, and no tiny texture. Follow every small payload literally even when it contains "
            "fewer objects than the large payload."
        )
    lines.extend(
        [
            "",
            (
                f"Never use {matte_hex} or a near-{matte_hex} color anywhere in a subject. Background: every "
                f"exterior pixel is the same uniform solid {matte_hex}."
            ),
            (
                "Constraints: exactly one complete asset composition per slot; generous padding; stable equal "
                "invisible cells; no overlaps; no text, labels, numbers, dividers, frames, people, or extra props."
            ),
            (
                "Forbidden: every exterior cast shadow, contact shadow, floor blob, ambient shadow outside the "
                "silhouette, reflection, glow, gradient, texture, floor plane, clipping, watermark, or logo. "
                "Lighting and form shading may exist only inside each asset silhouette."
            ),
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--mode", choices=("paired", "large", "small"), default="paired")
    parser.add_argument("--items", help="Comma-separated item ids for an item-specific repair prompt")
    parser.add_argument("--columns", type=int)
    parser.add_argument("--matte", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prompt = build_prompt(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(prompt, encoding="utf-8")
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    print(f"prompt:{args.output}")
    print(f"sha256:{digest}")


if __name__ == "__main__":
    main()
