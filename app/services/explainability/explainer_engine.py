from app.services.explainability.explainer import (
    generate_explanation
)


def explain_candidates(
        jd_profile,
        candidates
):

    explanations = []

    for candidate in candidates:

        explanation = (
            generate_explanation(
                jd_profile,
                candidate
            )
        )

        candidate[
            "explanation"
        ] = explanation

        explanations.append(
            candidate
        )

    return explanations