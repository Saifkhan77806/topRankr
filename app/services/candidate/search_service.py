from app.core.database import (SessionLocal)

from app.models.candidate import (Candidate)


def get_candidates(candidate_ids):

    db = SessionLocal()

    candidates = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()

    db.close()

    return candidates