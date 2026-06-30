from app.core.database import (
    SessionLocal
)

from app.models.search_job import (
    SearchJob
)

from app.models.search_result import (
    SearchResult
)

from app.models.candidate import (
    Candidate
)

from app.services.comparison.ai_comparison import (
    ai_compare_candidates
)


def compare_candidates(
        job_id,
        candidate_ids
):

    db = SessionLocal()

    try:

        job = (
            db.query(
                SearchJob
            )
            .filter(
                SearchJob.id == job_id
            )
            .first()
        )

        if not job:

            return {
                "error":
                    "Job not found"
            }

        results = (

            db.query(
                SearchResult,
                Candidate
            )

            .join(
                Candidate,
                Candidate.id ==
                SearchResult
                .candidate_id
            )

            .filter(
                SearchResult.job_id ==
                job_id,

                SearchResult
                .candidate_id
                .in_(
                    candidate_ids
                )
            )

            .all()
        )

        comparison = []

        for result, candidate in results:

            profile = (
                candidate.profile
            )

            comparison.append({

                "candidate_id":
                    candidate.id,

                "name":
                    candidate.name,

                "experience":
                    profile
                    .get(
                        "professional",
                        {}
                    )
                    .get(
                        "total_experience_years",
                        0
                    ),

                "industry":
                    profile
                    .get(
                        "professional",
                        {}
                    )
                    .get(
                        "industry",
                        ""
                    ),

                "seniority":
                    profile
                    .get(
                        "professional",
                        {}
                    )
                    .get(
                        "seniority",
                        ""
                    ),

                "skills":
                    profile
                    .get(
                        "skills",
                        {}
                    )
                    .get(
                        "technical",
                        []
                    ),

                "leadership":
                    result
                    .explanation
                    .get(
                        "reasons",
                        []
                    ),

                "semantic_score":
                    result
                    .semantic_score,

                "ranking_score":
                    result
                    .ranking_score,

                "ai_reason":
                    result
                    .ai_reason
            })

        ai_result = (
            ai_compare_candidates(
                job.result,
                comparison
            )
        )

        return {

            "job_id":
                job_id,

            "comparison":
                comparison,

            "winner":
                ai_result
        }

    finally:

        db.close()