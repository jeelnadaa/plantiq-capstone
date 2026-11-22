"""Records one Open-Meteo response per test location into data/weather_*.json (run once; the benchmark then never
calls the network, so every system and every rerun sees the same weather). Same request as the backend's
EnvironmentService._fetch."""
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

LOCATIONS = {"chikkamagaluru": (13.3161, 75.7720), "kodagu": (12.4244, 75.7382)}
PARAMS = {"current": "temperature_2m,relative_humidity_2m,rain,precipitation,wind_speed_10m,apparent_temperature",
          "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code",
          "timezone": "auto", "forecast_days": 3}
out = Path(__file__).resolve().parent / "data"
for name, (lat, lng) in LOCATIONS.items():
    r = httpx.get("https://api.open-meteo.com/v1/forecast", timeout=15,
                  params={"latitude": f"{lat:.4f}", "longitude": f"{lng:.4f}", **PARAMS})
    r.raise_for_status()
    data = r.json()
    data["_recorded"] = {"name": name, "lat": lat, "lng": lng, "utc": datetime.now(timezone.utc).isoformat()}
    (out / f"weather_{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(name, data["current"], data["daily"]["precipitation_probability_max"])
