"""SQLAlchemy database models for Global History Engine."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Topic(Base):
    """Represents a historical topic to research."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True)
    status = Column(String(50), default="pending")  # pending, researching, completed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stories: List["Story"] = relationship("Story", back_populates="topic")
    research_sources: List["ResearchSource"] = relationship(
        "ResearchSource", back_populates="topic"
    )
    historical_facts: List["HistoricalFact"] = relationship(
        "HistoricalFact", back_populates="topic"
    )


class ResearchSource(Base):
    """Represents a source used in research."""

    __tablename__ = "research_sources"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    url = Column(String(500), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    publisher = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    source_type = Column(String(50), nullable=False)  # academic, news, book, archive, etc.
    summary = Column(Text, nullable=True)
    credibility_score = Column(Integer, default=50)  # 0-100
    relevance_score = Column(Integer, default=50)  # 0-100
    is_verified = Column(Integer, default=0)  # 0=false, 1=true
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="research_sources")
    historical_facts: List["HistoricalFact"] = relationship(
        "HistoricalFact", back_populates="source"
    )


class HistoricalFact(Base):
    """Represents a verified historical fact extracted from research."""

    __tablename__ = "historical_facts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("research_sources.id"), nullable=False)
    claim = Column(Text, nullable=False)
    supporting_evidence = Column(Text, nullable=True)
    evidence_classification = Column(String(10), default="D")  # A, B, C, D
    confidence_score = Column(Integer, default=50)  # 0-100
    is_disputed = Column(Integer, default=0)  # 0=false, 1=true
    historical_period = Column(String(255), nullable=True)
    geographical_context = Column(String(255), nullable=True)
    uncertainty_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="historical_facts")
    source = relationship("ResearchSource", back_populates="historical_facts")


class Story(Base):
    """Represents a generated historical story."""

    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    hook = Column(Text, nullable=True)
    narration = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON array stored as string
    duration_seconds = Column(Integer, default=60)
    confidence_score = Column(Integer, default=50)  # 0-100
    review_required = Column(Integer, default=0)  # 0=false, 1=true
    status = Column(String(50), default="draft")  # draft, approved, published
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="stories")
