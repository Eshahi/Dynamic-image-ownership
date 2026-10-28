"""Pure-stdlib exact planning probabilities; never runs an image experiment."""

import json
import math


ALPHA = 0.05 / 6


def binomial_pmf(n, p):
    """Return all probabilities for the small, prespecified planning grids."""
    if not isinstance(n, int) or n < 0 or not 0 <= p <= 1:
        raise ValueError("Require integer n >= 0 and p in [0, 1]")
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k)
            for k in range(n + 1)]


def critical_successes(n, null_p, alpha=ALPHA):
    """Smallest count whose inclusive upper tail is <= alpha; n+1 if none."""
    if not 0 < alpha < 1:
        raise ValueError("Require alpha in (0, 1)")
    masses = binomial_pmf(n, null_p)
    for k in range(n + 1):
        if math.fsum(masses[k:]) <= alpha:
            return k
    return n + 1


def binomial_power(n, alternative_p, null_p=0.70, alpha=ALPHA):
    k = critical_successes(n, null_p, alpha)
    return math.fsum(binomial_pmf(n, alternative_p)[k:])


def mcnemar_power(n, p10, p01, alpha=ALPHA):
    """Exact unconditional power of the one-sided conditional exact test.

    D ~ Bin(n, p10+p01); X|D ~ Bin(D, p10/(p10+p01)).
    p10 is candidate success/comparator failure. No mid-p or randomization.
    """
    if p10 < 0 or p01 < 0 or p10 + p01 > 1:
        raise ValueError("Require valid discordant probabilities")
    q = p10 + p01
    if q == 0:
        binomial_pmf(n, 0)  # Validate n even in the degenerate case.
        return 0.0
    return math.fsum(weight * binomial_power(d, p10 / q, 0.5, alpha)
                     for d, weight in enumerate(binomial_pmf(n, q)))


def zero_event_upper(n, alpha=0.05):
    if not isinstance(n, int) or n <= 0 or not 0 < alpha < 1:
        raise ValueError("Require positive integer n and alpha in (0, 1)")
    return -math.expm1(math.log(alpha) / n)


def zero_event_sample_size(target, alpha=0.05):
    if not 0 < target < 1 or not 0 < alpha < 1:
        raise ValueError("Require target and alpha in (0, 1)")
    return math.ceil(math.log(alpha) / math.log1p(-target))


def planning_table():
    return [{"n": n, "critical_absolute": critical_successes(n, 0.70),
             "absolute": {str(p): binomial_power(n, p)
                          for p in (0.80, 0.85, 0.90)},
             "paired": {f"{a:.2f},{b:.2f}": mcnemar_power(n, a, b)
                        for a, b in ((0.25, 0.05), (0.20, 0.10), (0.35, 0.05))},
             "zero_event_upper95": zero_event_upper(n)}
            for n in (80, 120, 160, 200)]


if __name__ == "__main__":
    print(json.dumps({"alpha": ALPHA, "table": planning_table(),
                      "specificity_n": {str(t): zero_event_sample_size(t)
                                        for t in (0.01, 0.001, 0.0001)}},
                     indent=2))
