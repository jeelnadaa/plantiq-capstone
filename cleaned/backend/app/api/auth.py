import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, generate_token, get_current_user
from app.models.user import User, AuthToken
from app.models.chat import ChatThread, ChatMessage
from app.models.marketplace import CropListing, ListingReport
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token

auth_logger = logging.getLogger("plantiq.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

def _serialize_user(user: User) -> UserResponse:
    if hasattr(UserResponse, "model_validate"):
        return UserResponse.model_validate(user)
    return UserResponse.from_orm(user)

@router.post("/register", response_model=Token)
def register_user(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    existing = db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first()
    if existing:
        auth_logger.warning(f"[Auth Register Rejected] Duplicate username/email attempt for '{payload.username}' from ip={client_ip}")
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token_str = generate_token()
    auth_token = AuthToken(user_id=user.id, token=token_str)
    db.add(auth_token)
    db.commit()
    
    auth_logger.info(f"[Auth Register Success] New user registered: '{user.username}' (id={user.id}) from ip={client_ip}")
    return Token(access_token=token_str, token_type="bearer", user=_serialize_user(user))

@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(User).filter((User.username == payload.username) | (User.email == payload.username)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        auth_logger.warning(f"[Auth Login Failure] Failed login attempt for user identifier='{payload.username}' from ip={client_ip}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    
    token_str = generate_token()
    auth_token = AuthToken(user_id=user.id, token=token_str)
    db.add(auth_token)
    db.commit()
    
    auth_logger.info(f"[Auth Login Success] User '{user.username}' (id={user.id}) authenticated successfully from ip={client_ip}")
    return Token(access_token=token_str, token_type="bearer", user=_serialize_user(user))

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/me")
def delete_my_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GDPR & Data Privacy: Permanently purges user account, tokens, listings, reports, and chat sessions."""
    user_id = current_user.id
    username = current_user.username

    # 1. Purge marketplace listings & reports created by user
    db.query(ListingReport).filter(ListingReport.reported_by_user_id == user_id).delete()
    db.query(CropListing).filter(CropListing.user_id == user_id).delete()

    # 2. Purge chat threads and messages owned by user
    user_threads = db.query(ChatThread).filter(ChatThread.user_id == user_id).all()
    for t in user_threads:
        db.query(ChatMessage).filter(ChatMessage.thread_id == t.id).delete()
        db.delete(t)

    # 3. Purge active auth tokens
    db.query(AuthToken).filter(AuthToken.user_id == user_id).delete()

    # 4. Delete user record
    db.delete(current_user)
    db.commit()

    auth_logger.info(f"[Auth GDPR Purge] Account '{username}' (id={user_id}) and all associated records permanently erased.")
    return {
        "status": "deleted",
        "message": f"Account '{username}' and all associated personal data have been permanently removed."
    }

