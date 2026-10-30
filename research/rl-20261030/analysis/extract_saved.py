"""Numeric-only normalization of whitelisted development journals, stdlib only.

No image is opened. Stage2b already contains Stage2a; do not concatenate them.
Retain the last journal state per ID, including blocked/missing outcomes.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path

MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASE = MAIN / '.thesis-build/dev-runs'
OUT = Path(__file__).resolve().parent
FILES = {
    'stage2_union': BASE / '20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl',
    'phase_a_native': BASE / '20261026-0855-et-final-phase-a/results/native.jsonl',
    'phase_a_detect': BASE / '20261026-0855-et-final-phase-a/results/detect.jsonl',
}
ARMS = ('f5-r2', 'v5-r3', 'wam', 'vine-r')
CHANNELS = ('clean', 'R0', 'R1', 'R3', 'R1-rinse', 'R1-smooth', 'R1-mode')
OWNER = 'qim-pilot-owner-alpha'
inventory = {}

def read(key):
    path = FILES[key]
    h = hashlib.sha256()
    rows = {}
    events = collections.Counter()
    with path.open('rb') as stream:
        for line in stream:
            h.update(line)
            r = json.loads(line)
            rows[r['id']] = r
            events[r.get('status', 'missing')] += 1
    inventory[key] = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': path.stat().st_size,
        'events': dict(events), 'last_state_ids': len(rows),
        'last_statuses': dict(collections.Counter(r.get('status') for r in rows.values()))}
    return rows

def finite_sub(a, b):
    return a-b if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None

def normalize(cohort, r, calls):
    arm = r['arm']
    call = calls.get(OWNER, {})
    raw = call.get('raw', {})
    ep = call.get('endpoints', {})
    present = call.get('presence', {})
    ok = r.get('status') == 'ok' and call.get('status') == 'ok'
    internal = arm in ('f5-r2', 'v5-r3')
    out = {'cohort': cohort, 'row_id': r['id'], 'source': r.get('source_id', r.get('source')),
        'arm': arm, 'cell': r.get('cell') or (r['channel'] if r.get('strength') is None else f"{r['channel']}-{r['strength']}"),
        'seed': r.get('seed'), 'row_status': r.get('status'), 'ok': ok,
        'C': ep.get('C') if internal and ok else None,
        'J': ep.get('J') if internal and ok else None,
        'presence': present.get('present') if not internal and ok else None,
        'success': ep.get('C') if internal and ok else present.get('present') if ok else None,
        'exact_message': raw.get('exact_message_match') if not internal and ok else None,
        'endpoint_label': 'content-compatible C' if internal else 'message-presence P (no content binding)',
        'strict_quality': r.get('strict_quality') if r.get('channel') == 'clean' else None,
        'quality': {k: (r.get('distortion') or {}).get(k) for k in ('psnr_db','ssim_rgb','lpips')},
        'generation_seconds': r.get('generation_seconds'),
        'payload_bits': 64 if internal else present.get('bits'),
        'embedding_features': {k: (r.get('embedding_report') or {}).get(k)
            for k in ('margin_median', 'margin_min', 'negative_chips', 'rgb_psnr_db')},
    }
    for channel in ('semantic', 'instance'):
        value = raw.get(channel, {})
        for name in ('score', 'threshold', 'decoded_score', 'decoded_threshold', 'recomputed_score',
                     'recomputed_threshold', 'read', 'found', 'content_match', 'code_distance',
                     'corrected_distance', 'soft_distance'):
            out[f'{channel}_{name}'] = value.get(name) if ok else None
        for prefix in ('', 'decoded_', 'recomputed_'):
            out[f'{channel}_{prefix}margin'] = finite_sub(out[f'{channel}_{prefix}score'], out[f'{channel}_{prefix}threshold'])
    out['presence_margin'] = finite_sub(present.get('matches'), present.get('threshold')) if ok else None
    out['margin'] = out['semantic_decoded_margin'] if internal else out['presence_margin']
    out['margin_units'] = 'decoded normalized correlation minus threshold' if internal else 'matching bits minus threshold'
    return out

stage = read('stage2_union')
records = []
for r in stage.values():
    if r.get('arm') in ARMS and r.get('channel') in CHANNELS:
        records.append(normalize('stage2_union', r, r.get('detections', {}).get(r['arm'], {})))
native = read('phase_a_native')
det = read('phase_a_detect')
det_by_item = {r['item']: r for r in det.values() if r.get('item', '').startswith('native:') and r.get('arm') in ARMS}
for r in native.values():
    if r.get('kind') == 'native' and r.get('arm') in ARMS:
        d = det_by_item.get(r['id'], {})
        records.append(normalize('phase_a', r, d.get('calls', {})))

# Lightweight semantic checks validate extraction, not retained numerical science.
assert len({(r['cohort'], r['row_id']) for r in records}) == len(records)
for r in records:
    if r['arm'] in ('f5-r2', 'v5-r3') and r['ok']:
        assert r['C'] == bool(r['semantic_read'] and r['semantic_content_match'])
        assert r['J'] is not True or r['C'] is True
    if not r['ok']:
        assert r['margin'] is None and r['success'] is None
records.sort(key=lambda r: (r['cohort'], r['cell'], r['arm'], r['source'], -1 if r['seed'] is None else r['seed']))
with (OUT / 'dev-records.jsonl').open('w', encoding='utf-8', newline='\n') as stream:
    for r in records:
        stream.write(json.dumps(r, sort_keys=True, allow_nan=False) + '\n')
normalized_bytes = (OUT / 'dev-records.jsonl').read_bytes()
(OUT / 'dev-records.jsonl.gz').write_bytes(gzip.compress(normalized_bytes, mtime=0))
inventory['output'] = {'records': len(records), 'cohorts': dict(collections.Counter(r['cohort'] for r in records)),
    'normalized_sha256': hashlib.sha256(normalized_bytes).hexdigest(),
    'cells': sorted({r['cell'] for r in records}),
    'seeds': {c: sorted({r['seed'] for r in records if r['cohort']==c and r['seed'] is not None}) for c in ('stage2_union','phase_a')},
    'sources_per_cohort': {c: len({r['source'] for r in records if r['cohort']==c}) for c in ('stage2_union','phase_a')},
    'missing_by_cohort': dict(collections.Counter(r['cohort'] for r in records if not r['ok']))}
inventory['limitations'] = ['PHASE_B_JOURNALS=off; no Phase B journal accessed',
    'No image, TIFS run, reserve identifier or Stage C identifier opened',
    'Last-state development journals; earlier event statuses retained in inventory, no failed run deleted',
    'WAM/VINE presence is not C/J; across-arm oracle has heterogeneous endpoints',
    'Phase A and stage2 are separate cohorts of repeated development sources with different kernel/seed conditions']
(OUT / 'data-inventory.json').write_text(json.dumps(inventory, indent=2, allow_nan=False)+'\n', encoding='utf-8')
print(json.dumps(inventory['output']))
