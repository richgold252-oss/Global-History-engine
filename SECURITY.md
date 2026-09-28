# Global History AI Media Engine

Global History AI Media Engine is a modular Phase 1 system for researching historical topics, verifying sources, generating factual scripts, and creating production manifests for short-form history videos.

The project is designed to run in low-cost development mode using a mock AI provider and mock research provider by default. It is intended to stay compatible with future integrations for OpenAI, Gemini, Anthropic, voiceover, FFmpeg rendering, publishing, analytics, and monetization without forcing those services on day one.

## Project overview

This repository implements a foundation for:
- researching historical topics with structured metadata
- collecting evidence and confidence scores
- distinguishing documented evidence from interpretation and uncertainty
- generating short-form narration and video titles
- building production manifests for downstream rendering
- validating core logic through tests
- running in FREE_MODE without external API keys

## Current status

Phase 1 includes:
- configuration validation and environment settings
- AI provider abstraction with mock and optional provider adapters
- research abstraction with mock data and source metadata
- fact/evidence scoring and review gating
- script generation for historical topics
- media manifest generation
- pipeline orchestration
- CLI commands
- SQLite-ready storage layer
- GitHub Actions CI and daily workflow scaffolding

Not claimed as implemented:
- live scraping of websites
- automatic publishing to social platforms
- paid monetization integrations
- video rendering without FFmpeg or a renderer
- unsupported AI provider backends unless configured and installed

## Architecture

The repository is organized around a small set of modules:

- src/config/settings.py — configuration and environment validation
- src/core/models.py — database models
- src/core/schemas.py — validation schemas
- src/core/logging.py — logger setup
- src/research/provider.py — research interfaces and mock provider
- src/research/researcher.py — topic research and source verification
- src/intelligence/ai_provider.py — AI provider abstraction
- src/intelligence/fact_checker.py — evidence scoring
- src/writing/script_generator.py — script and script elements
- src/media/manifest.py — production manifest generation
- src/pipeline/orchestrator.py — orchestration of stages
- src/storage/database.py — SQLite startup
- src/main.py — CLI entry point

## Features

- FREE_MODE support (`FREE_MODE=true`)
- AI provider abstraction: `mock`, `openai`, `gemini`, `anthropic`
- Research provider abstraction: `mock`
- Database-ready SQLite foundation
- Historical evidence score classification: A/B/C/D
- Confidence threshold and review gating
- Script generation with title, hook, narration, description, hashtags
- Media production manifest with scenes and source metadata
- CLI commands for health, research, script, and generate
- tests and CI workflow scaffolding

## Installation

Use a virtual environment and install the project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

## Quick start

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Run the health check:

```bash
python -m src.main health
```

3. Generate a mock story:

```bash
python -m src.main generate "How Ancient African Traders Used Agricultural Supply, Demand and Seasonal Knowledge"
```

4. Run tests:

```bash
pytest -q
```

## FREE MODE

The default configuration is designed for low-cost local development:

- `FREE_MODE=true`
- `AI_PROVIDER=mock`
- `RESEARCH_PROVIDER=mock`
- local SQLite database
- no paid APIs required
- no external network calls needed for mock flows

This keeps the project useful before real API credentials are configured.

## Environment variables

See `.env.example` for the supported variables, including:
- `APP_ENV`
- `FREE_MODE`
- `AI_PROVIDER`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DATABASE_URL`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`
- `INSTAGRAM_ACCESS_TOKEN`
- `FACEBOOK_ACCESS_TOKEN`
- `TIKTOK_ACCESS_TOKEN`
- `X_API_KEY`
- `X_API_SECRET`

Do not commit `.env` or real credentials.

## AI providers

The project defines an AI provider abstraction and supports:
- `mock` — always available for development and tests
- `openai` — optional when installed and configured
- `gemini` — optional when installed and configured
- `anthropic` — optional when installed and configured

The application does not require a real provider in development mode.

## Research providers

The current research abstraction supports:
- `mock` — deterministic development data

This repository does not claim to scrape websites in a way that violates site terms.

## Historical accuracy

Historical accuracy is a first-class requirement.

The system keeps and exposes source metadata including:
- title
- URL
- publisher
- author
- source type
- relevance score
- credibility score
- verification state
- confidence score

Evidence classification is supported:
- A = primary/authoritative source
- B = strong scholarly/institutional source
- C = reputable secondary source
- D = weak or uncertain source

Generated output should clearly distinguish:
- fact
- interpretation
- uncertainty
- historical debate

Low-confidence stories can be flagged for review.

## African history support

The project is designed with African history as a first-class topic family, including themes such as:
- Ancient West Africa
- East Africa
- North Africa
- Central Africa
- Southern Africa
- Nigerian history
- Ghanaian history
- Mali Empire
- Songhai Empire
- Ghana Empire
- Benin Kingdom
- Oyo Empire
- Great Zimbabwe
- Ethiopia
- Nubia
- trade networks
- gold trade
- salt trade
- agricultural trade
- indigenous knowledge
- African philosophy

## Video production

Phase 1 focuses on generation of a production manifest rather than fully rendering video output.

A `video_manifest.json`-style structure is created by the media layer, containing:
- scene number
- duration
- narration
- visual description
- image prompt
- video prompt
- subtitle text
- transition
- source references

If FFmpeg is not installed, the pipeline still generates manifests and marks rendering as unavailable instead of crashing.

## Publishing

Publishing support is intentionally limited to architecture and configuration checks. The repository does not claim a live connection to YouTube, Instagram, Facebook, TikTok, or X unless credentials are actually set and the relevant integration code is added.

## Monetization

The repository includes a monetization-ready domain structure for:
- affiliate links
- digital products
- sponsorship records
- website advertising placeholders
- premium reports
- newsletter support
- YouTube monetization tracking

Phase 1 does not attempt to insert or apply monetization automatically to unrelated content.

## Testing

The project includes pytest-based tests for configuration, mock provider behavior, evidence scoring, research and script generation, and media manifest output.

```bash
pytest -q
```

## GitHub Actions

The repository includes:
- `.github/workflows/ci.yml` for CI validation
- `.github/workflows/daily-pipeline.yml` for scheduled or manual pipeline runs

The daily workflow uses mock mode by default and uploads generated artifacts without claiming social publishing.

## Security

See `SECURITY.md` for the project security policy.

## Roadmap

Phase 1: Research → verification → script → manifest → tests
Phase 2: Image/video generation integrations
Phase 3: Voiceover, subtitles, FFmpeg
Phase 4: Publishing integrations
Phase 5: Analytics
Phase 6: Monetization
Phase 7: Web dashboard

## Contributing

See `CONTRIBUTING.md`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
