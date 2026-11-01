"""WP1 descriptive endpoint accounting, stdlib only. Never reads images or Phase B.

Run from the worktree with MAIN's stdlib python -I. All inputs are allowlisted;
all outputs are confined to RD/results/wp1-accounting. No detector is executed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
RD = ROOT / 'research/f5-components-20261101'
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASE = MAIN / '.thesis-build/dev-runs'
OUT = RD / 'results/wp1-accounting'
INPUTS = {
    'stage2': BASE / '20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl',
    'native': BASE / '20261026-0855-et-final-phase-a/results/native.jsonl',
    'detect': BASE / '20261026-0855-et-final-phase-a/results/detect.jsonl',
    'attacks': BASE / '20261026-0855-et-final-phase-a/results/attacks.jsonl',
}
ARMS = ('f5-r2', 'v5-r3')
ALPHA, BETA = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
RADII = (0, 1, 2, 3, 4, 6)
SEEDS = (12, 13, 14)
T0 = time.monotonic()


def budget():
    if time.monotonic() - T0 > 540:
        raise RuntimeError('WP1 CPU run exceeds conservative 540-second budget')


def threshold(n):
    lo, hi = 0.0, 40.0
    for _ in range(150):
        mid = (lo + hi) / 2
        if n * math.erfc(mid / math.sqrt(2)) / (4 * math.erfc(1)) <= 1e-6:
            hi = mid
        else:
            lo = mid
    return hi


THRESHOLDS = {r: threshold(sum(math.comb(32, i) for i in range(r + 1))) for r in RADII}


def load(name):
    path = INPUTS[name]
    rows, audit, sha = {}, Counter(), hashlib.sha256()
    repeats = []
    with path.open('rb') as handle:
        for lineno, raw in enumerate(handle, 1):
            budget()
            sha.update(raw)
            if not raw.strip():
                continue
            row = json.loads(raw)
            audit['lines'] += 1
            audit['status:' + row['status']] += 1
            key = row['id']
            # Stage2 journal appends generated/ok progress rows. Its declared
            # retained union uses the last ok/safety-blocked record per ID.
            eligible = name != 'stage2' or row['status'] in ('ok', 'safety_blocked')
            if not eligible:
                continue
            if key in rows:
                old_line, old = rows[key]
                audit['duplicate_eligible_ids'] += 1
                if old != row:
                    repeats.append({'id': key, 'old_line': old_line, 'new_line': lineno,
                                    'old_status': old['status'], 'new_status': row['status']})
                    # A replacement of different terminal results needs review.
                    if old['status'] == 'ok' and row['status'] == 'ok':
                        raise ValueError(f'Conflicting ok records: {name}:{key}')
            rows[key] = (lineno, row)
    return rows, {'path': str(path), 'sha256': sha.hexdigest(), 'inventory': dict(audit),
                  'retained_ids': len(rows), 'nonidentical_replacements': repeats}


def finite(value):
    if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
        raise ValueError(f'Non-finite/non-numeric score: {value}')
    return value


def classify(call, status):
    if status != 'ok' or not call or call.get('status') != 'ok':
        return {'bucket': 'M', 'C': False, 'J': False, 'read': False, 'found': False,
                'old': {r: False for r in RADII}, 'ball_lb': {r: False for r in RADII},
                'ball_ub': {r: False for r in RADII}, 'semantic_available': False}
    raw, ep = call['raw'], call['endpoints']
    s = raw['semantic']
    c, read, found = bool(ep['C']), bool(s['read']), bool(s['found'])
    assert not c or read
    assert not read or found
    assert c == (read and bool(s['content_match']))
    dec, rec = finite(s.get('decoded_score')), finite(s.get('recomputed_score'))
    dt, rt = finite(s.get('decoded_threshold')), finite(s.get('recomputed_threshold'))
    code, center = s.get('decoded_code'), raw.get('semantic_code')
    distance = (int(code, 16) ^ int(center, 16)).bit_count() if code and center else None
    # candidate is a route label, not a content-code hex string. Reproduce the
    # judge's actually executed rule separately from the corrected lower bound.
    assert s.get('candidate') in ('decoded', 'recomputed', None)
    old, lower, upper = {}, {}, {}
    for r, t in THRESHOLDS.items():
        old[r] = rec is not None and rec >= t
        lower[r] = old[r] or (dec is not None and distance is not None and distance <= r and dec >= t)
        upper[r] = dec is not None and dec >= t
        assert not lower[r] or upper[r]
    return {'bucket': 'C' if c else 'B' if read else 'U' if found else 'L',
            'C': c, 'J': bool(ep['J']), 'read': read, 'found': found,
            'old': old, 'ball_lb': lower, 'ball_ub': upper, 'semantic_available': True,
            'decoded_score': dec, 'recomputed_score': rec,
            'decoded_margin': dec - dt if dec is not None and dt is not None else None,
            'recomputed_margin': rec - rt if rec is not None and rt is not None else None,
            'code_distance': distance, 'route': s.get('candidate')}


def csv_write(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def stat(values):
    v = [x for x in values if x is not None]
    return {'n': len(v), 'mean': statistics.mean(v) if v else None,
            'median': statistics.median(v) if v else None,
            'sd': statistics.stdev(v) if len(v) > 1 else None,
            'min': min(v) if v else None, 'max': max(v) if v else None}


def main():
    if OUT.exists():
        raise FileExistsError(f'Use a fresh output directory; not overwriting {OUT}')
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1', 'Keep CUDA disabled'
    data, provenance = {}, {}
    for name in INPUTS:
        data[name], provenance[name] = load(name)
    src2 = sorted({r['source_id'] for _, r in data['stage2'].values() if r['channel'] == 'clean'})
    srca = sorted({r['source'] for _, r in data['native'].values() if r['kind'] == 'native'})
    assert len(src2) == len(srca) == 60
    assert src2 == srca, 'Studies must not silently substitute sources'
    samples = defaultdict(list)
    missing = []

    def add(study, cell, arm, source, seed, owner_role, record, call, status, location):
        z = classify(call, status)
        z.update(source=source, seed=seed, record=record, location=location, status=status)
        samples[(study, cell, arm, owner_role)].append(z)
        if z['bucket'] == 'M':
            missing.append({'study': study, 'cell': cell, 'arm': arm, 'role': owner_role,
                            'source': source, 'seed': seed, 'record': record, 'status': status, 'location': location})

    index = {}
    cells2 = set()
    for key, (line, row) in data['stage2'].items():
        identity = (row['channel'], row['strength'], row['arm'], row['source_id'], row['seed'])
        assert identity not in index
        index[identity] = (line, row)
        cells2.add((row['channel'], row['strength']))
    for channel, strength in sorted(cells2, key=str):
        seeds = (None,) if strength is None else SEEDS
        cell = channel if strength is None else f'{channel}-{strength}'
        for arm in ARMS:
            for source in src2:
                for seed in seeds:
                    for role in ('marked', 'wrong_owner', 'C0'):
                        input_arm = 'unmarked' if role == 'C0' else arm
                        line, row = index.get((channel, strength, input_arm, source, seed), (None, {}))
                        owner = BETA if role == 'wrong_owner' else ALPHA
                        call = row.get('detections', {}).get(arm, {}).get(owner)
                        add('stage2-union', cell, arm, source, seed, role, row.get('id', 'ABSENT'), call,
                            row.get('status', 'absent_row'), f'stage2:{line}' if line else 'stage2:ABSENT')
    # All scheduled native cells are read from native journal, including blocks.
    acells = sorted({r['cell'] for _, r in data['native'].values() if r['kind'] == 'native'})
    assert acells == [f'{f}-{s}' for f in ('R0', 'R1') for s in (.1, .2, .4)]
    for cell in acells + ['ctrlB-codec']:
        seeds = (None,) if cell == 'ctrlB-codec' else SEEDS
        for arm in ARMS:
            for source in srca:
                for seed in seeds:
                    for role in ('marked', 'wrong_owner', 'C0'):
                        input_arm = 'unmarked' if role == 'C0' else arm
                        item = f'ctrlB-codec:{source}:{input_arm}' if seed is None else f'native:{cell}:{source}:{seed}:{input_arm}'
                        ident = f'det:{arm}:{item}'
                        line, row = data['detect'].get(ident, (None, {}))
                        if not row:
                            origin = data['attacks' if seed is None else 'native'].get(item)
                            status = origin[1]['status'] if origin else 'absent_origin'
                            assert status != 'ok', f'Missing detector for available output: {ident}'
                        else:
                            status = row['status']
                        owner = BETA if role == 'wrong_owner' else ALPHA
                        add('phase-a', cell, arm, source, seed, role, ident, row.get('calls', {}).get(owner),
                            status, f'detect:{line}' if line else f'native/attacks:{item}')

    summaries, source_rows, stats = [], [], []
    for (study, cell, arm, role), calls in sorted(samples.items()):
        per_source = defaultdict(list)
        for x in calls:
            per_source[x['source']].append(x)
        counts = Counter(x['bucket'] for x in calls)
        nseeds = len(next(iter(per_source.values())))
        assert nseeds in (1, 3)
        assert all(len(x) == nseeds for x in per_source.values())
        required = 1 if nseeds == 1 else 2
        maj = lambda predicate: sum(sum(bool(predicate(x)) for x in values) >= required for values in per_source.values())
        row = {'study': study, 'cell': cell, 'arm': arm, 'role': role, 'sources': len(per_source),
               'seeds_per_source': nseeds, 'expected_calls': len(calls),
               **{f'calls_{k}': counts[k] for k in ('C', 'B', 'U', 'L', 'M')},
               'C_sources': maj(lambda x: x['C']), 'J_calls': sum(x['J'] for x in calls), 'J_sources': maj(lambda x: x['J']),
               'C_missing_upper': maj(lambda x: x['C'] or x['bucket'] == 'M'),
               'read_oracle_sources': maj(lambda x: x['read']),
               'found_oracle_sources': maj(lambda x: x['found']),
               'read_missing_upper': maj(lambda x: x['read'] or x['bucket'] == 'M'),
               'found_missing_upper': maj(lambda x: x['found'] or x['bucket'] == 'M'),
               'median_decoded_margin': stat([x.get('decoded_margin') for x in calls])['median'],
               'median_recomputed_margin': stat([x.get('recomputed_margin') for x in calls])['median']}
        row['binding_only_increment'] = row['read_oracle_sources'] - row['C_sources']
        row['fixed_found_increment'] = row['found_oracle_sources'] - row['C_sources']
        row['unrestricted_trivial_increment'] = row['sources'] - row['C_sources']
        for r in RADII:
            row[f'r{r}_judge_reproduction'] = maj(lambda x: x['old'][r])
            row[f'r{r}_corrected_lower'] = maj(lambda x: x['ball_lb'][r])
            row[f'r{r}_global_upper'] = maj(lambda x: x['ball_ub'][r])
            row[f'r{r}_lower_calls'] = sum(x['ball_lb'][r] for x in calls)
        assert sum(row[f'calls_{k}'] for k in ('C', 'B', 'U', 'L', 'M')) == len(calls)
        summaries.append(row)
        for source, vals in sorted(per_source.items()):
            ct = Counter(x['bucket'] for x in vals)
            sr = {'study': study, 'cell': cell, 'arm': arm, 'role': role, 'source': source,
                  'required': required, **{k: ct[k] for k in ('C', 'B', 'U', 'L', 'M')},
                  'J': sum(x['J'] for x in vals), 'locations': ';'.join(x['location'] for x in vals)}
            for r in RADII:
                sr[f'r{r}_corrected_calls'] = sum(x['ball_lb'][r] for x in vals)
            source_rows.append(sr)
        for metric in ('decoded_score', 'recomputed_score', 'decoded_margin', 'recomputed_margin', 'code_distance'):
            stats.append({'study': study, 'cell': cell, 'arm': arm, 'role': role, 'metric': metric,
                          **stat([x.get(metric) for x in calls])})

    # Independent reproduction of every saved judge native-cell summary.
    expected = json.loads((RD / 'judge/loss-budget.json').read_text(encoding='utf-8'))
    expected_ball = json.loads((RD / 'judge/reader-ball.json').read_text(encoding='utf-8'))
    checks = []
    for row in summaries:
        key = f"{row['arm']}|{row['cell']}"
        if row['study'] != 'stage2-union' or row['role'] != 'marked' or key not in expected:
            continue
        ex = expected[key]
        for k, old in [('C', 'C'), ('B', 'binding'), ('U', 'undecoded'), ('L', 'lost'), ('M', 'missing')]:
            assert row[f'calls_{k}'] == ex['counts'].get(old, 0), (key, k)
        for new, old in [('C_sources', 'c_sources'), ('read_oracle_sources', 'read_sources'), ('found_oracle_sources', 'any_sources')]:
            assert row[new] == ex[old], (key, new)
        for r in RADII:
            assert row[f'r{r}_judge_reproduction'] == expected_ball['counts'][key][f'r{r}'], (key, r)
        checks.append(key)
    assert len(checks) == 14
    coverage = []
    for name in ('native', 'attacks'):
        inv = Counter()
        for _, r in data[name].values():
            cell = r.get('cell', str(r.get('strength')) if r['kind'] == 'gridA' else f"{r.get('epsilon')}:{r.get('lam')}" if r['kind'] == 'gridB' else r['kind'])
            inv[(r['kind'], cell, r.get('arm', 'f5-law'), r['status'])] += 1
        for (kind, cell, arm, status), n in sorted(inv.items()):
            coverage.append({'journal': name, 'kind': kind, 'cell': cell, 'arm': arm, 'status': status, 'n': n,
                             'endpoint_availability': 'NO_DETECTOR_QUALITY_GRID' if kind.startswith('grid') else 'NO_C_ENDPOINT_TANGENT' if kind == 'law' else 'ACCOUNTED'})
    OUT.mkdir(parents=True)
    csv_write('loss-cells.csv', [r for r in summaries if r['role'] == 'marked'])
    csv_write('negative-cells.csv', [r for r in summaries if r['role'] != 'marked'])
    csv_write('source-accounting.csv', source_rows)
    csv_write('score-statistics.csv', stats)
    csv_write('missing-calls.csv', missing)
    csv_write('phase-a-coverage.csv', coverage)
    doc = ['# Saved-development loss accounting', '',
           'MEASURED: stdlib aggregation of declared saved journals; no new reader/model/image execution. See provenance.json for exact paths, hashes, command and code commit. Each CSV row is a file-line locator (header is line 1).', '',
           'DERIVED: B = decoded/content-failed; U = recomputed-only; L = neither frozen test passed; M = unavailable. L does not prove physical erasure. Read/found are fixed-stage oracle ceilings, not safe endpoints or component-causal budgets. Missing calls count unsuccessful. Source majority = 2/3, one-image controls = 1/1.', '',
           'MEASURED: All 14 judge loss-budget cells and all 84 radius counts reproduce exactly. Corrected lower bounds use raw.semantic_code rather than semantic.candidate. A Hamming-ball endpoint is distinct from frozen F5 soft-binding C and J; these counts do not establish calibrated false-positive control or T4/T5 safety.', '',
           '| Study | Cell | Arm | C/B/U/L/M calls | C/J sources | Content oracle | Found oracle | r0 | r3 old -> corrected lower |',
           '|---|---|---|---|---|---|---|---|---|']
    for r in summaries:
        if r['role'] == 'marked':
            doc.append(f"| {r['study']} | {r['cell']} | {r['arm']} | {'/'.join(str(r['calls_'+k]) for k in ('C','B','U','L','M'))} | {r['C_sources']}/{r['J_sources']} | {r['read_oracle_sources']} | {r['found_oracle_sources']} | {r['r0_corrected_lower']} | {r['r3_judge_reproduction']} -> {r['r3_corrected_lower']} |")
    doc += ['', 'SOURCE: Phase A native covers R0/R1 only. K3 has mechanism diagnostics, not a 60-source Phase-A detector grid. Its gridA/gridB outputs were quality-ineligible and never detector-released: ceilings there are UNKNOWN. Coverage is explicit in phase-a-coverage.csv. Stage2 union includes clean, both codecs, resize controls, native families, rinse, mode and smoothing. Earlier development variants are report-level evidence in context/wp1-prior-evidence.md; no unavailable raw endpoint is invented.', '',
            'JUDGMENT: No ball radius is selected. C0 and wrong-owner results in negative-cells.csv are descriptive diagnostics, not copy-paste or semantic-collision tests. The two studies reuse the same 60 sources and are not independent replications. Stats are descriptive across correlated seed calls, not confidence intervals.']
    (OUT / 'REPORT.md').write_text('\n'.join(doc) + '\n', encoding='utf-8')
    output_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir())}
    meta = {'label': 'MEASURED exploratory saved-development accounting', 'inputs': provenance,
            'command': [sys.executable, '-I', str(Path(__file__).resolve())],
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'protocol_sha256': hashlib.sha256((RD / 'analysis/WP1-ACCOUNTING-SPEC.md').read_bytes()).hexdigest(),
            'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'), 'workers': 1,
            'phase_b_journals': 'off', 'seconds': time.monotonic() - T0,
            'thresholds': THRESHOLDS, 'judge_cells_reproduced': checks,
            'source_overlap': len(set(src2) & set(srca)), 'marked_cells': 44,
            'outputs_sha256': output_hashes}
    (OUT / 'provenance.json').write_text(json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'seconds': meta['seconds'], 'marked_cells': 44,
                      'negative_cells': 88, 'judge_cells_reproduced': len(checks), 'missing_calls': len(missing)}))


if __name__ == '__main__':
    main()
