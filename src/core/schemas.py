"""Pydantic schemas for data validation and serialization."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchSourceSchema(BaseModel):
    """Schema for research sources."""

    url: Optional[str] = None
    title: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    source_type: str  # academic, news, book, archive, etc.
    summary: Optional[str] = None
    credibility_score: int = Field(default=50, ge=0, le=100)
    relevance_score: int = Field(default=50, ge=0, le=100)
    is_verified: bool = False

    class Config:
        from_attributes = True


class FactSchema(BaseModel):
    """Schema for historical facts."""

    claim: str
    supporting_evidence: Optional[str] = None
    evidence_classification: str = Field(default="D", pattern="^[A-D]$")
    confidence_score: int = Field(default=50, ge=0, le=100)
    is_disputed: bool = False
    historical_period: Optional[str] = None
    geographical_context: Optional[str] = None
    uncertainty_notes: Optional[str] = None

    class Config:
        from_attributes = True


class StorySchema(BaseModel):
    """Schema for stories."""

    title: str
    hook: Optional[str] = None
    narration: str
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    duration_seconds: int = Field(default=60, ge=10, le=3600)
    confidence_score: int = Field(default=50, ge=0, le=100)
    review_required: bool = False
    sources: List[ResearchSourceSchema] = []

    class Config:
        from_attributes = True


class ScriptSchema(BaseModel):
    """Schema for video scripts."""

    title: str
    hook: str = Field(min_length=1)
    narration: str = Field(min_length=1)
    duration_seconds: int = Field(default=60, ge=10, le=3600)
    confidence_score: int = Field(default=50, ge=0, le=100)
    review_required: bool = False
    sources: List[ResearchSourceSchema] = []
    visuals: List[dict] = []
    subtitles: List[str] = []

    class Config:
        from_attributes = True


class ProductionManifestSchema(BaseModel):
    """Schema for video production manifests."""

    story_id: int
    title: str
    duration_seconds: int
    scenes: List[dict] = []
    narration_text: str
    visual_prompts: List[str] = []
    subtitle_file: Optional[str] = None
    source_references: List[ResearchSourceSchema] = []
    confidence_score: int = Field(default=50, ge=0, le=100)
    review_required: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
