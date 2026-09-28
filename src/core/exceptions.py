"""Custom exceptions for Global History Engine."""


class HistoryEngineException(Exception):
    """Base exception for the application."""

    pass


class ConfigurationError(HistoryEngineException):
    """Raised when configuration is invalid."""

    pass


class ResearchError(HistoryEngineException):
    """Raised when research fails."""

    pass


class AIProviderError(HistoryEngineException):
    """Raised when AI provider fails."""

    pass


class PipelineError(HistoryEngineException):
    """Raised when pipeline execution fails."""

    pass
