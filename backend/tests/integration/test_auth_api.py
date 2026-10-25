import pytest
from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import AuditEvent, User
from tests.conftest import PASSWORD, register

pytestmark = pytest.mark.integration
API = "/api/v1"


def auth(t):
    return {"Authorization": f"Bearer {t}"}


def test_register_returns_tokens_and_user(client):
    data = register(client, username="ravi", phone="+91 98765 43210", email="Ravi@Example.com", preferred_language="kn")
    assert data["token_type"] == "bearer" and data["expires_in"] == 900 and len(data["refresh_token"]) > 40
    u = data["user"]
    assert u["username"] == "ravi" and u["phone"] == "9876543210" and u["email"] == "ravi@example.com"
    assert u["preferred_language"] == "kn" and "hashed_password" not in u


def test_register_with_email_only(client):
    assert register(client, username="meena", phone=None, email="meena@example.com")["user"]["phone"] is None


@pytest.mark.parametrize("field,value,msg", [
    ("username", "RAVI", "username"), ("phone", "9876543210", "mobile number"), ("email", "ravi@example.com", "email"),
])
def test_register_conflicts(client, field, value, msg):
    register(client, username="ravi", phone="9876543210", email="ravi@example.com")
    body = {"full_name": "Other", "username": "other", "phone": "9000000000", "password": PASSWORD,
            "confirm_password": PASSWORD, "accept_terms": True, field: value}
    r = client.post(f"{API}/auth/register", json=body)
    assert r.status_code == 409 and msg in r.json()["detail"]


@pytest.mark.parametrize("pw,msg", [("short1", "8 characters"), ("password123", "too common"), ("allletters", "letters and numbers")])
def test_register_password_policy(client, pw, msg):
    r = client.post(f"{API}/auth/register", json={"full_name": "Ravi G", "username": "ravi", "phone": "9876543210",
                                                  "password": pw, "confirm_password": pw, "accept_terms": True})
    assert r.status_code == 422 and msg in r.json()["detail"]


def test_register_validation_error_shape(client):
    r = client.post(f"{API}/auth/register", json={"full_name": "R", "username": "x", "password": "a", "confirm_password": "b"})
    body = r.json()
    assert r.status_code == 422 and body["code"] == "validation_error" and body["errors"] and body["request_id"]


@pytest.mark.parametrize("identifier", ["ravi", "RAVI", "ravi@example.com", "98765 43210", "+919876543210"])
def test_login_with_username_email_or_phone(client, identifier):
    register(client, email="ravi@example.com")
    r = client.post(f"{API}/auth/login", json={"identifier": identifier, "password": PASSWORD})
    assert r.status_code == 200, r.text
    assert client.get(f"{API}/auth/me", headers=auth(r.json()["access_token"])).json()["username"] == "ravi"


def test_login_original_payload_shape(client):
    register(client)
    assert client.post("/api/auth/login", json={"username": "ravi", "password": PASSWORD}).status_code == 200


def test_login_wrong_password_and_unknown_user_same_message(client):
    register(client)
    a = client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": "Wrong2026!"})
    b = client.post(f"{API}/auth/login", json={"identifier": "nobody", "password": "Wrong2026!"})
    assert a.status_code == b.status_code == 401 and a.json()["detail"] == b.json()["detail"]


def test_lockout_after_failures_then_unlock_on_success_after_time(client, monkeypatch):
    register(client)
    for _ in range(5):
        assert client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": "nope-1234"}).status_code == 401
    locked = client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD})
    assert locked.status_code == 423
    assert locked.json()["detail"]["retry_after"] > 800 and locked.headers["retry-after"]
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == "ravi"))
        user.locked_until = None
        db.commit()
    assert client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD}).status_code == 200


def test_refresh_rotates_and_detects_reuse(client):
    data = register(client)
    r1 = client.post(f"{API}/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert r1.status_code == 200
    new = r1.json()
    assert new["refresh_token"] != data["refresh_token"]
    # replaying the old token = theft → whole family revoked, including the new one
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": data["refresh_token"]}).status_code == 401
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": new["refresh_token"]}).status_code == 401
    assert client.get(f"{API}/auth/me", headers=auth(new["access_token"])).status_code == 401
    with SessionLocal() as db:
        assert db.scalar(select(AuditEvent).where(AuditEvent.event == "refresh_reuse_detected"))


def test_refresh_with_garbage(client):
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": "x" * 40}).status_code == 401


def test_logout_kills_access_token_immediately(client):
    data = register(client)
    assert client.post(f"{API}/auth/logout", headers=data["headers"]).status_code == 204
    assert client.get(f"{API}/auth/me", headers=data["headers"]).status_code == 401
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": data["refresh_token"]}).status_code == 401


def test_sessions_list_revoke_and_logout_all(client):
    register(client)
    phone = client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD, "device": "Android phone"}).json()
    laptop = client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD, "device": "Laptop"}).json()
    sessions = client.get(f"{API}/auth/sessions", headers=auth(phone["access_token"])).json()
    assert len(sessions) == 3 and sum(s["current"] for s in sessions) == 1
    laptop_row = next(s for s in sessions if s["device"] == "Laptop")
    assert client.delete(f"{API}/auth/sessions/{laptop_row['id']}", headers=auth(phone["access_token"])).status_code == 204
    assert client.get(f"{API}/auth/me", headers=auth(laptop["access_token"])).status_code == 401
    assert client.post(f"{API}/auth/logout-all", headers=auth(phone["access_token"])).status_code == 204
    assert client.get(f"{API}/auth/me", headers=auth(phone["access_token"])).status_code == 401


def test_cannot_revoke_someone_elses_session(client):
    a = register(client)
    b = register(client, username="meena", phone="9123456780")
    b_sessions = client.get(f"{API}/auth/sessions", headers=b["headers"]).json()
    assert client.delete(f"{API}/auth/sessions/{b_sessions[0]['id']}", headers=a["headers"]).status_code == 404


def test_availability_and_strength(client):
    register(client, email="ravi@example.com")
    q = lambda f, v: client.get(f"{API}/auth/availability", params={"field": f, "value": v}).json()  # noqa: E731
    assert q("username", "ravi")["available"] is False and q("username", "newname")["available"] is True
    assert q("username", "x!")["reason"] == "invalid"
    assert q("phone", "98765 43210")["available"] is False and q("email", "other@example.com")["available"]
    s = client.post(f"{API}/auth/password-strength", json={"password": "Estate-Coffee-2026"}).json()
    assert s["ok"] and s["score"] == 4


def test_profile_update_and_stats(client, farmer):
    h = farmer["headers"]
    r = client.patch(f"{API}/users/me", json={"full_name": "Ravi K Gowda", "email": "rk@example.com", "preferred_language": "kn"},
                     headers=h)
    assert r.status_code == 200 and r.json()["full_name"] == "Ravi K Gowda" and r.json()["preferred_language"] == "kn"
    assert client.patch(f"{API}/users/me", json={"phone": "", "email": ""}, headers=h).status_code == 422
    assert client.get(f"{API}/users/me/stats", headers=h).json() == {"scans": 0, "listings": 0, "chats": 0}


def test_profile_update_conflict(client, farmer, buyer):
    r = client.patch(f"{API}/users/me", json={"phone": "9123456780"}, headers=farmer["headers"])
    assert r.status_code == 409


def test_change_password_revokes_other_sessions(client, farmer):
    other = client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD}).json()
    bad = client.post(f"{API}/users/me/password", headers=farmer["headers"],
                      json={"current_password": "wrong", "new_password": "NewCoffee2027", "confirm_password": "NewCoffee2027"})
    assert bad.status_code == 400
    same = client.post(f"{API}/users/me/password", headers=farmer["headers"],
                       json={"current_password": PASSWORD, "new_password": PASSWORD, "confirm_password": PASSWORD})
    assert same.status_code == 422
    ok = client.post(f"{API}/users/me/password", headers=farmer["headers"],
                     json={"current_password": PASSWORD, "new_password": "NewCoffee2027", "confirm_password": "NewCoffee2027"})
    assert ok.status_code == 200
    assert client.get(f"{API}/auth/me", headers=auth(other["access_token"])).status_code == 401
    assert client.get(f"{API}/auth/me", headers=auth(ok.json()["access_token"])).status_code == 200
    assert client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": "NewCoffee2027"}).status_code == 200


def test_delete_account_requires_password_and_purges(client, farmer):
    h = farmer["headers"]
    assert client.request("DELETE", f"{API}/users/me", json={"password": "wrong"}, headers=h).status_code == 400
    r = client.request("DELETE", f"{API}/users/me", json={"password": PASSWORD}, headers=h)
    assert r.status_code == 200 and r.json()["status"] == "deleted"
    assert client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD}).status_code == 401
    with SessionLocal() as db:
        assert db.scalar(select(User).where(User.username == "ravi")) is None


def test_legacy_hash_upgraded_on_login(client):
    import bcrypt

    register(client)
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.username == "ravi"))
        u.hashed_password = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode()
        db.commit()
    assert client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": PASSWORD}).status_code == 200
    with SessionLocal() as db:
        assert db.scalar(select(User.hashed_password).where(User.username == "ravi")).startswith("$argon2id$")
