"""
Game 2: Card Game (hypergeometric conditioning).

A shuffled deck of 40 cards (values 1-10, four of each) is drawn from,
one card per round, within a session. Before each draw, the market posts
a noisy quote centered on the deck's OVERALL average (5.5) — it doesn't
adjust for which cards have already been removed.

As cards get drawn, the TRUE expected value of the remaining deck shifts
away from 5.5 (e.g. if a lot of high cards have already come out, the
remaining deck skews low). A strategy that correctly recomputes the
conditional expected value of the remaining deck (hypergeometric
reasoning) can spot when the market's quote is mispriced relative to
what's actually left — one that doesn't, can't.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


CARD_VALUES = list(range(1, 11))   # 1 through 10
COPIES_PER_VALUE = 4               # 4 of each value, like suits in a real deck
N_DRAWS_PER_SESSION = 25           # how many cards get drawn per session (more draws = more drift)
EDGE_THRESHOLD = 0.3               # minimum mispricing required to act
QUOTE_NOISE = 0.75                 # market quote noise range (smaller = less noise drowning out the real signal)
OVERALL_MEAN = sum(CARD_VALUES * COPIES_PER_VALUE) / (len(CARD_VALUES) * COPIES_PER_VALUE)


class NaiveFixedValueStrategy(Strategy):
    """Always believes the fair value is the deck's original overall
    average (5.5), no matter which cards have already been drawn."""

    name = "naive_fixed_value"

    def decide(self, observation):
        quote = observation["quote"]
        fair_value = OVERALL_MEAN

        if quote < fair_value - EDGE_THRESHOLD:
            return "buy"
        elif quote > fair_value + EDGE_THRESHOLD:
            return "sell"
        return "pass"


class OptimalHypergeometricStrategy(Strategy):
    """Recomputes the true expected value of the REMAINING deck each
    round (sum of remaining cards / count of remaining cards), correctly
    accounting for what's already been drawn."""

    name = "optimal_hypergeometric"

    def decide(self, observation):
        quote = observation["quote"]
        fair_value = observation["remaining_sum"] / observation["remaining_count"]

        if quote < fair_value - EDGE_THRESHOLD:
            return "buy"
        elif quote > fair_value + EDGE_THRESHOLD:
            return "sell"
        return "pass"


class CardGame(Game):
    """One simulate_round() call = one full session of drawing cards
    from a freshly shuffled deck, deciding buy/sell/pass on each one."""

    name = "card_game"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        deck = CARD_VALUES * COPIES_PER_VALUE
        random.shuffle(deck)
        remaining = deck.copy()

        total_payoff = 0.0
        trade_count = 0

        for _ in range(N_DRAWS_PER_SESSION):
            remaining_sum = sum(remaining)
            remaining_count = len(remaining)

            # market's quote: noisy, centered on the ORIGINAL overall
            # average, not adjusted for what's already been drawn
            quote = OVERALL_MEAN + random.uniform(-QUOTE_NOISE, QUOTE_NOISE)

            observation = {
                "quote": quote,
                "remaining_sum": remaining_sum,
                "remaining_count": remaining_count,
            }
            action = strategy.decide(observation)

            drawn_value = remaining.pop()  # deck is pre-shuffled, so popping = a random draw

            if action == "buy":
                payoff = drawn_value - quote
                trade_count += 1
            elif action == "sell":
                payoff = quote - drawn_value
                trade_count += 1
            else:
                payoff = 0.0

            total_payoff += payoff

        return RoundResult(
            payoff=total_payoff,
            metadata={"trade_count": trade_count},
        )