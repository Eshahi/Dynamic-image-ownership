"""Frozen E3 source-blind T3 negative completion on retained pixels only."""
from __future__ import annotations

import time
STARTED = time.monotonic()  # Inclusive of imports, startup and finalization.
import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_e3_threat_supplement import read, write, working_set, full, IDS, OWNERS, ALPHA

CAP, GPU_CAP, RAM_CAP = 900., 10 * 1024**3, 16 * 1024**3
CONFIG = dict(cap_seconds=CAP, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
    detector='E1-BCH59-A', semantic_views=7, binding='soft', binding_mode='combined',
    roster_size=1, thresholds='unchanged', generation=False, pixel_edits=False,
    usd=0, planned_new_calls=340)


def identity(row):
    return row['arm'], int(row['source_id']), float(row['strength']), int(row['seed'])


def name(row):
    return '|'.join(map(str, identity(row)))


def negative_owners(row):
    return OWNERS if row['arm'] == 'shared_C0' else OWNERS[1:]


def predicates(call):
    if not full(call):
        raise ValueError('Raw native full call required')
    if (call['owners_tested'] != 1 or call['binding_mode'] != 'combined'
            or call.get('binding') != 'soft' or call.get('method') != 'E1-BCH59-A'):
        raise ValueError('Frozen independent roster-one combined E3 call required')
    return dict(A=bool(call['semantic']['found'] or call['instance']['found']),
        S=bool(call['semantic']['found'] and call['semantic']['content_match']),
        F=call['outcome'] == 'both_match')


def parent_panel(folder):
    run = read(folder / 'run.json')
    rows = [json.loads(s) for s in (folder / 'rows.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    expected = {(arm, sid, strength, seed) for arm in ('shared_C0', 'candidate_C1')
                for sid in IDS for strength in (.1, .2) for seed in (0, 1, 2)}
    config = run.get('config', {})
    if (run.get('schema') != 'journal-e3-bch-quality-select-stage-b-v1'
            or run.get('data_split') != 'development' or run.get('usd') != 0
            or run.get('outcome') != 'completed' or not run.get('e3_stage_a_dir')
            or config.get('detector') != 'E1-BCH59-A'
            or config.get('quality_rule') != 'retain_if_strict_else_contract_once'
            or config.get('factor') != .8 or config.get('semantic_views') != 7
            or config.get('binding') != 'soft' or config.get('roster_size') != 1
            or len(rows) != 144 or {identity(r) for r in rows} != expected):
        raise ValueError('Frozen complete E3 T3 parent identity/config panel required')
    counts = {}
    for row in rows:
        counts[row['arm'], row['status']] = counts.get((row['arm'], row['status']), 0) + 1
        calls = row.get('calls', {})
        wanted = {ALPHA} if row['arm'] == 'shared_C0' else set(OWNERS[:2])
        if row['status'] == 'ok':
            if set(calls) != wanted or not Path(row['image']).is_file():
                raise ValueError('Retained raw calls or exact saved image unavailable: ' + name(row))
            for owner, call in calls.items():
                predicates(call)
                if call['owner_id'] != owner:
                    raise ValueError('Parent call owner mismatch')
        elif row['status'] != 'safety_blocked' or calls or row.get('image'):
            raise ValueError('Unexpected parent failure or available blocked pixels')
    if counts != {('shared_C0', 'ok'): 66, ('candidate_C1', 'ok'): 71,
                  ('shared_C0', 'safety_blocked'): 6, ('candidate_C1', 'safety_blocked'): 1}:
        raise ValueError('Frozen 137 available / seven blocked image panel required')
    return rows, run


def summarize(rows):
    result = dict(scope='Exploratory E3 T3 negative completion only', m1a_pass=False,
        planned_negative_calls=504, observed_negative_calls=0, negative_A_detections=0,
        existing_calls_reused=0, new_calls=0, genuine_calls=0, blocked_images=[],
        unavailable_negative_calls=[], missing_available_negative_calls=[], cells={},
        interpretation='Repeated-source independent roster-one calls; zero observed negatives with '
        'declared safety-blocked coverage is not universal zero or population FPR. '
        'Strict E3-B remains FAILED_FINAL; broader M1a is assessed separately.')
    for arm, planned in (('shared_C0', 288), ('candidate_C1', 216)):
        cell = dict(planned=planned, observed=0, any_detection=0, positive_identities=[])
        for row in rows:
            if row['arm'] != arm:
                continue
            calls = row.get('calls', {})
            for owner, call in calls.items():
                predicates(call)
                provenance = row['call_provenance'][owner]['kind']
                result['existing_calls_reused'] += provenance == 'reused_full_call'
                result['new_calls'] += provenance == 'new_call'
                result['genuine_calls'] += arm == 'candidate_C1' and owner == ALPHA
            if row['status'] == 'safety_blocked':
                result['blocked_images'].append(name(row))
            for owner in negative_owners(row):
                slot = dict(identity=name(row), owner=owner)
                if owner in calls:
                    value = predicates(calls[owner])['A']
                    cell['observed'] += 1
                    cell['any_detection'] += value
                    if value:
                        cell['positive_identities'].append(slot)
                else:
                    field = 'unavailable_negative_calls' if row['status'] == 'safety_blocked' else 'missing_available_negative_calls'
                    result[field].append(slot)
        result['cells'][arm] = cell
        result['observed_negative_calls'] += cell['observed']
        result['negative_A_detections'] += cell['any_detection']
    result['available_completion'] = (len(rows) == 144 and result['new_calls'] == 340
        and result['existing_calls_reused'] == 208 and result['genuine_calls'] == 71
        and result['observed_negative_calls'] == 477
        and len(result['unavailable_negative_calls']) == 27
        and len(result['blocked_images']) == 7 and not result['missing_available_negative_calls'])
    result['observed_negative_panel_pass'] = result['available_completion'] and not result['negative_A_detections']
    return result


def save_rows(out, rows):
    (out / 'rows.jsonl').write_text(''.join(json.dumps(r, allow_nan=False) + '\n' for r in rows), encoding='utf-8')


def analyze(t3_dir, out):
    """CPU-only aggregate check; no detector recomputation or artifact hashing."""
    parent, _ = parent_panel(t3_dir)
    record = read(out / 'run.json')
    rows = [json.loads(s) for s in (out / 'rows.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    if len(rows) != len(parent) or {identity(r) for r in rows} != {identity(r) for r in parent}:
        raise ValueError('Completion image identity inventory differs')
    original = {identity(r): r for r in parent}
    for row in rows:
        old = original[identity(row)]
        if row.get('image') != old.get('image') or row['source_row'] != old:
            raise ValueError('Retained pixels/raw source row changed')
        if not set(row['calls']).issubset(set(OWNERS)):
            raise ValueError('Unexpected owner call')
        for owner, call in old['calls'].items():
            if row['calls'].get(owner) != call or row['call_provenance'][owner]['kind'] != 'reused_full_call':
                raise ValueError('Existing call changed or not reused once')
        if old['status'] == 'safety_blocked' and (row['status'] != 'safety_blocked' or row['calls']):
            raise ValueError('Blocked observation changed')
        for owner, call in row['calls'].items():
            if call['owner_id'] != owner or (owner not in old['calls'] and
                    (row['call_provenance'][owner]['kind'] != 'new_call' or
                     call['detector_config_id'] != old['calls'][ALPHA]['detector_config_id'])):
                raise ValueError('New call owner/config/provenance differs')
    summary = summarize(rows)
    if record['config'] != CONFIG or summary != read(out / 'summary.json'):
        raise ValueError('Frozen config or aggregate summary differs')
    write(out / 'analysis.json', dict(summary=summary, aggregate_agrees=True,
        outcome=record['outcome'], no_recomputation=True))
    print(json.dumps(summary), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--t3-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--analyze', action='store_true')
    args = parser.parse_args()
    t3_dir, out = args.t3_dir.resolve(), args.output_dir.resolve()
    if args.analyze:
        analyze(t3_dir, out)
        return
    parent, parent_run = parent_panel(t3_dir)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for old in parent:
        row = dict(old, calls=dict(old['calls']), source_row=old,
            call_provenance={owner:dict(kind='reused_full_call', record=str(t3_dir / 'rows.jsonl'),
                identity=name(old)) for owner in old['calls']})
        rows.append(row)
    record = dict(schema='journal-e3-negative-completion-v1', method='E3-BCH59-Q080',
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, config=CONFIG, seeds=[0, 1, 2], strengths=[.1, .2],
        sources=list(IDS), data_split='development', usd=0, outcome='running',
        t3_dir=str(t3_dir), parent_run=parent_run,
        method_label_provenance='Parent raw method frozen_F5 is the retained variable-shadow label bug. '
            'E3 identity follows e3 schema, initializer and authoritative frozen config; raw parent unmodified.')
    ev, active = None, None

    def budget():
        rss, peak = working_set()
        record['peak_ram_bytes'] = max(record.get('peak_ram_bytes', 0), peak)
        gpu = int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes'] = max(record.get('peak_allocated_bytes', 0), gpu)
        if time.monotonic() - STARTED > CAP or gpu > GPU_CAP or max(rss, peak) > RAM_CAP:
            raise RuntimeError('Fixed E3 negative-completion inclusive resource cap exceeded')

    write(out / 'run.json', record)
    save_rows(out, rows)
    try:
        budget()
        import numpy as np
        from PIL import Image
        import torch
        import revised_watermark_v5 as v5
        from journal_vae_probe import Evaluator
        from journal_bch_readout import detect_rgb
        torch.cuda.set_per_process_memory_fraction(GPU_CAP / torch.cuda.get_device_properties(0).total_memory)
        ev = Evaluator()
        stage_a = read(Path(parent_run['e3_stage_a_dir']) / 'run.json')
        if v5.validate_profile(stage_a['config']['profile']) != v5.validate_profile(ev.profile):
            raise ValueError('Pinned E3 profile differs')
        record['environment'] = dict(torch=torch.__version__, gpu=torch.cuda.get_device_name(0))
        budget()
        for row in rows:
            if row['status'] == 'safety_blocked':
                continue
            active = row
            budget()
            with Image.open(row['image']) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('Retained RGB8 512x512 image required')
                rgb = np.asarray(image, dtype=np.uint8).copy()
            features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
            budget()
            missing = [owner for owner in negative_owners(row) if owner not in row['calls']]
            for owner in missing:
                budget()
                call = detect_rgb(rgb, latent, owner, ev.profile, features,
                    binding_mode='combined', roster_size=1, binding='soft')
                predicates(call)
                if call['owner_id'] != owner or call['detector_config_id'] != row['calls'][ALPHA]['detector_config_id']:
                    raise ValueError('New native owner/config identity differs')
                row['calls'][owner] = call
                row['call_provenance'][owner] = dict(kind='new_call', image=row['image'])
                budget()
            save_rows(out, rows)
            print(json.dumps(dict(identity=name(row), added=len(missing))), flush=True)
            active = None
        budget()
        if not summarize(rows)['available_completion']:
            raise ValueError('Expected 340 new / 208 reused calls not complete')
        record['outcome'] = 'completed'
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc())
        if active is not None:
            active.update(status='failed', completion_error=record['error'])
        raise
    finally:
        save_rows(out, rows)
        record['summary'] = summarize(rows)
        for _ in range(2):
            record['duration_seconds'] = time.monotonic() - STARTED
            record['budget_overrun'] = record['duration_seconds'] > CAP
            if record['budget_overrun']:
                record['outcome'] = 'failed'
            write(out / 'summary.json', record['summary'])
            write(out / 'run.json', record)


if __name__ == '__main__':
    main()
