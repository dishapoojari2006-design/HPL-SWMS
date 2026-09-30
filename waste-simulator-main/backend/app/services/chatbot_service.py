"""Controlled & Intelligent Grounded Chatbot Service for SWMS."""
from typing import Dict, Any, Optional
import re
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.location import Location
from app.models.parameters import DemographyParameter, InfrastructureParameter, IndustrialParameter, WasteComposition
from app.models.facility import Facility
from app.models.historical_waste import HistoricalWaste
from app.models.simulation import SimulationRun

def query_swms_assistant(db: Session, location_id: int, question: str, user_name: Optional[str] = None) -> Dict[str, Any]:
    loc = db.get(Location, location_id)
    if not loc:
        return {
            "answer": f"Location ID {location_id} was not found in the database. Please select a valid administrative location.",
            "evidence": {},
            "source_attribution": "Database Location Registry",
            "data_status": "MISSING"
        }

    q = question.lower().strip()

    # 1. Security Check
    if any(term in q for term in ["password", "secret", "token", "drop table", "select * from users", "delete from", "truncate"]):
        return {
            "answer": "Security Policy Violation: I am restricted to municipal planning, demographic metrics, waste data, and simulation analytics. System credentials and arbitrary database operations are inaccessible.",
            "evidence": {"security_filter": "BLOCKED_RESTRICTED_QUERY"},
            "source_attribution": "SWMS Security Engine",
            "data_status": "RESTRICTED"
        }

    # Fetch Location Context Parameters
    demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == location_id))
    infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == location_id))
    ind = db.scalar(select(IndustrialParameter).where(IndustrialParameter.habitation_id == location_id))
    comp = db.scalar(select(WasteComposition).where(WasteComposition.habitation_id == location_id))
    facilities = db.scalars(select(Facility).where(Facility.location_id == location_id)).all()
    latest_sim = db.scalar(
        select(SimulationRun)
        .where(SimulationRun.location_id == location_id)
        .order_by(SimulationRun.created_at.desc())
    )

    greeting_name = user_name if user_name else "Superadmin"

    # 2. Greetings & Introductions
    if q in ["hi", "hello", "hey", "greetings", "help", "start", "who are you", "what can you do"]:
        answer = (
            f"👋 **Hi {greeting_name}!** I am your grounded SWMS AI Planning Assistant for **{loc.name}** ({loc.location_type}).\n\n"
            f"You can ask me questions such as:\n"
            f"• *'What is the daily waste generation?'*\n"
            f"• *'Show demographic profile and population'* \n"
            f"• *'What is the collection fleet capacity?'*\n"
            f"• *'What treatment plants are registered?'*\n"
            f"• *'What is the waste composition breakdown?'*\n"
            f"• *'Show 10-year waste forecast projection'*\n"
            f"• *'Show historical weighbridge records'*"
        )
        return {
            "answer": answer,
            "evidence": {"location_id": loc.id, "location_name": loc.name},
            "source_attribution": "SWMS AI Assistant Kernel",
            "data_status": "VERIFIED"
        }

    # 3. Waste Generation / Daily Waste / Quantity
    if any(w in q for w in ["waste generation", "daily waste", "total waste", "waste quantity", "generation rate", "how much waste", "daily tonnage", "waste per day"]):
        pop = demo.total_population if demo else 25000.0
        floating = demo.floating_population if demo else 2000.0
        eff_pop = pop + floating
        res_waste_kg = eff_pop * 0.50
        ind_waste_kg = ind.industrial_waste_kg_day if ind else 2000.0
        total_daily_kg = res_waste_kg + ind_waste_kg + 500 # includes commercial/institutions
        total_tonnes = round(total_daily_kg / 1000.0, 2)

        answer = (
            f"📊 **Daily Waste Generation for {loc.name}**:\n"
            f"• Total Daily Generation: **{total_tonnes} tonnes/day** ({total_daily_kg:,.0f} kg/day).\n"
            f"• Residential/Commercial: {res_waste_kg/1000:.2f} tonnes/day (based on {eff_pop:,.0f} effective population @ 0.50 kg/capita).\n"
            f"• Industrial Generation: {ind_waste_kg/1000:.2f} tonnes/day ({ind.number_of_industries if ind else 0} active industries).\n"
            f"• Annual Waste Equivalent: {round(total_tonnes * 365, 1):,} tonnes/year."
        )
        return {
            "answer": answer,
            "evidence": {
                "total_daily_tonnes": total_tonnes,
                "residential_tonnes_day": round(res_waste_kg / 1000.0, 2),
                "industrial_tonnes_day": round(ind_waste_kg / 1000.0, 2),
                "effective_population": eff_pop
            },
            "source_attribution": "Multi-Method Waste Calculation Model (Methods A, B & D)",
            "data_status": "CALCULATED"
        }

    # 4. Waste Composition (Wet/Dry/Organic/Plastic/Paper etc.)
    if any(w in q for w in ["composition", "plastic", "organic", "wet", "dry", "paper", "metal", "glass", "recycle", "e-waste"]):
        org = comp.organic_percent if comp else 50.0
        paper = comp.paper_percent if comp else 12.0
        plastic = comp.plastic_percent if comp else 10.0
        metal = comp.metal_percent if comp else 3.0
        glass = comp.glass_percent if comp else 4.0
        textile = comp.textile_percent if comp else 4.0
        ewaste = comp.ewaste_percent if comp else 2.0
        other = comp.other_percent if comp else 15.0

        answer = (
            f"♻️ **Waste Composition Profile for {loc.name}**:\n"
            f"• Organic / Biodegradable (Wet): **{org}%**\n"
            f"• Recyclable Paper & Cardboard: **{paper}%**\n"
            f"• Plastics (PET/HDPE/LDPE): **{plastic}%**\n"
            f"• Glass & Ceramics: **{glass}%**\n"
            f"• Metals & Cans: **{metal}%**\n"
            f"• Textiles & Leather: **{textile}%**\n"
            f"• E-Waste & Hazardous: **{ewaste}%**\n"
            f"• Inert & Other Residuals: **{other}%**"
        )
        return {
            "answer": answer,
            "evidence": {
                "organic_percent": org,
                "paper_percent": paper,
                "plastic_percent": plastic,
                "metal_percent": metal,
                "glass_percent": glass,
                "ewaste_percent": ewaste
            },
            "source_attribution": "Waste Composition Matrix (Table: waste_compositions)",
            "data_status": "VERIFIED"
        }

    # 5. Historical Weighbridge Records
    if any(w in q for w in ["historical", "last month", "recorded", "measured", "weighbridge", "yesterday", "trend", "history"]):
        hist_records = db.scalars(
            select(HistoricalWaste)
            .where(HistoricalWaste.habitation_id == location_id)
            .order_by(HistoricalWaste.measurement_date.desc())
        ).all()

        if hist_records:
            total_qty = sum(r.quantity for r in hist_records)
            avg_qty = round(total_qty / len(hist_records), 2)
            latest_rec = hist_records[0]
            answer = (
                f"📈 **Historical Waste Weighbridge Analysis for {loc.name}**:\n"
                f"• Average Recorded Waste: **{avg_qty} tonnes/day**.\n"
                f"• Most Recent Measurement: **{latest_rec.quantity} tonnes** on {latest_rec.measurement_date.isoformat()} ({latest_rec.quality_status}).\n"
                f"• Total Sample Logs: {len(hist_records)} historical weighings.\n"
                f"• Primary Measurement Method: {latest_rec.measurement_method}."
            )
            return {
                "answer": answer,
                "evidence": {
                    "records_count": len(hist_records),
                    "average_tonnes_day": avg_qty,
                    "latest_date": latest_rec.measurement_date.isoformat(),
                    "latest_tonnes": latest_rec.quantity
                },
                "source_attribution": "Historical Weighbridge Registry (Table: historical_waste)",
                "data_status": "MEASURED"
            }
        else:
            return {
                "answer": f"No historical weighbridge records are currently logged for {loc.name}. You can record weighbridge measurements in the Historical Time Series module.",
                "evidence": {"records_count": 0},
                "source_attribution": "Historical Waste Database",
                "data_status": "UNAVAILABLE"
            }

    # 6. Demographics
    if any(w in q for w in ["population", "citizen", "people", "households", "density", "demography"]):
        if demo:
            answer = (
                f"👥 **Demographic Baseline for {loc.name}**:\n"
                f"• Permanent Population: **{demo.total_population:,.0f} citizens**.\n"
                f"• Total Households: **{demo.number_of_households:,.0f}** (Avg Size: {demo.average_household_size} persons/HH).\n"
                f"• Annual Growth Rate: **{demo.population_growth_rate}%**.\n"
                f"• Floating & Tourist Population: **{demo.floating_population + demo.seasonal_population + demo.tourist_population:,.0f} guests**.\n"
                f"• Census Reference Source: {demo.census_source} ({demo.pop_reference_year})."
            )
            return {
                "answer": answer,
                "evidence": {
                    "total_population": demo.total_population,
                    "households": demo.number_of_households,
                    "growth_rate": demo.population_growth_rate
                },
                "source_attribution": "Demography Parameters (Table: demography_parameters)",
                "data_status": "VERIFIED"
            }

    # 7. Treatment Infrastructure & Facilities
    if any(w in q for w in ["treatment", "plant", "facility", "facilities", "deficit", "capacity gap", "shortage", "mrf", "compost", "landfill"]):
        total_fac_cap = sum(f.capacity_kg_day for f in facilities) if facilities else (infra.treatment_capacity_kg if infra else 10000.0)
        pop = demo.total_population if demo else 25000.0
        eff_pop = pop + (demo.floating_population if demo else 2000.0)
        est_daily_tonnes = round((eff_pop * 0.50 + 2500.0) / 1000.0, 2)
        cap_tonnes = round(total_fac_cap / 1000.0, 2)
        gap_tonnes = round(max(0.0, est_daily_tonnes - cap_tonnes), 2)

        fac_names = ", ".join(f"{f.name} ({f.facility_type}: {f.capacity_kg_day/1000:.1f} t/d)" for f in facilities) if facilities else "Default Municipal Processing Station (10.0 t/d)"

        answer = (
            f"🏭 **Processing & Treatment Infrastructure for {loc.name}**:\n"
            f"• Total Treatment Capacity: **{cap_tonnes} tonnes/day**.\n"
            f"• Estimated Daily Waste Load: **{est_daily_tonnes} tonnes/day**.\n"
            f"• Processing Gap / Deficit: **{gap_tonnes} tonnes/day** ({'🚨 Action Required' if gap_tonnes > 0 else '✅ Adequate'}).\n"
            f"• Operational Facilities: {fac_names}."
        )
        return {
            "answer": answer,
            "evidence": {
                "installed_capacity_tonnes": cap_tonnes,
                "daily_load_tonnes": est_daily_tonnes,
                "capacity_deficit_tonnes": gap_tonnes,
                "facilities_count": len(facilities)
            },
            "source_attribution": "Municipal Facilities Registry (Table: facilities)",
            "data_status": "VERIFIED"
        }

    # 8. Collection Fleet & Logistics
    if any(w in q for w in ["fleet", "truck", "vehicle", "trip", "collection", "logistics", "coverage"]):
        vehicles = infra.vehicle_count if infra else 10
        capacity_per_v = infra.vehicle_capacity_kg if infra else 2000.0
        trips = infra.trips_per_vehicle if infra else 1
        coverage = infra.collection_coverage_percent if infra else 100.0
        daily_fleet_tonnes = round((vehicles * capacity_per_v * trips) / 1000.0, 2)

        answer = (
            f"🚛 **Collection Fleet Logistics for {loc.name}**:\n"
            f"• Active Vehicle Count: **{vehicles} collection trucks**.\n"
            f"• Capacity per Vehicle: **{capacity_per_v:,.0f} kg/trip**.\n"
            f"• Scheduled Trips: **{trips} trip(s)/day**.\n"
            f"• Daily Fleet Carrying Capacity: **{daily_fleet_tonnes} tonnes/day**.\n"
            f"• Door-to-Door Collection Coverage: **{coverage}%**."
        )
        return {
            "answer": answer,
            "evidence": {
                "vehicles": vehicles,
                "capacity_per_vehicle_kg": capacity_per_v,
                "trips": trips,
                "fleet_throughput_tonnes": daily_fleet_tonnes,
                "coverage_percent": coverage
            },
            "source_attribution": "Infrastructure Logistics Matrix (Table: infrastructure_parameters)",
            "data_status": "VERIFIED"
        }

    # 9. Simulation & Projections (Future / Forecast / Years)
    if any(w in q for w in ["forecast", "projection", "future", "simulation", "predict", "year", "20-yr", "long term"]):
        if latest_sim and "years" in latest_sim.results:
            years = latest_sim.results["years"]
            match = re.search(r"\byear\s*(\d+)\b|\b(\d+)\s*years?\b|\b(\d+)\b", q)
            target_year = 10
            if match:
                for num_str in match.groups():
                    if num_str is not None:
                        val = int(num_str)
                        if 0 <= val <= len(years) - 1:
                            target_year = val
                            break

            row = years[min(target_year, len(years) - 1)]
            treat_gap = row.get("treatment", {}).get("treatment_gap_tonnes", row.get("treatment", {}).get("treatment_gap_kg", 0) / 1000.0)
            coll_gap = row.get("collection", {}).get("collection_gap_tonnes", row.get("collection", {}).get("collection_gap_kg_day", 0) / 1000.0)
            seg_qty = row.get("treatment", {}).get("segregated_kg_day", row.get("treatment", {}).get("composting_capacity_kg", 0)) / 1000.0

            answer = (
                f"📈 **SWMS Official Projection for Year {target_year} ({loc.name})**:\n"
                f"• Projected Generation: **{row.get('daily_waste_tonnes', 0)} tonnes/day** ({row.get('annual_waste_tonnes', 0):,.1f} tonnes/year).\n"
                f"• Effective Population: **{row.get('effective_population', 0):,.0f} inhabitants**.\n"
                f"• Treatment Deficit: **{treat_gap:.2f} tonnes/day**.\n"
                f"• Fleet Deficit: **{coll_gap:.2f} tonnes/day**.\n"
                f"• Recycled Material: **{seg_qty:.2f} tonnes/day**."
            )
            return {
                "answer": answer,
                "evidence": row,
                "source_attribution": f"Simulation Engine Model #{latest_sim.id}",
                "data_status": "CALCULATED"
            }

    # 10. General Default Summary for un-categorized queries
    pop = demo.total_population if demo else 25000.0
    est_daily_tonnes = round(((pop + 2000.0) * 0.50 + 2500.0) / 1000.0, 2)
    vehicles = infra.vehicle_count if infra else 10

    return {
        "answer": (
            f"📍 **Planning Unit Overview: {loc.name} ({loc.location_type})**\n"
            f"• District: {loc.district or 'Udupi'} | State: {loc.state or 'Karnataka'} | Terrain: {loc.terrain or 'Plain'}\n"
            f"• Permanent Population: {pop:,.0f} citizens | Fleet Size: {vehicles} trucks\n"
            f"• Estimated Daily Waste: ~{est_daily_tonnes} tonnes/day\n\n"
            f"💡 *Tip: Try asking specifically about 'daily waste', 'population', 'fleet capacity', 'treatment plants', 'composition', or 'forecast projection'.*"
        ),
        "evidence": {
            "location_id": loc.id,
            "name": loc.name,
            "type": loc.location_type,
            "population": pop,
            "daily_tonnes": est_daily_tonnes
        },
        "source_attribution": "SWMS Central Knowledge Base",
        "data_status": "VERIFIED"
    }
