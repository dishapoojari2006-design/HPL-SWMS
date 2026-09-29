from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db, is_postgres
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.location import Location
from app.models.planning_record import Record
from app.models.simulation import SimulationRun
from app.calculations import waste_breakdown, collection_plan, transport_plan, treatment_plan
from app.services.chatbot_service import query_swms_assistant

router = APIRouter(tags=["Legacy & Compatibility"])

ALLOWED = {"demography", "infrastructure", "industrial", "environment", "terrain", "economic", "cultural", "habitations", "waste", "events", "strategies", "scenarios"}

class RecordIn(BaseModel):
    payload: Dict[str, Any]

class CalculationIn(BaseModel):
    parameters: Dict[str, Any]
    event_population: float = Field(0, ge=0)
    event_percent: float = Field(0, ge=0, le=100)

class CapacityIn(BaseModel):
    daily_waste_kg: float = Field(ge=0)
    vehicle_count: int = Field(ge=0)
    vehicle_capacity_kg: float = Field(gt=0)
    trips_per_vehicle: int = Field(ge=1)
    collection_coverage_percent: float = Field(100, ge=0, le=100)

class TreatmentIn(BaseModel):
    daily_waste_kg: float = Field(ge=0)
    treatment_capacity_kg: float = Field(ge=0)
    segregation_percent: float = Field(ge=0, le=100)

class ChatIn(BaseModel):
    location_id: int
    question: str = Field(min_length=2, max_length=500)

@router.get("/health")
def health():
    return {"status": "healthy", "database": "configured", "postgis_mode": is_postgres()}

@router.post("/locations/{location_id}/{category}", status_code=status.HTTP_201_CREATED)
def add_record(
    location_id: int,
    category: str,
    x: RecordIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"))
):
    if category not in ALLOWED:
        raise HTTPException(404, "Unknown planning category")
    if not db.get(Location, location_id):
        raise HTTPException(404, "Location not found")
    row = Record(location_id=location_id, category=category, payload=x.payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "location_id": row.location_id, "category": row.category, "payload": row.payload, "created_at": row.created_at.isoformat()}

@router.get("/locations/{location_id}/{category}")
def records(
    location_id: int,
    category: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return [
        {"id": r.id, "location_id": r.location_id, "category": r.category, "payload": r.payload, "created_at": r.created_at.isoformat()}
        for r in db.scalars(select(Record).where(Record.location_id == location_id, Record.category == category)).all()
    ]

@router.put("/records/{record_id}")
def update_record(
    record_id: int,
    x: RecordIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "DATA_ENTRY"))
):
    r = db.get(Record, record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    r.payload = x.payload
    db.commit()
    db.refresh(r)
    return {"id": r.id, "location_id": r.location_id, "category": r.category, "payload": r.payload, "created_at": r.created_at.isoformat()}

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"))
):
    r = db.get(Record, record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    db.delete(r)
    db.commit()

@router.post("/calculations/waste")
def calculate_waste_legacy(x: CalculationIn, user: User = Depends(get_current_user)):
    result = waste_breakdown(x.parameters, event_population=x.event_population, event_percent=x.event_percent)
    composition = x.parameters.get("composition", {})
    if composition and round(sum(composition.values()), 4) != 100:
        raise HTTPException(422, "Waste composition percentages must total 100")
    result["composition"] = {
        k: {"percentage": v, "kg_day": round(result["daily_waste_kg"] * v / 100, 2)}
        for k, v in composition.items()
    }
    return result

@router.post("/calculations/collection")
def calculate_collection_legacy(x: CapacityIn, user: User = Depends(get_current_user)):
    return collection_plan(x.daily_waste_kg, x.vehicle_count, x.vehicle_capacity_kg, x.trips_per_vehicle, x.collection_coverage_percent)

@router.post("/calculations/transportation")
def calculate_transportation_legacy(x: CapacityIn, user: User = Depends(get_current_user)):
    return transport_plan(x.daily_waste_kg, x.vehicle_count, x.vehicle_capacity_kg, x.trips_per_vehicle)

@router.post("/calculations/treatment")
def calculate_treatment_legacy(x: TreatmentIn, user: User = Depends(get_current_user)):
    return treatment_plan(x.daily_waste_kg, x.treatment_capacity_kg, x.segregation_percent)

@router.get("/dashboard/{location_id}")
def dashboard_legacy(location_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = db.scalar(select(SimulationRun).where(SimulationRun.location_id == location_id).order_by(SimulationRun.created_at.desc()))
    records = db.scalars(select(Record).where(Record.location_id == location_id)).all()
    return {
        "location_id": location_id,
        "data_completeness_percent": round(len({r.category for r in records} & set(ALLOWED)) / 7 * 100, 1),
        "latest_simulation": run.results if run else None,
        "record_counts": {c: sum(1 for r in records if r.category == c) for c in ALLOWED}
    }

@router.get("/map")
def map_data_legacy(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    features = []
    for l in db.scalars(select(Location).where(Location.latitude.is_not(None), Location.longitude.is_not(None))).all():
        features.append({
            "type": "Feature",
            "geometry": l.geometry or {"type": "Point", "coordinates": [l.longitude, l.latitude]},
            "properties": {"id": l.id, "name": l.name, "type": l.location_type}
        })
    return {"type": "FeatureCollection", "features": features}

@router.post("/chatbot")
def chatbot_legacy(x: ChatIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    res = query_swms_assistant(db, x.location_id, x.question)
    return {"answer": res["answer"], "evidence": res["evidence"]}
