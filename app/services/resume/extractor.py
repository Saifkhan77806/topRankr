import fitz


def extract_resume_text(filepath: str):

    try:
        with fitz.open(filepath) as doc:

            pages = len(doc)

            text = ""

            for page in doc:
                text += page.get_text()

            return {
                "filepath": filepath,
                "pages": pages,
                "text": text
            }

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None