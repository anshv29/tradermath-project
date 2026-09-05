"""
Game 5: Auction / Winner's Curse Game.

There's a true value V (common to everyone, e.g. the value of an asset),
but nobody actually knows it. Each bidder gets their own private, noisy
signal (estimate) of V. Everyone submits a sealed bid; whoever bids
highest wins and pays their own bid.

The trap: if every bidder just bids their raw signal, the winner is
systematically the bidder whose signal happened to be the MOST
overoptimistic — not the most accurate one. Winning is itself bad news
about your own estimate, and a correct bidder needs to account for that
BEFORE bidding, not be surprised by it after.

This uses a real, provable result from order statistics: if signals are
V + Uniform(-E, E) noise across N bidders, the expected overpayment from
naive bidding is E * (N-1)/(N+1) — the expected value of the maximum of
N i.i.d. uniform noise draws.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


N_BIDDERS = 5              # total bidders in each auction, including ours
NOISE_RANGE = 20.0          # each bidder's signal = true value +/- this much noise
TRUE_VALUE_RANGE = (50, 150)  # range the true (unknown) value is drawn from


class NaiveRawSignalStrategy(Strategy):
    """Bids exactly its own private signal, with no correction for the
    fact that winning is itself evidence the signal was too optimistic."""

    name = "naive_raw_signal"

    def decide(self, observation):
        return observation["own_signal"]


class OptimalWinnersCurseStrategy(Strategy):
    """Shades its bid down below its own signal, correcting for the
    expected overestimation bias of whichever signal turns out to win
    (the expected value of the max of N-1 competing noise draws)."""

    name = "optimal_winners_curse"

    def decide(self, observation):
        own_signal = observation["own_signal"]
        n_bidders = observation["n_bidders"]
        noise_range = observation["noise_range"]

        # expected value of the max of (n_bidders - 1) i.i.d. Uniform(-E, E)
        # draws, the classic order-statistic correction for this setup
        shading = noise_range * (n_bidders - 1) / (n_bidders + 1)
        return own_signal - shading


class AuctionWinnersCurseGame(Game):
    """One simulate_round() call = one sealed-bid auction. Our strategy
    is one bidder; the other N_BIDDERS - 1 bidders always bid their raw
    signal (a fixed population of naive competitors), so the comparison
    isolates the effect of OUR bidding rule specifically."""

    name = "auction_winners_curse"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        true_value = random.uniform(*TRUE_VALUE_RANGE)

        own_signal = true_value + random.uniform(-NOISE_RANGE, NOISE_RANGE)
        observation = {
            "own_signal": own_signal,
            "n_bidders": N_BIDDERS,
            "noise_range": NOISE_RANGE,
        }
        our_bid = strategy.decide(observation)

        # the other bidders always bid their raw (uncorrected) signal
        opponent_bids = [
            true_value + random.uniform(-NOISE_RANGE, NOISE_RANGE)
            for _ in range(N_BIDDERS - 1)
        ]

        all_bids = opponent_bids + [our_bid]
        we_won = our_bid == max(all_bids)

        payoff = (true_value - our_bid) if we_won else 0.0

        return RoundResult(
            payoff=payoff,
            metadata={"true_value": true_value, "won": we_won, "our_bid": our_bid},
        )