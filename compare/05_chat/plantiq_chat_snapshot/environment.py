"""SNAPSHOT of backend/app/services/environment.py (see ../SNAPSHOT.md). Live microclimate from Open-Meteo. STRICT: no mock data — returns available=False when unknown.

Adds a 3-day forecast and a spray-window recommendation on top of the original behaviour.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import date


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


class FrozenEnvironmentService:
    """EnvironmentService with the HTTP call replaced by Open-Meteo responses recorded once (data/weather_*.json), so
    every system and every run sees the same weather. `_num` and `_parse` are the backend's code unchanged."""

    def __init__(self, responses: dict[tuple[float, float], dict]) -> None:
        self.responses = responses

    def get_environmental_data(self, lat: float | None, lng: float | None) -> dict:
        if lat is None or lng is None:
            return unavailable()
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return unavailable(note="Coordinates are out of range.")
        near = min(self.responses, key=lambda k: (k[0] - lat) ** 2 + (k[1] - lng) ** 2)
        if (near[0] - lat) ** 2 + (near[1] - lng) ** 2 > 0.01:
            return unavailable(lat, lng)
        return self._parse(lat, lng, self.responses[near])

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
