"""Tests for mock AI provider."""

from src.intelligence.ai_provider import MockAIProvider, get_ai_provider


def test_mock_ai_provider_init():
    """Test mock AI provider initialization."""
    provider = MockAIProvider()
    assert provider.name == "mock"


def test_mock_ai_generate_title():
    """Test mock AI provider generates titles."""
    provider = MockAIProvider()
    prompt = "Create a title for a history video about African trade"
    result = provider.generate_text(prompt, max_tokens=100)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Ancient" in result or "Trade" in result


def test_mock_ai_generate_hook():
    """Test mock AI provider generates hooks."""
    provider = MockAIProvider()
    prompt = "Create a hook for a history video"
    result = provider.generate_text(prompt, max_tokens=100)
    assert isinstance(result, str)
    assert len(result) > 0


def test_mock_ai_generate_narration():
    """Test mock AI provider generates narration."""
    provider = MockAIProvider()
    prompt = "Write historically accurate narration"
    result = provider.generate_text(prompt, max_tokens=500)
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_ai_provider_mock():
    """Test factory function returns mock provider."""
    provider = get_ai_provider("mock")
    assert provider.name == "mock"


def test_get_ai_provider_unknown():
    """Test factory function raises error for unknown provider."""
    try:
        provider = get_ai_provider("unknown_provider")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown AI provider" in str(e)
