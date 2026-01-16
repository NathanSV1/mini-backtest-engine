import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, 'src')

from data_loader import DataLoader
from strategy import BuyAndHoldStrategy, MomentumStrengthLongOnlyStrategy, MomentumStrengthLongShortStrategy
from portfolio import Portfolio
from plot import plot_trend_following_curves
from backtest_runner import run_backtest_variant
import numpy as np
import pandas as pd

INITIAL_CAPITAL = 10_000
FEES = 0.001
EQUITY_SYMBOL = "ACWI"
FI_SYMBOL = "AGG"
START_DATE = "2000-01-01"
END_DATE = "2025-01-01" 
ANNUAL_TARGET = 0.06  # 6%


def main_VolAjusted():
    # 1. Charger les données de prix
    loader = DataLoader(EQUITY_SYMBOL, START_DATE, END_DATE)
    loader.fetch_yfinance()
    close_prices = loader.get_close()  # pd.Series

    # 2. Définir les paramètres (lookback, vol_window) pour les stratégies momentum strength
    params_lists = [
        (25, 25),
        (50, 50),
        (75, 75),
        (100, 100),
        (50, 25),
        (100, 50)
    ]

    # Initialiser les dicts
    curves_dict = {}
    stats_dict = {}
    # 3 ===== LONG ONLY =====
    # Boucle sur toutes les combinaisons de paramètres
    for lookback, vol_window in params_lists:
        # Long only variant
        label = f"long_only_{lookback}_{vol_window}"
        label, curve, stats = run_backtest_variant(
            strategy_class=MomentumStrengthLongOnlyStrategy,
            close_prices=close_prices,
            label=label,
            initial_capital=INITIAL_CAPITAL,
            fees=FEES,
            strategy_params={"lookback": lookback, "vol_window": vol_window}
        )
        curves_dict[label] = curve
        stats_dict[label] = stats

    # 3.bis ===== LONG SHORT =====
    for lookback, vol_window in params_lists:
        # Long/short variant
        label = f"long_short_{lookback}_{vol_window}"
        label, curve, stats = run_backtest_variant(
            strategy_class=MomentumStrengthLongShortStrategy,
            close_prices=close_prices,
            label=label,
            initial_capital=INITIAL_CAPITAL,
            fees=FEES,
            strategy_params={"lookback": lookback, "vol_window": vol_window}
        )
        curves_dict[label] = curve
        stats_dict[label] = stats


    # Tri alphabétique des dictionnaires
    curves_dict = dict(sorted(curves_dict.items(), key=lambda x: x[0].lower()))
    stats_dict = dict(sorted(stats_dict.items(), key=lambda x: x[0].lower()))
    # 5. On plot les courbes
    plot_trend_following_curves(curves_dict, stats_dict)





if __name__ == "__main__":
    main_VolAjusted()