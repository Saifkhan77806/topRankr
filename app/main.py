from fastapi import FastAPI

from app.scheduler.gmail_scheduler import ( start_scheduler )
from app.api.recruiter import ( router as recruiter_router )
from app.api.candidate import (
    router as candidate_router
)

app = FastAPI()

app.include_router(recruiter_router)
app.include_router(candidate_router)


@app.on_event("startup")
def startup():

    start_scheduler() 




@app.get("/")
def health():

    return {
        "status": "running"
    }