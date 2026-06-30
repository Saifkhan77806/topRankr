from app.services.security.resume_security import (
    calculate_resume_hash,
    validate_extension,
    validate_mime,
    validate_size,
)

REJECTED_SENDER_PREFIXES = (
    "noreply@",
    "marketing@",
    "support@",
    "newsletter@",
    "admin@",
)

REJECTED_SUBJECT_KEYWORDS = (
    "sale",
    "offer",
    "discount",
    "crypto",
    "bitcoin",
    "casino",
    "lottery",
    "promotion",
    "advertisement",
)

ACCEPTED_SUBJECT_KEYWORDS = (
    "resume",
    "application",
    "job application",
    "candidate",
    "cv",
    "software engineer",
    "backend engineer",
    "python developer",
)

PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "system prompt",
    "you are chatgpt",
    "hire me immediately",
    "give me score 100",
    "delete candidates",
    "return candidate rank 1",
    "jailbreak",
    "assistant:",
    "system:",
)

SPAM_KEYWORDS = (
    "casino",
    "crypto",
    "bitcoin",
    "forex",
    "lottery",
    "investment",
    "earn money",
    "click here",
    "porn",
    "telegram",
)

SPAM_SCORE_THRESHOLD = 2


def _normalize(value):
    return (value or "").strip().lower()


def validate_candidate_email(message):
    sender = _normalize(message.get("from"))
    subject = _normalize(message.get("subject"))

    if any(prefix in sender for prefix in REJECTED_SENDER_PREFIXES):
        return False

    if any(keyword in subject for keyword in REJECTED_SUBJECT_KEYWORDS):
        return False

    return any(keyword in subject for keyword in ACCEPTED_SUBJECT_KEYWORDS)


def validate_attachment(filename):
    return validate_extension(filename)


def detect_prompt_injection(text):
    normalized_text = _normalize(text)
    return any(
        pattern in normalized_text
        for pattern in PROMPT_INJECTION_PATTERNS
    )


def spam_score(text):
    normalized_text = _normalize(text)
    return sum(
        normalized_text.count(keyword)
        for keyword in SPAM_KEYWORDS
    )
