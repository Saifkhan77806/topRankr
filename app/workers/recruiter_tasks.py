from app.workers.celery_worker import celery_app

from app.services.search_job.search_job_service import update_job

from app.services.jd.parser import parse_job_description

from app.services.jd.summary import generate_jd_summary

from app.services.jd.embedding import create_jd_embedding

from app.services.recruiter.faiss_search import semantic_candidate_search

from app.services.ranking.scorer import rank_candidates

from app.services.reranking.qwen_reranker import rerank_candidates

from app.services.explainability.explainer_engine import explain_candidates

from app.services.search_results.result_service import save_search_results

from app.services.recommendation.recommendation_engine import recommend_candidates

from app.workers.learning_tasks import task_store_job_embedding


@celery_app.task
def process_recruiter_search(
        job_id,
        job_description,
        top_k
):

    try:

        ##################################################
        # STEP 1 — Parse JD
        ##################################################

        update_job(job_id, "running", 10, "Parsing JD")

        jd_profile = parse_job_description(job_description)

        print("\n========== JD PROFILE ==========")
        print(jd_profile)

        ##################################################
        # STEP 2 — Generate Summary
        ##################################################

        update_job(job_id, "running", 20, "Generating Summary")

        jd_summary = generate_jd_summary(jd_profile)

        print("\n========== JD SUMMARY ==========")
        print(jd_summary)

        ##################################################
        # STEP 3 — Generate Embedding
        ##################################################

        update_job(job_id, "running", 30, "Generating Embedding")

        embedding = create_jd_embedding(jd_summary)

        print("\n========== EMBEDDING ==========")
        print(len(embedding))

        ##################################################
        # STEP 4 — Search Candidates
        ##################################################

        update_job(job_id, "running", 50, "Searching Candidates")

        candidates = semantic_candidate_search(
            embedding,
            requested_top_k=100
        )

        print("\n========== RETRIEVED ==========")
        print(len(candidates))

        ##################################################
        # STEP 5 — Rank Candidates (with boosted score)
        ##################################################

        update_job(job_id, "running", 70, "Ranking Candidates")

        ranked = rank_candidates(
            jd_profile,
            candidates,
            jd_embedding=embedding,
        )

        ranked = ranked[:30]

        print("\n========== TOP 30 ==========")
        for candidate in ranked:
            print()
            print("NAME:",    candidate["name"])
            print("EMAIL:",   candidate.get("email", "N/A"))
            print("SCORES:")
            print(candidate["scores"])
            print("BASE:",    candidate["ranking_score"])
            print("BOOSTED:", candidate["boosted_score"])

        ##################################################
        # STEP 6 — AI Re-ranking
        ##################################################

        update_job(job_id, "running", 85, "AI Re-ranking")

        reranked = rerank_candidates(
            jd_profile,
            ranked,
            top_k=top_k
        )

        print("\n========== QWEN RERANK ==========")
        for candidate in reranked:
            print()
            print("RANK:",      candidate["rank"])
            print("CANDIDATE:", candidate["candidate_id"])
            print("REASON:")
            print(candidate["reason"])

        ##################################################
        # STEP 7 — Generate Explanations
        ##################################################

        update_job(job_id, "running", 92, "Generating Explanations")

        ranked_lookup = {
            candidate["candidate_id"]: candidate
            for candidate in ranked
        }

        final_candidates = []

        for reranked_candidate in reranked:
            candidate = ranked_lookup.get(reranked_candidate["candidate_id"])
            if candidate:
                candidate["ai_rank"]   = reranked_candidate["rank"]
                candidate["ai_reason"] = reranked_candidate["reason"]
                final_candidates.append(candidate)

        explained = explain_candidates(jd_profile, final_candidates)

        ##################################################
        # STEP 8 — Generate Recommendations
        ##################################################

        update_job(job_id, "running", 95, "Generating Recommendations")

        explained = recommend_candidates(explained)

        ##################################################
        # STEP 9 — Save Results
        ##################################################

        update_job(job_id, "running", 97, "Saving Results")

        save_search_results(job_id, explained)

        ##################################################
        # STEP 9.5 — Store JD Embedding (async, non-blocking)
        ##################################################

        task_store_job_embedding.delay(
            job_id=job_id,
            embedding=embedding,
        )

        ##################################################
        # COMPLETE
        ##################################################

        update_job(job_id, "completed", 100, "Completed")

        print("\n========== EXPLAINABILITY ==========")
        for candidate in explained:
            print()
            print("RANK:",    candidate["ai_rank"])
            print("NAME:",    candidate["name"])
            print("AI REASON:")
            print(candidate["ai_reason"])
            print("EXPLANATION:")
            for reason in candidate["explanation"]["reasons"]:
                print("✓", reason)

        return explained

    except Exception as e:

        update_job(job_id, "failed", 100, str(e))
        raise
