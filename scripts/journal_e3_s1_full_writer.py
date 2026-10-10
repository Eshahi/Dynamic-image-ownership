"""Conditional E3-S1 Stage B: fixed twelve development sources, no T3 promotion.

Scientific supplier/writer/readout routines are imported unchanged. Stage A and
unchanged C0 observations are reused once; failure rows remain in the inventory.
"""
from __future__ import annotations

import time
STARTED = time.monotonic()  # Includes imports, loading, failures and finalization.
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_e3_threat_supplement import MAIN, IDS, OWNERS, ALPHA, read, write, working_set, full
from journal_bch_analysis import endpoint, CONDITIONS
from journal_e3_s1_analysis import quality

A_IDS = (6012, 147498)
CAP, GPU_CAP, RAM_CAP = 2700., 10 * 1024**3, 16 * 1024**3
COMPOSITION = MAIN / '.thesis-build/dev-runs/20261010-1417-e3-quality-composition'
CONTROLS = MAIN / '.thesis-build/dev-runs/20261010-1433-e3-threat-supplement'
SCHEMA = 'journal-e3-s1-stage-b-v1'
METHOD = 'E3-S1+E3-BCH59-Q080'


def rows_at(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines()
            if line.strip()]


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def config_base():
    return dict(cap_seconds=CAP, gpu_cap_bytes=GPU_CAP, ram_cap_bytes=RAM_CAP,
        owner=ALPHA, strengths=[.1, .2], semantic_views=7, binding='soft', roster_size=1,
        method_contract='research/journal-upgrade-20261009/e3-freeze-design.md',
        protocol='research/journal-upgrade-20261009/e3-s1-full-development.md',
        no_retry=True, source_order=list(IDS), new_constructions=10)


def summarize(rows):
    """Recompute endpoints from calls, keeping failures in fixed denominators."""
    issues = []
    counts = dict(strict_clean_quality=0, clean_exact_q_h_both_match=0,
        clean_wrong_owner_calls=0, clean_wrong_owner_any=0,
        vae_beta_calls=0, vae_beta_any=0, c0_clean_calls=0, c0_clean_any=0,
        c0_vae_alpha_calls=0, c0_vae_alpha_any=0,
        supplier_ok=0, writer_ok=0,
        vae={name:dict(S=0, Q=0, J=0) for name in CONDITIONS[1:]})
    complete = len(rows) == 12 and [r.get('source_id') for r in rows] == list(IDS)
    for row in rows:
        sid, payload = row.get('source_id'), row.get('payload')
        counts['supplier_ok'] += row.get('supplier', {}).get('status') == 'ok'
        counts['writer_ok'] += (row.get('writer', {}).get('status') == 'ok' and
                                row.get('writer', {}).get('admitted') is True)
        complete &= row.get('status') == 'ok' and set(row.get('conditions', {})) == set(CONDITIONS)
        try:
            if not payload or not {'q', 'h'} <= set(payload):
                raise ValueError('Missing fixed supplier payload')
            for name in CONDITIONS:
                cell = row.get('conditions', {}).get(name, {})
                expected = OWNERS if name == 'clean' else OWNERS[:2]
                if set(cell.get('calls', {})) != set(expected):
                    raise ValueError(f'{name}: incomplete owner calls')
                derived = {}
                for owner in expected:
                    call = cell['calls'][owner]
                    if not full(call) or call['owner_id'] != owner:
                        raise ValueError(f'{name}: incomplete/mismatched native call')
                    derived[owner] = endpoint(call, payload if owner == ALPHA else None)
                if derived != cell.get('endpoints'):
                    raise ValueError(f'{name}: recorded endpoint differs from call')
                if not full(cell.get('c0_call')) or cell['c0_call']['owner_id'] != ALPHA:
                    raise ValueError(f'{name}: incomplete C0 alpha call')
                c0 = endpoint(cell['c0_call'])
                if c0 != cell.get('c0_endpoint'):
                    raise ValueError(f'{name}: C0 endpoint differs from call')
                if not cell.get('image') or not cell.get('c0_image') or not cell.get('call_provenance'):
                    raise ValueError(f'{name}: missing image or reuse provenance')
                positive = derived[ALPHA]
                if name == 'clean':
                    q = quality(cell.get('quality_source'))
                    if not q['valid']:
                        raise ValueError('Invalid clean quality metrics')
                    counts['strict_clean_quality'] += q['strict_pass']
                    counts['clean_exact_q_h_both_match'] += bool(positive['Q'] and positive['H'] and positive['F'])
                    counts['clean_wrong_owner_calls'] += 3
                    counts['clean_wrong_owner_any'] += sum(derived[o]['A'] for o in OWNERS[1:])
                else:
                    for key in ('S', 'Q', 'J'):
                        counts['vae'][name][key] += bool(positive[key])
                    counts['vae_beta_calls'] += 1
                    counts['vae_beta_any'] += derived[OWNERS[1]]['A']
                    counts['c0_vae_alpha_calls'] += 1
                    counts['c0_vae_alpha_any'] += c0['A']
            clean_c0 = row.get('c0_clean_all_owners', {})
            if set(clean_c0.get('calls', {})) != set(OWNERS):
                raise ValueError('Incomplete clean C0 four-owner calls')
            ce = {}
            for owner in OWNERS:
                call = clean_c0['calls'][owner]
                if not full(call) or call['owner_id'] != owner:
                    raise ValueError('Incomplete/mismatched clean C0 native call')
                ce[owner] = endpoint(call)
            if ce != clean_c0.get('endpoints') or not clean_c0.get('provenance'):
                raise ValueError('Clean C0 endpoints/provenance invalid')
            counts['c0_clean_calls'] += 4
            counts['c0_clean_any'] += sum(e['A'] for e in ce.values())
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(f'{sid}: {exc}')
            complete = False
    passed = bool(complete and not issues and
        counts['supplier_ok'] == counts['writer_ok'] == counts['strict_clean_quality'] ==
        counts['clean_exact_q_h_both_match'] == 12 and
        all(counts['vae'][name][key] == 12 for name in CONDITIONS[1:] for key in ('S', 'J')) and
        counts['clean_wrong_owner_calls'] == 36 and counts['vae_beta_calls'] == 24 and
        counts['c0_clean_calls'] == 48 and counts['c0_vae_alpha_calls'] == 24 and
        all(counts[key] == 0 for key in ('clean_wrong_owner_any', 'vae_beta_any',
                                        'c0_clean_any', 'c0_vae_alpha_any')))
    return dict(planned_sources=12, observed_sources=len(rows), all_source_cells_complete=bool(complete),
        **counts, screen_pass=passed, issues=issues, m1a_pass=False, t3_evaluated=False,
        scope='Fixed development construction/VAE screen only; Stage A costs separate; T3/T4/T5 pending.')


def validate_stage_b(path):
    """Load finalized scientific B rows for dependent development adapters."""
    path = Path(path).resolve()
    run, rows = read(path / 'run.json'), rows_at(path / 'rows.jsonl')
    wall = read(path / 'parent-wall.json')
    cfg = run.get('config', {})
    if (run.get('schema') != SCHEMA or run.get('method') != METHOD or
        run.get('outcome') != 'completed' or run.get('data_split') != 'development' or
        run.get('usd') != 0 or run.get('seeds') != [0, 1, 2] or
        run.get('sources') != list(IDS) or not run.get('commit') or not run.get('command') or
        any(cfg.get(key) != value for key, value in config_base().items())):
        raise ValueError('Stage B is not a finalized frozen development record')
    analysis = summarize(rows)
    if analysis != run.get('summary') or not analysis['screen_pass'] or run.get('stage_b_pass') is not True:
        raise ValueError('Stage B recorded-call construction/VAE screen does not pass')
    duration, parent = run.get('duration_seconds'), wall.get('parent_inclusive_seconds')
    if not (number(duration) and number(parent) and 0 <= duration <= parent <= CAP and
            wall.get('within_cap') is True and not run.get('budget_overrun')):
        raise ValueError('Stage B lacks finalized parent-inclusive cap evidence')
    for key, cap in (('peak_allocated_bytes', GPU_CAP), ('peak_ram_bytes', RAM_CAP)):
        value = run.get(key)
        if not number(value) or not 0 < value <= cap:
            raise ValueError('Stage B resource peak exceeds frozen cap or is missing')
    _, stage_a_run, _ = require_stage_a(Path(run['ancestry']['stage_a']),
                                      Path(run['ancestry']['stage_a_analysis']))
    if (cfg.get('profile') != stage_a_run.get('config', {}).get('profile') or
            cfg.get('sdxl_revision') != '6f5909a7e596173e25d4e97b07fd19cdf9611c76'):
        raise ValueError('Stage B reader profile or pinned SDXL revision differs from frozen Stage A')
    return rows, run


def require_stage_a(folder, analysis_path):
    folder = folder.resolve()
    run, analysis = read(folder / 'run.json'), read(analysis_path)
    if (run.get('schema') != 'journal-e3-s1-stage-a-v1' or run.get('outcome') != 'completed' or
        run.get('stage_a_pass') is not True or analysis.get('stage_a_pass_recomputed') is not True or
        analysis.get('issues') != [] or analysis.get('discrepancies') != [] or
        Path(analysis.get('run_dir', '')).resolve() != folder or analysis.get('commit') != run.get('commit')):
        raise ValueError('Stage B requires a final passing Stage A and matching issue-free CPU analysis')
    rows = rows_at(folder / 'rows.jsonl')
    if len(rows) != 2 or [r['source_id'] for r in rows] != list(A_IDS):
        raise ValueError('Stage A fixed source inventory is incomplete')
    return rows, run, analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage-a-dir', type=Path, required=True)
    parser.add_argument('--stage-a-analysis', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    arows, arun, aanalysis = require_stage_a(args.stage_a_dir, args.stage_a_analysis)
    inherited = {r['source_id']:r for r in arows}
    c0 = {r['source_id']:r for r in rows_at(COMPOSITION / 'rows.jsonl')}
    clean_c0 = {r['source_id']:r for r in rows_at(CONTROLS / 'rows.jsonl')
                if r.get('axis') == 'clean' and r.get('method') == 'E3' and r.get('control') == 'C0'}
    if set(c0) != set(IDS) or set(clean_c0) != set(IDS):
        raise ValueError('Fixed unchanged C0 inventory missing')
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=False)
    record = dict(schema=SCHEMA, method=METHOD, data_split='development', usd=0,
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, sources=list(IDS), seeds=[0, 1, 2], outcome='running', config=config_base(),
        ancestry=dict(stage_a=str(args.stage_a_dir.resolve()), stage_a_analysis=str(args.stage_a_analysis.resolve()),
            composition=str(COMPOSITION), clean_c0=str(CONTROLS)),
        stage_a_separately_reported_cost=aanalysis['resources'],
        stage_a_commit=arun['commit'], peak_allocated_bytes=0, peak_ram_bytes=0,
        human_admissibility='missing', m1a_pass=False)
    rows, ev = [], None

    def budget():
        rss, peak = working_set()
        record['peak_ram_bytes'] = max(record['peak_ram_bytes'], rss, peak)
        gpu = int(ev.torch.cuda.max_memory_allocated()) if ev else 0
        record['peak_allocated_bytes'] = max(gpu, record['peak_allocated_bytes'])
        if time.monotonic() - STARTED >= CAP or gpu > GPU_CAP or max(rss, peak) > RAM_CAP:
            record['budget_overrun'] = True
            raise RuntimeError('Frozen Stage B inclusive resource cap exceeded')

    def save():
        (out / 'rows.jsonl').write_text(''.join(json.dumps(r, allow_nan=False)+'\n' for r in rows), encoding='utf-8')
        record['summary'] = summarize(rows)
        write(out / 'summary.json', record['summary'])
        record['duration_seconds'] = time.monotonic() - STARTED
        record['stage_b_pass'] = bool(record['outcome'] == 'completed' and
            record['summary']['screen_pass'] and record['duration_seconds'] <= CAP and
            not record.get('budget_overrun'))
        write(out / 'run.json', record)

    try:
        budget(); save()
        import torch
        import diffusers
        from diffusers import AutoencoderKL
        from PIL import Image
        import three_threat_models as models
        from f4_transfer_probe import ASSETS, SOURCES
        from journal_vae_probe import Evaluator, SDXL, SDXL_REV
        from journal_ddim_channel import DifferentiableDDIM
        from journal_readability_probe import load, reconstruct
        from journal_e3_writer import embed, supply_f5
        from journal_bch_readout import detect_rgb
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers required')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP / torch.cuda.get_device_properties(0).total_memory)
        ev = Evaluator(); channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
        other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True, use_safetensors=True,
            torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        record['config'].update(profile=ev.profile, sdxl_revision=SDXL_REV)
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), threads=torch.get_num_threads(),
            matmul_tf32=torch.backends.cuda.matmul.allow_tf32, cudnn_tf32=torch.backends.cudnn.allow_tf32)
        record['startup_seconds'] = time.monotonic() - STARTED

        def calls(rgb, owners):
            budget(); features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
            result = {o:detect_rgb(rgb, latent, o, ev.profile, features,
                binding='soft', binding_mode='combined', roster_size=1) for o in owners}
            budget(); return result

        def attach_c0(row):
            old = clean_c0[row['source_id']]
            row['c0_clean_all_owners'] = dict(image=old['image'], calls=copy.deepcopy(old['calls']),
                endpoints={o:endpoint(c) for o, c in old['calls'].items()},
                provenance=dict(kind='reused_full_calls', rows=str(CONTROLS / 'rows.jsonl'),
                    id=old['id'], call_provenance=old['call_provenance']))

        for sid in IDS:
            budget()
            row = dict(source_id=sid, source_image=str(SOURCES[sid]), status='running', conditions={},
                provenance=dict(source='canonical development original', retry=False))
            rows.append(row); folder = out / str(sid); folder.mkdir(); attach_c0(row); save()
            try:
                if sid in inherited:
                    old, arm = inherited[sid], inherited[sid]['arms']['S1']
                    row.update(payload=copy.deepcopy(arm['payload']), supplier=copy.deepcopy(old['supplier']),
                        writer=copy.deepcopy(arm['writer']))
                    row['provenance'].update(stage_a_rows=str(args.stage_a_dir.resolve() / 'rows.jsonl'),
                        stage_a_arm='S1', kind='reused_supplier_writer_and_C1_calls_once',
                        stage_a_arm_reuse=arm.get('reuse'), new_writer_executions=0)
                    marked = load(row['writer']['final_image'])
                else:
                    source = load(SOURCES[sid])
                    row['supplier'] = supply_f5(source, ev, folder / 'S1-supplier', budget)
                    save(); budget()
                    if row['supplier']['status'] != 'ok':
                        row['status'] = 'supplier_failed'; save()
                        if 'Fresh F5 bootstrap native channels unreadable' in row['supplier'].get('error', ''):
                            continue
                        raise RuntimeError('Supplier execution failure; saved supplier retained')
                    row['payload'] = copy.deepcopy(row['supplier']['payload'])
                    row['writer'] = embed(source, ALPHA, row['supplier']['q'], row['supplier']['h'],
                        ev, other, channel, folder / 'S1-writer', budget)
                    row['provenance'].update(kind='fresh_S1_then_E3_once', new_writer_executions=1)
                    save(); budget()
                    if row['writer']['status'] == 'construction_failed':
                        raise RuntimeError('Writer execution failure; saved result retained')
                    marked = load(row['writer']['final_image'])
                for condition in CONDITIONS:
                    budget()
                    if sid in inherited:
                        cell = copy.deepcopy(arm['conditions'][condition])
                        cell['call_provenance'] = {o:dict(kind='reused_full_call',
                            rows=str(args.stage_a_dir.resolve() / 'rows.jsonl'), source_id=sid,
                            arm='S1', condition=condition, owner=o) for o in cell['calls']}
                        cell['stage_a_c0_reference'] = dict(image=cell.get('c0_call_reference'),
                            endpoint=cell.get('c0_endpoint'))
                        if condition == 'clean':
                            extra = calls(load(cell['image']), OWNERS[2:])
                            cell['calls'].update(extra)
                            cell['call_provenance'].update({o:dict(kind='new_full_call', owner=o) for o in extra})
                    else:
                        if condition == 'clean':
                            cell = copy.deepcopy(row['writer']['conditions']['clean'])
                            cell['calls'].update(calls(marked, OWNERS[1:]))
                            cell['call_provenance'] = {o:dict(kind='writer_clean_call' if o == ALPHA else
                                'new_full_call', owner=o) for o in OWNERS}
                        else:
                            rgb = reconstruct(ev, other, marked, condition)
                            image = folder / f'S1-{condition}.png'; Image.fromarray(rgb).save(image)
                            rgb = load(image)
                            cell = dict(image=str(image), calls=calls(rgb, OWNERS[:2]),
                                quality_source=ev.metrics(source, rgb), quality_marked=ev.metrics(marked, rgb),
                                call_provenance={o:dict(kind='new_full_call', owner=o) for o in OWNERS[:2]})
                    cell['endpoints'] = {o:endpoint(c, row['payload'] if o == ALPHA else None)
                                         for o, c in cell['calls'].items()}
                    control = c0[sid]['conditions'][condition]
                    cell.update(c0_image=control['c0_image'], c0_call=copy.deepcopy(control['c0_call']),
                        c0_endpoint=endpoint(control['c0_call']), c0_provenance=dict(kind='reused_full_call',
                            rows=str(COMPOSITION / 'rows.jsonl'), source_id=sid, condition=condition, owner=ALPHA))
                    row['conditions'][condition] = cell
                    budget(); save()
                row['status'] = 'ok' if row['writer']['admitted'] else 'admission_failed'
                budget(); save()
                print(json.dumps(dict(source_id=sid, status=row['status'],
                    writer=row['writer']['status'], reused=sid in inherited)), flush=True)
            except Exception:
                row.update(status='execution_failed', error=traceback.format_exc()); save()
                raise
        budget(); record['outcome'] = 'completed'
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc())
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
