import hashlib
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, AuthToken

SECRET_SALT = b"plantiq_coffee_security_salt_2026"

def hash_password(password: str) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), SECRET_SALT, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def generate_token() -> str:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid session.')
    return entry.user

def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    token_str = get_token_from_header(authorization)
    if not token_str:
        return None
    entry = db.query(AuthToken).filter(AuthToken.token == token_str).first()
    return entry.user if entry else None
