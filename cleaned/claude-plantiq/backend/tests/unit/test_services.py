"""Environment, language router, chat helpers, LLM client, advisory and fakes."""
import json

import httpx
import pytest

from app.core.config import settings
from app.services.advisory import generate_advisory
from app.services.chat import extract_coordinates, is_weather_query
from app.services.environment import EnvironmentService, incubation_risk, region_for, spray_window
from app.services.fakes import FakeCNN, FakeLLM, FakeRetriever
from app.services.knowledge import CARDS, offline_advisory
from app.services.lang_router import heuristic_route, route_query
from app.services.llm import LLMClient
from tests.conftest import OPEN_METEO_SAMPLE, weather_transport

pytestmark = pytest.mark.unit


# ------------------------------------------------------------------ environment
@pytest.mark.parametrize("t,h,r,level", [
    (24, 85, 0, "high"), (30, 85, 0, "moderate"), (24, 70, 0, "moderate"), (24, 50, 1.2, "moderate"),
    (24, 50, 0, "low"), (None, 50, 0, "none"),
])
def test_incubation_risk_thresholds(t, h, r, level):
    assert incubation_risk(t, h, r)[1] == level


@pytest.mark.parametrize("lat,lng,region", [
    (13.3161, 75.7720, "Chikkamagaluru"), (12.42, 75.74, "Kodagu"), (12.94, 75.78, "Hassan"), (15.0, 74.0, "Karnataka"),
])
def test_region(lat, lng, region):
    assert region in region_for(lat, lng)


def test_spray_window_picks_first_dry_day():
    days = [{"rain_probability": 80, "rain_mm": 6, "weekday_en": "Mon", "weekday_kn": "ಸೋ"},
            {"rain_probability": 20, "rain_mm": 0.5, "weekday_en": "Tue", "weekday_kn": "ಮಂ"}]
    w = spray_window(days, raining_now=False)
    assert w["day_index"] == 1 and "Tue" in w["advice_en"]
    assert spray_window([{"rain_probability": 5, "rain_mm": 0}], raining_now=False)["status"] == "today"
    assert spray_window([{"rain_probability": 5, "rain_mm": 0}], raining_now=True)["status"] == "none"


def test_environment_parses_open_meteo():
    svc = EnvironmentService(transport=weather_transport())
    env = svc.get_environmental_data(13.3161, 75.7720)
    assert env["available"] and env["temperature"] == 24.6 and env["humidity"] == 88
    assert env["rainfall"] == 6.0 and env["elevation"] == 1090 and env["risk_level"] == "high"
    assert env["soil_ph"] == 6.2 and env["soil_ph_estimated"] is True
    assert len(env["forecast"]) == 3 and env["spray_window"]["day_index"] == 2
    assert env["region_name"].startswith("Chikkamagaluru")


def test_environment_never_mocks_when_missing_or_down():
    svc = EnvironmentService(transport=weather_transport(status=500))
    assert svc.get_environmental_data(None, None)["available"] is False
    down = svc.get_environmental_data(13.3, 75.7)
    assert down["available"] is False and down["temperature"] is None and down["region_name"]
    assert svc.get_environmental_data(95, 75)["available"] is False


def test_environment_cache():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(200, json=OPEN_METEO_SAMPLE)

    svc = EnvironmentService(transport=httpx.MockTransport(handler))
    svc.get_environmental_data(13.31612, 75.77201)
    svc.get_environmental_data(13.31609, 75.77198)
    assert calls["n"] == 1


# ------------------------------------------------------------------ router / chat helpers
@pytest.mark.parametrize("text,script,lang", [
    ("ಕಾಫಿ ಎಲೆಗೆ ಯಾವ ಔಷಧಿ?", "kannada_script", "kn"),
    ("Coffee beliyalu yaava gobbara beku?", "kanglish", "kn"),
    ("When should I spray Bordeaux?", "english", "en"),
])
def test_heuristic_router(text, script, lang):
    r = heuristic_route(text)
    assert r["detected_script"] == script and r["target_response_language"] == lang


def test_router_greeting_and_location():
    assert heuristic_route("Hello!")["is_greeting_or_location_only"]
    assert heuristic_route("Chikkamagaluru")["is_greeting_or_location_only"]
    assert not heuristic_route("rust on leaves")["is_greeting_or_location_only"]


def test_router_uses_llm_json_and_falls_back():
    r = route_query("When to spray for rust?", FakeLLM())
    assert r["search_query_english"] == "coffee rust spray timing" and r["source"] == "fake"

    class Broken(FakeLLM):
        def generate(self, *a, **k):
            from app.services.llm import LLMResult
            return LLMResult("not json", "x", "y")

    assert route_query("When to spray?", Broken())["source"] == "heuristic"
    assert route_query("When to spray?", None)["source"] == "heuristic"


@pytest.mark.parametrize("text,coords", [
    ("my estate is at 13.3161, 75.7720 what now", (13.3161, 75.772)),
    ("lat: 12.42 lng: 75.74", (12.42, 75.74)),
    ("Latitude=12.5 Longitude=76.1", (12.5, 76.1)),
    ("price 420.5 per 2 kg", None),
    ("91.5, 75.0", None),
])
def test_extract_coordinates(text, coords):
    assert extract_coordinates(text) == coords


def test_weather_intent():
    assert is_weather_query("How is the weather today?")
    assert is_weather_query("ಇಂದು ಮಳೆ ಬರುತ್ತದೆಯೇ")
    assert not is_weather_query("which fertilizer for flowering")


# ------------------------------------------------------------------ LLM client
def _llm(handler, monkeypatch, gemini="g-key", groq="q-key"):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", gemini)
    monkeypatch.setattr(settings, "GROQ_API_KEY", groq)
    return LLMClient(transport=httpx.MockTransport(handler))


def test_llm_gemini_success(monkeypatch):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "Use 0.5% Bordeaux"}]}}]})

    res = _llm(handler, monkeypatch).generate("prompt", system="sys")
    assert res.provider == "gemini" and res.text == "Use 0.5% Bordeaux"
    body = json.loads(seen[0].content)
    assert seen[0].headers["x-goog-api-key"] == "g-key" and body["systemInstruction"]["parts"][0]["text"] == "sys"


def test_llm_falls_back_to_groq_then_none(monkeypatch):
    def handler(req):
        if "googleapis" in str(req.url):
            return httpx.Response(400, json={"error": "bad"})
        return httpx.Response(200, json={"choices": [{"message": {"content": "groq answer"}}]})

    res = _llm(handler, monkeypatch).generate("p")
    assert res.provider == "groq" and res.text == "groq answer"
    dead = _llm(lambda r: httpx.Response(401, json={}), monkeypatch).generate("p")
    assert dead is None
    assert _llm(lambda r: httpx.Response(200), monkeypatch, gemini="", groq="").generate("p") is None


def test_llm_retries_once_on_503(monkeypatch):
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setattr("app.services.llm.time.sleep", lambda s: None)
    assert _llm(handler, monkeypatch, groq="").generate("p").text == "ok" and calls["n"] == 2


def test_llm_output_redacts_leaked_keys(monkeypatch):
    leak = "here is gsk_" + "Z" * 40

    def handler(req):
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": leak}]}}]})

    assert "gsk_" not in _llm(handler, monkeypatch).generate("p").text


# ------------------------------------------------------------------ advisory
def test_offline_cards_cover_all_classes_and_languages():
    for cls in ("Miner", "Rust", "Phoma", "Healthy", "Cerscospora"):
        for lang in ("en", "kn"):
            text = offline_advisory(cls, lang, None, [])
            assert CARDS[cls][lang]["summary"] in text


def test_generate_advisory_with_llm():
    llm = FakeLLM()
    adv = generate_advisory(disease="Rust", confidence=94.0, env={"available": True, "temperature": 24, "humidity": 88},
                            question="when to spray?", language="en", rag=FakeRetriever(), llm=llm)
    assert adv.provider == "fake:fake-llm" and not adv.is_blended and adv.safety_audit["verified"]
    assert adv.citations and adv.citations[0]["source"] == "Coffee_Diseases.pdf"
    assert "<user_query>" in llm.calls[-1] and "humidity: 88" in llm.calls[-1]


def test_generate_advisory_blended_and_offline_kannada():
    class NoLLM:
        available = False

    adv = generate_advisory(disease="Miner", confidence=55.0, env=None, question=None, language="kn",
                            rag=FakeRetriever(), llm=NoLLM())
    assert adv.provider == "offline" and adv.is_blended and adv.language == "kn"
    assert any("55.0%" in r for r in adv.reasons)
    assert "ಸುರಂಗ" in adv.answer


def test_fake_cnn_is_deterministic():
    a, b = FakeCNN().predict(b"abc"), FakeCNN().predict(b"abc")
    assert a == b and abs(sum(a["distribution"].values()) - 100) < 0.1


def test_gemini_disables_thinking_and_rejects_truncated_answers(monkeypatch):
    seen = []

    def handler(req):
        seen.append(json.loads(req.content))
        if "googleapis" in str(req.url):
            return httpx.Response(200, json={"candidates": [{"finishReason": "MAX_TOKENS",
                                                             "content": {"parts": [{"text": "ನಿಮ್ಮ ಕಾಫಿ"}]}}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "full groq answer"}}]})

    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
    res = _llm(handler, monkeypatch).generate("p", max_tokens=900)
    gen = seen[0]["generationConfig"]
    assert gen["thinkingConfig"] == {"thinkingBudget": 0} and gen["maxOutputTokens"] >= 1800
    assert res.provider == "groq" and res.text == "full groq answer"
