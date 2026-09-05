"""
This is the engine that actually runs the tests.

Give it a game and a strategy, and it will:
- run the game many times using that strategy
- track how much was won/lost each round
- calculate summary numbers (average profit, risk, etc)

This is the same engine used for every single game in the project, so
every game gets tested and scored the exact same way.
"""

from dataclasses import dataclass, field
from typing import List

import numpy as np

from core.game import Game
from core.strategy import Strategy


@dataclass
class EvalResult:
    """Holds all the results from running one strategy through one game
    many times, plus some calculated summary numbers."""

    game_name: str
    strategy_name: str
    n_rounds: int
    payoffs: List[float] = field(default_factory=list)

    @property
    def mean_payoff(self) -> float:
        """The average profit/loss per round."""
        return float(np.mean(self.payoffs))

    @property
    def std_payoff(self) -> float:
        """How much the results bounce around (risk/consistency)."""
        return float(np.std(self.payoffs, ddof=1)) if len(self.payoffs) > 1 else 0.0

    @property
    def sharpe_like(self) -> float:
        """A simple 'profit vs risk' score. Higher is better — it means
        good average profit without wild swings."""
        if self.std_payoff == 0:
            return 0.0
        return self.mean_payoff / self.std_payoff

    @property
    def max_drawdown(self) -> float:
        """The single worst losing streak, from peak to lowest point,
        across all the simulated rounds."""
        cumulative = np.cumsum(self.payoffs)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = running_max - cumulative
        return float(np.max(drawdowns)) if len(drawdowns) else 0.0

    @property
    def win_rate(self) -> float:
        """What fraction of rounds ended in profit."""
        wins = sum(1 for p in self.payoffs if p > 0)
        return wins / len(self.payoffs) if self.payoffs else 0.0

    def summary(self) -> dict:
        """Packs all the numbers above into one easy-to-print dictionary."""
        return {
            "game": self.game_name,
            "strategy": self.strategy_name,
            "n_rounds": self.n_rounds,
            "mean_payoff": round(self.mean_payoff, 4),
            "std_payoff": round(self.std_payoff, 4),
            "sharpe_like": round(self.sharpe_like, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "win_rate": round(self.win_rate, 4),
        }


def run_eval(game: Game, strategy: Strategy, n_rounds: int = 10_000, seed: int = None) -> EvalResult:
    """
    Runs the given strategy through the given game, n_rounds times,
    and returns all the results.
    """
    if seed is not None:
        np.random.seed(seed)

    strategy.reset()
    result = EvalResult(game_name=game.name, strategy_name=strategy.name, n_rounds=n_rounds)

    for _ in range(n_rounds):
        round_result = game.simulate_round(strategy)
        result.payoffs.append(round_result.payoff)

    return result


def compare_strategies(game: Game, strategies: List[Strategy], n_rounds: int = 10_000, seed: int = None) -> List[EvalResult]:
    """
    Runs several strategies through the same game, so you can directly
    compare them (example: naive strategy vs optimal strategy).
    """
    return [run_eval(game, s, n_rounds=n_rounds, seed=seed) for s in strategies]