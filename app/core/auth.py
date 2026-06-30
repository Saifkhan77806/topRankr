from fastapi import (
    Depends,
    HTTPException,
    status,
)

from app.core.security import get_current_user


def admin_required(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )

    return current_user


def recruiter_required(current_user=Depends(get_current_user)):
    if current_user.role not in (
            "admin",
            "recruiter"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter role required"
        )

    return current_user
