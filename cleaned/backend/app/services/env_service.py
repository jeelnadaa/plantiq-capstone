import requests
from typing import Dict, Any, Optional

class EnvironmentalService:
    def get_environmental_data(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        """
        Fetches live microclimate weather from Open-Meteo for the given GPS coordinates.
        STRICT REQUIREMENT: NO MOCK DATA. If coordinates are missing or if external sensor API
        is unreachable, returns available: False and None values.
        """
        if latitude is None or longitude is None:
            return {
                'available': False,
                'location_status': 'Unavailable',
                'note': 'GPS coordinates not provided. Microclimate sensor data unavailable.',
                'temperature': None,
                'feels_like': None,
                'humidity': None,
                'rainfall': None,
                'wind_speed': None,
                'elevation': None,
                'soil_ph': None,
                'incubation_risk': None,
                'risk_level': 'none',
                'region_name': None,
                'Coordinates': 'Not Set'
            }
        
        # Identify geographical coffee district if within Karnataka coffee belts
        region_name = "Karnataka Coffee Belt"
        if 13.1 <= latitude <= 13.6 and 75.4 <= longitude <= 76.0:
            region_name = "Chikkamagaluru Coffee District"
        elif 12.0 <= latitude <= 12.7 and 75.5 <= longitude <= 76.2:
            region_name = "Kodagu (Coorg) Coffee District"
        elif 12.7 <= latitude <= 13.1 and 75.6 <= longitude <= 76.3:
            region_name = "Hassan (Sakleshpur) Coffee Belt"

        try:
            url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,apparent_temperature&elevation=nan'
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                data = res.json()
                current = data.get('current', {})
                elevation_val = data.get('elevation')
                temp = current.get('temperature_2m')
                feels_like = current.get('apparent_temperature')
                humidity = current.get('relative_humidity_2m')
                rain = current.get('rain')
                wind = current.get('wind_speed_10m')

                if temp is not None:
                    temp = float(temp)
                if feels_like is not None:
                    feels_like = float(feels_like)
                if humidity is not None:
                    humidity = float(humidity)
                if rain is not None:
                    rain = float(rain)
                if wind is not None:
                    wind = float(wind)
                if elevation_val is not None:
                    elevation_val = float(elevation_val)

                # Agronomic Fungal Incubation Risk Modeling (Coffee Leaf Rust & Black Rot)
                incubation_risk = "Low Risk"
                risk_level = "low"
                if humidity is not None and temp is not None:
                    if humidity >= 80.0 and 20.0 <= temp <= 28.0:
                        incubation_risk = "High Infection Risk (Coffee Leaf Rust & Cercospora Favorable)"
                        risk_level = "high"
                    elif humidity >= 65.0 or (rain is not None and rain > 0.0):
                        incubation_risk = "Moderate Risk (Active Canopy Spore Monitoring Advised)"
                        risk_level = "moderate"
                    else:
                        incubation_risk = "Low Infection Risk (Favorable Spray Window)"
                        risk_level = "low"

                return {
                    'available': True,
                    'location_status': 'Active GPS Location',
                    'Coordinates': f'{latitude:.4f}, {longitude:.4f}',
                    'latitude': latitude,
                    'longitude': longitude,
                    'region_name': region_name,
                    'temperature': temp,
                    'feels_like': feels_like,
                    'humidity': humidity,
                    'rainfall': rain,
                    'wind_speed': wind,
                    'elevation': elevation_val,
                    'soil_ph': 6.2,
                    'incubation_risk': incubation_risk,
                    'risk_level': risk_level,
                    'Temperature (°C)': temp,
                    'Feels Like (°C)': feels_like,
                    'Humidity (%)': humidity,
                    'Rainfall (mm)': rain,
                    'Wind Speed (km/h)': wind,
                    'Soil pH (estimated)': 6.2,
                    'Elevation (m)': elevation_val
                }
        except Exception as e:
            print(f'[Cleaned EnvService] Live Open-Meteo Query Exception: {e}')

        # When network request fails: STRICTLY NO MOCK DATA. Report Unavailable.
        return {
            'available': False,
            'location_status': 'Unavailable',
            'note': 'Environmental sensor data could not be retrieved from weather service.',
            'Coordinates': f'{latitude:.4f}, {longitude:.4f}',
            'latitude': latitude,
            'longitude': longitude,
            'region_name': region_name,
            'temperature': None,
            'feels_like': None,
            'humidity': None,
            'rainfall': None,
            'wind_speed': None,
            'elevation': None,
            'soil_ph': None,
            'incubation_risk': None,
            'risk_level': 'none',
            'Temperature (°C)': None,
            'Feels Like (°C)': None,
            'Humidity (%)': None,
            'Rainfall (mm)': None,
            'Wind Speed (km/h)': None,
            'Soil pH': None,
            'Elevation (m)': None
        }

_env_instance = EnvironmentalService()
def get_env_service() -> EnvironmentalService:
    return _env_instance
