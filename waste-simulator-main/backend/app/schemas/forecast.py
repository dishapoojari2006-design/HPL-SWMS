from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ForecastRunIn(BaseModel):
    location_id: int
    habitation_id: Optional[int] = None
    forecast_period: str = Field("NEXT_MONTH", description="NEXT_DAY, NEXT_WEEK, NEXT_MONTH, NEXT_YEAR")
    selected_method: Optional[str] = Field(None, description="AUTO, BASELINE, MOVING_AVERAGE, WEIGHTED_MOVING_AVERAGE, TREND_ADJUSTED, SEASONAL_BASELINE")
    backtest_window_pct: float = Field(20.0, ge=10.0, le=50.0)

class ForecastOut(BaseModel):
    location_id: int
    forecast_period: str
    selected_method: str
    selection_reason: str
    forecast_value: float
    unit: str = "tonnes"
    training_start: Optional[date] = None
    training_end: Optional[date] = None
    historical_points_used: int
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    confidence_level: str
    limitations: str
    method_comparison: List[Dict[str, Any]]
    projected_series: List[Dict[str, Any]]
    created_at: datetime
