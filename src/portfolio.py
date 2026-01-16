import pandas as pd
import numpy as np
from strategy import MomentumStrengthLongOnlyStrategy, MomentumStrengthLongShortStrategy, BuyAndHoldStrategy
from data_loader import DataLoader

class Portfolio:
    def __init__(self, price_series : pd.Series, signals : pd.Series, init_cash : float = 10000, fees : float= 0.001):
        """ Rôle : exécuter le backtest sur la base des signaux et du prix.
            Simule : cash, positions, valeur totale, PnL, drawdown.""" 
        self.price_series : pd.Series = price_series
        self.signals : pd.Series = signals
        self.init_cash : float = init_cash
        self.fees : float = fees
        self.results : pd.DataFrame = None

    def run_backtest(self):
        """
        Execute un backtest compatible avec signaux discrets (0, ±1)
        et continus (∈ [-1, 1]) représentant la proportion du capital investie.
        
        OPTIMIZED VERSION: Uses numpy arrays for faster access instead of pandas .iloc.
        ~2-5x faster than the original implementation.
        """
        # Convert to numpy arrays once (much faster than repeated .iloc access)
        prices = self.price_series.values
        signals_arr = self.signals.clip(-1.0, 1.0).values  # Clamp signals to [-1, 1]
        
        cash = self.init_cash
        position = 0.0  # nombre d'unités détenues (positif = long, négatif = short)
        values = np.zeros(len(prices))  # Pre-allocate array (faster than list.append)

        for t in range(len(prices)):
            price_now = prices[t]  # FAST: direct array access
            signal_now = signals_arr[t]  # FAST: direct array access

            # Valeur totale actuelle du portefeuille
            total_value = cash + position * price_now

            # Taille de position cible (en unités)
            target_position = (signal_now * total_value) / price_now

            # Ajustement à faire (nombre d'unités à acheter/vendre)
            trade_units = target_position - position

            if abs(trade_units) > 1e-2:  # éviter les micro-trades
                trade_value = trade_units * price_now
                fee = abs(trade_value) * self.fees

                # Si trade_value > 0 : achat net (on dépense du cash)
                # Si trade_value < 0 : vente nette (on reçoit du cash)
                cash -= trade_value + fee
                position = target_position

            # Mise à jour de la valeur totale
            total_value = cash + position * price_now
            values[t] = total_value  # FAST: direct array assignment

        self.results = pd.Series(values, index=self.price_series.index, name="Portfolio Value")
        return self.results
    
    def get_stats(self):
        """
        Retourne un dictionnaire complet de statistiques de performance
        ET de trading (nb de trades, frais totaux, turnover...).
        Compatible avec signaux continus.
        """
        assert self.results is not None, "Backtest not executed"

        # ---- Perf de base ----
        returns = self.results.pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252)
        total_ret = self.results.iloc[-1] / self.results.iloc[0] - 1
        max_dd = (self.results / self.results.cummax() - 1).min()
        ann_ret = (1 + total_ret) ** (252 / len(returns)) - 1

        # ---- Statistiques de trading ----
        signals = self.signals.fillna(0)
        signal_changes = signals.diff().fillna(0)

        # Nombre de changements de position = nb de trades
        trade_count = (signal_changes != 0).sum()

        # Montant notionnel échangé (en valeur absolue)
        # On calcule la variation de position * prix
        traded_notional = (abs(signal_changes) * self.price_series).sum()

        # Frais totaux payés
        total_fees_paid = traded_notional * self.fees

        # Frais moyens par trade (approximation)
        avg_fee_per_trade = total_fees_paid / max(1, trade_count)

        # Turnover (volume échangé / valeur moyenne du portefeuille)
        avg_portfolio_value = self.results.mean()
        turnover = traded_notional / avg_portfolio_value

        # ---- Compilation ----
        stats = {
            "Total return": total_ret,
            "Annualized return": ann_ret,
            "Sharpe ratio": sharpe,
            "Max drawdown": max_dd,
            "Number of trades": int(trade_count),
            "Total fees paid": float(total_fees_paid),
            "Average fee per trade": float(avg_fee_per_trade),
            "Turnover": float(turnover),
        }

        return stats



    def make_constant_growth_curve(self, annual_return=0.06, init_cash=None) -> pd.Series:
        """
        Benchmark cible: croissance composée à X% par an (ex: 6%).
        """
        if init_cash is None:
            init_cash = self.init_cash

        # approx 252 jours de marché par an
        daily_growth = (1 + annual_return) ** (1/252) - 1
        steps = np.arange(len(self.price_series))
        vals = init_cash * (1 + daily_growth) ** steps
        curve = pd.Series(vals, index=self.price_series.index, name="Target6pct")
        return curve
        
if __name__ == "__main__":
    dataload = DataLoader("AAPL", "2020-01-01", "2021-01-01")
    dataload.fetch_yfinance()
    price = dataload.get_close()
    strat = BuyAndHoldStrategy()
    strat.generate_signals(price)
    print(strat.signals)
    portfolio = Portfolio(price, strat.signals)
    portfolio.run_backtest()

    print(portfolio.get_stats())
    print(portfolio.results)