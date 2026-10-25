"""Research-only schema inspection of existing JSONL; no project/ML imports."""
import collections
import hashlib
import json
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
JOURNAL = MAIN / '.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl'
OUT = Path(__file__).resolve().parent
rows = {}
states = collections.Counter()
line_count = 0
sha = hashlib.sha256()
with JOURNAL.open('rb') as f:
    for line in f:
        sha.update(line)
        if not line.strip():
            continue
        row = json.loads(line)
        line_count += 1
        states[str(row.get('status'))] += 1
        rows[row['id']] = row

cells = collections.Counter()
final_states = collections.Counter()
examples = {}
keys = collections.Counter()
for row in rows.values():
    final_states[str(row.get('status'))] += 1
    cells[(str(row.get('channel')), str(row.get('strength')), str(row.get('arm')))] += 1
    keys.update(row.keys())
    key = str(row.get('channel')) + '/' + str(row.get('arm')) + '/' + str(row.get('status'))
    if key not in examples:
        examples[key] = row

result = {
    'hypotheses_commit': '5cc20912a7120544e5ec4ece3d4a04bc5b4c9921',
    'input': str(JOURNAL), 'sha256': sha.hexdigest(),
    'lines': line_count, 'unique_ids': len(rows), 'all_states': dict(states),
    'final_states': dict(final_states), 'row_keys': dict(keys),
    'cells': [{'channel': k[0], 'strength': k[1], 'arm': k[2], 'count': v} for k, v in sorted(cells.items())],
    'examples': examples,
}
(OUT / 'schema-inventory.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps({k: result[k] for k in ('lines', 'unique_ids', 'final_states', 'row_keys')}, indent=2))
print('Representative records retained in schema-inventory.json; no image file opened.')
