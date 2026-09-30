from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import require_roles, get_current_user
from app.models.user import User
from app.models.historical_waste import HistoricalWaste
from app.models.forecast import ForecastRecord
from app.models.location import Location
from app.schemas.forecast import ForecastRunIn, ForecastOut
from app.services.forecasting_service import run_forecast_evaluation
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/forecast", tags=["Forecasting Engine"])

PLANNER_ROLES = ["SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER"]

@router.post("/run", response_model=ForecastOut)
def run_forecast(
    forecast_in: ForecastRunIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    loc = db.get(Location, forecast_in.location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found.")

    records = db.scalars(
        select(HistoricalWaste)
        .where(HistoricalWaste.habitation_id == forecast_in.location_id)
        .order_by(HistoricalWaste.measurement_date.asc())
    ).all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to calculate the forecast because no historical waste records were found for the selected location. Please record or import historical waste data first."
        )

    hist_dicts = [{
        "measurement_date": r.measurement_date,
        "quantity": r.quantity,
        "waste_category": r.waste_category,
        "quality_status": r.quality_status
    } for r in records]

    result = run_forecast_evaluation(
        historical_points=hist_dicts,
        period=forecast_in.forecast_period,
        selected_method_override=forecast_in.selected_method
    )

    forecast_rec = ForecastRecord(
        location_id=forecast_in.location_id,
        habitation_id=forecast_in.habitation_id,
        forecast_period=forecast_in.forecast_period,
        method_used=result["selected_method"],
        training_start=result["training_start"],
        training_end=result["training_end"],
        forecast_value=result["forecast_value"],
        unit="tonnes",
        mae=result["mae"],
        rmse=result["rmse"],
        mape=result["mape"],
        confidence_level=result["confidence_level"],
        limitations=result["limitations"],
        selection_reason=result["selection_reason"],
        details={
            "method_comparison": result["method_comparison"],
            "points_used": result["historical_points_used"]
        }
    )
    db.add(forecast_rec)
    db.commit()

    log_audit_event(
        db=db,
        user_name=user.name,
        user_id=user.id,
        action="RUN_FORECAST",
        module="FORECAST",
        record_id=forecast_rec.id,
        details={"method": result["selected_method"], "val": result["forecast_value"]}
    )

    return {
        "location_id": forecast_in.location_id,
        "forecast_period": forecast_in.forecast_period,
        "selected_method": result["selected_method"],
        "selection_reason": result["selection_reason"],
        "forecast_value": result["forecast_value"],
        "unit": "tonnes",
        "training_start": result["training_start"],
        "training_end": result["training_end"],
        "historical_points_used": result["historical_points_used"],
        "mae": result["mae"],
        "rmse": result["rmse"],
        "mape": result["mape"],
        "confidence_level": result["confidence_level"],
        "limitations": result["limitations"],
        "method_comparison": result["method_comparison"],
        "projected_series": result["projected_series"],
        "created_at": datetime.now(timezone.utc)
    }

@router.get("/history/{location_id}")
def get_forecast_history(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    recs = db.scalars(
        select(ForecastRecord)
        .where(ForecastRecord.location_id == location_id)
        .order_by(ForecastRecord.created_at.desc())
    ).all()
    return recs
