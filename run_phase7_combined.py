"""
Runs the Combined Trading Game (Game 7, capstone) comparing the naive
combined strategy (quoting and taking done independently) against the
optimal combined strategy (quoting and taking coordinated through a
shared inventory).

Run: python run_phase7_combined.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.combined_trading_game import CombinedTradingGame, NaiveCombinedStrategy, OptimalCombinedStrategy

if __name__ == "__main__":
    game = CombinedTradingGame()
    strategies = [NaiveCombinedStrategy(), OptimalCombinedStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase7_combined.png")