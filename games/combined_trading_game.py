"""
Game 7: Combined Trading Game (capstone).

This fuses two roles into one agent, acting on the SAME asset within
the same session, sharing the SAME inventory:

1. MARKET MAKING (like Game 1): the agent posts its own bid/ask quote.
   A counterparty may trade against it.
2. MARKET TAKING (like Game 2): the agent sees someone ELSE's quote
   and decides whether to buy/sell/pass against it.

Both actions affect the same running inventory, which gets settled
against the true (hidden until session end) value at the end.

The real point of combining them: a naive agent handles each role in
isolation, ignoring how one affects the other. An optimal agent
coordinates both — it quotes AND takes with the shared inventory in
mind, so it doesn't, for example, aggressively buy more via taking
while its own quotes are also accumulating a large position.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


FAIR_VALUE = 50.0
TRUE_VALUE_NOISE = 10.0      # session's true value = fair value +/- this much
T_STEPS = 20                  # rounds per session
P_INFORMED = 0.3              # probability a counterparty knows the true value
HALF_SPREAD = 1.5             # own quoting half-spread
EXTERNAL_QUOTE_NOISE = 3.0    # noise on the external quote we react to
EDGE_THRESHOLD = 1.0          # minimum mispricing required to take a trade


class NaiveCombinedStrategy(Strategy):
    """Handles quoting and taking completely independently, ignoring
    inventory in both — the two roles never coordinate."""

    name = "naive_combined"

    def decide(self, observation):
        fair_value = observation["fair_value"]
        external_quote = observation["external_quote"]

        # quoting: fixed spread, no inventory awareness
        bid = fair_value - HALF_SPREAD
        ask = fair_value + HALF_SPREAD

        # taking: trade on any edge past a fixed threshold, no inventory awareness
        if external_quote < fair_value - EDGE_THRESHOLD:
            take_action = "buy"
        elif external_quote > fair_value + EDGE_THRESHOLD:
            take_action = "sell"
        else:
            take_action = "pass"

        return {"bid": bid, "ask": ask, "take_action": take_action}


class OptimalCombinedStrategy(Strategy):
    """Coordinates quoting and taking through a SHARED inventory: quotes
    skew based on current inventory (like the optimal dice strategy),
    and taking decisions require MORE edge if they'd push inventory
    further in an already-lopsided direction — the two roles actively
    work together instead of fighting each other."""

    name = "optimal_combined"

    def __init__(self, gamma: float = 0.15, inventory_penalty: float = 0.15):
        self.gamma = gamma
        self.inventory_penalty = inventory_penalty
        self.inventory = 0

    def reset(self) -> None:
        self.inventory = 0

    def decide(self, observation):
        fair_value = observation["fair_value"]
        external_quote = observation["external_quote"]

        # quoting: reservation price skewed by inventory (same idea as Game 1)
        reservation_price = fair_value - (self.gamma * self.inventory)
        bid = reservation_price - HALF_SPREAD
        ask = reservation_price + HALF_SPREAD

        # taking: require MORE edge to take a trade that would push
        # inventory further in the direction it's already leaning
        buy_threshold = EDGE_THRESHOLD + max(0, self.inventory) * self.inventory_penalty
        sell_threshold = EDGE_THRESHOLD + max(0, -self.inventory) * self.inventory_penalty

        if external_quote < fair_value - buy_threshold:
            take_action = "buy"
        elif external_quote > fair_value + sell_threshold:
            take_action = "sell"
        else:
            take_action = "pass"

        return {"bid": bid, "ask": ask, "take_action": take_action}

    def on_trade(self, direction: str) -> None:
        if direction == "sold":
            self.inventory -= 1
        elif direction == "bought":
            self.inventory += 1


class CombinedTradingGame(Game):
    """One simulate_round() call = one full session combining market
    making and market taking on a shared inventory, settled at the end."""

    name = "combined_trading_game"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        strategy.reset()

        true_value = FAIR_VALUE + random.uniform(-TRUE_VALUE_NOISE, TRUE_VALUE_NOISE)
        cash = 0.0
        inventory = 0

        for _ in range(T_STEPS):
            external_quote = FAIR_VALUE + random.uniform(-EXTERNAL_QUOTE_NOISE, EXTERNAL_QUOTE_NOISE)
            observation = {"fair_value": FAIR_VALUE, "external_quote": external_quote}
            action = strategy.decide(observation)

            bid, ask = action["bid"], action["ask"]
            take_action = action["take_action"]

            is_informed = random.random() < P_INFORMED
            if is_informed:
                if true_value > ask:
                    mm_direction = "sold"
                elif true_value < bid:
                    mm_direction = "bought"
                else:
                    mm_direction = "no_trade"
            else:
                mm_direction = random.choice(["sold", "bought"])

            if mm_direction == "sold":
                cash += ask
                inventory -= 1
            elif mm_direction == "bought":
                cash -= bid
                inventory += 1

            if mm_direction != "no_trade":
                strategy.on_trade(mm_direction)

            if take_action == "buy":
                cash -= external_quote
                inventory += 1
                strategy.on_trade("bought")
            elif take_action == "sell":
                cash += external_quote
                inventory -= 1
                strategy.on_trade("sold")

        final_payoff = cash + (inventory * true_value)

        return RoundResult(
            payoff=final_payoff,
            metadata={"true_value": true_value, "final_inventory": inventory},
        )