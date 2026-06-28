from app.core.database import (
    Base,
    engine
)

from app.models.candidate import Candidate

Base.metadata.create_all(
    bind=engine
)

print("Tables created")