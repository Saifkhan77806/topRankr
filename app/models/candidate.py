from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base


class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    phone = Column(
        String,
        nullable=True
    )

    current_title = Column(
        String,
        nullable=True
    )

    experience_years = Column(
        Integer,
        nullable=True
    )

    industry = Column(
        String,
        nullable=True
    )

    profile = Column(
        JSON,
        nullable=False
    )

    summary = Column(
        Text,
        nullable=False
    )

    resume_path = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )