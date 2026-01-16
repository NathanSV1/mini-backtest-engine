"""
Module utilitaire pour exécuter des backtests de manière générique.
Élimine la duplication de code entre les différents scripts de stratégies.
"""

import pandas as pd
from typing import Type, Dict, Any, Tuple
from strategy import Strategy
from portfolio import Portfolio


def run_backtest_variant(
    strategy_class: Type[Strategy],
    close_prices: pd.Series,
    label: str,
    initial_capital: float,
    fees: float,
    strategy_params: Dict[str, Any] = None
) -> Tuple[str, pd.Series, Dict[str, Any]]:
    """
    Fonction générique pour exécuter un backtest avec n'importe quelle stratégie.
    
    Cette fonction remplace toutes les fonctions run_*_variant() dupliquées
    dans MA.py, CB.py, VolAjusted.py, etc.
    
    Parameters
    ----------
    strategy_class : Type[Strategy]
        La classe de stratégie à utiliser (ex: TrendFollowingStrategy)
    close_prices : pd.Series
        Série de prix de clôture
    label : str
        Label pour identifier cette variante
    initial_capital : float
        Capital initial pour le backtest
    fees : float
        Frais de transaction (ex: 0.001 = 0.1%)
    strategy_params : dict, optional
        Paramètres à passer au constructeur de la stratégie
        (ex: {"fast_window": 50, "slow_window": 200})
    
    Returns
    -------
    tuple : (label, curve, stats)
        - label : str - Le label de la stratégie
        - curve : pd.Series - Courbe de valeur du portefeuille
        - stats : dict - Statistiques de performance
    
    Examples
    --------
    >>> from strategy import TrendFollowingStrategy
    >>> label, curve, stats = run_backtest_variant(
    ...     strategy_class=TrendFollowingStrategy,
    ...     close_prices=prices,
    ...     label="long_only_50_200",
    ...     initial_capital=10_000,
    ...     fees=0.001,
    ...     strategy_params={"fast_window": 50, "slow_window": 200}
    ... )
    """
    if strategy_params is None:
        strategy_params = {}
    
    # 1. Créer la stratégie avec les paramètres donnés
    strat = strategy_class(**strategy_params)
    
    # 2. Générer les signaux
    strat.generate_signals(close_prices)
    signals = strat.signals
    
    # 3. Créer le portfolio et exécuter le backtest
    pf = Portfolio(
        price_series=close_prices,
        signals=signals,
        init_cash=initial_capital,
        fees=fees
    )
    
    # 4. Exécuter le backtest
    curve = pf.run_backtest()
    
    # 5. Calculer les statistiques
    stats = pf.get_stats()
    
    return label, curve, stats

