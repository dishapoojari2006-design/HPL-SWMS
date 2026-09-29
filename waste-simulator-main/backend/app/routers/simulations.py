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
from app.schemas.simulation import SimulationRunIn, WhatIfComparisonIn
from app.services.simulation_service import run_multi_year_simulation, run_what_if_analysis
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/simulations", tags=["20-Year Simulation Engine"])

PLANNER_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"]

@router.post("", status_code=status.HTTP_201_CREATED)
def run_simulation(
    sim_in: SimulationRunIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*PLANNER_ROLES))
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

    results = run_multi_year_simulation(
        params=sim_in.parameters,
        years=sim_in.years,
        scenario_overrides=sim_in.scenario_overrides,
        strategy_params=strat_params
    )

    run = SimulationRun(
        location_id=sim_in.location_id,
        strategy_id=sim_in.strategy_id,
        years=sim_in.years,
        parameters=sim_in.parameters,
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
