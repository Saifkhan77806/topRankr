from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.services.candidate.candidate_service import (
    get_resume
)
from app.core.auth import recruiter_required
from app.core.rate_limit import limiter

router = APIRouter(
    prefix="/candidate",
    tags=["candidate"]
)


@router.get(
    "/{candidate_id}/resume"
)
@limiter.limit("20/hour")
def resume(
        request: Request,
        candidate_id: int,
        current_user=Depends(recruiter_required)
):

    return get_resume(
        candidate_id
    )


@router.get(
    "/resume/{candidate_id}"
)
@limiter.limit("20/hour")
def resume_by_path(
        request: Request,
        candidate_id: int,
        current_user=Depends(recruiter_required)
):

    return get_resume(
        candidate_id
    )
