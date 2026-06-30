import hashlib
import mimetypes
import os
import zipfile


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

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

ALLOWED_EXTENSIONS = (
    ".pdf",
    ".docx",
)

REJECTED_EXTENSIONS = (
    ".exe",
    ".bat",
    ".cmd",
    ".zip",
    ".rar",
    ".7z",
    ".js",
    ".vbs",
    ".msi",
    ".scr",
)

ALLOWED_MIME_TYPES = (
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
    extension = os.path.splitext(_normalize(filename))[1]

    if extension in REJECTED_EXTENSIONS:
        return False

    return extension in ALLOWED_EXTENSIONS


def validate_mime(filepath):
    guessed_mime, _ = mimetypes.guess_type(filepath)

    if guessed_mime not in ALLOWED_MIME_TYPES:
        return False

    extension = os.path.splitext(_normalize(filepath))[1]

    try:
        if extension == ".pdf":
            with open(filepath, "rb") as file:
                return file.read(4) == b"%PDF"

        if extension == ".docx":
            if not zipfile.is_zipfile(filepath):
                return False

            with zipfile.ZipFile(filepath) as archive:
                if "[Content_Types].xml" not in archive.namelist():
                    return False

                content_types = archive.read("[Content_Types].xml").decode(
                    "utf-8",
                    errors="ignore"
                )

                return (
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document"
                ) in content_types

    except Exception:
        return False

    return False


def validate_size(file_bytes):
    return len(file_bytes or b"") <= MAX_FILE_SIZE_BYTES


def calculate_resume_hash(file_bytes):
    return hashlib.sha256(file_bytes or b"").hexdigest()


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
