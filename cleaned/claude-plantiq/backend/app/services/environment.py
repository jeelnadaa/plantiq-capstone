"""Live microclimate from Open-Meteo. STRICT: no mock data — returns available=False when unknown.

Adds a 3-day forecast and a spray-window recommendation on top of the original behaviour.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import date

import httpx

from app.core.config import settings

log = logging.getLogger("plantiq.env")
ESTIMATED_SOIL_PH = 6.2
CACHE_SECONDS = 60


def region_for(lat: float, lng: float) -> str:
    if 13.1 <= lat <= 13.6 and 75.4 <= lng <= 76.0:
        return "Chikkamagaluru Coffee District"
    if 12.0 <= lat <= 12.7 and 75.5 <= lng <= 76.2:
        return "Kodagu (Coorg) Coffee District"
    if 12.7 <= lat <= 13.1 and 75.6 <= lng <= 76.3:
        return "Hassan (Sakleshpur) Coffee Belt"
    return "Karnataka Coffee Belt"


def incubation_risk(temp: float | None, humidity: float | None, rain: float | None) -> tuple[str, str]:
    """Same thresholds as the original fungal incubation model."""
    if humidity is None or temp is None:
        return "Unknown", "none"
    if humidity >= 80.0 and 20.0 <= temp <= 28.0:
        return "High Infection Risk (Coffee Leaf Rust & Cercospora Favorable)", "high"
    if humidity >= 65.0 or (rain is not None and rain > 0.0):
        return "Moderate Risk (Active Canopy Spore Monitoring Advised)", "moderate"
    return "Low Infection Risk (Favorable Spray Window)", "low"


def spray_window(days: list[dict], raining_now: bool) -> dict:
    for i, d in enumerate(days):
        prob = d.get("rain_probability")
        total = d.get("rain_mm")
        dry = (prob is None or prob < 40) and (total is None or total < 2.0)
        if i == 0 and raining_now:
            dry = False
        if dry:
            return {"day_index": i, "date": d.get("date"), "status": "today" if i == 0 else "later",
                    "advice_en": "Good day to spray — low chance of rain." if i == 0
                    else f"Rain expected first. Next dry day to spray: {d.get('weekday_en')}.",
                    "advice_kn": "ಇಂದು ಸಿಂಪಡಿಸಲು ಒಳ್ಳೆಯ ದಿನ — ಮಳೆಯ ಸಾಧ್ಯತೆ ಕಡಿಮೆ." if i == 0
                    else f"ಮೊದಲು ಮಳೆ ಬರಲಿದೆ. ಸಿಂಪಡಿಸಲು ಮುಂದಿನ ಒಣ ದಿನ: {d.get('weekday_kn')}."}
    return {"day_index": None, "date": None, "status": "none",
            "advice_en": "Rain is likely for the next 3 days. Wait for a dry spell before spraying.",
            "advice_kn": "ಮುಂದಿನ 3 ದಿನ ಮಳೆ ಸಾಧ್ಯತೆ. ಸಿಂಪಡಿಸುವ ಮೊದಲು ಒಣ ಹವೆಗೆ ಕಾಯಿರಿ."}


_WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_WEEKDAYS_KN = ["ಸೋಮವಾರ", "ಮಂಗಳವಾರ", "ಬುಧವಾರ", "ಗುರುವಾರ", "ಶುಕ್ರವಾರ", "ಶನಿವಾರ", "ಭಾನುವಾರ"]


def unavailable(lat: float | None = None, lng: float | None = None, note: str | None = None) -> dict:
    has = lat is not None and lng is not None
    return {
        "available": False,
        "location_status": "Unavailable",
        "note": note or ("Weather service could not be reached." if has else "GPS coordinates not provided."),
        "latitude": lat, "longitude": lng,
        "coordinates": f"{lat:.4f}, {lng:.4f}" if has else None,
        "region_name": region_for(lat, lng) if has else None,
        "temperature": None, "feels_like": None, "humidity": None, "rainfall": None, "wind_speed": None,
        "elevation": None, "soil_ph": None, "incubation_risk": None, "risk_level": "none",
        "forecast": [], "spray_window": None,
    }


class EnvironmentService:
    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        self._cache: dict[str, tuple[float, dict]] = {}
        self._lock = threading.Lock()
        self._http = httpx.Client(timeout=settings.WEATHER_TIMEOUT_S, transport=transport,
                                  headers={"User-Agent": "PlantIQ/3.0 (coffee agronomy decision support)"})

    def get_environmental_data(self, lat: float | None, lng: float | None) -> dict:
        if lat is None or lng is None:
            return unavailable()
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return unavailable(note="Coordinates are out of range.")
        key = f"{round(lat, 3)}_{round(lng, 3)}"
        now = time.time()
        with self._lock:
            hit = self._cache.get(key)
            if hit and now - hit[0] < CACHE_SECONDS:
                return hit[1]
        data = self._fetch(lat, lng)
        if data is None:
            return unavailable(lat, lng)
        result = self._parse(lat, lng, data)
        with self._lock:
            self._cache[key] = (now, result)
            if len(self._cache) > 2000:
                self._cache.clear()
        return result

    def _fetch(self, lat: float, lng: float) -> dict | None:
        params = {
            "latitude": f"{lat:.4f}", "longitude": f"{lng:.4f}",
            "current": "temperature_2m,relative_humidity_2m,rain,precipitation,wind_speed_10m,apparent_temperature",
            "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code",
            "timezone": "auto", "forecast_days": 3,
        }
        for attempt in range(2):
            try:
                resp = self._http.get(settings.OPEN_METEO_URL, params=params)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (429, 503) and attempt == 0:
                    time.sleep(0.5)
                    continue
                log.warning("Open-Meteo HTTP %s", resp.status_code)
                return None
            except httpx.HTTPError as exc:
                if attempt == 0:
                    time.sleep(0.5)
                    continue
                log.warning("Open-Meteo unreachable: %s", exc.__class__.__name__)
        return None

    @staticmethod
    def _num(v) -> float | None:
        try:
            return None if v is None else round(float(v), 1)
        except (TypeError, ValueError):
            return None

    def _parse(self, lat: float, lng: float, data: dict) -> dict:
        cur = data.get("current") or {}
        if not cur:
            return unavailable(lat, lng, "Weather service returned no current data.")
        temp, feels = self._num(cur.get("temperature_2m")), self._num(cur.get("apparent_temperature"))
        hum, wind = self._num(cur.get("relative_humidity_2m")), self._num(cur.get("wind_speed_10m"))
        rain_now = self._num(cur.get("rain")) or self._num(cur.get("precipitation")) or 0.0
        daily = data.get("daily") or {}
        days = []
        for i, d in enumerate(daily.get("time") or []):
            try:
                wd = date.fromisoformat(d).weekday()
            except ValueError:
                wd = 0
            days.append({
                "date": d, "weekday_en": _WEEKDAYS_EN[wd], "weekday_kn": _WEEKDAYS_KN[wd],
                "rain_mm": self._num((daily.get("precipitation_sum") or [None] * 9)[i]),
                "rain_probability": self._num((daily.get("precipitation_probability_max") or [None] * 9)[i]),
                "t_max": self._num((daily.get("temperature_2m_max") or [None] * 9)[i]),
                "t_min": self._num((daily.get("temperature_2m_min") or [None] * 9)[i]),
                "weather_code": (daily.get("weather_code") or [None] * 9)[i],
            })
        rain_today = days[0]["rain_mm"] if days and days[0]["rain_mm"] is not None else rain_now
        risk_text, risk_level = incubation_risk(temp, hum, rain_today)
        return {
            "available": True,
            "location_status": "Active GPS Location",
            "latitude": lat, "longitude": lng, "coordinates": f"{lat:.4f}, {lng:.4f}",
            "region_name": region_for(lat, lng),
            "temperature": temp, "feels_like": feels, "humidity": hum,
            "rainfall": rain_today, "rain_now": rain_now, "wind_speed": wind,
            "elevation": self._num(data.get("elevation")),
            "soil_ph": ESTIMATED_SOIL_PH, "soil_ph_estimated": True,
            "incubation_risk": risk_text, "risk_level": risk_level,
            "forecast": days, "spray_window": spray_window(days, rain_now > 0) if days else None,
            "fetched_at": int(time.time()),
        }
