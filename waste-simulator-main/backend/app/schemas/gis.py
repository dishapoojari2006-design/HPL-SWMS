from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class GISEnrichmentOut(BaseModel):
    location_id: int
    habitation_id: Optional[int] = None
    enrichment_status: str
    source: str
    source_type: str
    retrieved_time: str
    data_quality: str
    administrative_boundary: Optional[Dict[str, Any]] = None
    roads_summary: Optional[Dict[str, Any]] = None
    nearby_facilities_found: int = 0
    facilities: List[Dict[str, Any]] = Field(default_factory=list)
    notes: str
