from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def read_and_validate_data(file_path):
    """
    Read a single data file and perform basic validation
    """
    try:
        df = pd.read_csv(
            file_path,
            delimiter=";",
            names=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d %H%M%S")
        df["source_file"] = file_path.name
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return None


def join_data_files():
    data_dir = Path("../data/MNQ")
    data_files = sorted(data_dir.glob("MNQ *.Last.txt"))

    print("\nReading and processing files:")
    all_data = pd.DataFrame()

    for file_path in data_files:
        print(f"\nProcessing {file_path.name}...")
        df = read_and_validate_data(file_path)
        if df is not None:
            print(f"  Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"  Records: {len(df):,}")
            all_data = pd.concat([all_data, df])

    # Sort by timestamp and handle overlaps
    print("\nHandling overlaps and sorting data...")
    all_data = all_data.sort_values("timestamp")

    # Keep the most recent data for each timestamp
    all_data = all_data.drop_duplicates(subset=["timestamp"], keep="last")

    # Find gaps
    all_data = all_data.sort_values("timestamp").reset_index(drop=True)
    time_diff = all_data["timestamp"].diff()
    gaps = time_diff[time_diff > timedelta(minutes=1)]

    if not gaps.empty:
        print("\nGaps found in data:")
        for idx in gaps.index:
            gap_start = all_data.iloc[idx - 1]["timestamp"]
            gap_end = all_data.iloc[idx]["timestamp"]
            gap_size = gaps[idx]
            print(f"  Gap from {gap_start} to {gap_end} ({gap_size})")

    # Basic statistics
    print("\nFinal Dataset Summary:")
    print(f"Total records: {len(all_data):,}")
    print(f"Date range: {all_data['timestamp'].min()} to {all_data['timestamp'].max()}")

    # Check for price continuity at file boundaries
    all_data["next_file"] = all_data["source_file"].shift(-1)
    file_boundaries = all_data[all_data["source_file"] != all_data["next_file"]].copy()

    if not file_boundaries.empty:
        print("\nChecking price continuity at file boundaries:")
        for idx in file_boundaries.index:
            current_record = all_data.iloc[idx]
            if idx + 1 < len(all_data):
                next_record = all_data.iloc[idx + 1]
                price_diff = abs(current_record["close"] - next_record["open"])
                if price_diff > 10:  # Adjust threshold as needed
                    print(f"  Large price gap ({price_diff:.2f}) at boundary:")
                    print(
                        f"    {current_record['timestamp']}: {current_record['source_file']} close: {current_record['close']}"
                    )
                    print(
                        f"    {next_record['timestamp']}: {next_record['source_file']} open: {next_record['open']}"
                    )

    # Save processed data
    output_file = "../data/MNQ/combined_MNQ_2023_2024_cleaned.csv"
    all_data = all_data.drop(["source_file", "next_file"], axis=1)
    all_data.to_csv(output_file, index=False)
    print(f"\nSaved cleaned and combined data to: {output_file}")

    return all_data


if __name__ == "__main__":
    joined_data = join_data_files()
