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


def create_continuous_contract(all_data):
    """
    Create a continuous contract using volume-based roll detection
    with backwards price adjustment.
    """
    # Extract contract months and sort data
    all_data["contract_month"] = all_data["source_file"].str.extract(
        r"MES (\d{2}-\d{2})"
    )[0]
    all_data = all_data.sort_values("timestamp")

    # Calculate daily volume for each contract
    daily_volume = (
        all_data.groupby(["contract_month", pd.Grouper(key="timestamp", freq="D")])[
            "volume"
        ]
        .sum()
        .reset_index()
    )

    # Find roll dates based on volume crossover
    roll_dates = []
    contract_months = sorted(daily_volume["contract_month"].unique())

    for i in range(len(contract_months) - 1):
        current_contract = contract_months[i]
        next_contract = contract_months[i + 1]

        # Get daily volumes for both contracts
        current_vol = daily_volume[daily_volume["contract_month"] == current_contract]
        next_vol = daily_volume[daily_volume["contract_month"] == next_contract]

        # Find dates where both contracts trade
        current_dates = set(current_vol["timestamp"].dt.date)
        next_dates = set(next_vol["timestamp"].dt.date)
        common_dates = current_dates & next_dates

        if common_dates:
            # Find first date where next contract volume exceeds current
            for date in sorted(common_dates):
                curr_vol = current_vol[current_vol["timestamp"].dt.date == date][
                    "volume"
                ].iloc[0]
                next_vol = next_vol[next_vol["timestamp"].dt.date == date][
                    "volume"
                ].iloc[0]

                if next_vol > curr_vol:
                    roll_dates.append((date, current_contract, next_contract))
                    print(
                        f"\nRoll detected from {current_contract} to {next_contract} on {date}"
                    )
                    print(f"  Current contract volume: {curr_vol:,}")
                    print(f"  Next contract volume: {next_vol:,}")
                    break

    # Create continuous contract by adjusting prices at roll dates
    continuous_data = all_data.copy()
    price_columns = ["open", "high", "low", "close"]

    for roll_date, old_contract, new_contract in roll_dates:
        # Calculate adjustment factor based on close price difference
        old_close = all_data[
            (all_data["contract_month"] == old_contract)
            & (all_data["timestamp"].dt.date == roll_date)
        ]["close"].iloc[-1]

        new_close = all_data[
            (all_data["contract_month"] == new_contract)
            & (all_data["timestamp"].dt.date == roll_date)
        ]["close"].iloc[-1]

        adjustment = old_close - new_close
        print(f"\nAdjustment at {roll_date}: {adjustment:.2f} points")

        # Apply adjustment to all prices after the roll date
        mask = continuous_data["timestamp"].dt.date > roll_date
        for col in price_columns:
            continuous_data.loc[mask, col] += adjustment

    # Add metadata columns to track the source contract
    continuous_data["active_contract"] = continuous_data["contract_month"]

    # Sort and clean final dataset
    continuous_data = continuous_data.sort_values("timestamp")

    # Add roll date markers
    continuous_data["roll_date"] = continuous_data["timestamp"].dt.date.isin(
        [rd[0] for rd in roll_dates]
    )

    return continuous_data


def join_data_files():
    """
    Read and combine multiple contract files into a continuous contract
    """
    data_dir = Path("../../MES/")
    data_files = sorted(data_dir.glob("MES *.Last.txt"))
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

    print("\nCreating continuous contract with volume-based roll detection...")
    continuous_data = create_continuous_contract(all_data)

    # Save continuous data
    output_file = "../../MES/continuous_MES_volume_rolled.csv"
    continuous_data.to_csv(output_file, index=False)
    print(f"\nSaved continuous contract data to: {output_file}")

    # Print summary
    print("\nContinuous Contract Summary:")
    print(f"Total records: {len(continuous_data):,}")
    print(
        f"Date range: {continuous_data['timestamp'].min()} to {continuous_data['timestamp'].max()}"
    )
    print(f"Number of roll events: {continuous_data['roll_date'].sum()}")

    # Print roll dates summary
    roll_dates = continuous_data[continuous_data["roll_date"]].copy()
    if not roll_dates.empty:
        print("\nRoll Dates Summary:")
        for _, row in roll_dates.iterrows():
            print(f"  {row['timestamp'].date()}: {row['active_contract']}")

    return continuous_data


if __name__ == "__main__":
    joined_data = join_data_files()
