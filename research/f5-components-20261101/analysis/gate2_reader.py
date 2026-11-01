"""Gate 2 R5 fixed decoded-word reader; pure logic, no data access."""
from __future__ import annotations
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import revised_watermark_v5 as v5

ALPHA = 1e-6
RADIUS = 9
LIMIT = 6
BALL = sum(math.comb(32, j) for j in range(RADIUS + 1))
THRESHOLD = v5._threshold(ALPHA / 2, BALL)
FROZEN_STYLE_THRESHOLD = 8.2593

def distance(a, b):
    return (int(a, 16) ^ int(b, 16)).bit_count()

def corrected(d, s):
    e = v5._decoding_error_rate(s)
    if e >= .5:
        return None
    return min(32., max(0., (d - 32 * e) / (1 - 2 * e)))

def tier(res, center, threshold=THRESHOLD):
    s = float(res['decoded_score'])
    d = distance(res['decoded_code'], center)
    c = corrected(d, s)
    return dict(passes=s >= threshold and c is not None and c <= LIMIT,
                distance=d, corrected=c, score=s)

def endpoints(raw, ep=None):
    s, i = raw['semantic'], raw['instance']
    a, b = tier(s, raw['semantic_code']), tier(i, raw['perceptual_hash'])
    veto = bool(s['read'] and not s['content_match'])
    C = bool(ep['C']) if ep is not None else bool(s['read'] and s['content_match'])
    B = bool(a['passes'] or (b['passes'] and not veto))
    td, tr = v5._threshold(ALPHA / 4, 2**32), v5._threshold(ALPHA / 4, 1)
    return dict(C=C, J=bool(ep['J']) if ep is not None else None,
                O=bool(C or (i['found'] and i['content_match'])),
                O_U=bool((s['decoded_score'] >= td and s['content_match']) or
                         ((i['decoded_score'] >= td or i['recomputed_score'] >= tr) and i['content_match'])),
                Bs=a['passes'], Bi=b['passes'], B=B, C_or_B=C or B, veto=veto,
                s_distance=a['distance'], s_corrected=a['corrected'],
                i_distance=b['distance'], i_corrected=b['corrected'])

def validate_bound():
    # f(mu)=E[max(N(mu,1),N(0,1))]/sqrt(1+mu^2/10).
    # f'(mu) has positive numerator Phi(mu/sqrt(2)) -
    # mu*exp(-mu^2/4)/(10*sqrt(pi)); the first is >=1/2 and
    # the second <=sqrt(2)*exp(-1/2)/(10*sqrt(pi)) < .05.
    # Thus error(s) is nonincreasing for all s, not only on a grid.
    # r_eff(s)=6+20e(s) <= r_eff(threshold) <10 proves every
    # accepted integer distance is <=9, including s>=sqrt(320).
    bound = LIMIT + (32 - 2 * LIMIT) * v5._decoding_error_rate(THRESHOLD)
    assert abs(THRESHOLD - 7.7791) < .0001
    assert bound < 10
    assert math.sqrt(2)*math.exp(-.5)/(10*math.sqrt(math.pi)) < .05
    for s in [THRESHOLD + k / 100 for k in range(1200)] + [100., 1e6]:
        assert LIMIT + 20 * v5._decoding_error_rate(s) <= bound + 1e-10
    return dict(threshold=THRESHOLD, ball=BALL, radius=RADIUS,
                effective_radius_upper=bound, per_tier_alpha=ALPHA/2,
                B_conditional_union=ALPHA, C_or_B_conditional_union=2*ALPHA)

if __name__ == '__main__':
    import json
    print(json.dumps(validate_bound(), indent=2))
