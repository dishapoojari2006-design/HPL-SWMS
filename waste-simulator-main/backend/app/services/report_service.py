from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.location import Location
from app.models.habitation import Habitation
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.models.waste_source import WasteSource
from app.models.facility import Facility
from app.models.historical_waste import HistoricalWaste
from app.models.simulation import SimulationRun
from app.models.event import Event
from app.services.time_series_service import analyze_time_series_records
from app.services.forecasting_service import run_forecast_evaluation

def generate_comprehensive_report(db: Session, location_id: int) -> Dict[str, Any]:
    loc = db.get(Location, location_id)
    if not loc:
        raise ValueError(f"Location {location_id} not found")

    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == location_id))
    ind = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == location_id))
    comp = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == location_id))
    
    habitations = db.scalars(select(Habitation).where(Habitation.location_id == location_id)).all()
    sources = db.scalars(select(WasteSource).where(WasteSource.habitation_id == location_id)).all()
    facilities = db.scalars(select(Facility).where(Facility.location_id == location_id)).all()
    events = db.scalars(select(Event).where(Event.habitation_id == location_id)).all()
    
    hist_records = db.scalars(select(HistoricalWaste).where(HistoricalWaste.habitation_id == location_id)).all()
    hist_dicts = [{
        "measurement_date": r.measurement_date,
        "quantity": r.quantity,
        "waste_category": r.waste_category,
        "quality_status": r.quality_status
    } for r in hist_records]
    time_series_summary = analyze_time_series_records(hist_dicts, period_type="ALL_RECORDS")

    latest_sim = db.scalar(
        select(SimulationRun)
        .where(SimulationRun.location_id == location_id)
        .order_by(SimulationRun.created_at.desc())
    )

    forecast_eval = run_forecast_evaluation(hist_dicts, period="NEXT_MONTH")

    completeness_fields = [
        bool(loc.latitude and loc.longitude),
        bool(demo and demo.total_population > 0),
        bool(infra and infra.vehicle_count > 0),
        bool(comp),
        len(sources) > 0,
        len(facilities) > 0,
        len(hist_records) > 0
    ]
    data_quality_pct = round(sum(completeness_fields) / len(completeness_fields) * 100, 1)

    return {
        "metadata": {
            "title": f"SWMS Comprehensive Waste Master Plan — {loc.name}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "location_name": loc.name,
            "location_type": loc.location_type,
            "district": loc.district,
            "state": loc.state,
            "data_quality_percent": data_quality_pct
        },
        "demographics": {
            "total_population": demo.total_population if demo else 0,
            "households": demo.number_of_households if demo else 0,
            "growth_rate_pct": demo.population_growth_rate if demo else 2.0,
            "floating_population": (demo.floating_population + demo.tourist_population) if demo else 0
        },
        "infrastructure": {
            "collection_vehicles": infra.vehicle_count if infra else 0,
            "vehicle_capacity_kg": infra.vehicle_capacity_kg if infra else 0,
            "collection_coverage_pct": infra.collection_coverage_percent if infra else 100.0,
            "installed_treatment_kg_day": sum(f.capacity_kg_day for f in facilities)
        },
        "waste_composition": {
            "organic_percent": comp.organic_percent if comp else 50.0,
            "food_percent": comp.food_percent if comp else 15.0,
            "recyclable_percent": (comp.paper_percent + comp.plastic_percent + comp.glass_percent + comp.metal_percent) if comp else 27.0,
            "other_percent": comp.other_percent if comp else 8.0
        },
        "waste_sources_count": len(sources),
        "active_facilities_count": len(facilities),
        "scheduled_events_count": len(events),
        "historical_waste_analytics": time_series_summary,
        "forecasting_outlook": {
            "forecast_value_tonnes_day": forecast_eval.get("forecast_value"),
            "selected_method": forecast_eval.get("selected_method"),
            "confidence_level": forecast_eval.get("confidence_level"),
            "selection_reason": forecast_eval.get("selection_reason")
        },
        "simulation_summary": latest_sim.results if latest_sim else None
    }
