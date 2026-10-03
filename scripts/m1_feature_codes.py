"""Fixed projection representation diagnostic on pinned v5 development vectors."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import numpy as np
import analyze_v5_semantic_geometry as old

ROOT = Path(__file__).resolve().parents[1]
SEEDS = [20261003, 20261004, 20261005]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    out = args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(old.MAIN / '.thesis-build/dev-runs'):
        raise ValueError('Fresh MAIN development run path required')
    if old.sha(args.results) != old.EXPECTED:
        raise ValueError('Pinned input hash mismatch')
    labels = json.loads(old.LABELS.read_text())
    index, pairs, _ = old.validate_inputs(json.loads(args.results.read_text()), labels, json.loads(old.PROFILE.read_text()))
    vectors = {(s, a): np.asarray(old.validate_feature(index[f'clean-{s}-{a}'])[0])
               for s in labels['source_ids'] for a in ('C0', 'C1')}
    matrices = {seed: np.random.default_rng(seed).standard_normal((512, 512)) for seed in SEEDS}
    encodings = {'full512': vectors}
    for seed, matrix in matrices.items():
        for dim in (32, 128, 512):
            projected = {k: matrix[:dim] @ v for k, v in vectors.items()}
            if dim != 512:
                encodings[f'real{dim}-seed{seed}'] = {k: v / np.linalg.norm(v) for k, v in projected.items()}
            encodings[f'sign{dim}-seed{seed}'] = {k: v > 0 for k, v in projected.items()}
    exported, summaries, drifts = [], {}, {}
    for name, enc in encodings.items():
        def similarity(a, b):
            return float(np.mean(a == b)) if name.startswith('sign') else float(a @ b)
        drifts[name] = [{'id': s, 'C0_C1_similarity': similarity(enc[s, 'C0'], enc[s, 'C1'])} for s in labels['source_ids']]
        summaries[name] = {}
        for arm in ('C0', 'C1'):
            rows = [{'left': p['left'], 'right': p['right'], 'label': p['label'],
                     'representation': name, 'arm': arm,
                     'similarity': similarity(enc[p['left'], arm], enc[p['right'], arm])} for p in pairs]
            exported.extend(rows)
            summaries[name][arm] = old.empirical_auc([r['similarity'] for r in rows if r['label'] == 'same'],
                                                   [r['similarity'] for r in rows if r['label'] == 'different'])
    summaries['v5-sign32-original'] = {a: old.rank_stats(pairs, a)['negative_q'] for a in ('C0', 'C1')}
    out.mkdir(parents=True)
    for filename, obj in [('pairs.json', exported), ('summary.json', summaries), ('drifts.json', drifts)]:
        (out / filename).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
    plan = ROOT / 'research/m1-feature-code-design.md'
    record = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'command': sys.argv, 'config': {'dimensions': [32,128,512], 'no_threshold_tuning': True},
              'seeds': SEEDS, 'data_split': 'development-saved-features', 'outcome': 'completed',
              'duration_seconds': time.monotonic()-start, 'input_sha256': old.EXPECTED,
              'script_sha256': old.sha(Path(__file__)), 'plan_sha256': old.sha(plan),
              'dependency_sha256': old.sha(Path(old.__file__)), 'numpy_version': np.__version__,
              'label_limitation': 'Agent topic labels; correlated pairs; no human assessment or population claims',
              'parent_failed_rows': [r['id'] for r in index.values() if r.get('status') == 'failed' or r.get('errors')],
              'outputs': {p.name: old.sha(p) for p in out.iterdir()}}
    (out/'run.json').write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: {a: v[a]['auc'] for a in ('C0','C1')} for k,v in summaries.items()}))


if __name__ == '__main__':
    main()
