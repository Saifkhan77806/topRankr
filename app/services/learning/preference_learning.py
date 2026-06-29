from app.core.database import SessionLocal
from app.models.recruiter_preferences import RecruiterPreference
from app.models.candidate import Candidate


# ---------------------------------------------------------------------------
# Weight constants
# ---------------------------------------------------------------------------

WEIGHT_HIRED       = 10.0
WEIGHT_INTERVIEWED = 5.0
WEIGHT_SHORTLISTED = 3.0
WEIGHT_REJECTED    = -8.0

MAX_FEATURE_WEIGHT =  50.0
MIN_FEATURE_WEIGHT = -50.0

PREFERENCE_SCORE_CAP = 30.0


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_features(profile: dict) -> dict:
    """
    Pull every learnable feature out of a candidate profile JSON.
    Returns a dict keyed by feature_type -> list of normalised strings.
    """

    features = {
        "skill":      [],
        "industry":   [],
        "seniority":  [],
        "domain":     [],
        "education":  [],
        "leadership": [],
        "experience": [],
    }

    # --- skills (technical + tools) ---
    skills = profile.get("skills", {})
    for skill in skills.get("technical", []):
        features["skill"].append(str(skill).lower().strip())
    for tool in skills.get("tools", []):
        features["skill"].append(str(tool).lower().strip())

    # --- industry ---
    industry = (
        profile
        .get("professional", {})
        .get("industry", "")
    )
    if industry:
        features["industry"].append(industry.lower().strip())

    # --- seniority ---
    seniority = (
        profile
        .get("professional", {})
        .get("seniority", "")
    )
    if seniority:
        features["seniority"].append(seniority.lower().strip())

    # --- domain expertise ---
    domains = (
        profile
        .get("professional", {})
        .get("domain_expertise", [])
    )
    for domain in domains:
        features["domain"].append(str(domain).lower().strip())

    # --- education (degree level) ---
    for edu in profile.get("education", []):
        degree = edu.get("degree", "")
        if degree:
            features["education"].append(degree.lower().strip())

    # --- leadership ---
    leadership = profile.get("leadership", {})
    if leadership.get("has_leadership"):
        features["leadership"].append("leadership")
    if leadership.get("management_experience"):
        features["leadership"].append("management")

    # --- experience bucket ---
    exp = (
        profile
        .get("professional", {})
        .get("total_experience_years", 0)
    ) or 0
    if exp <= 2:
        features["experience"].append("junior")
    elif exp <= 5:
        features["experience"].append("mid-level")
    elif exp <= 10:
        features["experience"].append("senior")
    else:
        features["experience"].append("principal")

    return features


def _upsert_preference(
    db,
    feature_name: str,
    feature_type: str,
    delta_positive: int,
    delta_negative: int,
    weight_delta: float,
):
    """
    Find or create the RecruiterPreference row for this feature,
    then apply the deltas in-place.
    """

    row = (
        db.query(RecruiterPreference)
        .filter(
            RecruiterPreference.feature_name == feature_name,
            RecruiterPreference.feature_type == feature_type,
        )
        .first()
    )

    if not row:
        row = RecruiterPreference(
            feature_name=feature_name,
            feature_type=feature_type,
            weight=0.0,
            positive_count=0,
            negative_count=0,
        )
        db.add(row)

    row.positive_count += delta_positive
    row.negative_count += delta_negative
    row.weight = max(
        MIN_FEATURE_WEIGHT,
        min(
            MAX_FEATURE_WEIGHT,
            row.weight + weight_delta,
        ),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def update_feature_weight(
    feature_name: str,
    feature_type: str,
    feedback_type: str,
):
    """
    Increment/decrement the weight for a single feature based on one
    feedback signal.

    feedback_type: "hired" | "interviewed" | "shortlisted" | "rejected"
    """

    weight_map = {
        "hired":       WEIGHT_HIRED,
        "interviewed": WEIGHT_INTERVIEWED,
        "shortlisted": WEIGHT_SHORTLISTED,
        "rejected":    WEIGHT_REJECTED,
    }

    weight_delta   = weight_map.get(feedback_type, 0.0)
    is_positive    = feedback_type != "rejected"
    delta_positive = 1 if is_positive else 0
    delta_negative = 1 if not is_positive else 0

    db = SessionLocal()
    try:
        _upsert_preference(
            db,
            feature_name=feature_name,
            feature_type=feature_type,
            delta_positive=delta_positive,
            delta_negative=delta_negative,
            weight_delta=weight_delta,
        )
        db.commit()
    finally:
        db.close()


def learn_from_feedback(
    job_id: int,
    candidate_id: int,
    feedback_type: str,
):
    """
    Pull the candidate profile, extract all learnable features,
    and update weights for each one.

    Called automatically after every POST /recruiter/feedback.
    """

    db = SessionLocal()
    try:
        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == candidate_id)
            .first()
        )

        if not candidate or not candidate.profile:
            return

        profile  = candidate.profile
        features = _extract_features(profile)

        weight_map = {
            "hired":       WEIGHT_HIRED,
            "interviewed": WEIGHT_INTERVIEWED,
            "shortlisted": WEIGHT_SHORTLISTED,
            "rejected":    WEIGHT_REJECTED,
        }

        weight_delta = weight_map.get(feedback_type, 0.0)
        is_positive  = feedback_type != "rejected"

        for feature_type, feature_list in features.items():
            for feature_name in feature_list:
                if not feature_name:
                    continue
                _upsert_preference(
                    db,
                    feature_name=feature_name,
                    feature_type=feature_type,
                    delta_positive=1 if is_positive else 0,
                    delta_negative=1 if not is_positive else 0,
                    weight_delta=weight_delta,
                )

        db.commit()

    finally:
        db.close()


def calculate_preference_score(profile: dict) -> float:
    """
    Given a candidate profile dict, look up every feature in
    recruiter_preferences and sum up the learned weights.

    Returns a score capped at PREFERENCE_SCORE_CAP (30).
    """

    features = _extract_features(profile)

    pairs = []
    for feature_type, feature_list in features.items():
        for feature_name in feature_list:
            if feature_name:
                pairs.append((feature_name, feature_type))

    if not pairs:
        return 0.0

    db = SessionLocal()
    try:
        total_weight = 0.0

        for feature_name, feature_type in pairs:
            row = (
                db.query(RecruiterPreference)
                .filter(
                    RecruiterPreference.feature_name == feature_name,
                    RecruiterPreference.feature_type == feature_type,
                )
                .first()
            )
            if row:
                total_weight += row.weight

        n_features = max(len(pairs), 1)
        normalised = total_weight / n_features

        # map average weight [-50, +50] -> [-PREFERENCE_SCORE_CAP, +PREFERENCE_SCORE_CAP]
        score = (normalised / 50.0) * PREFERENCE_SCORE_CAP

        return max(-PREFERENCE_SCORE_CAP, min(PREFERENCE_SCORE_CAP, score))

    finally:
        db.close()
