from sqlalchemy import (
    Column,
    Integer,
    JSON,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.core.database import Base


class JobEmbedding(Base):
    """
    Stores the JD embedding and outcome data for every completed search.
    Used by the Historical JD Learning engine to find past similar JDs
    and boost candidates that matched well in those searches.
    """

    __tablename__ = "job_embeddings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("search_jobs.id"),
        nullable=False,
        unique=True,
        index=True
    )

    # serialised as a JSON list of floats (BGE → 384 dims)
    embedding = Column(
        JSON,
        nullable=False
    )

    # list of candidate_ids that were shortlisted / interviewed / hired
    successful_candidate_ids = Column(
        JSON,
        nullable=False,
        default=list
    )

    # list of candidate_ids that were explicitly hired
    hired_candidate_ids = Column(
        JSON,
        nullable=False,
        default=list
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
