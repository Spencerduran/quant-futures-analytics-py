from datetime import datetime

import numpy as np
import pandas as pd


class PatternAnalyzer:
    def __init__(self, df=None):
        """Initialize with optional DataFrame"""
        self.df = df
        self.pct_tiers = range(25, 225, 25)

    def validate_data(self) -> bool:
        """Validate the data before processing"""
        if self.df is None:
            return False

        print(f"\nColumns in dataframe: {self.df.columns.tolist()}")

        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        missing_columns = [
            col for col in required_columns if col not in self.df.columns
        ]
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return False

        price_columns = ["open", "high", "low", "close"]
        for col in price_columns:
            if (self.df[col] <= 0).any():
                print(f"Found invalid prices in {col}")
                return False

        if (self.df["high"] < self.df["low"]).any():
            print("Found high price less than low price")
            return False

        if (
            (self.df["open"] > self.df["high"]) | (self.df["open"] < self.df["low"])
        ).any():
            print("Found open price outside high-low range")
            return False

        if (
            (self.df["close"] > self.df["high"]) | (self.df["close"] < self.df["low"])
        ).any():
            print("Found close price outside high-low range")
            return False

        return True

    def prepare_data(self, filepath: str) -> bool:
        """Read and prepare the data from combined CSV file"""
        try:
            # Read the CSV file
            self.df = pd.read_csv(filepath)
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

            print(f"\nData Summary before resampling:")
            print(f"Records: {len(self.df):,}")
            print(
                f"Date Range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}"
            )

            # Resample to 12-hour candles
            resampled = (
                self.df.resample("12h", on="timestamp")
                .agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
                .dropna()
            )

            # Reset index to make timestamp a column again
            self.df = resampled.reset_index()

            # Calculate ranges for 12h candles
            self.df["candle_range"] = self.df["high"] - self.df["low"]
            zero_range_12h = self.df[self.df["candle_range"] == 0]

            print(f"\nResampled Data Analysis:")
            print(f"Records: {len(self.df):,}")
            print(
                f"Date Range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}"
            )
            print(f"Zero range 12h candles: {len(zero_range_12h)}")

            if len(zero_range_12h) > 0:
                print("\nZero range 12h candles:")
                print(
                    zero_range_12h[
                        ["timestamp", "open", "high", "low", "close", "volume"]
                    ].head()
                )

            return True

        except Exception as e:
            print(f"Error in prepare_data: {str(e)}")
            print("Detailed error information:")
            import traceback

            print(traceback.format_exc())
            return False

    def analyze_patterns(self) -> dict:
        """Analyze '3' patterns and their moves past the open"""
        results = {
            "high_then_below_open": {
                "count": 0,
                "moves": [],
                "move_percentages": [],
                "tier_hits": {pct: 0 for pct in self.pct_tiers},
                "skipped_zero_range": 0,
            },
            "low_then_above_open": {
                "count": 0,
                "moves": [],
                "move_percentages": [],
                "tier_hits": {pct: 0 for pct in self.pct_tiers},
                "skipped_zero_range": 0,
            },
        }

        for i in range(1, len(self.df) - 1):
            curr_candle = self.df.iloc[i]
            prev_candle = self.df.iloc[i - 1]

            # Skip if previous candle had zero range
            prev_candle_size = prev_candle["high"] - prev_candle["low"]
            if prev_candle_size == 0:
                continue

            # Made higher high and went below open
            if curr_candle["high"] > prev_candle["high"]:
                # Target would be previous low after making higher high
                target_distance = curr_candle["open"] - prev_candle["low"]
                points_below_open = curr_candle["open"] - curr_candle["low"]

                if (
                    points_below_open > 0 and target_distance > 0
                ):  # Only if it went below open and target is valid
                    move_pct = (points_below_open / target_distance) * 100
                    results["high_then_below_open"]["count"] += 1
                    results["high_then_below_open"]["moves"].append(points_below_open)
                    results["high_then_below_open"]["move_percentages"].append(move_pct)

                    for pct in self.pct_tiers:
                        if move_pct >= pct:
                            results["high_then_below_open"]["tier_hits"][pct] += 1

            # Made lower low and went above open
            if curr_candle["low"] < prev_candle["low"]:
                # Target would be previous high after making lower low
                target_distance = prev_candle["high"] - curr_candle["open"]
                points_above_open = curr_candle["high"] - curr_candle["open"]

                if (
                    points_above_open > 0 and target_distance > 0
                ):  # Only if it went above open and target is valid
                    move_pct = (points_above_open / target_distance) * 100
                    results["low_then_above_open"]["count"] += 1
                    results["low_then_above_open"]["moves"].append(points_above_open)
                    results["low_then_above_open"]["move_percentages"].append(move_pct)

                    for pct in self.pct_tiers:
                        if move_pct >= pct:
                            results["low_then_above_open"]["tier_hits"][pct] += 1

        return results

    def print_pattern_analysis(self, results: dict):
        """Print pattern analysis results"""
        patterns = {
            "high_then_below_open": "Made Higher High then moved below open",
            "low_then_above_open": "Made Lower Low then moved above open",
        }

        print("\n=== Pattern Analysis Results ===")
        for pattern, data in results.items():
            print(f"\n{patterns[pattern]}:")
            print(f"Total occurrences: {data['count']}")

            if data["count"] > 0:
                moves = data["moves"]
                move_pcts = data["move_percentages"]

                print(f"\nAbsolute Move Statistics:")
                print(f"Average move past open: {np.mean(moves):.2f} points")
                print(f"Median move past open: {np.median(moves):.2f} points")
                print(f"Max move past open: {np.max(moves):.2f} points")
                print(f"Min move past open: {np.min(moves):.2f} points")

                print(f"\nMove as Percentage of Previous Candle Size:")
                print(f"Average: {np.mean(move_pcts):.2f}%")
                print(f"Median: {np.median(move_pcts):.2f}%")
                print(f"Max: {np.max(move_pcts):.2f}%")
                print(f"Min: {np.min(move_pcts):.2f}%")

                print(f"\nPercentage Tier Statistics:")
                print("(How often the move exceeded each % of previous candle size)")
                print("-" * 60)
                for pct, count in data["tier_hits"].items():
                    success_rate = (count / data["count"]) * 100
                    print(
                        f"{pct:3d}% : {count:3d} times ({success_rate:6.2f}% of occurrences)"
                    )


def main():
    filepath = "../../data/MNQ/continuous_MNQ_volume_rolled.csv"

    # Initialize analyzer
    analyzer = PatternAnalyzer()

    # Prepare and validate data
    if not analyzer.prepare_data(filepath):
        print("Failed to prepare data")
        return

    if not analyzer.validate_data():
        print("Data validation failed")
        return

    # Analyze patterns
    results = analyzer.analyze_patterns()

    # Print results
    analyzer.print_pattern_analysis(results)


if __name__ == "__main__":
    main()
