"""Quality scoring and publication-state evaluation for generated content."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


def _safe_average(values: Iterable[float]) -> float:
    """Compute average while gracefully handling empty iterables."""
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def _resolve_value(item: Any, name: str, default: float = 0.0) -> float:
    """Resolve a score value from obj or dict-like input."""
    if item is None:
        return default
    if isinstance(item, dict):
        value = item.get(name, default)
    else:
        value = getattr(item, name, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_factuality(sources: List[Any], facts: List[Any] | None = None) -> int:
    """
    Compute a factuality score based on source credibility and fact confidence.

    A higher score indicates stronger evidence quality and lower uncertainty.
    """
    if not sources:
        return 0

    source_scores = [
        max(0, min(100, _resolve_value(source, "credibility_score", 0.0)))
        for source in sources
    ]
    source_average = _safe_average(source_scores)

    if facts:
        fact_scores = [
            max(0, min(100, _resolve_value(fact, "confidence_score", 0.0)))
            for fact in facts
        ]
        fact_average = _safe_average(fact_scores)
    else:
        fact_average = source_average

    # Blend source quality and fact confidence.
    score = (source_average * 0.7) + (fact_average * 0.3)
    return int(round(score))


def calculate_source_quality(sources: List[Any]) -> int:
    """Compute source quality from credibility and relevance scores."""
    if not sources:
        return 0
    weighted = []
    for source in sources:
        credibility = _resolve_value(source, "credibility_score", 0.0)
        relevance = _resolve_value(source, "relevance_score", 0.0)
        weighted.append((credibility * 0.65) + (relevance * 0.35))
    return int(round(_safe_average(weighted)))


def calculate_historical_confidence(sources: List[Any], facts: List[Any] | None = None) -> int:
    """Estimate historical confidence based on source quality and claim support."""
    if not sources:
        return 0

    fact_scores = []
    if facts:
        for fact in facts:
            fact_score = _resolve_value(fact, "confidence_score", 0.0)
            disputed = bool(_resolve_value(fact, "is_disputed", 0.0))
            if disputed:
                fact_score *= 0.8
            fact_scores.append(fact_score)

    base = calculate_source_quality(sources)
    if fact_scores:
        base = int(round((base * 0.6) + (_safe_average(fact_scores) * 0.4)))
    return max(0, min(100, base))


def calculate_completeness(script: Any, sources: List[Any]) -> int:
    """Rate how complete the story output is based on required narrative sections."""
    if script is None:
        return 0

    script_fields = [
        "title",
        "hook",
        "narration",
        "description",
        "duration_seconds",
    ]

    coverage = 0
    for field in script_fields:
        value = getattr(script, field, None)
        if value:
            coverage += 1

    source_bonus = 20 if sources else 0
    completeness = int(round((coverage / len(script_fields)) * 80 + source_bonus))
    return max(0, min(100, completeness))


def calculate_overall_quality(sources: List[Any], facts: List[Any] | None, script: Any) -> Dict[str, int]:
    """Compute the overall quality envelope for a generated story."""
    factuality = calculate_factuality(sources, facts)
    source_quality = calculate_source_quality(sources)
    historical_confidence = calculate_historical_confidence(sources, facts)
    completeness = calculate_completeness(script, sources)

    overall = int(
        round(
            (factuality * 0.30)
            + (source_quality * 0.25)
            + (historical_confidence * 0.25)
            + (completeness * 0.20)
        )
    )

    return {
        "factuality": factuality,
        "source_quality": source_quality,
        "historical_confidence": historical_confidence,
        "completeness": completeness,
        "overall": max(0, min(100, overall)),
    }


def get_publication_status(overall_score: int) -> Tuple[str, str]:
    """Return publication status and explanatory note."""
    if overall_score < 70:
        return (
            "RESEARCH REQUIRED",
            "flag for additional fact-checking and source verification",
        )
    if 70 <= overall_score < 85:
        return (
            "HUMAN REVIEW",
            "requires editor approval before publishing",
        )
    return (
        "READY FOR PRODUCTION",
        "approved for automated publishing",
    )


def should_publish_automatically(overall_score: int, human_review_required: bool) -> bool:
    """Determine whether the item may be published automatically."""
    return overall_score >= 85 and not human_review_required


def score_story(sources: List[Any], script: Any, facts: List[Any] | None = None) -> Dict[str, Any]:
    """Bundle scoring, publication status, and publishability into one object."""
    scores = calculate_overall_quality(sources, facts, script)
    status, note = get_publication_status(scores["overall"])
    review_required = status != "READY FOR PRODUCTION"

    quality = {
        **scores,
        "status": status,
        "status_note": note,
        "review_required": review_required,
        "publish_eligible": should_publish_automatically(scores["overall"], review_required),
    }
    return quality
