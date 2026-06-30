from fastapi import (
    APIRouter
)

from app.schemas.comparison import (
    CandidateComparisonRequest
)

from app.services.comparison.comparison_service import (
    compare_candidates
)

router = APIRouter(

    prefix="/recruiter",

    tags=[
        "comparison"
    ]
)


@router.post(
    "/compare"
)
def compare(

        request:
        CandidateComparisonRequest
):

    return compare_candidates(

        request.job_id,

        request.candidate_ids
    )