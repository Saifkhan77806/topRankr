from app.workers.celery_worker import (celery_app)

from app.services.search_job.search_job_service import (update_job)

from app.services.jd.parser import (parse_job_description)

from app.services.jd.summary import (generate_jd_summary)

from app.services.jd.embedding import (create_jd_embedding)

from app.services.recruiter.faiss_search import (semantic_candidate_search)


@celery_app.task
def process_recruiter_search(job_id, job_description, top_k):
    try:
        # STEP 1
        update_job(job_id, "running", 10, "Parsing JD")

        jd_profile = parse_job_description(job_description)

        print("\nJD PROFILE")

        print(jd_profile)

        # STEP 2
        update_job(
            job_id,
            "running",
            20,
            "Generating Summary"
        )

        jd_summary = (
            generate_jd_summary(
                jd_profile
            )
        )

        print(
            "\nJD SUMMARY"
        )

        print(
            jd_summary
        )

        # STEP 3
        update_job(
            job_id,
            "running",
            30,
            "Generating Embedding"
        )

        embedding = (
            create_jd_embedding(
                jd_summary
            )
        )

        print(
            "\nEMBEDDING:",
            len(embedding)
        )

        # STEP 4
        update_job(
            job_id,
            "running",
            50,
            "Searching Candidates"
        )

        candidates = (
            semantic_candidate_search(
                embedding,
                requested_top_k=top_k
            )
        )

        print(
            "\nRetrieved:",
            len(candidates)
        )

        # TEMPORARY
        update_job(
            job_id,
            "completed",
            100,
            "Completed"
        )

        return candidates

    except Exception as e:

        update_job(
            job_id,
            "failed",
            100,
            str(e)
        )

        raise