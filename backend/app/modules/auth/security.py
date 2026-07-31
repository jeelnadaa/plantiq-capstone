import hashlib
import os
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.models import User, AuthToken

SECRET_SALT = b"plantiq_coffee_security_salt_2026"

def hash_password(password: str) -> str:
    """Hashes password using PBKDF2 HMAC SHA-256."""
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        SECRET_SALT,
        100000
    )
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed password."""
    return hash_password(plain_password) == hashed_password

def generate_token() -> str:
    """Generates a secure random 64-character hex token."""
    return secrets.token_hex(32)

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extracts bearer token from Authorization header."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI Dependency: Ensures request is authenticated and returns logged-in User."""
    token_str = get_token_from_header(authorization)
    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in to continue."
        )

    token_entry = db.query(AuthToken).filter(AuthToken.token == token_str).first()
    if not token_entry or not token_entry.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token."
        )

    return token_entry.user

def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """FastAPI Dependency: Returns User if authenticated, else None (for guest mode)."""
    token_str = get_token_from_header(authorization)
    if not token_str:
        return None

    token_entry = db.query(AuthToken).filter(AuthToken.token == token_str).first()
    return token_entry.user if token_entry else None
