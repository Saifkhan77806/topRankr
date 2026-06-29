def get_recommendation(
        candidate
):

    score = candidate.get(
        "ranking_score",
        0
    )

    semantic = (
        candidate
        .get(
            "scores",
            {}
        )
        .get(
            "semantic",
            0
        )
    )

    leadership = (
        candidate
        .get(
            "scores",
            {}
        )
        .get(
            "leadership",
            0
        )
    )

    ##################################################
    # Excellent Match
    ##################################################

    if (
        score >= 90
        and semantic >= 85
    ):

        return (
            "Excellent Match"
        )

    ##################################################
    # Strong Match
    ##################################################

    if score >= 75:

        return (
            "Strong Match"
        )

    ##################################################
    # Good Match
    ##################################################

    if score >= 60:

        return (
            "Good Match"
        )

    ##################################################
    # Potential Match
    ##################################################

    if (
        score >= 45
        or leadership >= 60
    ):

        return (
            "Potential Match"
        )

    ##################################################
    # Reject
    ##################################################

    return (
        "Not Recommended"
    )


def recommend_candidates(
        candidates
):

    for candidate in candidates:

        candidate[
            "recommendation"
        ] = get_recommendation(
            candidate
        )

    return candidates