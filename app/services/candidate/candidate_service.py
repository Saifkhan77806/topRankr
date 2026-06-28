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