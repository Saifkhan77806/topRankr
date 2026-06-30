from fastapi import (
    APIRouter
)

from app.services.candidate.candidate_service import (
    get_resume
)

router = APIRouter(
    prefix="/candidate",
    tags=["candidate"]
)


@router.get(
    "/{candidate_id}/resume"
)
def resume(
        candidate_id: int
):

    return get_resume(
        candidate_id
    )