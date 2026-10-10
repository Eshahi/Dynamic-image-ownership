"""E2 fixed integer 0.8 contraction: all-twelve cached clean/VAE falsifier.

No new embedding, optimization, fragile restoration, DDIM load or T3 execution.
This screen is exploratory and cannot qualify M1a.
"""
from __future__ import annotations

import time
PROCESS_STARTED = time.monotonic()  # Includes every scientific import/model load.

import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
IDS = (147498, 6012, 1675, 4795, 25394, 80932, 109798, 134882,
       177015, 190676, 468505, 499768)
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')
CAP = 300.
GPU_CAP_BYTES = 10 * 1024**3
METHOD = 'E2-BCH59-A080'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def attenuation(source, marked, np):
    """Exact frozen rule; endpoints ensure no clipping or half ties are needed."""
    d = marked.astype(np.int32)-source.astype(np.int32)
    return (source.astype(np.int32)+np.sign(d)*((4*np.abs(d)+2)//5)).astype(np.uint8)


def summarize(rows, owners, quality):
    good = [r for r in rows if r.get('status')=='ok' and
            all(r.get('conditions', {}).get(b, {}).get('status')=='ok' for b in CONDITIONS)]
    complete = len(rows)==12 and [r['source_id'] for r in rows]==list(IDS) and len(good)==12
    clean = [r['conditions']['clean'] for r in good]
    quality_count = sum(quality(c['quality_source']) for c in clean)
    exact = sum(c['delivery']['both_exact'] and c['calls'][owners[0]]['outcome']=='both_match'
                for c in clean)
    q_exact = sum(c['delivery']['semantic_exact'] for c in clean)
    h_exact = sum(c['delivery']['h_bit_errors']==0 and c['calls'][owners[0]]['instance']['read']
                  for c in clean)
    joint = {b:sum(r['conditions'][b]['joint_fixed_q'] for r in good) for b in CONDITIONS}
    cells = [r['conditions'][b] for r in rows for b in CONDITIONS
             if r.get('conditions', {}).get(b, {}).get('status')=='ok']
    all_cells = [r.get('conditions', {}).get(b, {}) for r in rows for b in CONDITIONS]
    c0_calls = [c['c0_call'] for c in all_cells if 'c0_call' in c]
    wrong_calls = [c['calls'][owners[1]] for c in all_cells if owners[1] in c.get('calls', {})]
    c0 = sum(bool(c['watermark_found']) for c in c0_calls)
    wrong = sum(bool(c['watermark_found']) for c in wrong_calls)
    passed = (complete and quality_count==q_exact==h_exact==exact==12 and
              joint['sd15_vae']==joint['sdxl_vae']==12 and c0+wrong==0)
    return dict(planned_sources=12, completed=len(good), missing_or_failed=12-len(good),
        all_source_cells_complete=complete, planned_condition_cells=36,
        completed_condition_cells=len(cells), strict_clean_quality=quality_count,
        clean_exact_q=q_exact, clean_exact_h=h_exact, clean_exact_q_h_both_match=exact,
        joint_fixed_q=joint, c0_any=c0, wrong_owner_any=wrong,
        planned_negative_calls=72, completed_negative_calls=len(c0_calls)+len(wrong_calls),
        screen_pass=passed, stage_a_pass=False, candidate_eligible=False, m1a_pass=False,
        t3_status='not_run; full frozen panel conditional on this cached screen',
        negative_interpretation='fresh repeated-source development calls on retained matched C0 pixels; no calibrated FPR',
        scope='E2 all-twelve cached clean/VAE prerequisites; no initializer qualification requirement')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--e1-stage-b-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    out, parent = args.output_dir.resolve(), args.e1_stage_b_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out/'images').mkdir()
    torch = None
    rows = []
    owners = ('qim-pilot-owner-alpha', 'qim-pilot-owner-beta')
    # Pure-Python predicate is also available if scientific imports fail.
    def quality(m):
        return bool((m['psnr_infinite'] or (m['psnr_db'] is not None and m['psnr_db']>35))
                    and m['ssim_rgb']>.9 and m['lpips']<.1)
    record = dict(schema='journal-e2-bch-attenuation-stage-a-v1',
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, data_split='development', usd=0, sources=list(IDS), seeds=[],
        outcome='running', qualification='pending',
        ancestry=dict(stage_b_run_json=str(parent/'run.json'), stage_b_rows_jsonl=str(parent/'rows.jsonl')),
        config=dict(candidate=METHOD, detector='E1-BCH59-A', factor=.8,
            integer_rule='x + sign(m-x)*floor((4*abs(m-x)+2)/5)',
            start='final saved E1 clean C1 endpoints, including inherited A',
            conditions=list(CONDITIONS), owners=list(owners), semantic_views=7,
            binding='soft', roster_size=1, precision='float32', posterior='mode',
            cap_seconds=CAP, gpu_allocated_cap_bytes=GPU_CAP_BYTES,
            optimization=False, fragile_restoration=False, threshold_change=False,
            target_basis='unchanged original recorded q and frozen operational h in E1 payload',
            source_selection='fixed twelve IDs, quality-failure and marginal case first',
            human_admissibility='missing', scope='cached exploratory clean/VAE screen only'))

    def append(row):
        with (out/'rows.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, allow_nan=False)+'\n')
            handle.flush()

    def budget():
        if time.monotonic()-PROCESS_STARTED>CAP:
            raise TimeoutError('E2 inclusive 300-second all-in cap exhausted')
        if torch is not None and torch.cuda.is_initialized() and torch.cuda.max_memory_allocated()>GPU_CAP_BYTES:
            raise torch.cuda.OutOfMemoryError('E2 10-GiB allocated peak cap exceeded')

    def save():
        record.update(duration_seconds=time.monotonic()-PROCESS_STARTED, rows=len(rows),
                      summary=summarize(rows, owners, quality))
        write(out/'summary.json', record['summary'])
        write(out/'run.json', record)

    save()
    try:
        budget()
        e1_run = json.loads((parent/'run.json').read_text(encoding='utf-8'))
        inputs = [json.loads(line) for line in (parent/'rows.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        lookup = {r['source_id']:r for r in inputs}
        if (e1_run.get('schema')!='journal-e1-bch-stage-b-v1' or
                e1_run.get('outcome')!='completed' or e1_run.get('data_split')!='development' or
                e1_run.get('usd')!=0 or len(inputs)!=12 or set(lookup)!=set(IDS) or
                any(r.get('status')!='ok' or r.get('method')!='E1-BCH59-A' or
                    set(r.get('conditions', {}))!=set(CONDITIONS) for r in inputs)):
            raise ValueError('E2 requires the completed exact all-twelve E1 B panel, including inherited A')
        record['ancestry'].update(stage_b_commit=e1_run['commit'],
                                 stage_a_provenance=e1_run.get('stage_a_provenance'))
        import numpy as np
        import torch
        import diffusers
        from diffusers import AutoencoderKL
        from PIL import Image
        from journal_bch_probe import delivery, coded_diagnostics, strict_quality
        from journal_readability_probe import load, reconstruct
        from journal_vae_probe import Evaluator, SDXL, SDXL_REV
        from f4_transfer_probe import SOURCES
        from f5_gate import OWNERS
        from scripts import journal_bch_readout as rc
        owners, quality = tuple(OWNERS[:2]), strict_quality
        if diffusers.__version__!='0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP_BYTES/torch.cuda.get_device_properties(0).total_memory)
        torch.cuda.reset_peak_memory_stats()
        budget()
        ev = Evaluator()
        other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True, use_safetensors=True,
            torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        record['config'].update(profile=ev.profile, sdxl_revision=SDXL_REV)
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), cpu_threads=torch.get_num_threads(),
            matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
            cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
            float32_matmul_precision=torch.get_float32_matmul_precision())
        record['startup_seconds'] = time.monotonic()-PROCESS_STARTED
        budget()
        save()
        for sid in IDS:
            budget()
            tick = time.monotonic()
            original = lookup[sid]
            row = dict(source_id=sid, config='E2', method=METHOD, status='running',
                payload=original['payload'], conditions={}, source_image=str(SOURCES[sid]),
                start_image=original['conditions']['clean']['image'],
                writer_ancestry=dict(input_e1_method=original['method'],
                    input_row_index=inputs.index(original), e1_stage_b_commit=e1_run['commit'],
                    inherited_provenance=original.get('inherited_provenance'),
                    e1_update_status=original.get('update_status'), factor=.8))
            try:
                source, marked = load(SOURCES[sid]), load(row['start_image'])
                if source.shape!=(512, 512, 3) or marked.shape!=source.shape:
                    raise ValueError('Fixed canonical 512x512 RGB8 source and E1 mark required')
                q, h = int(row['payload']['q'], 16), int(row['payload']['h'], 16)
                path = out/'images'/f'E2-{sid}-state.png'
                Image.fromarray(attenuation(source, marked, np)).save(path)
                final = load(path)
                row['final_state_image'] = str(path)
                row['construction_seconds'] = time.monotonic()-tick
                eval_tick = time.monotonic()
                for condition in CONDITIONS:
                    cell = dict(status='running')
                    row['conditions'][condition] = cell
                    try:
                        budget()
                        rgb = reconstruct(ev, other, final, condition)
                        path = out/'images'/f'E2-{sid}-C1-{condition}.png'
                        Image.fromarray(rgb).save(path)
                        saved = load(path)
                        features, latent = ev.features(saved, 7), ev.reader.latent(saved)
                        cell.update(image=str(path), calls={})
                        for owner in owners:
                            budget()
                            cell['calls'][owner] = rc.detect_rgb(saved, latent, owner, ev.profile, features,
                                binding='soft', roster_size=1)
                        calls = cell['calls']
                        call = calls[owners[0]]
                        sem = call['semantic']
                        cell.update(delivery=delivery(call, q, h), coded_diagnostics=coded_diagnostics(call, q),
                            joint_fixed_q=bool(sem['read'] and sem.get('decoded_code') is not None and
                                int(sem['decoded_code'], 16)==q and sem['content_match'] and sem['found']))
                        c0_path = Path(original['conditions'][condition]['c0_image'])
                        c0 = load(c0_path)
                        if condition=='clean' and not np.array_equal(c0, source):
                            raise ValueError('Retained matched clean C0 must equal canonical source')
                        budget()
                        c0_call = rc.detect_rgb(c0, ev.reader.latent(c0), owners[0], ev.profile,
                            ev.features(c0, 7), binding='soft', roster_size=1)
                        cell.update(c0_image=str(c0_path), c0_call=c0_call,
                            c0_scope='fresh calls on exact retained matched E1 C0 pixels; not independent controls')
                        cell['quality_source'] = ev.metrics(source, saved)
                        cell['quality_input'] = ev.metrics(final, saved)
                        budget()
                        cell['status'] = 'ok'
                    except Exception:
                        cell.update(status='failed', error=traceback.format_exc())
                        raise
                torch.cuda.synchronize()
                budget()
                row.update(status='ok', vae_negative_seconds=time.monotonic()-eval_tick)
            except Exception as error:
                row.update(status='failed', error=traceback.format_exc())
                if isinstance(error, (TimeoutError, torch.cuda.OutOfMemoryError)):
                    raise
            finally:
                for b in CONDITIONS:
                    row['conditions'].setdefault(b, dict(status='unrun', reason='Source/fatal failure; see row and run error'))
                row['duration_seconds'] = time.monotonic()-tick
                rows.append(row)
                append(row)
                save()
                print(json.dumps(dict(source_id=sid, status=row['status'])), flush=True)
        record['outcome'] = 'completed' if all(r['status']=='ok' for r in rows) else 'completed_with_failures'
    except Exception:
        record.update(outcome='failed_or_incomplete', error=traceback.format_exc())
        raise
    finally:
        seen = {r['source_id'] for r in rows}
        for sid in IDS:
            if sid not in seen:
                row = dict(source_id=sid, config='E2', method=METHOD, status='unrun',
                    reason='Fatal failure or inclusive cap; see run.json',
                    conditions={b:dict(status='unrun') for b in CONDITIONS})
                rows.append(row)
                append(row)
        if torch is not None and torch.cuda.is_initialized():
            record.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                          peak_reserved_bytes=torch.cuda.max_memory_reserved())
        save()  # Include ordinary summary/run serialization in the inclusive timer.
        record.update(duration_seconds=time.monotonic()-PROCESS_STARTED,
                      budget_overrun=time.monotonic()-PROCESS_STARTED>CAP)
        summary = record['summary']
        summary['stage_a_pass'] = bool(summary['screen_pass'] and record['outcome']=='completed' and
            not record['budget_overrun'] and record.get('peak_allocated_bytes', GPU_CAP_BYTES+1)<=GPU_CAP_BYTES)
        record['qualification'] = 'stage_a_pass' if summary['stage_a_pass'] else 'ineligible'
        if record['budget_overrun']:
            record['outcome'] = 'budget_incomplete'
        write(out/'summary.json', summary)
        write(out/'run.json', record)
        # Final writes belong to the same cap too; never retain a late pass.
        record['duration_seconds'] = time.monotonic()-PROCESS_STARTED
        if record['duration_seconds']>CAP:
            record.update(budget_overrun=True, outcome='budget_incomplete', qualification='ineligible')
            summary['stage_a_pass'] = False
        write(out/'summary.json', summary)
        write(out/'run.json', record)


if __name__=='__main__':
    main()
