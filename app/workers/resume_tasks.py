from app.workers.celery_worker import celery_app
from app.services.resume.extractor import extract_resume_text
from app.services.llm.openrouter_service import parseResumeWithLlm



@celery_app.task
def process_candidate_email(email):

    print("\n========== CANDIDATE ==========")

    print(email["from"])

    for attachment in email["attachments"]:

        resume = extract_resume_text(attachment)

        if not resume:
            continue

        resume_text = resume["text"]

        print("\n===== RESUME TEXT =====")
        print(resume_text[:500])

        candidate = (
            parseResumeWithLlm(resume_text)
        )

        print("\n===== CANDIDATE PROFILE =====")
        print(candidate)

        print("=============================")
 
