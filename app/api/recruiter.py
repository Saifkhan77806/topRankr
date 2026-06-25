from fastapi import APIRouter

from app.services.search_job.search_job_service import ( create_search_job, get_search_job )
from app.workers.recruiter_tasks import (
    process_recruiter_search
)

from app.schemas.recruiter import (
    RecruiterSearchRequest
)

from app.services.search_results.result_service import (
    get_search_results
)

from app.services.search_job.search_job_service import (
    get_all_jobs
)

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"]
        )


@router.post("/search")
def search_candidates(
    request: RecruiterSearchRequest
):

    job = create_search_job()

    process_recruiter_search.delay(
        job.id,
        request.job_description,
        request.top_k
    )

    return {
        "job_id": job.id,
        "status": "pending"
    }
@router.get(
    "/jobs/{job_id}"
)
def job_status(job_id: int):

    job = get_search_job(job_id)


    # ERROR: IF JOB NOT FOUND 
    if not job:
        return {
            "error":
                "job not found"
        }

    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "result": job.result
    }
    
    
@router.get(
    "/search/{job_id}/results"
)
def recruiter_results(
        job_id: int
):

    return get_search_results(
        job_id
    )

@router.get(
    "/jobs"
)
def recruiter_jobs():

    return get_all_jobs()