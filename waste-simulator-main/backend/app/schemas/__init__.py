from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut, UserUpdate
from app.schemas.location import LocationCreate, LocationUpdate, LocationOut, HabitationCreate, HabitationUpdate, HabitationOut
from app.schemas.parameters import (
    DemographyIn, DemographyOut,
    InfrastructureIn, InfrastructureOut,
    IndustrialIn, IndustrialOut,
    CompositionIn, CompositionOut
)
from app.schemas.waste import (
    WasteSourceCreate, WasteSourceUpdate, WasteSourceOut,
    FacilityCreate, FacilityUpdate, FacilityOut,
    EventCreate, EventUpdate, EventOut,
    MultiMethodCalculationIn, MultiMethodCalculationOut
)
from app.schemas.historical_waste import HistoricalWasteCreate, HistoricalWasteBulkCreate, HistoricalWasteOut, HistoricalPeriodAnalysisOut
from app.schemas.forecast import ForecastRunIn, ForecastOut
from app.schemas.simulation import StrategyCreate, StrategyOut, ScenarioCreate, ScenarioOut, SimulationRunIn, WhatIfComparisonIn
from app.schemas.gis import GeoJSONFeature, GeoJSONFeatureCollection, GISEnrichmentOut
from app.schemas.chat import ChatIn, ChatOut
from app.schemas.report import ReportCreate, ReportOut, AuditLogOut

__all__ = [
    "UserRegister", "UserLogin", "TokenResponse", "UserOut", "UserUpdate",
    "LocationCreate", "LocationUpdate", "LocationOut", "HabitationCreate", "HabitationUpdate", "HabitationOut",
    "DemographyIn", "DemographyOut", "InfrastructureIn", "InfrastructureOut",
    "IndustrialIn", "IndustrialOut", "CompositionIn", "CompositionOut",
    "WasteSourceCreate", "WasteSourceUpdate", "WasteSourceOut",
    "FacilityCreate", "FacilityUpdate", "FacilityOut",
    "EventCreate", "EventUpdate", "EventOut",
    "MultiMethodCalculationIn", "MultiMethodCalculationOut",
    "HistoricalWasteCreate", "HistoricalWasteBulkCreate", "HistoricalWasteOut", "HistoricalPeriodAnalysisOut",
    "ForecastRunIn", "ForecastOut",
    "StrategyCreate", "StrategyOut", "ScenarioCreate", "ScenarioOut", "SimulationRunIn", "WhatIfComparisonIn",
    "GeoJSONFeature", "GeoJSONFeatureCollection", "GISEnrichmentOut",
    "ChatIn", "ChatOut",
    "ReportCreate", "ReportOut", "AuditLogOut"
]
