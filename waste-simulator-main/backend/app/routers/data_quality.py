from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.location import Location
from app.models.habitation import Habitation
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.models.waste_source import WasteSource
from app.models.facility import Facility
from app.models.historical_waste import HistoricalWaste

router = APIRouter(prefix="/data-quality", tags=["Data Quality Dashboard"])

@router.get("/{location_id}")
def get_data_quality_report(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found.")

    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == location_id))
    ind = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == location_id))
    comp = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == location_id))
    
    habitations = db.scalars(select(Habitation).where(Habitation.location_id == location_id)).all()
    sources = db.scalars(select(WasteSource).where(WasteSource.habitation_id == location_id)).all()
    facilities = db.scalars(select(Facility).where(Facility.location_id == location_id)).all()
    hist_records = db.scalars(select(HistoricalWaste).where(HistoricalWaste.habitation_id == location_id)).all()

    checklist = [
        {"field": "GPS Coordinates", "status": bool(loc.latitude and loc.longitude), "critical": True},
        {"field": "Demography Parameters", "status": bool(demo and demo.total_population > 0), "critical": True},
        {"field": "Household Statistics", "status": bool(demo and demo.number_of_households > 0), "critical": True},
        {"field": "Fleet Infrastructure", "status": bool(infra and infra.vehicle_count > 0), "critical": True},
        {"field": "Vehicle Capacity", "status": bool(infra and infra.vehicle_capacity_kg > 0), "critical": True},
        {"field": "Waste Composition (Sums to 100%)", "status": bool(comp), "critical": False},
        {"field": "Documented Waste Sources", "status": len(sources) > 0, "critical": False},
        {"field": "Registered Treatment Facilities", "status": len(facilities) > 0, "critical": False},
        {"field": "Historical Weighbridge Records", "status": len(hist_records) > 0, "critical": False},
        {"field": "Sub-Habitations / Wards", "status": len(habitations) > 0, "critical": False}
    ]

    completed = sum(1 for item in checklist if item["status"])
    total = len(checklist)
    completeness_pct = round((completed / total) * 100, 1)

    warnings = []
    if not (loc.latitude and loc.longitude):
        warnings.append("Missing geographic coordinates: GIS mapping and enrichment unavailable.")
    if not demo:
        warnings.append("Demographic parameters not recorded: Per-capita waste calculations will use baseline fallbacks.")
    if not infra or infra.vehicle_count <= 0:
        warnings.append("No active collection vehicles configured.")
    if not facilities:
        warnings.append("No treatment facilities registered: 100% of waste will register as treatment deficit.")
    if not hist_records:
        warnings.append("No historical weighbridge records found: Forecasting engine will require manual parameter inputs.")

    return {
        "location_id": location_id,
        "location_name": loc.name,
        "completeness_percent": completeness_pct,
        "status_color": "GREEN" if completeness_pct >= 80 else "YELLOW" if completeness_pct >= 50 else "RED",
        "checklist": checklist,
        "warnings_count": len(warnings),
        "warnings": warnings,
        "critical_issues_count": sum(1 for item in checklist if item["critical"] and not item["status"])
    }
