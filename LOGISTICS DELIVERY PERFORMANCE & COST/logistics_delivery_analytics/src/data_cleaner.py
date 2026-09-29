"""Cleaning and type normalization for the logistics dataset."""

import pandas as pd


DATE_COLUMNS = [
    "order_date",
    "dispatch_date",
    "expected_delivery_date",
    "actual_delivery_date",
]
NUMERIC_COLUMNS = [
    "distance_km",
    "quantity",
    "weight_kg",
    "shipping_cost",
    "fuel_cost",
    "warehouse_processing_hours",
    "customer_rating",
]
REQUIRED_COLUMNS = ["order_id", "order_date", "expected_delivery_date", "actual_delivery_date"]


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize values, remove exact duplicates, and impute missing fuel cost.

    Missing fuel cost is filled with the median for that shipping mode, falling
    back to the dataset median. Ratings and processing hours remain missing.
    """
    cleaned = data.copy()

    text_columns = [
        column for column in cleaned.columns
        if pd.api.types.is_string_dtype(cleaned[column].dtype)
    ]
    for column in text_columns:
        cleaned[column] = cleaned[column].str.strip().replace("", pd.NA)

    for column in ("shipping_mode", "delivery_partner"):
        if column in cleaned.columns:
            labels = cleaned[column].dropna()
            canonical_labels = labels.groupby(labels.str.casefold()).agg(
                lambda values: values.value_counts().index[0]
            )
            cleaned[column] = cleaned[column].str.casefold().map(canonical_labels)

    cleaned = cleaned.drop_duplicates().copy()

    for column in DATE_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    present_required = [column for column in REQUIRED_COLUMNS if column in cleaned.columns]
    if present_required:
        cleaned = cleaned.dropna(subset=present_required).copy()

    if "fuel_cost" in cleaned.columns:
        if "shipping_mode" in cleaned.columns:
            mode_medians = cleaned.groupby("shipping_mode", dropna=False)["fuel_cost"].transform("median")
            cleaned["fuel_cost"] = cleaned["fuel_cost"].fillna(mode_medians)
        cleaned["fuel_cost"] = cleaned["fuel_cost"].fillna(cleaned["fuel_cost"].median())

    return cleaned.reset_index(drop=True)