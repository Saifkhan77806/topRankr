def generate_explanation(jd_profile, candidate):
    reasons = []
    profile = candidate["profile"]

    #################################################
    # REQUIRED SKILLS
    #################################################

    required_skills = set(jd_profile.get("skills", {}).get("required", []))

    candidate_skills = set()

    skills = profile.get("skills", {})

    candidate_skills.update(skills.get("technical", []))

    candidate_skills.update(skills.get("tools", []))

    matched = (required_skills &candidate_skills)

    for skill in matched:
        reasons.append(f"Strong {skill} experience")

    #################################################
    # EXPERIENCE
    #################################################

    candidate_experience = (profile.get("professional", {}).get("total_experience_years", 0))

    required_experience = (jd_profile.get("experience_years", 0))

    if candidate_experience >= required_experience:
        reasons.append(
            f"{candidate_experience} years "
            "of relevant experience"
        )

    #################################################
    # LEADERSHIP
    #################################################

    leadership_score = (candidate["scores"].get("leadership", 0))

    if leadership_score >= 60:

        reasons.append("Leadership experience")

    #################################################
    # INDUSTRY
    #################################################

    candidate_industry = (profile.get("professional", {}).get("industry",""))

    if candidate_industry:
        reasons.append(f"{candidate_industry} domain experience")

    #################################################
    # SENIORITY
    #################################################

    seniority = (
        profile
        .get(
            "professional",
            {}
        )
        .get(
            "seniority",
            ""
        )
    )

    if seniority:

        reasons.append(
            f"{seniority} level engineer"
        )

    #################################################
    # FALLBACK
    #################################################

    if not reasons:

        reasons.append(
            "Good overall candidate fit"
        )

    return {

        "candidate_id":
            candidate[
                "candidate_id"
            ],

        "score":
            round(
                candidate[
                    "ranking_score"
                ],
                2
            ),

        "reasons":
            reasons[:7]
    }