"""Password hashing, password policy, JWT access tokens and rotating refresh tokens."""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import settings
from app.core.timeutil import utcnow

# ---------------------------------------------------------------------------
# Password hashing (Argon2id; verifies legacy bcrypt / PBKDF2 hashes from the original app)
# ---------------------------------------------------------------------------
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2, hash_len=32, salt_len=16)
_LEGACY_PBKDF2_SALT = b"plantiq_coffee_security_salt_2026"
# Precomputed hash used to keep verification time constant for unknown users.
_DUMMY_HASH = _hasher.hash("plantiq-dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        # Burn comparable CPU time so a missing user is indistinguishable from a wrong password.
        try:
            _hasher.verify(_DUMMY_HASH, password + "x")
        except VerificationError:
            pass
        return False
    if hashed.startswith("$argon2"):
        try:
            return _hasher.verify(hashed, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        import bcrypt

        try:
            return bcrypt.checkpw(password.encode()[:72], hashed.encode())
        except ValueError:
            return False
    legacy = hashlib.pbkdf2_hmac("sha256", password.encode(), _LEGACY_PBKDF2_SALT, 100_000).hex()
    return hmac.compare_digest(legacy, hashed)


def needs_rehash(hashed: str) -> bool:
    if not hashed.startswith("$argon2"):
        return True
    try:
        return _hasher.check_needs_rehash(hashed)
    except InvalidHashError:
        return True


# ---------------------------------------------------------------------------
# Password policy
# ---------------------------------------------------------------------------
COMMON_PASSWORDS = frozenset({
    "password", "password1", "password123", "12345678", "123456789", "1234567890", "qwerty123", "qwertyuiop",
    "11111111", "00000000", "iloveyou", "abc12345", "admin123", "welcome1", "letmein1", "coffee123",
    "plantiq123", "farmer123", "india123", "karnataka1", "passw0rd", "p@ssw0rd", "asdf1234", "zxcvbnm1",
})


@dataclass
class PasswordCheck:
    ok: bool
    score: int  # 0..4
    problems: list[str]


def check_password_policy(password: str, username: str | None = None) -> PasswordCheck:
    problems: list[str] = []
    if len(password) < 8:
        problems.append("min_length")
    if len(password) > 128:
        problems.append("max_length")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        problems.append("letters_and_digits")
    if password.lower() in COMMON_PASSWORDS:
        problems.append("too_common")
    if username and password.lower() == username.lower():
        problems.append("same_as_username")
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[A-Za-z]", password) and re.search(r"\d", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password) or (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password)):
        score += 1
    if problems:
        score = min(score, 1)
    return PasswordCheck(ok=not problems, score=score, problems=problems)


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
class TokenError(Exception):
    pass


def create_access_token(user_id: int, session_family: str | None = None) -> tuple[str, int]:
    now = utcnow()
    expires = now + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    payload = {
        "sub": str(user_id),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": uuid.uuid4().hex,
        "typ": "access",
    }
    if session_family:
        payload["sid"] = session_family
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token, settings.ACCESS_TOKEN_MINUTES * 60


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],  # pinned: rejects alg=none and algorithm-confusion attacks
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "jti", "typ"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("expired") from exc
    except jwt.PyJWTError as exc:
        raise TokenError("invalid") from exc
    if payload.get("typ") != "access":
        raise TokenError("invalid")
    return payload


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_family_id() -> str:
    return uuid.uuid4().hex
