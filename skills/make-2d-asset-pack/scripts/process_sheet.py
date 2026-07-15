#!/usr/bin/env python3
"""Adaptively split, extract, measure, and board one generated asset sheet."""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from asset_pack_common import (
    color_hex,
    find_family,
    grid_for_slots,
    load_spec,
    parse_hex_color,
    parse_item_ids,
    resolve_input_path,
    retry_limits,
    sha256,
    slots_for_family,
    write_json,
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def percentile(values: np.ndarray, amount: float) -> float:
    return round(float(np.percentile(values, amount)), 3)


def border_samples(image: Image.Image, rows: int, columns: int, patch: int = 14) -> np.ndarray:
    array = np.asarray(image.convert("RGB"), dtype=np.float32)
    patch = max(4, min(patch, image.width // 12, image.height // 12))
    samples = [
        array[:patch].reshape(-1, 3),
        array[-patch:].reshape(-1, 3),
        array[:, :patch].reshape(-1, 3),
        array[:, -patch:].reshape(-1, 3),
    ]
    for row in range(rows):
        for column in range(columns):
            x0 = round(column * image.width / columns)
            x1 = round((column + 1) * image.width / columns)
            y0 = round(row * image.height / rows)
            y1 = round((row + 1) * image.height / rows)
            for x, y in ((x0, y0), (x1 - patch, y0), (x0, y1 - patch), (x1 - patch, y1 - patch)):
                samples.append(array[max(0, y):min(image.height, y + patch), max(0, x):min(image.width, x + patch)].reshape(-1, 3))
    return np.concatenate(samples, axis=0)


def matte_profile(image: Image.Image, rows: int, columns: int, requested: tuple[int, int, int]) -> dict[str, Any]:
    samples = border_samples(image, rows, columns)
    requested_array = np.asarray(requested, dtype=np.float32)
    median = np.median(samples, axis=0)
    requested_distance = np.linalg.norm(samples - requested_array, axis=1)
    median_distance = np.linalg.norm(samples - median, axis=1)
    return {
        "sampleCount": int(len(samples)),
        "requestedRgb": list(requested),
        "requestedHex": color_hex(requested),
        "medianRgb": [round(float(value), 2) for value in median],
        "medianDistanceFromRequested": round(float(np.linalg.norm(median - requested_array)), 3),
        "distanceFromRequestedP50": percentile(requested_distance, 50),
        "distanceFromRequestedP95": percentile(requested_distance, 95),
        "distanceFromRequestedP99": percentile(requested_distance, 99),
        "distanceFromMedianP50": percentile(median_distance, 50),
        "distanceFromMedianP95": percentile(median_distance, 95),
        "distanceFromMedianP99": percentile(median_distance, 99),
    }


def smooth_projection(values: np.ndarray, width: int = 9) -> np.ndarray:
    kernel = np.ones(width, dtype=np.float32) / width
    return np.convolve(values.astype(np.float32), kernel, mode="same")


def choose_gap(projection: np.ndarray, nominal: int, radius: int) -> int:
    smooth = smooth_projection(projection)
    left = max(8, nominal - radius)
    right = min(len(smooth) - 8, nominal + radius)
    if right <= left:
        return nominal
    segment = smooth[left:right]
    cutoff = float(np.percentile(segment, 12))
    candidates = np.where(segment <= cutoff)[0] + left
    if len(candidates) == 0:
        return int(left + np.argmin(segment))
    runs: list[tuple[int, int]] = []
    start = previous = int(candidates[0])
    for raw in candidates[1:]:
        value = int(raw)
        if value > previous + 1:
            runs.append((start, previous))
            start = value
        previous = value
    runs.append((start, previous))
    centers = [(start + end) // 2 for start, end in runs]
    return min(centers, key=lambda value: abs(value - nominal))


def adaptive_grid(image: Image.Image, rows: int, columns: int, profile: dict[str, Any]) -> dict[str, Any]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    measured_key = np.asarray(profile["medianRgb"], dtype=np.float32)
    distance = np.linalg.norm(rgb - measured_key, axis=2)
    foreground_threshold = max(48.0, float(profile["distanceFromMedianP99"]) + 12.0)
    foreground = distance > foreground_threshold
    row_projection = foreground.sum(axis=1)
    row_bounds = [0]
    for index in range(1, rows):
        nominal = round(index * image.height / rows)
        row_bounds.append(choose_gap(row_projection, nominal, round(image.height / rows * 0.22)))
    row_bounds.append(image.height)
    if row_bounds != sorted(set(row_bounds)):
        raise SystemExit("adaptive_row_boundaries_invalid")

    boxes: list[list[int]] = []
    column_bounds_by_row: list[list[int]] = []
    for row in range(rows):
        top, bottom = row_bounds[row], row_bounds[row + 1]
        projection = foreground[top:bottom].sum(axis=0)
        bounds = [0]
        for index in range(1, columns):
            nominal = round(index * image.width / columns)
            bounds.append(choose_gap(projection, nominal, round(image.width / columns * 0.22)))
        bounds.append(image.width)
        if bounds != sorted(set(bounds)):
            raise SystemExit(f"adaptive_column_boundaries_invalid:{row}")
        column_bounds_by_row.append(bounds)
        for column in range(columns):
            boxes.append([bounds[column], top, bounds[column + 1], bottom])
    return {
        "method": "matte-gap-adaptive",
        "foregroundThreshold": round(foreground_threshold, 3),
        "rowBounds": row_bounds,
        "columnBoundsByRow": column_bounds_by_row,
        "boxes": boxes,
    }


def split_overlay(image: Image.Image, rows: int, columns: int, layout: dict[str, Any], output: Path) -> None:
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    for index in range(1, rows):
        y = round(index * canvas.height / rows)
        draw.line((0, y, canvas.width, y), fill=(30, 100, 255), width=3)
    for index in range(1, columns):
        x = round(index * canvas.width / columns)
        draw.line((x, 0, x, canvas.height), fill=(30, 100, 255), width=3)
    for y in layout["rowBounds"][1:-1]:
        draw.line((0, y, canvas.width, y), fill=(255, 255, 0), width=3)
    for row, bounds in enumerate(layout["columnBoundsByRow"]):
        top, bottom = layout["rowBounds"][row], layout["rowBounds"][row + 1]
        for x in bounds[1:-1]:
            draw.line((x, top, x, bottom), fill=(255, 255, 0), width=3)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def crop_box(image: Image.Image, box: list[int]) -> Image.Image:
    x0, y0, x1, y1 = box
    inset = min(3, max(0, (x1 - x0) // 20), max(0, (y1 - y0) // 20))
    return image.crop((x0 + inset, y0 + inset, x1 - inset, y1 - inset)).convert("RGBA")


def supports_despill(key: tuple[int, int, int]) -> bool:
    return max(key) - min(key) > 16


def soft_chroma(
    image: Image.Image,
    key: tuple[int, int, int],
    transparent_threshold: float,
    opaque_threshold: float,
    despill: bool,
    hue_cleanup: bool = False,
) -> Image.Image:
    data = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    rgb = data[:, :, :3].astype(np.float32)
    distance = np.linalg.norm(rgb - np.asarray(key, dtype=np.float32), axis=2)
    alpha = np.clip((distance - transparent_threshold) / (opaque_threshold - transparent_threshold), 0.0, 1.0)
    key_chroma = np.asarray(key, dtype=np.float32) - float(min(key))
    key_chroma_norm = float(np.linalg.norm(key_chroma))
    if hue_cleanup and key_chroma_norm > 1.0:
        pixel_chroma = rgb - rgb.min(axis=2, keepdims=True)
        pixel_chroma_norm = np.linalg.norm(pixel_chroma, axis=2)
        similarity = np.divide(
            np.sum(pixel_chroma * key_chroma, axis=2),
            pixel_chroma_norm * key_chroma_norm,
            out=np.zeros_like(pixel_chroma_norm),
            where=pixel_chroma_norm > 1.0,
        )
        saturation = rgb.max(axis=2) - rgb.min(axis=2)
        hue_alpha = np.clip((0.985 - similarity) / (0.985 - 0.90), 0.0, 1.0)
        alpha = np.minimum(alpha, np.where(saturation >= 24.0, hue_alpha, 1.0))
    data[:, :, 3] = np.rint(alpha * 255).astype(np.uint8)
    if despill and supports_despill(key):
        key_array = np.asarray(key)
        spill_channels = [index for index in range(3) if int(key_array.max()) - int(key_array[index]) <= 16]
        retained_channels = [index for index in range(3) if index not in spill_channels]
        edge = (data[:, :, 3] > 0) & (data[:, :, 3] < 255)
        replacement = data[:, :, retained_channels].max(axis=2)
        for channel in spill_channels:
            data[:, :, channel][edge] = np.minimum(data[:, :, channel][edge], replacement[edge])
    return Image.fromarray(data)


def hard_key(image: Image.Image, key: tuple[int, int, int], tolerance: float) -> Image.Image:
    data = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    rgb = data[:, :, :3].astype(np.float32)
    key_rgb = np.asarray(key, dtype=np.float32)
    distance = np.linalg.norm(rgb - key_rgb, axis=2)
    data[:, :, 3] = np.where(distance <= tolerance, 0, 255).astype(np.uint8)
    return Image.fromarray(data)


def finish_chroma_edge(image: Image.Image, key: tuple[int, int, int]) -> Image.Image:
    data = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    rgb = data[:, :, :3].astype(np.float32)
    key_array = np.asarray(key, dtype=np.float32)
    key_chroma = key_array - key_array.min()
    key_chroma_norm = float(np.linalg.norm(key_chroma))
    if key_chroma_norm <= 1.0:
        return Image.fromarray(data)
    pixel_chroma = rgb - rgb.min(axis=2, keepdims=True)
    pixel_chroma_norm = np.linalg.norm(pixel_chroma, axis=2)
    similarity = np.divide(
        np.sum(pixel_chroma * key_chroma, axis=2),
        pixel_chroma_norm * key_chroma_norm,
        out=np.zeros_like(pixel_chroma_norm),
        where=pixel_chroma_norm > 1.0,
    )
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    hue_alpha = np.clip((0.985 - similarity) / (0.985 - 0.90), 0.0, 1.0)
    existing_alpha = data[:, :, 3].astype(np.float32) / 255.0
    alpha = np.minimum(existing_alpha, np.where(saturation >= 24.0, hue_alpha, 1.0))
    data[:, :, 3] = np.rint(alpha * 255).astype(np.uint8)
    key_u8 = np.asarray(key)
    spill_channels = [index for index in range(3) if int(key_u8.max()) - int(key_u8[index]) <= 16]
    retained_channels = [index for index in range(3) if index not in spill_channels]
    if retained_channels:
        edge = (data[:, :, 3] > 0) & (data[:, :, 3] < 255)
        replacement = data[:, :, retained_channels].max(axis=2)
        for channel in spill_channels:
            data[:, :, channel][edge] = np.minimum(data[:, :, channel][edge], replacement[edge])
    return Image.fromarray(data)


def rembg_extract(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove
    except ImportError as error:
        raise SystemExit("rembg_not_installed") from error
    result = remove(image.convert("RGBA"))
    if isinstance(result, Image.Image):
        return result.convert("RGBA")
    raise SystemExit("rembg_returned_unsupported_result")


def trim_and_fit(image: Image.Image, width: int, height: int, padding: int) -> Image.Image:
    alpha = np.asarray(image.convert("RGBA"))[:, :, 3]
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))
    trimmed = image.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    available_width = max(1, width - 2 * padding)
    available_height = max(1, height - 2 * padding)
    scale = min(available_width / trimmed.width, available_height / trimmed.height)
    resized = trimmed.resize(
        (max(1, round(trimmed.width * scale)), max(1, round(trimmed.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return canvas


def component_sizes(mask: np.ndarray) -> list[int]:
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=np.bool_)
    sizes: list[int] = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited[y, x] = True
            size = 0
            while queue:
                px, py = queue.popleft()
                size += 1
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
            sizes.append(size)
    return sizes


def remove_tiny_components(image: Image.Image, minimum_pixels: int = 10) -> Image.Image:
    data = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    # Match image_metrics' component-core threshold. Using the looser visible
    # threshold can connect an opaque speck to the subject through a faint
    # antialias bridge, leaving a component that validation still rejects.
    mask = data[:, :, 3] > 32
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=np.bool_)
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited[y, x] = True
            pixels: list[tuple[int, int]] = []
            while queue:
                px, py = queue.popleft()
                pixels.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
            if len(pixels) < minimum_pixels:
                for px, py in pixels:
                    data[py, px, 3] = 0
    return Image.fromarray(data)


def image_metrics(image: Image.Image, key: tuple[int, int, int]) -> dict[str, Any]:
    data = np.asarray(image.convert("RGBA"))
    alpha = data[:, :, 3]
    visible = alpha > 8
    visible_count = int(visible.sum())
    rgb = data[:, :, :3].astype(np.float32)
    key_rgb = np.asarray(key, dtype=np.float32)
    distance = np.linalg.norm(rgb - key_rgb, axis=2)
    key_chroma = key_rgb - key_rgb.min()
    key_chroma_norm = float(np.linalg.norm(key_chroma))
    hue_residue = 0
    if key_chroma_norm > 1.0:
        pixel_chroma = rgb - rgb.min(axis=2, keepdims=True)
        pixel_chroma_norm = np.linalg.norm(pixel_chroma, axis=2)
        similarity = np.divide(
            np.sum(pixel_chroma * key_chroma, axis=2),
            pixel_chroma_norm * key_chroma_norm,
            out=np.zeros_like(pixel_chroma_norm),
            where=pixel_chroma_norm > 1.0,
        )
        saturation = rgb.max(axis=2) - rgb.min(axis=2)
        hue_residue = int((visible & (saturation >= 24.0) & (similarity >= 0.985)).sum())
    sizes = component_sizes(alpha > 32)
    edge = np.concatenate((visible[0], visible[-1], visible[:, 0], visible[:, -1]))
    residue = int((visible & (distance <= 48)).sum())
    return {
        "width": image.width,
        "height": image.height,
        "visiblePixels": visible_count,
        "visibleRatio": round(float(visible.mean()), 6),
        "semiTransparentPixels": int(((alpha > 8) & (alpha < 247)).sum()),
        "componentCount": len(sizes),
        "tinyComponentCount": sum(size < 10 for size in sizes),
        "smallestComponentPixels": min(sizes) if sizes else 0,
        "outputEdgeTouchPixels": int(edge.sum()),
        "residualMattePixelsWithin48": residue,
        "residualMatteRatioWithin48": round(residue / max(1, visible_count), 7),
        "residualMatteHuePixels": hue_residue,
        "residualMatteHueRatio": round(hue_residue / max(1, visible_count), 7),
    }


def checker(size: tuple[int, int], step: int = 16) -> Image.Image:
    image = Image.new("RGBA", size, (235, 235, 235, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle((x, y, x + step - 1, y + step - 1), fill=(195, 195, 195, 255))
    return image


def board_font() -> ImageFont.ImageFont:
    path = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    return ImageFont.truetype(str(path), 18) if path.exists() else ImageFont.load_default()


def make_board(entries: list[dict[str, Any]], output: Path, background: str) -> None:
    columns, tile_width, tile_height = 4, 300, 330
    rows = math.ceil(len(entries) / columns)
    colors = {
        "white": (255, 255, 255, 255),
        "purple": (142, 0, 204, 255),
        "black": (0, 0, 0, 255),
    }
    board = checker((columns * tile_width, rows * tile_height), 20) if background == "checker" else Image.new(
        "RGBA", (columns * tile_width, rows * tile_height), colors[background]
    )
    draw = ImageDraw.Draw(board)
    text = (20, 20, 20, 255) if background in ("white", "checker") else (255, 255, 255, 255)
    for index, entry in enumerate(entries):
        x, y = (index % columns) * tile_width, (index // columns) * tile_height
        asset = Image.open(entry["path"]).convert("RGBA")
        board.alpha_composite(asset, (x + (tile_width - asset.width) // 2, y + 42 + (256 - asset.height) // 2))
        draw.text((x + 12, y + 12), entry["label"], fill=text, font=board_font())
    output.parent.mkdir(parents=True, exist_ok=True)
    board.convert("RGB").save(output)


def make_raw_small_board(entries: list[dict[str, Any]], output: Path) -> None:
    small = [entry for entry in entries if entry["kind"] == "small"]
    columns, tile = 4, 160
    rows = math.ceil(len(small) / columns)
    board = checker((columns * tile, rows * tile), 12)
    draw = ImageDraw.Draw(board)
    for index, entry in enumerate(small):
        x, y = (index % columns) * tile, (index // columns) * tile
        asset = Image.open(entry["path"]).convert("RGBA")
        board.alpha_composite(asset, (x + (tile - asset.width) // 2, y + 46))
        draw.text((x + 8, y + 8), entry["label"], fill=(20, 20, 20, 255), font=board_font())
    output.parent.mkdir(parents=True, exist_ok=True)
    board.convert("RGB").save(output)


def record_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError as error:
        raise SystemExit(f"provenance_path_outside_pack_root:{path.resolve()}") from error


def mode_includes_kind(mode: str, kind: str) -> bool:
    return mode == "paired" or mode == kind


def enforce_retry_limits(
    history: list[dict[str, Any]],
    family_id: str,
    mode: str,
    repair_items: list[str] | None,
    source_hash: str,
    limits: dict[str, int],
    override: bool,
) -> None:
    if override:
        return
    if not repair_items:
        prior_sources = {
            str(entry.get("sourceSha256"))
            for entry in history
            if entry.get("mode") == mode and not entry.get("repairItems") and entry.get("sourceSha256")
        }
        maximum = limits["fullSheetsPerFamilyMaximum"]
        if source_hash not in prior_sources and len(prior_sources) >= maximum:
            raise SystemExit(f"full_sheet_retry_limit_exceeded:{family_id}:{mode}:{maximum}")
        return
    maximum = limits["individualRepairsPerAssetMaximum"]
    kinds = ("large", "small") if mode == "paired" else (mode,)
    for item_id in repair_items:
        for kind in kinds:
            prior_sources = {
                str(entry.get("sourceSha256"))
                for entry in history
                if item_id in (entry.get("repairItems") or [])
                and mode_includes_kind(str(entry.get("mode")), kind)
                and entry.get("sourceSha256")
            }
            if source_hash not in prior_sources and len(prior_sources) >= maximum:
                raise SystemExit(f"item_repair_retry_limit_exceeded:{family_id}:{item_id}:{kind}:{maximum}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--mode", choices=("paired", "large", "small"), default="paired")
    parser.add_argument("--items", help="Comma-separated item ids for an item-specific repair")
    parser.add_argument("--columns", type=int)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--identity-template", type=Path, required=True)
    parser.add_argument("--matte", required=True)
    parser.add_argument("--method", choices=("soft-chroma", "hard-key", "rembg"), required=True)
    parser.add_argument("--round", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--transparent-threshold", type=float)
    parser.add_argument("--opaque-threshold", type=float)
    parser.add_argument("--hard-tolerance", type=float)
    parser.add_argument("--despill", action="store_true")
    parser.add_argument("--override-limit", action="store_true", help="Record and allow an owner-directed retry-limit override")
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    source = args.source.resolve()
    prompt_path = args.prompt.resolve()
    identity_template = args.identity_template.resolve()
    output_root = args.output_root.resolve()
    if not source.exists():
        raise SystemExit(f"source_not_found:{source}")
    if not prompt_path.is_file():
        raise SystemExit(f"prompt_not_found:{prompt_path}")
    if not identity_template.is_file():
        raise SystemExit(f"identity_template_not_found:{identity_template}")
    spec = load_spec(spec_path)
    style_anchor = resolve_input_path(spec_path, spec["styleAnchor"].get("path"))
    if not style_anchor or not style_anchor.is_file():
        raise SystemExit(f"style_anchor_not_found:{style_anchor}")
    family = find_family(spec, args.family)
    repair_items = parse_item_ids(args.items)
    slots = slots_for_family(family, args.mode, repair_items)
    rows, columns = grid_for_slots(len(slots), args.columns)
    key = parse_hex_color(args.matte)
    image = Image.open(source).convert("RGB")
    family_root = output_root / "families" / family["id"]
    status_path = family_root / "family-status.json"
    previous: dict[str, Any] = {}
    if status_path.exists():
        previous = json.loads(status_path.read_text(encoding="utf-8"))
    history = list(previous.get("roundHistory", []))
    source_hash = sha256(source)
    enforce_retry_limits(
        history,
        family["id"],
        args.mode,
        repair_items,
        source_hash,
        retry_limits(spec),
        args.override_limit,
    )
    for provenance_input in (source, prompt_path, style_anchor, identity_template):
        record_path(provenance_input, output_root)
    round_root = family_root / "extraction-rounds" / args.round
    validation_root = family_root / "validation" / args.round
    if round_root.exists() or validation_root.exists():
        raise SystemExit(f"round_already_exists:{args.round}")
    round_root.mkdir(parents=True)
    validation_root.mkdir(parents=True)

    profile = matte_profile(image, rows, columns, key)
    write_json(round_root / "source-preflight.json", profile)
    if profile["medianDistanceFromRequested"] > 96:
        raise SystemExit(f"matte_median_too_far_from_requested:{profile['medianDistanceFromRequested']}")
    if args.method in ("soft-chroma", "hard-key") and profile["distanceFromRequestedP99"] > 80:
        raise SystemExit(f"matte_spread_too_large_for_chroma:{profile['distanceFromRequestedP99']}")

    layout = adaptive_grid(image, rows, columns, profile)
    split_overlay(image, rows, columns, layout, validation_root / "split-overlay.png")
    transparent = args.transparent_threshold or max(12.0, min(80.0, math.ceil(profile["distanceFromRequestedP99"] + 3.0)))
    opaque = args.opaque_threshold or max(115.0, transparent + 64.0)
    if opaque <= transparent:
        raise SystemExit("opaque_threshold_must_exceed_transparent_threshold")
    hard_tolerance = args.hard_tolerance or transparent

    entries: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    code_failures: list[str] = []
    prompt_hash = sha256(prompt_path)
    style_anchor_hash = sha256(style_anchor)
    identity_template_hash = sha256(identity_template)
    crop_root = round_root / "crops"
    extracted_root = round_root / "extracted"
    crop_root.mkdir()
    extracted_root.mkdir()

    for slot, box in zip(slots, layout["boxes"]):
        filename = f"{slot['itemId']}-{slot['kind']}.png"
        crop = crop_box(image, box)
        crop_path = crop_root / filename
        crop.save(crop_path)
        if args.method == "soft-chroma":
            extracted = soft_chroma(crop, key, transparent, opaque, args.despill)
        elif args.method == "hard-key":
            extracted = hard_key(crop, key, hard_tolerance)
        else:
            extracted = rembg_extract(crop)
        variant = spec["variants"][slot["kind"]]
        asset = trim_and_fit(extracted, int(variant["width"]), int(variant["height"]), int(variant["padding"]))
        asset = remove_tiny_components(asset)
        asset_path = extracted_root / filename
        asset.save(asset_path)
        item_metrics = {
            "item": slot["item"],
            "itemId": slot["itemId"],
            "kind": slot["kind"],
            "file": record_path(asset_path, output_root),
            **image_metrics(asset, key),
        }
        minimum_visible = 500 if max(asset.size) >= 256 else 35
        failures = []
        if item_metrics["visiblePixels"] <= minimum_visible:
            failures.append("empty_or_too_small")
        if item_metrics["outputEdgeTouchPixels"] != 0:
            failures.append("output_edge_contact")
        if item_metrics["tinyComponentCount"] != 0:
            failures.append("tiny_disconnected_component")
        if item_metrics["residualMatteRatioWithin48"] > 0.002:
            failures.append("matte_residue_or_subject_overlap")
        if item_metrics["residualMatteHueRatio"] > 0.002:
            failures.append("matte_hue_fringe_or_subject_overlap")
        item_metrics["codeFailures"] = failures
        item_metrics["codePass"] = not failures
        metrics.append(item_metrics)
        code_failures.extend(f"{filename}:{failure}" for failure in failures)
        entries.append({"path": str(asset_path), "label": f"{slot['item']} {slot['kind']}", "kind": slot["kind"]})
        provenance.append(
            {
                "item": slot["item"],
                "itemId": slot["itemId"],
                "kind": slot["kind"],
                "payload": slot["payload"],
                "source": record_path(source, output_root),
                "sourceSha256": source_hash,
                "prompt": record_path(prompt_path, output_root),
                "promptSha256": prompt_hash,
                "styleAnchor": record_path(style_anchor, output_root),
                "styleAnchorSha256": style_anchor_hash,
                "identityTemplate": record_path(identity_template, output_root),
                "identityTemplateSha256": identity_template_hash,
                "adaptiveBox": box,
                "crop": record_path(crop_path, output_root),
                "cropSha256": sha256(crop_path),
                "extractor": args.method,
                "requestedKeyRgb": list(key),
                "transparentThreshold": transparent if args.method == "soft-chroma" else None,
                "opaqueThreshold": opaque if args.method == "soft-chroma" else None,
                "hardTolerance": hard_tolerance if args.method == "hard-key" else None,
                "despill": bool(args.despill and supports_despill(key)),
                "tinyComponentCleanupThreshold": 10,
                "output": record_path(asset_path, output_root),
                "outputSha256": sha256(asset_path),
            }
        )

    write_json(round_root / "metrics.json", {"codePass": not code_failures, "failures": code_failures, "assets": metrics})
    write_json(
        round_root / "provenance.json",
        {
            "schemaVersion": 1,
            "createdAt": now(),
            "family": family["name"],
            "familyId": family["id"],
            "mode": args.mode,
            "round": args.round,
            "source": record_path(source, output_root),
            "sourceSha256": source_hash,
            "prompt": record_path(prompt_path, output_root),
            "promptSha256": prompt_hash,
            "styleAnchor": record_path(style_anchor, output_root),
            "styleAnchorSha256": style_anchor_hash,
            "identityTemplate": record_path(identity_template, output_root),
            "identityTemplateSha256": identity_template_hash,
            "matteProfile": profile,
            "splitting": layout,
            "assets": provenance,
        },
    )
    for background in ("checker", "white", "purple", "black"):
        make_board(entries, validation_root / f"attempt-{background}.png", background)
    if any(entry["kind"] == "small" for entry in entries):
        make_raw_small_board(entries, validation_root / "attempt-small-raw-64.png")

    history.append(
        {
            "round": args.round,
            "mode": args.mode,
            "repairItems": repair_items or [],
            "sourceSha256": source_hash,
            "method": args.method,
            "limitOverride": bool(args.override_limit),
            "code": "approved" if not code_failures else "rejected",
            "createdAt": now(),
        }
    )
    previous_assets = list(previous.get("assets", []))
    if code_failures:
        selected_assets = previous_assets
    elif args.mode == "paired" and not repair_items:
        selected_assets = provenance
    else:
        replacements = {(asset["itemId"], asset["kind"]): asset for asset in provenance}
        selected_assets = [
            replacements.pop((asset["itemId"], asset["kind"]), asset)
            for asset in previous_assets
        ]
        selected_assets.extend(replacements.values())
        slot_order = {
            (slot["itemId"], slot["kind"]): index
            for index, slot in enumerate(slots_for_family(family, "paired"))
        }
        selected_assets.sort(key=lambda asset: slot_order[(asset["itemId"], asset["kind"])])
    expected_family_assets = len(family["items"]) * 2
    family_complete = len(selected_assets) == expected_family_assets
    if code_failures:
        family_code = previous.get("validation", {}).get("code", "rejected") if selected_assets else "rejected"
        family_status = previous.get("status", "code-rejected") if selected_assets else "code-rejected"
        codex_status = previous.get("validation", {}).get("codex", "pending")
        human_status = previous.get("validation", {}).get("human", "pending")
    else:
        family_code = "approved" if family_complete else "incomplete"
        family_status = "awaiting-codex-review" if family_complete else "incomplete"
        codex_status = "pending"
        human_status = "pending"
    if not code_failures:
        selected_entries = []
        for asset in selected_assets:
            path = Path(asset["output"])
            if not path.is_absolute():
                path = output_root / path
            selected_entries.append(
                {
                    "path": str(path),
                    "label": f"{asset['item']} {asset['kind']}",
                    "kind": asset["kind"],
                }
            )
        for background in ("checker", "white", "purple", "black"):
            make_board(selected_entries, validation_root / f"review-{background}.png", background)
        if any(entry["kind"] == "small" for entry in selected_entries):
            make_raw_small_board(selected_entries, validation_root / "small-raw-64.png")
    current_source = {
        "path": record_path(source, output_root),
        "sha256": source_hash,
        "mode": args.mode,
        "repairItems": repair_items or [],
        "matte": color_hex(key),
        "preflight": profile,
        "prompt": record_path(prompt_path, output_root),
        "promptSha256": prompt_hash,
        "styleAnchor": record_path(style_anchor, output_root),
        "styleAnchorSha256": style_anchor_hash,
        "identityTemplate": record_path(identity_template, output_root),
        "identityTemplateSha256": identity_template_hash,
    }
    current_extraction = {
        "method": args.method,
        "despill": bool(args.despill),
        "transparentThreshold": transparent if args.method == "soft-chroma" else None,
        "opaqueThreshold": opaque if args.method == "soft-chroma" else None,
        "hardTolerance": hard_tolerance if args.method == "hard-key" else None,
    }
    selected_source = previous.get("source", current_source) if code_failures and selected_assets else current_source
    selected_extraction = previous.get("extraction", current_extraction) if code_failures and selected_assets else current_extraction
    status = {
        "schemaVersion": 1,
        "family": family["name"],
        "familyId": family["id"],
        "status": family_status,
        "selectedRound": args.round if not code_failures else previous.get("selectedRound"),
        "source": selected_source,
        "extraction": selected_extraction,
        "lastAttempt": {
            "round": args.round,
            "mode": args.mode,
            "repairItems": repair_items or [],
            "limitOverride": bool(args.override_limit),
            "code": "approved" if not code_failures else "rejected",
            "failures": code_failures,
            "source": current_source,
            "extraction": current_extraction,
        },
        "validation": {
            "code": family_code,
            "codex": codex_status,
            "human": human_status,
            "codeFailures": previous.get("validation", {}).get("codeFailures", []) if code_failures and selected_assets else code_failures,
        },
        "expectedAssetCount": expected_family_assets,
        "selectedAssetCount": len(selected_assets),
        "assets": selected_assets,
        "roundHistory": history,
        "reviewHistory": list(previous.get("reviewHistory", [])),
        "updatedAt": now(),
    }
    previous_approved = previous.get("approvedAssets") or previous.get("lastApprovedAssets")
    if code_failures and previous.get("approvedAssets"):
        status["approvedAssets"] = previous["approvedAssets"]
    elif previous_approved:
        status["lastApprovedAssets"] = previous_approved
    write_json(status_path, status)
    print(f"family_status:{status_path}")
    print(f"round_code_gate:{'approved' if not code_failures else 'rejected'}")
    print(f"family_code_gate:{status['validation']['code']}")
    print(f"assets:{len(provenance)}")
    if code_failures:
        raise SystemExit("code_gate_failed")


if __name__ == "__main__":
    main()
