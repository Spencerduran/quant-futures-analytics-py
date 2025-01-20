# Quantitative Futures Analytics (Python)

## SSS50 Percent Rule Analysis

`quant-futures-analytics-py/TheStrat/sss50_percent_stats/README.md`

This script analyzes SSS50 retrace patterns in futures market data, specifically focusing on two key patterns:

- **2U Pattern**: When a candle makes a higher high than the previous candle
- **2D Pattern**: When a candle makes a lower low than the previous candle
  The analysis considers a pattern successful if:

- For 2U: Price reaches the previous candle's low
- For 2D: Price reaches the previous candle's high

Success is measured across three timeframes:

1. Within the same candle
2. Within the next 2 candles
3. Within the next 3 candles

## Failed 2's Analysis

`quant-futures-analytics-py/TheStrat/failed_twos/failed_two_stats.py`

This script analyzes the magnitude of price moves after a 2 fails and begins to "go - three"

- **2U**: When price makes a higher high and then moves below the opening price
- **2D**: When price makes a lower low and then moves above the opening price
- Analyzes moves in both absolute points and percentage terms
- Tracks success rates across multiple percentage tiers (25% to 200% in 25% increments)
