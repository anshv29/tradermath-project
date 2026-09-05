"""
Game 4: Fermi Estimation (calibrated uncertainty via a proper scoring rule).

Unlike the other games, this one isn't about trading — it's about giving
a good ESTIMATE with an honest CONFIDENCE INTERVAL for an unknown
quantity that's the product of several sub-quantities you have noisy
"hints" about (classic Fermi-problem decomposition: break a hard number
into a product of easier-to-guess pieces).

You're scored with a proper scoring rule (a Winkler interval score):
- A narrower interval scores better, IF the true value still falls inside it.
- If the true value falls OUTSIDE your interval, you get penalized hard,
  scaled by how far outside it fell.
This rewards being precisely as confident as you should be — not
overconfident (too narrow, truth falls outside), not underconfident
(needlessly wide "just in case" intervals).
"""

import math
import random

from core.game import Game, RoundResult
from core.strategy import Strategy


N_FACTORS = 3            # the unknown quantity is a product of this many factors
FACTOR_RANGE = (2, 8)     # true value of each factor is drawn from this range
NOISE_FRAC_RANGE = (0.05, 0.5)  # each factor's hint can be noisier or cleaner, varies per round
ALPHA = 0.1               # nominal 90% interval target for the Winkler score
NAIVE_INTERVAL_FRAC = 0.3  # naive always uses this fixed interval width, ignoring hint quality
Z_MULTIPLIER = 1.6         # scales the optimal strategy's computed uncertainty into an interval width


def winkler_score(lower: float, upper: float, true_value: float, alpha: float) -> float:
    """
    Standard interval scoring rule. LOWER is better in the classic
    definition (it's a penalty). We'll negate it before returning as a
    payoff, so higher payoff = better, consistent with the rest of the project.
    """
    width = upper - lower
    if true_value < lower:
        return width + (2 / alpha) * (lower - true_value)
    elif true_value > upper:
        return width + (2 / alpha) * (true_value - upper)
    else:
        return width


class NaiveFixedIntervalStrategy(Strategy):
    """Multiplies the hints together for a point estimate, then always
    slaps on the same fixed-width interval, regardless of how noisy or
    clean the underlying hints actually were."""

    name = "naive_fixed_interval"

    def decide(self, observation):
        hints = observation["hints"]  # list of (hint_value, noise_frac)
        point_estimate = 1.0
        for hint_value, _ in hints:
            point_estimate *= hint_value

        half_width = point_estimate * NAIVE_INTERVAL_FRAC
        return {"lower": point_estimate - half_width, "upper": point_estimate + half_width}


class OptimalCalibratedStrategy(Strategy):
    """Correctly propagates each factor's individual uncertainty into a
    combined uncertainty for the product, and sizes the interval
    accordingly — wider when the hints were noisy, narrower when they
    were clean."""

    name = "optimal_calibrated"

    def decide(self, observation):
        hints = observation["hints"]
        point_estimate = 1.0
        for hint_value, _ in hints:
            point_estimate *= hint_value

        # relative variance of a product of independent factors is
        # approximately the SUM of each factor's own relative variance
        relative_variance = sum((noise_frac / math.sqrt(3)) ** 2 for _, noise_frac in hints)
        relative_std = math.sqrt(relative_variance)

        half_width_frac = Z_MULTIPLIER * relative_std
        half_width = point_estimate * half_width_frac
        return {"lower": point_estimate - half_width, "upper": point_estimate + half_width}


class FermiEstimationGame(Game):
    """One simulate_round() call = one Fermi problem: a hidden true
    quantity (product of N_FACTORS unknowns), noisy hints about each
    factor, and a score for how well the strategy estimates it."""

    name = "fermi_estimation"

    def simulate_round(self, strategy: Strategy) -> RoundResult:
        true_factors = [random.uniform(*FACTOR_RANGE) for _ in range(N_FACTORS)]
        true_value = 1.0
        for f in true_factors:
            true_value *= f

        hints = []
        for f in true_factors:
            noise_frac = random.uniform(*NOISE_FRAC_RANGE)
            hint_value = f * (1 + random.uniform(-noise_frac, noise_frac))
            hints.append((hint_value, noise_frac))

        observation = {"hints": hints}
        estimate = strategy.decide(observation)

        score = winkler_score(estimate["lower"], estimate["upper"], true_value, ALPHA)
        payoff = -score  # negate so higher payoff = better, like every other game

        return RoundResult(
            payoff=payoff,
            metadata={
                "true_value": true_value,
                "interval_width": estimate["upper"] - estimate["lower"],
                "captured": estimate["lower"] <= true_value <= estimate["upper"],
            },
        )