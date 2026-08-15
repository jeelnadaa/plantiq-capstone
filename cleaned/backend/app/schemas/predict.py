from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class DiagnosisResponse(BaseModel):
    cache_hit: bool
    sha256_hash: str
    filename: Optional[str] = None
    disease: str
    confidence: float
    is_healthy: bool
    distribution: Dict[str, float]
    env_data: Optional[Dict[str, Any]] = None
    advisory: str
    sources: Optional[List[str]] = None
    is_blended: bool = False
    reasons: Optional[List[str]] = None
