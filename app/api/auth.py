from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from pydantic import BaseModel, EmailStr

from app.core.database import SessionLocal
from app.core.password import (
    hash_password,
    verify_password,
)
from app.core.security import (
    create_access_token,
    get_current_user,
)
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

ALLOWED_ROLES = {
    "admin",
    "recruiter"
}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "recruiter"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def _token_response(user):
    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }


@router.post("/register")
def register(request: RegisterRequest):
    role = request.role.lower().strip()

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            role=role,
            active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return _token_response(user)

    finally:
        db.close()


@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if not user or not verify_password(
                request.password,
                user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )

        return _token_response(user)

    finally:
        db.close()


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "active": current_user.active,
        "created_at": current_user.created_at
    }
