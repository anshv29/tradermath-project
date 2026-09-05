"""
Runs the Secretary / Optimal Stopping Game (Game 6) comparing the naive
halfway cutoff against the mathematically optimal 1/e cutoff.

Also reports the probability of landing the TRUE best candidate — the
classic metric for this problem, separate from raw payoff value.

Run: python run_phase6_secretary.py
"""

import random

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.secretary_stopping import SecretaryGame, NaiveHalfwayStrategy, OptimalStoppingStrategy


def print_best_candidate_rate(game, strategies, n_rounds=10_000, seed=42):
    print(f"\n=== {game.name} — probability of landing the TRUE best candidate ({n_rounds} rounds) ===")
    print(f"{'Strategy':<25}{'P(got best)':>15}")
    print("-" * 40)
    for strategy in strategies:
        random.seed(seed)
        strategy.reset()
        got_best_count = 0
        for _ in range(n_rounds):
            r = game.simulate_round(strategy)
            if r.metadata["got_best"]:
                got_best_count += 1
        rate = got_best_count / n_rounds
        print(f"{strategy.name:<25}{rate:>15.3f}")


if __name__ == "__main__":
    game = SecretaryGame()
    strategies = [NaiveHalfwayStrategy(), OptimalStoppingStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    print_best_candidate_rate(game, strategies, n_rounds=10_000, seed=42)
    plot_dashboard(results, save_path="phase6_secretary.png")