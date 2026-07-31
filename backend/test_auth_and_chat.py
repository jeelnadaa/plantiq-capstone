import sys
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_auth_and_multichat():
    # 0. Verify Unauthenticated Request gets rejected with 401 Unauthorized
    unauth_res = client.post("/api/chat/threads/new", data={"title": "Unauthorized Test"})
    assert unauth_res.status_code == 401
    print("[OK] Unauthenticated request correctly rejected with 401 Unauthorized!")

    # 1. Register User
    reg_payload = {
        "email": "testfarmer@plant.iq",
        "username": "testfarmer",
        "password": "farmerpassword123",
        "full_name": "Ramesh Gowda"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    if res.status_code != 200:
        # User may already exist from previous test run
        res = client.post("/api/auth/login", json={"email_or_username": "testfarmer", "password": "farmerpassword123"})

    assert res.status_code == 200, f"Auth failed: {res.text}"
    auth_data = res.json()
    token = auth_data["access_token"]
    print("[OK] Auth Successful! Token:", token[:15] + "...")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Thread 1
    t1_res = client.post("/api/chat/threads/new", data={"title": "Coffee Rust Care"}, headers=headers)
    assert t1_res.status_code == 200
    t1_id = t1_res.json()["thread_id"]
    print("[OK] Thread 1 Created:", t1_id[:10])

    # 3. Post Message to Thread 1
    m1_res = client.post(
        "/api/chat/message",
        data={"session_id": t1_id, "user_message": "What is the organic treatment for Coffee Leaf Rust?", "language": "en"},
        headers=headers
    )
    assert m1_res.status_code == 200
    print("[OK] Thread 1 Replied:", m1_res.json()["reply"][:40] + "...")

    # 4. Create Thread 2
    t2_res = client.post("/api/chat/threads/new", data={"title": "Fertilizer Schedule"}, headers=headers)
    assert t2_res.status_code == 200
    t2_id = t2_res.json()["thread_id"]
    print("[OK] Thread 2 Created:", t2_id[:10])

    # 5. Post Message to Thread 2
    m2_res = client.post(
        "/api/chat/message",
        data={"session_id": t2_id, "user_message": "How much NPK fertilizer for young Robusta plants?", "language": "en"},
        headers=headers
    )
    assert m2_res.status_code == 200
    print("[OK] Thread 2 Replied:", m2_res.json()["reply"][:40] + "...")

    # 6. Fetch User's Thread List
    list_res = client.get("/api/chat/threads", headers=headers)
    assert list_res.status_code == 200
    threads = list_res.json()
    print(f"[OK] Found {len(threads)} saved chat threads for Ramesh Gowda!")

    # 7. Reload Message History for Thread 1
    h1_res = client.get(f"/api/chat/threads/{t1_id}/messages", headers=headers)
    assert h1_res.status_code == 200
    h1_msgs = h1_res.json()
    assert len(h1_msgs) >= 2
    print(f"[OK] Successfully retrieved Thread 1 history with {len(h1_msgs)} messages!")

    print("\nALL USER AUTH & MULTI-THREAD CHAT PERSISTENCE TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_full_auth_and_multichat()
