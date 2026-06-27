from app.workers.celery_worker import celery_app
from app.services.resume.extractor import extract_resume_text



@celery_app.task
def process_candidate_email(email):

    print("\n========== CANDIDATE ==========")

    print("FROM:")
    print(email["from"])

    print("\nSUBJECT:")
    print(email["subject"])

    print("\nATTACHMENTS:")

    for attachment in email["attachments"]:
        print(attachment)
        
        resume = extract_resume_text(attachment)

        if resume is None:
            print("Resume extraction failed")
            continue

        print("\n===== EXTRACTED TEXT =====")
        print("Pages:", resume["pages"])
        print(resume["text"][:1000])
        print("==========================")

    print("==============================\n")