from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import ConfigDict, BaseModel, Field

class HistoricalWasteCreate(BaseModel):
    habitation_id: int
    source_id: Optional[int] = None
    measurement_date: date
    period_type: str = Field("1_DAY", description="1_DAY, 2_DAYS, 1_WEEK, 2_WEEKS, 1_MONTH, 3_MONTHS, 6_MONTHS, 1_YEAR, 2_YEARS, CUSTOM")
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    quantity: float = Field(..., ge=0, description="Quantity of waste recorded, must be non-negative")
    unit: str = "tonnes"
    waste_category: str = "MIXED"
    measurement_method: str = "WEIGHBRIDGE"
    data_source_id: Optional[int] = None
    quality_status: str = "MEASURED"
    notes: Optional[str] = None
    created_by: Optional[str] = None

class HistoricalWasteBulkCreate(BaseModel):
    records: List[HistoricalWasteCreate]

class HistoricalWasteOut(HistoricalWasteCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class HistoricalPeriodAnalysisOut(BaseModel):
    period_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    records_count: int
    total_quantity_tonnes: float
    daily_average_tonnes: float
    median_tonnes: Optional[float] = None
    minimum_tonnes: Optional[float] = None
    maximum_tonnes: Optional[float] = None
    std_dev: Optional[float] = None
    trend_direction: str = "STABLE"
    percentage_change: Optional[float] = None
    weekday_pattern: Optional[Dict[str, float]] = None
    source_breakdown: Optional[Dict[str, float]] = None
    composition_estimate: Optional[Dict[str, float]] = None
    yoy_growth_percent: Optional[float] = None
    data_quality_summary: Dict[str, Any]
    daily_time_series: List[Dict[str, Any]]
