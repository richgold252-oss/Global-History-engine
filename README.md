# Global-History-engine

Autonomous AI pipeline that researches, scripts, generates, and publishes short-form world history videos daily across YouTube Shorts, TikTok, Instagram Reels, Facebook Reels, and X.

Status
- Streaming JSONL timeline importer implemented with bounded event retention.
- CI workflow added in a previous PR (left enabled).

What’s included
- LICENSE (MIT)
- .gitignore (generic)
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- .github issue and PR templates
- src/main.py (entrypoint)
- src/timeline_importer.py (streaming importer and schema validation)
- tests/test_timeline_importer.py (importer tests)

Quick start
1. Clone the repo:
   git clone https://github.com/richgold252-oss/Global-History-engine.git
2. Create a virtual environment (for Python starter):
   python -m venv .venv && source .venv/bin/activate
3. Run an import:
   python src/timeline_importer.py timeline.jsonl --output normalized.jsonl --rejects rejected.jsonl

The importer accepts one event per JSONL line, validates `id`, `date`, `title`,
`description`, and at least one HTTP(S) source, then writes valid records
incrementally. Invalid and duplicate records are reported in the reject file;
processing continues by default. Use `--strict` to stop at the first error.

Run the tests without third-party dependencies:

```bash
python -m unittest discover -s tests -v
```

Contributing
See CONTRIBUTING.md for contribution guidelines.

License
This project is licensed under the MIT License — see the LICENSE file for details.
