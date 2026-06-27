from fastapi import APIRouter

from app.services.gmail_reader_service import get_latest_candidate_email
from app.workers.resume_tasks import process_candidate_email

router = APIRouter()

@router.post("/gmail-webhook")
async def gmail_webhook(payload: dict):
    print("GMAIL PUSH RECEIVED")

    email_data = get_latest_candidate_email(None)

    if email_data:
        process_candidate_email.delay(email_data)

    return {"status": "queued"}
