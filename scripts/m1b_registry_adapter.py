"""Layout-only bridge to the byte-frozen round-3 evaluator.

No thresholds, distances, pointer decoding or scientific classifications live here.
Each invocation preserves a separate scorer attempt, including its logs.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def journal(out):
    path = Path(out) / 'outputs/journal.jsonl'
    return {r['id']: r for line in path.read_text(encoding='utf-8').splitlines() if line.strip()
            for r in [json.loads(line)]}


def source_ids(sources):
    return [int(s['source_id']) if isinstance(s, dict) else int(s) for s in sources]


def link(source, target):
    source, target = Path(source).resolve(), Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    os.link(source, target)


def evaluate(out, plan, sources):
    out = Path(out).resolve()
    rows = journal(out)
    attempt = out / 'metrics' / ('frozen-scorer-' + str(time.time_ns()))
    fresh, canon = attempt / 'fresh', attempt / 'canonical'
    fresh.mkdir(parents=True)
    canon.mkdir()
    index, pointers = {}, []
    aliases = {}
    for rid, row in rows.items():
        if row.get('outcome') != 'completed' or not row.get('image'):
            continue
        parts = rid.split(':')
        target = None
        if parts[0] == 'canon':
            target = canon / f'coco-{parts[1]}-rgb512.png'
        elif parts[0] == 'embed':
            target = fresh / parts[1] / 'supplier-attempt1/F5-bootstrap.png'
        elif parts[0] == 't3':
            _, model, sid, strength, seed, arm = parts
            target = fresh / f'{model}-{sid}-{strength}-{seed}-{"f5-r2" if arm == "C1" else "C0"}-attempt1.png'
            if arm == 'C1':
                native = rows.get(f'native:{rid}:qim-pilot-owner-alpha', {})
                if isinstance(native.get('pointer_recovered'), bool):
                    pointers.append(dict(id=f'{model}:{sid}:{strength}:{seed}:f5-r2',
                                         pointer=dict(recovered=native['pointer_recovered'])))
        elif parts[0] == 'near':
            target = canon / f'{parts[1]}-{parts[2]}-rgb512.png'
        elif parts[0] == 't4':
            target = fresh / f'T4-evaluation-{row["donor_id"]}-{row["recipient_id"]}-{row["scale"]}.png'
        if target is not None:
            link(row['image'], target)
            aliases[rid] = str(target)
    for rid, path in aliases.items():
        descriptor = rows.get('descriptor:' + rid, {})
        cache = descriptor.get('cache')
        if descriptor.get('outcome') == 'completed' and cache:
            index[path] = dict(cache=str(Path(cache).resolve()))
    (attempt / 'descriptor-index.json').write_text(json.dumps(index, indent=2))
    (attempt / 'pointer-scores.json').write_text(json.dumps(dict(positives_and_C0=pointers), indent=2))
    frozen = plan.get('frozen') or plan.get('frozen_thresholds')
    if isinstance(frozen, dict):
        frozen = frozen.get('path')
    if not frozen:
        raise ValueError('plan must pin frozen threshold file')
    command = [sys.executable, str(ROOT / 'scripts/claude_round3_two_factor.py'), '--mode', 'evaluate',
               '--frozen', str(frozen), '--output-dir', str(attempt / 'scoring'),
               '--fresh-dir', str(fresh), '--canonical-dir', str(canon), '--index', str(attempt / 'descriptor-index.json'),
               '--pointer-scores', str(attempt / 'pointer-scores.json'), '--t4-glob', str(fresh / 'T4-*.png'),
               '--sources', *map(str, source_ids(sources)), '--near', *map(str, plan.get('near_pair_ids', [])),
               '--seeds', *map(str, plan.get('seeds', [15, 16, 17])),
               '--sibling-seeds', *map(str, plan.get('sibling_seeds', range(21, 33)))]
    (attempt / 'command.json').write_text(json.dumps(command, indent=2))
    with (attempt / 'stdout.log').open('w') as stdout, (attempt / 'stderr.log').open('w') as stderr:
        subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, check=True)
    return json.loads((attempt / 'scoring/run.json').read_text()), attempt
