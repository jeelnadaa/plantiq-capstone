import requests
from typing import Dict, Any, Optional

class EnvironmentalService:
    def get_environmental_data(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        if latitude is None or longitude is None:
            return {
                'location_status': 'Disallowed / Unavailable',
                'note': 'Operating with standard South Indian coffee belt agronomic baselines.'
            }
        try:
            url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,apparent_temperature&elevation=nan'
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                current = data.get('current', {})
                elevation_val = data.get('elevation', 980.0)
                return {
                    'location_status': 'Active GPS Location',
                    'Coordinates': f'{latitude:.4f}, {longitude:.4f}',
                    'Temperature (°C)': current.get('temperature_2m', 24.5),
                    'Feels Like (°C)': current.get('apparent_temperature', 25.0),
                    'Humidity (%)': current.get('relative_humidity_2m', 78.0),
                    'Rainfall (mm)': current.get('rain', 0.0),
                    'Wind Speed (km/h)': current.get('wind_speed_10m', 12.0),
                    'Soil pH (estimated)': 6.2,
                    'Elevation (m)': elevation_val
                }
        except Exception as e:
            print(f'[Cleaned EnvService] Open-Meteo Warning: {e}')
        return {
            'location_status': 'Active GPS Location (Fallback Weather)',
            'Coordinates': f'{latitude:.4f}, {longitude:.4f}',
            'Temperature (°C)': 23.5,
            'Feels Like (°C)': 24.5,
            'Humidity (%)': 82.0,
            'Rainfall (mm)': 5.0,
            'Wind Speed (km/h)': 10.0,
            'Soil pH': 6.2,
            'Elevation (m)': 980.0
        }

_env_instance = EnvironmentalService()
def get_env_service() -> EnvironmentalService:
    return _env_instance
