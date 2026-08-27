#!/usr/bin/env python3
"""Shared image-processing helpers for the canonical family workflow."""

from __future__ import annotations

import math
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from asset_pack_common import color_hex


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
    if not entries:
        raise SystemExit("review_board_assets_required")
    loaded = [(entry, Image.open(entry["path"]).convert("RGBA")) for entry in entries]
    columns = 4
    content_width = max(asset.width for _, asset in loaded)
    content_height = max(asset.height for _, asset in loaded)
    tile_width = max(300, content_width + 48)
    tile_height = max(330, content_height + 66)
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
    font = board_font()
    for index, (entry, asset) in enumerate(loaded):
        x, y = (index % columns) * tile_width, (index // columns) * tile_height
        board.alpha_composite(
            asset,
            (x + (tile_width - asset.width) // 2, y + 42 + (content_height - asset.height) // 2),
        )
        draw.text((x + 12, y + 12), entry["label"], fill=text, font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    board.convert("RGB").save(output)
