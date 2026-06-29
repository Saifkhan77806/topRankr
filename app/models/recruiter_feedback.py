from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.core.database import Base


class RecruiterFeedback(Base):

    __tablename__ = "recruiter_feedback"

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

    feedback = Column(
        String,
        nullable=False
    )
    # shortlisted
    # rejected
    # interviewed
    # hired

    created_at = Column(
        DateTime,
        server_default=func.now()
    )