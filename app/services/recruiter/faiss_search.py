from app.vectorstore.faiss_manager import (search_candidates)

from app.services.candidate.search_service import (get_candidates)


def semantic_candidate_search(
        jd_embedding,
        requested_top_k=20
):

    faiss_results = (
        search_candidates(
            jd_embedding,
            requested_top_k
        )
    )

    candidate_ids = [

        x["candidate_id"]

        for x in faiss_results
    ]

    candidates = get_candidates(
        candidate_ids
    )

    candidate_map = {

        candidate.id:
            candidate

        for candidate in candidates
    }

    results = []

    for result in faiss_results:

        candidate = candidate_map.get(
            result["candidate_id"]
        )

        if not candidate:
            continue

        results.append({

            "candidate_id":
                candidate.id,

            "name":
                candidate.name,
                
            "email": candidate.email,

            "title":
                candidate.current_title,

            "industry":
                candidate.industry,

            "summary":
                candidate.summary,

            "profile":
                candidate.profile,

            "semantic_score":
                result[
                    "semantic_score"
                ]
        })

    return results
