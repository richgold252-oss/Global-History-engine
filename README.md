# Global-History-engine

Status: prototype

What it is
An autonomous pipeline that researches, scripts, generates, and publishes short-form world history videos across YouTube Shorts, TikTok, Instagram Reels, Facebook Reels, and X (Twitter). Designed for a daily publishing cadence with human editorial oversight before release.

Why this repo
This project demonstrates an end-to-end content pipeline combining automated research, script generation, media assembly (TTS + visuals + captions), platform-specific publishing, and monitoring.

Key components
- researcher/: source discovery & scraping, citation extraction
- writer/: LLM prompt templates & script formatting
- media/: TTS, visual templates, subtitle generator
- editor-ui/: lightweight review & approval interface
- publisher/: adapters for each target platform
- orchestrator/: DAG runner and scheduler
- infra/: deployment manifests, CI pipelines

Getting started (dev)
1. Read SECURITY.md and CONTRIBUTING.md.
2. Copy .env.example -> .env and populate secrets via your secrets manager.
3. Run locally: docker-compose up --build
4. Run tests: make test

(Provide more detailed setup commands and service-level instructions in respective directories.)

Safety, ethics, and legal
- All episodes must include source citations in the video description.
- A human editorial review is required before publish.
- Do not publish content involving protected individuals without permissions.
- See LEGAL.md for copyright & platform policy requirements.

Contributing
See CONTRIBUTING.md for how to propose changes, run the editor UI locally, and submit content templates.

License
(Choose a license and state it here.)

Contact
Project owner: @richgold252-oss
