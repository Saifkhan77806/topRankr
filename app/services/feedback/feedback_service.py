from app.core.database import SessionLocal

from app.models.recruiter_feedback import RecruiterFeedback


def save_feedback(
    job_id: int,
    candidate_id: int,
    feedback: str,
):
    """
    Persist the feedback record.
    The learning pipeline is triggered separately from the API layer
    via a Celery task so this function stays fast.
    """

    db = SessionLocal()

    try:
        row = RecruiterFeedback(
            job_id=job_id,
            candidate_id=candidate_id,
            feedback=feedback,
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return row

    finally:
        db.close()
