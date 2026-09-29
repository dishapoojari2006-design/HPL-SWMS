import os
os.environ["DATABASE_URL"] = "sqlite:///./test_swms.db"
import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app, Base, engine
from app.services.disaster_engine import (
    calculate_disaster_waste_components,
    run_disaster_multi_day_accumulation,
    run_disaster_what_if_analysis
)
from app.services.emergency_waste_service import (
    calculate_shelter_waste,
    estimate_disaster_debris_breakdown
)

Base.metadata.create_all(engine)
client = TestClient(app)

def get_auth_header():
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Disaster Planner",
            "email": "disaster_admin@swms.org",
            "password": "Password123!",
            "role": "SUPER_ADMIN"
        }
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "disaster_admin@swms.org", "password": "Password123!"}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_disaster_engine_direct_calculation():
    """Verify disaster component breakdown and multi-day accumulation formulas."""
    components = calculate_disaster_waste_components(
        normal_waste_tonnes_day=10.0,
        affected_population=5000.0,
        displaced_population=2000.0,
        shelter_population=1000.0,
        additional_waste_pct=25.0,
        debris_tonnes_day=2.5,
        waste_per_person_kg=0.50
    )
    
    assert components["normal_baseline_waste_tonnes_day"] == 10.0
    assert components["shelter_waste_tonnes_day"] == 0.50
    assert components["debris_cleanup_waste_tonnes_day"] == 2.5
    assert components["total_disaster_waste_tonnes_day"] > 10.0
    
    res = run_disaster_multi_day_accumulation(
        normal_waste_tonnes_day=10.0,
        normal_fleet_capacity_tonnes_day=12.0,
        normal_treatment_capacity_tonnes_day=10.0,
        duration_days=7,
        affected_population=5000.0,
        displaced_population=2000.0,
        shelter_population=1000.0,
        road_access_pct=50.0,
        collection_efficiency_pct=60.0,
        treatment_capacity_pct=80.0,
        additional_waste_pct=25.0,
        debris_tonnes_day=2.5
    )
    
    assert len(res["daily_series"]) == 7
    assert res["duration_days"] == 7
    assert res["peak_accumulated_waste_tonnes"] > 0
    assert res["total_period_generated_tonnes"] > 0
    assert res["total_period_collected_tonnes"] > 0

def test_emergency_shelter_and_debris_service():
    """Verify shelter population waste calculation and empirical debris factors."""
    shelter_res = calculate_shelter_waste(shelter_population=2000, waste_per_person_kg=0.60)
    assert shelter_res["daily_shelter_waste_kg"] == 1200.0
    assert shelter_res["daily_shelter_waste_tonnes"] == 1.20
    
    debris_flood = estimate_disaster_debris_breakdown(
        disaster_type="Flood",
        severity="HIGH",
        affected_area_sqkm=20.0,
        affected_population=5000.0
    )
    assert debris_flood["total_debris_tonnes_day"] > 0
    assert debris_flood["sediment_silt_tonnes_day"] > 0

def test_disaster_endpoints():
    """Test full disaster REST API lifecycle."""
    headers = get_auth_header()
    
    # 1. Create Location
    loc_res = client.post(
        "/api/v1/locations",
        headers=headers,
        json={
            "name": "Disaster Test District",
            "location_type": "Gram Panchayat",
            "latitude": 13.35,
            "longitude": 74.78
        }
    )
    assert loc_res.status_code == 201
    loc_id = loc_res.json()["id"]
    
    # 2. Add Emergency Shelter
    shelter_res = client.post(
        "/api/v1/emergency-shelters",
        headers=headers,
        json={
            "location_id": loc_id,
            "name": "Central High School Camp",
            "shelter_code": "TEST-SH-01",
            "capacity_persons": 600,
            "current_population": 450,
            "waste_per_person_kg_day": 0.55,
            "status": "ACTIVE"
        }
    )
    assert shelter_res.status_code == 201
    
    # 3. List Shelters
    shelters_list = client.get(f"/api/v1/emergency-shelters?location_id={loc_id}", headers=headers)
    assert shelters_list.status_code == 200
    assert len(shelters_list.json()) >= 1
    
    # 4. Create Disaster Event
    disaster_res = client.post(
        "/api/v1/disasters",
        headers=headers,
        json={
            "location_id": loc_id,
            "disaster_type": "Flood",
            "name": "Severe Test Flash Flood",
            "start_date": str(date.today()),
            "duration_days": 7,
            "severity": "HIGH",
            "warning_level": "RED",
            "affected_area_sqkm": 25.0,
            "affected_population": 8000.0,
            "displaced_population": 3000.0,
            "temporary_population": 1500.0,
            "phase": "DURING",
            "status": "ACTIVE_DISASTER"
        }
    )
    assert disaster_res.status_code == 201
    disaster_id = disaster_res.json()["id"]
    
    # 5. Set Disaster Impact factors
    impact_res = client.post(
        f"/api/v1/disasters/{disaster_id}/impact",
        headers=headers,
        json={
            "infrastructure_damage_factor": 0.30,
            "road_access_factor": 0.45,
            "collection_access_factor": 0.50,
            "vehicle_availability_factor": 0.60,
            "collection_efficiency_factor": 0.50,
            "waste_generation_factor": 1.35,
            "treatment_capacity_factor": 0.70,
            "disposal_capacity_factor": 0.65,
            "additional_waste_pct": 35.0,
            "debris_factor": 4.0
        }
    )
    assert impact_res.status_code == 200
    
    # 6. Run Disaster Simulation / Trajectory
    sim_res = client.post(
        f"/api/v1/disasters/{disaster_id}/simulate",
        headers=headers,
        json={"nominal_daily_waste_tonnes": 15.0}
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert len(sim_data["daily_analysis"]) == 7
    assert sim_data["summary"]["peak_accumulated_tonnes"] >= 0
    
    # 7. Run Disaster Analysis simulation endpoint
    analysis_res = client.post(
        "/api/v1/disaster-analysis/simulate",
        headers=headers,
        json={
            "location_id": loc_id,
            "disaster_type": "Flood",
            "severity": "HIGH",
            "duration_days": 7,
            "affected_population": 6000.0,
            "displaced_population": 2500.0,
            "shelter_population": 1200.0,
            "road_access_pct": 50.0,
            "collection_efficiency_pct": 55.0,
            "treatment_capacity_pct": 75.0,
            "additional_waste_pct": 30.0,
            "debris_tonnes_day": 3.0
        }
    )
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert "daily_series" in analysis_data
    assert len(analysis_data["daily_series"]) == 7
