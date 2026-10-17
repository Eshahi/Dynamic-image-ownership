"""Endpoint analysis beyond the frozen scorer: inventories and competing-owner E3.

Trusted registry descriptors and owner/q lookup are added detector side information.
Beta enrollment never re-embeds: its q is the native beta semantic_code of the copy.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path

ALPHA, BETA = ('qim-pilot-owner-' + x for x in ('alpha', 'beta'))


def upper95(k, n):
    from scipy.stats import beta
    return None if n == 0 else (1.0 if k == n else float(beta.ppf(.95, k + 1, n - k)))


def native_q(call):
    det = call.get('detection') or {}
    sem = det.get('semantic') or {}
    return sem.get('decoded_code') if sem.get('found') and sem.get('read') else None


def qmatch(decoded, expected):
    if decoded is None or expected is None:
        return False
    return (int(str(decoded), 16) ^ int(str(expected), 16)).bit_count() <= 6


def near_clusters(near, psnrs, cutoff, different, accepted_clusters):
    """Offsets within one film shot are repeats of a single independent unit."""
    eligible = {str(p['pair_id']): str(p.get('shot', p['pair_id'])) for p in near
                if isinstance(p, dict) and p['pair_id'] in psnrs and psnrs[p['pair_id']] is not None
                and (psnrs[p['pair_id']] < cutoff) == different}
    accepted_ids = {c.removeprefix('near:') for c in accepted_clusters}
    return len(set(eligible.values())), len({shot for pid, shot in eligible.items() if pid in accepted_ids})


def attribution(records, scores, calls, rule, pointer=True):
    """Keep every matching record; ties and multiple owners never become a winner."""
    candidates = [i for i, rec in enumerate(records)
                  if not pointer or qmatch(native_q(calls.get(rec['owner'], {})), rec['q'])]
    matched = [i for i in candidates if scores[i] is not None and rule(scores[i])]
    owners = sorted({records[i]['owner'] for i in matched})
    # Fingerprint ranks by D1 then B1, preserving exact ties explicitly.
    ranked = sorted(matched, key=lambda i: (-(scores[i].get('d1') if scores[i].get('d1') is not None else -2),
                                           -scores[i]['b1'], records[i]['record_id']))
    best = records[ranked[0]]['record_id'] if ranked else None
    first = min(matched, key=lambda i: records[i]['enrollment_index']) if matched else None
    return dict(candidate_count=len(candidates), match_count=len(matched), owners=owners,
                matched_records=[records[i]['record_id'] for i in matched], best_record=best,
                attribution=('original_owner_unique' if owners == [ALPHA] else 'wrong_owner' if owners == [BETA]
                             else 'ambiguous_owners' if owners else 'no_attribution'),
                wrong_owner_present=BETA in owners,
                enrollment_order_alone_can_favor_original_owner=bool(first is not None and records[first]['owner'] == ALPHA and BETA in owners))


def scenario(rows, ids, frozen):
    # Deliberately lazy: tf import disables CUDA, so only import after runtime unloads.
    import numpy as np
    import claude_round3_two_factor as scorer
    from claude_two_factor_instance import cos, norm
    memo = {}

    def vector(unit):
        if unit in memo:
            return memo[unit]
        r = rows.get('descriptor:' + unit, {})
        result = None
        if r.get('outcome') == 'completed' and r.get('cache'):
            try:
                with np.load(r['cache'], allow_pickle=False) as data:
                    d, b = data['D1'], data['B1']
                    dn, bn = norm(d) if d.size else None, norm(b)
                    if bn is not None and ((d.size and dn is not None) or (not d.size and r.get('d1_abstained') is True)):
                        result = dict(D1=dn, B1=bn)
            except (OSError, ValueError, KeyError):
                pass
        memo[unit] = result
        return result

    accept = lambda p: scorer.rule(p, frozen['tau1_d1'], frozen['tau2_b1'], frozen['tauF_b1_fallback'])
    rules = {'pointer_registry': (accept, True), 'fingerprint_only': (accept, False),
             'd1_only': (lambda p: scorer.rule(p, scorer.D1_ONLY_TAU, -2., None), False)}
    results, cells = [], {}
    for model in ('sd15', 'sd21'):
        for strength in (.2, .4):
            records = []
            for owner in (ALPHA, BETA):
                for sid in ids:
                    unit = f'embed:{sid}' if owner == ALPHA else f't3:{model}:{sid}:{strength}:15:C1'
                    row = rows.get(unit, {})
                    native = rows.get(f'native:{unit}:{BETA}', {})
                    q = (row.get('payload') or {}).get('q') if owner == ALPHA else (native.get('detection') or {}).get('semantic_code')
                    records.append(dict(record_id=f'{"alpha" if owner == ALPHA else "beta"}:{sid}', owner=owner, q=q,
                                        enrollment_index=len(records), unit=unit, descriptor_available=vector(unit) is not None))
            for kind in ('exact_copy', 'further_regeneration'):
                cell = f'{model}/{strength}/{kind}'
                summary = dict(planned_sources=len(ids), planned_records=len(records),
                               unknown_records=sum(not r['descriptor_available'] or r['q'] is None for r in records), arms={})
                entries = []
                for sid in ids:
                    unit = f't3:{model}:{sid}:{strength}:15:C1' if kind == 'exact_copy' else f'scenario:{model}:{sid}:{strength}'
                    v = vector(unit)
                    calls = {o: rows.get(f'native:{unit}:{o}', {}) for o in (ALPHA, BETA)}
                    unknown = v is None or any(c.get('outcome') != 'completed' for c in calls.values()) or summary['unknown_records'] > 0
                    scores = []
                    for rec in records:
                        ref = vector(rec['unit'])
                        scores.append(None if ref is None or v is None else dict(d1=cos(v['D1'], ref['D1']), b1=cos(v['B1'], ref['B1'])))
                    arms = {name: attribution(records, scores, calls, rule, ptr) for name, (rule, ptr) in rules.items()}
                    entry = dict(source_id=sid, cell=cell, unknown=unknown, arms=arms)
                    entries.append(entry)
                    results.append(entry)
                for name in rules:
                    counts = Counter(e['arms'][name]['attribution'] for e in entries if not e['unknown'])
                    summary['arms'][name] = dict(attribution=dict(counts), unknown=sum(e['unknown'] for e in entries),
                        wrong_owner_present=sum(e['arms'][name]['wrong_owner_present'] for e in entries if not e['unknown']),
                        fingerprint_order_can_favor_alpha=sum(e['arms'][name]['enrollment_order_alone_can_favor_original_owner'] for e in entries if not e['unknown']),
                        original_record_best=sum(e['arms'][name]['best_record'] == f'alpha:{e["source_id"]}' for e in entries if not e['unknown']),
                        candidate_multiplicity=dict(Counter(e['arms'][name]['candidate_count'] for e in entries)))
                cells[cell] = summary
    primary = [e for e in results]
    return dict(cells=cells, rows=results,
                pass_=bool(primary) and not any(e['unknown'] or e['arms']['pointer_registry']['wrong_owner_present'] for e in primary),
                wrong_owner_definition='Any accepted beta record, including ambiguous alpha+beta attribution, fails E3.',
                beta_q_basis='Native beta semantic_code recomputed from seed15 C1 copy; no reembedding')


def analyze(out, plan, sources):
    from m1b_registry_adapter import evaluate, journal, source_ids
    out = Path(out)
    rows, ids = journal(out), source_ids(sources)
    plan = dict(plan)
    plan.setdefault('near_pair_ids', [n['pair_id'] if isinstance(n, dict) else n for n in plan.get('near', [])])
    scored, attempt = evaluate(out, plan, sources)
    view = scored['plan_view']
    negatives = {}
    for family, stats in view['negatives'].items():
        n = stats['n'] if family.startswith(('look_alike', 'synthetic')) else len(ids)
        accepted = len(set(stats.get('accepted_clusters', [])))
        if family.startswith('look_alike'):
            n, accepted = near_clusters(plan.get('near', []), scored['look_alike_psnr'],
                scored['frozen']['psnr_cutoff_primary'], family == 'look_alike_different', stats.get('accepted_clusters', []))
        negatives[family] = dict(stats, cluster_n=n, accepted_cluster_n=accepted, cluster_upper_95=upper95(accepted, n))
    e3 = scenario(rows, ids, scored['frozen'])
    # The scorer's legacy summary omits absent T4 files. Inventory them independently.
    expected = [f't4:{sid}:{scale}' for sid in ids for scale in (.5, 1.)]
    expected += [f'near:{pid}:{side}' for pid in plan['near_pair_ids'] for side in (0, 1)]
    missing = [rid for rid in expected if rows.get(rid, {}).get('outcome') != 'completed']
    primary = scored['summary']['round3']['cells']
    scorer_unknown = sum(s['missing'] + s.get('pointer_unknown', 0) for s in primary.values())
    negative_unknown = sum(s['missing'] for s in negatives.values())
    result = dict(schema='m1b-registry-endpoints-v1', scorer_attempt=str(attempt),
                  side_information='Trusted registry of owner/record/q and continuous D1+B1 descriptors; native owner-key calls.',
                  E1=view['E1'], E2=dict(families=negatives, false_accepts=view['E2_total'], missing_rows=missing,
                                      unknown_pairs=negative_unknown, pass_=view['E2_total'] == 0 and not missing and not negative_unknown),
                  E3=e3, unknown_primary_seeds=scorer_unknown,
                  quality=[dict(source_id=sid, quality=rows.get(f'embed:{sid}', {}).get('quality')) for sid in ids],
                  supplemental=scored['summary'])
    result['pass_'] = all(v['pass_'] for v in result['E1'].values()) and result['E2']['pass_'] and e3['pass_'] and not scorer_unknown
    (out / 'metrics').mkdir(exist_ok=True)
    (out / 'metrics/endpoints.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
