"""
Runs the ETF Arbitrage Game (Game 3) comparing the naive any-spread
strategy against the optimal cost-aware strategy.

Run: python run_phase3_etf_arbitrage.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.etf_arbitrage import ETFArbitrageGame, NaiveAnySpreadStrategy, OptimalCostAwareStrategy

if __name__ == "__main__":
    game = ETFArbitrageGame()
    strategies = [NaiveAnySpreadStrategy(), OptimalCostAwareStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase3_etf_arbitrage.png")