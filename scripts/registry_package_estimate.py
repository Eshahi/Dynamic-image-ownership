"""Estimate package resources from completed development receipts, never held-out pixels."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import shutil


def estimate(run, reproduction):
    run = Path(run)
    state = json.loads((run / 'outputs/run.json').read_text())
    if state['data_split'] != 'development' or state['outcome'] != 'completed':
        raise ValueError('Completed development rehearsal required')
    rows = [json.loads(line) for line in (run / 'outputs/journal.jsonl').read_text().splitlines()]
    sources = {r['source_id'] for r in rows if r['id'].startswith('canon:')}
    phases = defaultdict(lambda: dict(units=0, seconds=0.0))
    for row in rows:
        phase = row['id'].split(':')[0]
        phases[phase]['units'] += 1
        phases[phase]['seconds'] += row.get('duration_seconds', 0)
    # Scale source-dependent work linearly; keep the small near panel overhead
    # in this conservative source-scaled estimate too.
    linear = sum(p['seconds'] for p in phases.values()) * 300 / len(sources)
    historical = json.loads(Path(reproduction).read_text())
    if len(historical['evaluation_sources']) != 40:
        raise ValueError('Expected frozen 40-source development reproduction')
    # Scorer loops over 38 suspects per source and all other records. This
    # quadratic upper extrapolation also scales its fixed synthetic overhead.
    scoring = historical['duration_seconds'] * (300 * 299) / (40 * 39)
    predicted = linear + scoring
    inode_sizes = {}
    for path in run.rglob('*'):
        if path.is_file():
            st = path.stat()
            inode_sizes[(st.st_dev, st.st_ino)] = st.st_size
    bytes_used = sum(inode_sizes.values())
    # Include 3 GiB bounded footage acquisition and 25% operating margin.
    disk = bytes_used * 300 / len(sources) * 1.25 + 3 * 2**30
    descriptors = [Path(r['cache']) for r in rows if r['id'].startswith('descriptor:embed:') and r.get('cache')]
    registry_bytes = sum(p.stat().st_size for p in descriptors) * 300 / len(sources)
    return dict(basis='development only; phase-linear plus conservative quadratic scorer extrapolation',
                run=str(run), source_n=len(sources), phases=dict(phases),
                measured_compute_seconds=state['duration_seconds'],
                full_linear_seconds=linear, full_scoring_seconds=scoring,
                full_estimate_hours=predicted / 3600, planning_hours_with_25pct_margin=predicted * 1.25 / 3600,
                exceeds_16_hours=predicted * 1.25 > 16 * 3600,
                unique_rehearsal_bytes=bytes_used, full_disk_gib=disk / 2**30,
                registry_descriptor_mib=registry_bytes / 2**20,
                free_disk_gib=shutil.disk_usage(run).free / 2**30,
                limitations=['Eight development sources may not represent DIV2K costs.',
                    'Scorer extrapolation scales fixed overhead and is deliberately conservative.',
                    'Reboot downtime and an interrupted unfinished unit add elapsed time.',
                    'Acronis automatic reboot at 07:04 on 2026-10-17 reported by user.',
                    'Model weights are referenced in place; no copied weights in estimate.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--reproduction', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = estimate(args.run, args.reproduction)
    Path(args.out).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
