"""Stdlib-only checks of hypothetical source-level binomial precision, not data."""
import math

def cdf(k, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return float(k >= n)
    return math.fsum(math.exp(math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1)
                             + j*math.log(p)+(n-j)*math.log1p(-p))
                     for j in range(k+1))

def upper(k, n, alpha):
    if k == n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo+hi)/2
        if cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2

def lower(k, n, alpha):
    return 0.0 if k == 0 else 1-upper(n-k, n, alpha)

for n in (12, 86):
    print(f"Zero harmful groups, n={n}, alpha=.0125: upper={upper(0,n,.0125):.9f}")
for wins, losses in ((20,0),(20,20)):
    lo=lower(wins,200,.0125)-upper(losses,200,.0125)
    hi=upper(wins,200,.0125)-lower(losses,200,.0125)
    print(f"Hypothetical n=200, wins={wins},losses={losses}: paired bounds [{lo:.9f},{hi:.9f}]")
print("These are one-sided union-bound constructions, not measured success rates or necessary sample sizes.")
