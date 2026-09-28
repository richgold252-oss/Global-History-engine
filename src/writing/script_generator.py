"""Script generation for historical content."""

from typing import List, Optional

from src.core.logging import get_logger
from src.core.schemas import ResearchSourceSchema, ScriptSchema
from src.intelligence.ai_provider import AIProvider

logger = get_logger(__name__)


class ScriptGenerator:
    """Generates video scripts from historical research."""

    def __init__(self, ai_provider: AIProvider):
        """
        Initialize script generator.

        Args:
            ai_provider: AI provider instance for text generation
        """
        self.ai_provider = ai_provider
        logger.info(f"Initialized ScriptGenerator with {ai_provider.name} provider")

    def generate_script(
        self,
        topic: str,
        sources: List[ResearchSourceSchema],
        duration_seconds: int = 60,
        confidence_score: int = 75,
    ) -> ScriptSchema:
        """
        Generate a complete script from research.

        Args:
            topic: Historical topic
            sources: List of research sources
            duration_seconds: Target video duration
            confidence_score: Overall confidence in the script

        Returns:
            Complete script schema
        """
        logger.info(f"Generating script for topic: {topic} ({duration_seconds}s)")

        # Generate individual components
        title = self.generate_title(topic)
        hook = self.generate_hook(topic, duration_seconds)
        narration = self.generate_narration(topic, sources, duration_seconds)
        description = self.generate_description(topic, narration)
        hashtags = self.generate_hashtags(topic)

        # Determine if review is required
        review_required = confidence_score < 75

        # Build visual prompts for each major claim
        visuals = self._build_visual_prompts(narration)

        # Build subtitle list (simple sentence-by-sentence split)
        subtitles = narration.split(". ")

        # Create and return script
        script = ScriptSchema(
            title=title,
            hook=hook,
            narration=narration,
            duration_seconds=duration_seconds,
            confidence_score=confidence_score,
            review_required=review_required,
            sources=sources,
            visuals=visuals,
            subtitles=subtitles,
        )

        logger.info(f"Generated script: {title}")
        return script

    def generate_title(self, topic: str) -> str:
        """Generate a compelling video title."""
        prompt = (
            f"Create a short, compelling YouTube/TikTok video title (max 60 chars) "
            f"for a historical topic: {topic}\n"
            f"Response format: Just the title, nothing else."
        )
        title = self.ai_provider.generate_text(prompt, max_tokens=100).strip()
        logger.debug(f"Generated title: {title}")
        return title

    def generate_hook(self, topic: str, duration_seconds: int) -> str:
        """Generate an attention-grabbing hook for the first 3 seconds."""
        prompt = (
            f"Create an attention-grabbing hook (2-3 sentences, under 30 words) "
            f"for a {duration_seconds}-second history video about: {topic}\n"
            f"The hook should be surprising and make viewers want to watch more.\n"
            f"Response format: Just the hook, nothing else."
        )
        hook = self.ai_provider.generate_text(prompt, max_tokens=100).strip()
        logger.debug(f"Generated hook: {hook[:50]}...")
        return hook

    def generate_narration(
        self, topic: str, sources: List[ResearchSourceSchema], duration_seconds: int
    ) -> str:
        """Generate the main narration script."""
        # Estimate words: ~130 words per minute for narration
        estimated_words = int((duration_seconds / 60) * 130)

        source_refs = "\n".join(
            [f"- {s.title} ({s.source_type})" for s in sources[:3]]
        )

        prompt = (
            f"Write historically accurate narration for a {duration_seconds}-second video "
            f"about: {topic}\n"
            f"Target length: approximately {estimated_words} words\n"
            f"Use these sources:\n{source_refs}\n"
            f"Guidelines:\n"
            f"- Be factual and specific\n"
            f"- Avoid speculation unless clearly marked as interpretation\n"
            f"- Include specific dates, names, and places where possible\n"
            f"- Use engaging, conversational language\n"
            f"- Structure: Hook (3 sec) → Context (5-10 sec) → Main story (20-35 sec) "
            f"→ Insight (10 sec) → CTA (3 sec)\n"
            f"Response format: Just the narration, nothing else."
        )

        narration = self.ai_provider.generate_text(
            prompt, max_tokens=500
        ).strip()
        logger.debug(f"Generated narration ({len(narration)} chars)")
        return narration

    def generate_description(self, topic: str, narration: str) -> str:
        """Generate video description for social media."""
        prompt = (
            f"Write a brief, engaging video description (100-150 words) for a "
            f"history video about: {topic}\n"
            f"Include educational value and engagement call-to-action.\n"
            f"Response format: Just the description, nothing else."
        )
        description = self.ai_provider.generate_text(
            prompt, max_tokens=250
        ).strip()
        logger.debug(f"Generated description ({len(description)} chars)")
        return description

    def generate_hashtags(self, topic: str) -> List[str]:
        """Generate relevant hashtags for social media."""
        prompt = (
            f"Generate 8-12 relevant hashtags for a history video about: {topic}\n"
            f"Include mix of popular and niche hashtags.\n"
            f"Response format: Space-separated hashtags like: #History #Africa #Culture"
        )
        hashtags_str = self.ai_provider.generate_text(prompt, max_tokens=100).strip()

        # Parse hashtags
        hashtags = [tag.strip() for tag in hashtags_str.split() if tag.startswith("#")]
        logger.debug(f"Generated {len(hashtags)} hashtags")
        return hashtags

    @staticmethod
    def _build_visual_prompts(narration: str) -> List[dict]:
        """Build visual prompts from narration sentences."""
        sentences = narration.split(". ")
        visuals = []

        for i, sentence in enumerate(sentences[:5]):  # Max 5 scenes
            visual_prompt = {
                "scene_number": i + 1,
                "duration_seconds": 12,
                "description": sentence.strip()[:100],  # Truncate for visual prompt
                "style": "historical documentary",
                "mood": "educational and engaging",
            }
            visuals.append(visual_prompt)

        return visuals
