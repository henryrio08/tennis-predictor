"""Print a quick summary of the configured ATP dataset."""

import os
from pathlib import Path

import pandas as pd

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "atp_tennis.csv"
DATA_PATH = Path(os.environ.get("DATA_PATH", DEFAULT_DATA))

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset: {DATA_PATH}")
    print(df.head())
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
    print("Missing values:")
    print(df.isna().sum())
