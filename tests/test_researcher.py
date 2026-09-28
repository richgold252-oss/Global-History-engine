"""Tests for researcher module."""

from src.research.researcher import Researcher
from src.research.provider import MockResearchProvider
from src.core.schemas import ResearchSourceSchema


def test_researcher_init():
    """Test researcher initialization."""
    provider = MockResearchProvider()
    researcher = Researcher(provider)
    assert researcher is not None
    assert researcher.provider == provider


def test_researcher_research_topic():
    """Test researcher can research a topic."""
    provider = MockResearchProvider()
    researcher = Researcher(provider)

    sources = researcher.research_topic("Mali Empire", limit=3)

    assert isinstance(sources, list)
    assert len(sources) == 3
    assert all(isinstance(s, ResearchSourceSchema) for s in sources)


def test_researcher_verify_sources():
    """Test researcher can verify sources."""
    provider = MockResearchProvider()
    researcher = Researcher(provider)

    sources = researcher.research_topic("African trade", limit=2)
    verified = researcher.verify_sources(sources)

    assert len(verified) == len(sources)
    assert all(s.is_verified is True for s in verified)


def test_researcher_full_workflow():
    """Test full researcher workflow."""
    provider = MockResearchProvider()
    researcher = Researcher(provider)

    # Research
    sources = researcher.research_topic("Songhai Empire", limit=4)
    assert len(sources) == 4

    # Verify
    verified = researcher.verify_sources(sources)
    assert len(verified) == 4
    assert all(s.is_verified is True for s in verified)
