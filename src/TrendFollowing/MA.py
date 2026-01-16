import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'src')
from data_loader import DataLoader
from strategy import TrendFollowingStrategy, BuyAndHoldStrategy, TrendFollowingLongShortStrategy
from portfolio import Portfolio
from plot import plot_trend_following_curves
from backtest_runner import run_backtest_variant
import numpy as np

INITIAL_CAPITAL = 10_000
FEES = 0.001
SYMBOL = "ACWI"
START_DATE = "2008-01-01"
END_DATE = "2025-01-01"
ANNUAL_TARGET = 0.06  # 6%

def main_MA():
    # 1. Charger les données de prix
    loader = DataLoader(SYMBOL, START_DATE, END_DATE)
    loader.fetch_yfinance()
    close_prices = loader.get_close()  # pd.Series

    # 2. Définir les fenêtres de trend following
    tf_params_lists = [
        (10, 30),
        (25, 75),
        (50, 100),
        (75, 150),
        (100, 200)
    ]

    # 3. Boucle sur toutes les fenêtres de trend following

    curves_dict = {}
    stats_dict = {}

    for fast, long in tf_params_lists:
        # Long only variant
        label = f"long_only_{fast}_{long}"
        label, curve, stats = run_backtest_variant(
            strategy_class=TrendFollowingStrategy,
            close_prices=close_prices,
            label=label,
            initial_capital=INITIAL_CAPITAL,
            fees=FEES,
            strategy_params={"fast_window": fast, "slow_window": long}
        )
        curves_dict[label] = curve
        stats_dict[label] = stats

        # Long/short variant
        label = f"long_short_{fast}_{long}"
        label, curve, stats = run_backtest_variant(
            strategy_class=TrendFollowingLongShortStrategy,
            close_prices=close_prices,
            label=label,
            initial_capital=INITIAL_CAPITAL,
            fees=FEES,
            strategy_params={"fast_window": fast, "slow_window": long}
        )
        curves_dict[label] = curve
        stats_dict[label] = stats

    # 4 Construire le bench buy & hold

    strat_buy_and_hold = BuyAndHoldStrategy() 
    strat_buy_and_hold.generate_signals(close_prices) 
    signals_buy_and_hold = strat_buy_and_hold.signals

    pf_buy_and_hold = Portfolio(
        price_series=close_prices,
        signals=signals_buy_and_hold,
        init_cash=INITIAL_CAPITAL,
        fees=FEES
    )
    
    # Ajouter le bench aux dicts à plot

    curve_hold = pf_buy_and_hold.run_backtest()
    stats_hold = pf_buy_and_hold.get_stats()

    curves_dict["Buy&Hold_SPY"] = curve_hold
    stats_dict["Buy&Hold_SPY"] = stats_hold    # buy & hold SPY
    
    # 5. Construire 2e bench (6pct annuel)
    curve_6pct = pf_buy_and_hold.make_constant_growth_curve(
        annual_return=ANNUAL_TARGET,
        init_cash=INITIAL_CAPITAL
    )
    
    # On connaît les stats.. donc ajout manuel
    stats_6pct = {
        "Annualized return": ANNUAL_TARGET,
        "Sharpe ratio": float("nan"),
        "Max drawdown": float("nan")
    }

    curves_dict["Target_6%"] = curve_6pct
    stats_dict["Target_6%"] = stats_6pct

    # Tri alphabétique des dictionnaires
    curves_dict = dict(sorted(curves_dict.items(), key=lambda x: x[0].lower()))
    stats_dict = dict(sorted(stats_dict.items(), key=lambda x: x[0].lower()))

    # 5. On plot les courbes
    plot_trend_following_curves(curves_dict, stats_dict)


if __name__ == "__main__":
    main_MA()