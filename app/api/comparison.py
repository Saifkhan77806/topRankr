from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.schemas.comparison import (
    CandidateComparisonRequest
)

from app.services.comparison.comparison_service import (
    compare_candidates
)
from app.core.auth import recruiter_required
from app.core.rate_limit import limiter

router = APIRouter(

    prefix="/recruiter",

    tags=[
        "comparison"
    ]
)


@router.post(
    "/compare"
)
@limiter.limit("20/minute")
def compare(
        request: Request,

        payload:
        CandidateComparisonRequest
        ,

        current_user=Depends(recruiter_required)
):

    return compare_candidates(

        payload.job_id,

        payload.candidate_ids
    )
