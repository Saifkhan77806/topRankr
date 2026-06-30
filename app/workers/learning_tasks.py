from app.workers.celery_worker import celery_app

from app.services.learning.preference_learning import (
    learn_from_feedback,
)

from app.services.learning.historical_jd_learning import (
    update_job_embedding_outcomes,
    store_job_embedding,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def task_learn_from_feedback(
    self,
    job_id: int,
    candidate_id: int,
    feedback_type: str,
):
    """
    Triggered every time POST /recruiter/feedback is called.

    1. Updates feature weights in recruiter_preferences table.
    2. Updates the historical hiring outcome lists in job_embeddings table.

    Runs asynchronously so the API response is instant.
    """

    try:
        learn_from_feedback(
            job_id=job_id,
            candidate_id=candidate_id,
            feedback_type=feedback_type,
        )

        update_job_embedding_outcomes(
            job_id=job_id,
            candidate_id=candidate_id,
            feedback_type=feedback_type,
        )

    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def task_store_job_embedding(
    self,
    job_id: int,
    embedding: list,
):
    """
    Triggered at the end of process_recruiter_search.
    Persists the JD embedding so future searches can compare against it.
    """

    try:
        store_job_embedding(
            job_id=job_id,
            embedding=embedding,
        )

    except Exception as exc:
        raise self.retry(exc=exc)
