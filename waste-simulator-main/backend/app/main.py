from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import hash_password
from app.models import User, Location, Habitation, WasteSource, Facility
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.models.historical_waste import HistoricalWaste
from datetime import date, datetime, timezone

# Routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.locations import router as locations_router
from app.routers.habitations import router as habitations_router
from app.routers.parameters import router as parameters_router
from app.routers.waste import router as waste_router
from app.routers.waste_sources import router as waste_sources_router
from app.routers.historical_waste import router as historical_waste_router
from app.routers.forecast import router as forecast_router
from app.routers.facilities import router as facilities_router
from app.routers.events import router as events_router
from app.routers.strategies import router as strategies_router
from app.routers.scenarios import router as scenarios_router
from app.routers.simulations import router as simulations_router
from app.routers.gis import router as gis_router
from app.routers.chat import router as chat_router
from app.routers.reports import router as reports_router
from app.routers.audit import router as audit_router
from app.routers.data_quality import router as data_quality_router
from app.routers.legacy import router as legacy_router

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed initial users for all roles if not existing
        users_to_seed = [
            ("Admin User", "admin@swms.org", "Password123!", "SUPER_ADMIN", "ADMINISTRATOR", "State Urban Directorate"),
            ("Municipal Commissioner", "municipal@swms.org", "Password123!", "MUNICIPAL_AUTHORITY", "MUNICIPALITY", "Udupi City Municipal Council"),
            ("Panchayat Development Officer", "panchayat@swms.org", "Password123!", "PANCHAYAT_AUTHORITY", "PANCHAYAT", "Udupi Taluk Gram Panchayat"),
            ("Urban Planner", "planner@swms.org", "Password123!", "PLANNER", "PLANNING_BOARD", "District Planning Office"),
            ("Data Entry Officer", "dataentry@swms.org", "Password123!", "DATA_ENTRY", "FIELD_OFFICE", "Sanitation Field Unit"),
            ("Citizen Viewer", "viewer@swms.org", "Password123!", "VIEWER", "PUBLIC", "Community Observer"),
            ("Test Admin", "admin@example.com", "verysecurepass", "SUPER_ADMIN", "ADMINISTRATOR", "SWMS Core Test")
        ]
        
        for name, email, pwd, role, auth_type, org in users_to_seed:
            if not db.query(User).filter(User.email == email).first():
                db.add(User(
                    name=name,
                    email=email,
                    password_hash=hash_password(pwd),
                    role=role,
                    authority_type=auth_type,
                    organization=org,
                    active=True
                ))
        db.commit()

        # 2. Seed default Location if empty
        loc = db.query(Location).filter(Location.id == 1).first()
        if not loc:
            loc = Location(
                id=1,
                name="Udupi Demonstration",
                location_type="Gram Panchayat",
                country="India",
                state="Karnataka",
                district="Udupi",
                taluk="Udupi",
                panchayat="Udupi Demonstration",
                area=35.5,
                area_unit="sq_km",
                latitude=13.3409,
                longitude=74.7421,
                terrain="Plain",
                classification="RURAL",
                description="Standard demonstration dataset according to SWMS specification",
                data_source="DEMO DATA",
                source_year=2024,
                details={"notes": "Standard demonstration dataset according to SWMS specification"}
            )
            db.add(loc)
            db.commit()
            db.refresh(loc)

        # 3. Seed Habitation
        hab = db.query(Habitation).filter(Habitation.location_id == 1).first()
        if not hab:
            db.add(Habitation(
                location_id=1,
                name="Udupi Central Ward",
                habitation_code="HAB-001",
                population=25000.0,
                households=5500.0,
                area_sq_km=12.5,
                latitude=13.3409,
                longitude=74.7421,
                terrain="Plain",
                road_accessibility="Good",
                data_quality="SURVEYED",
                verification_status="VERIFIED"
            ))
            db.commit()

        # 4. Seed Demography Parameters
        demo = db.query(DemographyParameter).filter(DemographyParameter.habitation_id == 1).first()
        if not demo:
            db.add(DemographyParameter(
                habitation_id=1,
                total_population=25000.0,
                male_population=12400.0,
                female_population=12550.0,
                other_population=50.0,
                population_growth_rate=2.0,
                number_of_households=5500.0,
                average_household_size=4.55,
                population_density=704.2,
                floating_population=2000.0,
                seasonal_population=800.0,
                tourist_population=1500.0,
                migrant_population=500.0,
                pop_reference_year=2024,
                census_source="Census / Local ULB Survey 2024"
            ))
            db.commit()

        # 5. Seed Infrastructure Parameters
        infra = db.query(InfrastructureParameter).filter(InfrastructureParameter.habitation_id == 1).first()
        if not infra:
            db.add(InfrastructureParameter(
                habitation_id=1,
                collection_points=45,
                waste_bins=120,
                community_bins=35,
                vehicle_count=10,
                vehicle_capacity_kg=2000.0,
                trips_per_vehicle=1,
                collection_frequency_days=1,
                collection_coverage_percent=100.0,
                treatment_capacity_kg=10000.0,
                composting_capacity_kg=6000.0,
                recycling_capacity_kg=4000.0,
                mrf_capacity_kg=3000.0,
                wte_capacity_kg=0.0,
                landfill_capacity_kg=15000.0,
                workers_count=28,
                working_hours_day=8.0
            ))
            db.commit()

        # 6. Seed Industrial Parameters
        ind = db.query(IndustrialParameter).filter(IndustrialParameter.habitation_id == 1).first()
        if not ind:
            db.add(IndustrialParameter(
                habitation_id=1,
                number_of_industries=12,
                industrial_waste_kg_day=2000.0,
                industrial_growth_rate=2.0,
                commercial_waste_kg_day=800.0,
                market_waste_kg_day=500.0,
                construction_waste_kg_day=300.0,
                commercial_establishments=140,
                hazardous_category="NONE"
            ))
            db.commit()

        # 7. Seed Waste Composition
        comp = db.query(WasteComposition).filter(WasteComposition.habitation_id == 1).first()
        if not comp:
            db.add(WasteComposition(
                habitation_id=1,
                organic_percent=50.0,
                food_percent=15.0,
                paper_percent=10.0,
                plastic_percent=10.0,
                glass_percent=4.0,
                metal_percent=3.0,
                textile_percent=4.0,
                ewaste_percent=2.0,
                other_percent=2.0
            ))
            db.commit()

        # 8. Seed Facilities if empty
        if db.query(Facility).filter(Facility.location_id == 1).count() == 0:
            db.add(Facility(
                location_id=1,
                name="Udupi Central Composting Unit",
                facility_type="Composting",
                capacity_kg_day=6000.0,
                current_utilization_kg_day=4500.0,
                operating_status="Operational",
                latitude=13.345,
                longitude=74.745
            ))
            db.add(Facility(
                location_id=1,
                name="Udupi MRF & Recycling Depot",
                facility_type="MRF",
                capacity_kg_day=4000.0,
                current_utilization_kg_day=3000.0,
                operating_status="Operational",
                latitude=13.338,
                longitude=74.739
            ))
            db.commit()

        # 9. Seed Waste Sources if empty
        if db.query(WasteSource).filter(WasteSource.habitation_id == 1).count() == 0:
            db.add(WasteSource(
                habitation_id=1,
                source_type="HOUSEHOLD",
                name="Domestic Residential Wards",
                units_count=5500.0,
                rate_per_unit_kg_day=2.27,
                daily_waste_kg=12500.0,
                organic_pct=50.0,
                recyclable_pct=30.0,
                details={}
            ))
            db.add(WasteSource(
                habitation_id=1,
                source_type="INDUSTRY",
                name="Manipal Industrial Area",
                units_count=12.0,
                rate_per_unit_kg_day=0.0,
                daily_waste_kg=2000.0,
                organic_pct=50.0,
                recyclable_pct=30.0,
                details={}
            ))
            db.add(WasteSource(
                habitation_id=1,
                source_type="HOSPITAL",
                name="District General Hospital",
                units_count=250.0,
                rate_per_unit_kg_day=0.0,
                daily_waste_kg=500.0,
                organic_pct=50.0,
                recyclable_pct=30.0,
                details={}
            ))
            db.add(WasteSource(
                habitation_id=1,
                source_type="MARKET",
                name="Santhekatte Vegetable & Fish Market",
                units_count=80.0,
                rate_per_unit_kg_day=0.0,
                daily_waste_kg=800.0,
                organic_pct=50.0,
                recyclable_pct=30.0,
                details={}
            ))
            db.commit()

        # 10. Seed Historical Time-Series records (30 days of weighbridge measurements)
        if db.query(HistoricalWaste).filter(HistoricalWaste.habitation_id == 1).count() == 0:
            import datetime as dt
            base_date = dt.date(2026, 9, 1)
            quantities = [
                14.2, 14.5, 14.1, 15.0, 15.2, 16.1, 16.4,
                14.3, 14.6, 14.4, 15.1, 15.3, 16.0, 16.5,
                14.5, 14.7, 14.2, 15.2, 15.4, 16.2, 16.8,
                14.4, 14.8, 14.5, 15.3, 15.5, 16.3, 16.6,
                14.6, 15.0
            ]
            for i, qty in enumerate(quantities):
                rec_date = base_date + dt.timedelta(days=i)
                db.add(HistoricalWaste(
                    habitation_id=1,
                    measurement_date=rec_date,
                    period_type="1_DAY",
                    quantity=qty,
                    unit="tonnes",
                    waste_category="MIXED",
                    measurement_method="WEIGHBRIDGE",
                    quality_status="MEASURED",
                    notes="Daily weighbridge verified intake",
                    created_by="System Seeder"
                ))
            db.commit()

    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional decision-support and planning simulator for Urban Local Bodies and Panchayats.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API v1 Routers
api_v1 = FastAPI()
api_v1.include_router(auth_router)
api_v1.include_router(users_router)
api_v1.include_router(locations_router)
api_v1.include_router(habitations_router)
api_v1.include_router(parameters_router)
api_v1.include_router(waste_router)
api_v1.include_router(waste_sources_router)
api_v1.include_router(historical_waste_router)
api_v1.include_router(forecast_router)
api_v1.include_router(facilities_router)
api_v1.include_router(events_router)
api_v1.include_router(strategies_router)
api_v1.include_router(scenarios_router)
api_v1.include_router(simulations_router)
api_v1.include_router(gis_router)
api_v1.include_router(chat_router)
api_v1.include_router(reports_router)
api_v1.include_router(audit_router)
api_v1.include_router(data_quality_router)
api_v1.include_router(legacy_router)

# Mount both under /api/v1 and top-level for backwards compatibility
app.mount("/api/v1", api_v1)
app.include_router(legacy_router, prefix="/api/v1")
