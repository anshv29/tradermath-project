"""
This file turns test results into something you can actually see —
a full results dashboard with 4 different charts, plus a printed table.
Every game in the project uses this same code, so results look the
same way every time, no matter which game you're testing.
"""

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from core.harness import EvalResult


def print_comparison_table(results: List[EvalResult]) -> None:
    """Prints a clean table comparing strategies on the same game."""
    if not results:
        print("No results to report.")
        return

    game_name = results[0].game_name
    print(f"\n=== {game_name} — strategy comparison ({results[0].n_rounds} rounds) ===")
    header = f"{'Strategy':<25}{'Mean Payoff':>15}{'Std Dev':>12}{'Sharpe-like':>13}{'Max DD':>10}{'Win Rate':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        s = r.summary()
        print(f"{s['strategy']:<25}{s['mean_payoff']:>15}{s['std_payoff']:>12}"
              f"{s['sharpe_like']:>13}{s['max_drawdown']:>10}{s['win_rate']:>10}")


def _strategy_color(name: str) -> str:
    """Naive strategies show in grey, everything else (smart/optimal
    strategies) shows in orange, so it's easy to tell them apart at a glance."""
    return "#b0b0b0" if "naive" in name.lower() else "#d94f30"


def plot_dashboard(results: List[EvalResult], save_path: str = None) -> None:
    """
    Draws 4 charts together in one picture, comparing strategies:

    1. Bar chart      - the average result per strategy (quick glance)
    2. Line chart     - running total profit over time, per strategy
                        (shows the journey, not just the ending number)
    3. Histogram      - the full spread of results, so you can see if
                        a strategy hides big losses behind a good average
    4. Box plot       - a compact summary of the typical range and
                        any extreme outlier results
    """
    if not results:
        return

    game_name = results[0].game_name
    names = [r.strategy_name for r in results]
    colors = [_strategy_color(n) for n in names]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(f"{game_name} — Strategy Comparison ({results[0].n_rounds} rounds)", fontsize=14)

    # Chart 1: average payoff
    ax = axes[0, 0]
    means = [r.mean_payoff for r in results]
    bars = ax.bar(names, means, color=colors)
    ax.set_title("Average Payoff per Round")
    ax.set_ylabel("Mean Payoff")
    ax.bar_label(bars, fmt="%.3f")

    # Chart 2: running total profit over time
    ax = axes[0, 1]
    for r, color in zip(results, colors):
        cumulative = np.cumsum(r.payoffs)
        ax.plot(cumulative, label=r.strategy_name, color=color)
    ax.set_title("Cumulative P&L Over Rounds")
    ax.set_xlabel("Round")
    ax.set_ylabel("Cumulative Payoff")
    ax.legend()

    # Chart 3: full spread of results
    ax = axes[1, 0]
    for r, color in zip(results, colors):
        ax.hist(r.payoffs, bins=30, alpha=0.5, label=r.strategy_name, color=color)
    ax.set_title("Distribution of Round Payoffs")
    ax.set_xlabel("Payoff")
    ax.set_ylabel("Count")
    ax.legend()

    # Chart 4: typical range and outliers
    ax = axes[1, 1]
    box_data = [r.payoffs for r in results]
    bp = ax.boxplot(box_data, labels=names, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_title("Payoff Spread (Median, Range, Outliers)")
    ax.set_ylabel("Payoff")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved dashboard to {save_path}")
    else:
        plt.show()


def plot_comparison(results: List[EvalResult], metric: str = "mean_payoff", save_path: str = None) -> None:
    """A simpler option: draws just ONE bar chart instead of the full
    4-chart dashboard, in case you ever want a quick, lighter result."""
    if not results:
        return

    names = [r.strategy_name for r in results]
    values = [r.summary()[metric] for r in results]
    colors = [_strategy_color(n) for n in names]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(names, values, color=colors)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(f"{results[0].game_name} — {metric.replace('_', ' ').title()} by Strategy")
    ax.bar_label(bars, fmt="%.3f")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved plot to {save_path}")
    else:
        plt.show()