"""Tests for mock research provider."""

from src.research.provider import MockResearchProvider, get_research_provider
from src.core.schemas import ResearchSourceSchema


def test_mock_research_provider_init():
    """Test mock research provider initialization."""
    provider = MockResearchProvider()
    assert provider is not None


def test_mock_research_provider_search():
    """Test mock research provider returns sources."""
    provider = MockResearchProvider()
    sources = provider.search("Mali Empire trade", limit=5)

    assert isinstance(sources, list)
    assert len(sources) == 5
    assert all(isinstance(s, ResearchSourceSchema) for s in sources)


def test_mock_research_provider_source_structure():
    """Test mock research sources have correct structure."""
    provider = MockResearchProvider()
    sources = provider.search("African history", limit=1)

    source = sources[0]
    assert source.title is not None
    assert "[MOCK]" in source.title  # Clearly marked as mock
    assert source.publisher is not None
    assert source.author is not None
    assert source.source_type is not None
    assert 0 <= source.credibility_score <= 100
    assert 0 <= source.relevance_score <= 100
    assert source.is_verified is True


def test_mock_research_provider_limit():
    """Test mock research provider respects limit parameter."""
    provider = MockResearchProvider()

    sources_1 = provider.search("topic", limit=1)
    assert len(sources_1) == 1

    sources_3 = provider.search("topic", limit=3)
    assert len(sources_3) == 3

    sources_5 = provider.search("topic", limit=5)
    assert len(sources_5) == 5


def test_get_research_provider_mock():
    """Test factory function returns mock provider."""
    provider = get_research_provider("mock")
    assert isinstance(provider, MockResearchProvider)


def test_get_research_provider_unknown():
    """Test factory function raises error for unknown provider."""
    try:
        provider = get_research_provider("unknown_provider")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown research provider" in str(e)
