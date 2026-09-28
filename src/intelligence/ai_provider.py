"""AI provider abstraction with mock and real implementations."""

from typing import Optional

from src.core.logging import get_logger

logger = get_logger(__name__)


class AIProvider:
    """Base AI provider interface for text generation."""

    def __init__(self, name: str):
        """Initialize AI provider.

        Args:
            name: Provider name (mock, openai, gemini, anthropic)
        """
        self.name = name

    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt for text generation
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        raise NotImplementedError(f"generate_text not implemented for {self.name}")


class MockAIProvider(AIProvider):
    """Mock AI provider for development and testing.

    Returns deterministic responses without external API calls.
    """

    def __init__(self):
        """Initialize mock AI provider."""
        super().__init__("mock")

    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate deterministic mock responses.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens (ignored in mock mode)

        Returns:
            Mock text response
        """
        prompt_lower = prompt.lower()

        # Detect intent from prompt and return appropriate mock response
        if "title" in prompt_lower:
            return "Ancient African Trade Routes: Hidden Treasures of History"
        elif "hook" in prompt_lower:
            return "Most people don't know that African merchants controlled global commerce long before Europe entered the game. The Mali Empire, Songhai, and Swahili traders built economic networks that shaped world history."
        elif "narration" in prompt_lower:
            return "From the Mali Empire to the Swahili Coast, African traders built sophisticated networks that moved gold, salt, spices, and ideas across continents. The trans-Saharan trade routes weren't just commercial paths—they were cultural highways. Archaeological evidence and Islamic scholar records show that merchants from West Africa traded with Europe, the Middle East, and Asia. The Empire of Mali, at its height in the 14th century, controlled trade routes that generated enormous wealth. Modern historians recognize that these African trading systems influenced global economics for centuries. Understanding this history challenges the false narrative that Africa was isolated from world trade."
        elif "description" in prompt_lower:
            return "Explore the remarkable history of ancient African trade networks that dominated global commerce. Discover how empires like Mali and Songhai built economic systems that rivaled anything in Europe or Asia, and learn why this untold story matters today."
        elif "hashtag" in prompt_lower:
            return "#AfricanHistory #AncientTrade #Mali #Songhai #History #Africa #Education #Documentary #Heritage #MustWatch #HistoryLesson #FYP"
        else:
            # Default mock response
            return f"[MOCK RESPONSE] Generated response to prompt about {prompt[:50]}..."


def get_ai_provider(
    provider_name: str,
    openai_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
) -> AIProvider:
    """Factory function to get an AI provider instance.

    Args:
        provider_name: Name of provider (mock, openai, gemini, anthropic)
        openai_api_key: OpenAI API key (optional)
        gemini_api_key: Google Gemini API key (optional)
        anthropic_api_key: Anthropic Claude API key (optional)

    Returns:
        Configured AI provider instance

    Raises:
        ValueError: If provider name is unknown
    """
    if provider_name == "mock":
        logger.info("Using mock AI provider")
        return MockAIProvider()

    # Future: Add real provider implementations
    if provider_name == "openai":
        logger.warning("OpenAI provider not yet implemented, falling back to mock")
        return MockAIProvider()
    elif provider_name == "gemini":
        logger.warning("Gemini provider not yet implemented, falling back to mock")
        return MockAIProvider()
    elif provider_name == "anthropic":
        logger.warning("Anthropic provider not yet implemented, falling back to mock")
        return MockAIProvider()

    raise ValueError(f"Unknown AI provider: {provider_name}")
