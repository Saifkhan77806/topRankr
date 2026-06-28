from app.core.database import (
    SessionLocal
)

from app.models.candidate import (
    Candidate
)

db = SessionLocal()

candidates = db.query(
    Candidate
).all()

for c in candidates:

    print(
        c.id,
        c.name,
        c.industry
    )