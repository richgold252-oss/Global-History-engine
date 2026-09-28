"""Phase 1 comprehensive test suite."""

import json
from pathlib import Path

import pytest

from src.config.settings import AppConfig, get_config
from src.core.schemas import ResearchSourceSchema, ScriptSchema
from src.intelligence.ai_provider import MockAIProvider, get_ai_provider
from src.intelligence.fact_checker import evidence_score, review_required
from src.media.manifest import build_manifest_from_script
from src.pipeline.orchestrator import PipelineOrchestrator
from src.research.provider import MockResearchProvider
from src.research.researcher import Researcher
from src.writing.script_generator import ScriptGenerator


class TestConfiguration:
    """Test configuration loading and validation."""

    def test_config_loads(self):
        config = get_config()
        assert config is not None
        assert config.app_version == "0.1.0"

    def test_free_mode_enabled(self):
        config = get_config()
        assert config.free_mode is True

    def test_mock_provider_selected(self):
        config = get_config()
        assert config.ai_provider == "mock"
        assert config.research_provider == "mock"

    def test_default_video_duration(self):
        config = get_config()
        assert config.default_video_duration_seconds == 60

    def test_confidence_threshold(self):
        config = get_config()
        assert config.confidence_threshold == 75


class TestAIProvider:
    """Test AI provider abstraction."""

    def test_mock_provider_instantiation(self):
        provider = MockAIProvider()
        assert provider.is_available() is True
        assert provider.name == "mock"

    def test_mock_generate_title(self):
        provider = MockAIProvider()
        result = provider.generate_text("Generate a title")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_generate_hook(self):
        provider = MockAIProvider()
        result = provider.generate_text("Generate a hook")
        assert "ancient" in result.lower() or "african" in result.lower()

    def test_mock_deterministic(self):
        provider = MockAIProvider()
        result1 = provider.generate_text("Generate a title")
        result2 = provider.generate_text("Generate a title")
        assert result1 == result2

    def test_get_ai_provider_mock(self):
        provider = get_ai_provider("mock")
        assert provider.name == "mock"


class TestResearchProvider:
    """Test research provider abstraction."""

    def test_mock_research_provider_instantiation(self):
        provider = MockResearchProvider()
        assert provider.is_available() is True
        assert provider.name == "mock"

    def test_mock_search_returns_results(self):
        provider = MockResearchProvider()
        results = provider.search("African trade")
        assert len(results) > 0
        assert all(hasattr(r, "title") for r in results)

    def test_mock_search_respects_limit(self):
        provider = MockResearchProvider()
        results = provider.search("African trade", limit=3)
        assert len(results) <= 3

    def test_search_result_has_metadata(self):
        provider = MockResearchProvider()
        results = provider.search("African trade")
        assert len(results) > 0
        result = results[0]
        assert result.title
        assert result.credibility >= 0
        assert result.relevance >= 0


class TestResearcher:
    """Test researcher and source verification."""

    def test_researcher_instantiation(self):
        provider = MockResearchProvider()
        researcher = Researcher(provider)
        assert researcher is not None

    def test_research_topic(self):
        provider = MockResearchProvider()
        researcher = Researcher(provider)
        sources = researcher.research_topic("African trade")
        assert len(sources) > 0
        assert all(isinstance(s, ResearchSourceSchema) for s in sources)

    def test_verify_sources(self):
        provider = MockResearchProvider()
        researcher = Researcher(provider)
        sources = researcher.research_topic("African trade")
        verified = researcher.verify_sources(sources)
        assert len(verified) == len(sources)
        assert any(s.is_verified for s in verified)

    def test_collect_top_sources(self):
        provider = MockResearchProvider()
        researcher = Researcher(provider)
        sources = researcher.research_topic("African trade", limit=10)
        top = researcher.collect_top_sources(sources, limit=3)
        assert len(top) <= 3


class TestEvidenceScoring:
    """Test evidence classification and scoring."""

    def test_evidence_score_calculation(self):
        score = evidence_score(["A", "B"], [90, 85])
        assert 0 <= score <= 100

    def test_evidence_score_weights_A_highest(self):
        score_a = evidence_score(["A"], [0])
        score_d = evidence_score(["D"], [0])
        assert score_a > score_d

    def test_review_required_low_score(self):
        assert review_required(50, threshold=75) is True

    def test_review_not_required_high_score(self):
        assert review_required(85, threshold=75) is False


class TestScriptGenerator:
    """Test script generation."""

    def test_script_generator_instantiation(self):
        provider = MockAIProvider()
        generator = ScriptGenerator(provider)
        assert generator is not None

    def test_generate_script(self):
        ai_provider = MockAIProvider()
        research_provider = MockResearchProvider()
        researcher = Researcher(research_provider)
        
        sources = researcher.research_topic("African trade")
        generator = ScriptGenerator(ai_provider)
        
        script = generator.generate_script("African trade", sources)
        assert isinstance(script, ScriptSchema)
        assert script.title
        assert script.hook
        assert script.narration
        assert script.duration_seconds == 60

    def test_generate_title(self):
        provider = MockAIProvider()
        generator = ScriptGenerator(provider)
        title = generator.generate_title("African trade")
        assert isinstance(title, str)
        assert len(title) > 0

    def test_generate_hook(self):
        provider = MockAIProvider()
        generator = ScriptGenerator(provider)
        hook = generator.generate_hook("African trade", 60)
        assert isinstance(hook, str)
        assert len(hook) > 0

    def test_generate_narration(self):
        provider = MockAIProvider()
        research_provider = MockResearchProvider()
        researcher = Researcher(research_provider)
        
        sources = researcher.research_topic("African trade")
        generator = ScriptGenerator(provider)
        narration = generator.generate_narration("African trade", sources, 60)
        assert isinstance(narration, str)
        assert len(narration) > 50

    def test_generate_description(self):
        provider = MockAIProvider()
        generator = ScriptGenerator(provider)
        desc = generator.generate_description("African trade", "Test narration")
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_generate_hashtags(self):
        provider = MockAIProvider()
        generator = ScriptGenerator(provider)
        hashtags = generator.generate_hashtags("African trade")
        assert isinstance(hashtags, list)
        assert all(tag.startswith("#") for tag in hashtags)


class TestMediaManifest:
    """Test media manifest generation."""

    def test_build_manifest_from_script(self):
        script_data = {
            "title": "Test Story",
            "duration_seconds": 60,
            "narration": "Test narration. This is a scene. Another scene here.",
            "sources": [],
        }
        manifest = build_manifest_from_script("Test Story", script_data)
        assert manifest is not None
        assert manifest.title == "Test Story"
        assert len(manifest.scenes) > 0

    def test_manifest_save(self, tmp_path):
        script_data = {
            "title": "Test Story",
            "duration_seconds": 60,
            "narration": "Test narration. This is a scene.",
            "sources": [],
        }
        manifest = build_manifest_from_script("Test Story", script_data)
        output_path = manifest.save(str(tmp_path))
        assert output_path.exists()
        assert output_path.suffix == ".json"

    def test_manifest_json_valid(self, tmp_path):
        script_data = {
            "title": "Test Story",
            "duration_seconds": 60,
            "narration": "Test narration. Scene one.",
            "sources": [],
        }
        manifest = build_manifest_from_script("Test Story", script_data)
        output_path = manifest.save(str(tmp_path))
        
        with open(output_path) as f:
            data = json.load(f)
        
        assert data["title"] == "Test Story"
        assert data["duration_seconds"] == 60
        assert len(data["scenes"]) > 0


class TestPipelineOrchestrator:
    """Test end-to-end pipeline orchestration."""

    def test_orchestrator_instantiation(self):
        config = get_config()
        research_provider = MockResearchProvider()
        ai_provider = MockAIProvider()
        
        orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
        assert orchestrator is not None

    def test_pipeline_research_stage(self):
        config = get_config()
        research_provider = MockResearchProvider()
        ai_provider = MockAIProvider()
        
        orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
        sources = orchestrator.research("African trade")
        
        assert len(sources) > 0
        assert all(isinstance(s, ResearchSourceSchema) for s in sources)

    def test_pipeline_generate_full(self, tmp_path):
        import os
        os.chdir(str(tmp_path))
        Path("data/media").mkdir(parents=True, exist_ok=True)
        
        config = get_config()
        research_provider = MockResearchProvider()
        ai_provider = MockAIProvider()
        
        orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
        result = orchestrator.generate("African agricultural trade")
        
        assert "sources" in result
        assert "script" in result
        assert "manifest_path" in result
        assert len(result["sources"]) > 0
        assert result["script"].title
        assert result["script"].narration
        assert result["manifest_path"].exists()


class TestEndToEnd:
    """End-to-end validation of complete pipeline."""

    def test_complete_pipeline_flow(self, tmp_path):
        """Execute the complete Phase 1 pipeline."""
        import os
        os.chdir(str(tmp_path))
        Path("data/media").mkdir(parents=True, exist_ok=True)
        
        # Step 1: Configure
        config = get_config()
        assert config.free_mode is True
        
        # Step 2: Initialize providers
        research_provider = MockResearchProvider()
        ai_provider = MockAIProvider()
        
        # Step 3: Create orchestrator
        orchestrator = PipelineOrchestrator(research_provider, ai_provider, config)
        
        # Step 4: Run full pipeline
        topic = "How Ancient African Traders Used Agricultural Supply, Demand and Seasonal Knowledge"
        result = orchestrator.generate(topic)
        
        # Validate results
        assert result["sources"], "No sources found"
        assert result["script"], "No script generated"
        assert result["manifest_path"], "No manifest created"
        
        # Validate script
        script = result["script"]
        assert script.title, "Missing title"
        assert script.hook, "Missing hook"
        assert script.narration, "Missing narration"
        assert script.duration_seconds > 0, "Invalid duration"
        assert 0 <= script.confidence_score <= 100, "Invalid confidence score"
        
        # Validate manifest
        manifest_path = result["manifest_path"]
        assert manifest_path.exists(), f"Manifest not found at {manifest_path}"
        
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        
        assert manifest_data["title"], "Missing manifest title"
        assert manifest_data["scenes"], "No scenes in manifest"
        assert manifest_data["duration_seconds"] > 0, "Invalid manifest duration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
