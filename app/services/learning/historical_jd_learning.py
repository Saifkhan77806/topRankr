import numpy as np

from app.core.database import SessionLocal
from app.models.job_embedding import JobEmbedding


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HISTORICAL_SCORE_CAP = 20.0

SIMILARITY_THRESHOLD = 0.70

TOP_PAST_JDS = 10

WEIGHT_HIRED       = 2.0
WEIGHT_SHORTLISTED = 1.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Pure-numpy cosine similarity between two embedding lists.
    Returns 0.0 if either vector is zero-norm.
    """

    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


# ---------------------------------------------------------------------------
# Store / update job embedding
# ---------------------------------------------------------------------------

def store_job_embedding(
    job_id: int,
    embedding: list,
):
    """
    Persist the JD embedding for a completed search job.
    Called at the end of process_recruiter_search via Celery task.
    Skipped if a row already exists for this job_id.
    """

    db = SessionLocal()
    try:
        existing = (
            db.query(JobEmbedding)
            .filter(JobEmbedding.job_id == job_id)
            .first()
        )

        if existing:
            return

        row = JobEmbedding(
            job_id=job_id,
            embedding=embedding,
            successful_candidate_ids=[],
            hired_candidate_ids=[],
        )
        db.add(row)
        db.commit()

    finally:
        db.close()


def update_job_embedding_outcomes(
    job_id: int,
    candidate_id: int,
    feedback_type: str,
):
    """
    When a recruiter gives feedback on a candidate, record that
    candidate_id in the appropriate outcome list on the JobEmbedding row
    so future searches can learn from it.

    feedback_type: "shortlisted" | "interviewed" | "hired" | "rejected"
    """

    if feedback_type == "rejected":
        return

    db = SessionLocal()
    try:
        row = (
            db.query(JobEmbedding)
            .filter(JobEmbedding.job_id == job_id)
            .first()
        )

        if not row:
            return

        successful = list(row.successful_candidate_ids or [])
        if candidate_id not in successful:
            successful.append(candidate_id)
        row.successful_candidate_ids = successful

        if feedback_type == "hired":
            hired = list(row.hired_candidate_ids or [])
            if candidate_id not in hired:
                hired.append(candidate_id)
            row.hired_candidate_ids = hired

        db.commit()

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Score calculation
# ---------------------------------------------------------------------------

def calculate_historical_score(
    current_embedding: list,
    candidate_id: int,
) -> float:
    """
    Compare current JD embedding against the TOP_PAST_JDS most recent
    stored embeddings.  For each past JD whose cosine similarity exceeds
    SIMILARITY_THRESHOLD, check whether candidate_id appeared in the
    successful or hired lists and accumulate a weighted score.

    Returns a float in [0, HISTORICAL_SCORE_CAP].
    """

    db = SessionLocal()
    try:
        past_jobs = (
            db.query(JobEmbedding)
            .order_by(JobEmbedding.id.desc())
            .limit(TOP_PAST_JDS)
            .all()
        )

        if not past_jobs:
            return 0.0

        accumulated = 0.0

        for past_job in past_jobs:

            similarity = _cosine_similarity(
                current_embedding,
                past_job.embedding,
            )

            if similarity < SIMILARITY_THRESHOLD:
                continue

            jd_weight      = similarity
            successful_ids = past_job.successful_candidate_ids or []
            hired_ids      = past_job.hired_candidate_ids or []

            if candidate_id in hired_ids:
                accumulated += jd_weight * WEIGHT_HIRED

            elif candidate_id in successful_ids:
                accumulated += jd_weight * WEIGHT_SHORTLISTED

        raw_max = WEIGHT_HIRED * TOP_PAST_JDS
        score   = (accumulated / raw_max) * HISTORICAL_SCORE_CAP

        return max(0.0, min(HISTORICAL_SCORE_CAP, score))

    finally:
        db.close()


def calculate_hiring_success_score(candidate_id: int) -> float:
    """
    Global hiring success score: how often has this candidate been hired
    across all past searches regardless of JD similarity.

    Returns a float in [0, 10.0].
    """

    db = SessionLocal()
    try:
        all_jobs = db.query(JobEmbedding).all()

        hire_count = sum(
            1
            for job in all_jobs
            if candidate_id in (job.hired_candidate_ids or [])
        )

        return min(hire_count * 5.0, 10.0)

    finally:
        db.close()
