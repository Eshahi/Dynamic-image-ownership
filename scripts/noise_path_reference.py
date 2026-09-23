"""Scalar/index contract reference only: no torch, models, images, or execution manifests."""
import math


def leading_suffix(steps, strength):
    if type(steps) is not int or not 1 <= steps <= 1000:
        raise ValueError("steps must be an integer in [1,1000]")
    if isinstance(strength, bool) or not isinstance(strength, (int, float)):
        raise ValueError("strength must be numeric")
    if not math.isfinite(strength) or not 0 < strength <= 1:
        raise ValueError("strength must be finite and in (0,1]")
    retained = int(steps * strength)
    if retained < 1:
        raise ValueError("empty reverse suffix")
    times = [j * (1000 // steps) + 1 for j in reversed(range(steps))]
    # Validate the whole configured schedule, not only the chosen suffix.
    if any(not 0 <= t < 1000 for t in times):
        raise ValueError("offset creates an out-of-range timestep")
    return times[steps - retained:]


def _finite(*values):
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
           for v in values):
        raise ValueError("finite real scalars required")


def add_initial_noise(latent, noise, delta, alpha):
    _finite(latent, noise, delta, alpha)
    if not 0 < alpha <= 1:
        raise ValueError("cumulative alpha must be in (0,1]")
    return math.sqrt(alpha) * latent + math.sqrt(1 - alpha) * (noise + delta)


def eta_zero_step(sample, predicted_noise, alpha_t, alpha_previous):
    _finite(sample, predicted_noise, alpha_t, alpha_previous)
    if not 0 < alpha_t <= alpha_previous <= 1:
        raise ValueError("reverse cumulative alphas must satisfy 0 < a_t <= a_prev <= 1")
    clean_estimate = (sample - math.sqrt(1 - alpha_t) * predicted_noise) / math.sqrt(alpha_t)
    return math.sqrt(alpha_previous) * clean_estimate + math.sqrt(1 - alpha_previous) * predicted_noise
