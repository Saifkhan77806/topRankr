from app.services.learning.preference_learning import (
    calculate_preference_score,
)

from app.services.learning.historical_jd_learning import (
    calculate_historical_score,
    calculate_hiring_success_score,
)


# ---------------------------------------------------------------------------
# Individual dimension scorers
# ---------------------------------------------------------------------------

def experience_score(jd, profile):

    required = jd.get("experience_years", 0)

    actual = (
        profile
        .get("professional", {})
        .get("total_experience_years", 0)
    )

    if required == 0:
        return 100

    return min((actual / required) * 100, 100)


def skill_score(jd, profile):

    required = set(jd["skills"]["required"])

    candidate_skills = set()

    skills = profile.get("skills", {})
    candidate_skills.update(skills.get("technical", []))
    candidate_skills.update(skills.get("tools", []))

    if not required:
        return 100

    matched = len(required & candidate_skills)
    return (matched / len(required)) * 100


def industry_score(jd, profile):

    jd_industry = jd.get("industry", "").lower()

    candidate_industry = (
        profile
        .get("professional", {})
        .get("industry", "")
        .lower()
    )

    if jd_industry == candidate_industry:
        return 100

    return 0


def seniority_score(jd, profile):

    jd_level = jd.get("seniority", "").lower()

    candidate_level = (
        profile
        .get("professional", {})
        .get("seniority", "")
        .lower()
    )

    if jd_level == candidate_level:
        return 100

    return 0


def education_score(jd, profile):

    jd_education = set(jd.get("education", []))

    candidate_education = set()
    for e in profile.get("education", []):
        degree = e.get("degree", "")
        candidate_education.add(degree)

    if not jd_education:
        return 100

    matched = len(jd_education & candidate_education)
    return (matched / len(jd_education)) * 100


def leadership_score(profile):

    leadership_keywords = [
        "lead",
        "leader",
        "manager",
        "architect",
        "mentored",
        "managed",
    ]

    text  = str(profile).lower()
    score = 0

    for keyword in leadership_keywords:
        if keyword in text:
            score += 20

    return min(score, 100)


# ---------------------------------------------------------------------------
# Base ranking score — same weighted formula as original
# ---------------------------------------------------------------------------

def base_ranking_score(
    semantic,
    skills,
    experience,
    industry,
    seniority,
    education,
    leadership,
):
    return (
        semantic    * 0.40 +
        skills      * 0.25 +
        experience  * 0.10 +
        industry    * 0.05 +
        seniority   * 0.05 +
        education   * 0.05 +
        leadership  * 0.10
    )


# ---------------------------------------------------------------------------
# Main ranking function — includes preference + historical boosting
# ---------------------------------------------------------------------------

def rank_candidates(
    jd,
    candidates,
    jd_embedding=None,
):
    """
    Score every candidate, apply preference and historical boosts,
    sort descending, and return the top 30.

    Boosted formula:
        boosted_score = ranking_score
                      + preference_score       (max +/-30)
                      + historical_score       (max +20)
                      + hiring_success_score   (max +10)
    """

    ranked = []

    for candidate in candidates:

        profile = candidate["profile"]

        semantic   = candidate["semantic_score"] * 100
        skills     = skill_score(jd, profile)
        experience = experience_score(jd, profile)
        industry   = industry_score(jd, profile)
        seniority  = seniority_score(jd, profile)
        education  = education_score(jd, profile)
        leadership = leadership_score(profile)

        base_score = base_ranking_score(
            semantic,
            skills,
            experience,
            industry,
            seniority,
            education,
            leadership,
        )

        preference_score = calculate_preference_score(profile)

        candidate_id = candidate.get("candidate_id") or candidate.get("id")

        if jd_embedding and candidate_id:
            historical_score     = calculate_historical_score(jd_embedding, candidate_id)
            hiring_success_score = calculate_hiring_success_score(candidate_id)
        else:
            historical_score     = 0.0
            hiring_success_score = 0.0

        boosted_score = (
            base_score
            + preference_score
            + historical_score
            + hiring_success_score
        )

        candidate["scores"] = {
            "semantic":             semantic,
            "skills":               skills,
            "experience":           experience,
            "industry":             industry,
            "seniority":            seniority,
            "education":            education,
            "leadership":           leadership,
            "preference_score":     preference_score,
            "historical_score":     historical_score,
            "hiring_success_score": hiring_success_score,
        }

        candidate["ranking_score"] = base_score
        candidate["boosted_score"] = boosted_score

        ranked.append(candidate)

    ranked.sort(
        key=lambda x: x["boosted_score"],
        reverse=True,
    )

    return ranked[:30]
