"""Comprehensive Disaster Impact & Natural Calamity Simulation Engine for SWMS."""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from math import ceil
from app.services.emergency_waste_service import calculate_shelter_waste, estimate_disaster_debris_breakdown

def calculate_disaster_waste_components(
    normal_waste_tonnes_day: float,
    affected_population: float,
    displaced_population: float,
    shelter_population: float,
    additional_waste_pct: float = 25.0,
    debris_tonnes_day: float = 2.5,
    waste_per_person_kg: float = 0.50
) -> Dict[str, Any]:
    """
    Computes transparent disaster components:
    Total = Normal Baseline + Shelter Waste + Additional Disaster Waste + Debris/Cleanup.
    """
    # Shelter waste
    shelter_res = calculate_shelter_waste(shelter_population, waste_per_person_kg)
    shelter_tonnes = shelter_res["daily_shelter_waste_tonnes"]

    # Disaster surge waste on affected population remaining in area
    remaining_affected = max(0.0, affected_population - displaced_population)
    surge_kg = remaining_affected * waste_per_person_kg * (additional_waste_pct / 100.0)
    surge_tonnes = round(surge_kg / 1000.0, 3)

    # General additional emergency waste
    disaster_additional_tonnes = round(surge_tonnes + (normal_waste_tonnes_day * (additional_waste_pct / 100.0) * 0.2), 3)

    total_generated_tonnes = round(normal_waste_tonnes_day + shelter_tonnes + disaster_additional_tonnes + debris_tonnes_day, 3)

    return {
        "normal_baseline_waste_tonnes_day": normal_waste_tonnes_day,
        "shelter_waste_tonnes_day": shelter_tonnes,
        "disaster_additional_waste_tonnes_day": disaster_additional_tonnes,
        "debris_cleanup_waste_tonnes_day": debris_tonnes_day,
        "total_disaster_waste_tonnes_day": total_generated_tonnes,
        "disaster_surge_percentage": round(((total_generated_tonnes - normal_waste_tonnes_day) / normal_waste_tonnes_day * 100) if normal_waste_tonnes_day > 0 else 0, 1)
    }

def run_disaster_multi_day_accumulation(
    normal_waste_tonnes_day: float,
    normal_fleet_capacity_tonnes_day: float,
    normal_treatment_capacity_tonnes_day: float,
    duration_days: int = 7,
    affected_population: float = 5000.0,
    displaced_population: float = 2000.0,
    shelter_population: float = 1500.0,
    road_access_pct: float = 50.0,
    collection_efficiency_pct: float = 60.0,
    treatment_capacity_pct: float = 80.0,
    additional_waste_pct: float = 25.0,
    debris_tonnes_day: float = 2.5,
    start_date_val: Optional[date] = None,
    vehicle_capacity_tonnes: float = 2.0,
    trips_per_vehicle: int = 1
) -> Dict[str, Any]:
    """
    Calculates day-by-day generation, collection with disruption, treatment deficit,
    and cumulative uncollected waste accumulation.
    """
    if start_date_val is None:
        start_date_val = date.today()

    components = calculate_disaster_waste_components(
        normal_waste_tonnes_day=normal_waste_tonnes_day,
        affected_population=affected_population,
        displaced_population=displaced_population,
        shelter_population=shelter_population,
        additional_waste_pct=additional_waste_pct,
        debris_tonnes_day=debris_tonnes_day
    )

    daily_gen_tonnes = components["total_disaster_waste_tonnes_day"]

    # Effective capacities under disaster constraints
    effective_fleet_cap_tonnes = round(normal_fleet_capacity_tonnes_day * (collection_efficiency_pct / 100.0) * (road_access_pct / 100.0), 3)
    effective_treatment_cap_tonnes = round(normal_treatment_capacity_tonnes_day * (treatment_capacity_pct / 100.0), 3)

    daily_series = []
    cumulative_accumulated = 0.0
    total_generated_sum = 0.0
    total_collected_sum = 0.0
    total_treated_sum = 0.0

    for day in range(1, duration_days + 1):
        cur_date = start_date_val + timedelta(days=day - 1)
        
        # In early disaster days, road blockage is higher; in later days, cleanup debris increases
        day_factor = 1.0
        if day <= 2:
            day_road_pct = max(20.0, road_access_pct * 0.8)
            day_eff_pct = max(30.0, collection_efficiency_pct * 0.7)
        elif day >= duration_days - 2:
            day_road_pct = min(100.0, road_access_pct * 1.2)
            day_eff_pct = min(100.0, collection_efficiency_pct * 1.1)
        else:
            day_road_pct = road_access_pct
            day_eff_pct = collection_efficiency_pct

        day_fleet_cap = round(normal_fleet_capacity_tonnes_day * (day_eff_pct / 100.0) * (day_road_pct / 100.0), 3)
        day_collected = min(daily_gen_tonnes + cumulative_accumulated, day_fleet_cap)
        day_uncollected = max(0.0, daily_gen_tonnes - day_collected)
        
        cumulative_accumulated = round(cumulative_accumulated + day_uncollected, 3)
        
        day_treated = min(day_collected, effective_treatment_cap_tonnes)
        day_treatment_gap = max(0.0, day_collected - effective_treatment_cap_tonnes)

        # Vehicle requirement
        required_trips = ceil((daily_gen_tonnes * 1000) / (vehicle_capacity_tonnes * 1000)) if vehicle_capacity_tonnes > 0 else 0
        vehicles_needed = ceil(required_trips / trips_per_vehicle) if trips_per_vehicle > 0 else 0
        current_avail_vehicles = ceil(day_fleet_cap / vehicle_capacity_tonnes) if vehicle_capacity_tonnes > 0 else 0
        vehicle_deficit = max(0, vehicles_needed - current_avail_vehicles)

        daily_row = {
            "day": day,
            "date": cur_date.isoformat(),
            "normal_waste_tonnes": normal_waste_tonnes_day,
            "temporary_pop_waste_tonnes": components["shelter_waste_tonnes_day"],
            "disaster_additional_waste_tonnes": components["disaster_additional_waste_tonnes_day"],
            "debris_cleanup_waste_tonnes": debris_tonnes_day,
            "total_generated_tonnes": daily_gen_tonnes,
            "effective_fleet_capacity_tonnes": day_fleet_cap,
            "collected_tonnes": day_collected,
            "uncollected_tonnes": day_uncollected,
            "cumulative_accumulated_tonnes": cumulative_accumulated,
            "effective_treatment_capacity_tonnes": effective_treatment_cap_tonnes,
            "treated_tonnes": day_treated,
            "treatment_gap_tonnes": day_treatment_gap,
            "vehicles_required": vehicles_needed,
            "available_vehicles": current_avail_vehicles,
            "vehicle_deficit": vehicle_deficit,
            "road_access_pct": round(day_road_pct, 1),
            "collection_efficiency_pct": round(day_eff_pct, 1)
        }
        daily_series.append(daily_row)

        total_generated_sum += daily_gen_tonnes
        total_collected_sum += day_collected
        total_treated_sum += day_treated

    return {
        "components": components,
        "duration_days": duration_days,
        "daily_series": daily_series,
        "total_period_generated_tonnes": round(total_generated_sum, 2),
        "total_period_collected_tonnes": round(total_collected_sum, 2),
        "total_period_uncollected_tonnes": round(total_generated_sum - total_collected_sum, 2),
        "peak_accumulated_waste_tonnes": round(max(r["cumulative_accumulated_tonnes"] for r in daily_series), 2),
        "total_period_treated_tonnes": round(total_treated_sum, 2),
        "total_period_treatment_gap_tonnes": round(total_collected_sum - total_treated_sum, 2),
        "max_vehicle_deficit": max(r["vehicle_deficit"] for r in daily_series),
        "normal_vs_disaster_ratio": round(daily_gen_tonnes / normal_waste_tonnes_day if normal_waste_tonnes_day > 0 else 1.0, 2)
    }

def run_disaster_what_if_analysis(
    baseline_analysis_params: Dict[str, Any],
    modified_analysis_params: Dict[str, Any]
) -> Dict[str, Any]:
    """Compares two disaster scenarios (e.g. Medium Severity vs High Severity)."""
    base_res = run_disaster_multi_day_accumulation(**baseline_analysis_params)
    mod_res = run_disaster_multi_day_accumulation(**modified_analysis_params)

    base_gen = base_res["components"]["total_disaster_waste_tonnes_day"]
    mod_gen = mod_res["components"]["total_disaster_waste_tonnes_day"]
    base_peak_acc = base_res["peak_accumulated_waste_tonnes"]
    mod_peak_acc = mod_res["peak_accumulated_waste_tonnes"]

    delta_gen_tonnes = round(mod_gen - base_gen, 3)
    delta_gen_pct = round(((mod_gen - base_gen) / base_gen * 100) if base_gen > 0 else 0, 1)

    delta_peak_acc_tonnes = round(mod_peak_acc - base_peak_acc, 3)
    delta_peak_acc_pct = round(((mod_peak_acc - base_peak_acc) / base_peak_acc * 100) if base_peak_acc > 0 else 0, 1)

    return {
        "baseline": base_res,
        "scenario": mod_res,
        "delta": {
            "daily_generation_tonnes": delta_gen_tonnes,
            "daily_generation_percentage": delta_gen_pct,
            "peak_accumulation_tonnes": delta_peak_acc_tonnes,
            "peak_accumulation_percentage": delta_peak_acc_pct,
            "vehicle_deficit_delta": mod_res["max_vehicle_deficit"] - base_res["max_vehicle_deficit"]
        },
        "explanation": f"Scenario modifications result in a {delta_gen_pct}% change in daily waste generation and a {delta_peak_acc_pct}% change in peak accumulated uncollected waste."
    }
