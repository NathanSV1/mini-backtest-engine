import pandas as pd
from abc import ABC, abstractmethod
import numpy as np
import yfinance as yf
from data_loader import DataLoader

class Strategy(ABC):
    def __init__(self, name: str, params: dict):
        self.name :str = name
        self.params : dict = params
        self.signals : pd.Series = None

    @abstractmethod
    def generate_signals(self, price_series: pd.Series):
        """ À implémenter dans les classes filles """
        pass

# === Sous-classes ===

class TrendFollowingStrategy(Strategy):
    def __init__(self, fast_window :int = 50, slow_window :int = 200):
        super().__init__("TrendFollowingStrategy", {"fast_window": fast_window, "slow_window": slow_window})

    def generate_signals(self, price_series: pd.Series)-> None:
        """ Générer les signaux de la stratégie de suivi de tendance """
        # Force Series type
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]
        
        fast_ma = price_series.rolling(window=self.params["fast_window"]).mean()
        slow_ma = price_series.rolling(window=self.params["slow_window"]).mean()

        # 1 si fast_ma > slow_ma, sinon 0
        self.signals = (fast_ma > slow_ma).astype(int)

class TrendFollowingLongShortStrategy(Strategy):
    """Trend-following strategy with long/short signals (+1 / -1)."""

    def __init__(self, fast_window: int = 50, slow_window: int = 200):
        super().__init__(
            name="TrendFollowingLongShort",
            params={"fast_window": fast_window, "slow_window": slow_window}
        )

    def generate_signals(self, price_series: pd.Series) -> pd.Series:
        """Generate signals: +1 for long, -1 for short, 0 for neutral."""

        # Force a 1D Series
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]

        # Ensure DatetimeIndex
        price_series.index = pd.to_datetime(price_series.index)

        # Moving averages
        fast_ma = price_series.rolling(window=self.params["fast_window"]).mean()
        slow_ma = price_series.rolling(window=self.params["slow_window"]).mean()

        # Signals: +1 (long) if fast > slow, -1 (short) if fast < slow
        signals = np.where(fast_ma > slow_ma, 1, -1)

        # Convert to pandas Series and align with prices
        self.signals = pd.Series(signals, index=price_series.index, name="signal")

        # Optional: neutralize NaN zones (beginning of series)
        self.signals = self.signals.fillna(0)

        return self.signals

class BuyAndHoldStrategy(Strategy):
    def __init__(self):
        super().__init__("BuyAndHold", {})

    def generate_signals(self, price_series):
        self.signals = pd.Series(1, index=price_series.index)
        return self.signals

class ChannelBreakoutLongOnlyStrategy(Strategy):
    def __init__(self, window: int = 20):
        super().__init__("ChannelBreakoutLongOnly", {"window": window})

    def generate_signals(self, price_series: pd.Series) -> pd.Series:
        """Generate signals: +1 for long, -1 for short, 0 for neutral.
        
        VECTORIZED VERSION: Uses pandas operations instead of Python loop.
        ~10-100x faster than loop-based implementation.
        """
        N = self.params["window"]

        # Force a 1D Series
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]
        
        # Rolling channel bounds
        rolling_high = price_series.rolling(window=N, min_periods=1).max().shift(1)
        rolling_low  = price_series.rolling(window=N, min_periods=1).min().shift(1)

        # Signal rules
        long_signal = price_series >= rolling_high
        exit_signal = price_series < rolling_low

        # VECTORIZED: Use pandas operations instead of loop
        # Create state change indicators
        state_changes = pd.Series(0, index=price_series.index, dtype=int)
        state_changes[long_signal] = 1   # Enter long position
        state_changes[exit_signal] = -1  # Exit position (go to cash)
        
        # Use cumulative sum to track position state
        # When we enter (1), cumulative sum increases to 1
        # When we exit (-1), cumulative sum decreases to 0
        # Clip to ensure we stay in [0, 1] range
        signals = state_changes.cumsum().clip(0, 1).astype(int)
        
        self.signals = pd.Series(signals, index=price_series.index, name="Signal")
        return self.signals

class ChannelBreakoutLongShortStrategy(Strategy):
    def __init__(self, window: int = 20):
        super().__init__("ChannelBreakoutLongShort", {"window": window})

    def generate_signals(self, price_series: pd.Series) -> pd.Series:
        """Generate signals: +1 for long, -1 for short, 0 for neutral.
        
        VECTORIZED VERSION: Uses pandas operations instead of Python loop.
        ~10-100x faster than loop-based implementation.
        """
        N = self.params["window"]

        # Force a 1D Series
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]
        
        # Rolling channel bounds
        rolling_high = price_series.rolling(window=N, min_periods=1).max().shift(1)
        rolling_low  = price_series.rolling(window=N, min_periods=1).min().shift(1)

        # Signal rules
        long_signal = price_series >= rolling_high
        short_signal = price_series < rolling_low

        # VECTORIZED: Use pandas operations instead of loop
        # Create a Series that marks signal changes (1 for long, -1 for short)
        # Priority: long_signal takes precedence if both occur on same day
        signal_changes = pd.Series(0, index=price_series.index, dtype=int)
        signal_changes[long_signal] = 1   # Enter long position
        signal_changes[short_signal & ~long_signal] = -1  # Enter short (only if not long)
        
        # Forward fill to maintain position state until next signal change
        # Replace 0 (no change) with NaN, then forward fill
        signal_changes = signal_changes.replace(0, np.nan)
        signals = signal_changes.ffill().fillna(0).astype(int)
        
        self.signals = pd.Series(signals, index=price_series.index, name="Signal")
        return self.signals

class MomentumStrengthLongShortStrategy(Strategy):
    """
    Volatility-adjusted momentum (Long/Short)
    ----------------------------------------
    Signal s_t = tanh((r_t / sigma_t)), continuous in [-1, 1].
    Exposure scales linearly with trend strength and direction.

    Parameters
    ----------
    lookback : int
        Period for momentum calculation (e.g. 50)
    vol_window : int
        Window for rolling volatility (e.g. 50)
    """

    def __init__(self, lookback: int = 50, vol_window: int = 50):
        super().__init__("MomentumStrength_LongShort", {"lookback": lookback, "vol_window": vol_window})

    def generate_signals(self, price_series: pd.Series) -> pd.Series:
        # Force Series type
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]

        L = self.params["lookback"]
        V = self.params["vol_window"]
        
        # Rolling momentum raw
        returns = price_series.pct_change(L)
        # Rolling volatility
        vol = returns.rolling(window=V).std()
        vol.replace(0, np.nan, inplace=True)

        # Momentum strength
        raw_signal = returns / vol
        # Normalize to [-1, 1]
        normalized_signal = np.tanh(raw_signal)
        # Convert to Series with same index
        self.signals = pd.Series(normalized_signal, index=price_series.index, name="Signal")
        return self.signals

class MomentumStrengthLongOnlyStrategy(Strategy):
    """
    Volatility-adjusted momentum (Long Only)
    ----------------------------------------
    Signal s_t = tanh((r_t / sigma_t)), clipped to [0, 1].
    Exposure scales with momentum intensity; negative signals are set to 0.

    Parameters
    ----------
    lookback : int
        Period for momentum calculation (e.g. 50)
    vol_window : int
        Window for rolling volatility (e.g. 50)
    """

    def __init__(self, lookback: int = 50, vol_window: int = 50):
        super().__init__("MomentumStrength_LongOnly", {"lookback": lookback, "vol_window": vol_window})

    def generate_signals(self, price_series: pd.Series) -> pd.Series:
        # Force Series type
        if isinstance(price_series, pd.DataFrame):
            price_series = price_series.iloc[:, 0]

        L = self.params["lookback"]
        V = self.params["vol_window"]

        # Rolling momentum
        returns = price_series.pct_change(L)

        # Rolling volatility
        vol = returns.rolling(V).std()
        vol.replace(0, np.nan, inplace=True)

        # Scaled momentum
        raw_signal = returns / vol
        scaled_signal = np.tanh(raw_signal)

        # Long-only: no short exposure
        scaled_signal = np.clip(scaled_signal, 0, 1)

        self.signals = pd.Series(scaled_signal, index=price_series.index, name="Signal")
        return self.signals

if __name__ == "__main__":
    dataload = DataLoader("AAPL", "2020-01-01", "2021-01-01")
    dataload.fetch_yfinance()
    price = dataload.get_close()
    strat = MomentumStrengthLongShortStrategy()
    strat.generate_signals(price)
    print(strat.signals.head())
    print(strat.signals.tail())
    print(strat.signals.describe())
    print(strat.signals.info())
    print(strat.signals.shape)
    print(strat.signals.index)
    print(strat.signals.values)

