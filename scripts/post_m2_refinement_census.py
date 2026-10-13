"""Exploratory development census of retained E3-S1 initializer/final pixels.

This inspects twelve already-seen development sources, not confirmatory data.
Pixel identity can establish a zero effect of the retained refinement/selector
on those outputs without model inference. Nonidentity does not establish benefit.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498,
       177015, 190676, 468505, 499768)
STAGE_B = MAIN / '.thesis-build/dev-runs/20261010-1522-e3-s1-stage-b'
PROTOCOL = ROOT / 'research/journal-upgrade-20261009/post-m2-fair-comparison-protocol.md'
INDEX = ROOT / 'research/journal-upgrade-20261009/e3-s1-external-index.json'
SPLITS = Path('C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5/data/splits.csv')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rgb(path):
    with Image.open(path) as image:
        if image.mode != 'RGB' or image.size != (512, 512):
            raise ValueError(f'Expected retained RGB8 512x512 image: {path}')
        return np.asarray(image, dtype=np.uint8).copy()


def word(value):
    return int(value, 16) if isinstance(value, str) else int(value)


def difference(a, b):
    delta = b.astype(np.int16) - a.astype(np.int16)
    return dict(identical_pixels=bool(np.array_equal(a, b)),
        changed_channel_values=int(np.count_nonzero(delta)),
        changed_spatial_pixels=int(np.count_nonzero(np.any(delta != 0, axis=2))),
        mse_rgb8=float(np.mean(delta.astype(np.float64)**2)),
        max_absolute_rgb8_change=int(np.abs(delta).max()))


def qualification(value):
    return {k: value[k] for k in ('metrics', 'q_exact', 'h_exact', 'both_match',
                                 'strict_quality', 'qualified')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    if not PROTOCOL.is_file():
        raise ValueError('Write the bounded protocol before observing the census')
    parent = read(STAGE_B / 'run.json')
    if parent.get('data_split') != 'development' or not parent.get('commit'):
        raise ValueError('Retained development provenance required')
    rows = [json.loads(line) for line in (STAGE_B / 'rows.jsonl').read_text(
        encoding='utf-8-sig').splitlines() if line.strip()]
    if tuple(r['source_id'] for r in rows) != IDS:
        raise ValueError('Fixed twelve-source inventory differs')
    heldout_ids = set()
    for entry in read(INDEX)['entries']:
        match = re.fullmatch(r'ms-coco:coco-2017:val2017:(\d+)', entry['source_uid'])
        if not match:
            raise ValueError('Unrecognized held-out COCO source UID')
        heldout_ids.add(int(match.group(1)))
    if set(IDS) & heldout_ids:
        raise ValueError('Development and completed held-out IDs overlap')
    with SPLITS.open(encoding='utf-8-sig', newline='') as handle:
        for source in csv.DictReader(handle):
            if (source['domain'] == 'ms-coco' and
                source['source_id'].isdigit() and int(source['source_id']) in IDS and
                source['study_split'] in ('validation', 'test')):
                raise ValueError('Development source is in a historical held-out split')
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    record = dict(schema='post-m2-refinement-census-v1',
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                      text=True).strip(),
        command=sys.argv, data_split='development', sources=list(IDS), seeds=[],
        started_at_utc=datetime.now(timezone.utc).isoformat(),
        started_unix=time.time(), wall_cap_seconds=2700,
        usd=0, outcome='running',
        config=dict(protocol=str(PROTOCOL), protocol_sha256=hashlib.sha256(
            PROTOCOL.read_bytes()).hexdigest(), source_run=str(STAGE_B),
            source_commit=parent['commit'], heldout_metadata_guard=str(INDEX),
            historical_split_guard=str(SPLITS),
            no_model_inference=True, adaptive_seen_sources=True), rows=[])

    def save():
        record['duration_seconds'] = time.monotonic() - started
        (out / 'run.json').write_text(json.dumps(record, indent=2,
            allow_nan=False) + '\n', encoding='utf-8')

    save()
    try:
        for row in rows:
            writer = row['writer']
            targets = writer['supplied_targets']
            if any(word(row['payload'][k]) != word(targets[k]) for k in ('q', 'h')):
                raise ValueError('Saved initializer/final payload target mismatch')
            initial_path = Path(writer['start_image'])
            state_path = Path(writer['final_state_image'])
            final_path = Path(row['conditions']['clean']['image'])
            if final_path.resolve() != Path(writer['final_image']).resolve():
                raise ValueError('Selected clean image differs from writer final path')
            initial, state, final = rgb(initial_path), rgb(state_path), rgb(final_path)
            equal = bool(np.array_equal(initial, final))
            record['rows'].append(dict(source_id=row['source_id'],
                source_image=row['source_image'], initializer=str(initial_path),
                state=str(state_path), inherited_provenance=row['provenance'],
                final=str(final_path), payload=row['payload'], identical_pixels=equal,
                initializer_to_state=difference(initial, state),
                state_to_final=difference(state, final),
                initializer_to_final=difference(initial, final),
                recorded_update_status=writer['update_status'],
                recorded_accepted_updates=writer['accepted_updates'],
                recorded_quality_branch=writer['quality_branch'],
                recorded_initial_qualification=qualification(writer['initial_qualification']),
                recorded_final_qualification=qualification(writer['final_qualification']),
                recorded_clean_endpoints=row['conditions']['clean']['endpoints'],
                recorded_refinement_seconds=writer['refinement_seconds']))
            save()
        identical = sum(r['identical_pixels'] for r in record['rows'])
        record['summary'] = dict(planned_sources=12, observed_sources=len(record['rows']),
            identical_pairs=identical, changed_pairs=12-identical,
            initializer_state_identical_pairs=sum(r['initializer_to_state']['identical_pixels'] for r in record['rows']),
            state_final_identical_pairs=sum(r['state_to_final']['identical_pixels'] for r in record['rows']),
            recorded_refinement_seconds=sum(r['recorded_refinement_seconds'] for r in record['rows']),
            any_new_detection_or_attack_observation=False,
            refinement_benefit_established=False,
            next_action=('stop_gpu_refinement_comparison_identical_outputs'
                         if identical == 12 else 'evaluate_fixed_paired_arms_on_seeds_6_7_8'),
            interpretation=('Exact output equality establishes zero output-mediated refinement '
                'effect only on these retained sources; nonidentity requires the planned '
                'paired evaluation. Reused development evidence is exploratory.'))
        record['outcome'] = 'completed'
    except Exception as exc:
        record['outcome'] = 'failed'
        record['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        save()
    print(json.dumps(record['summary']))


if __name__ == '__main__':
    main()
