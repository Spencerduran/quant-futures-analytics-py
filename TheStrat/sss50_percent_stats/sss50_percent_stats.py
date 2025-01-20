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

    def print_analysis(self, results: dict, instrument: str):
        """Store results for comparative table"""
        # Convert results into row format for later tabulation
        data = []
        for pattern_type in ["higher_high_retrace", "lower_low_retrace"]:
            pattern_data = results[pattern_type]
            targets = pattern_data["reached_target"]
            total = pattern_data["total_patterns"]

            if total > 0:
                data.append(
                    {
                        "instrument": instrument,
                        "pattern": "2U"
                        if pattern_type == "higher_high_retrace"
                        else "2D",
                        "total": total,
                        "same_count": targets["same_candle"],
                        "same_pct": (targets["same_candle"] / total * 100),
                        "two_count": targets["within_2"],
                        "two_pct": (targets["within_2"] / total * 100),
                        "three_count": targets["within_3"],
                        "three_pct": (targets["within_3"] / total * 100),
                        "never_count": targets["never"],
                        "never_pct": (targets["never"] / total * 100),
                        "cum_two_count": targets["same_candle"] + targets["within_2"],
                        "cum_two_pct": (
                            (targets["same_candle"] + targets["within_2"]) / total * 100
                        ),
                        "cum_three_count": targets["same_candle"]
                        + targets["within_2"]
                        + targets["within_3"],
                        "cum_three_pct": (
                            (
                                targets["same_candle"]
                                + targets["within_2"]
                                + targets["within_3"]
                            )
                            / total
                            * 100
                        ),
                    }
                )

        return data


def print_comparative_table(all_results):
    """Print a comparative table of all results"""
    print("\n=== Comparative Analysis ===")
    print(
        "┌──────┬────┬───────┬────────────────┬────────────────┬────────────────┬────────────────┬─────────────────┬─────────────────┐"
    )
    print(
        "│ Inst │ Pat│ Total │  Same Candle   │   Within 2     │   Within 3     │     Never      │    Cum 2 bars   │    Cum 3 bars   │"
    )
    print(
        "├──────┼────┼───────┼────────────────┼────────────────┼────────────────┼────────────────┼─────────────────┼─────────────────┤"
    )

    for row in all_results:
        print(
            f"│ {row['instrument']:<4} │ {row['pattern']:<2} │ {row['total']:>5} │ "
            f"{row['same_count']:>5} {row['same_pct']:>6.1f}% │ "
            f"{row['two_count']:>5} {row['two_pct']:>6.1f}% │ "
            f"{row['three_count']:>5} {row['three_pct']:>6.1f}% │ "
            f"{row['never_count']:>5} {row['never_pct']:>6.1f}% │ "
            f"{row['cum_two_count']:>6} {row['cum_two_pct']:>6.1f}% │ "
            f"{row['cum_three_count']:>6} {row['cum_three_pct']:>6.1f}% │"
        )

    print(
        "└──────┴────┴───────┴────────────────┴────────────────┴────────────────┴────────────────┴─────────────────┴─────────────────┘"
    )


def analyze_instrument(filepath: str, instrument: str):
    """Analyze a single instrument"""
    analyzer = RetracementFollowAnalyzer()

    if not analyzer.prepare_data(filepath):
        print(f"Failed to prepare data for {instrument}")
        return

    results = analyzer.analyze_follow_through()
    analyzer.print_analysis(results, instrument)


def main():
    # Analyze both MNQ and MES
    instruments = {
        "MNQ": "../../data/MNQ/continuous_MNQ_volume_rolled.csv",
        "MES": "../../data/MES/continuous_MES_volume_rolled.csv",
    }

    all_results = []

    for instrument, filepath in instruments.items():
        try:
            analyzer = RetracementFollowAnalyzer()
            if analyzer.prepare_data(filepath):
                results = analyzer.analyze_follow_through()
                all_results.extend(analyzer.print_analysis(results, instrument))
        except Exception as e:
            print(f"Error analyzing {instrument}: {str(e)}")
            import traceback

            print(traceback.format_exc())

    # Print comparative table of all results
    print_comparative_table(all_results)


if __name__ == "__main__":
    main()
