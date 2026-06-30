from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from sqlalchemy.sql import func

from app.core.database import Base


class CandidateSecurity(Base):

    __tablename__ = "candidate_security"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_email = Column(
        String,
        nullable=True,
        index=True
    )

    resume_hash = Column(
        String,
        nullable=True,
        index=True
    )

    spam_score = Column(
        Integer,
        nullable=False,
        default=0
    )

    prompt_injection = Column(
        Boolean,
        nullable=False,
        default=False
    )

    duplicate_resume = Column(
        Boolean,
        nullable=False,
        default=False
    )

    virus_scan = Column(
        String,
        nullable=False,
        default="not_scanned"
    )

    allowed = Column(
        Boolean,
        nullable=False,
        default=False
    )

    rejection_reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
