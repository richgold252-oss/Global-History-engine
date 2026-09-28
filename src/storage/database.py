"""SQLite-compatible database initialization."""
from pathlib import Path

from sqlalchemy import create_engine

from src.core.models import Base


def init_database(url: str = "sqlite:///./data/history_engine.db"):
    if url.startswith("sqlite"):
        Path("data").mkdir(exist_ok=True)
    engine = create_engine(
        url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
    )
    Base.metadata.create_all(engine)
    return engine
