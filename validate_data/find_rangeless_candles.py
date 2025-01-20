from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def analyze_candle_ranges():
    """
    Analyze candles for zero or suspicious ranges
    """
    # Read the combined data file
    filepath = "../data/MNQ/combined_MNQ_2023_2024.csv"
    df = pd.read_csv(filepath)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Calculate ranges
    df["candle_range"] = abs(df["high"] - df["low"])

    # Find zero range candles
    zero_range = df[df["candle_range"] == 0].copy()

    # Find suspiciously small ranges (e.g., less than 0.01)
    tiny_range = df[(df["candle_range"] > 0) & (df["candle_range"] < 0.01)].copy()

    # Check for price consistency
    inconsistent = df[
        (df["high"] < df["low"])
        | (df["open"] > df["high"])  # High should never be less than low
        | (df["open"] < df["low"])  # Open should never be higher than high
        | (df["close"] > df["high"])  # Open should never be lower than low
        | (  # Close should never be higher than high
            df["close"] < df["low"]
        )  # Close should never be lower than low
    ].copy()

    print("=== Candle Range Analysis ===")
    print(f"\nTotal candles analyzed: {len(df):,}")

    print("\nZero Range Candles:")
    print(f"Count: {len(zero_range)}")
    if not zero_range.empty:
        print("\nSample of zero range candles:")
        print(
            zero_range[["timestamp", "open", "high", "low", "close", "volume"]].head()
        )

    print("\nTiny Range Candles (0 < range < 0.01):")
    print(f"Count: {len(tiny_range)}")
    if not tiny_range.empty:
        print("\nSample of tiny range candles:")
        print(
            tiny_range[["timestamp", "open", "high", "low", "close", "volume"]].head()
        )

    print("\nInconsistent Price Candles:")
    print(f"Count: {len(inconsistent)}")
    if not inconsistent.empty:
        print("\nSample of inconsistent candles:")
        print(
            inconsistent[["timestamp", "open", "high", "low", "close", "volume"]].head()
        )

    # Range distribution analysis
    print("\nRange Distribution Statistics:")
    range_stats = df["candle_range"].describe()
    print(range_stats)

    # Save problematic candles to CSV for further investigation
    if not zero_range.empty or not tiny_range.empty or not inconsistent.empty:
        output_dir = Path("../data/analysis")
        output_dir.mkdir(exist_ok=True)

        if not zero_range.empty:
            zero_range.to_csv(output_dir / "zero_range_candles.csv", index=False)
        if not tiny_range.empty:
            tiny_range.to_csv(output_dir / "tiny_range_candles.csv", index=False)
        if not inconsistent.empty:
            inconsistent.to_csv(output_dir / "inconsistent_candles.csv", index=False)

        print("\nDetailed results have been saved to the data/analysis directory")


if __name__ == "__main__":
    analyze_candle_ranges()
