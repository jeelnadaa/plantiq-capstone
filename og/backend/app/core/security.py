import bcrypt
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, AuthToken

# Legacy salt preserved strictly for backward-compatible verification of legacy seed hashes
LEGACY_SALT = b"plantiq_coffee_security_salt_2026"

def hash_password(password: str) -> str:
    """Hashes a password using standard bcrypt with automatic salt generation."""
    pwd_bytes = password.encode('utf-8')
    # Bcrypt maximum input length is 72 bytes
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies password using bcrypt with timing-safe comparison, with fallback for legacy PBKDF2 hashes."""
    pwd_bytes = plain_password.encode('utf-8')
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]

    # Bcrypt format check ($2b$, $2a$, $2y$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
        except Exception:
            return False

    # Backward-compatible PBKDF2-HMAC-SHA256 verification for legacy records with constant-time equality
    legacy_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), LEGACY_SALT, 100000).hex()
    return hmac.compare_digest(legacy_key, hashed_password)

def generate_token() -> str:
    """Generates a cryptographically secure 256-bit random session token."""
    return secrets.token_hex(32)

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return authorization

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    token_str = get_token_from_header(authorization)
    if not token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required.')
    
    entry = db.query(AuthToken).filter(AuthToken.token == token_str).first()
    if not entry or not entry.user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired session.')
    
    # Enforce token expiration (sliding/fixed window from settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if entry.created_at:
        expiry_threshold = entry.created_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        if datetime.utcnow() > expiry_threshold:
            db.delete(entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Session expired. Please log in again.')
            
    return entry.user

def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    token_str = get_token_from_header(authorization)
    if not token_str:
        return None
    
    entry = db.query(AuthToken).filter(AuthToken.token == token_str).first()
    if not entry or not entry.user:
        return None

    if entry.created_at:
        expiry_threshold = entry.created_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        if datetime.utcnow() > expiry_threshold:
            db.delete(entry)
            db.commit()
            return None

    return entry.user
