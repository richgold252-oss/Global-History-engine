"""Research provider abstraction for sourcing historical information."""

from typing import List
from datetime import datetime

from src.core.logging import get_logger
from src.core.schemas import ResearchSourceSchema

logger = get_logger(__name__)


class ResearchProvider:
    """Base research provider interface."""

    def search(self, query: str, limit: int = 5) -> List[ResearchSourceSchema]:
        """Search for research sources on a topic.

        Args:
            query: Research query/topic
            limit: Maximum number of sources to return

        Returns:
            List of research sources
        """
        raise NotImplementedError("search not implemented")


class MockResearchProvider(ResearchProvider):
    """Mock research provider for development and testing.

    Returns deterministic, clearly-marked MOCK/DEMO sources.
    Does not make external API calls or web requests.
    """

    def search(self, query: str, limit: int = 5) -> List[ResearchSourceSchema]:
        """Return mock research sources.

        Args:
            query: Research topic (used only for logging)
            limit: Maximum sources to return

        Returns:
            List of mock research sources
        """
        logger.info(f"Mock research: searching for '{query}' (returning demo data)")

        # Always return the same demo sources for consistency
        # These are clearly marked as MOCK/DEMO to distinguish from real research
        mock_sources = [
            ResearchSourceSchema(
                title="[MOCK] Mali Empire: Architects of West African Trade Networks",
                publisher="[DEMO] Historical Documentation Archive",
                author="[DEMO] Research Team",
                source_type="academic",
                credibility_score=90,
                relevance_score=95,
                is_verified=True,
                publication_date=datetime(2020, 1, 1),
                summary="Demonstration source about Mali Empire trade systems for development purposes.",
            ),
            ResearchSourceSchema(
                title="[MOCK] Songhai Empire and Trans-Saharan Commerce",
                publisher="[DEMO] Educational Records",
                author="[DEMO] Learning Module",
                source_type="academic",
                credibility_score=85,
                relevance_score=90,
                is_verified=True,
                publication_date=datetime(2019, 6, 15),
                summary="Demo content about Songhai trade networks for testing purposes.",
            ),
            ResearchSourceSchema(
                title="[MOCK] Swahili Coast Trade Systems and Indian Ocean Networks",
                publisher="[DEMO] Comparative History Studies",
                author="[DEMO] Test Data Generator",
                source_type="academic",
                credibility_score=88,
                relevance_score=87,
                is_verified=True,
                publication_date=datetime(2021, 3, 20),
                summary="Demonstration content about Swahili trade for development and testing.",
            ),
            ResearchSourceSchema(
                title="[MOCK] Gold Trade in Medieval Africa: Economic Systems",
                publisher="[DEMO] Historical Analysis Platform",
                author="[DEMO] Curriculum Content",
                source_type="academic",
                credibility_score=82,
                relevance_score=85,
                is_verified=True,
                publication_date=datetime(2020, 9, 10),
                summary="Test data about African gold trade systems for mock research.",
            ),
            ResearchSourceSchema(
                title="[MOCK] African Agricultural Innovation and Trade",
                publisher="[DEMO] Technology History Archive",
                author="[DEMO] Development Team",
                source_type="academic",
                credibility_score=80,
                relevance_score=82,
                is_verified=True,
                publication_date=datetime(2021, 11, 5),
                summary="Demo source about agricultural practices and trade in ancient Africa.",
            ),
        ]

        logger.debug(f"Returning {min(limit, len(mock_sources))} mock sources")
        return mock_sources[:limit]


def get_research_provider(provider_name: str) -> ResearchProvider:
    """Factory function to get a research provider instance.

    Args:
        provider_name: Name of provider (currently only 'mock' is supported)

    Returns:
        Configured research provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    if provider_name == "mock":
        logger.info("Using mock research provider")
        return MockResearchProvider()

    raise ValueError(f"Unknown research provider: {provider_name}")
