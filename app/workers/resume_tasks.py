from app.workers.celery_worker import celery_app
from app.services.resume.extractor import extract_resume_text
from app.services.llm.openrouter_service import parseResumeWithLlm
from app.services.summary.candidate_summary import generate_candidate_summary
from app.services.embedding.bge_embedding import createEmbedding
from app.services.candidate.candidate_service import (
    save_candidate
)

from app.vectorstore.faiss_manager import (
    add_candidate
)



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

        # STEP 1
        resume = extract_resume_text(attachment)

        if not resume:
            continue

        resume_text = resume["text"]

        print("\n===== EXTRACTED TEXT =====")

        print(resume_text[:500])

        # STEP 2
        candidate_profile = parseResumeWithLlm(resume_text)

        print("\n===== CANDIDATE PROFILE =====")

        print(candidate_profile)

        # STEP 3
        summary = generate_candidate_summary(candidate_profile)
        

        print("\n===== CANDIDATE SUMMARY =====")

        print(summary)

        # STEP 4
        embedding = createEmbedding(summary)

        print("\n===== EMBEDDING =====")

        print("Dimension:",len(embedding))

        print(embedding[:10])
        
        candidate = save_candidate(
        profile=candidate_profile,
        summary=summary,
        resume_path=attachment
    )

    print(
        "\nCandidate ID:",
        candidate.id
    )

    add_candidate(
        candidate.id,
        embedding
    )

    print(
        "\nStored in FAISS"
    )

    print("\n=============================")