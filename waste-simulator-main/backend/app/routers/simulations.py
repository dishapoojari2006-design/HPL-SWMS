from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.simulation import SimulationRun
from app.models.location import Location
from app.models.strategy_scenario import Strategy
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter
from app.schemas.simulation import SimulationRunIn, WhatIfComparisonIn
from app.services.simulation_service import run_multi_year_simulation, run_what_if_analysis
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/simulations", tags=["20-Year Simulation Engine"])

PLANNER_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"]

def _execute_simulation(
    sim_in: SimulationRunIn,
    db: Session,
    user: User
):
    if not db.get(Location, sim_in.location_id):
        raise HTTPException(status_code=404, detail="Location not found.")

    strat_params = None
    if sim_in.strategy_id:
        strat = db.get(Strategy, sim_in.strategy_id)
        if strat:
            strat_params = {
                "collection_efficiency_pct": strat.collection_efficiency_pct,
                "target_segregation_percent": strat.segregation_efficiency_pct,
                "additional_treatment_capacity_kg": strat.treatment_capacity_kg
            }

    # Enrich from DB parameters if not provided in request
    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == sim_in.location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == sim_in.location_id))
    ind = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == sim_in.location_id))

    enriched_params = {}
    if demo:
        enriched_params.update({
            "total_population": demo.total_population,
            "households": demo.number_of_households,
            "floating_population": demo.floating_population or 0.0,
            "tourist_population": demo.tourist_population or 0.0,
            "seasonal_population": demo.seasonal_population or 0.0,
            "migrant_population": demo.migrant_population or 0.0,
            "population_growth_rate": getattr(demo, "population_growth_rate", 2.0) or 2.0,
        })
    if infra:
        enriched_params.update({
            "vehicle_count": infra.vehicle_count,
            "vehicle_capacity_kg": infra.vehicle_capacity_kg,
            "trips_per_vehicle": infra.trips_per_vehicle,
            "collection_coverage_percent": infra.collection_coverage_percent,
            "treatment_capacity_kg": infra.treatment_capacity_kg,
            "segregation_percent": getattr(infra, "segregation_percent", 60.0) or 60.0,
        })
    if ind:
        enriched_params.update({
            "industrial_waste_kg_day": getattr(ind, "industrial_waste_kg_day", 0.0) or 0.0,
            "commercial_waste_kg_day": getattr(ind, "commercial_waste_kg_day", 0.0) or 0.0,
            "market_waste_kg_day": getattr(ind, "market_waste_kg_day", 0.0) or 0.0,
            "industrial_growth_rate": getattr(ind, "industrial_growth_rate", 2.0) or 2.0,
        })

    # The caller's parameters override the DB parameters
    final_params = {**enriched_params, **sim_in.parameters}

    results = run_multi_year_simulation(
        params=final_params,
        years=sim_in.years,
        scenario_overrides=sim_in.scenario_overrides,
        strategy_params=strat_params
    )

    run = SimulationRun(
        location_id=sim_in.location_id,
        strategy_id=sim_in.strategy_id,
        years=sim_in.years,
        parameters=final_params,
        results=results
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="RUN_SIMULATION",
        module="SIMULATIONS",
        record_id=run.id,
        details={"years": sim_in.years, "cumulative_20yr_tonnes": results["total_cumulative_20yr_tonnes"]}
    )

    return {"simulation_id": run.id, "results": run.results}

@router.post("", status_code=status.HTTP_201_CREATED)
def run_simulation(
    sim_in: SimulationRunIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PLANNER_ROLES))
):
    return _execute_simulation(sim_in, db, user)

@router.post("/run", status_code=status.HTTP_200_OK)
def run_simulation_endpoint(
    sim_in: SimulationRunIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PLANNER_ROLES))
):
    return _execute_simulation(sim_in, db, user)

@router.post("/what-if")
def run_what_if(
    what_if_in: WhatIfComparisonIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return run_what_if_analysis(
        baseline_params=what_if_in.baseline_parameters,
        overrides=what_if_in.what_if_overrides,
        years=what_if_in.years
    )

@router.get("/latest/{location_id}")
def get_latest_simulation(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    run = db.scalar(
        select(SimulationRun)
        .where(SimulationRun.location_id == location_id)
        .order_by(SimulationRun.created_at.desc())
    )
    if not run:
        raise HTTPException(status_code=404, detail="No simulation runs found for this location.")
    return {"simulation_id": run.id, "results": run.results, "created_at": run.created_at}

@router.get("/{run_id}")
def get_simulation_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    run = db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return {"simulation_id": run.id, "results": run.results, "created_at": run.created_at}
