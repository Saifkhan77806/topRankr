from pydantic import BaseModel


class RecruiterSearchRequest(BaseModel):

    job_description: str

    top_k: int = 20