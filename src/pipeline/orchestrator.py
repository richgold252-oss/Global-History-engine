"""Phase 1 pipeline orchestration."""

from src.media.manifest import build_manifest_from_script
from src.research.researcher import Researcher
from src.writing.script_generator import ScriptGenerator


class PipelineOrchestrator:
    """Compose research, verification, script, and manifest stages."""

    def __init__(self, research_provider, ai_provider, config):
        self.researcher = Researcher(research_provider)
        self.generator = ScriptGenerator(ai_provider)
        self.config = config

    def research(self, topic: str):
        sources = self.researcher.research_topic(topic)
        return self.researcher.verify_sources(sources)

    def generate(self, topic: str):
        sources = self.research(topic)
        confidence = min((source.credibility_score for source in sources), default=0)
        script = self.generator.generate_script(
            topic, sources, self.config.default_video_duration_seconds, confidence
        )
        manifest = build_manifest_from_script(script.title, script.model_dump())
        path = manifest.save("data/media")
        return {"sources": sources, "script": script, "manifest_path": path}
