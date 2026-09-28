"""Tests for script generation."""

from src.writing.script_generator import ScriptGenerator
from src.intelligence.ai_provider import MockAIProvider
from src.core.schemas import ResearchSourceSchema, ScriptSchema
from datetime import datetime


def test_script_generator_init():
    """Test script generator initialization."""
    ai_provider = MockAIProvider()
    generator = ScriptGenerator(ai_provider)
    assert generator is not None
    assert generator.ai_provider == ai_provider


def test_script_generator_generate_title():
    """Test script title generation."""
    ai_provider = MockAIProvider()
    generator = ScriptGenerator(ai_provider)

    title = generator.generate_title("Mali Empire trade networks")
    assert isinstance(title, str)
    assert len(title) > 0


def test_script_generator_generate_hook():
    """Test script hook generation."""
    ai_provider = MockAIProvider()
    generator = ScriptGenerator(ai_provider)

    hook = generator.generate_hook("Ancient African traders", 60)
    assert isinstance(hook, str)
    assert len(hook) > 0


def test_script_generator_generate_narration():
    """Test script narration generation."""
    ai_provider = MockAIProvider()
    generator = ScriptGenerator(ai_provider)

    sources = [
        ResearchSourceSchema(
            title="Test Source",
            source_type="academic",
            credibility_score=90,
            relevance_score=85,
        )
    ]

    narration = generator.generate_narration("African trade", sources, 60)
    assert isinstance(narration, str)
    assert len(narration) > 0


def test_script_generator_generate_script():
    """Test full script generation."""
    ai_provider = MockAIProvider()
    generator = ScriptGenerator(ai_provider)

    sources = [
        ResearchSourceSchema(
            title="[MOCK] Test Source 1",
            source_type="academic",
            credibility_score=90,
            relevance_score=85,
            is_verified=True,
        ),
        ResearchSourceSchema(
            title="[MOCK] Test Source 2",
            source_type="academic",
            credibility_score=85,
            relevance_score=80,
            is_verified=True,
        ),
    ]

    script = generator.generate_script(
        topic="Mali Empire gold trade",
        sources=sources,
        duration_seconds=60,
        confidence_score=85,
    )

    assert isinstance(script, ScriptSchema)
    assert script.title is not None
    assert len(script.title) > 0
    assert script.hook is not None
    assert script.narration is not None
    assert script.duration_seconds == 60
    assert script.confidence_score == 85
    assert script.review_required is False  # confidence >= 75
    assert len(script.sources) == 2
    assert len(script.visuals) > 0
    assert len(script.subtitles) > 0
