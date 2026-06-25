from app.core.database import (
    SessionLocal
)

from app.models.search_result import (
    SearchResult
)


def save_search_results(
        job_id,
        candidates
):

    db = SessionLocal()

    try:

        for candidate in candidates:

            result = SearchResult(

                job_id=job_id,

                candidate_id=
                    candidate[
                        "candidate_id"
                    ],

                rank=
                    candidate.get(
                        "ai_rank",
                        0
                    ),

                semantic_score=
                    candidate[
                        "scores"
                    ][
                        "semantic"
                    ],

                ranking_score=
                    candidate[
                        "ranking_score"
                    ],

                recommendation=
                    candidate.get(
                        "recommendation"
                    ),

                ai_reason=
                    candidate.get(
                        "ai_reason"
                    ),

                explanation=
                    candidate.get(
                        "explanation"
                    )
            )

            db.add(
                result
            )

        db.commit()

    finally:

        db.close()