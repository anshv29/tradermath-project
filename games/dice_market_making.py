"""
Game 1: Market Making Dice Game.

Each session (one call to simulate_round) is a mini trading day:
- A hidden true value is picked once at the start (a number 1-6),
  and kept secret from the market maker the whole session.
- Over 20 rounds within the session, the market maker posts a buy price
  and a sell price around its best guess of the true average (3.5).
- Some counterparties are "informed" (they secretly know the true value
  and only trade when it's profitable for them — bad for the market maker).
  Some are "noise" traders (trade randomly, regardless of price — good
  for the market maker, easy profit from the spread).
- At the end of the session, whatever inventory the market maker is still
  holding gets settled against the true value — so an unbalanced position
  is real risk, not free.
"""

import random

from core.game import Game, RoundResult
from core.strategy import Strategy


FAIR_VALUE = 3.5  # the true average of a fair 6-sided die
N_SUBROUNDS = 20  # number of trade opportunities per session
P_INFORMED = 0.3  # probability a given counterparty already knows the true value


class NaiveFixedSpreadStrategy(Strategy):
    """Always posts the same fixed buy/sell prices around fair value.
    Never adjusts for inventory — this is the baseline to beat."""

    name = "naive_fixed_spread"

    def __init__(self, half_spread: float = 0.5):
        self.half_spread = half_spread

    def decide(self, observation):
        fair_value = observation["fair_value"]
        return {
            "bid": fair_value - self.half_spread,
            "ask": fair_value + self.half_spread,
        }


class OptimalInventoryAwareStrategy(Strategy):
    """
    Shifts both the buy and sell price based on current inventory, to
    reduce risk from a lopsided position.

    reservation_price = fair_value - (gamma * inventory)

    If inventory is positive (we've bought too much), the reservation
    price drops, which lowers both quotes — makes it harder for someone
    to sell us even more (our buy price is lower) and easier for someone
    to buy from us (our sell price is lower too), nudging our inventory
    back toward zero.
    """

    name = "optimal_inventory_aware"

    def __init__(self, half_spread: float = 0.5, gamma: float = 0.15):
        self.half_spread = half_spread
        self.gamma = gamma
        self.inventory = 0

    def reset(self) -> None:
        self.inventory = 0

    def decide(self, observation):
        fair_value = observation["fair_value"]
        reservation_price = fair_value - (self.gamma * self.inventory)
        return {
            "bid": reservation_price - self.half_spread,
            "ask": reservation_price + self.half_spread,
        }

    def on_trade(self, direction: str) -> None:
        if direction == "mm_sold":
            self.inventory -= 1  # we sold, now more short
        elif direction == "mm_bought":
            self.inventory += 1  # we bought, now more long
        # "no_trade" changes nothing


class DiceMarketMakingGame(Game):
    """
    One simulate_round() call = one full trading session of 20
    dice-trade opportunities against a single hidden true value.
    """

    name = "dice_market_making"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        strategy.reset()  # fresh inventory at the start of each session

        true_value = random.randint(1, 6)  # hidden until session ends
        cash_flow = 0.0
        inventory = 0
        trade_count = 0

        for _ in range(N_SUBROUNDS):
            quote = strategy.decide({"fair_value": FAIR_VALUE})
            bid, ask = quote["bid"], quote["ask"]

            is_informed = random.random() < P_INFORMED

            if is_informed:
                if true_value > ask:
                    direction = "mm_sold"      # customer buys, we sell
                elif true_value < bid:
                    direction = "mm_bought"    # customer sells, we buy
                else:
                    direction = "no_trade"
            else:
                # noise trader always trades, direction is random
                direction = random.choice(["mm_sold", "mm_bought"])

            if direction == "mm_sold":
                cash_flow += ask
                inventory -= 1
                trade_count += 1
            elif direction == "mm_bought":
                cash_flow -= bid
                inventory += 1
                trade_count += 1

            strategy.on_trade(direction)

        # Settle remaining inventory against the true value, now revealed
        final_payoff = cash_flow + (inventory * true_value)

        return RoundResult(
            payoff=final_payoff,
            metadata={
                "true_value": true_value,
                "final_inventory": inventory,
                "trade_count": trade_count,
            },
        )