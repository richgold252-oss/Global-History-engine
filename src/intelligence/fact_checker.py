"""Evidence scoring helpers."""

CLASS_WEIGHTS = {"A": 100, "B": 85, "C": 70, "D": 35}


def evidence_score(classifications, source_scores):
    values = [CLASS_WEIGHTS.get(str(item).upper(), 0) for item in classifications]
    values.extend(max(0, min(100, int(score))) for score in source_scores)
    return round(sum(values) / len(values)) if values else 0


def review_required(score: int, threshold: int = 75) -> bool:
    return score < threshold
