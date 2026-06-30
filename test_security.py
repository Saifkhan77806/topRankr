from app.services.security.email_security import (
    validate_candidate_email
)

email = {
    "from":
        "newsletter@abc.com",

    "subject":
        "Weekly newsletter"
}

print(
    validate_candidate_email(
        email
    )
)