import urllib.request
import json

def test_live():
    # 1. Health check
    with urllib.request.urlopen("http://localhost:8000/api/v1/health") as resp:
        health = json.loads(resp.read().decode())
        print(f"[LIVE] Backend Health: {health}")

    # 2. Login as Super Admin
    login_data = json.dumps({"email": "admin@swms.org", "password": "Password123!"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8000/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        login_res = json.loads(resp.read().decode())
        token = login_res["access_token"]
        print(f"[LIVE] Logged in as: {login_res['user']['name']} ({login_res['user']['role']})")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def fetch(url):
        r = urllib.request.Request(f"http://localhost:8000{url}", headers=headers)
        with urllib.request.urlopen(r) as res:
            return json.loads(res.read().decode())

    def post(url, payload):
        data = json.dumps(payload).encode("utf-8")
        r = urllib.request.Request(f"http://localhost:8000{url}", data=data, headers=headers)
        with urllib.request.urlopen(r) as res:
            return json.loads(res.read().decode())

    # 3. Locations
    locations = fetch("/api/v1/locations")
    print(f"[LIVE] Total Locations: {len(locations)}")
    for loc in locations:
        print(f"       -> ID {loc['id']}: {loc['name']} [{loc['classification']}]")

    # 4. Disaster Events
    disasters = fetch("/api/v1/disasters")
    print(f"[LIVE] Total Disaster Events: {len(disasters)}")
    for d in disasters:
        print(f"       -> ID {d['id']}: {d.get('name')} [{d.get('disaster_type')}] - Severity: {d.get('severity')}")

    # 5. Emergency Shelters
    shelters = fetch("/api/v1/emergency-shelters")
    print(f"[LIVE] Total Emergency Shelters: {len(shelters)}")

    # 6. Facilities
    facilities = fetch("/api/v1/facilities")
    print(f"[LIVE] Total Waste Facilities: {len(facilities)}")

    # 7. Parameters check
    demo = fetch("/api/v1/parameters/demography/1")
    print(f"[LIVE] Ward 1 Demography: Pop {demo['total_population']}, Households {demo['number_of_households']}")

    # 8. Waste Multi-Method Calculation
    calc = post("/api/v1/waste/calculate-multi-method", {
        "population": 42000.0,
        "waste_per_person_kg_day": 0.52,
        "households": 9500.0,
        "waste_per_household_kg_day": 2.35,
        "floating_population": 8000.0,
        "market_vendors": 120
    })
    print(f"[LIVE] Multi-Method Calculation: Reconciled = {calc['reconciliation']['reconciled_daily_kg']} kg/day ({calc['reconciliation']['reconciled_tonnes_day']} T/day)")

    # 9. 20-Year Simulation
    sim = post("/api/v1/simulations/run", {
        "location_id": 1,
        "horizon_years": 20,
        "params": {
            "population_growth_rate": 2.0,
            "waste_per_capita_kg": 0.52,
            "collection_coverage_pct": 85.0
        }
    })
    print(f"[LIVE] 20-Yr Simulation Run ID {sim['simulation_id']}: Cumulative 20-Yr Tonnes = {sim['results']['total_cumulative_20yr_tonnes']} T")

    # 10. GIS GeoJSON
    gis = fetch("/api/v1/gis/layers?location_id=1")
    print(f"[LIVE] GIS FeatureCollection: {len(gis.get('features', []))} features")

    # 11. Grounded Chatbot
    chat = post("/api/v1/chat", {
        "location_id": 1,
        "question": "What is the population and estimated waste generation?"
    })
    safe_answer = chat['answer'][:120].encode('ascii', 'replace').decode('ascii')
    print(f"[LIVE] Grounded AI Chat Assistant: {safe_answer}...")

    # 12. Audit Logs
    audit = fetch("/api/v1/audit-logs")
    print(f"[LIVE] Audit Logs Count: {len(audit)}")

    # 13. Frontend Check
    with urllib.request.urlopen("http://localhost:5173") as resp:
        print(f"[LIVE] Frontend Dev Server: HTTP {resp.status} OK")

if __name__ == "__main__":
    test_live()
