"""Tests for fact checking and evidence scoring."""

from src.intelligence.fact_checker import evidence_score, review_required


def test_evidence_score_single():
    """Test evidence scoring with single value."""
    classifications = ["A"]
    source_scores = [90]
    score = evidence_score(classifications, source_scores)
    assert isinstance(score, int)
    assert 0 <= score <= 100


def test_evidence_score_multiple():
    """Test evidence scoring with multiple values."""
    classifications = ["A", "B", "C"]
    source_scores = [95, 85, 70]
    score = evidence_score(classifications, source_scores)
    assert isinstance(score, int)
    assert 0 <= score <= 100


def test_evidence_score_empty():
    """Test evidence scoring with empty inputs."""
    classifications = []
    source_scores = []
    score = evidence_score(classifications, source_scores)
    assert score == 0


def test_review_required_threshold():
    """Test review_required function."""
    assert review_required(50) is True  # Below 75
    assert review_required(75) is False  # At threshold
    assert review_required(85) is False  # Above threshold
