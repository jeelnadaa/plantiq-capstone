from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IEnvironmentalDataService(ABC):
    @abstractmethod
    def get_environmental_data(
        self, 
        latitude: Optional[float] = None, 
        longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Abstract method to fetch environmental parameters based on geolocation coordinates.
        Returns a dictionary containing metrics such as Temperature, Humidity, Elevation, Rainfall, Soil pH, etc.
        """
        pass
