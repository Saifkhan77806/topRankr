from fastapi import FastAPI

from app.scheduler.gmail_scheduler import (
    start_scheduler
)

app = FastAPI()


@app.on_event("startup")
def startup():

    start_scheduler() 


@app.get("/")
def health():

    return {
        "status": "running"
    }