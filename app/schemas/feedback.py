from pydantic import BaseModel


class FeedbackRequest(
    BaseModel
):

    job_id: int

    candidate_id: int

    feedback: str