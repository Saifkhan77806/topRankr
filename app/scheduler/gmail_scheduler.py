from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.services.gmail_service import (
    check_candidate_emails
)

scheduler = BackgroundScheduler()


def start_scheduler():

    scheduler.add_job(
        check_candidate_emails,
        "interval",
        seconds=30
    )

    scheduler.start()

    print(
        "Gmail polling started"
    )
    
