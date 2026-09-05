"""
Runs the Fermi Estimation Game (Game 4) comparing the naive fixed-interval
strategy against the optimal calibrated (uncertainty-propagating) strategy.

Note: this game's "payoff" is a negated scoring-rule penalty, not real
P&L, so the shared Sharpe-like metric can look misleading here (dividing
a negative mean by a smaller std can make a BETTER strategy look worse).
For this game specifically, interval width and capture rate (did the
true value actually land inside the interval) are the metrics that
actually matter — printed separately below.

Run: python run_phase4_fermi.py
"""

from core.harness import compare_strategies, run_eval
from core.reporting import print_comparison_table, plot_dashboard
from games.fermi_estimation import FermiEstimationGame, NaiveFixedIntervalStrategy, OptimalCalibratedStrategy


def print_calibration_summary(game, strategies, n_rounds=10_000, seed=42):
    print(f"\n=== {game.name} — calibration summary ({n_rounds} rounds) ===")
    print(f"{'Strategy':<25}{'Avg Interval Width':>22}{'Capture Rate':>16}")
    print("-" * 63)
    for strategy in strategies:
        result = run_eval(game, strategy, n_rounds=n_rounds, seed=seed)
        # re-run to also pull metadata (run_eval only stores payoffs)
        import random
        random.seed(seed)
        strategy.reset()
        widths, captures = [], []
        for _ in range(n_rounds):
            r = game.simulate_round(strategy)
            widths.append(r.metadata["interval_width"])
            captures.append(r.metadata["captured"])
        avg_width = sum(widths) / len(widths)
        capture_rate = sum(captures) / len(captures)
        print(f"{strategy.name:<25}{avg_width:>22.2f}{capture_rate:>16.3f}")


if __name__ == "__main__":
    game = FermiEstimationGame()
    strategies = [NaiveFixedIntervalStrategy(), OptimalCalibratedStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    print_calibration_summary(game, strategies, n_rounds=10_000, seed=42)
    plot_dashboard(results, save_path="phase4_fermi.png")