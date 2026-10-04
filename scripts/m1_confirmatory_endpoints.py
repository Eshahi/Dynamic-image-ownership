"""Pure per-cell binomial summaries; callers must supply independent planned units.

No file/model/data access. Repeated owner claims, seeds and attacks must never be
submitted as extra independent units. Cross-cell simultaneous coverage is absent.
"""
import math
from scipy.stats import beta, norm

VERSION = 'm1-confirmatory-endpoints-v1'


def bounds(events, total, alpha=0.05):
    if type(events) is not int or type(total) is not int or not 0 <= events <= total:
        raise ValueError('Invalid binomial counts')
    if not 0 < alpha < 1:
        raise ValueError('Invalid tail probability')
    if total == 0:
        return dict(rate=None, lower_one_sided=None, upper_one_sided=None, wilson_two_sided=None)
    p = events / total
    lower = 0.0 if events == 0 else float(beta.ppf(alpha, events, total-events+1))
    upper = 1.0 if events == total else float(beta.ppf(1-alpha, events+1, total-events))
    z = float(norm.ppf(1-alpha/2))
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total))/denominator
    radius = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/denominator
    return dict(rate=p, lower_one_sided=lower, upper_one_sided=upper,
                wilson_two_sided=[max(0.0, center-radius), min(1.0, center+radius)])


def cell(planned_units, observations, *, event_kind):
    """A positive event is success; a negative event is false attribution.

    observations maps unique unit ID to bool or None. Missing/None positives
    count as misses; missing/None negatives count as errors conservatively.
    This function cannot verify scientific independence or valid detections.
    """
    if event_kind not in ('positive_success', 'negative_error'):
        raise ValueError('Unknown endpoint')
    units = list(planned_units)
    if any(type(u) is not str or not u for u in units) or len(set(units)) != len(units):
        raise ValueError('Require unique nonempty planned unit IDs')
    if not isinstance(observations, dict) or set(observations)-set(units):
        raise ValueError('Unexpected unit observations')
    if any(v is not None and type(v) is not bool for v in observations.values()):
        raise ValueError('Only bool or missing observations permitted')
    valid = [observations[u] for u in units if observations.get(u) is not None]
    missing = len(units)-len(valid)
    events = sum(valid)
    conservative_events = events + (missing if event_kind == 'negative_error' else 0)
    conservative = bounds(conservative_events, len(units))
    endpoint = conservative['lower_one_sided' if event_kind == 'positive_success' else 'upper_one_sided']
    target = 0.80 if event_kind == 'positive_success' else 0.01
    meets = None if endpoint is None else (endpoint >= target if event_kind == 'positive_success' else endpoint <= target)
    return dict(schema_version=VERSION, event_kind=event_kind, planned=len(units), valid=len(valid),
                missing=missing, observed_events=events, conservative_events=conservative_events,
                observed_valid=bounds(events, len(valid)), conservative=conservative,
                numerical_target=target, meets_numerical_target=meets,
                caveat='Per-cell independent-unit assumption required; no simultaneous coverage, quality gate, security or milestone verdict')
