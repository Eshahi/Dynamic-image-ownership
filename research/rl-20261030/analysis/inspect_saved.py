"""Read only explicitly allowed development JSONL; print schema/counts, not arrays/images."""
import collections
import json
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASE = MAIN / '.thesis-build/dev-runs'
FILES = [
    BASE / '20261024-1431-encoder-transfer-stage2a/results/stage2a-full/rows.jsonl',
    BASE / '20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl',
    BASE / '20261026-0855-et-final-phase-a/results/detect.jsonl',
    BASE / '20261026-0855-et-final-phase-a/results/native.jsonl',
    BASE / '20261026-0855-et-final-phase-a/results/mechanism.jsonl',
]

def small(x, depth=0):
    if isinstance(x, dict):
        if depth > 3:
            return list(x)
        return {k: small(v, depth + 1) for k, v in x.items() if k not in ('output', 'f0', 'chips', 'path')}
    if isinstance(x, list):
        return {'list_length': len(x)}
    return x

for path in FILES:
    rows = {}
    statuses = collections.Counter()
    examples = {}
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            statuses[row.get('status')] += 1
            rows[row['id']] = row
            tag = (row.get('status'), row.get('arm'), row.get('kind'))
            if tag not in examples and row.get('arm') in ('f5-r2', 'v5-r3', 'wam', 'vine-r'):
                examples[tag] = small(row)
    print(json.dumps({'file': str(path), 'lines': sum(statuses.values()), 'unique_ids': len(rows),
        'statuses': dict(statuses), 'arms': dict(collections.Counter(r.get('arm') for r in rows.values())),
        'channels': dict(collections.Counter(r.get('channel', r.get('cell')) for r in rows.values())),
        'key_shapes': [list(r) for r in list(rows.values())[:2]],
        'examples': list(examples.values())[:3]}, allow_nan=False))
