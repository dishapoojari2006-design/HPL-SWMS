from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.location import Location
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.models.facility import Facility
from app.models.historical_waste import HistoricalWaste
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.waste import MultiMethodCalculationIn, MultiMethodCalculationOut
from app.services.calculation_service import (
    calculate_method_a_person,
    calculate_method_b_household,
    calculate_method_c_measured,
    calculate_method_d_industry,
    calculate_method_e_hospital,
    calculate_method_f_institution,
    calculate_method_g_hotel,
    calculate_method_h_market,
    cross_method_reconcile,
    collection_gap_analysis,
    transport_gap_analysis,
    segregation_gap_analysis,
    treatment_gap_analysis
)

router = APIRouter(prefix="/waste", tags=["Waste Calculations & Multi-Method"])

@router.get("/comprehensive/{location_id}")
def get_comprehensive_waste(location_id: int, db: Session = Depends(get_db)):
    loc = db.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
        
    demo = db.query(DemographyParameter).filter(DemographyParameter.habitation_id == location_id).first()
    infra = db.query(InfrastructureParameter).filter(InfrastructureParameter.habitation_id == location_id).first()
    ind = db.query(IndustrialParameter).filter(IndustrialParameter.habitation_id == location_id).first()
    comp = db.query(WasteComposition).filter(WasteComposition.habitation_id == location_id).first()
    facilities = db.query(Facility).filter(Facility.location_id == location_id).all()
    
    pop = demo.total_population if demo else 25000.0
    floating_pop = demo.floating_population if demo else 2000.0
    per_capita = 0.50
    households = demo.number_of_households if demo else 5000.0
    per_hh = 2.27
    
    effective_pop = pop + floating_pop
    method_a = calculate_method_a_person(effective_pop, per_capita)
    method_b = calculate_method_b_household(households, per_hh)
    
    hist = db.query(HistoricalWaste).filter(HistoricalWaste.habitation_id == location_id).order_by(HistoricalWaste.measurement_date.desc()).first()
    measured_tonnes = hist.quantity if hist else None
    method_c = calculate_method_c_measured(measured_tonnes)
    
    ind_waste = ind.industrial_waste_kg_day if ind else 2000.0
    method_d = calculate_method_d_industry(
        industry_count=ind.number_of_industries if ind else 10,
        workers=500,
        worker_rate_kg_day=0.60,
        reported_kg_day=ind_waste
    )
    
    method_e = calculate_method_e_hospital(beds=50, occupied_beds=35)
    method_f = calculate_method_f_institution(students_staff=2000)
    method_g = calculate_method_g_hotel(rooms=100, occupancy_rate=70)
    method_h = calculate_method_h_market(vendors=150)
    
    source_total_kg = (
        method_a["daily_kg"] +
        method_d["daily_kg"] +
        method_e["daily_kg"] +
        method_f["daily_kg"] +
        method_g["daily_kg"] +
        method_h["daily_kg"]
    )
    
    reconciliation = cross_method_reconcile(
        method_a=method_a,
        method_b=method_b,
        method_c=method_c,
        source_aggregated_kg=source_total_kg
    )
    
    daily_waste_kg = reconciliation["reconciled_daily_kg"]
    
    vehicle_count = infra.vehicle_count if infra else 10
    vehicle_cap = infra.vehicle_capacity_kg if infra else 2000.0
    trips = infra.trips_per_vehicle if infra else 1
    
    collection = collection_gap_analysis(
        daily_waste_kg=daily_waste_kg,
        vehicle_count=vehicle_count,
        vehicle_capacity_kg=vehicle_cap,
        trips_per_vehicle=trips,
        coverage_pct=infra.collection_coverage_percent if infra else 100.0
    )
    
    transport = transport_gap_analysis(
        daily_waste_kg=daily_waste_kg,
        vehicle_count=vehicle_count,
        vehicle_capacity_kg=vehicle_cap,
        trips_per_vehicle=trips
    )
    
    segregation = segregation_gap_analysis(
        daily_waste_kg=daily_waste_kg,
        current_segregation_pct=60.0,
        target_segregation_pct=80.0
    )
    
    facility_cap = sum([f.capacity_kg_day for f in facilities if f.capacity_kg_day]) if facilities else 0.0
    infra_treatment_cap = infra.treatment_capacity_kg if infra else 10000.0
    treatment_cap = max(facility_cap, infra_treatment_cap)
    
    treatment = treatment_gap_analysis(
        daily_waste_kg=daily_waste_kg,
        treatment_capacity_kg=treatment_cap
    )
    
    comp_dict = {
        "organic_percent": comp.organic_percent if comp else 50.0,
        "paper_percent": comp.paper_percent if comp else 12.0,
        "plastic_percent": comp.plastic_percent if comp else 10.0,
        "metal_percent": comp.metal_percent if comp else 3.0,
        "glass_percent": comp.glass_percent if comp else 4.0,
        "textile_percent": comp.textile_percent if comp else 4.0,
        "ewaste_percent": comp.ewaste_percent if comp else 2.0,
        "other_percent": comp.other_percent if comp else 15.0
    }
    
    return {
        "location": {
            "id": loc.id,
            "name": loc.name,
            "location_type": loc.location_type,
            "district": loc.district,
            "state": loc.state,
            "terrain": loc.terrain
        },
        "composition": comp_dict,
        "method_a": method_a,
        "method_b": method_b,
        "method_c": method_c,
        "source_aggregated_daily_kg": source_total_kg,
        "reconciliation": reconciliation,
        "collection": collection,
        "transport": transport,
        "segregation": segregation,
        "treatment": treatment
    }



@router.post("/calculate-multi-method", response_model=MultiMethodCalculationOut)
def calculate_multi_method(calc_in: MultiMethodCalculationIn, user: User = Depends(get_current_user)):
    effective_pop = (
        calc_in.population +
        calc_in.floating_population +
        calc_in.tourist_population +
        calc_in.event_population
    )
    method_a = calculate_method_a_person(
        population=effective_pop,
        per_capita_kg_day=calc_in.waste_per_person_kg_day,
        seasonal_factor=calc_in.seasonal_factor
    )

    method_b = calculate_method_b_household(
        households=calc_in.households,
        per_household_kg_day=calc_in.waste_per_household_kg_day,
        seasonal_factor=calc_in.seasonal_factor
    )

    method_c = calculate_method_c_measured(
        measured_tonnes_day=calc_in.measured_waste_tonnes_day,
        data_quality=calc_in.measured_data_quality
    )

    method_d = calculate_method_d_industry(
        industry_count=calc_in.industry_count,
        workers=calc_in.industry_workers,
        worker_rate_kg_day=calc_in.industry_worker_waste_kg_day,
        reported_kg_day=calc_in.reported_industry_waste_kg_day
    )

    method_e = calculate_method_e_hospital(
        beds=calc_in.hospital_beds,
        occupied_beds=calc_in.occupied_beds,
        rate_per_bed_kg_day=calc_in.hospital_waste_per_bed_kg_day,
        reported_kg_day=calc_in.reported_hospital_waste_kg_day
    )

    method_f = calculate_method_f_institution(
        students_staff=calc_in.institution_students_staff,
        rate_kg_day=calc_in.institution_waste_per_person_kg_day,
        reported_kg_day=calc_in.reported_institution_waste_kg_day
    )

    method_g = calculate_method_g_hotel(
        rooms=calc_in.hotel_rooms,
        occupancy_rate=calc_in.hotel_occupancy_rate,
        rate_per_guest_kg_day=calc_in.hotel_waste_per_guest_kg_day,
        reported_kg_day=calc_in.reported_hotel_waste_kg_day
    )

    method_h = calculate_method_h_market(
        vendors=calc_in.market_vendors,
        rate_per_vendor_kg_day=calc_in.market_waste_per_vendor_kg_day,
        reported_kg_day=calc_in.reported_market_waste_kg_day
    )

    source_total_kg = (
        method_a["daily_kg"] +
        method_d["daily_kg"] +
        method_e["daily_kg"] +
        method_f["daily_kg"] +
        method_g["daily_kg"] +
        method_h["daily_kg"]
    )
    source_aggregated = {
        "daily_kg": round(source_total_kg, 2),
        "daily_tonnes": round(source_total_kg / 1000.0, 3),
        "breakdown": {
            "residential_kg": method_a["daily_kg"],
            "industrial_kg": method_d["daily_kg"],
            "hospital_kg": method_e["daily_kg"],
            "institution_kg": method_f["daily_kg"],
            "hotel_kg": method_g["daily_kg"],
            "market_kg": method_h["daily_kg"]
        }
    }

    reconciliation = cross_method_reconcile(
        method_a=method_a,
        method_b=method_b,
        method_c=method_c,
        source_aggregated_kg=source_total_kg
    )

    return {
        "method_a_person_based": method_a,
        "method_b_household_based": method_b,
        "method_c_measured_based": method_c,
        "method_d_industry_based": method_d,
        "method_e_hospital_based": method_e,
        "method_f_institution_based": method_f,
        "method_g_hotel_based": method_g,
        "method_h_market_based": method_h,
        "source_aggregated": source_aggregated,
        "cross_method_comparison": reconciliation["method_estimates"],
        "reconciliation": reconciliation
    }

@router.post("/collection-plan")
def calculate_collection(data: Dict[str, Any], user: User = Depends(get_current_user)):
    return collection_gap_analysis(
        daily_waste_kg=float(data.get("daily_waste_kg", 0)),
        vehicle_count=int(data.get("vehicle_count", 1)),
        vehicle_capacity_kg=float(data.get("vehicle_capacity_kg", 2000)),
        trips_per_vehicle=int(data.get("trips_per_vehicle", 1)),
        coverage_pct=float(data.get("collection_coverage_percent", 100.0))
    )

@router.post("/transport-plan")
def calculate_transport(data: Dict[str, Any], user: User = Depends(get_current_user)):
    return transport_gap_analysis(
        daily_waste_kg=float(data.get("daily_waste_kg", 0)),
        vehicle_count=int(data.get("vehicle_count", 1)),
        vehicle_capacity_kg=float(data.get("vehicle_capacity_kg", 2000)),
        trips_per_vehicle=int(data.get("trips_per_vehicle", 1))
    )

@router.post("/segregation-plan")
def calculate_segregation(data: Dict[str, Any], user: User = Depends(get_current_user)):
    return segregation_gap_analysis(
        daily_waste_kg=float(data.get("daily_waste_kg", 0)),
        current_segregation_pct=float(data.get("current_segregation_percent", 60.0)),
        target_segregation_pct=float(data.get("target_segregation_percent", 80.0))
    )

@router.post("/treatment-plan")
def calculate_treatment(data: Dict[str, Any], user: User = Depends(get_current_user)):
    return treatment_gap_analysis(
        daily_waste_kg=float(data.get("daily_waste_kg", 0)),
        treatment_capacity_kg=float(data.get("treatment_capacity_kg", 0)),
        composting_capacity_kg=float(data.get("composting_capacity_kg", 0)),
        recycling_capacity_kg=float(data.get("recycling_capacity_kg", 0)),
        mrf_capacity_kg=float(data.get("mrf_capacity_kg", 0)),
        wte_capacity_kg=float(data.get("wte_capacity_kg", 0)),
        landfill_capacity_kg=float(data.get("landfill_capacity_kg", 0))
    )
