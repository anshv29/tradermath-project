"""
This file sets the rules that every game must follow.

Every game must have a function called simulate_round() that takes in
a strategy, runs one round of the game using that strategy, and returns
a result. That way, one piece of code can run ANY game with ANY strategy
plugged into it later on.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict

from core.strategy import Strategy

@dataclass
class RoundResult:
    """
    This is what every single simulated round returns, no matter the game.

    payoff = the score or profit/loss from that one round
    metadata = any extra details worth keeping, like what actually
               happened in that round (useful for double-checking later)
    """
    payoff: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class Game(ABC):
    """This is a template. You never use Game directly — you make new
    games that follow its rules, like DiceMarketMakingGame or CardGame."""

    name: str = "unnamed_game"

    @abstractmethod
    def simulate_round(self, strategy: "Strategy") -> RoundResult:
        """
        Every game must have this function.

        Runs one round of the game using the given strategy, and must
        return a RoundResult (at minimum, a payoff number).
        """
        raise NotImplementedError