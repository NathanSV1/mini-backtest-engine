import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd





# ====== DONE WITH AI, that is actually better than me to plot great graphs =======

# This function is called at the end of the backtest to plot the curves and the stats (those have been computed in the backtest)

# Takes in argument 
# - curves_dict: a dictionary of curves
# - stats_dict: a dictionary of stats

def plot_trend_following_curves(curves_dict, stats_dict, 
                                 figsize=(21, 7),
                                 show_recessions=True,
                                 initial_capital=None,
                                 show_trades=True,
                                 text_position=(0.20, 0.8),
                                 title_suffix="",
                                 save_path=None):
    """
    Fonction consolidée pour tracer les courbes de backtest.
    
    Parameters
    ----------
    curves_dict : dict
        Dictionnaire {label: pd.Series} des courbes à tracer
    stats_dict : dict
        Dictionnaire {label: dict} des statistiques pour chaque courbe
    figsize : tuple, default=(21, 7)
        Taille de la figure (width, height)
    show_recessions : bool, default=True
        Afficher les zones de récession (GFC, COVID)
    initial_capital : float, optional
        Capital initial pour le titre. Si None, extrait de la première courbe
    show_trades : bool, default=True
        Afficher le nombre de trades dans le résumé
    text_position : tuple, default=(0.20, 0.8)
        Position (x, y) du texte de résumé (en coordonnées axes)
    title_suffix : str, default=""
        Suffixe à ajouter au titre
    save_path : str, optional
        Chemin pour sauvegarder la figure. Si None, n'enregistre pas
    """
    # === Tri alphabétique des dictionnaires ===
    plt.figure(figsize=figsize)

    # === Préparer les sous-groupes de labels ===
    long_only_labels = [label for label in curves_dict if "long_only" in label.lower()]
    long_short_labels = [label for label in curves_dict if "long_short" in label.lower()]

    n_long = len(long_only_labels)
    n_short = len(long_short_labels)

    # === Dégradés simples ===
    cmap_long = cm.Greens(np.linspace(0.4, 0.8, max(1, n_long)))   # verts doux
    cmap_short = cm.Blues(np.linspace(0.4, 0.8, max(1, n_short)))  # bleus doux

    # === Boucle principale ===
    for label, series in curves_dict.items():
        label_lower = label.lower()

        # Couleurs fixes
        if "buy&hold" in label_lower:
            color = "black"
        elif "target" in label_lower:
            color = "red"
        elif "long_only" in label_lower:
            color = cmap_long[long_only_labels.index(label)]
        elif "long_short" in label_lower:
            color = cmap_short[long_short_labels.index(label)]
        else:
            color = "grey"  # fallback

        # Tracé propre et uniforme
        plt.plot(
            series.index, series.values,
            linewidth=1.0,
            label=label,
            color=color
        )

    # === Mise en forme du graphe ===
    ax = plt.gca()
    
    # Afficher les récessions si demandé
    if show_recessions:
        # GFC (NBER recession)
        ax.axvspan(pd.Timestamp("2007-12-01"), pd.Timestamp("2009-06-30"),
                color="orange", alpha=0.12, zorder=0)
        # COVID (NBER recession)
        ax.axvspan(pd.Timestamp("2020-02-01"), pd.Timestamp("2020-04-30"),
                color="purple", alpha=0.12, zorder=0)
        y_top = ax.get_ylim()[1]
        ax.text(pd.Timestamp("2008-09-01"), y_top*0.98, "GFC 2007–2009 (NBER)", color="orange", fontsize=9)
        ax.text(pd.Timestamp("2020-03-01"), y_top*0.94, "COVID 2020 (NBER)", color="purple", fontsize=9)

    # Titre avec capital initial
    if initial_capital is None:
        initial_capital = next(iter(curves_dict.values())).iloc[0] if curves_dict else 10000
    
    title = f"Portfolio Value Over Time{title_suffix} (Start ${initial_capital:,.0f})"
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Value ($)")
    plt.grid(True, alpha=0.3)
    plt.legend(
        fontsize=8,
        loc="center left",      # à gauche du centre vertical
        bbox_to_anchor=(1.02, 0.5),  # décalage à droite de la figure
        )

    # === Encadré résumé ===
    final_lines = []
    for label, series in curves_dict.items():
        if stats_dict and label in stats_dict:
            ann_ret = stats_dict[label].get("Annualized return", float("nan"))
            sharpe = stats_dict[label].get("Sharpe ratio", float("nan"))
            trade_info = ""
            if show_trades and "Number of trades" in stats_dict[label]:
                trade_info = f"  | Number of trades: {stats_dict[label]['Number of trades']}"
            final_lines.append(
                f"{label}: {ann_ret*100:,.2f}%  |  Sharpe: {sharpe:,.2f}{trade_info}"
            )
        else:
            final_lines.append(f"{label}: ${series.iloc[-1]:,.0f}")

    boxtext = "\n".join(final_lines)
    ax = plt.gca()
    ax.text(
        text_position[0], text_position[1], boxtext,
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # laisse de la place à droite
    plt.suptitle(
        "Figure 1 — Trend-following strategies : long only vs long short vs Buy & Hold (2000–2025)",
        y=-0.15, fontsize=15, style='italic'
    )
    
    if save_path:
        plt.savefig(save_path)
    
    plt.show()