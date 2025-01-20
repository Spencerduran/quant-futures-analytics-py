# Failed 2's Analysis

```
MNQ Data Summary:
Original Records: 695,408
Date Range: 2022-12-18 06:01:00 to 2024-12-13 22:00:00

=== MNQ Pattern Analysis ===

2U -> 3D

Timeframe  Count    ≥25%    ≥50%    ≥75%    ≥100%   ≥125%   ≥150%   ≥175%   ≥200%
--------------------------------------------------------------------------
12h        596        72.0   60.6   54.0   45.0   39.6   34.9   30.7   27.9
4h         1588       69.1   51.7   38.5   31.5   25.9   22.6   19.5   16.5
60min      5876       70.3   48.8   34.6   25.8   20.5   16.8   13.7   11.7
30min      11390      68.6   46.5   32.3   23.5   17.8   14.1   11.3    9.5
15min      22411      68.5   46.0   30.9   21.7   16.2   12.7   10.0    8.3

2D - 3U

Timeframe  Count    ≥25%    ≥50%    ≥75%    ≥100%   ≥125%   ≥150%   ≥175%   ≥200%
--------------------------------------------------------------------------
12h        503        77.5   68.4   59.0   53.5   47.7   42.9   39.8   35.0
4h         1367       75.0   56.7   45.5   36.5   30.4   24.4   21.2   18.7
60min      5246       72.8   51.8   37.1   28.7   22.8   18.9   15.9   13.8
30min      10426      71.0   49.9   34.6   25.2   19.5   15.9   12.9   11.0
15min      20771      71.9   49.3   33.4   23.6   17.3   13.7   10.6    9.1

MES Data Summary:
Original Records: 708,409
Date Range: 2022-12-14 05:01:00 to 2024-12-16 05:00:00

=== MES Pattern Analysis ===

2U -> 3D

Timeframe  Count    ≥25%    ≥50%    ≥75%    ≥100%   ≥125%   ≥150%   ≥175%   ≥200%
--------------------------------------------------------------------------
12h        598        73.9   61.5   52.0   44.1   39.0   33.1   27.9   24.6
4h         1598       69.2   52.6   39.4   31.7   25.6   21.5   18.5   15.6
60min      5825       70.6   50.2   35.2   26.4   19.9   16.2   12.9   11.5
30min      11146      69.6   47.8   32.9   24.7   17.3   13.7   10.6    9.2
15min      21301      69.5   47.6   31.5   23.7   15.4   12.3    9.5    8.3

2D - 3U

Timeframe  Count    ≥25%    ≥50%    ≥75%    ≥100%   ≥125%   ≥150%   ≥175%   ≥200%
--------------------------------------------------------------------------
12h        509        78.0   66.6   58.9   51.7   46.2   40.5   35.4   32.6
4h         1399       76.1   58.0   45.1   36.1   28.8   24.4   20.3   18.9
60min      5210       73.8   53.1   38.0   29.2   21.9   18.1   14.4   12.7
30min      10213      71.9   51.3   35.7   27.1   18.9   15.1   12.0   10.5
15min      19790      72.3   50.7   33.6   25.5   16.1   12.8    9.7    8.6
```

## Summary

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

1. **Percentage-Based Analysis**:
   - Move sizes as percentage of remainint previous candle retracement range
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
