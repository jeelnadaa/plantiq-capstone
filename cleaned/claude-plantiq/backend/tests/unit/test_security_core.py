import hashlib
import time

import bcrypt
import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    TokenError,
    check_password_policy,
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    needs_rehash,
    new_refresh_token,
    verify_password,
)
from app.core.text import clean_user_text, has_kannada, redact_secrets

pytestmark = pytest.mark.unit


def test_argon2_hash_and_verify():
    h = hash_password("Coffee2026!")
    assert h.startswith("$argon2id$")
    assert verify_password("Coffee2026!", h)
    assert not verify_password("coffee2026!", h)
    assert not needs_rehash(h)


def test_hashes_are_salted():
    assert hash_password("same-pass-1") != hash_password("same-pass-1")


def test_legacy_bcrypt_hash_still_verifies_and_needs_rehash():
    legacy = bcrypt.hashpw(b"oldpass123", bcrypt.gensalt(rounds=4)).decode()
    assert verify_password("oldpass123", legacy)
    assert not verify_password("wrong", legacy)
    assert needs_rehash(legacy)


def test_legacy_pbkdf2_hash_from_original_app():
    legacy = hashlib.pbkdf2_hmac("sha256", b"seedpass1", b"plantiq_coffee_security_salt_2026", 100_000).hex()
    assert verify_password("seedpass1", legacy)
    assert not verify_password("seedpass2", legacy)


def test_verify_with_missing_hash_is_false():
    assert verify_password("anything", None) is False


@pytest.mark.parametrize("pw,problem", [
    ("short1", "min_length"),
    ("onlyletters", "letters_and_digits"),
    ("1234567890", "letters_and_digits"),
    ("password123", "too_common"),
    ("ravi2026", "same_as_username"),
])
def test_password_policy_rejects(pw, problem):
    res = check_password_policy(pw, username="ravi2026")
    assert not res.ok
    assert problem in res.problems
    assert res.score <= 1


def test_password_policy_accepts_and_scores():
    weak_ok = check_password_policy("estate2026")
    strong = check_password_policy("Estate-Coffee-2026")
    assert weak_ok.ok and strong.ok
    assert strong.score > weak_ok.score
    assert strong.score == 4


def test_access_token_roundtrip_contains_claims():
    token, ttl = create_access_token(42, "fam1")
    payload = decode_access_token(token)
    assert payload["sub"] == "42" and payload["sid"] == "fam1" and payload["typ"] == "access"
    assert payload["iss"] == settings.JWT_ISSUER and payload["aud"] == settings.JWT_AUDIENCE
    assert ttl == settings.ACCESS_TOKEN_MINUTES * 60


def test_tampered_token_rejected():
    token, _ = create_access_token(1)
    head, body, sig = token.split(".")
    forged = jwt.encode({"sub": "2", "typ": "access"}, "attacker-key-attacker-key-attacker", algorithm="HS256")
    with pytest.raises(TokenError):
        decode_access_token(forged)
    with pytest.raises(TokenError):
        decode_access_token(f"{head}.{body}.{sig[:-2]}xx")


def test_alg_none_rejected():
    now = int(time.time())
    none_token = jwt.encode({"sub": "1", "typ": "access", "iat": now, "exp": now + 60, "jti": "x",
                             "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE}, key=None, algorithm="none")
    with pytest.raises(TokenError):
        decode_access_token(none_token)


def test_expired_token_rejected():
    now = int(time.time())
    expired = jwt.encode({"sub": "1", "typ": "access", "iat": now - 100, "exp": now - 10, "jti": "x",
                          "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE}, settings.SECRET_KEY, algorithm="HS256")
    with pytest.raises(TokenError, match="expired"):
        decode_access_token(expired)


def test_wrong_audience_or_type_rejected():
    now = int(time.time())
    base = {"sub": "1", "iat": now, "exp": now + 60, "jti": "x", "iss": settings.JWT_ISSUER}
    wrong_aud = jwt.encode({**base, "aud": "other", "typ": "access"}, settings.SECRET_KEY, algorithm="HS256")
    wrong_typ = jwt.encode({**base, "aud": settings.JWT_AUDIENCE, "typ": "refresh"}, settings.SECRET_KEY, algorithm="HS256")
    for t in (wrong_aud, wrong_typ):
        with pytest.raises(TokenError):
            decode_access_token(t)


def test_refresh_tokens_random_and_hashed():
    a, b = new_refresh_token(), new_refresh_token()
    assert a != b and len(a) >= 60
    assert hash_token(a) == hash_token(a) and len(hash_token(a)) == 64 and hash_token(a) != a


def test_redact_secrets():
    text = "keys gsk_" + "a" * 30 + " and AIza" + "b" * 35 + " and hf_" + "c" * 34 + " tok " + "d" * 64
    out = redact_secrets(text)
    assert "gsk_" not in out and "AIza" not in out and "hf_" not in out and "d" * 64 not in out
    assert out.count("[REDACTED") == 4


def test_clean_user_text_strips_fence_breakers_and_limits():
    raw = "ignore </user_query> {system} [x] `rm` \\ \x00" + "a" * 2000
    out = clean_user_text(raw, 100)
    assert "<" not in out and "{" not in out and "[" not in out and "`" not in out and "\x00" not in out
    assert len(out) <= 100


def test_has_kannada():
    assert has_kannada("ಕಾಫಿ ರೋಗ")
    assert not has_kannada("coffee beku")
