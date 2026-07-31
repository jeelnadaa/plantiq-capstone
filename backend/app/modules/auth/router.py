from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.models import User, AuthToken
from app.modules.auth.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.modules.auth.security import (
    hash_password,
    verify_password,
    generate_token,
    get_current_user,
    get_token_from_header
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user account and returns bearer token."""
    existing_email = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    existing_user = db.query(User).filter(User.username == payload.username.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken.")

    new_user = User(
        email=payload.email.lower(),
        username=payload.username.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name or payload.username
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate Token
    token_str = generate_token()
    auth_token = AuthToken(token=token_str, user_id=new_user.id)
    db.add(auth_token)
    db.commit()

    return TokenResponse(
        access_token=token_str,
        user=UserResponse.from_orm(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user with email/username + password and returns bearer token."""
    query = payload.email_or_username.lower()
    user = db.query(User).filter(
        (User.email == query) | (User.username == query)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email/username or password.")

    # Generate Token
    token_str = generate_token()
    auth_token = AuthToken(token=token_str, user_id=user.id)
    db.add(auth_token)
    db.commit()

    return TokenResponse(
        access_token=token_str,
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return UserResponse.from_orm(current_user)

@router.post("/logout")
def logout_user(
    authorization: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    """Invalidates active session token."""
    if authorization:
        token_entry = db.query(AuthToken).filter(AuthToken.token == authorization).first()
        if token_entry:
            db.delete(token_entry)
            db.commit()
    return {"status": "logged_out"}
