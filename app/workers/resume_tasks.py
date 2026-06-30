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

from app.services.security.email_security import (
    SPAM_SCORE_THRESHOLD,
    detect_prompt_injection,
    spam_score,
    validate_candidate_email,
)

from app.services.security.resume_security import (
    calculate_resume_hash,
    validate_extension,
    validate_mime,
    validate_size
)

from app.services.security.candidate_security_service import (
    duplicate_resume_exists,
    save_candidate_security_record
)


def log_security(message):

    print(message)


def reject_candidate_attachment(
        email,
        resume_hash,
        score,
        prompt_injection,
        duplicate_resume,
        reason
):

    save_candidate_security_record(
        candidate_email=email.get("from"),
        resume_hash=resume_hash,
        spam_score=score,
        prompt_injection=prompt_injection,
        duplicate_resume=duplicate_resume,
        virus_scan="not_scanned",
        allowed=False,
        rejection_reason=reason
    )

    log_security("SECURITY FAILED")

    if reason in (
            "invalid_attachment",
            "invalid_mime_type",
            "oversized_file",
            "non_resume_attachment"
    ):
        log_security("INVALID ATTACHMENT")

    if duplicate_resume:
        log_security("DUPLICATE RESUME DETECTED")

    if prompt_injection:
        log_security("PROMPT INJECTION DETECTED")

    if score > SPAM_SCORE_THRESHOLD:
        log_security("SPAM DETECTED")



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

        resume_hash = None
        score = 0
        prompt_injection = False
        duplicate_resume = False

        if not validate_candidate_email(email):
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="invalid_candidate_email"
            )
            continue

        if not validate_extension(attachment):
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="invalid_attachment"
            )
            continue

        try:
            with open(attachment, "rb") as file:
                file_bytes = file.read()
        except Exception:
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="attachment_read_failed"
            )
            continue

        if not validate_size(file_bytes):
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="oversized_file"
            )
            continue

        if not validate_mime(attachment):
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="invalid_mime_type"
            )
            continue

        resume_hash = calculate_resume_hash(file_bytes)
        duplicate_resume = duplicate_resume_exists(resume_hash)

        if duplicate_resume:
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="duplicate_resume"
            )
            continue

        # STEP 1
        resume = extract_resume_text(attachment)

        if not resume:
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="non_resume_attachment"
            )
            continue

        resume_text = resume["text"]

        prompt_injection = detect_prompt_injection(resume_text)
        score = spam_score(
            f"{email.get('subject', '')}\n{resume_text}"
        )

        if prompt_injection:
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="prompt_injection"
            )
            continue

        if score > SPAM_SCORE_THRESHOLD:
            reject_candidate_attachment(
                email=email,
                resume_hash=resume_hash,
                score=score,
                prompt_injection=prompt_injection,
                duplicate_resume=duplicate_resume,
                reason="spam_detected"
            )
            continue

        save_candidate_security_record(
            candidate_email=email.get("from"),
            resume_hash=resume_hash,
            spam_score=score,
            prompt_injection=prompt_injection,
            duplicate_resume=duplicate_resume,
            virus_scan="not_scanned",
            allowed=True,
            rejection_reason=None
        )

        log_security("SECURITY PASSED")

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
