"""E1 fixed Stage A falsifier or gated ten-source Stage B continuation.

Stage A includes conditional official T3. Stage B inherits those two source
rows and calls without new T3. Neither stage qualifies E1 for M1a.
Native gradients remain proposal heuristics.
"""
from __future__ import annotations

import time
PROCESS_STARTED = time.monotonic()  # Before scientific imports and model loads.

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_readability_probe import Objective as LegacyObjective, CONDITIONS, payload, load, projected_update, restore_fragile, reconstruct
from journal_vae_probe import Evaluator, write, SDXL, SDXL_REV
from journal_native_utility import BRANCHES
from journal_ddim_channel import DifferentiableDDIM
from f4_transfer_probe import MAIN, ASSETS, SOURCES
from f5_gate import OWNERS
from scripts import journal_bch_readout as rc
from scripts import journal_bch_carrier as carrier
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5

CAP = 900.
GPU_CAP_BYTES = 10 * 1024**3
IDS = (1675, 499768)
ALL_IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015,
    190676, 468505, 499768)
D2_WRITER = MAIN / '.thesis-build/dev-runs/20261010-1212-native-writer'


def delivery(result, q, h):
    """Same delivery predicate; an unavailable BCH word has unknown errors."""
    def errors(tier, target):
        decoded = result[tier].get('decoded_code')
        return None if target is None or decoded is None else (int(decoded, 16)^target).bit_count()
    qe, he = errors('semantic', q), errors('instance', h)
    sem = q is not None and bool(result['semantic']['read']) and qe == 0
    full = sem and h is not None and bool(result['instance']['read']) and he == 0
    return dict(semantic_exact=sem, both_exact=full, q_bit_errors=qe, h_bit_errors=he,
        semantic_presence=bool(result['semantic']['found']),
        both_presence=bool(result['semantic']['found'] and result['instance']['found']))


def validate_stage_a(folder):
    """Inspect completed fixed A evidence before creating or loading anything for B."""
    folder = folder.resolve()
    run = json.loads((folder/'run.json').read_text(encoding='utf-8'))
    summary = json.loads((folder/'summary.json').read_text(encoding='utf-8'))
    rows = [json.loads(line) for line in (folder/'rows.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if (run.get('schema')!='journal-e1-bch-stage-a-v1' or run.get('sources')!=list(IDS) or
        run.get('config')!=stage_config() or run.get('data_split')!='development' or
        run.get('usd')!=0 or run.get('seeds')!=[0, 1, 2] or
        run.get('outcome')!='completed' or run.get('qualification')!='stage_a_pass' or
        summary!=run.get('summary') or summary.get('stage_a_pass') is not True or
        run.get('budget_overrun') is not False or not 0<run.get('duration_seconds', math.inf)<=CAP or
        not 0<run.get('peak_allocated_bytes', math.inf)<=GPU_CAP_BYTES or
        len(rows)!=2 or [r.get('source_id') for r in rows]!=list(IDS) or
        any(r.get('method')!='E1-BCH59-A' or r.get('config')!='E1' for r in rows) or
        not summarize(rows)['screen_pass']):
        raise ValueError('Stage B requires the exact completed passing two-source Stage A')
    projection = run.get('timing_projection', {})
    measured = run['startup_seconds'] + 10*1.5*max(r['construction_seconds']+
        r['refinement_seconds']+r['vae_negative_seconds'] for r in rows) + run['finalization_seconds']
    if (projection.get('feasible') is not True or projection.get('cap_seconds')!=3300. or
        not math.isfinite(measured) or measured>3300. or
        not math.isclose(projection.get('projected_remaining', math.inf), measured, rel_tol=1e-9)):
        raise ValueError('Stage A measured ten-source projection must pass the fixed 3300-second cap')
    # Recompute endpoint counts from retained full calls, never infer T3 from screen flags.
    from journal_bch_t3_screen import _summarize, _endpoint, _identity, PLAN, D2_ROWS, ALPHA, BETA
    t3_rows = [json.loads(line) for line in (folder/'e1-t3-rows.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    retained = [json.loads(line) for line in D2_ROWS.read_text(encoding='utf-8').splitlines() if line.strip()]
    sources = {r['source_id']:r for r in rows}
    comparisons = {key:{} for key in PLAN}
    for method, arm, field in (('D2', 'candidate_C1', 'calls'),
        ('frozen_F5', 'frozen_C1_enrichment', 'native_calls')):
        panel = [r for r in retained if r['arm']==arm and _identity(r) in PLAN]
        if len(panel)!=12 or {_identity(r) for r in panel}!=set(PLAN):
            raise ValueError('Stage A exact frozen comparator panel is incomplete')
        for r in panel:
            key = _identity(r)
            if (r['status']!='ok' or r['payload']['q']!=sources[key[0]]['payload']['q'] or
                r['payload']['h']!=sources[key[0]]['payload']['h']):
                raise ValueError('Stage A comparator status or fixed payload differs')
            comparisons[key][method] = _endpoint(r[field][ALPHA], sources[key[0]]['payload'])
            comparisons[key][method+'_image'] = r['image']
    for r in t3_rows:
        if r['status']=='ok':
            expected_owners = {ALPHA, BETA} if r['arm']=='candidate_C1' else {ALPHA}
            if set(r['calls'])!=expected_owners:
                raise ValueError('Stage A T3 required full calls missing')
            if r['arm']=='candidate_C1':
                target = sources[r['source_id']]['payload']
                if r['payload']!=target or r['endpoints']!=_endpoint(r['calls'][ALPHA], target, coded=True):
                    raise ValueError('Stage A T3 fixed target endpoints disagree with full calls')
    t3 = _summarize(t3_rows, comparisons)
    recorded_t3 = json.loads((folder/'e1-t3-summary.json').read_text(encoding='utf-8'))
    if (not t3['stage_a_t3_pass'] or t3!=recorded_t3 or recorded_t3!=run.get('conditional_t3')):
        raise ValueError('Stage B requires complete passing official Stage A T3 evidence')
    for index, r in enumerate(rows):
        for condition in CONDITIONS:
            c = r['conditions'][condition]
            if not Path(c['image']).is_file():
                raise ValueError('Inherited final Stage A image is missing')
            call = c['calls'][OWNERS[0]]
            semantic = call['semantic']
            q, h = int(r['payload']['q'], 16), int(r['payload']['h'], 16)
            joint = bool(semantic['read'] and semantic.get('decoded_code') is not None and
                int(semantic['decoded_code'], 16)==q and semantic['content_match'] and semantic['found'])
            if c['delivery']!=delivery(call, q, h) or c['joint_fixed_q']!=joint:
                raise ValueError('Inherited Stage A endpoint disagrees with its full call')
        r['inherited_provenance'] = dict(stage='A', run_json=str(folder/'run.json'),
            rows_jsonl=str(folder/'rows.jsonl'), row_index=index, commit=run['commit'],
            reuse='exact final row and clean/VAE/negative calls; no new evaluation or raw overwrite')
    return rows, run


def summarize_b(rows, d2_rows):
    good = [r for r in rows if r.get('status')=='ok' and
        set(r.get('conditions', {}))==set(CONDITIONS)]
    ids = [r.get('source_id') for r in rows]
    complete = len(ids)==12 and set(ids)==set(ALL_IDS) and len(good)==12
    clean = [r['conditions']['clean'] for r in good]
    quality = sum(strict_quality(c['quality_source']) for c in clean)
    exact = sum(c['delivery']['both_exact'] and c['calls'][OWNERS[0]]['outcome']=='both_match' for c in clean)
    initial = sum(r['initial_qualification']['qualified'] and r['initial_balls']['feasible'] for r in good)
    feasible = sum(r['final_balls']['feasible'] for r in good)
    joint = {b:sum(r['conditions'][b]['joint_fixed_q'] for r in good) for b in CONDITIONS}
    c0 = sum(bool(r['conditions'][b]['c0_call']['watermark_found']) for r in good for b in CONDITIONS)
    wrong = sum(bool(r['conditions'][b]['calls'][OWNERS[1]]['watermark_found']) for r in good for b in CONDITIONS)
    d2_complete = len(d2_rows)==12 and {r.get('source_id') for r in d2_rows}==set(ALL_IDS) and all(
        r.get('status')=='ok' and set(r.get('conditions', {}))==set(CONDITIONS) for r in d2_rows)
    available = {r['source_id']:r for r in good}
    positives = [(r['source_id'], b) for r in d2_rows if r.get('status')=='ok'
        for b in ('sd15_vae', 'sdxl_vae') if r['conditions'][b]['joint_fixed_q']]
    lost = [dict(source_id=sid, condition=b) for sid, b in positives
        if sid not in available or not available[sid]['conditions'][b]['joint_fixed_q']]
    passed = (complete and d2_complete and quality==exact==initial==feasible==12 and
        joint['sd15_vae']==12 and joint['sdxl_vae']>=11 and not lost and c0+wrong==0)
    return dict(planned_sources=12, completed=len(good), missing_or_failed=12-len(good),
        all_source_cells_complete=complete, strict_clean_quality=quality,
        clean_exact_q_h_both_match=exact, valid_initializers=initial, final_feasible=feasible,
        joint_fixed_q=joint, d2_vae_comparison_complete=d2_complete,
        d2_vae_positive_count=len(positives), lost_d2_positive_vae_identities=lost,
        c0_any=c0, wrong_owner_any=wrong, planned_negative_calls=72,
        completed_negative_calls=6*len(good), inherited_negative_calls=6*sum(
            'inherited_provenance' in r for r in good), stage_b_evidence_pass=passed,
        stage_b_pass=False, stage_a_pass=False, candidate_eligible=False, m1a_pass=False,
        t3_status='inherited completed Stage A only; full twelve-source Stage C required',
        negative_interpretation='observed repeated-source development calls including inherited A; no calibrated FPR',
        scope='all-twelve clean/VAE prerequisites; ten new sources and two inherited A sources; no new T3')


def strict_quality(metrics):
    return bool((metrics['psnr_infinite'] or
        (metrics['psnr_db'] is not None and metrics['psnr_db'] > 35)) and
        metrics['ssim_rgb'] > .9 and metrics['lpips'] < .1)


def patterns(profile, q):
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(OWNERS[0])
    w = np.asarray(carrier.pattern(profile, OWNERS[0], q), np.float64)
    return f5.Layout(checked, key, config, owner), w, 2 * w


class Objective(LegacyObjective):
    """Same 320-chip projection; only the fixed antipodal 59-bit gaps differ."""
    def loss_details(self, x, condition):
        p = self.projection(x, condition)
        norm = p.norm().clamp_min(1e-8)
        score = (self.w * p).sum() / norm
        sigma = (p.norm() / math.sqrt(320)).clamp_min(1e-8)
        gaps = self.torch.stack([(p[(320*i)//59:(320*(i+1))//59] *
            self.gaps[(320*i)//59:(320*(i+1))//59]).sum() for i in range(59)]) / sigma
        score_hinge, bit_hinges = 9 - score, 1 - gaps
        loss = self.torch.relu(score_hinge).square() + self.torch.relu(bit_hinges).square().mean()
        return loss, dict(score_hinge=float(score_hinge.detach().item()),
            maximum_bit_hinge=float(bit_hinges.detach().max().item()),
            normalized_coded_bit_gaps=gaps.detach().cpu().tolist(),
            fixed_q_score=float(score.detach().item()),
            hinges_inactive=bool((score_hinge <= 0).item() and (bit_hinges <= 0).all().item()),
            finite_forward=bool(self.torch.isfinite(score).item() and self.torch.isfinite(gaps).all().item()))


def coded_diagnostics(call, q):
    semantic = call['semantic']
    raw = semantic.get('raw_coded_word')
    decoded = semantic.get('decoded_code')
    return dict(intended_coded_word=f'{carrier.encode(q):015x}',
        raw_coded_word=raw,
        raw_coded_errors=(int(raw, 16)^carrier.encode(q)).bit_count() if raw is not None else None,
        decoded_q_errors=(int(decoded, 16)^q).bit_count() if decoded is not None else None,
        decoded_q_available=decoded is not None, semantic_read=bool(semantic['read']))


def summarize(rows):
    good = [r for r in rows if r['status'] == 'ok']
    clean = [r['conditions']['clean'] for r in good]
    quality = sum(strict_quality(c['quality_source']) for c in clean)
    exact = sum(c['delivery']['both_exact'] and
        c['calls'][OWNERS[0]]['outcome'] == 'both_match' for c in clean)
    joint = {b: sum(r['conditions'][b]['joint_fixed_q'] for r in good) for b in CONDITIONS}
    c0 = sum(bool(r['conditions'][b]['c0_call']['watermark_found']) for r in good for b in CONDITIONS)
    wrong = sum(bool(r['conditions'][b]['calls'][OWNERS[1]]['watermark_found']) for r in good for b in CONDITIONS)
    initial = sum(r['initial_qualification']['qualified'] and r['initial_balls']['feasible'] for r in good)
    feasible = sum(r['final_balls']['feasible'] for r in good)
    passed = (len(good)==2 and quality==exact==initial==feasible==2 and
        joint['sd15_vae']==joint['sdxl_vae']==2 and c0+wrong==0)
    return dict(planned_sources=2, completed=len(good), missing_or_failed=2-len(good),
        strict_clean_quality=quality, clean_exact_q_h_both_match=exact,
        valid_initializers=initial, final_feasible=feasible, joint_fixed_q=joint,
        c0_any=c0, wrong_owner_any=wrong, planned_negative_calls=12,
        completed_negative_calls=6*len(good), screen_pass=passed,
        t3_status='required_missing' if passed else 'not_triggered_screen_failure',
        stage_a_pass=False, candidate_eligible=False,
        negative_interpretation='observed repeated-source development calls; no calibrated FPR',
        scope='E1 two-source clean/VAE screen; official conditional T3 still required')



def stage_config(cap=CAP, stage_b=False):
    return dict(candidate='E1-BCH59-A', start='fresh canonical source', detector='E1-BCH59-A',
            branches=list(BRANCHES), logical_iterations=20,
            fractions_B={'0-9': [.1, .5, 1.], '10-19': [.025, .125, .25]},
            added_psnr_db=52., total_psnr_db=35.1, cap_seconds=cap,
            improvement_rule='current_max - trial_max >= max(1e-6, 1e-4*current_max)',
            selection='lowest eligible maximum; ties by proposal order; otherwise retain',
            current_loss_vector='cached for exact selected saved RGB8; one baseline per source',
            gradient='full native graph, unit scale, first worst branch; unvalidated heuristic',
            precision='float16 DDIM; float32 reader/SDXL', strengths=[.1, .2],
            num_inference_steps=20, guidance_scale=1., eta=0., sdxl_revision=SDXL_REV,
            initialization=dict(first_psnr_db=46., first_steps=150, second_psnr_db=52., second_steps=50,
                margin=4., mask_power=0., fixed_q_h_restorations=2),
            state='saved RGB8 only; no restoration after initializer',
            gpu_allocated_cap_bytes=GPU_CAP_BYTES,
            source_selection=('remaining ten ascending frozen IDs; two inherited A rows' if stage_b else
                'smallest/largest numeric IDs frozen before outcomes'),
            human_admissibility='missing', scope=('exploratory all-twelve clean/VAE continuation; full Stage C T3 remains required'
                if stage_b else 'exploratory image-domain refinement'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stage-b-from', type=Path, help='Completed passing Stage A folder; ten-source continuation only')
    args = parser.parse_args()
    stage_b = args.stage_b_from is not None
    cap = 3300. if stage_b else CAP
    run_ids = tuple(sid for sid in ALL_IDS if sid not in IDS) if stage_b else IDS
    inherited, stage_a = validate_stage_a(args.stage_b_from) if stage_b else ([], None)
    started = PROCESS_STARTED
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    (out / 'trials').mkdir()
    rows, torch = list(inherited), None
    d2_rows = []
    record = dict(schema='journal-e1-bch-stage-b-v1' if stage_b else 'journal-e1-bch-stage-a-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        data_split='development', usd=0, sources=list(ALL_IDS if stage_b else IDS), seeds=[0, 1, 2],
        d2_c0_source=str(D2_WRITER/'rows.jsonl'), outcome='running', qualification='pending',
        config=stage_config(cap, stage_b))

    if stage_b:
        record.update(stage='B', constructed_sources=list(run_ids), inherited_sources=list(IDS),
            stage_a_provenance=dict(folder=str(args.stage_b_from.resolve()), commit=stage_a['commit'],
                run_json=str(args.stage_b_from.resolve()/'run.json'),
                rows_jsonl=str(args.stage_b_from.resolve()/'rows.jsonl'),
                conditional_t3='inherited completed Stage A only; no Stage B T3 execution'))

    def save():
        if stage_b:
            summary = summarize_b(rows, d2_rows)
            summary['stage_b_pass'] = bool(summary['stage_b_evidence_pass'] and
                record.get('outcome')=='completed' and time.monotonic()-started<=cap and
                not record.get('budget_overrun', False) and record.get('peak_allocated_bytes', 0)<=GPU_CAP_BYTES)
            record.update(elapsed_seconds=time.monotonic()-started, rows=len(rows), summary=summary)
            write(out/'run.json', record)
            write(out/'summary.json', summary)
            return
        summary = summarize(rows)
        t3 = record.get('conditional_t3', {})
        projection = record.get('timing_projection', {})
        t3_pass = t3.get('stage_a_t3_pass', t3.get('prerequisite_pass', t3.get('pass', False))) is True
        t3_status = ('completed_pass' if t3_pass else 'completed_fail') if t3.get('complete') else summary['t3_status']
        summary.update(t3_status=t3.get('status', t3_status), t3_pass=t3_pass,
            projection_feasible=projection.get('feasible', False),
            stage_a_pass=bool(summary['screen_pass'] and t3_pass and projection.get('feasible', False)
                and time.monotonic()-started<=CAP and not record.get('budget_overrun', False)),
            candidate_eligible=False)
        record.update(elapsed_seconds=time.monotonic()-started, rows=len(rows), summary=summary)
        write(out / 'run.json', record)
        write(out / 'summary.json', record['summary'])

    def append(name, value):
        with (out / name).open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(value, allow_nan=False)+'\n')
            handle.flush()

    def budget():
        if time.monotonic()-started >= cap:
            raise TimeoutError(f'E1 Stage {"B" if stage_b else "A"} all-in {cap:g}-second cap exhausted')
        if torch is not None and torch.cuda.is_initialized() and torch.cuda.max_memory_allocated()>GPU_CAP_BYTES:
            raise torch.cuda.OutOfMemoryError('E1 10-GiB allocated memory hard cap exceeded')

    def sync():
        torch.cuda.synchronize()

    for inherited_row in inherited:
        append('rows.jsonl', inherited_row)
    save()
    try:
        budget()
        d2_rows = [json.loads(line) for line in (D2_WRITER/'rows.jsonl').read_text().splitlines()]
        c0_lookup = {r['source_id']:r for r in d2_rows}
        if any(sid not in c0_lookup for sid in (ALL_IDS if stage_b else IDS)):
            raise ValueError('Every planned frozen D2 source cache row is required for matched C0')
        import torch
        torch.cuda.set_per_process_memory_fraction(GPU_CAP_BYTES/torch.cuda.get_device_properties(0).total_memory)
        import diffusers
        from diffusers import AutoencoderKL
        from PIL import Image
        import three_threat_models as models
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')
        ev = Evaluator()
        channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
        other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True,
            use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), cpu_threads=torch.get_num_threads(),
            matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
            cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
            float32_matmul_precision=torch.get_float32_matmul_precision())
        save()

        def tensor(rgb):
            return ev.reader.tensor(rgb.astype(np.float32)/255)

        def save_rgb(path, rgb):
            Image.fromarray(rgb).save(path)
            return load(path)

        ev.reader.vae.enable_gradient_checkpointing()
        class BoundedReader:
            # Keep the existing PGD algorithm; check its budget at every encode.
            def __getattr__(self, name):
                return getattr(ev.reader, name)
            def encode(self, x):
                budget()
                return ev.reader.encode(x)
        bounded_reader = BoundedReader()
        record['startup_seconds'] = time.monotonic()-started
        for sid in run_ids:
            budget()
            tick = time.monotonic()
            row = dict(source_id=sid, config='E1', method='E1-BCH59-A', status='running', conditions={})
            save()
            try:
                construction_tick = time.monotonic()
                _, q, h, row['payload'] = payload(ev, sid)
                source = load(SOURCES[sid])
                if source.shape != (512, 512, 3):
                    raise ValueError('Fixed 512x512 RGB8 inputs required')
                layout, w, gaps = patterns(ev.profile, q)
                budget()
                first = f5.robust_pgd(bounded_reader, source.astype(np.float64)/255., layout, w, 46., 150, 4., 0.)
                original_rgb = np.clip(np.rint(first*255), 0, 255).astype(np.uint8)
                original_rgb, first_restore = restore_fragile(original_rgb, q, h, ev.profile)
                first_path = out/'images'/f'E1-{sid}-initial-46-restored.png'
                original_rgb = save_rgb(first_path, original_rgb)
                budget()
                second = f5.robust_pgd(bounded_reader, original_rgb.astype(np.float64)/255., layout, w, 52., 50, 4., 0.)
                original_rgb = np.clip(np.rint(second*255), 0, 255).astype(np.uint8)
                original_rgb, second_restore = restore_fragile(original_rgb, q, h, ev.profile)
                initial_path = out/'images'/f'E1-{sid}-initializer.png'
                original_rgb = save_rgb(initial_path, original_rgb)
                sync()
                row['construction_seconds'] = time.monotonic()-construction_tick
                refinement_tick = time.monotonic()
                row['initializer_reports'] = dict(first_restore=first_restore, second_restore=second_restore)
                budget()
                base, clean = tensor(original_rgb), tensor(source)
                B, T = math.sqrt(base.numel())*10**(-52/20), math.sqrt(base.numel())*10**(-35.1/20)
                obj = Objective(ev, other, layout, w, gaps)
                obj.enable_checkpointing()

                def balls(x):
                    a, t = float((x-base).norm()), float((x-clean).norm())
                    box = bool(((x >= 0) & (x <= 1)).all())
                    return dict(added_norm=a, total_norm=t, added_radius=B, total_radius=T,
                        box=box, feasible=box and a<=B and t<=T)

                def qualify(rgb):
                    budget()
                    call = rc.detect_rgb(rgb, ev.reader.latent(rgb), OWNERS[0], ev.profile,
                        ev.features(rgb, 7), binding='soft', roster_size=1)
                    metrics = ev.metrics(source, rgb)
                    q_ok = bool(call['semantic']['read'] and int(call['semantic']['decoded_code'], 16)==q)
                    h_ok = bool(call['instance']['read'] and int(call['instance']['decoded_code'], 16)==h)
                    quality = strict_quality(metrics)
                    budget()
                    return dict(call=call, coded_diagnostics=coded_diagnostics(call, q), metrics=metrics, q_exact=q_ok, h_exact=h_ok,
                        both_match=call['outcome']=='both_match', strict_quality=quality,
                        qualified=q_ok and h_ok and call['outcome']=='both_match' and quality)

                def branch_loss(x, index):
                    if index < 3:
                        loss, detail = obj.loss_details(x, BRANCHES[index])
                    else:
                        k = index-3
                        loss, detail = obj.loss_details(channel.forward(x, (.1, .2)[k//3], k%3).image, 'clean')
                    if not bool(torch.isfinite(loss)) or not detail['finite_forward']:
                        raise ValueError('Nonfinite native branch objective')
                    return loss, detail

                def nine(x):
                    losses, details = {}, {}
                    with torch.no_grad():
                        for index, branch in enumerate(BRANCHES):
                            budget()
                            loss, detail = branch_loss(x, index)
                            losses[branch], details[branch] = float(loss), detail
                    budget()
                    values = list(losses.values())
                    return dict(branch_losses=losses, branch_details=details,
                        max_loss=max(values), worst_index=int(np.argmax(values)))

                state_path = out / 'images' / f'E1-{sid}-state.png'
                current_rgb = save_rgb(state_path, original_rgb)
                current = tensor(current_rgb)
                current_clean, current_balls = qualify(current_rgb), balls(current)
                row.update(start_image=str(initial_path), source_image=str(SOURCES[sid]),
                    initial_qualification=current_clean, initial_balls=current_balls)
                initializer_valid = current_clean['qualified'] and current_balls['feasible']
                cached = nine(current) if initializer_valid else None
                append('iterations.jsonl', dict(source_id=sid, stage='baseline', image=str(initial_path), **(cached or {})))
                step, accepted = 0, 0
                while initializer_valid and step < 20:
                    budget()
                    phase_end = 10 if step < 10 else 20
                    inactive = cached['max_loss']==0 and all(v==0 for v in cached['branch_losses'].values()) and all(
                        d['finite_forward'] and d['hinges_inactive'] and d['score_hinge']<=0 and
                        d['maximum_bit_hinge']<=0 for d in cached['branch_details'].values())
                    if inactive and current_clean['qualified'] and current_balls['feasible']:
                        append('iterations.jsonl', dict(source_id=sid, stage='exact_inactive_noops',
                            logical_start=step, logical_end_exclusive=20, max_loss=cached['max_loss']))
                        step = 20
                        row['update_status'] = 'exact_inactive'
                        break
                    worst = cached['worst_index']
                    iteration = dict(source_id=sid, stage='iteration', logical_step=step,
                        active_branch=BRANCHES[worst], current_max_loss=cached['max_loss'], proposals=[])
                    sync()
                    gradient_tick = time.monotonic()
                    x = current.detach().clone().requires_grad_(True)
                    loss, detail = branch_loss(x, worst)
                    gradient, = torch.autograd.grad(loss, x)
                    gradient = gradient.detach()
                    norm = float(gradient.norm())
                    sync()
                    iteration.update(gradient_seconds=time.monotonic()-gradient_tick,
                        gradient_loss=float(loss.detach()), gradient_detail=detail,
                        gradient_norm=norm if math.isfinite(norm) else None)
                    del x, loss
                    if not bool(torch.isfinite(gradient).all()) or not math.isfinite(norm) or norm<=0:
                        iteration.update(update_status='stalled_invalid', reason='positive or unresolved loss with zero/nonfinite heuristic gradient')
                        append('iterations.jsonl', iteration)
                        row['update_status'] = 'stalled_invalid'
                        row['stalled_logical_step'] = step
                        del gradient
                        break
                    margin = max(1e-6, 1e-4*cached['max_loss'])
                    eligible = []
                    fractions = (.1, .5, 1.) if step < 10 else (.025, .125, .25)
                    for order, fraction in enumerate(fractions):
                        budget()
                        trial_record = dict(source_id=sid, stage='proposal', logical_step=step,
                            proposal_order=order, fraction_B=fraction, status='running')
                        try:
                            with torch.no_grad():
                                trial, projection_ok = projected_update(current-fraction*B*gradient/norm, base, clean, B, T, torch)
                                rgb = torch.round(trial.clamp(0, 1)*255)[0].permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                                path = out / 'trials' / f'E1-{sid}-step{step:02d}-proposal{order}.png'
                                rgb = save_rgb(path, rgb)
                                rounded = tensor(rgb)
                                trial_record.update(image=str(path), projected_feasible=projection_ok,
                                    continuous_balls=balls(trial), rounded_balls=balls(rounded),
                                    changed_rgb_components=int(np.count_nonzero(rgb!=current_rgb)),
                                    changed_pixels=int(np.count_nonzero(np.any(rgb!=current_rgb, axis=2))))
                                trial_record['qualification'] = qualify(rgb)
                                trial_record.update(nine(rounded))  # All nine, even for infeasible trials.
                            decrease = cached['max_loss']-trial_record['max_loss']
                            reasons = [name for name, passed in (
                                ('projection', projection_ok), ('continuous_balls', trial_record['continuous_balls']['feasible']),
                                ('rounded_balls', trial_record['rounded_balls']['feasible']),
                                ('clean_qualification', trial_record['qualification']['qualified']),
                                ('decrease_margin', decrease>=margin)) if not passed]
                            trial_record.update(status='ok', loss_decrease=decrease, required_decrease=margin,
                                eligible=not reasons, rejection_reasons=reasons)
                            if not reasons:
                                eligible.append((trial_record['max_loss'], order, path, trial_record))
                        except Exception:
                            trial_record.update(status='failed', error=traceback.format_exc())
                            raise
                        finally:
                            append('iterations.jsonl', trial_record)
                        iteration['proposals'].append(dict(proposal_order=order, image=str(path),
                            max_loss=trial_record['max_loss'], eligible=trial_record['eligible'],
                            rejection_reasons=trial_record['rejection_reasons']))
                    del gradient
                    if eligible:
                        _, order, path, selected = min(eligible, key=lambda z: (z[0], z[1]))
                        current_rgb = save_rgb(state_path, load(path))
                        current = tensor(current_rgb)  # No continuous accumulation.
                        cached = {k:selected[k] for k in ('branch_losses', 'branch_details', 'max_loss', 'worst_index')}
                        current_clean, current_balls = selected['qualification'], selected['rounded_balls']
                        accepted += 1
                        iteration.update(selected_order=order, update_status='accepted', next_max_loss=cached['max_loss'])
                        step += 1
                    else:
                        iteration.update(selected_order=None, update_status='retained',
                            exact_same_phase_noops=dict(logical_start=step+1, logical_end_exclusive=phase_end))
                        step = phase_end  # Changed second-phase lengths must still be tested.
                    append('iterations.jsonl', iteration)
                    save()
                row.update(planned_logical_iterations=20, completed_logical_iterations=step,
                    accepted_updates=accepted,
                    final_state_image=str(state_path), final_loss_vector=cached,
                    final_balls=balls(tensor(load(state_path))))
                sync()
                row['refinement_seconds'] = time.monotonic()-refinement_tick
                row.setdefault('update_status', 'schedule_completed' if initializer_valid else 'invalid_initializer_no_refinement')
                evaluation_tick = time.monotonic()
                final = load(state_path)
                for condition in CONDITIONS:
                    budget()
                    transformed = reconstruct(ev, other, final, condition)
                    path = out / 'images' / f'E1-{sid}-C1-{condition}.png'
                    saved = save_rgb(path, transformed)
                    features, latent = ev.features(saved, 7), ev.reader.latent(saved)
                    owner_calls = {owner:rc.detect_rgb(saved, latent, owner, ev.profile, features,
                        binding='soft', roster_size=1) for owner in OWNERS[:2]}
                    c0_path = Path(c0_lookup[sid]['conditions'][condition]['c0_image'])
                    c0 = load(c0_path)
                    if condition=='clean' and not np.array_equal(c0, source):
                        raise ValueError('Exact discovery clean C0 must equal canonical source')
                    c0_call = rc.detect_rgb(c0, ev.reader.latent(c0), OWNERS[0], ev.profile,
                        ev.features(c0, 7), binding='soft', roster_size=1)
                    intended = owner_calls[OWNERS[0]]
                    semantic = intended['semantic']
                    row['conditions'][condition] = dict(image=str(path), calls=owner_calls,
                        c0_image=str(c0_path), c0_call=c0_call,
                        c0_scope='fresh calls on exact shared discovery pixels; not independent controls',
                        delivery=delivery(intended, q, h), coded_diagnostics=coded_diagnostics(intended, q),
                        joint_fixed_q=bool(semantic['read'] and int(semantic['decoded_code'], 16)==q and
                            semantic['content_match'] and semantic['found']),
                        quality_source=ev.metrics(source, saved), quality_input=ev.metrics(final, saved))
                    budget()
                sync()
                row['vae_negative_seconds'] = time.monotonic()-evaluation_tick
                row['status'] = 'ok'
            except Exception as error:
                row.update(status='failed', error=traceback.format_exc())
                if isinstance(error, (TimeoutError, torch.cuda.OutOfMemoryError)):
                    raise
            finally:
                row['duration_seconds'] = time.monotonic()-tick
                rows.append(row)
                append('rows.jsonl', row)
                save()
                print(json.dumps(dict(source_id=sid, status=row['status'])), flush=True)
        if stage_b:
            record['conditional_t3'] = dict(status='inherited_stage_a_only_no_new_t3',
                stage_a_t3_pass=True, source=str(args.stage_b_from.resolve()/'e1-t3-summary.json'))
        elif summarize(rows)['screen_pass']:
            budget()
            from journal_bch_t3_screen import run_stage_a_t3
            record['conditional_t3'] = run_stage_a_t3(ev, channel.pipe, rows, out, budget)
            budget()
        else:
            record['conditional_t3'] = dict(status='not_triggered_screen_failure', stage_a_t3_pass=False,
                planned_c1_slots=12)
        record.update(outcome='completed', qualification='pending_finalization')
    except Exception:
        record.update(outcome='failed_or_incomplete', qualification='ineligible', error=traceback.format_exc())
        seen = {r['source_id'] for r in rows}
        for sid in run_ids:
            if sid not in seen:
                row = dict(source_id=sid, config='E1', status='unrun', reason='Fatal failure or all-in cap; see run.json')
                rows.append(row)
                append('rows.jsonl', row)
        raise
    finally:
        finalization_tick = time.monotonic()
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>cap)
        completed = [r for r in rows if r.get('status')=='ok']
        record['source_phase_counts'] = {phase:sum(phase in r for r in rows) for phase in
            ('construction_seconds', 'refinement_seconds', 'vae_negative_seconds')}
        if stage_b:
            record['new_source_phase_counts'] = {phase:sum(phase in r for r in rows
                if 'inherited_provenance' not in r) for phase in record['source_phase_counts']}
        record.setdefault('conditional_t3', dict(status='not_run_stage_b' if stage_b else
            'required_missing' if summarize(rows)['screen_pass'] else
            'not_triggered_screen_failure', stage_a_t3_pass=False, planned_c1_slots=12))
        save()  # Count a real summary serialization in finalization timing.
        record['finalization_seconds'] = time.monotonic()-finalization_tick
        if not stage_b and len(completed)==2:
            projected = record['startup_seconds'] + 10*1.5*max(r['construction_seconds']+
                r['refinement_seconds']+r['vae_negative_seconds'] for r in completed) + record['finalization_seconds']
            record['timing_projection'] = dict(projected_remaining=projected, cap_seconds=3300.,
                feasible=projected<=3300., formula='startup + 10*1.5*max(source construction+refinement+VAE negatives) + finalization')
        if torch is not None and torch.cuda.is_initialized():
            record.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())
        save()
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>cap)
        save()
        record['finalization_seconds'] = time.monotonic()-finalization_tick
        if 'timing_projection' in record:
            record['timing_projection']['projected_remaining'] = record['startup_seconds'] + 10*1.5*max(
                r['construction_seconds']+r['refinement_seconds']+r['vae_negative_seconds'] for r in completed
            ) + record['finalization_seconds']
            record['timing_projection']['feasible'] = record['timing_projection']['projected_remaining']<=3300.
        save()
        pass_key = 'stage_b_pass' if stage_b else 'stage_a_pass'
        record['qualification'] = pass_key if record['summary'][pass_key] else 'ineligible'
        write(out/'run.json', record)
        if record['budget_overrun']:
            if not stage_b:
                record['summary']['screen_pass'] = False
            record['summary'][pass_key] = False
            record.update(qualification='ineligible', outcome='budget_incomplete')
            write(out/'summary.json', record['summary'])
            write(out/'run.json', record)


if __name__ == '__main__':
    main()
