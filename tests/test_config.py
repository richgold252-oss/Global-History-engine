"""Tests for configuration module."""

import os
from src.config.settings import get_config, Config


def test_config_defaults():
    """Test default configuration values."""
    config = get_config()
    assert config is not None
    assert config.app_version == "0.1.0"
    assert config.free_mode is True
    assert config.ai_provider == "mock"
    assert config.research_provider == "mock"
    assert config.log_level == "INFO"


def test_config_from_env():
    """Test configuration from environment variables."""
    os.environ["APP_ENV"] = "production"
    os.environ["FREE_MODE"] = "false"
    os.environ["AI_PROVIDER"] = "openai"

    config = get_config()
    assert config.app_env == "production"
    assert config.free_mode is False
    assert config.ai_provider == "openai"

    # Cleanup
    del os.environ["APP_ENV"]
    del os.environ["FREE_MODE"]
    del os.environ["AI_PROVIDER"]


def test_config_free_mode():
    """Test FREE_MODE configuration."""
    os.environ["FREE_MODE"] = "true"
    config = get_config()
    assert config.free_mode is True

    os.environ["FREE_MODE"] = "False"
    config = get_config()
    assert config.free_mode is False

    del os.environ["FREE_MODE"]
