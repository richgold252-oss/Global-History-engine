# Timeline Schema and JSONL Import Contract

This document defines the contributor-facing input contract for the Global-History-engine timeline importer. The canonical transport format is **JSON Lines (JSONL)**: each non-empty line contains one complete JSON object.[1] JSONL is used because records can be processed incrementally without loading an entire timeline into memory.

The importer is implemented in [`src/timeline_importer.py`](../src/timeline_importer.py). It validates each event, emits valid records in bounded batches, and writes malformed records to an optional reject file.

## Canonical event schema

Each timeline event must be a JSON object with these required fields:

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | string | Yes | 1–200 characters; starts with a letter or number; remaining characters may be letters, numbers, `.`, `_`, `:`, or `-` |
| `date` | string | Yes | `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or an ISO 8601 datetime |
| `title` | string | Yes | Non-empty; maximum 300 characters |
| `description` | string | Yes | Non-empty; maximum 10,000 characters |
| `sources` | array of objects | Yes | At least one source with a title and HTTP(S) URL |

The following fields are optional:

| Field | Type | Constraints |
|---|---|---|
| `date_precision` | string | `day`, `month`, `year`, or `unknown`; defaults to `day` |
| `updated_at` | string | ISO 8601 datetime |
| `location` | object | May contain `name`, `country_code`, `latitude`, and `longitude` |
| `people` | array of strings | No duplicate values; each value is non-empty and at most 200 characters |
| `organizations` | array of strings | No duplicate values; each value is non-empty and at most 200 characters |
| `tags` | array of strings | No duplicate values; each value is non-empty and at most 100 characters |
| `media` | array of objects | Each object has a supported type and HTTP(S) URL |
| `metadata` | object | Application-specific values are allowed |

Unknown top-level fields are rejected. Optional string arrays default to empty arrays in the normalized output.

### Source objects

Every source must contain `title` and `url`. A source may also contain `publisher`, `published_at`, and `accessed_at`.

```json
{
  "title": "United States Holocaust Memorial Museum",
  "url": "https://encyclopedia.ushmm.org/content/en/article/invasion-of-poland",
  "publisher": "USHMM",
  "accessed_at": "2026-09-17"
}
```

The source URL must use `http` or `https`. Date fields in a source use `YYYY-MM-DD`.

### Location objects

A location may include a display name, an ISO-style two-letter uppercase country code, and coordinates. Latitude must be between `-90` and `90`; longitude must be between `-180` and `180`.

```json
{
  "name": "Warsaw, Poland",
  "country_code": "PL",
  "latitude": 52.2297,
  "longitude": 21.0122
}
```

### Media objects

Media supports four types: `image`, `video`, `audio`, and `document`. Every media object requires `type` and an HTTP(S) `url`. Optional accessibility and attribution fields are `alt`, `credit`, and `license`.

```json
{
  "type": "image",
  "url": "https://example.org/images/event.jpg",
  "alt": "A historical map of Poland",
  "credit": "Example Archive",
  "license": "CC BY 4.0"
}
```

## JSONL example

The following is a valid two-record JSONL file. There must be one complete JSON object per physical line.

```jsonl
{"id":"ww2-1939-invasion-poland","date":"1939-09-01","date_precision":"day","title":"Germany invades Poland","description":"Germany invaded Poland, marking the beginning of the European theatre of the Second World War.","sources":[{"title":"United States Holocaust Memorial Museum","url":"https://encyclopedia.ushmm.org/content/en/article/invasion-of-poland","accessed_at":"2026-09-17"}],"location":{"name":"Poland","country_code":"PL"},"people":["Adolf Hitler"],"organizations":["Nazi Germany","Second Polish Republic"],"tags":["World War II","Europe","military history"],"media":[],"metadata":{"era":"20th century","confidence":"high"}}
{"id":"apollo-11-moon-landing","date":"1969-07-20","date_precision":"day","title":"Apollo 11 lands on the Moon","description":"Apollo 11 became the first crewed mission to land on the Moon.","sources":[{"title":"NASA","url":"https://www.nasa.gov/mission/apollo-11/","accessed_at":"2026-09-17"}],"people":["Neil Armstrong","Buzz Aldrin","Michael Collins"],"organizations":["NASA"],"tags":["space exploration","20th century"],"media":[]}
```

## Import behavior

The importer reads the input line by line. It does not retain the imported event list. Valid records are accumulated only up to the configured `batch_size`, then written to the output stream and passed to the optional batch callback.

The default configuration is:

```text
strict=false
max_line_bytes=1048576
batch_size=500
duplicate_policy=reject
on_error=continue
```

The importer counts non-empty input lines as records. Blank lines are ignored. Each record is parsed and validated independently.

### Invalid records and rejects

By default, processing continues after malformed JSON, schema violations, oversized lines, and duplicate IDs. If a reject file is supplied, each rejected record is written as JSON containing:

```json
{
  "line": 12,
  "error": "duplicate id: event-1",
  "record": "{...original line...}"
}
```

Use strict mode when an import must be all-or-nothing from the caller’s perspective. In strict mode, the first validation error stops processing and is raised to the caller.

### Duplicate IDs

`id` is the stable identity of an event. The default `duplicate_policy=reject` keeps the first occurrence and rejects later occurrences. The `replace` policy allows repeated IDs to pass through for downstream replacement handling; it does not silently merge records.

### Import summary

The function returns an `ImportSummary`. The command-line interface prints it as JSON:

```json
{
  "input_file": "timeline.jsonl",
  "records_read": 100000,
  "records_imported": 99872,
  "records_rejected": 128,
  "duplicate_ids": 4,
  "duration_seconds": 18.42,
  "peak_memory_mb": null,
  "errors": []
}
```

`peak_memory_mb` is reserved for future runtime instrumentation and is currently `null`.

## Command-line usage

From the repository root:

```bash
python src/timeline_importer.py timeline.jsonl \
  --output normalized.jsonl \
  --rejects rejected.jsonl \
  --batch-size 500 \
  --max-line-bytes 1048576
```

Add `--strict` to stop on the first invalid record:

```bash
python src/timeline_importer.py timeline.jsonl --strict
```

The command exits with status `0` after a completed import. File-access failures and fatal validation failures produce status `1`.

## Contributor checklist

Before adding or changing timeline data, contributors should validate that every record has a stable ID, a supported date, a concise title, a factual description, and at least one traceable source. New schema fields should be added to the validator, documented here, covered by unit tests, and included in the normalized-output expectations. Large fixtures should use JSONL rather than one large JSON array so that tests exercise the production streaming path.

Run the local checks before opening a pull request:

```bash
ruff check src tests
coverage run --branch -m unittest discover -s tests -v
coverage report --fail-under=80
python -m py_compile src/*.py
```

## References

[1]: https://jsonlines.org/ "JSON Lines documentation"
[2]: https://json-schema.org/specification "JSON Schema specification"
