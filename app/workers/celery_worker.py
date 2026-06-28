from celery import Celery

celery_app = Celery(
    "toprankr",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.workers.resume_tasks", 
        "app.workers.recruiter_tasks"
        ]
)
