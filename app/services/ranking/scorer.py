def experience_score(
        jd,
        candidate
):

    required = (
        jd.get(
            "experience_years",
            0
        )
    )

    actual = (
        candidate.get(
            "experience_years",
            0
        )
    )

    if required == 0:
        return 100

    return min(
        actual /
        required * 100,
        100
    )

def skill_score(
        jd,
        candidate
):

    required = set(
        jd["skills"]["required"]
    )

    candidate_skills = set(
        candidate.get(
            "skills",
            []
        )
    )

    if not required:
        return 100

    matched = len(
        required &
        candidate_skills
    )

    return (
        matched /
        len(required)
    ) * 100

def industry_score(
        jd,
        candidate
):

    if (
        jd.get(
            "industry",
            ""
        ).lower()
        ==
        candidate.get(
            "industry",
            ""
        ).lower()
    ):
        return 100

    return 0

def seniority_score(
        jd,
        candidate
):

    if (
        jd.get(
            "seniority",
            ""
        ).lower()
        ==
        candidate.get(
            "seniority",
            ""
        ).lower()
    ):
        return 100

    return 0

def final_score(semantic, skills, experience, industry, seniority):
    return (
        semantic * 0.50 +
        skills * 0.25 +
        experience * 0.15 +
        industry * 0.05 +
        seniority * 0.05
    )
    
def rank_candidates(jd_profile, candidates):
    ranked = []


    for candidate in candidates:
        semantic = candidate["semantic_score"] * 100

        skills = skill_score(jd_profile, candidate["profile"])

        experience = experience_score(jd_profile, candidate["profile"])

        industry = industry_score(jd_profile, candidate["profile"])

        seniority = seniority_score(jd_profile, candidate["profile"])

        score = final_score(semantic, skills, experience, industry, seniority)

        candidate["ranking_score"] = score
        
        print()

        print(
            candidate["name"]
        )

        print(
            candidate["profile"]
        )

        ranked.append(candidate)

    ranked.sort(
        key=lambda x:x["ranking_score"],
        reverse=True
        )
    
    return ranked