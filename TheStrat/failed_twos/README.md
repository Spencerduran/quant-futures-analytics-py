# Failed 2's Analysis

This script analyzes the magnitude of price moves after a 2 fails and begins to "go - three"

- **2U**: When price makes a higher high and then moves below the opening price
- **2D**: When price makes a lower low and then moves above the opening price

## Features

- Analyzes moves in both absolute points and percentage terms
- Tracks success rates across multiple percentage tiers (25% to 200% in 25% increments)
- Validates data quality with comprehensive checks:
  - Price relationship validation (high > low, open/close within range)
  - Zero-range candle detection
  - Invalid price filtering
  - Missing data identification

## Output Format

The analysis generates detailed statistics for each pattern type:

1. **Absolute Move Metrics**:

   - Average move
   - Median move
   - Maximum move
   - Minimum move

2. **Percentage-Based Analysis**:
   - Move sizes as percentage of previous candle range
   - Success rates at different percentage tiers
   - Distribution of move magnitudes

## Methodology

The analysis focuses on two specific scenarios:

1. After making a higher high, how far price moves below the open
2. After making a lower low, how far price moves above the open

Moves are measured in both:

- Absolute points
- Percentage of the previous candle's range

For statistical relevance, the analysis excludes:

- Zero-range candles
- Invalid price data
- Moves that don't exceed the open price

```
MNQ Data Summary:
Records: 695,408
Date Range: 2022-12-18 06:01:00 to 2024-12-13 22:00:00
Resampled to 1,144 12h candles
Zero range candles: 42

=== MNQ Pattern Analysis ===

Pattern                   Total Count     Retrace %
--------------------------------------------------
Higher High Retracements  597
                          ≥25%              94.1%
                          ≥50%              81.9%
                          ≥75%              71.4%
                          ≥100%             45.1%
                          ≥125%             27.5%
                          ≥150%             19.3%
                          ≥175%             12.6%
                          ≥200%              8.2%

Lower Low Retracements    503
                          ≥25%              98.6%
                          ≥50%              88.5%
                          ≥75%              78.7%
                          ≥100%             53.5%
                          ≥125%             31.0%
                          ≥150%             18.9%
                          ≥175%             13.1%
                          ≥200%              8.3%


MES Data Summary:
Records: 708,409
Date Range: 2022-12-14 05:01:00 to 2024-12-16 05:00:00
Resampled to 1,160 12h candles
Zero range candles: 40

=== MES Pattern Analysis ===

Pattern                   Total Count     Retrace %
--------------------------------------------------
Higher High Retracements  600
                          ≥25%              95.5%
                          ≥50%              83.8%
                          ≥75%              70.0%
                          ≥100%             44.3%
                          ≥125%             27.2%
                          ≥150%             17.5%
                          ≥175%             11.8%
                          ≥200%              7.8%

Lower Low Retracements    510
                          ≥25%              98.6%
                          ≥50%              89.2%
                          ≥75%              77.3%
                          ≥100%             51.8%
                          ≥125%             29.8%
                          ≥150%             19.0%
                          ≥175%             13.3%
                          ≥200%              9.0%
```
