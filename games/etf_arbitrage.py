"""
Game 3: ETF Arbitrage (mean-reverting spread, transaction-cost aware).

The gap between an ETF's price and its true underlying value (the spread)
doesn't sit at zero and stay there — it wanders around, but tends to pull
back toward zero over time. We model that wandering-but-pulling-back
behavior with an Ornstein-Uhlenbeck (OU) process, a standard tool for
"mean-reverting" quantities in finance.

Each round, the strategy sees the current spread and decides whether to
bet on it reverting (mean-reversion trade). Every trade costs a small
transaction fee. A strategy that trades on ANY nonzero spread bleeds
money to fees on tiny, not-worth-it mispricings. A strategy that only
trades when the spread is big enough to clear the fee (with room to
spare) should come out ahead.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


THETA = 0.3             # how fast the spread pulls back toward zero
MU = 0.0                 # the spread's long-run average (zero = fair value)
SIGMA = 1.0               # how much random noise/volatility the spread has
T_STEPS = 50              # number of time steps per session
TRANSACTION_COST = 0.3    # cost paid every time a trade is made


class NaiveAnySpreadStrategy(Strategy):
    """Trades on ANY nonzero spread, ignoring transaction costs entirely."""

    name = "naive_any_spread"
    threshold = 0.0

    def decide(self, observation):
        spread = observation["spread"]
        if spread > self.threshold:
            return "short_spread"   # bet the spread falls back toward 0
        elif spread < -self.threshold:
            return "long_spread"    # bet the spread rises back toward 0
        return "hold"


class OptimalCostAwareStrategy(Strategy):
    """Only trades when the spread is large enough that the expected
    reversion profit clears the transaction cost with room to spare."""

    name = "optimal_cost_aware"
    threshold = 1.0  # calibrated to comfortably clear TRANSACTION_COST

    def decide(self, observation):
        spread = observation["spread"]
        if spread > self.threshold:
            return "short_spread"
        elif spread < -self.threshold:
            return "long_spread"
        return "hold"


class ETFArbitrageGame(Game):
    """One simulate_round() call = one full session of watching a
    mean-reverting spread evolve over T_STEPS, deciding whether to
    trade it at each step."""

    name = "etf_arbitrage"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        # start the spread somewhere plausible for this process
        spread = random.gauss(0, SIGMA)

        total_payoff = 0.0
        trade_count = 0

        for _ in range(T_STEPS):
            observation = {"spread": spread}
            action = strategy.decide(observation)

            # simulate the next step of the mean-reverting spread (OU process)
            noise = random.gauss(0, 1)
            next_spread = spread + THETA * (MU - spread) + SIGMA * noise

            if action == "short_spread":
                # profits if spread falls (moves toward 0), pays the fee
                payoff = (spread - next_spread) - TRANSACTION_COST
                trade_count += 1
            elif action == "long_spread":
                # profits if spread rises (moves toward 0 from below), pays the fee
                payoff = (next_spread - spread) - TRANSACTION_COST
                trade_count += 1
            else:
                payoff = 0.0

            total_payoff += payoff
            spread = next_spread

        return RoundResult(
            payoff=total_payoff,
            metadata={"trade_count": trade_count},
        )