from typing import Dict, Any, Optional
import requests
from app.modules.environment.interface import IEnvironmentalDataService

class MockGeoWeatherProvider(IEnvironmentalDataService):
    """
    Concrete implementation of IEnvironmentalDataService.
    Swappable with real IoT hardware or proprietary agronomy APIs in the future.
    """

    def get_environmental_data(
        self, 
        latitude: Optional[float] = None, 
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        
        # Scenario 1: Location Disallowed or Unavailable
        if latitude is None or longitude is None:
            return {
                "location_status": "Disallowed / Unavailable",
                "note": "Operating with general agronomic defaults."
            }

        # Scenario 2: Location Allowed — query free weather API or fallback to region-aware data
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,rain&elevation=nan"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                current = data.get("current", {})
                return {
                    "location_status": "Active GPS Location",
                    "Coordinates": f"{latitude:.4f}, {longitude:.4f}",
                    "Temperature (°C)": current.get("temperature_2m", 24.5),
                    "Humidity (%)": current.get("relative_humidity_2m", 78.0),
                    "Rainfall (mm)": current.get("rain", 12.0),
                    "Soil pH (estimated)": 6.2,
                    "Elevation (m)": 980.0
                }
        except Exception as e:
            print(f"[EnvProvider] Weather API query warning: {e}")

        # Default fallback snapshot for active location
        return {
            "location_status": "Active GPS Location (Fallback Weather)",
            "Coordinates": f"{latitude:.4f}, {longitude:.4f}",
            "Temperature (°C)": 23.5,
            "Humidity (%)": 82.0,
            "Rainfall (mm)": 15.0,
            "Soil pH": 6.0,
            "Elevation (m)": 1100.0
        }

_env_service_instance = MockGeoWeatherProvider()

def get_env_service() -> IEnvironmentalDataService:
    return _env_service_instance
