"""Forecasting Service for SWMS."""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import math
import statistics

def calculate_errors(actuals: List[float], predictions: List[float]) -> Tuple[float, float, Optional[float]]:
    if not actuals or len(actuals) != len(predictions):
        return 0.0, 0.0, None

    n = len(actuals)
    abs_errors = [abs(a - p) for a, p in zip(actuals, predictions)]
    sq_errors = [(a - p) ** 2 for a, p in zip(actuals, predictions)]

    mae = sum(abs_errors) / n
    rmse = math.sqrt(sum(sq_errors) / n)

    if all(a > 0.01 for a in actuals):
        mape = (sum(abs(a - p) / a for a, p in zip(actuals, predictions)) / n) * 100.0
    else:
        mape = None

    return round(mae, 3), round(rmse, 3), round(mape, 2) if mape is not None else None

def forecast_baseline(series: List[float], steps: int = 1) -> List[float]:
    val = series[-1] if series else 0.0
    return [round(val, 3)] * steps

def forecast_moving_average(series: List[float], window: int = 3, steps: int = 1) -> List[float]:
    if not series:
        return [0.0] * steps
    k = min(window, len(series))
    avg = sum(series[-k:]) / k
    return [round(avg, 3)] * steps

def forecast_weighted_ma(series: List[float], window: int = 3, steps: int = 1) -> List[float]:
    if not series:
        return [0.0] * steps
    k = min(window, len(series))
    recent = series[-k:]
    weights = list(range(1, k + 1))
    weighted_sum = sum(w * x for w, x in zip(weights, recent))
    total_weights = sum(weights)
    val = weighted_sum / total_weights
    return [round(val, 3)] * steps

def forecast_trend_adjusted(series: List[float], steps: int = 1) -> List[float]:
    n = len(series)
    if n < 2:
        return forecast_baseline(series, steps)

    x = list(range(n))
    y = series
    x_mean = sum(x) / n
    y_mean = sum(y) / n

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    slope = numerator / denominator if denominator != 0 else 0.0
    intercept = y_mean - slope * x_mean

    results = []
    for step in range(1, steps + 1):
        future_x = n - 1 + step
        pred = max(0.0, intercept + slope * future_x)
        results.append(round(pred, 3))
    return results

def forecast_seasonal_baseline(series: List[float], season_length: int = 7, steps: int = 1) -> List[float]:
    n = len(series)
    if n < season_length * 2:
        return forecast_weighted_ma(series, window=min(5, n), steps=steps)

    overall_mean = sum(series) / n if n > 0 else 1.0
    if overall_mean == 0:
        return [0.0] * steps

    seasonal_indices = []
    for i in range(season_length):
        season_vals = [series[j] for j in range(i, n, season_length)]
        season_mean = sum(season_vals) / len(season_vals) if season_vals else overall_mean
        seasonal_indices.append(season_mean / overall_mean)

    recent_baseline = sum(series[-season_length:]) / season_length
    results = []
    for step in range(1, steps + 1):
        idx = (n + step - 1) % season_length
        val = max(0.0, recent_baseline * seasonal_indices[idx])
        results.append(round(val, 3))
    return results

def run_forecast_evaluation(
    historical_points: List[Dict[str, Any]],
    period: str = "NEXT_MONTH",
    selected_method_override: Optional[str] = None
) -> Dict[str, Any]:
    if not historical_points:
        return {
            "forecast_value": 0.0,
            "selected_method": "NO_DATA",
            "selection_reason": "No historical waste data is available for this location to compute a forecast.",
            "confidence_level": "NONE",
            "limitations": "Forecast cannot be generated without historical baseline records.",
            "mae": None, "rmse": None, "mape": None,
            "method_comparison": [],
            "projected_series": []
        }

    sorted_records = sorted(historical_points, key=lambda x: x["measurement_date"])
    series = [float(r["quantity"]) for r in sorted_records]
    dates = [r["measurement_date"] for r in sorted_records]
    n = len(series)

    steps = 1
    if period in ["NEXT_WEEK", "1_WEEK"]:
        steps = 7
    elif period in ["NEXT_MONTH", "1_MONTH"]:
        steps = 30
    elif period in ["NEXT_YEAR", "1_YEAR"]:
        steps = 12

    methods_to_test = [
        ("BASELINE", lambda s, k: forecast_baseline(s, k)),
        ("MOVING_AVERAGE", lambda s, k: forecast_moving_average(s, window=3, steps=k)),
        ("WEIGHTED_MOVING_AVERAGE", lambda s, k: forecast_weighted_ma(s, window=3, steps=k)),
        ("TREND_ADJUSTED", lambda s, k: forecast_trend_adjusted(s, steps=k)),
        ("SEASONAL_BASELINE", lambda s, k: forecast_seasonal_baseline(s, season_length=7 if n >= 14 else 3, steps=k)),
    ]

    method_evaluations = []
    if n >= 6:
        split_idx = max(3, int(n * 0.8))
        train = series[:split_idx]
        test = series[split_idx:]
        test_len = len(test)

        for name, fn in methods_to_test:
            preds = fn(train, test_len)
            mae, rmse, mape = calculate_errors(test, preds)
            method_evaluations.append({
                "method": name,
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "test_window": test_len
            })
        
        method_evaluations.sort(key=lambda x: x["mae"])
        best_method = method_evaluations[0]["method"]
        best_mae = method_evaluations[0]["mae"]
        best_rmse = method_evaluations[0]["rmse"]
        best_mape = method_evaluations[0]["mape"]
        auto_reason = f"{best_method} was selected because it achieved the lowest backtesting error (MAE: {best_mae} tonnes, RMSE: {best_rmse} tonnes) on {test_len} validation records."
    else:
        best_method = "WEIGHTED_MOVING_AVERAGE" if n >= 3 else "BASELINE"
        best_mae = None
        best_rmse = None
        best_mape = None
        auto_reason = f"{best_method} was selected as a robust baseline for limited historical records ({n} data points available)."

    chosen_method_name = selected_method_override if selected_method_override and selected_method_override != "AUTO" else best_method
    method_fn = dict(methods_to_test).get(chosen_method_name, lambda s, k: forecast_weighted_ma(s, 3, k))
    predictions = method_fn(series, steps)
    forecast_val = round(sum(predictions) / steps, 3)

    last_date = dates[-1]
    projected_series = []
    for i, p in enumerate(predictions):
        future_date = last_date + timedelta(days=i + 1)
        projected_series.append({
            "date": future_date.isoformat(),
            "forecast_tonnes": p,
            "method": chosen_method_name
        })

    confidence = "HIGH" if n >= 30 and (best_mae is not None and best_mae < 2.0) else "MEDIUM" if n >= 10 else "LOW"

    return {
        "forecast_value": forecast_val,
        "selected_method": chosen_method_name,
        "selection_reason": auto_reason if chosen_method_name == best_method else f"User explicitly selected {chosen_method_name} override.",
        "confidence_level": confidence,
        "limitations": "Projections assume continuation of historical growth rates and do not account for unmodelled natural disasters or abrupt industrial closures.",
        "mae": best_mae,
        "rmse": best_rmse,
        "mape": best_mape,
        "historical_points_used": n,
        "training_start": dates[0],
        "training_end": dates[-1],
        "method_comparison": method_evaluations,
        "projected_series": projected_series
    }
