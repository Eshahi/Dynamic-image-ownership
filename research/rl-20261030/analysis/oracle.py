"""Post-hoc fixed-arm and clairvoyant ceilings; numeric development records only.

Standard library. Run with approved stdlib Python -I. No policy is fitted.
"""
import collections
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'dev-records.jsonl'
ROWS = [json.loads(line) for line in INPUT.read_text(encoding='utf-8').splitlines()]
ARMS = ('f5-r2', 'v5-r3', 'wam', 'vine-r')
SEEDS = (12, 13, 14)
NATIVE = tuple(f'{family}-{strength}' for family in ('R0', 'R1') for strength in ('0.1', '0.2', '0.4'))
EXTRA = ('R1-mode-0.2', 'R1-rinse-0.1', 'R1-smooth-0.2')
POOLS = {'C': ARMS[:2], 'J': ARMS[:2], 'P': ARMS[2:], 'heterogeneous_C_or_P': ARMS}
INDEX = {(r['cohort'], r['source'], r['arm'], r['cell'], r['seed']): r for r in ROWS}
assert len(INDEX) == len(ROWS)
SOURCES = {c: sorted({r['source'] for r in ROWS if r['cohort'] == c}) for c in ('stage2_union', 'phase_a')}
assert SOURCES['stage2_union'] == SOURCES['phase_a'] and len(SOURCES['phase_a']) == 60
QUALITY = {(r['source'], r['arm']): r['strict_quality'] for r in ROWS if r['cohort'] == 'stage2_union' and r['cell'] == 'clean'}
GLOBAL_QUALITY = [a for a in ARMS if all(QUALITY.get((s, a)) is True for s in SOURCES['stage2_union'])]


def source_score(cohort, source, arm, cell, endpoint, optimistic=False):
    key = endpoint if endpoint in ('C', 'J') else 'presence' if arm in ARMS[2:] else 'C'
    values = [INDEX.get((cohort, source, arm, cell, seed), {}).get(key) for seed in SEEDS]
    missing = sum(v is None for v in values)
    return int(sum(v is True for v in values) + (missing if optimistic else 0) >= 2), missing


def prune(states):
    """Exact nondominated integer vectors, up to three family dimensions."""
    ordered = sorted(states, reverse=True)
    if len(ordered[0]) == 1:
        v = ordered[0]
        return {v: states[v]}
    if len(ordered[0]) == 2:
        best, result = -1, {}
        for v in ordered:
            if v[1] > best:
                result[v] = states[v]
                best = v[1]
        return result
    assert len(ordered[0]) == 3
    # Descending x then y then z: a prefix-max on descending y detects dominance.
    ymax = max(v[1] for v in ordered)
    tree = [-1] * (ymax + 3)
    result = {}
    for v in ordered:
        index = ymax - v[1] + 1
        j, best = index, -1
        while j:
            best = max(best, tree[j])
            j -= j & -j
        if v[2] <= best:
            continue
        result[v] = states[v]
        j = index
        while j < len(tree):
            tree[j] = max(tree[j], v[2])
            j += j & -j
    return result


def analyze(cohort, cells, endpoint, quality=False, mode='conservative'):
    arms = POOLS[endpoint]
    sources = SOURCES[cohort]
    if mode == 'complete_case':
        sources = [s for s in sources if all(source_score(cohort, s, a, c, endpoint)[1] == 0 for a in arms for c in cells)]
    optimistic = mode == 'optimistic'
    scores = {(s, a, c): source_score(cohort, s, a, c, endpoint, optimistic)[0] for s in sources for a in arms for c in cells}
    allowed = {s: [a for a in arms if not quality or QUALITY.get((s, a)) is True] for s in sources}
    fixed_allowed = [a for a in arms if not quality or a in GLOBAL_QUALITY]
    n = len(sources)
    family_cells = {f: [c for c in cells if c.rsplit('-', 1)[0] == f] for f in sorted({c.rsplit('-', 1)[0] for c in cells})}
    families = list(family_cells)

    def summarize(selection):
        bycell = {c: sum(scores[s, selection[s], c] for s in sources if selection.get(s) is not None) for c in cells}
        byfamily = {f: {'successes': sum(bycell[c] for c in cs), 'denominator': n * len(cs)} for f, cs in family_cells.items()}
        return {'successes': sum(bycell.values()), 'denominator': n * len(cells), 'by_cell': bycell,
                'by_family': byfamily, 'average_rate': sum(bycell.values()) / (n * len(cells)) if n else None,
                'worst_family_rate': min(v['successes'] / v['denominator'] for v in byfamily.values()) if n else None,
                'selected_arm_counts': dict(collections.Counter(selection.values()))}

    fixed = {a: summarize({s: a for s in sources}) for a in fixed_allowed}
    average_choice = {s: max(allowed[s], key=lambda a: sum(scores[s, a, c] for c in cells), default=None) for s in sources}
    average = summarize(average_choice)
    # Exact global minimax portfolio: choose each source's arm once, before cell is known.
    states = {(0,) * len(families): ()}
    max_frontier = 1
    for s in sources:
        options = {}
        for a in allowed[s] or [None]:
            vector = tuple(sum(scores[s, a, c] for c in family_cells[f]) if a is not None else 0 for f in families)
            options.setdefault(vector, a)
        options = prune(options)
        new = {}
        for vector, path in states.items():
            for addition, a in options.items():
                v = tuple(x + y for x, y in zip(vector, addition))
                new.setdefault(v, path + (a,))
        states = prune(new)
        max_frontier = max(max_frontier, len(states))
    best = max(states, key=lambda v: (min(Fraction(x, len(family_cells[f])) for x, f in zip(v, families)), sum(v)))
    minimax_selection = dict(zip(sources, states[best]))
    minimax = summarize(minimax_selection)
    clairvoyant = {c: sum(max((scores[s, a, c] for a in allowed[s]), default=0) for s in sources) for c in cells}
    percell = {}
    for c in cells:
        counts = {a: sum(scores[s, a, c] for s in sources) for a in arms}
        constrained_counts = {a: sum(scores[s, a, c] for s in sources if QUALITY.get((s, a)) is True) for a in arms}
        b = max((counts[a] for a in fixed_allowed), default=None)
        percell[c] = {'arm_successes': counts, 'arm_quality_gated_successes': constrained_counts,
                      'best_fixed_successes': b, 'best_fixed_arms': [a for a in fixed_allowed if counts[a] == b],
                      'per_source_oracle_successes': clairvoyant[c], 'oracle_gain': clairvoyant[c] - b if b is not None else None,
                      'denominator': n}
    best_fixed_average = max(fixed, key=lambda a: fixed[a]['average_rate'], default=None)
    best_fixed_minimax = max(fixed, key=lambda a: fixed[a]['worst_family_rate'], default=None)
    return {'n_sources': n, 'cells': cells, 'endpoint': endpoint, 'quality_constrained': quality, 'missing_mode': mode,
            'no_eligible_arm_sources': sum(not allowed[s] for s in sources), 'eligible_fixed_arms': fixed_allowed,
            'missing_seed_endpoints': sum(source_score(cohort, s, a, c, endpoint)[1] for s in sources for a in arms for c in cells),
            'per_cell': percell, 'fixed_arms': fixed, 'best_fixed_average_arm': best_fixed_average,
            'cell_known_fixed_arm_total': sum(v['best_fixed_successes'] for v in percell.values()) if fixed_allowed else None,
            'best_fixed_worst_family_arm': best_fixed_minimax, 'unknown_cell_average_oracle': average,
            'unknown_cell_worst_family_oracle': minimax, 'exact_minimax_max_frontier': max_frontier,
            'clairvoyant_cell_oracle': {'successes': sum(clairvoyant.values()), 'denominator': n * len(cells),
                'average_rate': sum(clairvoyant.values()) / (n * len(cells)) if n else None,
                'worst_family_rate': min(sum(clairvoyant[c] for c in cs) / (n * len(cs)) for cs in family_cells.values()) if n else None,
                'by_cell': clairvoyant}}


def main():
    results = {'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'quality_origin': 'stage2_union clean rows, same marked inputs reused for phase_a; no independent phase_a clean measurement',
               'strict_quality_passes': {a: sum(QUALITY.get((s, a)) is True for s in SOURCES['stage2_union']) for a in ARMS},
               'globally_quality_eligible': GLOBAL_QUALITY, 'analyses': {}}
    for cohort in SOURCES:
        suites = {'native6': NATIVE}
        if cohort == 'stage2_union':
            suites.update(native6_plus_R3=NATIVE + ('R3-0.2',), additionalT3=EXTRA)
        for suite, cells in suites.items():
            for endpoint in POOLS:
                for quality in (False, True):
                    for mode in ('conservative', 'optimistic', 'complete_case'):
                        key = '|'.join((cohort, suite, endpoint, 'quality' if quality else 'unconstrained', mode))
                        results['analyses'][key] = analyze(cohort, cells, endpoint, quality, mode)
    (HERE / 'oracle-results.json').write_text(json.dumps(results, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    lines = ['# Retrospective arm-selection ceilings', '',
             'DERIVED from `dev-records.jsonl` (hash in `oracle-results.json`); script `oracle.py`. Numeric development analysis only. No new policy tested.', '',
             '## Definition and limitations', '',
             '- One success is source majority: at least two of seeds 12/13/14. Conservative missing endpoints count as non-success; optimistic assigns them success; complete-case removes a source from the whole suite when any selected arm/cell/seed endpoint is missing. Complete-case denominators are displayed and differ by endpoint pool.',
             '- Per-cell fixed arm and per-source oracle both know the cell. The unknown-cell average oracle selects one arm per source to maximize total successes across all cells. The unknown-cell worst-family oracle selects one arm per source to maximize the minimum aggregate family success fraction, using exact integer-vector Pareto dynamic programming; average is the tie-break. These are retrospective portfolios, not trainable effects. No arm changes after the unknown cell is revealed. The clairvoyant oracle may change arm for every source and cell.',
             '- Native R0/R1 each have three strengths; R3 has one. Average weights cells equally; minimax weights family rates equally. Each additional T3 variant is a distinct group for the additional-only minimax, not an independently trained encoder family. Phase A has only six native cells; R3 and additional T3 are absent. Stage2 union already contains Stage2a and is not duplicated. Both cohorts reuse the same 60 sources and are not independent replications.',
             '- C/J compare only F5/v5. P compares WAM/VINE message presence, not content binding. The heterogeneous C-or-P ceiling mixes different tasks and is explicitly non-comparable as security performance. F5/v5 carry q32+h32; WAM carries 32 bits and VINE 100 bits with different readers. J tests exact original q and content compatibility, not h recovery. Payload lengths do not imply equal usable capacity.',
             '- Strict clean quality is PSNR >35, SSIM >0.9, LPIPS <0.1. Stage2 clean pass counts: F5 60/60, v5 60/60, WAM 58/60, VINE 31/60. Phase A borrows these checks from the same marked inputs; it has no independently measured clean quality in this normalized file. A quality-constrained source oracle can use only that source’s eligible arms; a fixed arm must pass on all 60 sources. Thus external-only P has no globally eligible fixed arm, not a zero-success fixed arm. Sources with no eligible arm stay in the denominator and yield zero.',
             '- These are optimistic selection ceilings for the finite observed arm set and observed cells, not bounds over unseen methods/encoders. Outcomes were not randomized for a policy comparison. Clean margins, embedding reports and quality require producing/reading each candidate and incur compute; no equal-budget or free-feature claim is made. Missing/failure records remain in the input and primary denominator.', '',
             '## Main implications', '',
             'DERIVED: In Stage2 native6+R3, internal C is 196/420 for the best single fixed arm (v5), 209/420 for an average-optimized per-source portfolio chosen before the cell is known, and 276/420 for the source-and-cell clairvoyant oracle. A simpler cell-known fixed-arm selector already achieves 275/420. The within-cell personalization headroom is therefore only one source majority (R0 .2: 57 to 58); most clairvoyant improvement is knowing the regenerator, not identifying special sources. C worst-family performance stays 62/180 = 0.344444 even for the exact minimax source portfolio.', '',
             'DERIVED: Internal J in the same seven cells is 93/420 fixed, 108/420 for the unknown-cell average portfolio and 132/420 clairvoyant; the cell-known fixed-arm baseline is 130/420. Worst-family J remains 6/180 = 0.033333. Additional T3 has C 14/180 and J 0/180 with no source-oracle improvement. These findings do not establish that a policy can learn the retrospective arm allocation.', '',
             'DERIVED: WAM/VINE P has no unconstrained source-oracle gain beyond VINE: 392/420 on the seven native cells. Its quality-constrained source oracle is 262/420; neither external arm meets strict clean quality on all 60 sources, so there is no globally eligible fixed P comparator. Combining external P with internal C produces a different, heterogeneous task and cannot support a content-binding claim.', '',
             '## Per-cell conservative counts', '',
             'All denominators are 60; F5/v5 columns are C or J, WAM/VINE columns are P. Quality oracle uses per-source eligibility. `none` means no globally eligible fixed arm.', '',
             '| Cohort | Cell | Endpoint pool | Arm counts | Fixed | Oracle | Gain | Quality fixed | Quality oracle |',
             '|---|---|---|---|---:|---:|---:|---:|---:|']
    for cohort in SOURCES:
        suite_names = ('native6_plus_R3', 'additionalT3') if cohort == 'stage2_union' else ('native6',)
        for suite in suite_names:
            for endpoint in POOLS:
                base = results['analyses'][f'{cohort}|{suite}|{endpoint}|unconstrained|conservative']
                q = results['analyses'][f'{cohort}|{suite}|{endpoint}|quality|conservative']
                for c, r in base['per_cell'].items():
                    qc = q['per_cell'][c]
                    counts = ', '.join(f'{a}:{v}' for a, v in r['arm_successes'].items())
                    lines.append(f"| {cohort} | {c} | {endpoint} | {counts} | {r['best_fixed_successes']} | {r['per_source_oracle_successes']} | {r['oracle_gain']} | {qc['best_fixed_successes'] if qc['best_fixed_successes'] is not None else 'none'} | {qc['per_source_oracle_successes']} |")
    lines += ['', '## Across-cell portfolios, conservative', '',
              'Each average entry is successful source-cell majorities / total source-cell pairs. Each worst-family entry is a fraction. Fixed average and fixed worst-family may select different arms; separate unknown-cell portfolios optimize the two objectives.', '',
              '| Cohort/suite | Pool | Quality | Best fixed average | Unknown-cell average oracle | Clairvoyant average oracle | Best fixed worst-family | Unknown-cell minimax | Clairvoyant worst-family |',
              '|---|---|---|---|---|---|---|---|---|']
    for key, r in results['analyses'].items():
        if r['missing_mode'] != 'conservative':
            continue
        cohort, suite, endpoint, quality, _ = key.split('|')
        a, m = r['best_fixed_average_arm'], r['best_fixed_worst_family_arm']
        fixedavg = f"{a}: {r['fixed_arms'][a]['successes']}/{r['fixed_arms'][a]['denominator']}" if a else 'none'
        fixedmin = f"{m}: {r['fixed_arms'][m]['worst_family_rate']:.6f}" if m else 'none'
        av, cv, mm = r['unknown_cell_average_oracle'], r['clairvoyant_cell_oracle'], r['unknown_cell_worst_family_oracle']
        lines.append(f"| {cohort}/{suite} | {endpoint} | {quality} | {fixedavg} | {av['successes']}/{av['denominator']} | {cv['successes']}/{cv['denominator']} | {fixedmin} | {mm['worst_family_rate']:.6f} | {cv['worst_family_rate']:.6f} |")
    lines += ['', '## Missingness sensitivity', '',
              'Every endpoint, quality setting, suite, per-cell count, portfolio and selected-arm count is provided for conservative, optimistic and complete-case modes in `oracle-results.json`. Table below summarizes the unconstrained aggregate oracle sensitivity; missing is seed endpoints across the pool, not missing sources.', '',
              '| Cohort/suite | Pool | Missing | Conservative clairvoyant | Optimistic clairvoyant | Complete sources | Complete clairvoyant |',
              '|---|---|---:|---|---|---:|---|']
    for key, r in results['analyses'].items():
        if r['missing_mode'] != 'conservative' or r['quality_constrained']:
            continue
        cohort, suite, endpoint, _, _ = key.split('|')
        opt = results['analyses'][key.replace('|conservative', '|optimistic')]
        cc = results['analyses'][key.replace('|conservative', '|complete_case')]
        def fraction(x):
            y = x['clairvoyant_cell_oracle']
            return f"{y['successes']}/{y['denominator']}"
        lines.append(f"| {cohort}/{suite} | {endpoint} | {r['missing_seed_endpoints']} | {fraction(r)} | {fraction(opt)} | {cc['n_sources']} | {fraction(cc)} |")
    (HERE / 'oracle-note.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'analyses': len(results['analyses']), 'quality': results['strict_quality_passes'], 'max_DP_frontier': max(r['exact_minimax_max_frontier'] for r in results['analyses'].values())}))


if __name__ == '__main__':
    main()
