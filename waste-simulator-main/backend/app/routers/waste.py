from typing import Dict, Any
from fastapi import APIRouter, Depends
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
