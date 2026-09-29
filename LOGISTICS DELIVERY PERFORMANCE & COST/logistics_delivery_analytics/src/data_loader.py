"""Load the raw logistics orders dataset."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "logistics_data.csv"


def load_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read a logistics CSV, parsing its date columns consistently."""
    return pd.read_csv(path, na_values=["", " ", "NA", "N/A"])