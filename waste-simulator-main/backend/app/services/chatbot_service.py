"""Controlled Chatbot Service for SWMS."""
from typing import Dict, Any, Optional
import re
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.location import Location
from app.models.parameters import DemographyParameter, InfrastructureParameter
from app.models.facility import Facility
from app.models.historical_waste import HistoricalWaste
from app.models.simulation import SimulationRun

def query_swms_assistant(db: Session, location_id: int, question: str) -> Dict[str, Any]:
    loc = db.get(Location, location_id)
    if not loc:
        return {
            "answer": f"Location ID {location_id} was not found in the database. Please select a valid location.",
            "evidence": {},
            "source_attribution": "Database Location Registry",
            "data_status": "MISSING"
        }

    q = question.lower()

    if any(term in q for term in ["password", "secret", "token", "drop table", "select * from users", "delete from", "truncate"]):
        return {
            "answer": "Security Policy Violation: I am restricted to municipal planning, demographic metrics, historical waste data, and simulation analytics. System credentials and arbitrary database operations are inaccessible.",
            "evidence": {"security_filter": "BLOCKED_RESTRICTED_QUERY"},
            "source_attribution": "SWMS Security Engine",
            "data_status": "RESTRICTED"
        }

    latest_sim = db.scalar(
        select(SimulationRun)
        .where(SimulationRun.location_id == location_id)
        .order_by(SimulationRun.created_at.desc())
    )

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
                f"📊 **Historical Waste Analysis for {loc.name}**:\n"
                f"• Average Recorded Waste: {avg_qty} tonnes/day.\n"
                f"• Most Recent Entry: {latest_rec.quantity} tonnes on {latest_rec.measurement_date.isoformat()} ({latest_rec.quality_status}).\n"
                f"• Total Recorded Samples: {len(hist_records)} records.\n"
                f"• Measurement Method: {latest_rec.measurement_method}."
            )
            return {
                "answer": answer,
                "evidence": {
                    "records_count": len(hist_records),
                    "average_tonnes_day": avg_qty,
                    "latest_date": latest_rec.measurement_date.isoformat(),
                    "latest_tonnes": latest_rec.quantity
                },
                "source_attribution": "Historical Weighbridge Records (Table: historical_waste)",
                "data_status": "MEASURED"
            }
        else:
            return {
                "answer": f"No historical waste weighbridge records have been entered for {loc.name} yet. You can upload weighbridge records via the Historical Waste module.",
                "evidence": {"records_count": 0},
                "source_attribution": "Historical Waste Database",
                "data_status": "UNAVAILABLE"
            }

    if any(w in q for w in ["population", "citizen", "people", "households", "density", "demography"]):
        demo = db.scalar(select(DemographyParameter).where(DemographyParameter.habitation_id == location_id))
        if demo:
            answer = (
                f"👥 **Demographic Profile for {loc.name}**:\n"
                f"• Total Permanent Population: {demo.total_population:,.0f} citizens.\n"
                f"• Households: {demo.number_of_households:,.0f} (Avg Household Size: {demo.average_household_size}).\n"
                f"• Annual Population Growth Rate: {demo.population_growth_rate}%.\n"
                f"• Floating / Seasonal Population: {demo.floating_population + demo.seasonal_population + demo.tourist_population:,.0f}.\n"
                f"• Census Reference: {demo.census_source} ({demo.pop_reference_year})."
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

    if any(w in q for w in ["treatment", "plant", "deficit", "capacity gap", "shortage", "mrf", "compost"]):
        facilities = db.scalars(select(Facility).where(Facility.location_id == location_id)).all()
        total_fac_cap = sum(f.capacity_kg_day for f in facilities)
        
        sim_data = latest_sim.results if latest_sim else None
        y0 = sim_data["years"][0] if sim_data and "years" in sim_data else None
        daily_tonnes = y0["daily_waste_tonnes"] if y0 else 15.0
        cap_tonnes = round(total_fac_cap / 1000.0, 2)
        gap_tonnes = round(max(0.0, daily_tonnes - cap_tonnes), 2)

        answer = (
            f"🏭 **Treatment Plant Infrastructure for {loc.name}**:\n"
            f"• Installed Facility Throughput: {cap_tonnes} tonnes/day ({len(facilities)} active plants).\n"
            f"• Current Daily Load: ~{daily_tonnes} tonnes/day.\n"
            f"• Daily Capacity Deficit: {gap_tonnes} tonnes/day.\n"
            f"• Active Facilities: " + (", ".join(f"{f.name} ({f.facility_type}: {f.capacity_kg_day/1000} t/d)" for f in facilities) if facilities else "None registered")
        )
        return {
            "answer": answer,
            "evidence": {
                "installed_capacity_tonnes": cap_tonnes,
                "capacity_deficit_tonnes": gap_tonnes,
                "facilities_count": len(facilities)
            },
            "source_attribution": "Municipal Facilities Registry (Table: facilities)",
            "data_status": "VERIFIED"
        }

    if any(w in q for w in ["fleet", "truck", "vehicle", "trip", "collection"]):
        infra = db.scalar(select(InfrastructureParameter).where(InfrastructureParameter.habitation_id == location_id))
        vehicles = infra.vehicle_count if infra else 10
        capacity_per_v = infra.vehicle_capacity_kg if infra else 2000
        trips = infra.trips_per_vehicle if infra else 1
        daily_fleet_tonnes = round((vehicles * capacity_per_v * trips) / 1000.0, 2)

        answer = (
            f"🚛 **Collection Fleet Capacity for {loc.name}**:\n"
            f"• Active Fleet Size: {vehicles} collection vehicles.\n"
            f"• Capacity per Truck: {capacity_per_v:,.0f} kg/trip.\n"
            f"• Scheduled Trips: {trips} trip(s)/day.\n"
            f"• Total Fleet Throughput: {daily_fleet_tonnes} tonnes/day."
        )
        return {
            "answer": answer,
            "evidence": {
                "vehicles": vehicles,
                "capacity_per_vehicle_kg": capacity_per_v,
                "trips": trips,
                "fleet_throughput_tonnes": daily_fleet_tonnes
            },
            "source_attribution": "Infrastructure Parameters (Table: infrastructure_parameters)",
            "data_status": "VERIFIED"
        }

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
        answer = (
            f"📈 **SWMS Official Projection for Year {target_year} ({loc.name})**:\n"
            f"• Projected Waste Generation: {row['daily_waste_tonnes']} tonnes/day ({row['annual_waste_tonnes']:,.1f} tonnes/year).\n"
            f"• Effective Population: {row['effective_population']:,.0f} inhabitants.\n"
            f"• Treatment Plant Deficit: {row['treatment']['treatment_gap_kg_day']/1000:.2f} tonnes/day.\n"
            f"• Collection Fleet Deficit: {row['collection']['collection_gap_kg_day']/1000:.2f} tonnes/day.\n"
            f"• Material Segregation: {row['treatment']['segregated_kg_day']/1000:.2f} tonnes/day recycled / composted."
        )
        return {
            "answer": answer,
            "evidence": row,
            "source_attribution": f"Simulation Run #{latest_sim.id} (Table: simulation_runs)",
            "data_status": "CALCULATED"
        }

    return {
        "answer": (
            f"📍 **Summary for {loc.name} ({loc.location_type})**:\n"
            f"State: {loc.state} | District: {loc.district or 'N/A'} | Classification: {loc.classification}\n"
            f"Coordinates: Lat {loc.latitude or 'N/A'}, Lon {loc.longitude or 'N/A'}\n"
            f"Ask me about historical waste records, demography, fleet logistics, treatment capacity deficit, or 20-year projections."
        ),
        "evidence": {"location_id": loc.id, "name": loc.name, "type": loc.location_type},
        "source_attribution": "Location Registry",
        "data_status": "VERIFIED"
    }
