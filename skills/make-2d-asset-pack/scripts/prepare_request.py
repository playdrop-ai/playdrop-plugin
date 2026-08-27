#!/usr/bin/env python3
"""Normalize a sheet or pack request into portable specs and family jobs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from asset_pack_common import (
    DEFAULT_RETRY_LIMITS,
    append_jsonl,
    now,
    parse_hex_color,
    read_json,
    slug,
    write_json,
)


DEFAULT_MATTE = "#ff00ff"
DEFAULT_FALLBACK_MATTES = ["#00ff00", "#00ffff", "#0000ff", "#ffffff", "#000000"]
MATTE_CANDIDATES = ["#00ff00", "#ff00ff", "#00ffff", "#0000ff", "#ff0000", "#ffff00", "#8000ff", "#ffffff", "#000000"]
OWNERSHIP = {"creator-owned", "licensed", "unknown"}
REQUEST_KINDS = {"sheet", "pack"}
LICENSES = {"CLOSED", "PLAYDROP", "MIT", "CC0"}


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"request_text_required:{label}")
    return value.strip()


def resolve_request_path(request_path: Path, source_folder: Path | None, value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    request_relative = (request_path.parent / candidate).resolve()
    if request_relative.exists() or source_folder is None:
        return request_relative
    return (source_folder / candidate).resolve()


def copy_input(source: Path, destination: Path) -> str:
    if not source.is_file():
        raise SystemExit(f"request_input_not_found:{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def source_index(source_folder: Path | None) -> dict[str, Path]:
    if source_folder is None:
        return {}
    if not source_folder.is_dir():
        raise SystemExit(f"request_source_folder_not_found:{source_folder}")
    index: dict[str, Path] = {}
    for path in sorted(source_folder.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        key = "".join(character for character in path.stem.lower() if character.isalnum())
        index.setdefault(key, path)
    return index


def reference_candidates(item_id: str, item_name: str) -> list[str]:
    bases = {item_id, slug(item_name)}
    return [
        "".join(character for character in base.lower() if character.isalnum())
        for base in bases
    ]


def normalize_output(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"request_output_object_required:{label}")
    output = dict(value)
    for field in ("width", "height", "padding"):
        number = output.get(field)
        if not isinstance(number, int) or isinstance(number, bool):
            raise SystemExit(f"request_output_integer_required:{label}:{field}")
    if output["width"] < 16 or output["height"] < 16 or output["padding"] < 0:
        raise SystemExit(f"request_output_invalid:{label}")
    if output["padding"] * 2 >= min(output["width"], output["height"]):
        raise SystemExit(f"request_output_padding_invalid:{label}")
    output["contract"] = require_text(output.get("contract"), f"{label}.contract")
    return output


def normalize_item(
    raw: Any,
    family_id: str,
    request_path: Path,
    source_folder: Path | None,
    indexed_sources: dict[str, Path],
    output_root: Path,
    default_output: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(raw, str):
        name = require_text(raw, f"families.{family_id}.items")
        item: dict[str, Any] = {"name": name}
    elif isinstance(raw, dict):
        item = dict(raw)
        name = require_text(item.get("name"), f"families.{family_id}.items.name")
    else:
        raise SystemExit(f"request_item_invalid:{family_id}")
    item_id = str(item.get("id") or slug(name))
    if slug(item_id) != item_id:
        raise SystemExit(f"request_item_id_invalid:{family_id}:{item_id}")
    description = str(item.get("description") or name).strip()
    payload = str(item.get("payload") or (
        f"One complete {description} as a polished casual game asset with a readable silhouette; "
        "no text, floor, loose props, clipping, or exterior shadow."
    )).strip()
    source: Path | None = None
    if item.get("reference"):
        source = resolve_request_path(request_path, source_folder, str(item["reference"]))
    else:
        for candidate in reference_candidates(item_id, name):
            if candidate in indexed_sources:
                source = indexed_sources[candidate]
                break
    portable_reference: str | None = None
    if source:
        extension = source.suffix.lower() or ".png"
        destination = output_root / "private-reference-inputs" / family_id / f"{item_id}{extension}"
        copy_input(source, destination)
        portable_reference = str(destination.relative_to(output_root))
    output = normalize_output(item.get("output") or default_output, f"families.{family_id}.items.{item_id}.output")
    return {
        "id": item_id,
        "name": name,
        "description": description,
        "referenceType": "visual-reference" if portable_reference else "semantic-only",
        **({"reference": portable_reference} if portable_reference else {}),
        "payload": payload,
        "output": output,
    }


def validate_request(request: dict[str, Any]) -> None:
    if request.get("schemaVersion") != 1:
        raise SystemExit("unsupported_request_version")
    kind = request.get("kind")
    if kind not in REQUEST_KINDS:
        raise SystemExit(f"request_kind_invalid:{kind}")
    for key in ("id", "name", "description"):
        require_text(request.get(key), key)
    if slug(str(request["id"])) != request["id"]:
        raise SystemExit(f"request_id_invalid:{request['id']}")
    style = request.get("style")
    if not isinstance(style, dict):
        raise SystemExit("request_style_object_required")
    require_text(style.get("description"), "style.description")
    normalize_output(request.get("output"), "output")
    references = style.get("referenceImages", [])
    if not isinstance(references, list):
        raise SystemExit("request_style_references_array_required")
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            raise SystemExit(f"request_style_reference_object_required:{index}")
        require_text(reference.get("path"), f"style.referenceImages.{index}.path")
        if reference.get("ownership") not in OWNERSHIP:
            raise SystemExit(f"request_style_reference_ownership_invalid:{index}")
    families = request.get("families")
    if not isinstance(families, list) or not families:
        raise SystemExit("request_families_required")
    if kind == "sheet" and len(families) != 1:
        raise SystemExit("sheet_request_requires_one_family")
    seen: set[str] = set()
    for family in families:
        if not isinstance(family, dict):
            raise SystemExit("request_family_object_required")
        family_id = require_text(family.get("id"), "families.id")
        if slug(family_id) != family_id or family_id in seen:
            raise SystemExit(f"request_family_id_invalid_or_duplicate:{family_id}")
        seen.add(family_id)
        require_text(family.get("name"), f"families.{family_id}.name")
        items = family.get("items")
        if not isinstance(items, list) or not items:
            raise SystemExit(f"request_family_items_required:{family_id}")
        slot_count = len(items)
        if slot_count > 16:
            raise SystemExit(f"request_sheet_slot_limit_exceeded:{family_id}:{slot_count}")
        requested_matte = str(family.get("matte", "auto")).lower()
        if requested_matte != "auto":
            parse_hex_color(requested_matte)
        for matte in family.get("fallbackMattes", DEFAULT_FALLBACK_MATTES):
            parse_hex_color(str(matte))
        family_references = family.get("styleReferenceImages", [])
        if not isinstance(family_references, list):
            raise SystemExit(f"request_family_style_references_array_required:{family_id}")
        for index, reference in enumerate(family_references):
            if not isinstance(reference, dict):
                raise SystemExit(f"request_family_style_reference_object_required:{family_id}:{index}")
            require_text(reference.get("path"), f"families.{family_id}.styleReferenceImages.{index}.path")
            if reference.get("ownership") not in OWNERSHIP:
                raise SystemExit(f"request_family_style_reference_ownership_invalid:{family_id}:{index}")


def reference_pixels(items: list[dict[str, Any]], output_root: Path) -> np.ndarray:
    samples: list[np.ndarray] = []
    for item in items:
        value = item.get("reference")
        if not value:
            continue
        path = output_root / value
        image = Image.open(path).convert("RGBA")
        image.thumbnail((256, 256), Image.Resampling.LANCZOS)
        data = np.asarray(image)
        visible = data[:, :, 3] > 32
        if visible.any():
            samples.append(data[:, :, :3][visible].astype(np.float32))
    return np.concatenate(samples, axis=0) if samples else np.empty((0, 3), dtype=np.float32)


def matte_ranking(items: list[dict[str, Any]], output_root: Path) -> list[dict[str, Any]]:
    pixels = reference_pixels(items, output_root)
    if len(pixels) == 0:
        return [{"matte": matte, "conflictRatio": 0.0, "samplePixels": 0} for matte in MATTE_CANDIDATES]
    pixel_chroma = pixels - pixels.min(axis=1, keepdims=True)
    pixel_chroma_norm = np.linalg.norm(pixel_chroma, axis=1)
    saturation = pixels.max(axis=1) - pixels.min(axis=1)
    scores: list[dict[str, Any]] = []
    for order, matte in enumerate(MATTE_CANDIDATES):
        key = np.asarray(parse_hex_color(matte), dtype=np.float32)
        distance_match = np.linalg.norm(pixels - key, axis=1) <= 64.0
        key_chroma = key - key.min()
        key_norm = float(np.linalg.norm(key_chroma))
        hue_match = np.zeros(len(pixels), dtype=np.bool_)
        if key_norm > 1.0:
            similarity = np.divide(
                np.sum(pixel_chroma * key_chroma, axis=1),
                pixel_chroma_norm * key_norm,
                out=np.zeros_like(pixel_chroma_norm),
                where=pixel_chroma_norm > 1.0,
            )
            hue_match = (saturation >= 32.0) & (similarity >= 0.99)
        conflict = float(np.mean(distance_match | hue_match))
        scores.append(
            {
                "matte": matte,
                "conflictRatio": round(conflict, 7),
                "samplePixels": int(len(pixels)),
                "candidateOrder": order,
            }
        )
    return sorted(scores, key=lambda score: (score["conflictRatio"], score["candidateOrder"]))


def run_builder(script: Path, arguments: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"builder_failed:{script.name}:{result.stderr.strip() or result.stdout.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    request_path = args.request.resolve()
    output_root = args.output_root.resolve()
    request = read_json(request_path)
    validate_request(request)
    existing_request = output_root / "request.json"
    if existing_request.exists() and not args.resume:
        raise SystemExit(f"pack_request_already_prepared:{existing_request}")
    if existing_request.exists() and read_json(existing_request) != request:
        raise SystemExit("resume_request_hash_mismatch")
    if existing_request.exists() and args.resume:
        print(f"resumed:{output_root}")
        print("state_preserved:true")
        return
    output_root.mkdir(parents=True, exist_ok=True)

    source_folder_value = request.get("sourceFolder")
    source_folder = resolve_request_path(request_path, None, str(source_folder_value)) if source_folder_value else None
    indexed_sources = source_index(source_folder)
    style = request["style"]
    copied_style_references: list[str] = []
    style_ownership = "creator-owned"
    for index, reference in enumerate(style.get("referenceImages", []), start=1):
        source = resolve_request_path(request_path, source_folder, reference["path"])
        extension = source.suffix.lower() or ".png"
        destination = output_root / "style-anchor" / f"reference-{index}{extension}"
        copy_input(source, destination)
        copied_style_references.append(str(destination.relative_to(output_root)))
        if index == 1:
            style_ownership = reference["ownership"]

    metadata = dict(request.get("metadata") or {})
    version = str(metadata.get("version") or "1.0.0")
    license_name = str(metadata.get("license") or "PLAYDROP").upper()
    if license_name not in LICENSES:
        raise SystemExit(f"request_license_invalid:{license_name}")
    default_output = normalize_output(request.get("output"), "output")
    normalized_families: list[dict[str, Any]] = []
    family_configs: dict[str, dict[str, Any]] = {}
    for raw_family in request["families"]:
        family_id = raw_family["id"]
        columns = min(int(raw_family.get("columns") or 4), len(raw_family["items"]))
        continuity_style_references: list[dict[str, str]] = []
        for reference_index, reference in enumerate(raw_family.get("styleReferenceImages", []), start=1):
            source = resolve_request_path(request_path, source_folder, reference["path"])
            extension = source.suffix.lower() or ".png"
            destination = (
                output_root
                / "family-style-references"
                / family_id
                / f"reference-{reference_index}{extension}"
            )
            copy_input(source, destination)
            continuity_style_references.append(
                {
                    "path": str(destination.relative_to(output_root)),
                    "ownership": reference["ownership"],
                }
            )
        items = [
            normalize_item(item, family_id, request_path, source_folder, indexed_sources, output_root, default_output)
            for item in raw_family["items"]
        ]
        ranking = matte_ranking(items, output_root)
        requested_matte = str(raw_family.get("matte") or "auto").lower()
        matte = ranking[0]["matte"] if requested_matte == "auto" else requested_matte
        requested_fallbacks = raw_family.get("fallbackMattes")
        fallbacks = (
            [str(value).lower() for value in requested_fallbacks]
            if requested_fallbacks is not None
            else [score["matte"] for score in ranking if score["matte"] != matte][:4]
        )
        selected_score = next((score for score in ranking if score["matte"] == matte), None)
        matte_analysis = {
            "selection": "automatic" if requested_matte == "auto" else "explicit",
            "selected": matte,
            "selectedConflictRatio": selected_score["conflictRatio"] if selected_score else None,
            "requiresVisualReview": bool(selected_score and selected_score["conflictRatio"] > 0.002),
            "ranking": ranking,
        }
        normalized_families.append(
            {
                "id": family_id,
                "name": raw_family["name"],
                "description": str(raw_family.get("description") or raw_family["name"]),
                "production": {
                    "columns": columns,
                    "matte": matte,
                    "fallbackMattes": [value for value in fallbacks if value != matte],
                    "matteAnalysis": matte_analysis,
                },
                "continuityStyleReferences": continuity_style_references,
                "items": items,
            }
        )
        family_configs[family_id] = {
            "columns": columns,
            "matte": matte,
            "fallbackMattes": fallbacks,
            "matteAnalysis": matte_analysis,
            "continuityStyleReferences": [reference["path"] for reference in continuity_style_references],
        }

    spec = {
        "schemaVersion": 1,
        "pack": {
            "id": request["id"],
            "name": request["name"],
            "description": request["description"],
            "version": version,
            "license": license_name,
            "visibility": str(metadata.get("visibility") or "PRIVATE").upper(),
            "publicationRights": str(metadata.get("publicationRights") or "private-only"),
            "tags": list(metadata.get("tags") or []),
            "requestKind": request["kind"],
        },
        "styleAnchor": {
            **({"path": copied_style_references[0]} if copied_style_references else {}),
            "ownership": style_ownership,
            "stylePrompt": style["description"],
            "origin": "reference-image" if copied_style_references else "text-only",
            "additionalReferences": copied_style_references[1:],
        },
        "retryLimits": {**DEFAULT_RETRY_LIMITS, **dict(request.get("retryLimits") or {})},
        "families": normalized_families,
    }
    write_json(output_root / "request.json", request)
    write_json(output_root / "pack-spec.json", spec)

    scripts = Path(__file__).resolve().parent
    queued_at = now()
    for index, family in enumerate(normalized_families):
        family_id = family["id"]
        config = family_configs[family_id]
        job_style_references = [
            *copied_style_references,
            *config["continuityStyleReferences"],
        ]
        family_root = output_root / "families" / family_id
        template_dir = family_root / "private-templates" / "generation-v1"
        prompt_path = family_root / "prompts" / "generation-v1.txt"
        run_builder(
            scripts / "build_template.py",
            [
                "--spec", str(output_root / "pack-spec.json"),
                "--family", family_id,
                "--columns", str(config["columns"]),
                "--output-dir", str(template_dir),
            ],
        )
        template = template_dir / f"{family_id}-identity-template.png"
        run_builder(
            scripts / "build_prompt.py",
            [
                "--spec", str(output_root / "pack-spec.json"),
                "--family", family_id,
                "--columns", str(config["columns"]),
                "--matte", config["matte"],
                "--output", str(prompt_path),
            ],
        )
        bootstrap = not job_style_references and index == 0
        state = "ready" if job_style_references or bootstrap else "blocked-style-anchor"
        job = {
            "schemaVersion": 1,
            "jobId": "generation-v1",
            "type": "generation",
            "familyId": family_id,
            "items": [],
            "attempt": 1,
            "columns": config["columns"],
            "matte": config["matte"],
            "fallbackMattes": config["fallbackMattes"],
            "matteAnalysis": config["matteAnalysis"],
            "state": state,
            "bootstrapStyle": bootstrap,
            "prompt": str(prompt_path.relative_to(output_root)),
            "identityTemplate": str(template.relative_to(output_root)),
            "styleReferences": job_style_references,
            "output": str((family_root / "generated" / "generation-v1.png").relative_to(output_root)),
            "timing": {"queuedAt": queued_at},
            "errors": [],
        }
        job_path = family_root / "jobs" / "generation-v1.json"
        write_json(job_path, job)
        expected = len(family["items"])
        status = {
            "schemaVersion": 1,
            "family": family["name"],
            "familyId": family_id,
            "status": "queued-generation" if state == "ready" else "blocked-style-anchor",
            "selectedRound": None,
            "validation": {"code": "pending", "agent": "pending", "human": "pending", "codeFailures": []},
            "expectedAssetCount": expected,
            "selectedAssetCount": 0,
            "assets": [],
            "roundHistory": [],
            "reviewHistory": [],
            "pipeline": {
                "stage": "generation" if state == "ready" else "blocked-style-anchor",
                "activeJob": str(job_path.relative_to(output_root)),
                "timing": {"queuedAt": queued_at},
                "lastError": None,
            },
            "updatedAt": queued_at,
        }
        write_json(family_root / "family-status.json", status)
        append_jsonl(
            family_root / "events.jsonl",
            {"at": queued_at, "event": "job-prepared", "jobId": job["jobId"], "state": state},
        )

    write_json(
        output_root / "pack-status.json",
        {
            "schemaVersion": 1,
            "packId": request["id"],
            "kind": request["kind"],
            "status": "prepared",
            "familyCount": len(normalized_families),
            "concurrency": {"generation": 3, "extraction": 2},
            "timing": {"preparedAt": queued_at},
            "updatedAt": queued_at,
        },
    )
    print(f"prepared:{output_root}")
    print(f"kind:{request['kind']}")
    print(f"families:{len(normalized_families)}")
    ready_jobs = sum(
        1
        for index, family in enumerate(normalized_families)
        if index == 0 or copied_style_references or family["continuityStyleReferences"]
    )
    print(f"ready_jobs:{ready_jobs}")
    for family in normalized_families:
        analysis = family["production"]["matteAnalysis"]
        if analysis["requiresVisualReview"]:
            print(
                f"matte_review_required:{family['id']}:{analysis['selected']}:"
                f"{analysis['selectedConflictRatio']}"
            )


if __name__ == "__main__":
    main()
