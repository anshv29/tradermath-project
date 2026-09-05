"""
This file sets the rules that every strategy must follow.

No matter what game it's for (dice, cards, poker, etc), every strategy
must have a function called decide() that looks at the current situation
and picks an action. That way, one piece of code can run ANY strategy
against ANY game later on.
"""

from abc import ABC, abstractmethod
from typing import Any


class Strategy(ABC):
    """This is a template. You never use Strategy directly — you make
    new strategies that follow its rules, like NaiveQuoter or OptimalQuoter."""

    name: str = "unnamed_strategy"

    @abstractmethod
    def decide(self, observation: Any) -> Any:
        """
        Every strategy must have this function.

        observation = whatever info the strategy can currently see
                       (example: a dice roll, or a price someone quoted)
        returns = the action the strategy picks
                  (example: "bet", "pass", or a price to quote back)
        """
        raise NotImplementedError

    def reset(self) -> None:
        """
        Optional: lets a strategy clear its memory before a new test run.
        Most simple strategies won't need this, so it does nothing by default.
        """
        pass

    def on_trade(self, direction: str) -> None:
        """
        Optional: lets a strategy find out what happened after a trade,
        so it can update things like its own inventory count.
        Most simple strategies won't need this, so it does nothing by default.
        """
        pass