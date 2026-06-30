import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.scheduler.gmail_scheduler import ( start_scheduler )
from app.api.recruiter import ( router as recruiter_router )
from app.api.candidate import (
    router as candidate_router
)
from app.api.auth import (
    router as auth_router
)
from app.core.rate_limit import limiter

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

from app.api.comparison import (
    router as comparison_router
)

app.include_router(auth_router)
app.include_router(recruiter_router)
app.include_router(candidate_router)
app.include_router(comparison_router)


@app.on_event("startup")
def startup():

    start_scheduler() 




@app.get("/")
def health():

    return {
        "status": "running"
    }
