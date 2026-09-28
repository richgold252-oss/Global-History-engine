"""Configuration and environment settings for Global History Engine."""

import os
from typing import Optional


class Config:
    """Application configuration loaded from environment variables."""

    # Application settings
    app_version = "0.1.0"
    app_env = os.getenv("APP_ENV", "development")
    free_mode = os.getenv("FREE_MODE", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # AI Provider configuration
    ai_provider = os.getenv("AI_PROVIDER", "mock")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

    # Research Provider configuration
    research_provider = os.getenv("RESEARCH_PROVIDER", "mock")

    # Database configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/history_engine.db")

    # Content settings
    default_video_duration_seconds = int(os.getenv("DEFAULT_VIDEO_DURATION", "60"))
    confidence_threshold = int(os.getenv("CONFIDENCE_THRESHOLD", "75"))

    # Social Media credential presence checks (do not expose values)
    has_youtube_credentials = bool(os.getenv("YOUTUBE_CLIENT_ID"))
    has_instagram_credentials = bool(os.getenv("INSTAGRAM_ACCESS_TOKEN"))
    has_facebook_credentials = bool(os.getenv("FACEBOOK_ACCESS_TOKEN"))
    has_tiktok_credentials = bool(os.getenv("TIKTOK_ACCESS_TOKEN"))
    has_x_credentials = bool(os.getenv("X_API_KEY"))


def get_config() -> Config:
    """
    Get the application configuration.

    Returns:
        Config instance with all settings from environment
    """
    return Config()
