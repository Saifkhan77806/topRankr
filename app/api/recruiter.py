from fastapi import APIRouter

from app.services.search_job.search_job_service import ( create_search_job, get_search_job )

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"]
        )


@router.post("/search")
def search_candidates():

    job = create_search_job()

    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress
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