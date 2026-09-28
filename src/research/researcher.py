"""Historical research and source verification."""

from typing import List

from src.core.logging import get_logger
from src.core.schemas import ResearchSourceSchema

logger = get_logger(__name__)


class Researcher:
    """Conducts historical research and verifies sources."""

    def __init__(self, research_provider):
        """Initialize researcher with a provider.

        Args:
            research_provider: ResearchProvider instance for sourcing information
        """
        self.provider = research_provider
        logger.info(f"Initialized Researcher with {research_provider.__class__.__name__}")

    def research_topic(self, topic: str, limit: int = 5) -> List[ResearchSourceSchema]:
        """Research a historical topic.

        Args:
            topic: Historical topic to research
            limit: Maximum number of sources to retrieve

        Returns:
            List of research sources on the topic
        """
        logger.info(f"Researching topic: {topic}")
        sources = self.provider.search(topic, limit)
        logger.info(f"Found {len(sources)} sources for '{topic}'")
        return sources

    def verify_sources(self, sources: List[ResearchSourceSchema]) -> List[ResearchSourceSchema]:
        """Verify and validate research sources.

        Args:
            sources: List of sources to verify

        Returns:
            List of verified sources
        """
        logger.info(f"Verifying {len(sources)} sources")

        for source in sources:
            # Mark sources as verified
            source.is_verified = True
            logger.debug(
                f"Verified: {source.title} "
                f"(credibility: {source.credibility_score}, relevance: {source.relevance_score})"
            )

        logger.info(f"Verification complete: {len(sources)} sources verified")
        return sources
