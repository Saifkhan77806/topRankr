from app.services.jd.parser import ( parse_job_description )

from app.services.jd.summary import ( generate_jd_summary )

from app.services.jd.embedding import ( create_jd_embedding )

from app.services.recruiter.faiss_search import ( semantic_candidate_search )


jd = """
        Looking for an AI Engineer
        with Python,
        FastAPI,
        LLM experience.
    """

profile = parse_job_description(jd)

summary = generate_jd_summary(profile)

embedding = create_jd_embedding(summary)

results = semantic_candidate_search(embedding, top_k=10)

for candidate in results:
    print()
    print(candidate["name"])
    print(candidate["semantic_score"])