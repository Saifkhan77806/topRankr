import hashlib
import mimetypes
import os
import zipfile


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = (
    ".pdf",
    ".docx",
)

REJECTED_EXTENSIONS = (
    ".exe",
    ".bat",
    ".cmd",
    ".scr",
    ".vbs",
    ".js",
    ".zip",
    ".rar",
    ".7z",
)

ALLOWED_MIME_TYPES = (
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)


def _extension(filename):
    return os.path.splitext((filename or "").lower().strip())[1]


def validate_extension(filename):
    extension = _extension(filename)

    if extension in REJECTED_EXTENSIONS:
        return False

    return extension in ALLOWED_EXTENSIONS


def validate_size(file_bytes):
    return len(file_bytes or b"") <= MAX_FILE_SIZE_BYTES


def validate_mime(filepath):
    guessed_mime, _ = mimetypes.guess_type(filepath)

    if guessed_mime not in ALLOWED_MIME_TYPES:
        return False

    extension = _extension(filepath)

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


def calculate_resume_hash(file_bytes):
    return hashlib.sha256(file_bytes or b"").hexdigest()
