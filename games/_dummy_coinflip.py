"""
This is a throwaway test game — NOT at ALL of the real 7 trading games.
It's just a simple coin flip, used to prove that Strategy, Game, harness,
and reporting all work correctly together before we build anything real.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


class AlwaysBetStrategy(Strategy):
    """A strategy that always bets on heads, every round."""
    name = "always_bet"

    def decide(self, observation):
        return "bet"


class NeverBetStrategy(Strategy):
    """A strategy that always sits out, every round."""
    name = "never_bet"

    def decide(self, observation):
        return "pass"


class CoinFlipGame(Game):
    """Bet $1 on heads. Win $1 if heads, lose $1 if tails. Fair coin,
    50/50 either way. This is just a simple test — not real trading math."""

    name = "dummy_coinflip"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        action = strategy.decide(observation=None)
        if action == "bet":
            outcome = random.choice(["heads", "tails"])
            payoff = 1.0 if outcome == "heads" else -1.0
        else:
            payoff = 0.0
        return RoundResult(payoff=payoff, metadata={"action": action})