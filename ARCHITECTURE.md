# Architecture du Projet Backtest

# ===== DONE WITH AI ======

## 📁 Structure du Projet

```
src/
├── data_loader.py          # 📥 Chargement des données (Yahoo Finance, CSV)
├── strategy.py             # 🎯 Définition des stratégies de trading
├── portfolio.py            # 💼 Moteur de backtest (simulation)
├── plot.py                 # 📊 Visualisation des résultats
│
├── TrendFollowing/        # 📈 Scripts d'exécution pour stratégies trend-following
│   ├── MA.py              # Moving Average strategies
│   ├── CB.py              # Channel Breakout strategies
│   └── VolAjusted.py       # Volatility-adjusted strategies
│
└── MultiAsset/            # 🔄 Stratégies multi-actifs
    ├── multi_asset_strategy.py
    ├── portfolio_multi_asset.py
    └── runners.py
```

---

## 🔄 Flux d'Exécution Complet

### Exemple avec `MA.py` (Moving Average)

```
1. main_MA() est appelé
   │
   ├─► DataLoader.fetch_yfinance()
   │   └─► Télécharge les prix depuis Yahoo Finance
   │
   ├─► Pour chaque combinaison de paramètres (fast, slow):
   │   │
   │   ├─► run_trend_following_variant()
   │   │   │
   │   │   ├─► TrendFollowingStrategy(fast, slow)
   │   │   │   └─► strategy.generate_signals(price_series)
   │   │   │       └─► Calcule les moyennes mobiles
   │   │   │           └─► Retourne: signals (pd.Series)
   │   │   │
   │   │   ├─► Portfolio(price_series, signals, cash, fees)
   │   │   │   └─► Crée un objet portfolio
   │   │   │
   │   │   └─► portfolio.run_backtest()
   │   │       └─► Simule les trades jour par jour
   │   │           └─► Retourne: curve (pd.Series des valeurs)
   │   │
   │   └─► portfolio.get_stats()
   │       └─► Calcule Sharpe, return, drawdown, etc.
   │
   ├─► BuyAndHoldStrategy (benchmark)
   │   └─► Même processus
   │
   └─► plot_trend_following_curves(curves_dict, stats_dict)
       └─► Affiche tous les graphiques
```

---

## 📦 Rôle de Chaque Fichier

### 1. `data_loader.py` - Chargement des Données
**Rôle** : Récupérer les données de prix depuis Yahoo Finance ou CSV

**Fonctions principales** :
- `fetch_yfinance()` : Télécharge les données depuis Yahoo Finance
- `get_close()` : Retourne les prix de clôture (pd.Series)
- `get_open()` : Retourne les prix d'ouverture
- `get_daily_returns()` : Retourne les rendements quotidiens

**Utilisé par** : Tous les scripts `main_*()` dans `TrendFollowing/`

---

### 2. `strategy.py` - Définition des Stratégies
**Rôle** : Définir les différentes stratégies de trading

**Classes principales** :
- `Strategy` (classe abstraite) : Interface de base
- `TrendFollowingStrategy` : Suivi de tendance (long only)
- `TrendFollowingLongShortStrategy` : Suivi de tendance (long/short)
- `ChannelBreakoutLongOnlyStrategy` : Channel breakout (long only)
- `ChannelBreakoutLongShortStrategy` : Channel breakout (long/short)
- `MomentumStrengthLongOnlyStrategy` : Momentum ajusté volatilité (long only)
- `MomentumStrengthLongShortStrategy` : Momentum ajusté volatilité (long/short)
- `BuyAndHoldStrategy` : Stratégie buy & hold (benchmark)

**Méthode clé** :
```python
strategy.generate_signals(price_series)
# Retourne: pd.Series avec les signaux (-1, 0, 1 ou valeurs continues)
```

**Utilisé par** : Tous les scripts `run_*_variant()` dans `TrendFollowing/`

---

### 3. `portfolio.py` - Moteur de Backtest
**Rôle** : Simuler l'exécution des trades et calculer la performance

**Classe principale** : `Portfolio`

**Méthodes principales** :
- `run_backtest()` : 
  - Simule jour par jour les trades
  - Gère le cash, les positions, les frais
  - Retourne une courbe de valeur du portefeuille (pd.Series)
  
- `get_stats()` :
  - Calcule les statistiques de performance
  - Sharpe ratio, return annualisé, drawdown max, nombre de trades, etc.
  - Retourne un dictionnaire de stats

- `make_constant_growth_curve()` :
  - Crée une courbe de référence (ex: 6% par an)

**Utilisé par** : Tous les scripts `run_*_variant()` dans `TrendFollowing/`

---

### 4. `plot.py` - Visualisation
**Rôle** : Afficher les graphiques des résultats de backtest

**Fonction principale** :
- `plot_trend_following_curves(curves_dict, stats_dict, ...)` :
  - Prend un dictionnaire de courbes et de stats
  - Trace toutes les courbes sur un même graphique
  - Affiche les statistiques dans un encadré
  - Gère les couleurs, légendes, récessions, etc.

**Paramètres optionnels** :
- `figsize` : Taille de la figure
- `show_recessions` : Afficher les zones de récession (GFC, COVID)
- `initial_capital` : Capital initial pour le titre
- `show_trades` : Afficher le nombre de trades
- `save_path` : Chemin pour sauvegarder le graphique

**Appelé par** : Tous les scripts `main_*()` à la fin de leur exécution

---

### 5. Scripts `TrendFollowing/*.py` - Scripts d'Exécution

**Rôle** : Orchestrer l'exécution complète d'un type de stratégie

**Structure typique** :
```python
def main_MA():
    # 1. Charger les données
    loader = DataLoader(...)
    loader.fetch_yfinance()
    prices = loader.get_close()
    
    # 2. Définir les paramètres à tester
    params_list = [(10, 30), (25, 75), ...]
    
    # 3. Boucle sur les paramètres
    curves_dict = {}
    stats_dict = {}
    
    for params in params_list:
        # Créer stratégie → générer signaux → backtest → stats
        label, curve, stats = run_*_variant(prices, params, ...)
        curves_dict[label] = curve
        stats_dict[label] = stats
    
    # 4. Ajouter benchmarks (Buy&Hold, 6% target)
    
    # 5. Plotter les résultats
    plot_trend_following_curves(curves_dict, stats_dict)
```

**Fichiers** :
- `MA.py` : Teste les stratégies Moving Average
- `CB.py` : Teste les stratégies Channel Breakout
- `VolAjusted.py` : Teste les stratégies Volatility-adjusted

**Fonctions helper** :
- `run_trend_following_variant()` : Exécute une variante de stratégie
- `run_channel_breakout_*_variant()` : Exécute une variante CB
- `run_momentum_strength_*_variant()` : Exécute une variante momentum

---

## 🔍 Exemple Concret : Exécution de `MA.py`

```python
# 1. Vous lancez : python src/TrendFollowing/MA.py

# 2. Python exécute :
if __name__ == "__main__":
    main_MA()

# 3. main_MA() fait :
#    a) DataLoader("ACWI", "2008-01-01", "2025-01-01")
#       └─► Télécharge les prix ACWI depuis Yahoo Finance
#
#    b) Pour chaque (fast=10, slow=30), (fast=25, slow=75), etc. :
#       ├─► TrendFollowingStrategy(fast=10, slow=30)
#       ├─► strategy.generate_signals(prices)
#       │   └─► Calcule: fast_ma = prices.rolling(10).mean()
#       │       slow_ma = prices.rolling(30).mean()
#       │       signals = (fast_ma > slow_ma).astype(int)
#       │
#       ├─► Portfolio(prices, signals, cash=10000, fees=0.001)
#       ├─► portfolio.run_backtest()
#       │   └─► Simule jour par jour:
#       │       - Si signal change → trade
#       │       - Calcule cash, position, valeur totale
#       │       - Applique les frais
#       │       - Stocke la valeur à chaque jour
#       │
#       └─► portfolio.get_stats()
#           └─► Calcule: Sharpe, return, drawdown, nb trades, etc.
#
#    c) Crée Buy&Hold benchmark
#
#    d) plot_trend_following_curves(curves_dict, stats_dict)
#       └─► Affiche le graphique avec toutes les courbes
```

---

## 📊 Types de Données Échangés

### Entre les modules :

1. **DataLoader → Strategy** :
   - Input : `price_series` (pd.Series avec dates et prix)
   - Output : `signals` (pd.Series avec dates et signaux -1/0/1 ou continus)

2. **Strategy → Portfolio** :
   - Input : `price_series` + `signals`
   - Output : `results` (pd.Series avec dates et valeurs du portefeuille)

3. **Portfolio → Plot** :
   - Input : `curves_dict` (dict de pd.Series) + `stats_dict` (dict de dicts)
   - Output : Graphique matplotlib

---

## 🎯 Points Clés à Retenir

1. **Séparation des responsabilités** :
   - `data_loader.py` : Données
   - `strategy.py` : Logique de trading
   - `portfolio.py` : Simulation
   - `plot.py` : Visualisation

2. **Pattern d'exécution** :
   - Les scripts `main_*()` orchestrent tout
   - Ils appellent des fonctions `run_*_variant()` pour chaque paramètre
   - Ces fonctions créent Strategy → Portfolio → run_backtest() → get_stats()
   - Tout est collecté dans des dictionnaires
   - À la fin, `plot_trend_following_curves()` affiche tout

3. **Réutilisabilité** :
   - Les classes Strategy sont réutilisables
   - Portfolio peut être utilisé avec n'importe quelle stratégie
   - plot.py est utilisé par tous les scripts

4. **Flux de données** :
   ```
   Prix → Signaux → Positions → Valeur Portfolio → Stats → Graphique
   ```

---

## 🚀 Comment Lancer un Backtest

```bash
# Moving Average strategies
python src/TrendFollowing/MA.py

# Channel Breakout strategies
python src/TrendFollowing/CB.py

# Volatility-adjusted strategies
python src/TrendFollowing/VolAjusted.py
```

Chaque script :
1. Charge les données
2. Teste plusieurs variantes de stratégies
3. Calcule les benchmarks
4. Affiche un graphique comparatif

