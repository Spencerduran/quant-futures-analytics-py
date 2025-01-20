from datetime import datetime

import numpy as np
import pandas as pd


class PatternAnalyzer:
    def __init__(self, df=None):
        """Initialize with optional DataFrame"""
        self.df = df
        self.pct_tiers = range(25, 225, 25)
        self.instrument_name = None

    def validate_data(self) -> bool:
        """Validate the data before processing"""
        if self.df is None:
            return False

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

    def prepare_data(self, filepath: str, instrument_name: str) -> bool:
        """Read and prepare the data from combined CSV file"""
        try:
            self.instrument_name = instrument_name
            # Read the CSV file
            self.df = pd.read_csv(filepath)
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

            print(f"\n{instrument_name} Data Summary:")
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

            print(f"Resampled to {len(self.df):,} 12h candles")
            print(f"Zero range candles: {len(zero_range_12h)}")

            return True

        except Exception as e:
            print(f"Error in prepare_data: {str(e)}")
            return False

    def analyze_patterns(self) -> dict:
        """Analyze retracements after making higher highs/lower lows"""
        results = {
            "high_then_below_open": {
                "count": 0,
                "tier_hits": {pct: 0 for pct in self.pct_tiers},
            },
            "low_then_above_open": {
                "count": 0,
                "tier_hits": {pct: 0 for pct in self.pct_tiers},
            },
        }

        for i in range(1, len(self.df) - 1):
            curr_candle = self.df.iloc[i]
            prev_candle = self.df.iloc[i - 1]

            # Skip if previous candle had zero range
            prev_range = prev_candle["high"] - prev_candle["low"]
            if prev_range == 0:
                continue

            # Made higher high then retraced
            if curr_candle["high"] > prev_candle["high"]:
                curr_low = curr_candle["low"]
                possible_retrace = curr_candle["high"] - prev_candle["low"]
                actual_retrace = curr_candle["high"] - curr_low

                if possible_retrace > 0:
                    retrace_pct = (actual_retrace / possible_retrace) * 100
                    results["high_then_below_open"]["count"] += 1

                    for pct in self.pct_tiers:
                        if retrace_pct >= pct:
                            results["high_then_below_open"]["tier_hits"][pct] += 1

            # Made lower low then retraced
            if curr_candle["low"] < prev_candle["low"]:
                curr_high = curr_candle["high"]
                possible_retrace = prev_candle["high"] - curr_candle["low"]
                actual_retrace = curr_high - curr_candle["low"]

                if possible_retrace > 0:
                    retrace_pct = (actual_retrace / possible_retrace) * 100
                    results["low_then_above_open"]["count"] += 1

                    for pct in self.pct_tiers:
                        if retrace_pct >= pct:
                            results["low_then_above_open"]["tier_hits"][pct] += 1

        return results

    def print_pattern_analysis(self, results: dict):
        """Print pattern analysis results"""
        patterns = {
            "high_then_below_open": "Higher High Retracements",
            "low_then_above_open": "Lower Low Retracements",
        }

        print(f"\n=== {self.instrument_name} Pattern Analysis ===")

        # Header
        print("\n{:<25} {:<15} {:<10}".format("Pattern", "Total Count", "Retrace %"))
        print("-" * 50)

        for pattern, data in results.items():
            pattern_name = patterns[pattern]
            total_count = data["count"]

            # Print first line with pattern name and total count
            print("{:<25} {:<15}".format(pattern_name, total_count))

            # Print percentage tiers
            for pct in self.pct_tiers:
                count = data["tier_hits"][pct]
                success_rate = (count / total_count * 100) if total_count > 0 else 0
                print("{:<25} {:<15} {:>6.1f}%".format("", f"≥{pct}%", success_rate))
            print("")


def main():
    filepaths = {
        "MNQ": "../../data/MNQ/continuous_MNQ_volume_rolled.csv",
        "MES": "../../data/MES/continuous_MES_volume_rolled.csv",
    }

    for instrument, filepath in filepaths.items():
        # Initialize analyzer
        analyzer = PatternAnalyzer()

        # Prepare and validate data
        if not analyzer.prepare_data(filepath, instrument):
            print(f"Failed to prepare data for {instrument}")
            continue

        if not analyzer.validate_data():
            print(f"Data validation failed for {instrument}")
            continue

        # Analyze patterns
        results = analyzer.analyze_patterns()

        # Print results
        analyzer.print_pattern_analysis(results)


if __name__ == "__main__":
    main()
