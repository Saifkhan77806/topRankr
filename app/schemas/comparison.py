from pydantic import BaseModel
from typing import List


class CandidateComparisonRequest(
    BaseModel
):

    job_id: int

    candidate_ids: List[int]