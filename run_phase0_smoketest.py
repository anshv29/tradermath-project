"""
This script actually runs the test and shows you results.

Run it with: python run_phase0_smoketest.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games._dummy_coinflip import CoinFlipGame, AlwaysBetStrategy, NeverBetStrategy

if __name__ == "__main__":
    game = CoinFlipGame()
    strategies = [AlwaysBetStrategy(), NeverBetStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase0_smoketest.png")