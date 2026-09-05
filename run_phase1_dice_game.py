"""
Runs the Dice Market Making Game (Game 1) comparing the naive fixed-spread
strategy against the optimal inventory-aware strategy.

Run: python run_phase1_dice_game.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.dice_market_making import (
    DiceMarketMakingGame,
    NaiveFixedSpreadStrategy,
    OptimalInventoryAwareStrategy,
)

if __name__ == "__main__":
    game = DiceMarketMakingGame()
    strategies = [NaiveFixedSpreadStrategy(), OptimalInventoryAwareStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase1_dice_game.png")