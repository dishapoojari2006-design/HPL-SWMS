from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.gis import GeoJSONFeatureCollection, GISEnrichmentOut
from app.services.gis_service import get_geojson_layers, enrich_location_gis

router = APIRouter(prefix="/gis", tags=["GIS and Geospatial"])

@router.get("/layers", response_model=GeoJSONFeatureCollection)
def get_gis_layers(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_geojson_layers(db=db, location_id=location_id)

@router.get("/enrich/{location_id}", response_model=GISEnrichmentOut)
def enrich_gis(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return enrich_location_gis(db=db, location_id=location_id)
