"""Exact descriptive loss-bound arithmetic on existing JSON, not a fitted model."""
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
OWNER = 'qim-pilot-owner-alpha'
METRICS = ('lpips', 'psnr_db', 'ssim_rgb')
SEEDS = (12, 13, 14)


def extract(row, reference):
    if row is None or row.get('status') != 'ok':
        return None
    det = row.get('detections', {}).get('f5-r2', {}).get(OWNER, {})
    q = row.get(reference, {})
    y = det.get('endpoints', {}).get('C')
    if det.get('status') != 'ok' or q.get('status') != 'ok' or not isinstance(y, bool):
        return None
    vals = [q.get(k) for k in METRICS]
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in vals):
        return None
    return y, vals


def main():
    rows = {}
    digest = hashlib.sha256()
    lines = 0
    with INPUT.open('rb') as f:
        for line in f:
            digest.update(line)
            r = json.loads(line)
            rows[r['id']] = r
            lines += 1
    index = {}
    for r in rows.values():
        if r.get('arm') != 'f5-r2' or r.get('control') != 'C1':
            continue
        if (r.get('channel'), r.get('strength')) not in (('R0', .2), ('R1', .1)) or r.get('seed') not in SEEDS:
            continue
        key = (r['source_id'], r['channel'], r['seed'])
        if key in index:
            raise ValueError('Duplicate scientific identity')
        index[key] = r
    sources = sorted({key[0] for key in index})
    if len(sources) != 60 or len(index) != 360:
        raise ValueError('Unexpected source/record count')
    results = []
    for reference in ('distortion', 'total_distortion'):
        hist = Counter({k: 0 for k in range(4)})
        included, incomplete = [], []
        for sid in sources:
            a = [extract(index.get((sid, 'R0', seed)), reference) for seed in SEEDS]
            b = [extract(index.get((sid, 'R1', seed)), reference) for seed in SEEDS]
            if any(v is None for v in a + b):
                incomplete.append(sid)
                continue
            if any(v[0] for v in b):
                raise ValueError('Required R1-negative premise fails; no selective deletion allowed')
            for _, qa in a:
                for _, qb in b:
                    if not (qb[0] < qa[0] and qb[1] > qa[1] and qb[2] > qa[2]):
                        raise ValueError('Required complete dominance premise fails')
            k = sum(v[0] for v in a)
            hist[k] += 1
            included.append({'source_id': sid, 'r0_positive_calls': k})
        n = len(included)
        if not n:
            raise ValueError('No complete sources')
        brier = sum((Fraction(k, 2 * (k + 3)) * count for k, count in hist.items()), Fraction()) / n
        hard = sum((Fraction(k, 6) * count for k, count in hist.items()), Fraction()) / n
        results.append({'quality_reference': reference, 'complete_sources': n,
                        'incomplete_source_ids': incomplete, 'positive_r0_histogram': dict(hist),
                        'sources': included, 'complete_outputs': 6 * n,
                        'verified_all_local_dominance_pairs': 9 * n,
                        'brier_lower_bound_fraction': str(brier), 'brier_lower_bound': float(brier),
                        'hard_error_lower_bound_fraction': str(hard), 'hard_error_lower_bound': float(hard)})
    out = {'status': 'Post-hoc empirical observed-subset bound; not a new fit, experiment or population test',
           'input': str(INPUT), 'input_sha256': digest.hexdigest(), 'journal_lines': lines,
           'final_ids': len(rows), 'results': results}
    (HERE / 'monotone-bound-check.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps([{k: v for k, v in r.items() if k != 'sources'} for r in results], indent=2))


if __name__ == '__main__':
    main()
