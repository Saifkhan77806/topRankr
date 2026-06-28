def experience_score(
        jd,
        profile
):

    required = jd.get(
        "experience_years",
        0
    )

    actual = (
        profile
        .get(
            "professional",
            {}
        )
        .get(
            "total_experience_years",
            0
        )
    )

    if required == 0:
        return 100

    return min(
        (
            actual /
            required
        ) * 100,
        100
    )

def skill_score(
        jd,
        profile
):

    required = set(
        jd["skills"]["required"]
    )

    candidate_skills = set()

    skills = profile.get(
        "skills",
        {}
    )

    candidate_skills.update(
        skills.get(
            "technical",
            []
        )
    )

    candidate_skills.update(
        skills.get(
            "tools",
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
        profile
):

    jd_industry = (
        jd.get(
            "industry",
            ""
        )
        .lower()
    )

    candidate_industry = (
        profile
        .get(
            "professional",
            {}
        )
        .get(
            "industry",
            ""
        )
        .lower()
    )

    if jd_industry == candidate_industry:
        return 100

    return 0

def seniority_score(
        jd,
        profile
):

    jd_level = (
        jd.get(
            "seniority",
            ""
        )
        .lower()
    )

    candidate_level = (
        profile
        .get(
            "professional",
            {}
        )
        .get(
            "seniority",
            ""
        )
        .lower()
    )

    if jd_level == candidate_level:
        return 100

    return 0

def education_score(
        jd,
        profile
):

    jd_education = set(
        jd.get(
            "education",
            []
        )
    )

    candidate_education = set()

    education = profile.get(
        "education",
        []
    )

    for e in education:

        degree = e.get(
            "degree",
            ""
        )

        candidate_education.add(
            degree
        )

    if not jd_education:
        return 100

    matched = len(
        jd_education &
        candidate_education
    )

    return (
        matched /
        len(
            jd_education
        )
    ) * 100
    
    
def leadership_score(
        profile
):

    leadership_keywords = [

        "lead",

        "leader",

        "manager",

        "architect",

        "mentored",

        "managed"
    ]

    text = str(
        profile
    ).lower()

    score = 0

    for keyword in leadership_keywords:

        if keyword in text:
            score += 20

    return min(
        score,
        100
    )

def final_score(

        semantic,

        skills,

        experience,

        industry,

        seniority,

        education,

        leadership
):

    return (

        semantic * 0.40 +

        skills * 0.25 +

        experience * 0.10 +

        industry * 0.05 +

        seniority * 0.05 +

        education * 0.05 +

        leadership * 0.10
    )
    
def rank_candidates(
        jd,
        candidates
):

    ranked = []

    for candidate in candidates:

        profile = (
            candidate[
                "profile"
            ]
        )

        semantic = (
            candidate[
                "semantic_score"
            ] * 100
        )

        skills = skill_score(
            jd,
            profile
        )

        experience = (
            experience_score(
                jd,
                profile
            )
        )

        industry = (
            industry_score(
                jd,
                profile
            )
        )

        seniority = (
            seniority_score(
                jd,
                profile
            )
        )

        education = (
            education_score(
                jd,
                profile
            )
        )

        leadership = (
            leadership_score(
                profile
            )
        )

        candidate[
            "scores"
        ] = {

            "semantic":
                semantic,

            "skills":
                skills,

            "experience":
                experience,

            "industry":
                industry,

            "seniority":
                seniority,

            "education":
                education,

            "leadership":
                leadership
        }

        candidate[
            "ranking_score"
        ] = final_score(

            semantic,

            skills,

            experience,

            industry,

            seniority,

            education,

            leadership
        )

        ranked.append(
            candidate
        )

    ranked.sort(

        key=lambda x:
            x[
                "ranking_score"
            ],

        reverse=True
    )

    return ranked[:30]