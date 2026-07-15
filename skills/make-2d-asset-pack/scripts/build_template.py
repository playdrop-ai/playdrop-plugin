#!/usr/bin/env python3
"""Compose a private identity template from a PlayDrop asset-pack spec."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from asset_pack_common import (
    find_family,
    grid_for_slots,
    load_spec,
    parse_item_ids,
    read_json,
    resolve_input_path,
    sha256,
    slots_for_family,
    write_json,
)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGBA")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def build(args: argparse.Namespace) -> None:
    spec_path = args.spec.resolve()
    spec = load_spec(spec_path)
    family = find_family(spec, args.family)
    payload_overrides = read_json(args.payload_overrides.resolve()) if args.payload_overrides else None
    slots = slots_for_family(
        family,
        args.mode,
        parse_item_ids(args.items),
        payload_overrides,
    )
    rows, columns = grid_for_slots(len(slots), args.columns)
    cell = args.cell_size
    canvas = Image.new("RGB", (columns * cell, rows * cell), (246, 246, 246))
    draw = ImageDraw.Draw(canvas)
    label_font = font(max(20, cell // 18), bold=True)
    detail_font = font(max(16, cell // 24))
    metadata_slots: list[dict[str, object]] = []

    for index, slot in enumerate(slots):
        row, column = divmod(index, columns)
        x0, y0 = column * cell, row * cell
        x1, y1 = x0 + cell, y0 + cell
        draw.rectangle((x0, y0, x1 - 1, y1 - 1), outline=(70, 70, 70), width=2)
        label = f"{index + 1}. {slot['item']} {slot['kind']}"
        draw.text((x0 + 16, y0 + 12), label, fill=(20, 20, 20), font=label_font)
        reference = resolve_input_path(spec_path, slot.get("reference"))
        reference_hash = None
        if slot["referenceType"] == "visual-reference" and (not reference or not reference.exists()):
            raise SystemExit(f"visual_reference_not_found:{slot['itemId']}:{slot['kind']}:{reference}")
        if reference and reference.exists():
            reference_hash = sha256(reference)
            source = Image.open(reference)
            image = contain(source, (cell - 48, cell - 100))
            px = x0 + (cell - image.width) // 2
            py = y0 + 62 + (cell - 86 - image.height) // 2
            canvas.paste(image, (px, py), image)
        else:
            text = f"SEMANTIC ONLY\n{slot['payload']}"
            box = (x0 + 28, y0 + 92, x1 - 28, y1 - 28)
            draw.rounded_rectangle(box, radius=12, fill=(230, 230, 230), outline=(130, 130, 130), width=2)
            wrapped = "\n".join(wrap_text(text, 34))
            draw.multiline_text((box[0] + 18, box[1] + 18), wrapped, fill=(35, 35, 35), font=detail_font, spacing=7)
        metadata_slots.append(
            {
                **slot,
                "box": [x0, y0, x1, y1],
                "referenceFile": Path(str(slot["reference"])).name if slot.get("reference") else None,
                "referenceSha256": reference_hash,
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.family}-{args.mode}-identity-template"
    image_path = args.output_dir / f"{stem}.png"
    metadata_path = args.output_dir / f"{stem}.json"
    canvas.save(image_path)
    write_json(
        metadata_path,
        {
            "schemaVersion": 1,
            "private": True,
            "family": family["name"],
            "familyId": family["id"],
            "mode": args.mode,
            "canvas": {"width": canvas.width, "height": canvas.height},
            "grid": {"rows": rows, "columns": columns},
            "slots": metadata_slots,
            "template": image_path.name,
            "templateSha256": sha256(image_path),
        },
    )
    print(f"template:{image_path}")
    print(f"metadata:{metadata_path}")


def wrap_text(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--mode", choices=("paired", "large", "small"), default="paired")
    parser.add_argument("--items", help="Comma-separated item ids for an item-specific repair template")
    parser.add_argument("--payload-overrides", type=Path, help="JSON payload replacements for requested variants")
    parser.add_argument("--columns", type=int)
    parser.add_argument("--cell-size", type=int, default=384)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.cell_size < 192:
        raise SystemExit("cell_size_too_small")
    build(args)


if __name__ == "__main__":
    main()
