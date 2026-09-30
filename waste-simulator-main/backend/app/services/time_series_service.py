"""Time Series Analytics Service for SWMS."""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import statistics

def analyze_time_series_records(
    records: List[Dict[str, Any]],
    period_type: str = "CUSTOM",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    if not records:
        return {
            "period_type": period_type,
            "start_date": start_date,
            "end_date": end_date,
            "records_count": 0,
            "total_quantity_tonnes": 0.0,
            "daily_average_tonnes": 0.0,
            "median_tonnes": 0.0,
            "minimum_tonnes": 0.0,
            "maximum_tonnes": 0.0,
            "std_dev": 0.0,
            "trend_direction": "NO_DATA",
            "percentage_change": 0.0,
            "weekday_pattern": {},
            "source_breakdown": {},
            "composition_estimate": {},
            "yoy_growth_percent": None,
            "data_quality_summary": {"status": "NO_DATA", "completeness_pct": 0.0, "missing_dates": []},
            "daily_time_series": []
        }

    sorted_records = sorted(records, key=lambda x: x["measurement_date"])
    
    # Filter by period_type if start_date/end_date not explicitly supplied
    if sorted_records and period_type and period_type not in ["ALL", "ALL_RECORDS", "CUSTOM"]:
        max_d = sorted_records[-1]["measurement_date"]
        days_map = {
            "1_DAY": 1,
            "2_DAY": 2,
            "2_DAYS": 2,
            "1_WEEK": 7,
            "1_MONTH": 30,
            "3_MONTH": 90,
            "3_MONTHS": 90,
            "6_MONTH": 180,
            "6_MONTHS": 180,
            "1_YEAR": 365,
            "1_YEARS": 365,
            "2_YEARS": 730,
        }
        if period_type in days_map:
            cutoff = max_d - timedelta(days=days_map[period_type])
            sorted_records = [r for r in sorted_records if r["measurement_date"] > cutoff]
            if not sorted_records:
                sorted_records = sorted(records, key=lambda x: x["measurement_date"])

    quantities = [float(r["quantity"]) for r in sorted_records]
    dates = [r["measurement_date"] for r in sorted_records]
    
    total_qty = sum(quantities)
    count = len(quantities)
    mean_val = total_qty / count if count > 0 else 0.0
    median_val = statistics.median(quantities) if count > 0 else 0.0
    min_val = min(quantities) if count > 0 else 0.0
    max_val = max(quantities) if count > 0 else 0.0
    std_dev = statistics.stdev(quantities) if count > 1 else 0.0

    trend_dir = "STABLE"
    pct_change = 0.0
    if count >= 2:
        first_val = quantities[0]
        last_val = quantities[-1]
        pct_change = round(((last_val - first_val) / first_val * 100) if first_val > 0 else 0.0, 2)
        if pct_change > 2.0:
            trend_dir = "INCREASING"
        elif pct_change < -2.0:
            trend_dir = "DECREASING"

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_bins = {day: [] for day in weekday_names}
    for r in sorted_records:
        d = r["measurement_date"]
        weekday = weekday_names[d.weekday()]
        weekday_bins[weekday].append(float(r["quantity"]))
    weekday_pattern = {
        day: round(statistics.mean(vals), 2) if vals else 0.0 
        for day, vals in weekday_bins.items()
    }

    source_breakdown = {}
    for r in sorted_records:
        src = r.get("waste_category") or r.get("source_name") or "Mixed Waste"
        source_breakdown[src] = round(source_breakdown.get(src, 0.0) + float(r["quantity"]), 2)

    min_date = dates[0]
    max_date = dates[-1]
    expected_days = (max_date - min_date).days + 1
    date_set = set(dates)
    missing_dates = []
    curr = min_date
    while curr <= max_date:
        if curr not in date_set:
            missing_dates.append(curr.isoformat())
        curr += timedelta(days=1)

    completeness_pct = round((count / expected_days * 100), 1) if expected_days > 0 else 100.0

    yoy_growth = None
    if (max_date - min_date).days >= 365:
        mid_date = min_date + timedelta(days=365)
        y1_qty = sum(r["quantity"] for r in sorted_records if r["measurement_date"] < mid_date)
        y2_qty = sum(r["quantity"] for r in sorted_records if r["measurement_date"] >= mid_date)
        if y1_qty > 0:
            yoy_growth = round(((y2_qty - y1_qty) / y1_qty) * 100.0, 2)

    daily_ts = []
    for r in sorted_records:
        qty_val = round(float(r["quantity"]), 3)
        daily_ts.append({
            "date": r["measurement_date"].isoformat(),
            "quantity": qty_val,
            "quantity_tonnes": qty_val,
            "category": r.get("waste_category", "MIXED"),
            "quality_status": r.get("quality_status", "MEASURED")
        })

    return {
        "period_type": period_type,
        "start_date": min_date,
        "end_date": max_date,
        "records_count": count,
        "total_quantity_tonnes": round(total_qty, 3),
        "daily_average_tonnes": round(mean_val, 3),
        "median_tonnes": round(median_val, 3),
        "minimum_tonnes": round(min_val, 3),
        "maximum_tonnes": round(max_val, 3),
        "std_dev": round(std_dev, 3),
        "trend_direction": trend_dir,
        "percentage_change": pct_change,
        "weekday_pattern": weekday_pattern,
        "source_breakdown": source_breakdown,
        "composition_estimate": {
            "Organic": round(total_qty * 0.52, 2),
            "Recyclable": round(total_qty * 0.28, 2),
            "Inert / Landfill": round(total_qty * 0.20, 2)
        },
        "yoy_growth_percent": yoy_growth,
        "data_quality_summary": {
            "status": "EXCELLENT" if completeness_pct >= 95 else "ADEQUATE" if completeness_pct >= 80 else "WARNING",
            "completeness_pct": completeness_pct,
            "missing_dates_count": len(missing_dates),
            "missing_dates": missing_dates[:15]
        },
        "daily_time_series": daily_ts
    }
