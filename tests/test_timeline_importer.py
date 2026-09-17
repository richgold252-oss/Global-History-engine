import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from timeline_importer import (
    ImportConfig,
    TimelineValidationError,
    import_jsonl,
    main,
    validate_event,
)

VALID = {
    "id": "event-1",
    "date": "1939-09-01",
    "title": "Germany invades Poland",
    "description": "The invasion began the European theatre of World War II.",
    "sources": [{"title": "USHMM", "url": "https://example.org/source"}],
}


class TimelineImporterTests(unittest.TestCase):
    def test_validate_applies_optional_defaults(self):
        event = validate_event(VALID)
        self.assertEqual(event["date_precision"], "day")
        self.assertEqual(event["tags"], [])
        self.assertEqual(event["media"], [])

    def test_streams_in_batches_and_writes_valid_records(self):
        lines = "\n".join(json.dumps({**VALID, "id": f"event-{i}"}) for i in range(5))
        output = io.StringIO()
        batches = []
        summary = import_jsonl(io.StringIO(lines), output_file=output, config=ImportConfig(batch_size=2), on_batch=lambda batch: batches.append(len(batch)))
        self.assertEqual(summary.records_read, 5)
        self.assertEqual(summary.records_imported, 5)
        self.assertEqual(summary.records_rejected, 0)
        self.assertEqual(batches, [2, 2, 1])
        self.assertEqual(len(output.getvalue().splitlines()), 5)

    def test_rejects_bad_json_and_schema_records(self):
        bad = json.dumps({**VALID, "id": "bad id"})
        rejects = io.StringIO()
        summary = import_jsonl(io.StringIO("not-json\n" + bad + "\n"), reject_file=rejects)
        self.assertEqual(summary.records_read, 2)
        self.assertEqual(summary.records_imported, 0)
        self.assertEqual(summary.records_rejected, 2)
        self.assertEqual(len(rejects.getvalue().splitlines()), 2)

    def test_duplicate_ids_are_rejected(self):
        content = "\n".join(json.dumps(VALID) for _ in range(2))
        summary = import_jsonl(io.StringIO(content))
        self.assertEqual(summary.records_imported, 1)
        self.assertEqual(summary.duplicate_ids, 1)

    def test_strict_mode_stops_on_first_error(self):
        with self.assertRaises(TimelineValidationError):
            import_jsonl(io.StringIO(json.dumps({"id": "missing"}) + "\n"), config=ImportConfig(strict=True))

    def test_line_limit_is_enforced(self):
        with self.assertRaises(TimelineValidationError):
            import_jsonl(io.StringIO(json.dumps(VALID) + "\n"), config=ImportConfig(max_line_bytes=10))

    def test_invalid_config_values_are_rejected(self):
        with self.assertRaises(ValueError):
            ImportConfig(batch_size=0)
        with self.assertRaises(ValueError):
            ImportConfig(max_line_bytes=0)
        with self.assertRaises(ValueError):
            ImportConfig(duplicate_policy="ignore")
        with self.assertRaises(ValueError):
            ImportConfig(on_error="skip")

    def test_supported_partial_and_datetime_dates_are_accepted(self):
        for event_date in ("1939", "1939-09", "1939-09-01T12:30:00Z"):
            with self.subTest(event_date=event_date):
                validate_event({**VALID, "date": event_date})

    def test_invalid_dates_are_rejected(self):
        for event_date in ("1939-99-01", "1939-02-30", "not-a-date"):
            with self.subTest(event_date=event_date), self.assertRaises(TimelineValidationError):
                validate_event({**VALID, "date": event_date})

    def test_unknown_fields_and_missing_sources_are_rejected(self):
        with self.assertRaises(TimelineValidationError):
            validate_event({**VALID, "unexpected": True})
        with self.assertRaises(TimelineValidationError):
            validate_event({**VALID, "sources": []})
        with self.assertRaises(TimelineValidationError):
            validate_event({**VALID, "sources": "source"})

    def test_invalid_source_metadata_is_rejected(self):
        invalid_sources = [
            [{"title": "Source", "url": "ftp://example.org"}],
            [{"title": "Source", "url": "https://example.org", "published_at": "yesterday"}],
            [{"title": "Source", "url": "https://example.org", "unknown": True}],
        ]
        for sources in invalid_sources:
            with self.subTest(sources=sources), self.assertRaises(TimelineValidationError):
                validate_event({**VALID, "sources": sources})

    def test_location_and_media_validation(self):
        invalid_locations = [
            {"latitude": 91, "longitude": 0},
            {"country_code": "usa"},
            {"name": "Place", "unknown": True},
            {},
        ]
        for location in invalid_locations:
            with self.subTest(location=location), self.assertRaises(TimelineValidationError):
                validate_event({**VALID, "location": location})
        invalid_media = [
            [{"type": "image", "url": "not-a-url"}],
            [{"type": "spreadsheet", "url": "https://example.org/file"}],
            [{"type": "image"}],
            "media",
        ]
        for media in invalid_media:
            with self.subTest(media=media), self.assertRaises(TimelineValidationError):
                validate_event({**VALID, "media": media})

    def test_array_metadata_and_timestamp_validation(self):
        for field_name in ("people", "organizations", "tags"):
            with self.subTest(field_name=field_name), self.assertRaises(TimelineValidationError):
                validate_event({**VALID, field_name: ["same", "same"]})
        with self.assertRaises(TimelineValidationError):
            validate_event({**VALID, "updated_at": "not-a-timestamp"})
        with self.assertRaises(TimelineValidationError):
            validate_event({**VALID, "metadata": []})

    def test_blank_lines_and_empty_input_are_handled(self):
        summary = import_jsonl(io.StringIO("\n\n" + json.dumps(VALID) + "\n\n"))
        self.assertEqual(summary.records_read, 1)
        self.assertEqual(summary.records_imported, 1)
        empty = import_jsonl(io.StringIO(""))
        self.assertEqual(empty.records_read, 0)
        self.assertEqual(empty.records_imported, 0)

    def test_replace_policy_and_raise_error_policy(self):
        content = "\n".join(json.dumps(VALID) for _ in range(2))
        summary = import_jsonl(io.StringIO(content), config=ImportConfig(duplicate_policy="replace"))
        self.assertEqual(summary.records_imported, 2)
        with self.assertRaises(json.JSONDecodeError):
            import_jsonl(io.StringIO("not-json\n"), config=ImportConfig(on_error="raise"))

    def test_cli_success_and_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.jsonl"
            source.write_text(json.dumps(VALID) + "\n", encoding="utf-8")
            self.assertEqual(main([str(source)]), 0)
        self.assertEqual(main(["does-not-exist.jsonl"]), 1)

    def test_file_paths_are_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.jsonl"
            output = Path(directory) / "output.jsonl"
            source.write_text(json.dumps(VALID) + "\n", encoding="utf-8")
            summary = import_jsonl(source, output_file=output)
            self.assertEqual(summary.records_imported, 1)
            self.assertEqual(len(output.read_text(encoding="utf-8").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
