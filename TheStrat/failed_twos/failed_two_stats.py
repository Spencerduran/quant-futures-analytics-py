from datetime import datetime

import numpy as np
import pandas as pd


class PatternAnalyzer:
    def __init__(self, df=None):
        """Initialize with optional DataFrame"""
        self.df = df
        self.pct_tiers = range(25, 225, 25)
        self.instrument_name = None
        self.timeframes = {
            "12h": "12h",
            "4h": "4h",
            "60min": "60min",
            "30min": "30min",
            "15min": "15min",
        }

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
            print(f"Original Records: {len(self.df):,}")
            print(
                f"Date Range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}"
            )

            return True

        except Exception as e:
            print(f"Error in prepare_data: {str(e)}")
            return False

    def resample_data(self, timeframe: str) -> pd.DataFrame:
        """Resample data to specified timeframe"""
        resampled = (
            self.df.resample(timeframe, on="timestamp")
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

        return resampled.reset_index()

    def analyze_patterns(self, df: pd.DataFrame) -> dict:
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

        for i in range(1, len(df) - 1):
            curr_candle = df.iloc[i]
            prev_candle = df.iloc[i - 1]

            # Skip if previous candle had zero range
            prev_range = prev_candle["high"] - prev_candle["low"]
            if prev_range == 0:
                continue

            # Made higher high then retraced
            if curr_candle["high"] > prev_candle["high"]:
                curr_low = curr_candle["low"]
                possible_retrace = curr_candle["open"] - prev_candle["low"]
                actual_retrace = curr_candle["open"] - curr_low

                if possible_retrace > 0:
                    retrace_pct = (actual_retrace / possible_retrace) * 100
                    results["high_then_below_open"]["count"] += 1

                    for pct in self.pct_tiers:
                        if retrace_pct >= pct:
                            results["high_then_below_open"]["tier_hits"][pct] += 1

            # Made lower low then retraced
            if curr_candle["low"] < prev_candle["low"]:
                curr_high = curr_candle["high"]
                possible_retrace = prev_candle["high"] - curr_candle["open"]
                actual_retrace = curr_high - curr_candle["open"]

                if possible_retrace > 0:
                    retrace_pct = (actual_retrace / possible_retrace) * 100
                    results["low_then_above_open"]["count"] += 1

                    for pct in self.pct_tiers:
                        if retrace_pct >= pct:
                            results["low_then_above_open"]["tier_hits"][pct] += 1

        return results

    def print_timeframe_analysis(self, all_results: dict):
        """Print analysis results in table format with colors"""
        # ANSI color codes
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        print(f"\n{BOLD}=== {self.instrument_name} Pattern Analysis ==={RESET}")

        # Print 2U -> 3D results
        print(f"\n{BOLD}2U -> 3D {RESET}")
        self._print_pattern_table("high_then_below_open", all_results)

        # Print 2D - 3U results
        print(f"\n{BOLD}2D - 3U {RESET}")
        self._print_pattern_table("low_then_above_open", all_results)

    def _print_pattern_table(self, pattern: str, all_results: dict):
        """Helper method to print pattern-specific table"""
        # ANSI color codes
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        # Print header
        print(f"\n{BOLD}{'Timeframe':<10} {'Count':<8}", end="")
        for pct in self.pct_tiers:
            print(f" {f'≥{pct}%':<7}", end="")
        print(f"{RESET}")
        print("-" * (10 + 8 + 7 * len(self.pct_tiers)))

        # Print data for each timeframe
        for tf in self.timeframes:
            results = all_results[tf]
            count = results[pattern]["count"]
            print(f"{tf:<10} {count:<8}", end="")

            for pct in self.pct_tiers:
                if count > 0:
                    success_rate = (results[pattern]["tier_hits"][pct] / count) * 100
                    # Color code based on success rate
                    if success_rate >= 50:
                        color = GREEN
                    elif success_rate >= 40:
                        color = YELLOW
                    else:
                        color = RED
                    print(f" {color}{success_rate:>6.1f}{RESET}", end="")
                else:
                    print(f" {'-':>6}", end="")
            print()


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

        # Analyze each timeframe
        all_results = {}
        for tf in analyzer.timeframes:
            # Resample data to current timeframe
            resampled_df = analyzer.resample_data(analyzer.timeframes[tf])
            # Analyze patterns
            all_results[tf] = analyzer.analyze_patterns(resampled_df)

        # Print results
        analyzer.print_timeframe_analysis(all_results)


if __name__ == "__main__":
    main()
