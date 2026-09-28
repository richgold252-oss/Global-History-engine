"""Global History Engine CLI."""

import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

from src.config.settings import get_config
from src.core.logging import get_logger
from src.intelligence.ai_provider import get_ai_provider
from src.pipeline.orchestrator import PipelineOrchestrator
from src.research.provider import get_research_provider

logger = get_logger(__name__, level="INFO")


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Global History AI Media Engine - Research, verify, and generate historical content"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Research command
    research_parser = subparsers.add_parser("research", help="Research a historical topic")
    research_parser.add_argument("topic", help="Historical topic to research")
    research_parser.add_argument("--limit", type=int, default=5, help="Number of sources to retrieve")

    # Script command
    script_parser = subparsers.add_parser("script", help="Generate script for a topic")
    script_parser.add_argument("topic", help="Historical topic")
    script_parser.add_argument("--duration", type=int, default=60, help="Video duration in seconds")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate complete story with manifest"
    )
    generate_parser.add_argument("topic", help="Historical topic")
    generate_parser.add_argument("--duration", type=int, default=60, help="Video duration in seconds")
    generate_parser.add_argument("--output-dir", default="data/media", help="Output directory")

    # Health command
    subparsers.add_parser("health", help="Check system health and configuration")

    # Daily command
    subparsers.add_parser("daily", help="Run the daily pipeline")

    return parser


def cmd_health() -> int:
    """Display system health and configuration status."""
    try:
        config = get_config()
        ffmpeg_installed = bool(shutil.which("ffmpeg"))

        health_status = {
            "status": "healthy",
            "python_version": platform.python_version(),
            "application_version": config.app_version,
            "environment": config.app_env,
            "free_mode": config.free_mode,
            "ai_provider": config.ai_provider,
            "research_provider": config.research_provider,
            "database_configured": bool(config.database_url),
            "ffmpeg_available": ffmpeg_installed,
            "logging_level": config.log_level,
            "confidence_threshold": config.confidence_threshold,
            "publishing_platforms": {
                "youtube": config.has_youtube_credentials,
                "instagram": config.has_instagram_credentials,
                "facebook": config.has_facebook_credentials,
                "tiktok": config.has_tiktok_credentials,
                "x": config.has_x_credentials,
            },
        }

        print(json.dumps(health_status, indent=2))
        return 0

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 1


def cmd_research(topic: str, limit: int = 5) -> int:
    """Execute research on a historical topic."""
    try:
        config = get_config()
        pipeline = PipelineOrchestrator(
            get_research_provider(config.research_provider),
            get_ai_provider(
                config.ai_provider,
                config.openai_api_key,
                config.gemini_api_key,
                config.anthropic_api_key,
            ),
            config,
        )

        logger.info(f"Researching topic: {topic}")
        sources = pipeline.research(topic)

        output = {
            "topic": topic,
            "source_count": len(sources),
            "sources": [
                {
                    "title": s.title,
                    "url": s.url,
                    "publisher": s.publisher,
                    "author": s.author,
                    "source_type": s.source_type,
                    "credibility_score": s.credibility_score,
                    "relevance_score": s.relevance_score,
                    "is_verified": s.is_verified,
                }
                for s in sources
            ],
        }

        print(json.dumps(output, indent=2, default=str))
        return 0

    except Exception as e:
        logger.error(f"Research failed: {e}")
        return 1


def cmd_script(topic: str, duration: int = 60) -> int:
    """Generate a video script for a topic."""
    try:
        config = get_config()
        pipeline = PipelineOrchestrator(
            get_research_provider(config.research_provider),
            get_ai_provider(
                config.ai_provider,
                config.openai_api_key,
                config.gemini_api_key,
                config.anthropic_api_key,
            ),
            config,
        )

        logger.info(f"Generating script for topic: {topic}")
        sources = pipeline.research(topic)
        script = pipeline.generator.generate_script(
            topic, sources, duration, min((s.credibility_score for s in sources), default=0)
        )

        output = {
            "title": script.title,
            "hook": script.hook,
            "narration_length": len(script.narration),
            "duration_seconds": script.duration_seconds,
            "confidence_score": script.confidence_score,
            "review_required": script.review_required,
            "source_count": len(script.sources),
            "hashtags": script.hashtags,
        }

        print(json.dumps(output, indent=2, default=str))
        return 0

    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        return 1


def cmd_generate(topic: str, duration: int = 60, output_dir: str = "data/media") -> int:
    """Generate complete story, script, and manifest."""
    try:
        config = get_config()
        pipeline = PipelineOrchestrator(
            get_research_provider(config.research_provider),
            get_ai_provider(
                config.ai_provider,
                config.openai_api_key,
                config.gemini_api_key,
                config.anthropic_api_key,
            ),
            config,
        )

        logger.info(f"Generating complete story for topic: {topic}")
        result = pipeline.generate(topic)

        output = {
            "topic": topic,
            "title": result["script"].title,
            "hook": result["script"].hook,
            "narration_preview": result["script"].narration[:100] + "...",
            "duration_seconds": result["script"].duration_seconds,
            "confidence_score": result["script"].confidence_score,
            "review_required": result["script"].review_required,
            "sources_used": len(result["sources"]),
            "manifest_path": str(result["manifest_path"]),
            "manifest_exists": result["manifest_path"].exists(),
            "next_step": (
                "REQUIRES HUMAN REVIEW"
                if result["script"].review_required
                else "Ready for media production"
            ),
        }

        print(json.dumps(output, indent=2, default=str))
        logger.info(f"Story generated and saved to {result['manifest_path']}")
        return 0

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return 1


def cmd_daily() -> int:
    """Run the daily pipeline."""
    logger.info("Daily pipeline execution not yet implemented")
    logger.info("Use: python -m src.main generate '<topic>' for manual generation")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.command == "health":
            return cmd_health()
        elif args.command == "research":
            return cmd_research(args.topic, args.limit)
        elif args.command == "script":
            return cmd_script(args.topic, args.duration)
        elif args.command == "generate":
            return cmd_generate(args.topic, args.duration, args.output_dir)
        elif args.command == "daily":
            return cmd_daily()
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
