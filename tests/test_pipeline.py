"""Tests for pipeline orchestration."""

from src.pipeline.orchestrator import PipelineOrchestrator
from src.research.provider import MockResearchProvider
from src.intelligence.ai_provider import MockAIProvider
from src.config.settings import get_config


def test_pipeline_orchestrator_init():
    """Test pipeline orchestrator initialization."""
    research_provider = MockResearchProvider()
    ai_provider = MockAIProvider()
    config = get_config()

    orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
    assert orchestrator is not None
    assert orchestrator.researcher is not None
    assert orchestrator.generator is not None


def test_pipeline_orchestrator_research():
    """Test pipeline research stage."""
    research_provider = MockResearchProvider()
    ai_provider = MockAIProvider()
    config = get_config()

    orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
    sources = orchestrator.research("Mali Empire")

    assert isinstance(sources, list)
    assert len(sources) > 0
    assert all(s.is_verified is True for s in sources)


def test_pipeline_orchestrator_generate():
    """Test full pipeline generation."""
    research_provider = MockResearchProvider()
    ai_provider = MockAIProvider()
    config = get_config()

    orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
    result = orchestrator.generate("How Ancient African Traders Used Agricultural Supply, Demand and Seasonal Knowledge")

    assert isinstance(result, dict)
    assert "sources" in result
    assert "script" in result
    assert "manifest_path" in result
    assert len(result["sources"]) > 0
    assert result["script"].title is not None
