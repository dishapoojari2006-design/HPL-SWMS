"""Enterprise-Grade Master Database Seeder for SWMS.

Populates all aspects of data across the platform:
- Administrative Locations (Urban, Semi-Urban, Rural)
- Multi-tier Habitations & Wards
- Comprehensive Demographic Parameters (permanent, floating, tourist, seasonal, migrant)
- Complete Infrastructure Parameters (collection points, bins, fleet, treatment, workforce)
- Industrial Parameters (industries, industrial waste, commercial, market, construction, hazard)
- Waste Physical Composition Breakdown (organic, food, paper, plastic, glass, metal, textile, ewaste, other)
- Bulk Waste Generators (Hotels, Hospitals, Markets, Institutions, Industries)
- Solid Waste Treatment & Processing Facilities (Composting, MRF, Biogas, Landfill, CBWTF)
- Seasonal Events, Festivals & Inundation Peaks
- Multi-Month Historical Weighbridge Time-Series Records
- Statistical Forecast Benchmark Models (Linear, Holt-Winters, ARIMA, SARIMAX)
- Long-Term Municipal Strategies & What-If Policy Scenarios
- Disaster & Environmental Emergency Events (Cyclones, Floods, Chemical Spills)
- Disaster Impacts & Day-by-Day Dynamic Debris Analyses
- Designated Emergency Shelters & Evacuation Centers
- Disaster Planning Scenarios
- Published Municipal Decision-Support Reports
- User Directory & Comprehensive Audit Trail
"""
from datetime import date, datetime, timedelta, timezone
from math import sin, pi
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models import (
    User,
    Location,
    Habitation,
    DemographyParameter,
    InfrastructureParameter,
    IndustrialParameter,
    WasteComposition,
    WasteSource,
    Facility,
    Event,
    HistoricalWaste,
    ForecastRecord,
    Strategy,
    Scenario,
    DataSource,
    AuditLog,
    Report,
    DisasterEvent,
    DisasterImpact,
    EmergencyShelter,
    DisasterDailyAnalysis,
    DisasterScenario,
)

def seed_enterprise_data():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        print("[SEED-SWMS] Starting comprehensive enterprise data population...")

        # -------------------------------------------------------------
        # 1. Official Data Sources
        # -------------------------------------------------------------
        data_sources = [
            ("GOVERNMENT_CENSUS", "Census of India & Projected Demographic Model", 2024, "https://censusindia.gov.in", "DOC-CENSUS-2024-KA"),
            ("MUNICIPAL_AUDIT", "State Urban Development Directorate Annual Waste Audit", 2024, "https://urban.karnataka.gov.in", "DOC-SWM-AUDIT-2024"),
            ("POLLUTION_CONTROL", "Karnataka State Pollution Control Board (KSPCB) Compliance Register", 2024, "https://kspcb.karnataka.gov.in", "DOC-KSPCB-HW-2024"),
            ("DISASTER_MANAGEMENT", "District Disaster Management Authority (DDMA) Coastal Masterplan", 2024, "https://ndma.gov.in", "DOC-DDMA-UDUPI-2024"),
            ("CENTRAL_STANDARDS", "Central Pollution Control Board (CPCB) SWM Rules 2016 Guidelines", 2024, "https://cpcb.nic.in", "DOC-CPCB-SWM-2016"),
        ]
        for stype, name, yr, url, dref in data_sources:
            if not db.query(DataSource).filter(DataSource.name == name).first():
                db.add(DataSource(
                    source_type=stype,
                    name=name,
                    source_year=yr,
                    reference_url=url,
                    document_ref=dref,
                    notes="Verified benchmark data source for official municipal planning",
                    data_quality="OFFICIAL",
                    verification_status="VERIFIED"
                ))
        db.commit()

        # -------------------------------------------------------------
        # 2. Administrative Locations (Urban, Semi-Urban, Rural)
        # -------------------------------------------------------------
        locations_data = [
            {
                "id": 1,
                "name": "Udupi City Municipal Council",
                "location_type": "City Municipal Council",
                "country": "India",
                "state": "Karnataka",
                "district": "Udupi",
                "taluk": "Udupi",
                "panchayat": "Udupi Urban Authority",
                "area": 68.2,
                "area_unit": "sq_km",
                "latitude": 13.3409,
                "longitude": 74.7421,
                "terrain": "Coastal Plain",
                "classification": "URBAN",
                "description": "Primary district headquarters, major administrative, commercial, and educational urban center.",
                "data_source": "District Urban Directorate Survey 2024",
                "source_year": 2024,
                "details": {"wards_count": 35, "zone": "Coastal Karnataka", "swm_tier": "Tier-2 Urban"}
            },
            {
                "id": 2,
                "name": "Malpe Coastal & Port Authority",
                "location_type": "Town Panchayat",
                "country": "India",
                "state": "Karnataka",
                "district": "Udupi",
                "taluk": "Udupi",
                "panchayat": "Malpe Coastal Local Body",
                "area": 18.5,
                "area_unit": "sq_km",
                "latitude": 13.3512,
                "longitude": 74.7045,
                "terrain": "Coastal Strip / Port",
                "classification": "SEMI_URBAN",
                "description": "Major commercial fishing harbor, tourism destination (Malpe Beach), seafood processing cluster.",
                "data_source": "Coastal Zone Management Authority 2024",
                "source_year": 2024,
                "details": {"harbor_berths": 450, "tourist_peak_season": "October-May", "swm_tier": "Coastal Semi-Urban"}
            },
            {
                "id": 3,
                "name": "Brahmavar Agro-Industrial Hub",
                "location_type": "Town Panchayat",
                "country": "India",
                "state": "Karnataka",
                "district": "Udupi",
                "taluk": "Brahmavar",
                "panchayat": "Brahmavar Local Body",
                "area": 28.4,
                "area_unit": "sq_km",
                "latitude": 13.4320,
                "longitude": 74.7470,
                "terrain": "Plain River Basin",
                "classification": "SEMI_URBAN",
                "description": "Agricultural market hub, agro-processing units, sugar factory zone, transit corridor on NH-66.",
                "data_source": "Taluk Panchayat Data 2024",
                "source_year": 2024,
                "details": {"apmc_market_yards": 2, "industry_presence": "Medium", "swm_tier": "Agro Semi-Urban"}
            },
            {
                "id": 4,
                "name": "Belapu Model Green Gram Panchayat",
                "location_type": "Gram Panchayat",
                "country": "India",
                "state": "Karnataka",
                "district": "Udupi",
                "taluk": "Kaup",
                "panchayat": "Belapu Gram Panchayat",
                "area": 14.8,
                "area_unit": "sq_km",
                "latitude": 13.2680,
                "longitude": 74.7890,
                "terrain": "Rolling Hills & Agricultural Valley",
                "classification": "RURAL",
                "description": "Award-winning model green panchayat with 100% door-to-door segregation and decentralized biomethanation.",
                "data_source": "SBM-Gramin National Portal 2024",
                "source_year": 2024,
                "details": {"model_panchayat": True, "green_rating": "5-Star", "swm_tier": "Rural Eco-Panchayat"}
            },
            {
                "id": 5,
                "name": "Hebri Western Ghats Foothills Panchayat",
                "location_type": "Gram Panchayat",
                "country": "India",
                "state": "Karnataka",
                "district": "Udupi",
                "taluk": "Hebri",
                "panchayat": "Hebri Gram Panchayat",
                "area": 48.0,
                "area_unit": "sq_km",
                "latitude": 13.4680,
                "longitude": 75.0120,
                "terrain": "Hilly / Forest Fringe",
                "classification": "RURAL",
                "description": "Eco-sensitive buffer zone at the foothills of Western Ghats with dispersed rural settlements and eco-tourism.",
                "data_source": "Forest Buffer Zone Survey 2024",
                "source_year": 2024,
                "details": {"forest_cover_pct": 65, "wildlife_buffer": True, "swm_tier": "Eco-Sensitive Rural"}
            }
        ]

        for l_data in locations_data:
            existing_loc = db.query(Location).filter(Location.id == l_data["id"]).first()
            if not existing_loc:
                loc = Location(**l_data)
                db.add(loc)
            else:
                for k, v in l_data.items():
                    setattr(existing_loc, k, v)
        db.commit()

        # -------------------------------------------------------------
        # 3. Multi-tier Habitations / Wards
        # -------------------------------------------------------------
        habitations_data = [
            # Udupi CMC
            {"location_id": 1, "name": "City Center & Temple Square Ward", "habitation_code": "UDU-W01", "population": 42000.0, "households": 9300.0, "area_sq_km": 14.5, "latitude": 13.3409, "longitude": 74.7421, "terrain": "Plain", "road_accessibility": "High", "data_quality": "VERIFIED"},
            {"location_id": 1, "name": "Manipal University Town & Tech Park", "habitation_code": "UDU-W02", "population": 55000.0, "households": 11500.0, "area_sq_km": 22.0, "latitude": 13.3525, "longitude": 74.7885, "terrain": "Plateau", "road_accessibility": "High", "data_quality": "VERIFIED"},
            {"location_id": 1, "name": "Kadiyali-Bailoor Residential Sector", "habitation_code": "UDU-W03", "population": 28000.0, "households": 6200.0, "area_sq_km": 16.2, "latitude": 13.3320, "longitude": 74.7560, "terrain": "Plain", "road_accessibility": "Good", "data_quality": "VERIFIED"},
            {"location_id": 1, "name": "Santhekatte Market & Transit Hub", "habitation_code": "UDU-W04", "population": 20000.0, "households": 4500.0, "area_sq_km": 15.5, "latitude": 13.3750, "longitude": 74.7350, "terrain": "Plain", "road_accessibility": "High", "data_quality": "VERIFIED"},

            # Malpe Town
            {"location_id": 2, "name": "Malpe Commercial Fisheries Harbor", "habitation_code": "MLP-W01", "population": 16000.0, "households": 3400.0, "area_sq_km": 6.2, "latitude": 13.3512, "longitude": 74.7045, "terrain": "Coastal Harbor", "road_accessibility": "Good", "data_quality": "VERIFIED"},
            {"location_id": 2, "name": "Vadabhandeshwara Beach & Resort Zone", "habitation_code": "MLP-W02", "population": 12000.0, "households": 2600.0, "area_sq_km": 7.5, "latitude": 13.3600, "longitude": 74.6980, "terrain": "Beach Strip", "road_accessibility": "Good", "data_quality": "VERIFIED"},
            {"location_id": 2, "name": "Thottam Coastal Settlement", "habitation_code": "MLP-W03", "population": 10000.0, "households": 2100.0, "area_sq_km": 4.8, "latitude": 13.3720, "longitude": 74.7080, "terrain": "Coastal Lowland", "road_accessibility": "Moderate", "data_quality": "VERIFIED"},

            # Brahmavar
            {"location_id": 3, "name": "Brahmavar Central Market Ward", "habitation_code": "BRH-W01", "population": 24000.0, "households": 5200.0, "area_sq_km": 12.4, "latitude": 13.4320, "longitude": 74.7470, "terrain": "Plain", "road_accessibility": "High", "data_quality": "VERIFIED"},
            {"location_id": 3, "name": "Chanthar Agricultural Sector", "habitation_code": "BRH-W02", "population": 18000.0, "households": 3900.0, "area_sq_km": 16.0, "latitude": 13.4450, "longitude": 74.7620, "terrain": "River Basin", "road_accessibility": "Good", "data_quality": "VERIFIED"},

            # Belapu Model GP
            {"location_id": 4, "name": "Belapu Central Eco-Village", "habitation_code": "BLP-H01", "population": 5200.0, "households": 1150.0, "area_sq_km": 8.5, "latitude": 13.2680, "longitude": 74.7890, "terrain": "Rolling Farmland", "road_accessibility": "Good", "data_quality": "VERIFIED"},
            {"location_id": 4, "name": "Paniyur Rural Settlement", "habitation_code": "BLP-H02", "population": 3300.0, "households": 750.0, "area_sq_km": 6.3, "latitude": 13.2550, "longitude": 74.7980, "terrain": "Farmland", "road_accessibility": "Good", "data_quality": "VERIFIED"},

            # Hebri GP
            {"location_id": 5, "name": "Hebri Gateway Settlement", "habitation_code": "HBR-H01", "population": 7500.0, "households": 1650.0, "area_sq_km": 22.0, "latitude": 13.4680, "longitude": 75.0120, "terrain": "Hilly Valley", "road_accessibility": "Moderate", "data_quality": "VERIFIED"},
            {"location_id": 5, "name": "Someshwara Eco-Buffer Hamlet", "habitation_code": "HBR-H02", "population": 4500.0, "households": 980.0, "area_sq_km": 26.0, "latitude": 13.4920, "longitude": 75.0450, "terrain": "Forest Fringe", "road_accessibility": "Challenging", "data_quality": "SURVEYED"},
        ]

        for h in habitations_data:
            if not db.query(Habitation).filter(Habitation.habitation_code == h["habitation_code"]).first():
                db.add(Habitation(
                    location_id=h["location_id"],
                    name=h["name"],
                    habitation_code=h["habitation_code"],
                    population=h["population"],
                    households=h["households"],
                    area_sq_km=h["area_sq_km"],
                    latitude=h["latitude"],
                    longitude=h["longitude"],
                    terrain=h["terrain"],
                    road_accessibility=h["road_accessibility"],
                    data_quality=h["data_quality"],
                    verification_status="VERIFIED"
                ))
        db.commit()

        # -------------------------------------------------------------
        # 4. Demographic Parameters
        # -------------------------------------------------------------
        demo_configs = [
            (1, 145000.0, 71500.0, 73200.0, 300.0, 2.1, 32200.0, 4.5, 2126.0, 25000.0, 5000.0, 15000.0, 6000.0),
            (2, 38000.0, 19200.0, 18750.0, 50.0, 1.8, 8100.0, 4.7, 2054.0, 8000.0, 12000.0, 18000.0, 5000.0),
            (3, 42000.0, 20800.0, 21150.0, 50.0, 1.9, 9100.0, 4.6, 1478.0, 6500.0, 2500.0, 3000.0, 2000.0),
            (4, 8500.0, 4180.0, 4310.0, 10.0, 1.2, 1900.0, 4.47, 574.0, 800.0, 400.0, 500.0, 300.0),
            (5, 12000.0, 5950.0, 6030.0, 20.0, 1.4, 2630.0, 4.56, 250.0, 1200.0, 800.0, 2500.0, 400.0),
        ]
        for loc_id, pop, m, f, o, gr, hh, hsz, dens, flt, sea, trst, mig in demo_configs:
            demo_rec = db.query(DemographyParameter).filter(DemographyParameter.habitation_id == loc_id).first()
            if not demo_rec:
                db.add(DemographyParameter(
                    habitation_id=loc_id,
                    total_population=pop,
                    male_population=m,
                    female_population=f,
                    other_population=o,
                    population_growth_rate=gr,
                    number_of_households=hh,
                    average_household_size=hsz,
                    population_density=dens,
                    floating_population=flt,
                    seasonal_population=sea,
                    tourist_population=trst,
                    migrant_population=mig,
                    pop_reference_year=2024,
                    census_source="Census 2011 & 2024 ULB Projection Model"
                ))
            else:
                demo_rec.total_population = pop
                demo_rec.male_population = m
                demo_rec.female_population = f
                demo_rec.other_population = o
                demo_rec.population_growth_rate = gr
                demo_rec.number_of_households = hh
                demo_rec.average_household_size = hsz
                demo_rec.population_density = dens
                demo_rec.floating_population = flt
                demo_rec.seasonal_population = sea
                demo_rec.tourist_population = trst
                demo_rec.migrant_population = mig
        db.commit()

        # -------------------------------------------------------------
        # 5. Infrastructure Parameters
        # -------------------------------------------------------------
        infra_configs = [
            (1, 240, 850, 420, 28, 2000.0, 2, 1, 88.5, 65000.0, 35000.0, 15000.0, 20000.0, 0.0, 45000.0, 185, 8.0),
            (2, 65, 220, 110, 8, 2000.0, 2, 1, 82.0, 18000.0, 8000.0, 4000.0, 6000.0, 0.0, 12000.0, 52, 8.0),
            (3, 75, 260, 130, 9, 2000.0, 2, 1, 79.0, 19000.0, 10000.0, 4500.0, 5000.0, 0.0, 14000.0, 58, 8.0),
            (4, 25, 90, 45, 3, 1200.0, 1, 1, 95.0, 6000.0, 4500.0, 1500.0, 2000.0, 0.0, 1000.0, 18, 7.5),
            (5, 35, 110, 55, 4, 1500.0, 1, 1, 72.0, 5500.0, 3500.0, 1200.0, 1500.0, 0.0, 2000.0, 22, 7.5),
        ]
        for loc_id, cpts, bins, cbins, vcnt, vcap, vtrips, freq, cov, tcap, ccap, rcap, mcap, wcap, lcap, wrk, hrs in infra_configs:
            infra_rec = db.query(InfrastructureParameter).filter(InfrastructureParameter.habitation_id == loc_id).first()
            if not infra_rec:
                db.add(InfrastructureParameter(
                    habitation_id=loc_id,
                    collection_points=cpts,
                    waste_bins=bins,
                    community_bins=cbins,
                    vehicle_count=vcnt,
                    vehicle_capacity_kg=vcap,
                    trips_per_vehicle=vtrips,
                    collection_frequency_days=freq,
                    collection_coverage_percent=cov,
                    treatment_capacity_kg=tcap,
                    composting_capacity_kg=ccap,
                    recycling_capacity_kg=rcap,
                    mrf_capacity_kg=mcap,
                    wte_capacity_kg=wcap,
                    landfill_capacity_kg=lcap,
                    workers_count=wrk,
                    working_hours_day=hrs
                ))
            else:
                infra_rec.collection_points = cpts
                infra_rec.waste_bins = bins
                infra_rec.community_bins = cbins
                infra_rec.vehicle_count = vcnt
                infra_rec.vehicle_capacity_kg = vcap
                infra_rec.trips_per_vehicle = vtrips
                infra_rec.collection_frequency_days = freq
                infra_rec.collection_coverage_percent = cov
                infra_rec.treatment_capacity_kg = tcap
                infra_rec.composting_capacity_kg = ccap
                infra_rec.recycling_capacity_kg = rcap
                infra_rec.mrf_capacity_kg = mcap
                infra_rec.wte_capacity_kg = wcap
                infra_rec.landfill_capacity_kg = lcap
                infra_rec.workers_count = wrk
                infra_rec.working_hours_day = hrs
        db.commit()

        # -------------------------------------------------------------
        # 6. Industrial Parameters
        # -------------------------------------------------------------
        ind_configs = [
            (1, 62, 5200.0, 2.5, 4500.0, 3800.0, 8500.0, 850, "LOW_TO_MEDIUM"),
            (2, 38, 7800.0, 3.2, 3200.0, 5500.0, 4200.0, 320, "ORGANIC_MARINE"),
            (3, 49, 6100.0, 2.8, 2800.0, 3400.0, 3800.0, 410, "AGRO_INDUSTRIAL"),
            (4, 5, 450.0, 1.2, 350.0, 250.0, 600.0, 35, "NONE"),
            (5, 8, 680.0, 1.5, 450.0, 380.0, 800.0, 52, "NONE"),
        ]
        for loc_id, n_ind, i_wst, i_gr, c_wst, m_wst, cn_wst, c_est, h_cat in ind_configs:
            ind_rec = db.query(IndustrialParameter).filter(IndustrialParameter.habitation_id == loc_id).first()
            if not ind_rec:
                db.add(IndustrialParameter(
                    habitation_id=loc_id,
                    number_of_industries=n_ind,
                    industrial_waste_kg_day=i_wst,
                    industrial_growth_rate=i_gr,
                    commercial_waste_kg_day=c_wst,
                    market_waste_kg_day=m_wst,
                    construction_waste_kg_day=cn_wst,
                    commercial_establishments=c_est,
                    hazardous_category=h_cat
                ))
            else:
                ind_rec.number_of_industries = n_ind
                ind_rec.industrial_waste_kg_day = i_wst
                ind_rec.industrial_growth_rate = i_gr
                ind_rec.commercial_waste_kg_day = c_wst
                ind_rec.market_waste_kg_day = m_wst
                ind_rec.construction_waste_kg_day = cn_wst
                ind_rec.commercial_establishments = c_est
                ind_rec.hazardous_category = h_cat
        db.commit()

        # -------------------------------------------------------------
        # 7. Waste Composition Breakdown
        # -------------------------------------------------------------
        comp_configs = [
            (1, 52.0, 18.0, 11.0, 14.0, 4.0, 3.0, 3.5, 1.5, 7.0),
            (2, 62.0, 22.0, 7.5, 13.0, 3.5, 2.5, 2.5, 1.0, 8.0),
            (3, 56.0, 19.0, 9.5, 12.0, 3.5, 3.0, 3.0, 1.0, 12.0),
            (4, 71.0, 25.0, 6.0, 8.5, 2.0, 1.5, 2.0, 0.5, 8.5),
            (5, 68.0, 24.0, 6.5, 9.0, 2.5, 1.5, 2.0, 0.5, 10.0),
        ]
        for loc_id, org, fd, ppr, pls, gls, mtl, txt, ewt, oth in comp_configs:
            c_rec = db.query(WasteComposition).filter(WasteComposition.habitation_id == loc_id).first()
            if not c_rec:
                db.add(WasteComposition(
                    habitation_id=loc_id,
                    organic_percent=org,
                    food_percent=fd,
                    paper_percent=ppr,
                    plastic_percent=pls,
                    glass_percent=gls,
                    metal_percent=mtl,
                    textile_percent=txt,
                    ewaste_percent=ewt,
                    other_percent=oth
                ))
            else:
                c_rec.organic_percent = org
                c_rec.food_percent = fd
                c_rec.paper_percent = ppr
                c_rec.plastic_percent = pls
                c_rec.glass_percent = gls
                c_rec.metal_percent = mtl
                c_rec.textile_percent = txt
                c_rec.ewaste_percent = ewt
                c_rec.other_percent = oth
        db.commit()

        # -------------------------------------------------------------
        # 8. Waste Sources (Bulk Waste Generators)
        # -------------------------------------------------------------
        bulk_sources = [
            (1, "HOTEL", "The Ocean Pearl Grand Luxury Hotel", 120.0, 3.8, 456.0, 65.0, 25.0, 13.3420, 74.7450, {"rooms": 120, "banquet": True}),
            (1, "HOSPITAL", "Kasturba Multi-Specialty Hospital Manipal", 1200.0, 1.8, 2160.0, 45.0, 35.0, 13.3530, 74.7880, {"beds": 1200, "cbwtf_linked": True}),
            (1, "MARKET", "Santhekatte APMC Wholesale Produce Market", 160.0, 18.0, 2880.0, 85.0, 10.0, 13.3750, 74.7350, {"vendors": 160, "cold_storage": True}),
            (1, "INSTITUTION", "Manipal Academy of Higher Education Campus", 18000.0, 0.18, 3240.0, 55.0, 35.0, 13.3510, 74.7920, {"hostel_residents": 14000}),
            (1, "COMMERCIAL", "Canara Central Mall & Retail Center", 85.0, 12.0, 1020.0, 35.0, 50.0, 13.3410, 74.7480, {"shops": 85, "food_court": True}),
            (1, "INDUSTRY", "Manipal Universal Printing & Packaging Unit", 1.0, 1250.0, 1250.0, 10.0, 80.0, 13.3550, 74.7950, {"paper_scrap": True}),

            (2, "MARKET", "Malpe Fisheries Harbor Wholesale Auction Yard", 350.0, 22.0, 7700.0, 88.0, 8.0, 13.3512, 74.7045, {"fish_offal": True}),
            (2, "HOTEL", "Paradise Isle Beach Resort & Waterpark", 80.0, 4.2, 336.0, 60.0, 30.0, 13.3600, 74.6980, {"tourist_resort": True}),
            (2, "INDUSTRY", "Coastal Marine Cold Storage & Filleting Co", 1.0, 2400.0, 2400.0, 85.0, 12.0, 13.3540, 74.7060, {"ice_bags": True}),

            (3, "INDUSTRY", "Brahmavar Agro Sugar & Jaggery Factory", 1.0, 3800.0, 3800.0, 80.0, 15.0, 13.4350, 74.7510, {"bagasse": True}),
            (3, "MARKET", "Brahmavar APMC Grains & Vegetable Yard", 90.0, 15.0, 1350.0, 75.0, 18.0, 13.4310, 74.7460, {"produce_sheds": 90}),

            (4, "COMMERCIAL", "Belapu Model Bio-Center & Dairy Cooperative", 1.0, 550.0, 550.0, 90.0, 8.0, 13.2685, 74.7895, {"dairy_dung": True}),
            (5, "HOTEL", "Hebri Eco-Tourism Rainforest Resort", 35.0, 3.5, 122.5, 65.0, 28.0, 13.4700, 75.0150, {"tents": 35}),
        ]
        for hid, stype, name, ucnt, rate, dkg, opct, rpct, lat, lon, dtls in bulk_sources:
            if not db.query(WasteSource).filter(WasteSource.name == name).first():
                db.add(WasteSource(
                    habitation_id=hid,
                    source_type=stype,
                    name=name,
                    units_count=ucnt,
                    rate_per_unit_kg_day=rate,
                    daily_waste_kg=dkg,
                    organic_pct=opct,
                    recyclable_pct=rpct,
                    latitude=lat,
                    longitude=lon,
                    details=dtls
                ))
        db.commit()

        # -------------------------------------------------------------
        # 9. Waste Processing & Treatment Facilities
        # -------------------------------------------------------------
        facilities = [
            (1, "Alevoor Integrated Material Recovery Facility (MRF)", "RECYCLING", 25000.0, 19500.0, "Operational", 13.3180, 74.7620),
            (1, "Baje Water Works Central Composting Plant", "COMPOSTING", 35000.0, 28000.0, "Operational", 13.3650, 74.8120),
            (1, "Santhekatte Market Biomethanation Plant", "BIOGAS", 5000.0, 4200.0, "Operational", 13.3750, 74.7350),
            (1, "Alevoor Scientific Sanitary Landfill Cell-2", "LANDFILL", 45000.0, 24000.0, "Operational", 13.3150, 74.7650),
            (1, "Kaup Regional CBWTF Bio-Medical Waste Facility", "INCINERATOR", 10000.0, 6800.0, "Operational", 13.2250, 74.7450),

            (2, "Malpe Coastal Dry Waste Collection Center", "MRF", 8000.0, 5800.0, "Operational", 13.3550, 74.7080),
            (2, "Malpe Fish Offal Biomethanation Plant", "BIOGAS", 8000.0, 7200.0, "Operational", 13.3490, 74.7020),

            (3, "Brahmavar Regional Composting Hub", "COMPOSTING", 12000.0, 9200.0, "Operational", 13.4350, 74.7520),

            (4, "Belapu Zero-Waste Village Vermicomposting Center", "COMPOSTING", 4500.0, 3100.0, "Operational", 13.2680, 74.7890),
            (4, "Belapu Community Biogas Grid", "BIOGAS", 2000.0, 1500.0, "Operational", 13.2690, 74.7910),

            (5, "Hebri Decentralized Composting Shed", "COMPOSTING", 3500.0, 2200.0, "Operational", 13.4680, 75.0120),
        ]
        for lid, fname, ftype, cap, load, st, lat, lon in facilities:
            if not db.query(Facility).filter(Facility.name == fname).first():
                db.add(Facility(
                    location_id=lid,
                    name=fname,
                    facility_type=ftype,
                    capacity_kg_day=cap,
                    current_utilization_kg_day=load,
                    operating_status=st,
                    latitude=lat,
                    longitude=lon
                ))
        db.commit()

        # -------------------------------------------------------------
        # 10. Seasonal Events, Festivals & Surge Peaks
        # -------------------------------------------------------------
        events_data = [
            (1, "Biennial Paryaya Temple Pilgrimage Festival", "FESTIVAL", 120000.0, 150000.0, 10, 45.0, {"notes": "Major pilgrimage; leaf plates and floral organic waste."}),
            (1, "Karavali Cultural & Heritage Utsav", "CULTURAL", 35000.0, 25000.0, 7, 25.0, {"notes": "Beverage cans, wrappers, and street food packaging surge."}),
            (1, "Southwest Monsoon Storm Drainage Sediment Surge", "WEATHER", 5000.0, 8000.0, 45, 30.0, {"notes": "Stormwater canal cleaning and silt deposits."}),

            (2, "Malpe Beach Winter Carnival & Water Sports Fest", "TOURISM", 45000.0, 35000.0, 5, 40.0, {"notes": "Extreme surge in beach plastic litter and PET bottles."}),
            (2, "Peak Trawl Fishing Season Harvest", "SEASONAL", 8000.0, 12000.0, 90, 35.0, {"notes": "Fish offal and ice-melt packaging surge."}),

            (3, "Brahmavar APMC Annual Agricultural Harvest Fair", "COMMERCIAL", 25000.0, 18000.0, 4, 20.0, {"notes": "Produce crates, straw, packaging, and commercial waste surge."}),
            (4, "Belapu Grama Utsava & Organic Farmers Convention", "CULTURAL", 12000.0, 8000.0, 3, 15.0, {"notes": "Zero-waste eco dining showcase."}),
            (5, "Hebri Rainforest Ecotourism Trekking Season", "TOURISM", 2000.0, 2500.0, 60, 15.0, {"notes": "Strict trail plastic checks."}),
        ]
        for hid, ename, etype, att, add_p, dur, winc, dtls in events_data:
            if not db.query(Event).filter(Event.name == ename).first():
                db.add(Event(
                    habitation_id=hid,
                    name=ename,
                    event_type=etype,
                    expected_attendance=att,
                    additional_population=add_p,
                    duration_days=dur,
                    waste_increase_percent=winc,
                    details=dtls
                ))
        db.commit()

        # -------------------------------------------------------------
        # 11. Historical Weighbridge Time-Series (90 Days per Location)
        # -------------------------------------------------------------
        base_date = date.today() - timedelta(days=90)
        for loc_id in [1, 2, 3, 4, 5]:
            count_hist = db.query(HistoricalWaste).filter(HistoricalWaste.habitation_id == loc_id).count()
            if count_hist < 30:
                base_tons = {1: 72.5, 2: 24.0, 3: 22.5, 4: 4.2, 5: 5.8}[loc_id]
                for day_idx in range(90):
                    curr_date = base_date + timedelta(days=day_idx)
                    weekday = curr_date.weekday()
                    day_factor = 1.08 if weekday in [5, 6] else (0.95 if weekday == 0 else 1.0)
                    seasonal_factor = 1.0 + 0.08 * sin(day_idx * pi / 30.0)
                    variance = 0.95 + ((day_idx * 7) % 11) / 100.0
                    daily_tons = round(base_tons * day_factor * seasonal_factor * variance, 2)

                    db.add(HistoricalWaste(
                        habitation_id=loc_id,
                        measurement_date=curr_date,
                        period_type="1_DAY",
                        quantity=daily_tons,
                        unit="tonnes",
                        waste_category="MIXED",
                        measurement_method="WEIGHBRIDGE",
                        quality_status="MEASURED",
                        notes=f"Weighbridge entry for {curr_date.isoformat()}",
                        created_by="Automated Weighbridge SCADA"
                    ))
        db.commit()

        # -------------------------------------------------------------
        # 12. Strategic Plans & Scenarios
        # -------------------------------------------------------------
        strategies_data = [
            (1, "Mission Swachh 2030: 100% Source Segregation & Decentralized MRF", "Comprehensive", 94.0, 85.0, 55.0, 75000.0, 45000000.0, 1.25, "Complete transition to segregated door-to-door collection with 3-bin source segregation and automated MRF optical sorting."),
            (1, "Zero-Landfill Circular Economy & Compost Quality Certification", "Treatment Upgrade", 90.0, 78.0, 45.0, 65000.0, 28000000.0, 1.15, "Upgrading windrow composting with bio-inoculant acceleration and organic fertilizer market certification."),
            (1, "Electric Fleet Transition & AI Route Optimization", "Logistics", 95.0, 70.0, 35.0, 50000.0, 32000000.0, 1.35, "Replacing diesel tipper autos with 35 battery-electric smart tippers linked to GIS route navigation."),

            (2, "Coastal Plastic Interception & Marine Offal Biogas Grid", "Marine Environmental", 88.0, 75.0, 50.0, 22000.0, 18000000.0, 1.40, "Dedicated harbor offal collection fleet with beach containment nets and compressed biogas bottling."),
            (3, "Agro-Waste Biomass Pelletization & Sugar Industry Synergy", "Circular Economy", 85.0, 70.0, 48.0, 24000.0, 15000000.0, 1.20, "Converting agricultural residue and sugarcane bagasse into combustible industrial biomass briquettes."),
            (4, "Gram Panchayat Carbon-Neutral Decentralized Model", "Rural Eco", 98.0, 92.0, 70.0, 8000.0, 4500000.0, 1.50, "Zero-waste village model with community vermicomposting and decentralized graywater bio-swales."),
            (5, "Foothills Eco-Buffer Community Waste & Deterrence Plan", "Eco-Sensitive", 82.0, 75.0, 42.0, 7000.0, 5500000.0, 1.30, "Animal-proof community waste reception bins and localized composting along forest boundaries."),
        ]
        for loc_id, sname, stype, c_eff, s_eff, div_pct, t_cap, cost, env_fac, nts in strategies_data:
            if not db.query(Strategy).filter(Strategy.name == sname).first():
                db.add(Strategy(
                    location_id=loc_id,
                    name=sname,
                    strategy_type=stype,
                    collection_efficiency_pct=c_eff,
                    segregation_efficiency_pct=s_eff,
                    diversion_percent=div_pct,
                    treatment_capacity_kg=t_cap,
                    estimated_cost_inr=cost,
                    environmental_factor=env_fac,
                    notes=nts
                ))
        db.commit()

        scenarios_data = [
            (1, "Rapid Urbanization & Tech Corridor Expansion (+3.8% Pop Growth)", "Growth", {"population_growth_rate": 3.8, "waste_per_person_per_day": 0.58, "industrial_growth_rate": 4.5}),
            (1, "Strict Single-Use Plastics Enforcement (-45% Plastic Waste)", "Policy", {"plastic_reduction_pct": 45.0, "segregation_percent": 82.0, "waste_per_person_per_day": 0.46}),
            (1, "Pilgrimage Tourism Surge (+80% Peak Season Floating Pop)", "Tourism", {"floating_population": 45000.0, "tourist_population": 30000.0, "seasonal_factor": 1.35}),

            (2, "Harbor Expansion & Seafood Processing Boom (+60% Marine Waste)", "Industrial", {"industrial_waste_kg_day": 12500.0, "seasonal_population": 18000.0}),
            (3, "NH-66 Highway Logistics Corridor Urbanization", "Growth", {"population_growth_rate": 3.2, "commercial_waste_kg_day": 4500.0}),
            (4, "100% Organic Village Export Certification", "Policy", {"segregation_percent": 96.0, "diversion_percent": 85.0}),
            (5, "Rainforest Eco-Trekking Influx Surge", "Tourism", {"tourist_population": 6500.0, "seasonal_factor": 1.25}),
        ]
        for loc_id, scname, sctype, ovrds in scenarios_data:
            if not db.query(Scenario).filter(Scenario.name == scname).first():
                db.add(Scenario(
                    location_id=loc_id,
                    name=scname,
                    scenario_type=sctype,
                    overrides=ovrds
                ))
        db.commit()

        # -------------------------------------------------------------
        # 13. Statistical Forecasting Benchmarks
        # -------------------------------------------------------------
        forecast_configs = [
            (1, "Holt-Winters Triple Exponential Smoothing", "90_DAYS", 78.4, 1.85, 2.40, 3.1, "HIGH", "Selected for robust seasonal decomposition across weekly and festival cycles."),
            (1, "ARIMA(2,1,2) Autoregressive Moving Average", "90_DAYS", 77.8, 2.10, 2.75, 3.6, "HIGH", "Stationary differenced model capturing long-term trends and autocorrelation."),
            (1, "Linear Trend Regression", "90_DAYS", 76.5, 3.20, 4.15, 5.4, "MEDIUM", "Baseline demographic trajectory benchmark."),

            (2, "Holt-Winters Additive Seasonality", "90_DAYS", 26.2, 0.95, 1.30, 4.2, "HIGH", "Captures coastal fishing seasonal surge and weekend tourism peaks."),
            (3, "ARIMA(1,1,1) Time-Series Model", "90_DAYS", 23.8, 0.85, 1.15, 3.8, "HIGH", "Modeled on agricultural market weighbridge intakes."),
            (4, "Exponential Growth Projection", "90_DAYS", 4.3, 0.15, 0.22, 2.8, "HIGH", "Captures steady organic rural growth."),
            (5, "Seasonal Decomposition Method", "90_DAYS", 6.1, 0.25, 0.35, 4.1, "HIGH", "Trekking season and monsoon silt variance integration."),
        ]
        for loc_id, meth, per, fval, mae, rmse, mape, conf, rsn in forecast_configs:
            if not db.query(ForecastRecord).filter(
                ForecastRecord.location_id == loc_id,
                ForecastRecord.method_used == meth
            ).first():
                db.add(ForecastRecord(
                    location_id=loc_id,
                    habitation_id=loc_id,
                    forecast_period=per,
                    method_used=meth,
                    training_start=base_date,
                    training_end=date.today(),
                    forecast_value=fval,
                    unit="tonnes",
                    mae=mae,
                    rmse=rmse,
                    mape=mape,
                    confidence_level=conf,
                    selection_reason=rsn,
                    limitations="Subject to extreme climate anomalies and unscheduled major political/religious events.",
                    details={"seasonal_periods": 7, "damped": False}
                ))
        db.commit()

        # -------------------------------------------------------------
        # 14. Disaster & Environmental Emergency Management
        # -------------------------------------------------------------
        disasters = [
            {
                "location_id": 1,
                "disaster_type": "Cyclone",
                "name": "Very Severe Cyclonic Storm Tauktae-Grade Coastal Impact",
                "start_date": date(2026, 6, 10),
                "end_date": date(2026, 6, 17),
                "duration_days": 7,
                "severity": "EXTREME",
                "warning_level": "RED",
                "affected_area_sqkm": 42.0,
                "affected_population": 45000.0,
                "displaced_population": 12500.0,
                "temporary_population": 8000.0,
                "phase": "IMMEDIATE_RESPONSE",
                "status": "ACTIVE_DISASTER",
                "source": "India Meteorological Department (IMD) / DDMA",
                "notes": "Coastal storm surge, sustained winds of 130 km/h, widespread uprooted trees, damaged roofing sheets, and power disruption.",
                "impact": {
                    "infrastructure_damage_factor": 0.35,
                    "road_access_factor": 0.45,
                    "collection_access_factor": 0.50,
                    "vehicle_availability_factor": 0.65,
                    "collection_efficiency_factor": 0.55,
                    "waste_generation_factor": 1.40,
                    "treatment_capacity_factor": 0.60,
                    "disposal_capacity_factor": 0.70,
                    "additional_waste_pct": 40.0,
                    "debris_factor": 18.5,
                    "emergency_waste_factor": 1.8,
                    "notes": "Severe debris clearance required on Arterial Roads NH-66 and Temple Square."
                }
            },
            {
                "location_id": 1,
                "disaster_type": "Flood",
                "name": "Swarna River Monsoon Flash Flood & Inundation",
                "start_date": date(2026, 7, 22),
                "end_date": date(2026, 7, 27),
                "duration_days": 5,
                "severity": "HIGH",
                "warning_level": "ORANGE",
                "affected_area_sqkm": 28.0,
                "affected_population": 22000.0,
                "displaced_population": 6500.0,
                "temporary_population": 4000.0,
                "phase": "RECOVERY",
                "status": "PLANNED_DISASTER",
                "source": "State Natural Disaster Monitoring Center (KSNDMC)",
                "notes": "Low-lying wards along the riverbank inundated by 1.5m floodwaters, resulting in waterlogged silt, mud, and damaged household items.",
                "impact": {
                    "infrastructure_damage_factor": 0.25,
                    "road_access_factor": 0.55,
                    "collection_access_factor": 0.60,
                    "vehicle_availability_factor": 0.75,
                    "collection_efficiency_factor": 0.65,
                    "waste_generation_factor": 1.30,
                    "treatment_capacity_factor": 0.75,
                    "disposal_capacity_factor": 0.80,
                    "additional_waste_pct": 30.0,
                    "debris_factor": 12.0,
                    "emergency_waste_factor": 1.5,
                    "notes": "Massive silt accumulation in stormwater drains and basements."
                }
            },
            {
                "location_id": 2,
                "disaster_type": "Other",
                "name": "NH-66 Hazardous Material Chemical Transport Tanker Spill",
                "start_date": date(2026, 8, 14),
                "end_date": date(2026, 8, 17),
                "duration_days": 3,
                "severity": "HIGH",
                "warning_level": "RED",
                "affected_area_sqkm": 5.0,
                "affected_population": 6000.0,
                "displaced_population": 1800.0,
                "temporary_population": 1200.0,
                "phase": "IMMEDIATE_RESPONSE",
                "status": "ACTIVE_DISASTER",
                "source": "District HAZMAT Emergency Response Unit",
                "notes": "Corrosive chemical spill near the harbor transit junction requiring specialized hazardous absorbent, neutralizers, and evacuation.",
                "impact": {
                    "infrastructure_damage_factor": 0.15,
                    "road_access_factor": 0.30,
                    "collection_access_factor": 0.40,
                    "vehicle_availability_factor": 0.70,
                    "collection_efficiency_factor": 0.50,
                    "waste_generation_factor": 1.20,
                    "treatment_capacity_factor": 0.50,
                    "disposal_capacity_factor": 0.60,
                    "additional_waste_pct": 20.0,
                    "debris_factor": 6.5,
                    "emergency_waste_factor": 2.2,
                    "notes": "Hazardous absorbent materials must be segregated from municipal solid waste and dispatched to TSDF."
                }
            }
        ]

        for d_info in disasters:
            impact_info = d_info.pop("impact")
            existing_event = db.query(DisasterEvent).filter(DisasterEvent.name == d_info["name"]).first()
            if not existing_event:
                d_event = DisasterEvent(**d_info)
                db.add(d_event)
                db.flush()

                d_impact = DisasterImpact(
                    disaster_event_id=d_event.id,
                    **impact_info
                )
                db.add(d_impact)

                base_d = d_info["start_date"]
                for day_n in range(1, d_info["duration_days"] + 1):
                    c_date = base_d + timedelta(days=day_n - 1)
                    normal_t = 72.5
                    temp_pop_t = round((d_info["temporary_population"] * 0.8) / 1000.0, 2)
                    disaster_add_t = round(normal_t * (impact_info["additional_waste_pct"] / 100.0), 2)
                    debris_t = impact_info["debris_factor"] * (1.2 if day_n <= 3 else 0.8)
                    total_gen = round(normal_t + temp_pop_t + disaster_add_t + debris_t, 2)

                    eff_coll_cap = round(total_gen * impact_info["collection_efficiency_factor"], 2)
                    coll_t = min(total_gen, eff_coll_cap)
                    uncoll_t = round(total_gen - coll_t, 2)
                    accum_t = round(uncoll_t * day_n * 0.7, 2)

                    eff_treat_cap = round(coll_t * impact_info["treatment_capacity_factor"], 2)
                    treated_t = min(coll_t, eff_treat_cap)
                    t_gap = round(coll_t - treated_t, 2)

                    db.add(DisasterDailyAnalysis(
                        disaster_event_id=d_event.id,
                        day_number=day_n,
                        date=c_date,
                        normal_waste_tonnes=normal_t,
                        temporary_pop_waste_tonnes=temp_pop_t,
                        disaster_additional_waste_tonnes=disaster_add_t,
                        debris_cleanup_waste_tonnes=debris_t,
                        total_generated_tonnes=total_gen,
                        effective_collection_cap_tonnes=eff_coll_cap,
                        collected_tonnes=coll_t,
                        uncollected_tonnes=uncoll_t,
                        cumulative_accumulated_tonnes=accum_t,
                        effective_treatment_cap_tonnes=eff_treat_cap,
                        treated_tonnes=treated_t,
                        treatment_gap_tonnes=t_gap,
                        effective_vehicles_required=34,
                        vehicle_deficit=8
                    ))
        db.commit()

        # -------------------------------------------------------------
        # 15. Designated Emergency Shelters & Evacuation Centers
        # -------------------------------------------------------------
        shelters_data = [
            (1, "Udupi Town Hall Central Evacuation Camp", "SHELTER-UDU-01", 1200, 950, 0.65, 13.3420, 74.7450, "ACTIVE", "Equipped with 24 bio-toilets, RO drinking water, and segregated waste collection bins."),
            (1, "Board High School Relief Center & Kitchen", "SHELTER-UDU-02", 800, 680, 0.60, 13.3380, 74.7410, "ACTIVE", "Central mass community kitchen; daily wet food waste exceeds 450 kg."),
            (1, "Manipal Indoor Sports Stadium Mega-Shelter", "SHELTER-UDU-03", 2500, 0, 0.55, 13.3540, 74.7890, "STANDBY", "Primary high-capacity standby shelter for mass coastal evacuation."),
            (1, "Kadiyali Community Welfare Bhavan", "SHELTER-UDU-04", 500, 420, 0.58, 13.3310, 74.7550, "ACTIVE", "Neighborhood shelter with localized composting pit."),

            (2, "Malpe Coastal Cyclone Relief Center", "SHELTER-MLP-01", 1000, 820, 0.70, 13.3520, 74.7060, "ACTIVE", "Elevated multi-hazard cyclone shelter with emergency generator and medical bay."),
            (2, "Vadabhandeshwara High School Shelter", "SHELTER-MLP-02", 600, 480, 0.62, 13.3610, 74.6990, "ACTIVE", "Temporary shelter for displaced beachfront fishermen families."),

            (3, "Brahmavar Taluk Community Hall Relief Post", "SHELTER-BRH-01", 750, 520, 0.55, 13.4330, 74.7480, "ACTIVE", "Equipped for agricultural flood evacuees."),

            (4, "Belapu Model Disaster Resilience Center", "SHELTER-BLP-01", 450, 0, 0.50, 13.2685, 74.7895, "STANDBY", "Solar-powered rural emergency shelter."),
            (5, "Hebri Foothills Emergency Transit Camp", "SHELTER-HBR-01", 600, 310, 0.52, 13.4690, 75.0130, "ACTIVE", "Flash flood and landslide transit shelter."),
        ]
        for loc_id, sname, scode, cap, curr_p, wrate, lat, lon, st, nts in shelters_data:
            if not db.query(EmergencyShelter).filter(EmergencyShelter.name == sname).first():
                db.add(EmergencyShelter(
                    location_id=loc_id,
                    name=sname,
                    shelter_code=scode,
                    capacity_persons=cap,
                    current_population=curr_p,
                    waste_per_person_kg_day=wrate,
                    latitude=lat,
                    longitude=lon,
                    start_date=date(2026, 6, 10),
                    status=st,
                    source="Taluk Disaster Relief Officer",
                    notes=nts
                ))
        db.commit()

        # -------------------------------------------------------------
        # 16. Disaster Planning Scenarios
        # -------------------------------------------------------------
        disaster_scenarios = [
            (1, "Category 4 Coastal Super-Cyclone Window", "Cyclone", "EXTREME", 10, 65000.0, 22000.0, 15000.0, 35.0, 45.0, 50.0, 60.0, 28.5, {"surge_height_m": 3.5, "wind_speed_kmh": 165}),
            (1, "Swarna River 100-Year Flood Basin Inundation", "Flood", "HIGH", 7, 35000.0, 11000.0, 7500.0, 48.0, 55.0, 65.0, 40.0, 16.0, {"rain_24h_mm": 320, "drain_backlog_pct": 75}),
            (2, "Malpe Fisheries Harbor Tsunami Inundation Surge", "Tsunami", "EXTREME", 14, 28000.0, 14000.0, 9500.0, 25.0, 35.0, 40.0, 75.0, 35.0, {"saline_silt_tonnes": 450.0}),
            (3, "Agro-Industrial Chemical Explosion & Fire", "Other", "HIGH", 4, 12000.0, 4500.0, 3000.0, 40.0, 50.0, 55.0, 30.0, 8.5, {"toxic_ash_tonnes": 45.0}),
        ]
        for loc_id, scname, dtype, sev, dur, aff, disp, shelt, r_acc, c_eff, t_cap, a_wst, d_t, pms in disaster_scenarios:
            if not db.query(DisasterScenario).filter(DisasterScenario.name == scname).first():
                db.add(DisasterScenario(
                    location_id=loc_id,
                    name=scname,
                    disaster_type=dtype,
                    severity=sev,
                    duration_days=dur,
                    affected_population=aff,
                    displaced_population=disp,
                    shelter_population=shelt,
                    road_access_pct=r_acc,
                    collection_efficiency_pct=c_eff,
                    treatment_capacity_pct=t_cap,
                    additional_waste_pct=a_wst,
                    debris_tonnes_day=d_t,
                    parameters=pms
                ))
        db.commit()

        # -------------------------------------------------------------
        # 17. Published Municipal Decision-Support Reports
        # -------------------------------------------------------------
        reports = [
            (1, "Annual Comprehensive Municipal Solid Waste Audit Report 2026", "ANNUAL_AUDIT", {
                "generated_annual_tonnes": 26462.5,
                "collected_tonnes": 23420.0,
                "treated_tonnes": 19800.0,
                "landfill_diverted_pct": 75.2,
                "compliance_score": 92.4,
                "major_recommendation": "Expand automated MRF sorting and deploy 15 additional electric collection tippers."
            }),
            (1, "Multi-Hazard Disaster Debris & Environmental Contingency Plan", "DISASTER_PLAN", {
                "high_risk_zones": ["Coastal Ward 1", "Riverine Lowlands Ward 4"],
                "debris_staging_sites": ["Alevoor Emergency Yard", "Santhekatte Deposition Grounds"],
                "emergency_fleet_mobilization": 38,
                "safe_shelter_capacity": 5500
            }),
            (2, "Coastal Marine Plastics & Harbor Offal Management Action Plan", "COASTAL_PLAN", {
                "annual_marine_waste_tonnes": 8760.0,
                "biodigester_utilization_pct": 88.0,
                "beach_cleanliness_index": "Grade-A"
            }),
            (4, "Rural Gram Panchayat SBM Model Verification & Carbon Credits Audit", "RURAL_GREEN", {
                "organic_diversion_pct": 94.0,
                "vermicompost_produced_tonnes": 480.0,
                "biogas_households_connected": 320
            })
        ]
        for loc_id, title, rtype, rdata in reports:
            if not db.query(Report).filter(Report.title == title).first():
                db.add(Report(
                    location_id=loc_id,
                    title=title,
                    report_type=rtype,
                    data=rdata,
                    created_at=datetime.now(timezone.utc)
                ))
        db.commit()

        # -------------------------------------------------------------
        # 18. Audit Trail Records
        # -------------------------------------------------------------
        audit_events = [
            ("Admin User", 1, "INITIALIZE_DATABASE", "SYSTEM", 1, {"status": "SUCCESS", "version": "2.0.0"}),
            ("Municipal Commissioner", 2, "APPROVE_ANNUAL_PLAN", "PLANNING", 1, {"target_collection_pct": 95.0}),
            ("Panchayat Development Officer", 3, "VERIFY_DEMOGRAPHY", "DEMOGRAPHY", 4, {"verified_households": 1900}),
            ("Urban Planner", 4, "RUN_LONG_TERM_SIMULATION", "SIMULATION", 1, {"horizon_years": 20, "breach_year": 2038}),
            ("Emergency Planner", 7, "ACTIVATE_DISASTER_PROTOCOL", "DISASTERS", 1, {"disaster": "Cyclone Tauktae Grade", "shelters_activated": 4}),
            ("Data Entry Officer", 5, "RECORD_WEIGHBRIDGE_BATCH", "HISTORICAL_WASTE", 1, {"records_logged": 90, "tonnes_total": 6525.0}),
        ]
        for uname, uid, act, mod, recid, dtls in audit_events:
            db.add(AuditLog(
                user_name=uname,
                user_id=uid,
                action=act,
                module=mod,
                record_id=recid,
                details=dtls,
                timestamp=datetime.now(timezone.utc)
            ))
        db.commit()

        print("[SEED-SWMS] Enterprise database population finished successfully!")

    except Exception as e:
        db.rollback()
        print(f"[SEED-SWMS ERROR] Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_data()
