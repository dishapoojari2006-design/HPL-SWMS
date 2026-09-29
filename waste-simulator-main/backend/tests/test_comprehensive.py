import os
os.environ["DATABASE_URL"] = "sqlite:///./test_swms.db"
import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app, Base, engine

Base.metadata.create_all(engine)
client = TestClient(app)

def get_admin_token():
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Super Auditor",
            "email": "auditor@swms.org",
            "password": "Password123!",
            "role": "SUPER_ADMIN"
        }
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "auditor@swms.org", "password": "Password123!"}
    )
    return res.json()["access_token"]

def get_viewer_token():
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Public Viewer",
            "email": "public_viewer@swms.org",
            "password": "Password123!",
            "role": "VIEWER"
        }
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "public_viewer@swms.org", "password": "Password123!"}
    )
    return res.json()["access_token"]

def test_authentication_and_rbac():
    admin_tok = get_admin_token()
    viewer_tok = get_viewer_token()
    
    # 1. Admin can view current user
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_tok}"})
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "SUPER_ADMIN"
    
    # 2. Viewer cannot create a location (RBAC restriction)
    forbidden_res = client.post(
        "/api/v1/locations",
        headers={"Authorization": f"Bearer {viewer_tok}"},
        json={"name": "Forbidden City", "location_type": "Municipality"}
    )
    assert forbidden_res.status_code == 403

def test_full_planning_and_calculation_pipeline():
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Location
    loc_res = client.post(
        "/api/v1/locations",
        headers=headers,
        json={
            "name": "Audit Test Ward",
            "location_type": "Municipality",
            "latitude": 13.34,
            "longitude": 74.75,
            "classification": "URBAN"
        }
    )
    assert loc_res.status_code == 201
    loc_id = loc_res.json()["id"]
    
    # 2. Add Demography Parameters
    demo_res = client.post(
        "/api/v1/parameters/demography",
        headers=headers,
        json={
            "habitation_id": loc_id,
            "total_population": 30000.0,
            "number_of_households": 6500.0,
            "floating_population": 4000.0,
            "average_household_size": 4.5
        }
    )
    assert demo_res.status_code == 201
    
    # 3. Add Infrastructure Parameters
    infra_res = client.post(
        "/api/v1/parameters/infrastructure",
        headers=headers,
        json={
            "habitation_id": loc_id,
            "vehicle_count": 8,
            "vehicle_capacity_kg": 2000.0,
            "trips_per_vehicle": 1,
            "collection_coverage_percent": 80.0,
            "treatment_capacity_kg": 12000.0
        }
    )
    assert infra_res.status_code == 201
    
    # 4. Multi-Method Waste Calculation
    calc_res = client.post(
        "/api/v1/waste/calculate-multi-method",
        headers=headers,
        json={
            "population": 30000.0,
            "waste_per_person_kg_day": 0.52,
            "households": 6500.0,
            "waste_per_household_kg_day": 2.40,
            "floating_population": 4000.0,
            "market_vendors": 80
        }
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert "method_a_person_based" in calc_data
    assert "method_b_household_based" in calc_data
    assert "reconciliation" in calc_data
    assert calc_data["reconciliation"]["reconciled_daily_kg"] > 0
    
    # 5. Run 20-Year Long-Term Simulation
    sim_res = client.post(
        "/api/v1/simulations/run",
        headers=headers,
        json={
            "location_id": loc_id,
            "horizon_years": 20,
            "params": {
                "population_growth_rate": 2.0,
                "waste_per_capita_kg": 0.52,
                "collection_coverage_pct": 80.0,
                "vehicle_count": 8,
                "vehicle_capacity_kg": 2000.0,
                "treatment_capacity_kg": 12000.0
            }
        }
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert len(sim_data["results"]["years"]) == 21
    assert sim_data["results"]["total_cumulative_20yr_tonnes"] > 0
    
    # 6. GIS GeoJSON Feature Collection
    gis_res = client.get(f"/api/v1/gis/layers?location_id={loc_id}", headers=headers)
    assert gis_res.status_code == 200
    gis_data = gis_res.json()
    assert gis_data["type"] == "FeatureCollection"
    
    # 7. Grounded AI Chat Assistant
    chat_res = client.post(
        "/api/v1/chat",
        headers=headers,
        json={
            "location_id": loc_id,
            "question": "What is the total population and estimated waste generation?"
        }
    )
    assert chat_res.status_code == 200
    chat_body = chat_res.json()
    assert len(chat_body.get("reply") or chat_body.get("answer", "")) > 10
    
    # 8. Audit Log Verification
    audit_res = client.get("/api/v1/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1
