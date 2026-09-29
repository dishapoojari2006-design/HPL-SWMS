from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import ConfigDict, BaseModel, Field

class StrategyCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=255)
    strategy_type: str = "Combined Strategy"
    collection_efficiency_pct: float = Field(90.0, ge=0, le=100.0)
    segregation_efficiency_pct: float = Field(70.0, ge=0, le=100.0)
    diversion_percent: float = Field(40.0, ge=0, le=100.0)
    treatment_capacity_kg: float = Field(5000.0, ge=0)
    estimated_cost_inr: float = Field(0.0, ge=0)
    environmental_factor: float = Field(1.0, ge=0.1, le=5.0)
    notes: Optional[str] = None

class StrategyOut(StrategyCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ScenarioCreate(BaseModel):
    location_id: int
    name: str = Field(min_length=2, max_length=255)
    scenario_type: str = "Growth Scenario"
    overrides: Dict[str, Any] = Field(default_factory=dict)

class ScenarioOut(ScenarioCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SimulationRunIn(BaseModel):
    location_id: int
    years: int = Field(20, ge=1, le=50)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    scenario_overrides: Dict[str, Any] = Field(default_factory=dict)
    strategy_id: Optional[int] = None

class WhatIfComparisonIn(BaseModel):
    location_id: int
    years: int = Field(20, ge=1, le=50)
    baseline_parameters: Dict[str, Any]
    what_if_overrides: Dict[str, Any]
