#!/usr/bin/env python3
"""Shared helpers for the PlayDrop 2D asset-pack scripts."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


MODES = ("paired", "large", "small")
DEFAULT_RETRY_LIMITS = {
    "fullSheetsPerFamilyMaximum": 2,
    "individualRepairsPerAssetMaximum": 2,
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SystemExit(f"file_not_found:{path}") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"invalid_json:{path}:{error}") from error
    if not isinstance(value, dict):
        raise SystemExit(f"json_object_required:{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = f"{json.dumps(value, indent=2)}\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


@contextmanager
def exclusive_file_lock(
    path: Path,
    timeout_seconds: float = 10.0,
    stale_seconds: float = 60.0,
) -> Iterator[None]:
    """Use a short-lived lock file for cross-process state and ledger writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
        except FileExistsError:
            try:
                stale = time.time() - path.stat().st_mtime > stale_seconds
            except FileNotFoundError:
                continue
            if stale:
                path.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                raise SystemExit(f"file_lock_timeout:{path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(descriptor)
        path.unlink(missing_ok=True)


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    with exclusive_file_lock(path.with_suffix(f"{path.suffix}.lock")):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{json.dumps(value, separators=(',', ':'))}\n")
            handle.flush()
            os.fsync(handle.fileno())


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not normalized:
        raise SystemExit(f"invalid_slug_source:{value}")
    return normalized


def validate_spec(spec: dict[str, Any]) -> None:
    if spec.get("schemaVersion") != 1:
        raise SystemExit("unsupported_pack_spec_version")
    for key in ("pack", "styleAnchor", "variants", "families"):
        if key not in spec:
            raise SystemExit(f"pack_spec_missing:{key}")
    style_anchor = spec["styleAnchor"]
    if not isinstance(style_anchor, dict):
        raise SystemExit("pack_spec_style_anchor_object_required")
    if not str(style_anchor.get("stylePrompt", "")).strip():
        raise SystemExit("pack_spec_style_prompt_required")
    if style_anchor.get("path") is not None and not str(style_anchor.get("path", "")).strip():
        raise SystemExit("pack_spec_style_anchor_path_invalid")
    variants = spec["variants"]
    for kind in ("large", "small"):
        variant = variants.get(kind)
        if not isinstance(variant, dict):
            raise SystemExit(f"pack_spec_variant_missing:{kind}")
        for field in ("width", "height", "padding", "contract"):
            if field not in variant:
                raise SystemExit(f"pack_spec_variant_field_missing:{kind}:{field}")
    families = spec["families"]
    if not isinstance(families, list) or not families:
        raise SystemExit("pack_spec_families_required")
    family_ids: set[str] = set()
    for family in families:
        family_id = family.get("id")
        if not isinstance(family_id, str) or not family_id:
            raise SystemExit("pack_spec_family_id_required")
        if family_id in family_ids:
            raise SystemExit(f"pack_spec_duplicate_family:{family_id}")
        family_ids.add(family_id)
        items = family.get("items")
        if not isinstance(items, list) or not items:
            raise SystemExit(f"pack_spec_family_items_required:{family_id}")
        item_ids: set[str] = set()
        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise SystemExit(f"pack_spec_item_id_required:{family_id}")
            if item_id in item_ids:
                raise SystemExit(f"pack_spec_duplicate_item:{family_id}:{item_id}")
            item_ids.add(item_id)
            payloads = item.get("payloads")
            if not isinstance(payloads, dict):
                raise SystemExit(f"pack_spec_payloads_required:{family_id}:{item_id}")
            for kind in ("large", "small"):
                if not str(payloads.get(kind, "")).strip():
                    raise SystemExit(f"pack_spec_payload_required:{family_id}:{item_id}:{kind}")
    retry_limits = spec.get("retryLimits", {})
    if not isinstance(retry_limits, dict):
        raise SystemExit("pack_spec_retry_limits_object_required")
    for key, default in DEFAULT_RETRY_LIMITS.items():
        value = retry_limits.get(key, default)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise SystemExit(f"pack_spec_retry_limit_invalid:{key}")


def load_spec(path: Path) -> dict[str, Any]:
    spec = read_json(path)
    validate_spec(spec)
    return spec


def find_family(spec: dict[str, Any], family_id: str) -> dict[str, Any]:
    for family in spec["families"]:
        if family.get("id") == family_id:
            return family
    raise SystemExit(f"family_not_found:{family_id}")


def parse_item_ids(value: str | None) -> list[str] | None:
    if not value:
        return None
    item_ids = [item.strip() for item in value.split(",") if item.strip()]
    if not item_ids:
        raise SystemExit("items_required")
    if len(item_ids) != len(set(item_ids)):
        raise SystemExit("duplicate_repair_item")
    return item_ids


def retry_limits(spec: dict[str, Any]) -> dict[str, int]:
    configured = spec.get("retryLimits", {})
    return {
        key: int(configured.get(key, default))
        for key, default in DEFAULT_RETRY_LIMITS.items()
    }


def normalize_payload_overrides(value: Any) -> dict[str, dict[str, str]]:
    if value in (None, {}):
        return {}
    if not isinstance(value, dict):
        raise SystemExit("payload_overrides_must_be_object")
    normalized: dict[str, dict[str, str]] = {}
    for item_id, variants in value.items():
        if not isinstance(item_id, str) or not item_id.strip() or not isinstance(variants, dict):
            raise SystemExit("payload_override_item_invalid")
        normalized_variants: dict[str, str] = {}
        for kind, payload in variants.items():
            if kind not in {"large", "small"}:
                raise SystemExit(f"payload_override_kind_invalid:{item_id}:{kind}")
            if not isinstance(payload, str) or not payload.strip():
                raise SystemExit(f"payload_override_text_required:{item_id}:{kind}")
            normalized_variants[kind] = payload.strip()
        if not normalized_variants:
            raise SystemExit(f"payload_override_variants_required:{item_id}")
        normalized[item_id.strip()] = normalized_variants
    return normalized


def slots_for_family(
    family: dict[str, Any],
    mode: str,
    item_ids: list[str] | None = None,
    payload_overrides: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    if mode not in MODES:
        raise SystemExit(f"unsupported_mode:{mode}")
    requested = set(item_ids or [])
    known = {item["id"] for item in family["items"]}
    missing = sorted(requested - known)
    if missing:
        raise SystemExit(f"family_items_not_found:{','.join(missing)}")
    overrides = normalize_payload_overrides(payload_overrides)
    missing_overrides = sorted(set(overrides) - known)
    if missing_overrides:
        raise SystemExit(f"payload_override_items_not_found:{','.join(missing_overrides)}")
    if requested:
        outside_request = sorted(set(overrides) - requested)
        if outside_request:
            raise SystemExit(f"payload_override_outside_request:{','.join(outside_request)}")
    allowed_kinds = {"large", "small"} if mode == "paired" else {mode}
    for override_item, variants in overrides.items():
        invalid_kinds = sorted(set(variants) - allowed_kinds)
        if invalid_kinds:
            raise SystemExit(
                f"payload_override_outside_mode:{override_item}:{','.join(invalid_kinds)}"
            )
    slots: list[dict[str, Any]] = []
    for item in family["items"]:
        if requested and item["id"] not in requested:
            continue
        kinds = ("large", "small") if mode == "paired" else (mode,)
        for kind in kinds:
            original_payload = item["payloads"][kind]
            override_payload = overrides.get(item["id"], {}).get(kind)
            slots.append(
                {
                    "item": item["name"],
                    "itemId": item["id"],
                    "kind": kind,
                    "payload": override_payload or original_payload,
                    "originalPayload": original_payload if override_payload else None,
                    "payloadOverride": bool(override_payload),
                    "referenceType": "semantic-only" if override_payload else item.get("referenceType", "semantic-only"),
                    "reference": None if override_payload else (item.get("references") or {}).get(kind),
                }
            )
    if len(slots) > 16:
        raise SystemExit(f"sheet_slot_limit_exceeded:{len(slots)}")
    return slots


def grid_for_slots(count: int, requested_columns: int | None = None) -> tuple[int, int]:
    if count < 1:
        raise SystemExit("sheet_requires_slots")
    columns = requested_columns or min(4, count)
    if columns < 1 or columns > 8:
        raise SystemExit(f"invalid_column_count:{columns}")
    return math.ceil(count / columns), columns


def resolve_input_path(spec_path: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else (spec_path.parent / path).resolve()


def parse_hex_color(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", value.strip())
    if not match:
        raise SystemExit(f"invalid_hex_color:{value}")
    raw = match.group(1)
    return tuple(int(raw[index:index + 2], 16) for index in (0, 2, 4))


def color_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in rgb)
