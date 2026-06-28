from app.services.jd.parser import (parse_job_description)

from app.services.jd.summary import (generate_jd_summary)

from app.services.jd.embedding import (create_jd_embedding)

jd = """
        Looking for a Senior AI Engineer
        with 3+ years experience in
        Python, FastAPI, LLMs,
        Docker and AWS.
    """

parsed = parse_job_description(jd)

print("\n==== JD PROFILE ====")

print(parsed)

summary = generate_jd_summary(parsed)

print("\n==== JD SUMMARY ====")

print(summary)

embedding = create_jd_embedding(summary)

print("\n==== EMBEDDING ====")

print(len(embedding))

print(embedding[:10])