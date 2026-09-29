"""Focused tests for data cleaning and logistics metric definitions."""

import pandas as pd

from src.business_analysis import add_business_metrics
from src.data_cleaner import clean_data


def sample_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["A1", "A1", "B2"],
            "customer_id": ["C1", "C1", "C2"],
            "order_date": ["2025-01-01", "2025-01-01", "2025-01-02"],
            "warehouse": ["Delhi", "Delhi", "Mumbai"],
            "origin_city": ["Delhi", "Delhi", "Mumbai"],
            "destination_city": ["Jaipur", "Jaipur", "Pune"],
            "distance_km": [200, 200, 150],
            "product_category": ["Books", "Books", "Clothing"],
            "quantity": [1, 1, 2],
            "weight_kg": [1.0, 1.0, 2.0],
            "shipping_mode": ["Road", "road", "Air"],
            "delivery_partner": ["Partner A", "partner a", "Partner B"],
            "shipping_cost": [400.0, 400.0, 800.0],
            "fuel_cost": [None, None, 100.0],
            "warehouse_processing_hours": [5.0, 5.0, None],
            "dispatch_date": ["2025-01-02", "2025-01-02", "2025-01-03"],
            "expected_delivery_date": ["2025-01-05", "2025-01-05", "2025-01-06"],
            "actual_delivery_date": ["2025-01-04", "2025-01-04", "2025-01-08"],
            "delivery_status": ["Delivered", "Delivered", "Delayed"],
            "customer_rating": [5.0, 5.0, None],
            "damage_flag": ["No", "No", "No"],
            "return_flag": ["No", "No", "Yes"],
        }
    )


def test_clean_data_drops_exact_duplicates_and_imputes_mode_median() -> None:
    cleaned = clean_data(sample_orders())

    assert len(cleaned) == 2
    assert cleaned["order_id"].is_unique
    assert cleaned.loc[cleaned["order_id"] == "A1", "delivery_partner"].item() == "Partner A"
    assert cleaned.loc[cleaned["order_id"] == "A1", "fuel_cost"].item() == 100.0
    assert pd.api.types.is_datetime64_any_dtype(cleaned["order_date"])
    assert cleaned["customer_rating"].isna().sum() == 1


def test_business_metrics_use_expected_date_for_timeliness() -> None:
    enriched = add_business_metrics(clean_data(sample_orders()))

    assert enriched["on_time"].tolist() == [True, False]
    assert enriched["delay_days"].tolist() == [0, 2]
    assert enriched["tracked_total_cost"].tolist() == [500.0, 900.0]
    assert enriched["order_month"].tolist() == ["2025-01", "2025-01"]