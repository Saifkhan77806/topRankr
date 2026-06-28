from fastapi import FastAPI

from app.scheduler.gmail_scheduler import ( start_scheduler )
from app.api.recruiter import ( router as recruiter_router )

app = FastAPI()

app.include_router(recruiter_router)


@app.on_event("startup")
def startup():

    start_scheduler() 


@app.get("/")
def health():

    return {
        "status": "running"
    }