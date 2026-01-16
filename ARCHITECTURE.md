# Backtest Project Architecture

## Project Structure

```
src/
├── data_loader.py          # Data loading (Yahoo Finance, CSV)
├── strategy.py             # Trading strategy definitions
├── portfolio.py            # Backtesting engine (simulation)
├── plot.py                 # Results visualization
│
├── TrendFollowing/         # Execution scripts for trend-following strategies
│   ├── MA.py               # Moving Average strategies
│   ├── CB.py               # Channel Breakout strategies
│   └── VolAjusted.py       # Volatility-adjusted strategies
│
└── MultiAsset/             # Multi-asset strategies
    ├── multi_asset_strategy.py
    ├── portfolio_multi_asset.py
    └── runners.py
```

---

## Complete Execution Flow

### Example with `MA.py` (Moving Average)

```
1. main_MA() is called
   │
   ├─► DataLoader.fetch_yfinance()
   │   └─► Downloads prices from Yahoo Finance
   │
   ├─► For each parameter combination (fast, slow):
   │   │
   │   ├─► run_trend_following_variant()
   │   │   │
   │   │   ├─► TrendFollowingStrategy(fast, slow)
   │   │   │   └─► strategy.generate_signals(price_series)
   │   │   │       └─► Computes moving averages
   │   │   │           └─► Returns: signals (pd.Series)
   │   │   │
   │   │   ├─► Portfolio(price_series, signals, cash, fees)
   │   │   │   └─► Creates a portfolio object
   │   │   │
   │   │   └─► portfolio.run_backtest()
   │   │       └─► Simulates trades day by day
   │   │           └─► Returns: curve (pd.Series of values)
   │   │
   │   └─► portfolio.get_stats()
   │       └─► Computes Sharpe, return, drawdown, etc.
   │
   ├─► BuyAndHoldStrategy (benchmark)
   │   └─► Same process
   │
   └─► plot_trend_following_curves(curves_dict, stats_dict)
       └─► Displays all charts

```

---

## Role of Each File

### 1. `data_loader.py` - Data loading
**Role**: Retrieve price data from Yahoo Finance or CSV

**Main functions:**
- `fetch_yfinance()` : Downloads data from Yahoo Finance
- `get_close()` : Returns closing prices (pd.Series)
- `get_open()` : Returns opening prices
- `get_daily_returns()` : Returns daily returns

`**Used by:** All `main_*()` scripts in ``TrendFollowing/`

---

### 2. `strategy.py` - Strategy Definitions
**Role**: Define the different trading strategies

**Main classes**:
- `Strategy` (abstract class): Base interface
- `TrendFollowingStrategy` : Trend following (long only)
- `TrendFollowingLongShortStrategy` : Trend following (long/short)
- `ChannelBreakoutLongOnlyStrategy` : Channel breakout (long only)
- `ChannelBreakoutLongShortStrategy` : Channel breakout (long/short)
- `MomentumStrengthLongOnlyStrategy` : Volatility-adjusted momentum (long only)
- `MomentumStrengthLongShortStrategy` : Volatility-adjusted momentum (long/short)
- `BuyAndHoldStrategy` : Buy & hold strategy (benchmark)

**Key method** :
```python
strategy.generate_signals(price_series)
# Returns: pd.Series with signals (-1, 0, 1 or continuous values)
```

**Used by** : All `run_*_variant()` scripts in `TrendFollowing/`

---

### 3. `portfolio.py` - Backtesting Engine
**Role** : Simulate trade execution and compute performance

**Main class** : `Portfolio`

**Main methods:** :
- `run_backtest()` : 
  -Simulates trades day by day
  - Manages cash, positions, and fees
  - Returns a portfolio value curve (pd.Series)
  
- `get_stats()` :
  - Computes performance statistics
  - Sharpe ratio, annualized return, max drawdown, number of trades, etc.
  - Returns a dictionary of statistics

- `make_constant_growth_curve()` :
  - Creates a reference curve (e.g. 6% per year)

**Used by:** : all `run_*_variant()` scripts in `TrendFollowing/`

---

### 4. `plot.py` - Visualization
**Role** : Display backtest result charts

**Main function:** :
- `plot_trend_following_curves(curves_dict, stats_dict, ...)` :
    - Takes a dictionary of curves and statistics
    - Plots all curves on the same chart
    - Displays statistics in a summary box
    - Handles colors, legends, recessions, etc.

**Optional parameters** :
- `figsize` : Figure size
- `show_recessions` : Display recession periods (GFC, COVID)
- `initial_capital` : Initial capital for the title
- `show_trades` : Display the number of trades
- `save_path` : Path to save the figure

**Called by** : all `main_*()` scripts at the end of execution

---

### 5. `TrendFollowing/*.py` Scripts – Execution Scripts

**Role** : Orchestrate the full execution of a given strategy type

**Typical Structure** :
```python
def main_MA():
    # 1. Load data
    loader = DataLoader(...)
    loader.fetch_yfinance()
    prices = loader.get_close()
    
    # 2. Define parameters to test
    params_list = [(10, 30), (25, 75), ...]
    
    # 3. Loop over parameters
    curves_dict = {}
    stats_dict = {}
    
    for params in params_list:
        # Create strategy → generate signals → backtest → stats
        label, curve, stats = run_*_variant(prices, params, ...)
        curves_dict[label] = curve
        stats_dict[label] = stats
    
    # 4. Add benchmarks (Buy & Hold, 6% target)
    
    # 5. Plot results
    plot_trend_following_curves(curves_dict, stats_dict)
```

**Files** :
- `MA.py` : Tests Moving Average strategies
- `CB.py` : Tests Channel Breakout strategies
- `VolAjusted.py` : Tests Volatility-adjusted strategies

**Functions helper** :
- `run_trend_following_variant()` : Executes a strategy variant
- `run_channel_breakout_*_variant()` : Executes a channel breakout variant
- `run_momentum_strength_*_variant()` : Executes a momentum variant

---

## Concrete Example: Executing `MA.py`

```python
# 1. You run: python src/TrendFollowing/MA.py

# 2. Python executes:
if __name__ == "__main__":
    main_MA()

# 3. main_MA() does:
#    a) DataLoader("ACWI", "2008-01-01", "2025-01-01")
#       └─► Downloads ACWI prices from Yahoo Finance
#
#    b) For each (fast=10, slow=30), (fast=25, slow=75), etc.:
#       ├─► TrendFollowingStrategy(fast=10, slow=30)
#       ├─► strategy.generate_signals(prices)
#       │   └─► Computes:
#       │       fast_ma = prices.rolling(10).mean()
#       │       slow_ma = prices.rolling(30).mean()
#       │       signals = (fast_ma > slow_ma).astype(int)
#       │
#       ├─► Portfolio(prices, signals, cash=10000, fees=0.001)
#       ├─► portfolio.run_backtest()
#       │   └─► Simulates day by day:
#       │       - If signal changes → trade
#       │       - Computes cash, position, total value
#       │       - Applies fees
#       │       - Stores daily portfolio value
#       │
#       └─► portfolio.get_stats()
#           └─► Computes: Sharpe, return, drawdown, number of trades, etc.
#
#    c) Creates Buy & Hold benchmark
#
#    d) plot_trend_following_curves(curves_dict, stats_dict)
#       └─► Displays the chart with all curves

```

---

## Data Types Exchanged

### Between modules:

1. **DataLoader → Strategy** :
   - Input : `price_series` (pd.Series)
   - Output : `signals` (pd.Series with dates and signals -1/0/1 or continuous)

2. **Strategy → Portfolio** :
   - Input : `price_series` + `signals`
   - Output : `results` (pd.Series with dates and portfolio values)

3. **Portfolio → Plot** :
   - Input : `curves_dict` (dict of pd.Series) + `stats_dict` (dict of dicts)
   - Output : matplotlib chart

---

## Key Takeaways

1. **Separation of responsibilities:** :
   - `data_loader.py` : Data
   - `strategy.py` : Trading logic
   - `portfolio.py` : Simulation
   - `plot.py` : Vizualisation

2. **Execution pattern:** :
   -  `main_*()` scripts orchestrate everything
   - They call`run_*_variant()` functions for each parameter set
   - These functions create Strategy → Portfolio → run_backtest() → get_stats()
   - Everything is collected into dictionaries
   - Finally, `plot_trend_following_curves()` displays the results

3. **Reusability** :
   - Strategy classes are reusable
   - Portfolio can be used with any strategy
   - plot.py is used by all scripts

4. **Data flow** :
   ```
   Prices → Signals → Positions → Portfolio Value → Stats → Chart
   ```

---

## How to Run a Backtest

```bash
# Moving Average strategies
python src/TrendFollowing/MA.py

# Channel Breakout strategies
python src/TrendFollowing/CB.py

# Volatility-adjusted strategies
python src/TrendFollowing/VolAjusted.py
```

Each script:
1. Loads data
2. Tests multiple strategy variants
3. Computes benchmarks
4. Displays a comparative chart
