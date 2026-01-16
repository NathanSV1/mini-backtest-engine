# Backtest Engine

Un moteur de backtest simple et efficace pour tester des stratégies de trading algorithmique.

## Fonctionnalités

- **Stratégies multiples** : Moving Average, Channel Breakout, Momentum (volatility-adjusted)
- **Moteur de backtest optimisé** : Utilise numpy pour des performances optimales
- **Visualisation** : Graphiques comparatifs avec statistiques de performance
- **Architecture modulaire** : Facile à étendre avec de nouvelles stratégies

## Installation

```bash
# Cloner le repository
git clone https://github.com/NathanSV1/mini-backtest-engine.git
cd backtest0

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Exemple basique

```python
from data_loader import DataLoader
from strategy import TrendFollowingStrategy
from portfolio import Portfolio
from backtest_runner import run_backtest_variant

# Charger les données
loader = DataLoader("SPY", "2020-01-01", "2024-01-01")
loader.fetch_yfinance()
prices = loader.get_close()

# Exécuter un backtest
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

### Scripts d'exécution

```bash
# Test des stratégies Moving Average
python src/TrendFollowing/MA.py

# Test des stratégies Channel Breakout
python src/TrendFollowing/CB.py

# Test des stratégies Volatility-adjusted
python src/TrendFollowing/VolAjusted.py
```

## Structure du Projet

```
src/
├── data_loader.py          # Chargement des données (Yahoo Finance)
├── strategy.py             # Définition des stratégies de trading
├── portfolio.py            # Moteur de backtest
├── backtest_runner.py      # Fonction utilitaire pour exécuter des backtests
├── plot.py                 # Visualisation des résultats
└── TrendFollowing/
    ├── MA.py              # Scripts d'exécution pour Moving Average
    ├── CB.py              # Scripts d'exécution pour Channel Breakout
    └── VolAjusted.py      # Scripts d'exécution pour Momentum
```

Pour plus de détails sur l'architecture, voir [ARCHITECTURE.md](ARCHITECTURE.md).

## Stratégies Disponibles

- **TrendFollowingStrategy** : Suivi de tendance avec moyennes mobiles (long only)
- **TrendFollowingLongShortStrategy** : Suivi de tendance (long/short)
- **ChannelBreakoutLongOnlyStrategy** : Channel breakout (long only)
- **ChannelBreakoutLongShortStrategy** : Channel breakout (long/short)
- **MomentumStrengthLongOnlyStrategy** : Momentum ajusté volatilité (long only)
- **MomentumStrengthLongShortStrategy** : Momentum ajusté volatilité (long/short)
- **BuyAndHoldStrategy** : Stratégie buy & hold (benchmark)

## 🔧 Dépendances

- `pandas` : Manipulation de données
- `numpy` : Calculs numériques
- `yfinance` : Téléchargement de données financières
- `matplotlib` : Visualisation

##  Statistiques Calculées

- Total return
- Annualized return
- Sharpe ratio
- Max drawdown
- Number of trades
- Total fees paid
- Turnover

## Optimisations

- **Vectorisation** : Les stratégies utilisent des opérations pandas/numpy vectorisées
- **Numpy arrays** : Le moteur de backtest utilise numpy pour des performances optimales
- **Code DRY** : Fonctions génériques pour éviter la duplication

## Notes

Ce projet est un outil éducatif pour comprendre les backtests de stratégies de trend following. Les résultats ne constituent pas des conseils financiers.

