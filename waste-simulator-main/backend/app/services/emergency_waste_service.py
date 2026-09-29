"""Emergency Waste & Shelter Calculation Service for SWMS."""
from typing import Dict, Any, List
from math import ceil

def calculate_shelter_waste(shelter_population: float, waste_per_person_kg: float = 0.50) -> Dict[str, Any]:
    daily_kg = shelter_population * waste_per_person_kg
    return {
        "shelter_population": shelter_population,
        "waste_per_person_kg_day": waste_per_person_kg,
        "daily_shelter_waste_kg": round(daily_kg, 2),
        "daily_shelter_waste_tonnes": round(daily_kg / 1000.0, 3)
    }

def estimate_disaster_debris_breakdown(disaster_type: str, severity: str, affected_area_sqkm: float, affected_population: float) -> Dict[str, Any]:
    # Specific empirical debris factors by disaster category
    type_upper = disaster_type.upper()
    sev_mult = 1.0
    if severity == "LOW":
        sev_mult = 0.5
    elif severity == "MEDIUM":
        sev_mult = 1.0
    elif severity == "HIGH":
        sev_mult = 1.8
    elif severity == "EXTREME":
        sev_mult = 3.0

    if "FLOOD" in type_upper:
        spoiled_food_kg_day = affected_population * 0.20 * sev_mult
        damaged_household_kg_day = affected_population * 0.35 * sev_mult
        sediment_silt_tonnes_day = (affected_area_sqkm * 0.15) * sev_mult
        vegetation_tonnes_day = (affected_area_sqkm * 0.05) * sev_mult
    elif "CYCLONE" in type_upper or "STORM" in type_upper:
        spoiled_food_kg_day = affected_population * 0.10 * sev_mult
        damaged_household_kg_day = affected_population * 0.50 * sev_mult
        sediment_silt_tonnes_day = (affected_area_sqkm * 0.02) * sev_mult
        vegetation_tonnes_day = (affected_area_sqkm * 0.80) * sev_mult
    elif "EARTHQUAKE" in type_upper or "LANDSLIDE" in type_upper:
        spoiled_food_kg_day = affected_population * 0.05 * sev_mult
        damaged_household_kg_day = affected_population * 0.80 * sev_mult
        sediment_silt_tonnes_day = (affected_area_sqkm * 1.20) * sev_mult
        vegetation_tonnes_day = (affected_area_sqkm * 0.10) * sev_mult
    else:
        spoiled_food_kg_day = affected_population * 0.10 * sev_mult
        damaged_household_kg_day = affected_population * 0.20 * sev_mult
        sediment_silt_tonnes_day = 0.5 * sev_mult
        vegetation_tonnes_day = 0.5 * sev_mult

    total_debris_tonnes_day = round((spoiled_food_kg_day + damaged_household_kg_day) / 1000.0 + sediment_silt_tonnes_day + vegetation_tonnes_day, 3)

    return {
        "disaster_type": disaster_type,
        "severity": severity,
        "spoiled_food_tonnes_day": round(spoiled_food_kg_day / 1000.0, 3),
        "damaged_household_materials_tonnes_day": round(damaged_household_kg_day / 1000.0, 3),
        "sediment_silt_tonnes_day": round(sediment_silt_tonnes_day, 3),
        "vegetation_debris_tonnes_day": round(vegetation_tonnes_day, 3),
        "total_debris_tonnes_day": total_debris_tonnes_day
    }
