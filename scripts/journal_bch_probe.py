"""E1 exact two-source Stage A image falsifier.

Conditional T3 runs in this process after the screen passes; screen-only
results can never qualify E1. Native gradients remain proposal heuristics.
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
from journal_binding_probe import delivery
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
D2_WRITER = MAIN / '.thesis-build/dev-runs/20261010-1212-native-writer'


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = PROCESS_STARTED
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    (out / 'trials').mkdir()
    rows, torch = [], None
    record = dict(schema='journal-e1-bch-stage-a-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        data_split='development', usd=0, sources=list(IDS), seeds=[0, 1, 2],
        d2_c0_source=str(D2_WRITER/'rows.jsonl'), outcome='running', qualification='pending',
        config=dict(candidate='E1-BCH59-A', start='fresh canonical source', detector='E1-BCH59-A',
            branches=list(BRANCHES), logical_iterations=20,
            fractions_B={'0-9': [.1, .5, 1.], '10-19': [.025, .125, .25]},
            added_psnr_db=52., total_psnr_db=35.1, cap_seconds=CAP,
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
            source_selection='smallest/largest numeric IDs frozen before outcomes',
            human_admissibility='missing', scope='exploratory image-domain refinement'))

    def save():
        summary = summarize(rows)
        t3 = record.get('conditional_t3', {})
        projection = record.get('timing_projection', {})
        t3_pass = t3.get('stage_a_t3_pass', t3.get('prerequisite_pass', t3.get('pass', False))) is True
        summary.update(t3_status=t3.get('status', summary['t3_status']), t3_pass=t3_pass,
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
        if time.monotonic()-started >= CAP:
            raise TimeoutError('E1 Stage A all-in 900-second cap exhausted')
        if torch is not None and torch.cuda.is_initialized() and torch.cuda.max_memory_allocated()>GPU_CAP_BYTES:
            raise torch.cuda.OutOfMemoryError('E1 10-GiB allocated memory hard cap exceeded')

    def sync():
        torch.cuda.synchronize()

    save()
    try:
        budget()
        d2_rows = [json.loads(line) for line in (D2_WRITER/'rows.jsonl').read_text().splitlines()]
        c0_lookup = {r['source_id']:r for r in d2_rows}
        if any(sid not in c0_lookup for sid in IDS):
            raise ValueError('Both frozen D2 source cache rows required for matched C0')
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
        for sid in IDS:
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
        if summarize(rows)['screen_pass']:
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
        for sid in IDS:
            if sid not in seen:
                row = dict(source_id=sid, config='E1', status='unrun', reason='Fatal failure or all-in cap; see run.json')
                rows.append(row)
                append('rows.jsonl', row)
        raise
    finally:
        finalization_tick = time.monotonic()
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>CAP)
        completed = [r for r in rows if r.get('status')=='ok']
        record['source_phase_counts'] = {phase:sum(phase in r for r in rows) for phase in
            ('construction_seconds', 'refinement_seconds', 'vae_negative_seconds')}
        record.setdefault('conditional_t3', dict(status='required_missing' if summarize(rows)['screen_pass'] else
            'not_triggered_screen_failure', stage_a_t3_pass=False, planned_c1_slots=12))
        save()  # Count a real summary serialization in finalization timing.
        record['finalization_seconds'] = time.monotonic()-finalization_tick
        if len(completed)==2:
            projected = record['startup_seconds'] + 10*1.5*max(r['construction_seconds']+
                r['refinement_seconds']+r['vae_negative_seconds'] for r in completed) + record['finalization_seconds']
            record['timing_projection'] = dict(projected_remaining=projected, cap_seconds=3300.,
                feasible=projected<=3300., formula='startup + 10*1.5*max(source construction+refinement+VAE negatives) + finalization')
        if torch is not None and torch.cuda.is_initialized():
            record.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())
        save()
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>CAP)
        save()
        record['finalization_seconds'] = time.monotonic()-finalization_tick
        if 'timing_projection' in record:
            record['timing_projection']['projected_remaining'] = record['startup_seconds'] + 10*1.5*max(
                r['construction_seconds']+r['refinement_seconds']+r['vae_negative_seconds'] for r in completed
            ) + record['finalization_seconds']
            record['timing_projection']['feasible'] = record['timing_projection']['projected_remaining']<=3300.
        save()
        record['qualification'] = 'stage_a_pass' if record['summary']['stage_a_pass'] else 'ineligible'
        write(out/'run.json', record)
        if record['budget_overrun']:
            record['summary']['screen_pass'] = False
            record['summary']['stage_a_pass'] = False
            record.update(qualification='ineligible', outcome='budget_incomplete')
            write(out/'summary.json', record['summary'])
            write(out/'run.json', record)


if __name__ == '__main__':
    main()
