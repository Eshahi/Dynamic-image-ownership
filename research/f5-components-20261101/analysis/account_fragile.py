"""Saved-data supplement: distinguish fragile F/H from semantic exact-q J."""
import csv
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time
from collections import defaultdict

START = time.monotonic()
API = runpy.run_path(str(Path(__file__).with_name('account_saved_development.py')))
RD, ROOT = API['RD'], API['ROOT']
OUT = RD / 'results/wp1-fragile'
if OUT.exists():
    raise FileExistsError(OUT)
data, provenance = {}, {}
for name in ('stage2', 'detect'):
    data[name], provenance[name] = API['load'](name)
groups = defaultdict(dict)


def add(study, cell, arm, source, seed, call, location):
    if not call or call.get('status') != 'ok':
        return
    ep, raw = call['endpoints'], call['raw']
    assert ep['J'] == bool(ep['Q'] and raw['semantic']['content_match'])
    z = {k: bool(ep[k]) for k in ('C', 'J', 'Q', 'H', 'D', 'F', 'A')}
    z.update(instance_found=bool(raw['instance']['found']), instance_read=bool(raw['instance']['read']),
             semantic_found=bool(raw['semantic']['found']), location=location)
    identity = (source, seed)
    assert identity not in groups[(study, cell, arm)]
    groups[(study, cell, arm)][identity] = z


for _, (line, r) in data['stage2'].items():
    arm = r['arm']
    if arm not in API['ARMS'] or r['status'] != 'ok':
        continue
    cell = r['channel'] if r['strength'] is None else f"{r['channel']}-{r['strength']}"
    add('stage2-union', cell, arm, r['source_id'], r['seed'], r.get('detections', {}).get(arm, {}).get(API['ALPHA']), f'stage2:{line}')
for _, (line, r) in data['detect'].items():
    if r['method'] not in API['ARMS'] or r['arm'] != r['method'] or r['status'] != 'ok':
        continue
    parts = r['item'].split(':')
    cell, seed = (parts[1], int(parts[3])) if parts[0] == 'native' else (parts[0], None)
    assert parts[0] in ('native', 'ctrlB-codec')
    add('phase-a', cell, r['method'], r['source'], seed, r['calls'].get(API['ALPHA']), f'detect:{line}')

out, detail = [], []
with (RD / 'results/wp1-accounting/loss-cells.csv').open(encoding='utf-8') as handle:
    for base in csv.DictReader(handle):
        group = groups[(base['study'], base['cell'], base['arm'])]
        required = 1 if int(base['seeds_per_source']) == 1 else 2
        per_source = defaultdict(list)
        for (source, seed), z in group.items():
            per_source[source].append(z)
        row = {k: base[k] for k in ('study', 'cell', 'arm', 'sources', 'expected_calls', 'calls_M')}
        assert len(group) + int(base['calls_M']) == int(base['expected_calls'])
        for metric in ('C', 'J', 'Q', 'H', 'D', 'F', 'A', 'instance_found', 'instance_read', 'semantic_found'):
            row[metric + '_calls'] = sum(z[metric] for z in group.values())
            row[metric + '_sources'] = sum(sum(z[metric] for z in zz) >= required for zz in per_source.values())
        assert row['C_sources'] == int(base['C_sources']) and row['J_sources'] == int(base['J_sources'])
        out.append(row)
        for source, zz in sorted(per_source.items()):
            detail.append({'study': base['study'], 'cell': base['cell'], 'arm': base['arm'], 'source': source,
                           **{k: sum(z[k] for z in zz) for k in ('C', 'J', 'Q', 'H', 'D', 'F', 'A', 'instance_found', 'instance_read')},
                           'locations': ';'.join(z['location'] for z in zz)})
OUT.mkdir(parents=True)
for name, rows in [('fragile-cells.csv', out), ('fragile-sources.csv', detail)]:
    with (OUT / name).open('w', encoding='utf-8', newline='') as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = ['# Fragile-tier and exact-code endpoint supplement', '',
      'SOURCE: scripts/m1b_e3_s1_analysis.py:70-84 defines J = exact decoded q AND semantic content_match; H = exact decoded h; D = exact q AND exact h; F = both_match; A = either tier found. J alone says nothing about fragile-tier survival. This supplement resolves the endpoint ambiguity in the Gate-1 finding-3 challenge.', '',
      'MEASURED: Only saved marked/self-owner development calls. Missing calls remain unsuccessful; each source denominator is 60. Original C/J reproduced as assertions. Line locators and input hashes are in the CSV/provenance files.', '',
      '| Study | Cell | Arm | C | J | H | F | A | Instance found | Instance read |',
      '|---|---|---|---|---|---|---|---|---|---|']
for r in out:
    md.append('| ' + ' | '.join([r['study'], r['cell'], r['arm']] + [str(r[k+'_sources']) for k in ('C','J','H','F','A','instance_found','instance_read')]) + ' |')
(OUT / 'REPORT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
meta = {'label': 'MEASURED descriptive fragile supplement', 'inputs': provenance,
        'command': [sys.executable, '-I', str(Path(__file__).resolve())],
        'commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256': hashlib.sha256(Path(__file__).with_name('account_saved_development.py').read_bytes()).hexdigest(),
        'phase_b_journals': 'off', 'seconds': time.monotonic()-START,
        'outputs_sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir())}}
(OUT/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT),'seconds':meta['seconds'],'cells':len(out)}))
