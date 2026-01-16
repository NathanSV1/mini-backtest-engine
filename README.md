# Backtest Engine

A simple and efficient backtesting engine for testing algorithmic trading strategies.

## Features

- **Multiple strategies**: Moving Average, Channel Breakout, Momentum (volatility-adjusted)
- **Optimized backtesting engine**: Uses NumPy for optimal performance
- **Visualization**: Comparative charts with performance statistics
- **Modular architecture**: Easy to extend with new strategies

## Installation

```bash
# Clone the repository
git clone https://github.com/NathanSV1/mini-backtest-engine.git
cd mini-backtest-engine

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic example

```python
from data_loader import DataLoader
from strategy import TrendFollowingStrategy
from portfolio import Portfolio
from backtest_runner import run_backtest_variant

# Load data
loader = DataLoader("SPY", "2020-01-01", "2024-01-01")
loader.fetch_yfinance()
prices = loader.get_close()

# Run a backtest
label, curve, stats = run_backtest_variant(
    strategy_class=TrendFollowingStrategy,
    close_prices=prices,
    label="MA_50_200",
    initial_capital=10_000,
    fees=0.001,
    strategy_params={"fast_window": 50, "slow_window": 200}
)

print(stats)
```

### Execution scripts

```bash
# Test Moving Average strategies
python src/TrendFollowing/MA.py

# Test Channel Breakout strategies
python src/TrendFollowing/CB.py

# Test Volatility-adjusted strategies
python src/TrendFollowing/VolAjusted.py

```

## Project Structure

```
src/
├── data_loader.py          # Data loading (Yahoo Finance)
├── strategy.py             # Trading strategy definitions
├── portfolio.py            # Backtesting engine
├── backtest_runner.py      # Utility function to run backtests
├── plot.py                 # Results visualization
└── TrendFollowing/
    ├── MA.py               # Execution scripts for Moving Average
    ├── CB.py               # Execution scripts for Channel Breakout
    └── VolAjusted.py       # Execution scripts for Momentum
```

For more details on the architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Available Strategies
- **TrendFollowingStrategy**: Trend following with moving averages (long only)
- **TrendFollowingLongShortStrategy**: Trend following (long/short)
- **ChannelBreakoutLongOnlyStrategy**: Channel breakout (long only)
- **ChannelBreakoutLongShortStrategy**: Channel breakout (long/short)
- **MomentumStrengthLongOnlyStrategy**: Volatility-adjusted momentum (long only)
- **MomentumStrengthLongShortStrategy**: Volatility-adjusted momentum (long/short)
- **BuyAndHoldStrategy**: Buy & hold strategy (benchmark)

## Dependencies

- `pandas` : Data manipulation
- `numpy` : Numerical computations
- `yfinance` : Financial data download
- `matplotlib` : Visualization

## Computed Statistics

- Total return
- Annualized return
- Sharpe ratio
- Max drawdown
- Number of trades
- Total fees paid
- Turnover

## Optimizations

- **Vectorization** : Strategies use vectorized pandas/NumPy operations
- **NumPy arrays** : The backtesting engine relies on NumPy for performance
- **DRY code** : Generic functions to avoid code duplication

## Notes

This project is an educational tool designed to understand backtesting of trend-following strategies.
Results do not constitute financial advice.

