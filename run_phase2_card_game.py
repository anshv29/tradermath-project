"""
Runs the Card Game (Game 2) comparing the naive fixed-value strategy
against the optimal hypergeometric (correctly-conditioned) strategy.

Run: python run_phase2_card_game.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.card_game import CardGame, NaiveFixedValueStrategy, OptimalHypergeometricStrategy

if __name__ == "__main__":
    game = CardGame()
    strategies = [NaiveFixedValueStrategy(), OptimalHypergeometricStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase2_card_game.png")