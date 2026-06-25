from app.core.database import (
    SessionLocal
)

from app.models.search_result import (
    SearchResult
)

from app.models.search_job import SearchJob
from app.models.search_result import SearchResult
from app.models.candidate import Candidate


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


def get_search_results(
        job_id: int
):

    db = SessionLocal()

    try:

        job = (
            db.query(SearchJob)
            .filter(
                SearchJob.id == job_id
            )
            .first()
        )

        if not job:
            return None

        results = (
            db.query(
                SearchResult,
                Candidate
            )
            .join(
                Candidate,
                Candidate.id ==
                SearchResult.candidate_id
            )
            .filter(
                SearchResult.job_id ==
                job_id
            )
            .order_by(
                SearchResult.rank
            )
            .all()
        )

        response = []

        for result, candidate in results:

            response.append({

                "rank":
                    result.rank,

                "candidate_id":
                    candidate.id,

                "name":
                    candidate.name,

                "email":
                    candidate.email,

                "resume_path":
                    candidate.resume_path,

                "semantic_score":
                    result.semantic_score,

                "ranking_score":
                    result.ranking_score,

                "ai_reason":
                    result.ai_reason,

                "explanation":
                    result.explanation
            })

        return {

            "job_id":
                job.id,

            "status":
                job.status,

            "progress":
                job.progress,

            "results":
                response
        }

    finally:
        db.close()