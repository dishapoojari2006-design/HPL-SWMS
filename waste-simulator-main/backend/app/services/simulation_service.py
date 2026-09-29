"""Simulation Service for SWMS."""
from typing import Dict, Any, List, Optional
from math import ceil
from app.services.calculation_service import collection_gap_analysis, segregation_gap_analysis, treatment_gap_analysis

def run_multi_year_simulation(
    params: Dict[str, Any],
    years: int = 20,
    scenario_overrides: Optional[Dict[str, Any]] = None,
    strategy_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    merged_params = {**params}
    if scenario_overrides:
        merged_params.update(scenario_overrides)

    growth_rate = float(merged_params.get("population_growth_rate", 2.0)) / 100.0
    base_pop = float(merged_params.get("total_population", 25000.0))
    base_hh = float(merged_params.get("households", base_pop / 4.5 if base_pop > 0 else 5500.0))
    per_capita_kg = float(merged_params.get("waste_per_person_per_day", 0.50))
    per_hh_kg = float(merged_params.get("waste_per_household_per_day", 2.27))

    floating_pop = float(merged_params.get("floating_population", 0.0))
    tourist_pop = float(merged_params.get("tourist_population", 0.0))
    seasonal_pop = float(merged_params.get("seasonal_population", 0.0))
    migrant_pop = float(merged_params.get("migrant_population", 0.0))
    event_pop = float(merged_params.get("event_population", 0.0))

    base_ind_kg = float(merged_params.get("industrial_waste_kg_day", 0.0))
    ind_growth = float(merged_params.get("industrial_growth_rate", 2.0)) / 100.0
    base_comm_kg = float(merged_params.get("commercial_waste_kg_day", 0.0))
    base_market_kg = float(merged_params.get("market_waste_kg_day", 0.0))
    seasonal_factor = float(merged_params.get("seasonal_factor", 1.0))
    event_waste_pct = float(merged_params.get("event_waste_percent", 0.0))

    vehicles = int(merged_params.get("vehicle_count", 10))
    vehicle_cap_kg = float(merged_params.get("vehicle_capacity_kg", 2000.0))
    trips_per_v = int(merged_params.get("trips_per_vehicle", 1))
    coverage_pct = float(merged_params.get("collection_coverage_percent", 100.0))
    treatment_cap_kg = float(merged_params.get("treatment_capacity_kg", 10000.0))
    segregation_pct = float(merged_params.get("segregation_percent", 60.0))

    if strategy_params:
        if "additional_vehicles" in strategy_params:
            vehicles += int(strategy_params["additional_vehicles"])
        if "additional_treatment_capacity_kg" in strategy_params:
            treatment_cap_kg += float(strategy_params["additional_treatment_capacity_kg"])
        if "target_segregation_percent" in strategy_params:
            segregation_pct = float(strategy_params["target_segregation_percent"])
        if "collection_efficiency_pct" in strategy_params:
            coverage_pct = float(strategy_params["collection_efficiency_pct"])

    yearly_series = []
    cumulative_tonnes = 0.0

    for y in range(years + 1):
        perm_pop = base_pop * ((1.0 + growth_rate) ** y)
        hh = base_hh * ((1.0 + growth_rate) ** y)
        effective_pop = perm_pop + floating_pop + tourist_pop + seasonal_pop + migrant_pop + event_pop

        res_kg = effective_pop * per_capita_kg
        hh_kg = hh * per_hh_kg
        ind_kg = base_ind_kg * ((1.0 + ind_growth) ** y)
        comm_kg = base_comm_kg
        market_kg = base_market_kg

        subtotal_kg = (res_kg + ind_kg + comm_kg + market_kg) * seasonal_factor
        event_add_kg = subtotal_kg * (event_waste_pct / 100.0)
        daily_total_kg = subtotal_kg + event_add_kg
        daily_tonnes = daily_total_kg / 1000.0

        collection_res = collection_gap_analysis(
            daily_waste_kg=daily_total_kg,
            vehicle_count=vehicles,
            vehicle_capacity_kg=vehicle_cap_kg,
            trips_per_vehicle=trips_per_v,
            coverage_pct=coverage_pct
        )

        segregation_res = segregation_gap_analysis(
            daily_waste_kg=daily_total_kg,
            current_segregation_pct=segregation_pct
        )

        treatment_res = treatment_gap_analysis(
            daily_waste_kg=daily_total_kg,
            treatment_capacity_kg=treatment_cap_kg
        )

        annual_tonnes = (daily_total_kg * 365.25) / 1000.0
        cumulative_tonnes += annual_tonnes

        row = {
            "year": y,
            "permanent_population": round(perm_pop, 1),
            "households": round(hh, 1),
            "effective_population": round(effective_pop, 1),
            "waste_per_person_kg_day": per_capita_kg,
            "waste_per_household_kg_day": per_hh_kg,
            "residential_waste_kg_day": round(res_kg, 2),
            "residential_tonnes": round(res_kg / 1000.0, 3),
            "industrial_waste_kg_day": round(ind_kg, 2),
            "industrial_tonnes": round(ind_kg / 1000.0, 3),
            "commercial_waste_kg_day": round(comm_kg, 2),
            "market_waste_kg_day": round(market_kg, 2),
            "daily_waste_kg": round(daily_total_kg, 2),
            "daily_waste_tonnes": round(daily_tonnes, 3),
            "monthly_waste_tonnes": round(daily_tonnes * 30, 2),
            "annual_waste_tonnes": round(annual_tonnes, 2),
            "cumulative_waste_tonnes": round(cumulative_tonnes, 2),
            "collection": collection_res,
            "segregation": segregation_res,
            "treatment": treatment_res,
            "treatment_capacity_tonnes": round(treatment_cap_kg / 1000.0, 3),
            "fleet_capacity_tonnes": round(collection_res["current_fleet_capacity_tonnes_day"], 3),
            "treatment_gap_tonnes": round(treatment_res["treatment_gap_tonnes"], 3),
            "segregated_tonnes": round(segregation_res["current_segregated_tonnes_day"], 3),
            "unsegregated_tonnes": round(segregation_res["current_unsegregated_tonnes_day"], 3)
        }
        yearly_series.append(row)

    return {
        "parameters": merged_params,
        "years": yearly_series,
        "total_cumulative_20yr_tonnes": round(cumulative_tonnes, 1),
        "fleet_breach_year": next((r["year"] for r in yearly_series if r["collection"].get("collection_gap_kg_day", 0) > 0), None),
        "treatment_breach_year": next((r["year"] for r in yearly_series if r["treatment"].get("treatment_gap_kg", 0) > 0 or r["treatment"].get("treatment_gap_tonnes", 0) > 0), None)
    }

def run_what_if_analysis(baseline_params: Dict[str, Any], overrides: Dict[str, Any], years: int = 20) -> Dict[str, Any]:
    base_run = run_multi_year_simulation(baseline_params, years=years)
    scenario_run = run_multi_year_simulation(baseline_params, years=years, scenario_overrides=overrides)

    base_y0 = base_run["years"][0]["daily_waste_tonnes"]
    scen_y0 = scenario_run["years"][0]["daily_waste_tonnes"]
    base_y20 = base_run["years"][-1]["daily_waste_tonnes"]
    scen_y20 = scenario_run["years"][-1]["daily_waste_tonnes"]

    diff_y20 = round(scen_y20 - base_y20, 3)
    diff_pct_y20 = round(((scen_y20 - base_y20) / base_y20 * 100) if base_y20 > 0 else 0, 1)

    return {
        "baseline_summary": {"year_0_tonnes": base_y0, "year_20_tonnes": base_y20},
        "scenario_summary": {"year_0_tonnes": scen_y0, "year_20_tonnes": scen_y20},
        "year_20_difference_tonnes": diff_y20,
        "year_20_difference_percent": diff_pct_y20,
        "baseline_series": base_run["years"],
        "scenario_series": scenario_run["years"]
    }
