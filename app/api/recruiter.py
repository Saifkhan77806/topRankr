import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, FileResponse

from app.services.search_job.search_job_service import (
    create_search_job,
    get_search_job,
    get_all_jobs,
)

from app.workers.recruiter_tasks import process_recruiter_search

from app.schemas.recruiter import RecruiterSearchRequest

from app.services.search_results.result_service import get_search_results

from app.services.search_job.stream_service import job_progress_stream

from app.services.candidate.candidate_service import get_candidate_details

from app.schemas.feedback import FeedbackRequest

from app.services.feedback.feedback_service import save_feedback

from app.services.feedback.analytics import feedback_stats

from app.workers.learning_tasks import task_learn_from_feedback


router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"],
)


@router.post("/search")
def search_candidates(request: RecruiterSearchRequest):

    job = create_search_job()

    process_recruiter_search.delay(
        job.id,
        request.job_description,
        request.top_k,
    )

    return {
        "job_id": job.id,
        "status": "pending",
    }


@router.get("/jobs/{job_id}")
def job_status(job_id: int):

    job = get_search_job(job_id)

    if not job:
        return {"error": "job not found"}

    return {
        "job_id":       job.id,
        "status":       job.status,
        "progress":     job.progress,
        "current_step": job.current_step,
        "result":       job.result,
    }


@router.get("/search/{job_id}/results")
def recruiter_results(job_id: int):

    return get_search_results(job_id)


@router.get("/jobs")
def recruiter_jobs():

    return get_all_jobs()


@router.get(
    "/stream/{job_id}",
    summary="Stream real-time job progress via Server-Sent Events",
)
async def stream_job_progress(job_id: int):

    return StreamingResponse(
        job_progress_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "Connection":        "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/candidate/{candidate_id}")
def candidate_details(candidate_id: int):

    candidate = get_candidate_details(candidate_id)

    if not candidate:
        return {
            "success": False,
            "message": "Candidate not found",
        }

    return {
        "success": True,
        "data":    candidate,
    }


@router.get("/resume/{candidate_id}")
def download_resume(candidate_id: int):

    candidate = get_candidate_details(candidate_id)

    if not candidate:
        return {
            "success": False,
            "message": "Candidate not found",
        }

    path = candidate["resume_path"]

    if not path or not os.path.exists(path):
        return {
            "success": False,
            "message": "Resume not found",
        }

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=os.path.basename(path),
    )


@router.post("/feedback")
def recruiter_feedback(request: FeedbackRequest):
    """
    Save recruiter feedback and automatically trigger:
    1. Feature weight learning  (updates recruiter_preferences)
    2. Historical JD outcome update  (updates job_embeddings)

    Both learning steps run asynchronously via Celery —
    the API response is instant.
    """

    feedback = save_feedback(
        request.job_id,
        request.candidate_id,
        request.feedback,
    )

    task_learn_from_feedback.delay(
        job_id=request.job_id,
        candidate_id=request.candidate_id,
        feedback_type=request.feedback,
    )

    return {
        "success":     True,
        "message":     "Feedback saved. Learning pipeline triggered.",
        "feedback_id": feedback.id,
    }


@router.get("/feedback/stats")
def recruiter_feedback_stats():

    return feedback_stats()
