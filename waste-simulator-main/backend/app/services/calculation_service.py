"""Calculation Service for SWMS.

Implements explainable planning calculations across Methods A through H,
multi-method cross-validation, collection, transport, segregation, and treatment.
"""
from math import ceil
from typing import Dict, Any, Optional, List

def calculate_method_a_person(population: float, per_capita_kg_day: float, seasonal_factor: float = 1.0) -> Dict[str, Any]:
    daily_kg = population * per_capita_kg_day * seasonal_factor
    return {
        "method": "METHOD_A_PERSON_BASED",
        "description": "Population x Waste per person per day",
        "inputs": {"population": population, "per_capita_kg_day": per_capita_kg_day, "seasonal_factor": seasonal_factor},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3),
        "weekly_tonnes": round((daily_kg * 7) / 1000.0, 3),
        "monthly_tonnes": round((daily_kg * 30) / 1000.0, 3),
        "annual_tonnes": round((daily_kg * 365) / 1000.0, 3),
        "confidence": "HIGH" if population > 0 and per_capita_kg_day > 0 else "LOW"
    }

def calculate_method_b_household(households: float, per_household_kg_day: float, seasonal_factor: float = 1.0) -> Dict[str, Any]:
    daily_kg = households * per_household_kg_day * seasonal_factor
    return {
        "method": "METHOD_B_HOUSEHOLD_BASED",
        "description": "Households x Waste per household per day",
        "inputs": {"households": households, "per_household_kg_day": per_household_kg_day, "seasonal_factor": seasonal_factor},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3),
        "weekly_tonnes": round((daily_kg * 7) / 1000.0, 3),
        "monthly_tonnes": round((daily_kg * 30) / 1000.0, 3),
        "annual_tonnes": round((daily_kg * 365) / 1000.0, 3),
        "confidence": "HIGH" if households > 0 and per_household_kg_day > 0 else "LOW"
    }

def calculate_method_c_measured(measured_tonnes_day: Optional[float], data_quality: str = "HIGH") -> Optional[Dict[str, Any]]:
    if measured_tonnes_day is None or measured_tonnes_day < 0:
        return None
    daily_kg = measured_tonnes_day * 1000.0
    return {
        "method": "METHOD_C_MEASURED_WEIGHBRIDGE",
        "description": "Directly measured weighbridge / weigh scale data",
        "inputs": {"measured_tonnes_day": measured_tonnes_day, "data_quality": data_quality},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(measured_tonnes_day, 3),
        "weekly_tonnes": round(measured_tonnes_day * 7, 3),
        "monthly_tonnes": round(measured_tonnes_day * 30, 3),
        "annual_tonnes": round(measured_tonnes_day * 365, 3),
        "confidence": data_quality
    }

def calculate_method_d_industry(
    industry_count: int,
    workers: int,
    worker_rate_kg_day: float = 0.60,
    reported_kg_day: Optional[float] = None
) -> Dict[str, Any]:
    if reported_kg_day is not None and reported_kg_day > 0:
        daily_kg = reported_kg_day
        sub_method = "REPORTED"
    else:
        daily_kg = workers * worker_rate_kg_day
        sub_method = "WORKER_BASED"
    return {
        "method": "METHOD_D_INDUSTRY_BASED",
        "sub_method": sub_method,
        "inputs": {"industry_count": industry_count, "workers": workers, "worker_rate_kg_day": worker_rate_kg_day, "reported_kg_day": reported_kg_day},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3),
        "annual_tonnes": round((daily_kg * 365) / 1000.0, 3)
    }

def calculate_method_e_hospital(
    beds: int,
    occupied_beds: int,
    rate_per_bed_kg_day: float = 1.50,
    reported_kg_day: Optional[float] = None
) -> Dict[str, Any]:
    if reported_kg_day is not None and reported_kg_day > 0:
        daily_kg = reported_kg_day
        sub_method = "REPORTED"
    else:
        active_beds = occupied_beds if occupied_beds > 0 else beds
        daily_kg = active_beds * rate_per_bed_kg_day
        sub_method = "BED_BASED"
    return {
        "method": "METHOD_E_HOSPITAL_BASED",
        "sub_method": sub_method,
        "inputs": {"beds": beds, "occupied_beds": occupied_beds, "rate_per_bed_kg_day": rate_per_bed_kg_day, "reported_kg_day": reported_kg_day},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3),
        "annual_tonnes": round((daily_kg * 365) / 1000.0, 3)
    }

def calculate_method_f_institution(
    students_staff: int,
    rate_kg_day: float = 0.15,
    reported_kg_day: Optional[float] = None
) -> Dict[str, Any]:
    if reported_kg_day is not None and reported_kg_day > 0:
        daily_kg = reported_kg_day
        sub_method = "REPORTED"
    else:
        daily_kg = students_staff * rate_kg_day
        sub_method = "STAFF_STUDENT_BASED"
    return {
        "method": "METHOD_F_INSTITUTION_BASED",
        "sub_method": sub_method,
        "inputs": {"students_staff": students_staff, "rate_kg_day": rate_kg_day, "reported_kg_day": reported_kg_day},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3)
    }

def calculate_method_g_hotel(
    rooms: int,
    occupancy_rate: float = 0.70,
    rate_per_guest_kg_day: float = 0.80,
    reported_kg_day: Optional[float] = None
) -> Dict[str, Any]:
    if reported_kg_day is not None and reported_kg_day > 0:
        daily_kg = reported_kg_day
        sub_method = "REPORTED"
    else:
        estimated_guests = rooms * occupancy_rate * 1.5
        daily_kg = estimated_guests * rate_per_guest_kg_day
        sub_method = "OCCUPANCY_BASED"
    return {
        "method": "METHOD_G_HOTEL_BASED",
        "sub_method": sub_method,
        "inputs": {"rooms": rooms, "occupancy_rate": occupancy_rate, "rate_per_guest_kg_day": rate_per_guest_kg_day, "reported_kg_day": reported_kg_day},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3)
    }

def calculate_method_h_market(
    vendors: int,
    rate_per_vendor_kg_day: float = 8.0,
    reported_kg_day: Optional[float] = None
) -> Dict[str, Any]:
    if reported_kg_day is not None and reported_kg_day > 0:
        daily_kg = reported_kg_day
        sub_method = "REPORTED"
    else:
        daily_kg = vendors * rate_per_vendor_kg_day
        sub_method = "VENDOR_BASED"
    return {
        "method": "METHOD_H_MARKET_BASED",
        "sub_method": sub_method,
        "inputs": {"vendors": vendors, "rate_per_vendor_kg_day": rate_per_vendor_kg_day, "reported_kg_day": reported_kg_day},
        "daily_kg": round(daily_kg, 2),
        "daily_tonnes": round(daily_kg / 1000.0, 3)
    }

def cross_method_reconcile(
    method_a: Dict[str, Any],
    method_b: Dict[str, Any],
    method_c: Optional[Dict[str, Any]],
    source_aggregated_kg: float
) -> Dict[str, Any]:
    a_tonnes = method_a["daily_tonnes"]
    b_tonnes = method_b["daily_tonnes"]
    c_tonnes = method_c["daily_tonnes"] if method_c else None
    src_tonnes = round(source_aggregated_kg / 1000.0, 3)

    estimates = {"Person Based (Method A)": a_tonnes, "Household Based (Method B)": b_tonnes}
    if c_tonnes is not None:
        estimates["Measured Weighbridge (Method C)"] = c_tonnes
    if src_tonnes > 0:
        estimates["Source-Level Aggregation"] = src_tonnes

    if c_tonnes is not None and method_c.get("confidence") in ["HIGH", "VERIFIED", "MEASURED"]:
        selected_method = "Measured Weighbridge (Method C)"
        selected_val = c_tonnes
        reason = "Measured weighbridge data was selected as the gold-standard source of truth because verified physical weights exist."
        confidence = "HIGH"
    elif src_tonnes > 0 and src_tonnes >= max(a_tonnes, b_tonnes) * 0.8:
        selected_method = "Source-Level Aggregation"
        selected_val = src_tonnes
        reason = "Bottom-up source aggregation was selected because specific verified establishment counts (industry, hospital, market) are documented."
        confidence = "HIGH"
    elif a_tonnes > 0 and b_tonnes > 0:
        diff_pct = abs(a_tonnes - b_tonnes) / max(a_tonnes, b_tonnes) * 100
        if diff_pct <= 10.0:
            selected_method = "Person-Based Model (Method A)"
            selected_val = a_tonnes
            reason = f"Person and Household estimates agree within {round(diff_pct, 1)}%. Person-based baseline was selected as standard municipal benchmark."
            confidence = "HIGH"
        else:
            selected_method = "Person-Based Model (Method A)"
            selected_val = a_tonnes
            reason = f"Variance of {round(diff_pct, 1)}% detected between person ({a_tonnes}t) and household ({b_tonnes}t) models. Selected person model; investigate average household size."
            confidence = "MEDIUM"
    else:
        selected_method = "Person-Based Model (Method A)"
        selected_val = max(a_tonnes, b_tonnes, 0.0)
        reason = "Fallback demographic estimate used due to limited primary records."
        confidence = "LOW"

    deviations = {}
    for name, val in estimates.items():
        diff = round(val - selected_val, 3)
        diff_pct = round((diff / selected_val * 100) if selected_val > 0 else 0, 1)
        deviations[name] = {"tonnes": val, "difference_tonnes": diff, "difference_pct": diff_pct}

    return {
        "selected_estimate_tonnes": selected_val,
        "selected_method": selected_method,
        "reconciliation_reason": reason,
        "confidence_level": confidence,
        "method_estimates": estimates,
        "deviations": deviations,
        "data_status": "MEASURED" if "Measured" in selected_method else "CALCULATED",
        "reconciled_daily_kg": round(selected_val * 1000.0, 2),
        "reconciled_kg_day": round(selected_val * 1000.0, 2),
        "reconciled_tonnes_day": selected_val
    }

def collection_gap_analysis(daily_waste_kg: float, vehicle_count: int, vehicle_capacity_kg: float, trips_per_vehicle: int, coverage_pct: float = 100.0) -> Dict[str, Any]:
    if vehicle_capacity_kg <= 0:
        raise ValueError("Vehicle capacity must be greater than zero kg")
    if trips_per_vehicle < 1:
        raise ValueError("Trips per vehicle must be at least 1")

    required_kg = daily_waste_kg * (coverage_pct / 100.0)
    required_trips = ceil(required_kg / vehicle_capacity_kg) if vehicle_capacity_kg > 0 else 0
    vehicles_required = ceil(required_trips / trips_per_vehicle) if trips_per_vehicle > 0 else 0
    
    current_capacity_kg = vehicle_count * vehicle_capacity_kg * trips_per_vehicle
    gap_kg = max(0.0, required_kg - current_capacity_kg)
    vehicle_deficit = max(0, vehicles_required - vehicle_count)

    return {
        "required_collection_kg_day": round(required_kg, 2),
        "required_collection_tonnes_day": round(required_kg / 1000.0, 3),
        "required_trips": required_trips,
        "vehicles_required": vehicles_required,
        "current_vehicle_count": vehicle_count,
        "current_fleet_capacity_kg_day": round(current_capacity_kg, 2),
        "current_fleet_capacity_tonnes_day": round(current_capacity_kg / 1000.0, 3),
        "collection_gap_kg_day": round(gap_kg, 2),
        "collection_gap_tonnes_day": round(gap_kg / 1000.0, 3),
        "vehicle_deficit_count": vehicle_deficit,
        "status": "Adequate collection fleet" if gap_kg <= 0 else "Fleet capacity shortage"
    }

def transport_gap_analysis(daily_waste_kg: float, vehicle_count: int, vehicle_capacity_kg: float, trips_per_vehicle: int) -> Dict[str, Any]:
    if vehicle_capacity_kg <= 0:
        raise ValueError("Vehicle capacity must be greater than zero kg")
    capacity_kg = vehicle_count * vehicle_capacity_kg * trips_per_vehicle
    required_trips = ceil(daily_waste_kg / vehicle_capacity_kg)
    gap_kg = max(0.0, daily_waste_kg - capacity_kg)
    return {
        "daily_transport_required_kg": round(daily_waste_kg, 2),
        "required_trips": required_trips,
        "daily_transport_capacity_kg": round(capacity_kg, 2),
        "daily_transport_capacity_tonnes": round(capacity_kg / 1000.0, 3),
        "transport_gap_kg": round(gap_kg, 2),
        "transport_gap_tonnes": round(gap_kg / 1000.0, 3)
    }

def segregation_gap_analysis(daily_waste_kg: float, current_segregation_pct: float, target_segregation_pct: float = 80.0) -> Dict[str, Any]:
    current_segregated_kg = daily_waste_kg * (current_segregation_pct / 100.0)
    current_unsegregated_kg = daily_waste_kg - current_segregated_kg
    target_segregated_kg = daily_waste_kg * (target_segregation_pct / 100.0)
    segregation_gap_kg = max(0.0, target_segregated_kg - current_segregated_kg)

    return {
        "daily_waste_kg": round(daily_waste_kg, 2),
        "current_segregation_percent": current_segregation_pct,
        "target_segregation_percent": target_segregation_pct,
        "current_segregated_kg_day": round(current_segregated_kg, 2),
        "current_segregated_tonnes_day": round(current_segregated_kg / 1000.0, 3),
        "current_unsegregated_kg_day": round(current_unsegregated_kg, 2),
        "current_unsegregated_tonnes_day": round(current_unsegregated_kg / 1000.0, 3),
        "target_segregated_kg_day": round(target_segregated_kg, 2),
        "target_segregated_tonnes_day": round(target_segregated_kg / 1000.0, 3),
        "segregation_gap_kg_day": round(segregation_gap_kg, 2),
        "segregation_gap_tonnes_day": round(segregation_gap_kg / 1000.0, 3)
    }

def treatment_gap_analysis(
    daily_waste_kg: float,
    treatment_capacity_kg: float,
    composting_capacity_kg: float = 0.0,
    recycling_capacity_kg: float = 0.0,
    mrf_capacity_kg: float = 0.0,
    wte_capacity_kg: float = 0.0,
    landfill_capacity_kg: float = 0.0
) -> Dict[str, Any]:
    total_processing_cap = treatment_capacity_kg
    if total_processing_cap <= 0:
        total_processing_cap = composting_capacity_kg + recycling_capacity_kg + mrf_capacity_kg + wte_capacity_kg

    treatment_gap_kg = max(0.0, daily_waste_kg - total_processing_cap)
    
    return {
        "daily_waste_kg": round(daily_waste_kg, 2),
        "daily_waste_tonnes": round(daily_waste_kg / 1000.0, 3),
        "total_treatment_capacity_kg": round(total_processing_cap, 2),
        "total_treatment_capacity_tonnes": round(total_processing_cap / 1000.0, 3),
        "treatment_gap_kg": round(treatment_gap_kg, 2),
        "treatment_gap_tonnes": round(treatment_gap_kg / 1000.0, 3),
        "facility_breakdown": {
            "composting_capacity_kg": composting_capacity_kg,
            "recycling_capacity_kg": recycling_capacity_kg,
            "mrf_capacity_kg": mrf_capacity_kg,
            "wte_capacity_kg": wte_capacity_kg,
            "landfill_capacity_kg": landfill_capacity_kg
        },
        "status": "Adequate treatment capacity" if treatment_gap_kg <= 0 else "Treatment capacity deficit"
    }
