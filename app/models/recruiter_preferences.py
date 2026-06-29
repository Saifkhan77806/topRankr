from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base


class RecruiterPreference(Base):

    __tablename__ = "recruiter_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # The feature name e.g. "Java", "SpringBoot", "Leadership"
    feature_name = Column(
        String,
        nullable=False,
        index=True
    )

    # skill | industry | seniority | domain | education | leadership | experience
    feature_type = Column(
        String,
        nullable=False
    )

    # learned weight: positive = preferred, negative = avoided
    weight = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # how many times this feature appeared in shortlisted/interviewed/hired
    positive_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    # how many times this feature appeared in rejected candidates
    negative_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
