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
