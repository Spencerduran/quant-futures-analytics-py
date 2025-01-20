from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class RetracementFollowAnalyzer:
    def __init__(self, df=None):
        self.df = df

    def prepare_data(self, filepath: str) -> bool:
        """Read and prepare the data"""
        try:
            self.df = pd.read_csv(filepath)
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

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

            self.df = resampled.reset_index()
            return True

        except Exception as e:
            print(f"Error in prepare_data: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return False

    def analyze_follow_through(self) -> dict:
        """Analyze what happens after 50% retracements"""
        results = {
            "higher_high_retrace": {
                "total_patterns": 0,
                "reached_target": {
                    "same_candle": 0,
                    "within_2": 0,
                    "within_3": 0,
                    "never": 0,
                },
                "timestamps": [],  # For debugging
            },
            "lower_low_retrace": {
                "total_patterns": 0,
                "reached_target": {
                    "same_candle": 0,
                    "within_2": 0,
                    "within_3": 0,
                    "never": 0,
                },
                "timestamps": [],  # For debugging
            },
        }

        # We need to look ahead up to 3 candles, so stop 3 candles before the end
        for i in range(1, len(self.df) - 3):
            curr_candle = self.df.iloc[i]
            prev_candle = self.df.iloc[i - 1]

            prev_range = prev_candle["high"] - prev_candle["low"]
            if prev_range == 0:  # Skip zero-range previous candles
                continue

            # Higher High Pattern with 50% retrace
            if curr_candle["high"] > prev_candle["high"]:
                # Calculate retracement
                retrace = curr_candle["high"] - curr_candle["low"]
                retrace_pct = (retrace / prev_range) * 100

                if retrace_pct >= 50:  # Only analyze candles with 50%+ retrace
                    results["higher_high_retrace"]["total_patterns"] += 1
                    results["higher_high_retrace"]["timestamps"].append(
                        curr_candle["timestamp"]
                    )

                    # Check if it hit previous low in same candle
                    if curr_candle["low"] <= prev_candle["low"]:
                        results["higher_high_retrace"]["reached_target"][
                            "same_candle"
                        ] += 1
                        continue

                    # Look ahead up to 2 candles
                    next_two_lows = min(self.df.iloc[i + 1 : i + 3]["low"])
                    if next_two_lows <= prev_candle["low"]:
                        results["higher_high_retrace"]["reached_target"][
                            "within_2"
                        ] += 1
                        continue

                    # Look ahead to 3rd candle
                    next_three_lows = min(self.df.iloc[i + 1 : i + 4]["low"])
                    if next_three_lows <= prev_candle["low"]:
                        results["higher_high_retrace"]["reached_target"][
                            "within_3"
                        ] += 1
                    else:
                        results["higher_high_retrace"]["reached_target"]["never"] += 1

            # Lower Low Pattern with 50% retrace
            if curr_candle["low"] < prev_candle["low"]:
                # Calculate retracement from the low
                retrace = curr_candle["high"] - curr_candle["low"]
                retrace_pct = (retrace / prev_range) * 100

                if retrace_pct >= 50:  # Only analyze candles with 50%+ retrace
                    results["lower_low_retrace"]["total_patterns"] += 1
                    results["lower_low_retrace"]["timestamps"].append(
                        curr_candle["timestamp"]
                    )

                    # Check if it hit previous high in same candle
                    if curr_candle["high"] >= prev_candle["high"]:
                        results["lower_low_retrace"]["reached_target"][
                            "same_candle"
                        ] += 1
                        continue

                    # Look ahead up to 2 candles
                    next_two_highs = max(self.df.iloc[i + 1 : i + 3]["high"])
                    if next_two_highs >= prev_candle["high"]:
                        results["lower_low_retrace"]["reached_target"]["within_2"] += 1
                        continue

                    # Look ahead to 3rd candle
                    next_three_highs = max(self.df.iloc[i + 1 : i + 4]["high"])
                    if next_three_highs >= prev_candle["high"]:
                        results["lower_low_retrace"]["reached_target"]["within_3"] += 1
                    else:
                        results["lower_low_retrace"]["reached_target"]["never"] += 1

        return results

    def print_analysis(self, results: dict):
        """Print forward-looking analysis results"""
        patterns = {
            "higher_high_retrace": "After Higher High + 50% Retrace",
            "lower_low_retrace": "After Lower Low + 50% Retrace",
        }

        print("\n=== Forward-Looking Analysis Results ===")
        for pattern, data in results.items():
            print(f"\n{patterns[pattern]}:")
            print(f"Total qualifying patterns: {data['total_patterns']}")

            if data["total_patterns"] > 0:
                targets = data["reached_target"]
                total = data["total_patterns"]

                print("\nTarget Reached:")
                print(
                    f"Same candle  : {targets['same_candle']:3d} times ({(targets['same_candle']/total*100):6.2f}%)"
                )
                print(
                    f"Within 2 bars: {targets['within_2']:3d} times ({(targets['within_2']/total*100):6.2f}%)"
                )
                print(
                    f"Within 3 bars: {targets['within_3']:3d} times ({(targets['within_3']/total*100):6.2f}%)"
                )
                print(
                    f"Never reached: {targets['never']:3d} times ({(targets['never']/total*100):6.2f}%)"
                )

                # Print cumulative stats
                cumulative_2 = targets["same_candle"] + targets["within_2"]
                cumulative_3 = cumulative_2 + targets["within_3"]
                print(f"\nCumulative Success Rates:")
                print(
                    f"By 2 bars: {cumulative_2:3d} times ({(cumulative_2/total*100):6.2f}%)"
                )
                print(
                    f"By 3 bars: {cumulative_3:3d} times ({(cumulative_3/total*100):6.2f}%)"
                )


def main():
    filepath = "../data/MNQ/combined_MNQ_2023_2024.csv"

    analyzer = RetracementFollowAnalyzer()

    if not analyzer.prepare_data(filepath):
        print("Failed to prepare data")
        return

    results = analyzer.analyze_follow_through()
    analyzer.print_analysis(results)


if __name__ == "__main__":
    main()
