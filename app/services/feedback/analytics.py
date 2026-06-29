from app.core.database import (
    SessionLocal
)

from app.models.recruiter_feedback import (
    RecruiterFeedback
)


def feedback_stats():

    db = SessionLocal()

    try:

        rows = db.query(
            RecruiterFeedback
        ).all()

        stats = {

            "shortlisted":0,

            "rejected":0,

            "interviewed":0,

            "hired":0
        }

        for row in rows:

            if row.feedback in stats:

                stats[
                    row.feedback
                ] += 1

        return stats

    finally:

        db.close()