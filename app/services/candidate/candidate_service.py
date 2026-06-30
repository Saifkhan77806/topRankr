from app.core.database import (
    SessionLocal
)

from app.models.candidate import (
    Candidate
)


def save_candidate(profile, summary, resume_path):

    db = SessionLocal()

    candidate = Candidate(
        name=profile.get("personal", {}).get("name"),

        email=profile.get("personal",{}).get("email"),

        phone=profile.get("personal",{}).get("phone"),

        current_title=profile.get("professional",{}).get("current_title"),

        experience_years=profile.get("professional",{}).get("total_experience_years",0),

        industry=profile
            .get(
                "professional",
                {}
            )
            .get(
                "industry"
            ),

        profile=profile,

        summary=summary,

        resume_path=resume_path
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    db.close()

    return candidate



def get_resume(
        candidate_id
):

    db = SessionLocal()

    try:

        candidate = (

            db.query(
                Candidate
            )

            .filter(
                Candidate.id ==
                candidate_id
            )

            .first()
        )

        if not candidate:
            return None

        return {

            "candidate_id":
                candidate.id,

            "name":
                candidate.name,

            "resume_path":
                candidate.resume_path
        }

    finally:
        db.close()



def get_candidate_details(
        candidate_id
):

    db = SessionLocal()

    try:

        candidate = (
            db.query(
                Candidate
            )
            .filter(
                Candidate.id ==
                candidate_id
            )
            .first()
        )

        if not candidate:
            return None

        return {

            "id":
                candidate.id,

            "name":
                candidate.name,

            "email":
                candidate.email,

            "phone":
                candidate.phone,

            "current_title":
                candidate.current_title,

            "experience_years":
                candidate.experience_years,

            "industry":
                candidate.industry,

            "summary":
                candidate.summary,

            "resume_path":
                candidate.resume_path,

            "profile":
                candidate.profile
        }

    finally:

        db.close()

