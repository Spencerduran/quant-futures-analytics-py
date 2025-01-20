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
