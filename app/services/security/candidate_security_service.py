import os

from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.candidate_security import CandidateSecurity
from app.services.security.resume_security import calculate_resume_hash


def duplicate_resume_exists(resume_hash):
    if not resume_hash:
        return False

    db = SessionLocal()

    try:
        existing_security_record = (
            db.query(CandidateSecurity)
            .filter(
                CandidateSecurity.resume_hash == resume_hash,
                CandidateSecurity.allowed.is_(True)
            )
            .first()
        )

        if existing_security_record:
            return True

        candidates = db.query(Candidate).all()

        for candidate in candidates:
            resume_path = candidate.resume_path

            if not resume_path or not os.path.exists(resume_path):
                continue

            try:
                with open(resume_path, "rb") as file:
                    existing_hash = calculate_resume_hash(file.read())
            except Exception:
                continue

            if existing_hash == resume_hash:
                return True

        return False

    finally:
        db.close()


def save_candidate_security_record(
        candidate_email,
        resume_hash,
        spam_score,
        prompt_injection,
        duplicate_resume,
        virus_scan,
        allowed,
        rejection_reason
):
    db = SessionLocal()

    try:
        record = CandidateSecurity(
            candidate_email=candidate_email,
            resume_hash=resume_hash,
            spam_score=spam_score,
            prompt_injection=prompt_injection,
            duplicate_resume=duplicate_resume,
            virus_scan=virus_scan,
            allowed=allowed,
            rejection_reason=rejection_reason
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        db.close()
