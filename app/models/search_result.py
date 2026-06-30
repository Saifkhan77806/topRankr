from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON
)

from sqlalchemy.sql import func

from app.core.database import Base


class SearchResult(Base):

    __tablename__ = "search_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey(
            "search_jobs.id"
        ),
        nullable=False
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "candidates.id"
        ),
        nullable=False
    )

    rank = Column(
        Integer,
        nullable=False
    )

    semantic_score = Column(
        Float,
        nullable=True
    )

    ranking_score = Column(
        Float,
        nullable=True
    )

    recommendation = Column(
        String,
        nullable=True
    )

    ai_reason = Column(
        Text,
        nullable=True
    )

    explanation = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )