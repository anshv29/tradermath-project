"""
Game 6: Optimal Stopping / Secretary Game.

Candidates arrive one at a time, in random order, with hidden quality
values. You see each one's value the moment it arrives, and must decide
IMMEDIATELY whether to select it (stop) or pass on it forever (you can
never go back to a rejected candidate). Goal: end up with the best
candidate you can, having only ever seen candidates in sequence.

The classic result (the "1/e rule"): observe and reject the first
N/e (~37%) of candidates purely to learn what "good" looks like in this
pool, then select the very next candidate that beats everyone you've
seen so far. This specific cutoff fraction maximizes your chances of
actually landing the single best candidate in the whole sequence.
"""

import math
import random

from core.game import Game, RoundResult
from core.strategy import Strategy


N_CANDIDATES = 20
VALUE_RANGE = (0, 100)


class NaiveHalfwayStrategy(Strategy):
    """Uses a plausible-sounding but mathematically wrong cutoff: skip
    the first HALF of candidates, then select the next one that beats
    everything seen so far."""

    name = "naive_halfway"

    def decide(self, observation):
        position = observation["position"]
        n_total = observation["n_total"]
        current_value = observation["current_value"]
        best_so_far = observation["best_so_far"]

        skip_count = n_total // 2

        if position <= skip_count:
            return "skip"
        if best_so_far is None or current_value > best_so_far:
            return "select"
        return "skip"


class OptimalStoppingStrategy(Strategy):
    """Uses the correct 1/e cutoff: skip the first N/e candidates, then
    select the next one that beats everything seen so far."""

    name = "optimal_stopping"

    def decide(self, observation):
        position = observation["position"]
        n_total = observation["n_total"]
        current_value = observation["current_value"]
        best_so_far = observation["best_so_far"]

        skip_count = round(n_total / math.e)

        if position <= skip_count:
            return "skip"
        if best_so_far is None or current_value > best_so_far:
            return "select"
        return "skip"


class SecretaryGame(Game):
    """One simulate_round() call = one full sequence of N_CANDIDATES
    candidates, observed one at a time, ending with a single selection
    (forced on the last candidate if the strategy hasn't selected by then)."""

    name = "secretary_stopping"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        values = [random.uniform(*VALUE_RANGE) for _ in range(N_CANDIDATES)]

        best_so_far = None
        selected_value = None
        selected_position = None

        for position in range(1, N_CANDIDATES + 1):
            current_value = values[position - 1]
            is_last = position == N_CANDIDATES

            observation = {
                "position": position,
                "n_total": N_CANDIDATES,
                "current_value": current_value,
                "best_so_far": best_so_far,
            }
            action = strategy.decide(observation)

            if action == "select" or (is_last and selected_value is None):
                selected_value = current_value
                selected_position = position
                break

            if best_so_far is None or current_value > best_so_far:
                best_so_far = current_value

        true_best = max(values)
        got_best = selected_value == true_best

        return RoundResult(
            payoff=selected_value,
            metadata={
                "true_best": true_best,
                "got_best": got_best,
                "selected_position": selected_position,
            },
        )