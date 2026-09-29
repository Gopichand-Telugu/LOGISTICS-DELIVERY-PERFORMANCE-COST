"""Operational metrics and report generation for logistics orders."""

from pathlib import Path

import pandas as pd


def add_business_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Add delivery timeliness, cost, and calendar dimensions."""
    result = data.copy()
    result["delay_days"] = (result["actual_delivery_date"] - result["expected_delivery_date"]).dt.days.clip(lower=0)
    result["on_time"] = result["actual_delivery_date"] <= result["expected_delivery_date"]
    result["delivery_days"] = (result["actual_delivery_date"] - result["dispatch_date"]).dt.days
    result["tracked_total_cost"] = result["shipping_cost"] + result["fuel_cost"]
    result["shipping_cost_per_km"] = result["shipping_cost"] / result["distance_km"].replace(0, pd.NA)
    result["order_month"] = result["order_date"].dt.to_period("M").astype(str)
    return result


def summarize_business(data: pd.DataFrame) -> dict[str, float | int]:
    """Return portfolio-level KPIs from data enriched by add_business_metrics."""
    return {
        "orders": int(data["order_id"].nunique()),
        "on_time_rate_pct": float(data["on_time"].mean() * 100),
        "average_shipping_cost": float(data["shipping_cost"].mean()),
        "average_tracked_total_cost": float(data["tracked_total_cost"].mean()),
        "average_customer_rating": float(data["customer_rating"].mean()),
        "average_delay_days_late_only": float(data.loc[~data["on_time"], "delay_days"].mean()),
        "damaged_order_rate_pct": float(data["damage_flag"].eq("Yes").mean() * 100),
        "returned_order_rate_pct": float(data["return_flag"].eq("Yes").mean() * 100),
    }


def write_business_report(
    data: pd.DataFrame,
    raw_rows: int,
    report_path: str | Path,
    raw_data: pd.DataFrame | None = None,
) -> Path:
    """Write a reproducible Markdown summary and grouped operating metrics."""
    metrics = summarize_business(data)
    raw_missing = raw_data.isna().sum() if raw_data is not None else pd.Series(dtype="int64")
    missing_summary = "; ".join(
        f"{column}: {int(count)}" for column, count in raw_missing.items() if count > 0
    ) or "None detected"
    partner = (
        data.groupby("delivery_partner", dropna=False)
        .agg(orders=("order_id", "nunique"), on_time_rate=("on_time", "mean"), avg_shipping_cost=("shipping_cost", "mean"), avg_rating=("customer_rating", "mean"))
        .sort_values("orders", ascending=False)
    )
    modes = (
        data.groupby("shipping_mode", dropna=False)
        .agg(orders=("order_id", "nunique"), on_time_rate=("on_time", "mean"), avg_shipping_cost=("shipping_cost", "mean"))
        .sort_values("orders", ascending=False)
    )

    partner_table = partner.to_string(float_format=lambda value: f"{value:.2f}")
    mode_table = modes.to_string(float_format=lambda value: f"{value:.2f}")
    report = f"""# Logistics Delivery Performance & Cost Report

## Scope and data quality

- Raw rows: {raw_rows:,}
- Cleaned orders: {metrics['orders']:,}
- Rows removed during cleaning: {raw_rows - len(data):,} (exact duplicates and rows missing required identifiers/dates)
- Missing values in the raw file: {missing_summary}.
- Missing fuel cost is imputed using the shipping-mode median, then the overall median. Missing shipping costs, destinations, customer ratings, and warehouse processing hours are retained.
- The source `delivery_status` field is retained; on-time performance is independently calculated from actual versus expected delivery dates.

## Portfolio snapshot

| KPI | Value |
| --- | ---: |
| Unique orders | {metrics['orders']:,} |
| On-time delivery | {metrics['on_time_rate_pct']:.1f}% |
| Average shipping cost | {metrics['average_shipping_cost']:,.2f} |
| Average tracked shipping + fuel cost | {metrics['average_tracked_total_cost']:,.2f} |
| Average customer rating | {metrics['average_customer_rating']:.2f} / 5 |
| Average delay among late orders | {metrics['average_delay_days_late_only']:.2f} days |
| Orders flagged damaged | {metrics['damaged_order_rate_pct']:.1f}% |
| Orders flagged returned | {metrics['returned_order_rate_pct']:.1f}% |

## Delivery partner comparison

Rates and costs are unadjusted averages; differences may reflect route, distance, mode, or order mix.

```text
{partner_table}
```

## Shipping mode comparison

```text
{mode_table}
```

## Interpretation notes

- `tracked_total_cost` is the sum of recorded shipping and fuel costs; confirm whether fuel is already included in shipping charges before treating it as an accounting total.
- Compare delivery partners within similar routes and shipping modes before making sourcing decisions.
- Missing ratings, shipping costs, and warehouse processing hours are not imputed; averages use available observations only. Destination city remains blank where missing.
"""
    output = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return output