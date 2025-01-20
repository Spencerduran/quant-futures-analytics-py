from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class RetracementFollowAnalyzer:
    def __init__(self, df=None):
        self.df = df

    def prepare_data(self, filepath: str, timeframe: str = "12h") -> bool:
        """Read and prepare the data"""
        try:
            self.df = pd.read_csv(filepath)
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])

            # Resample to specified timeframe
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

            self.df = resampled.reset_index()
            return True

        except Exception as e:
            print(f"Error in prepare_data: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return False

    def analyze_follow_through(self) -> dict:
        """Analyze full moves to previous candle's opposite extreme when 50%+ retraced"""
        results = {
            "higher_high_retrace": {
                "total_patterns": 0,
                "gap_patterns": 0,
                "reached_target": {
                    "same_candle": 0,
                    "within_2": 0,
                    "within_3": 0,
                    "never": 0,
                },
                "timestamps": [],
            },
            "lower_low_retrace": {
                "total_patterns": 0,
                "gap_patterns": 0,
                "reached_target": {
                    "same_candle": 0,
                    "within_2": 0,
                    "within_3": 0,
                    "never": 0,
                },
                "timestamps": [],
            },
        }

        for i in range(1, len(self.df) - 3):
            curr_candle = self.df.iloc[i]
            prev_candle = self.df.iloc[i - 1]

            prev_range = prev_candle["high"] - prev_candle["low"]
            if prev_range == 0:  # Skip zero-range previous candles
                continue

            # Higher High Pattern (2U)
            is_2u = False
            gap_retrace = False

            # Check for regular higher high or gap up
            if curr_candle["high"] > prev_candle["high"]:
                is_2u = True
            elif curr_candle["open"] > prev_candle["high"]:
                # If gap up and open is already 50% retraced from prev high to prev low
                open_retrace = (
                    (prev_candle["high"] - curr_candle["open"]) / prev_range * 100
                )
                if open_retrace >= 50:
                    is_2u = True
                    gap_retrace = True
                    results["higher_high_retrace"]["gap_patterns"] += 1

            if is_2u:
                retrace = prev_candle["high"] - curr_candle["low"]
                retrace_pct = (retrace / prev_range) * 100

                if (
                    retrace_pct >= 50 or gap_retrace
                ):  # Include if 50%+ retrace or gap already retraced
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

            # Lower Low Pattern (2D)
            is_2d = False
            gap_retrace = False

            # Check for regular lower low or gap down
            if curr_candle["low"] < prev_candle["low"]:
                is_2d = True
            elif curr_candle["open"] < prev_candle["low"]:
                # If gap down and open is already 50% retraced from prev low to prev high
                open_retrace = (
                    (curr_candle["open"] - prev_candle["low"]) / prev_range * 100
                )
                if open_retrace >= 50:
                    is_2d = True
                    gap_retrace = True
                    results["lower_low_retrace"]["gap_patterns"] += 1

            if is_2d:
                # For 2D: measure from previous low
                retrace = curr_candle["high"] - prev_candle["low"]
                retrace_pct = (retrace / prev_range) * 100

                if (
                    retrace_pct >= 50 or gap_retrace
                ):  # Include if 50%+ retrace or gap already retraced
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

    def print_analysis(self, results: dict, instrument: str, timeframe: str):
        """Store results for comparative table, including gap statistics"""
        data = []
        for pattern_type in ["higher_high_retrace", "lower_low_retrace"]:
            pattern_data = results[pattern_type]
            targets = pattern_data["reached_target"]
            total = pattern_data["total_patterns"]
            gaps = pattern_data["gap_patterns"]

            if total > 0:
                data.append(
                    {
                        "timeframe": timeframe,
                        "instrument": instrument,
                        "pattern": "2U"
                        if pattern_type == "higher_high_retrace"
                        else "2D",
                        "total": total,
                        "gaps": gaps,
                        "gaps_pct": (gaps / total * 100) if total > 0 else 0,
                        "same_count": targets["same_candle"],
                        "same_pct": (targets["same_candle"] / total * 100)
                        if total > 0
                        else 0,
                        "two_count": targets["within_2"],
                        "two_pct": (targets["within_2"] / total * 100)
                        if total > 0
                        else 0,
                        "three_count": targets["within_3"],
                        "three_pct": (targets["within_3"] / total * 100)
                        if total > 0
                        else 0,
                        "never_count": targets["never"],
                        "never_pct": (targets["never"] / total * 100)
                        if total > 0
                        else 0,
                        "cum_two_count": targets["same_candle"] + targets["within_2"],
                        "cum_two_pct": (
                            (targets["same_candle"] + targets["within_2"]) / total * 100
                        )
                        if total > 0
                        else 0,
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
                        )
                        if total > 0
                        else 0,
                    }
                )

        return data


def print_comparative_table(all_results):
    """Print a comparative table of all results including gap statistics and timeframe"""
    print("\n=== Comparative Analysis ===")
    print(
        "┌──────┬────┬────┬───────┬────────────────┬────────────────┬────────────────┬────────────────┬────────────────┬─────────────────┬─────────────────┐"
    )
    print(
        "│ Inst │ TF │ Pat│ Total │     Gaps       │  Same Candle   │   Within 2     │   Within 3     │     Never      │    Cum 2 bars   │    Cum 3 bars   │"
    )
    print(
        "├──────┼────┼────┼───────┼────────────────┼────────────────┼────────────────┼────────────────┼────────────────┼─────────────────┼─────────────────┤"
    )

    for row in all_results:
        print(
            f"│ {row['instrument']:<4} │ {row['timeframe']:<2} │ {row['pattern']:<2} │ {row['total']:>5} │ "
            f"{row['gaps']:>5} {row['gaps_pct']:>6.1f}% │ "
            f"{row['same_count']:>5} {row['same_pct']:>6.1f}% │ "
            f"{row['two_count']:>5} {row['two_pct']:>6.1f}% │ "
            f"{row['three_count']:>5} {row['three_pct']:>6.1f}% │ "
            f"{row['never_count']:>5} {row['never_pct']:>6.1f}% │ "
            f"{row['cum_two_count']:>6} {row['cum_two_pct']:>6.1f}% │ "
            f"{row['cum_three_count']:>6} {row['cum_three_pct']:>6.1f}% │"
        )

    print(
        "└──────┴────┴────┴───────┴────────────────┴────────────────┴────────────────┴────────────────┴────────────────┴─────────────────┴─────────────────┘"
    )


def analyze_instrument(filepath: str, instrument: str):
    """Analyze a single instrument"""
    analyzer = RetracementFollowAnalyzer()

    if not analyzer.prepare_data(filepath):
        print(f"Failed to prepare data for {instrument}")
        return

    results = analyzer.analyze_follow_through()
    analyzer.print_analysis(results, instrument)


def save_to_csv(all_timeframe_results):
    """Save all results to a CSV file"""
    output_data = []

    for timeframe, results in all_timeframe_results.items():
        for row in results:
            output_data.append(
                {
                    "timeframe": timeframe,
                    "instrument": row["instrument"],
                    "pattern": row["pattern"],
                    "total_patterns": row["total"],
                    "same_candle_count": row["same_count"],
                    "same_candle_pct": row["same_pct"],
                    "within_2_count": row["two_count"],
                    "within_2_pct": row["two_pct"],
                    "within_3_count": row["three_count"],
                    "within_3_pct": row["three_pct"],
                    "never_count": row["never_count"],
                    "never_pct": row["never_pct"],
                    "cum_2bars_count": row["cum_two_count"],
                    "cum_2bars_pct": row["cum_two_pct"],
                    "cum_3bars_count": row["cum_three_count"],
                    "cum_3bars_pct": row["cum_three_pct"],
                }
            )

    df = pd.DataFrame(output_data)
    df.to_csv("retracement_analysis_results.csv", index=False)
    print("\nResults saved to retracement_analysis_results.csv")


def main():
    timeframes = {
        "12H": "12h",
        "4H": "4h",
        "60min": "60min",
        "30min": "30min",
        "15min": "15min",
    }

    instruments = {
        "MNQ": "../../data/MNQ/continuous_MNQ_volume_rolled.csv",
        "MES": "../../data/MES/continuous_MES_volume_rolled.csv",
    }

    # Store all results for CSV export
    all_timeframe_results = {}

    # Analyze each instrument and timeframe combination
    for timeframe_name, timeframe in timeframes.items():
        print(f"\n\n=== Analysis for {timeframe_name} Timeframe ===")
        all_results = []

        for instrument, filepath in instruments.items():
            try:
                analyzer = RetracementFollowAnalyzer()
                if analyzer.prepare_data(filepath, timeframe):
                    results = analyzer.analyze_follow_through()
                    result_data = analyzer.print_analysis(
                        results, instrument, timeframe_name
                    )
                    all_results.extend(result_data)
            except Exception as e:
                print(f"Error analyzing {instrument}: {str(e)}")
                import traceback

                print(traceback.format_exc())

        if all_results:  # Only print if we have results
            # Print comparative table for this timeframe
            print_comparative_table(all_results)

        # Store results for this timeframe
        all_timeframe_results[timeframe_name] = all_results

    # Save all results to CSV
    save_to_csv(all_timeframe_results)


if __name__ == "__main__":
    main()
