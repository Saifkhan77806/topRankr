from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base


class SearchJob(Base):

    __tablename__ = "search_jobs"

    id = Column( Integer, primary_key=True, index=True )

    status = Column( String, default="pending" )

    progress = Column( Integer, default=0 )

    current_step = Column( String, default="queued" )

    result = Column( JSON, nullable=True )

    created_at = Column( DateTime, server_default=func.now() )