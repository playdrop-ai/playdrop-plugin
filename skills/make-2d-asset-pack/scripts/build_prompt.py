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
    read_json,
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
    payload_overrides = read_json(args.payload_overrides.resolve()) if args.payload_overrides else None
    slots = slots_for_family(
        family,
        args.mode,
        parse_item_ids(args.items),
        payload_overrides,
    )
    rows, columns = grid_for_slots(len(slots), args.columns)
    matte = parse_hex_color(args.matte)
    matte_hex = color_hex(matte)
    style_anchor = spec.get("styleAnchor", {})
    style = str(style_anchor.get("stylePrompt") or DEFAULT_STYLE).strip()
    style_references = [
        value
        for value in [style_anchor.get("path"), *style_anchor.get("additionalReferences", [])]
        if value
    ]
    style_references.extend(
        reference["path"] if isinstance(reference, dict) else reference
        for reference in family.get("continuityStyleReferences", [])
    )
    style_references = list(dict.fromkeys(style_references))
    style_reference_count = (
        args.style_reference_count
        if args.style_reference_count is not None
        else len(style_references)
    )
    identity_number = style_reference_count + 1 if style_reference_count else 1
    if style_reference_count:
        count = style_reference_count
        style_images = "Image 1" if count == 1 else f"Images 1 through {count}"
        input_contract = (
            f"Input images: {style_images} are creator-authorized visual style references only; ignore their "
            f"subjects and backgrounds. Image {identity_number} is the authoritative identity, slot order, payload, "
            "and target-view template; ignore its original visual style."
        )
    else:
        input_contract = (
            "Input images: Image 1 is the authoritative identity, slot order, payload, and target-view template. "
            "There is no visual style reference in this bootstrap call; establish the canonical style from the "
            "written Style contract below."
        )
    variant_summary = {
        "paired": "large and small gameplay assets",
        "large": "large gameplay assets",
        "small": "small gameplay icons",
    }[args.mode]
    lines = [
        "Use case: style-transfer",
        f"Asset type: {family['name']} {variant_summary} on a removable matte",
        input_contract,
        "",
        (
            f"Create one high-resolution source sheet with exactly {columns} columns by {rows} rows and exactly "
            f"{len(slots)} slots on a visually uniform solid {matte_hex} matte. Follow Image {identity_number} "
            "exactly, left to "
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
                "invisible cells; no overlaps; no text, labels, numbers, dividers, frames, people, or unrequested "
                "extra props. Every object explicitly required by a slot payload is part of that asset, not an "
                "extra prop."
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
    parser.add_argument("--payload-overrides", type=Path, help="JSON payload replacements for requested variants")
    parser.add_argument("--style-reference-count", type=int, help="Exact number of supplied style images")
    parser.add_argument("--columns", type=int)
    parser.add_argument("--matte", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.style_reference_count is not None and args.style_reference_count < 0:
        raise SystemExit("style_reference_count_must_be_nonnegative")
    prompt = build_prompt(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(prompt, encoding="utf-8")
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    print(f"prompt:{args.output}")
    print(f"sha256:{digest}")


if __name__ == "__main__":
    main()
