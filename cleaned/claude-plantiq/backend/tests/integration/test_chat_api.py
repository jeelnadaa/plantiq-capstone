import base64
import json

import pytest

from app.services import registry
from app.services.fakes import FakeLLM
from tests.conftest import image_bytes

pytestmark = pytest.mark.integration
API = "/api/v1"


def send(client, headers, text, files=None, **form):
    return client.post(f"{API}/chat/message", headers=headers, data={"user_message": text, "language": "en", **form},
                       files=files)


def test_new_thread_then_continue(client, farmer):
    h = farmer["headers"]
    r1 = send(client, h, "How do I control coffee leaf rust?")
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    assert d1["session_id"] and d1["reply"] and len(d1["history"]) == 2 and d1["sources"]
    d2 = send(client, h, "And organic options?", session_id=d1["session_id"]).json()
    assert d2["session_id"] == d1["session_id"] and len(d2["history"]) == 4
    threads = client.get(f"{API}/chat/threads", headers=h).json()
    assert len(threads) == 1 and threads[0]["message_count"] == 4 and threads[0]["title"].startswith("How do I control")


def test_history_is_included_in_prompt(client, farmer):
    llm = FakeLLM()
    registry.override("llm", llm)
    sid = send(client, farmer["headers"], "My rust problem is severe").json()["session_id"]
    send(client, farmer["headers"], "what next?", session_id=sid)
    assert "Farmer: My rust problem is severe" in llm.calls[-1]


def test_attach_uploaded_image_runs_cnn_and_is_persisted(client, farmer):
    h = farmer["headers"]
    d = send(client, h, "What is wrong with this leaf?", files={"image_file": ("leaf.png", image_bytes("PNG"), "image/png")}).json()
    assert d["disease"] and d["image_url"]
    msgs = client.get(f"{API}/chat/threads/{d['session_id']}/messages", headers=h).json()
    assert msgs[0]["image_url"] == d["image_url"] and msgs[0]["attached_image_name"] and msgs[1]["role"] == "assistant"
    assert client.get(d["image_url"]).status_code == 200


def test_attach_base64_image_original_api(client, farmer):
    b64 = "data:image/jpeg;base64," + base64.b64encode(image_bytes()).decode()
    d = send(client, farmer["headers"], "check", image_base64=b64).json()
    assert d["disease"] and d["image_url"]


def test_attach_from_scan_history_by_media_id(client, farmer, buyer):
    scan = client.post(f"{API}/predict", headers=farmer["headers"], files={"file": ("l.jpg", image_bytes(), "image/jpeg")}).json()
    media_id = scan["image_url"].split("/")[-1].removesuffix(".jpg")
    ok = send(client, farmer["headers"], "about this scan", media_id=media_id)
    assert ok.status_code == 200 and ok.json()["image_url"] == scan["image_url"]
    assert send(client, buyer["headers"], "steal", media_id=media_id).status_code == 404  # not theirs


def test_scan_metadata_handoff(client, farmer):
    llm = FakeLLM()
    registry.override("llm", llm)
    meta = {"disease": "Rust", "confidence": 94.1, "advisory": "Spray Bordeaux 0.5%",
            "env_data": {"available": True, "humidity": 88, "temperature": 24.6}}
    d = send(client, farmer["headers"], "What should be my spray timing?", scan_metadata_json=json.dumps(meta)).json()
    assert d["disease"] == "Rust"
    assert "PAST SCAN ATTACHED" in llm.calls[-1] and "humidity=88" in llm.calls[-1]


def test_coordinates_in_message_used_for_weather(client, farmer):
    llm = FakeLLM()
    registry.override("llm", llm)
    d = send(client, farmer["headers"], "weather at 13.3161, 75.7720 today?").json()
    assert d["env_used"] is True and "temperature: 24.6" in llm.calls[-1]


def test_weather_question_without_location_says_unavailable(client, farmer):
    llm = FakeLLM()
    registry.override("llm", llm)
    d = send(client, farmer["headers"], "How is the weather?").json()
    assert d["env_used"] is False and "NOT available" in llm.calls[-1]


def test_kannada_message_routes_to_kannada(client, farmer):
    d = send(client, farmer["headers"], "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಏನು ಮಾಡಬೇಕು?").json()
    assert d["language"] == "kn"


def test_offline_reply_without_llm(client, farmer):
    class NoLLM:
        available = False

        def providers(self):
            return []

    registry.override("llm", NoLLM())
    d = send(client, farmer["headers"], "rust control?", disease_context="Rust").json()
    assert d["provider"] == "offline" and "Bordeaux" in d["reply"]


def test_rename_and_delete_thread(client, farmer):
    h = farmer["headers"]
    sid = send(client, h, "hello there").json()["session_id"]
    assert client.patch(f"{API}/chat/threads/{sid}", json={"title": "Rust plan"}, headers=h).json()["title"] == "Rust plan"
    assert client.delete(f"{API}/chat/threads/{sid}", headers=h).status_code == 200
    assert client.get(f"{API}/chat/threads", headers=h).json() == []
    assert client.get(f"{API}/chat/threads/{sid}/messages", headers=h).status_code == 404


def test_thread_isolation_between_users(client, farmer, buyer):
    sid = send(client, farmer["headers"], "private").json()["session_id"]
    assert client.get(f"{API}/chat/threads/{sid}/messages", headers=buyer["headers"]).status_code == 403
    assert send(client, buyer["headers"], "inject into their thread", session_id=sid).status_code == 403
    assert client.delete(f"{API}/chat/threads/{sid}", headers=buyer["headers"]).status_code == 403
    assert client.get(f"{API}/chat/threads", headers=buyer["headers"]).json() == []


def test_chat_validation(client, farmer):
    assert send(client, farmer["headers"], "").status_code == 422
    assert send(client, farmer["headers"], "x" * 2001).status_code == 422
    assert send(client, farmer["headers"], "hi", files={"image_file": ("a.gif", b"GIF89a", "image/gif")}).status_code == 415
