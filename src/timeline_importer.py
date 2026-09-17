"""Bounded-memory JSONL importer for Global-History-engine timeline events.

The importer processes one JSON object per line, validates it, and emits valid
records incrementally. It intentionally does not retain imported events.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO
from urllib.parse import urlparse

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DATE_RE = re.compile(r"^(?:\d{4}|\d{4}-\d{2}|\d{4}-\d{2}-\d{2})(?:T.*)?$")
_PRECISIONS = {"day", "month", "year", "unknown"}
_MEDIA_TYPES = {"image", "video", "audio", "document"}


@dataclass(frozen=True)
class ImportConfig:
    """Runtime limits and error-handling policy for an import."""

    strict: bool = False
    max_line_bytes: int = 1_048_576
    batch_size: int = 500
    duplicate_policy: str = "reject"
    on_error: str = "continue"

    def __post_init__(self) -> None:
        if self.max_line_bytes <= 0 or self.batch_size <= 0:
            raise ValueError("max_line_bytes and batch_size must be positive")
        if self.duplicate_policy not in {"reject", "replace"}:
            raise ValueError("duplicate_policy must be 'reject' or 'replace'")
        if self.on_error not in {"continue", "raise"}:
            raise ValueError("on_error must be 'continue' or 'raise'")


@dataclass
class ImportSummary:
    input_file: str
    records_read: int = 0
    records_imported: int = 0
    records_rejected: int = 0
    duplicate_ids: int = 0
    duration_seconds: float = 0.0
    peak_memory_mb: float | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TimelineValidationError(ValueError):
    """A timeline record does not satisfy the import contract."""


def _require_string(record: dict[str, Any], field_name: str, *, maximum: int) -> None:
    value = record.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise TimelineValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise TimelineValidationError(f"{field_name} exceeds {maximum} characters")


def _validate_url(value: Any, field_name: str) -> None:
    if not isinstance(value, str):
        raise TimelineValidationError(f"{field_name} must be a URL string")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TimelineValidationError(f"{field_name} must be an http(s) URL")


def _validate_date(value: Any) -> None:
    if not isinstance(value, str) or not _DATE_RE.fullmatch(value):
        raise TimelineValidationError("date must be YYYY, YYYY-MM, YYYY-MM-DD, or an ISO datetime")
    try:
        if len(value) == 4:
            date(int(value), 1, 1)
        elif len(value) == 7:
            date.fromisoformat(value + "-01")
        elif "T" not in value:
            date.fromisoformat(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TimelineValidationError(f"invalid date: {value}") from exc


def _validate_string_list(record: dict[str, Any], field_name: str, maximum: int) -> None:
    value = record.get(field_name, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise TimelineValidationError(f"{field_name} must be an array of non-empty strings")
    if any(len(item) > maximum for item in value):
        raise TimelineValidationError(f"items in {field_name} exceed {maximum} characters")
    if len(value) != len(set(value)):
        raise TimelineValidationError(f"{field_name} must not contain duplicates")


def _validate_source(source: Any, index: int) -> None:
    if not isinstance(source, dict):
        raise TimelineValidationError(f"sources[{index}] must be an object")
    allowed = {"title", "url", "publisher", "published_at", "accessed_at"}
    unknown = set(source) - allowed
    if unknown:
        raise TimelineValidationError(f"sources[{index}] contains unknown fields: {sorted(unknown)}")
    _require_string(source, "title", maximum=300)
    _validate_url(source.get("url"), f"sources[{index}].url")
    for key in ("published_at", "accessed_at"):
        if key in source:
            try:
                date.fromisoformat(source[key])
            except (TypeError, ValueError) as exc:
                raise TimelineValidationError(f"sources[{index}].{key} must be YYYY-MM-DD") from exc
    if "publisher" in source:
        _require_string(source, "publisher", maximum=200)


def _validate_location(location: Any) -> None:
    if not isinstance(location, dict) or not location:
        raise TimelineValidationError("location must be a non-empty object")
    allowed = {"name", "country_code", "latitude", "longitude"}
    unknown = set(location) - allowed
    if unknown:
        raise TimelineValidationError(f"location contains unknown fields: {sorted(unknown)}")
    if "name" in location and (not isinstance(location["name"], str) or len(location["name"]) > 300):
        raise TimelineValidationError("location.name must be a string of at most 300 characters")
    if "country_code" in location and (
        not isinstance(location["country_code"], str) or not re.fullmatch(r"[A-Z]{2}", location["country_code"])
    ):
        raise TimelineValidationError("location.country_code must be a two-letter uppercase code")
    for key, low, high in (("latitude", -90, 90), ("longitude", -180, 180)):
        if key in location and (not isinstance(location[key], (int, float)) or not low <= location[key] <= high):
            raise TimelineValidationError(f"location.{key} is out of range")


def _validate_media(media: Any, index: int) -> None:
    if not isinstance(media, dict):
        raise TimelineValidationError(f"media[{index}] must be an object")
    if set(media) - {"type", "url", "alt", "credit", "license"}:
        raise TimelineValidationError(f"media[{index}] contains unknown fields")
    if media.get("type") not in _MEDIA_TYPES:
        raise TimelineValidationError(f"media[{index}].type is invalid")
    _validate_url(media.get("url"), f"media[{index}].url")
    for key, maximum in (("alt", 500), ("credit", 300), ("license", 200)):
        if key in media and (not isinstance(media[key], str) or len(media[key]) > maximum):
            raise TimelineValidationError(f"media[{index}].{key} is invalid")


def validate_event(record: Any) -> dict[str, Any]:
    """Validate and return a normalized event without mutating the input."""
    if not isinstance(record, dict):
        raise TimelineValidationError("record must be a JSON object")
    allowed = {
        "id", "date", "date_precision", "title", "description", "sources", "updated_at",
        "location", "people", "organizations", "tags", "media", "metadata",
    }
    unknown = set(record) - allowed
    if unknown:
        raise TimelineValidationError(f"unknown fields: {sorted(unknown)}")
    _require_string(record, "id", maximum=200)
    if not _ID_RE.fullmatch(record["id"]):
        raise TimelineValidationError("id contains unsupported characters")
    _validate_date(record.get("date"))
    if record.get("date_precision", "day") not in _PRECISIONS:
        raise TimelineValidationError("date_precision is invalid")
    _require_string(record, "title", maximum=300)
    _require_string(record, "description", maximum=10_000)
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        raise TimelineValidationError("sources must contain at least one source")
    for index, source in enumerate(sources):
        _validate_source(source, index)
    if "updated_at" in record:
        try:
            datetime.fromisoformat(record["updated_at"].replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as exc:
            raise TimelineValidationError("updated_at must be an ISO datetime") from exc
    for field_name in ("people", "organizations", "tags"):
        _validate_string_list(record, field_name, 200 if field_name != "tags" else 100)
    if "location" in record:
        _validate_location(record["location"])
    if "media" in record:
        if not isinstance(record["media"], list):
            raise TimelineValidationError("media must be an array")
        for index, media in enumerate(record["media"]):
            _validate_media(media, index)
    if "metadata" in record and not isinstance(record["metadata"], dict):
        raise TimelineValidationError("metadata must be an object")
    normalized = dict(record)
    normalized.setdefault("date_precision", "day")
    for field_name in ("people", "organizations", "tags", "media"):
        normalized.setdefault(field_name, [])
    return normalized


def _iter_lines(source: TextIO, max_line_bytes: int) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(source, 1):
        if len(line.encode("utf-8")) > max_line_bytes:
            raise TimelineValidationError(f"line exceeds max_line_bytes ({max_line_bytes})")
        yield line_number, line


def import_jsonl(
    input_file: str | Path | TextIO,
    *,
    output_file: str | Path | TextIO | None = None,
    reject_file: str | Path | TextIO | None = None,
    config: ImportConfig | None = None,
    on_batch: Callable[[list[dict[str, Any]]], None] | None = None,
) -> ImportSummary:
    """Stream-import JSONL records, emitting batches and never retaining events."""
    config = config or ImportConfig()
    summary = ImportSummary(input_file=str(input_file) if not hasattr(input_file, "read") else "<stream>")
    seen_ids: set[str] = set()
    close_input = close_output = close_reject = False
    source = input_file if hasattr(input_file, "read") else open(input_file, "r", encoding="utf-8")
    close_input = not hasattr(input_file, "read")
    destination = None if output_file is None else (output_file if hasattr(output_file, "write") else open(output_file, "w", encoding="utf-8"))
    close_output = destination is not None and not hasattr(output_file, "write")
    rejects = None if reject_file is None else (reject_file if hasattr(reject_file, "write") else open(reject_file, "w", encoding="utf-8"))
    close_reject = rejects is not None and not hasattr(reject_file, "write")
    batch: list[dict[str, Any]] = []
    try:
        for line_number, line in _iter_lines(source, config.max_line_bytes):
            if not line.strip():
                continue
            summary.records_read += 1
            try:
                record = json.loads(line)
                event = validate_event(record)
                event_id = event["id"]
                if event_id in seen_ids and config.duplicate_policy == "reject":
                    summary.duplicate_ids += 1
                    raise TimelineValidationError(f"duplicate id: {event_id}")
                seen_ids.add(event_id)
                batch.append(event)
                if len(batch) >= config.batch_size:
                    _emit_batch(batch, destination, on_batch)
                    summary.records_imported += len(batch)
                    batch.clear()
            except (json.JSONDecodeError, TimelineValidationError, UnicodeError) as exc:
                summary.records_rejected += 1
                error = {"line": line_number, "error": str(exc)}
                summary.errors.append(error)
                if rejects is not None:
                    rejects.write(json.dumps({"line": line_number, "error": str(exc), "record": line.rstrip("\n")}) + "\n")
                if config.strict or config.on_error == "raise":
                    raise
        if batch:
            _emit_batch(batch, destination, on_batch)
            summary.records_imported += len(batch)
            batch.clear()
    finally:
        if close_input:
            source.close()
        if close_output and destination is not None:
            destination.close()
        if close_reject and rejects is not None:
            rejects.close()
    return summary


def _emit_batch(batch: list[dict[str, Any]], destination: TextIO | None, on_batch: Callable[[list[dict[str, Any]]], None] | None) -> None:
    if destination is not None:
        for event in batch:
            destination.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        destination.flush()
    if on_batch is not None:
        on_batch(batch)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stream-validate and import timeline JSONL data")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rejects", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--max-line-bytes", type=int, default=1_048_576)
    args = parser.parse_args(argv)
    try:
        summary = import_jsonl(args.input, output_file=args.output, reject_file=args.rejects, config=ImportConfig(strict=args.strict, batch_size=args.batch_size, max_line_bytes=args.max_line_bytes))
    except (OSError, TimelineValidationError, json.JSONDecodeError) as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
