"""D2 cached native-forward-validated RGB8 writer; fixed development data only.

Native backward is an unvalidated proposal heuristic. Reported endpoints use
suspect-only F5-RC1 calls; DDIM training losses are not attack outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_readability_probe import Objective, IDS, CONDITIONS, DISCOVERY, patterns, payload, load, projected_update
from journal_vae_probe import Evaluator, write, SDXL, SDXL_REV
from journal_read_conditioning_probe import SCREEN, calls
from journal_binding_probe import delivery
from journal_native_utility import BRANCHES
from journal_ddim_channel import DifferentiableDDIM
from f4_transfer_probe import MAIN, ASSETS, SOURCES
from f5_gate import OWNERS
from scripts import journal_read_conditioning as rc

CAP = 3300.
UTILITY = MAIN / '.thesis-build/dev-runs/20261010-1206-native-utility'


def strict_quality(metrics):
    return bool((metrics['psnr_infinite'] or
        (metrics['psnr_db'] is not None and metrics['psnr_db'] > 35)) and
        metrics['ssim_rgb'] > .9 and metrics['lpips'] < .1)


def summarize(rows):
    good = [r for r in rows if r['status'] == 'ok']
    clean = [r['conditions']['clean'] for r in good]
    quality = sum(strict_quality(c['quality_source']) for c in clean)
    exact = sum(c['delivery']['both_exact'] and
        c['calls'][OWNERS[0]]['outcome'] == 'both_match' for c in clean)
    joint = {b: sum(r['conditions'][b]['joint_fixed_q'] for r in good) for b in CONDITIONS}
    c0 = sum(bool(r['conditions'][b]['c0_call']['watermark_found']) for r in good for b in CONDITIONS)
    wrong = sum(bool(r['conditions'][b]['calls'][OWNERS[1]]['watermark_found']) for r in good for b in CONDITIONS)
    feasible = sum(r['final_balls']['feasible'] for r in good)
    return dict(planned_sources=len(IDS), completed=len(good), missing_or_failed=len(IDS)-len(good),
        strict_clean_quality=quality, clean_exact_q_h_both_match=exact, final_feasible=feasible,
        joint_fixed_q=joint, sdxl_twelve_preserved=joint['sdxl_vae'] == 12,
        c0_any=c0, wrong_owner_any=wrong, planned_negative_calls=72,
        completed_negative_calls=6*len(good),
        prerequisite_pass=len(good)==12 and quality==exact==feasible==12 and
            joint['sd15_vae']==12 and joint['sdxl_vae']>=11 and c0+wrong==0,
        negative_interpretation='observed development counts; shared discovery C0 pixels; no calibrated FPR',
        scope='clean/VAE prerequisites only; official matched T3 remains required')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()  # Includes utility inspection, load, writing and final qualification.
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    (out / 'trials').mkdir()
    rows, torch = [], None
    record = dict(schema='journal-native-writer-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        data_split='development', usd=0, sources=list(IDS), seeds=[0, 1, 2],
        utility_run=str(UTILITY), outcome='running', qualification='pending',
        config=dict(candidate='D2', start='fixed RC3 final saved RGB8', detector='F5-RC1',
            branches=list(BRANCHES), logical_iterations=20,
            fractions_B={'0-9': [.1, .5, 1.], '10-19': [.025, .125, .25]},
            added_psnr_db=52., total_psnr_db=35.1, cap_seconds=CAP,
            improvement_rule='current_max - trial_max >= max(1e-6, 1e-4*current_max)',
            selection='lowest eligible maximum; ties by proposal order; otherwise retain',
            current_loss_vector='cached for exact selected saved RGB8; one baseline per source',
            gradient='full native graph, unit scale, first worst branch; unvalidated heuristic',
            precision='float16 DDIM; float32 reader/SDXL', strengths=[.1, .2],
            num_inference_steps=20, guidance_scale=1., eta=0., sdxl_revision=SDXL_REV,
            state='saved RGB8 only; no h restoration or floating accumulator',
            human_admissibility='missing', scope='exploratory image-domain refinement'))

    def save():
        record.update(elapsed_seconds=time.monotonic()-started, rows=len(rows), summary=summarize(rows))
        write(out / 'run.json', record)
        write(out / 'summary.json', record['summary'])

    def append(name, value):
        with (out / name).open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(value, allow_nan=False)+'\n')
            handle.flush()

    def budget():
        if time.monotonic()-started >= CAP:
            raise TimeoutError('D2 all-in 3300-second writer/qualification cap exhausted')

    def sync():
        torch.cuda.synchronize()

    save()
    try:
        utility = json.loads((UTILITY / 'run.json').read_text(encoding='utf-8'))
        if utility.get('outcome') != 'completed_internal_utility_only' or not utility.get('utility_pass'):
            raise ValueError('The fixed completed native utility must pass before writing')
        timing = utility['throughput']
        # Correct the screen's extra current-vector charge: selected trial vectors are cached.
        f, g, c = (timing[k] for k in ('nine_forward_seconds', 'forward_backward_seconds', 'clean_check_seconds'))
        old_load = timing['twenty_by_twelve_seconds']-240*timing['conservative_iteration_seconds']-24*(f+c)
        utility_rows = json.loads((UTILITY / 'results.json').read_text(encoding='utf-8'))['rows']
        overhead = max(r['duration_seconds']-r['clean_check_seconds']-sum(r['branch_seconds'].values())
            for r in utility_rows if r['stage']=='rounded_local_proposal')
        cached_only = old_load+240*(g+3*(f+c))+24*(f+c)
        projected = old_load+240*g+720*(f+c+overhead)+12*(f+c)+12*(f+6*c)+12*c
        record['timing_projection'] = dict(source=str(UTILITY/'run.json'),
            original_record_unchanged=True, load_seconds=old_load,
            nine_forward_seconds=f, gradient_seconds=g, clean_check_seconds=c,
            original_projection_seconds=timing['twenty_by_twelve_seconds'],
            cached_only_seconds=cached_only, proposal_overhead_seconds=overhead,
            projected_seconds=projected, budget_feasible=projected <= CAP,
            reserve_seconds=CAP-projected,
            decision='research/journal-upgrade-20261009/native-writer-execution-decision.md',
            formula='load + 240*gradient + 720*(nine+clean+overhead) + 12*(nine+clean) + 12*(nine+6*clean) + 12*clean',
            caveat='uses measured slowest screen timings; cap also enforced during actual final qualification')
        save()
        if projected > CAP:
            raise TimeoutError('Cached full-schedule projection exceeds fixed writer cap')
        budget()
        import torch
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

        for sid in IDS:
            budget()
            tick = time.monotonic()
            row = dict(source_id=sid, config='D2', method='F5-RC1', status='running', conditions={})
            save()
            try:
                _, q, h, row['payload'] = payload(ev, sid)
                initial_path = SCREEN / f'images/R3-{sid}-C1-clean.png'
                original_rgb, source = load(initial_path), load(SOURCES[sid])
                if original_rgb.shape != (512, 512, 3) or source.shape != original_rgb.shape:
                    raise ValueError('Fixed 512x512 RGB8 inputs required')
                base, clean = tensor(original_rgb), tensor(source)
                B, T = math.sqrt(base.numel())*10**(-52/20), math.sqrt(base.numel())*10**(-35.1/20)
                obj = Objective(ev, other, *patterns(ev.profile, q))
                obj.enable_checkpointing()

                def balls(x):
                    a, t = float((x-base).norm()), float((x-clean).norm())
                    box = bool(((x >= 0) & (x <= 1)).all())
                    return dict(added_norm=a, total_norm=t, added_radius=B, total_radius=T,
                        box=box, feasible=box and a<=B and t<=T)

                def qualify(rgb):
                    budget()
                    new, _, _ = calls(ev, rgb, OWNERS[0])
                    call, metrics = new['combined'], ev.metrics(source, rgb)
                    q_ok = bool(call['semantic']['read'] and int(call['semantic']['decoded_code'], 16)==q)
                    h_ok = bool(call['instance']['read'] and int(call['instance']['decoded_code'], 16)==h)
                    quality = strict_quality(metrics)
                    budget()
                    return dict(call=call, metrics=metrics, q_exact=q_ok, h_exact=h_ok,
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

                state_path = out / 'images' / f'D2-{sid}-state.png'
                current_rgb = save_rgb(state_path, original_rgb)
                current = tensor(current_rgb)
                current_clean, current_balls = qualify(current_rgb), balls(current)
                row.update(start_image=str(initial_path), source_image=str(SOURCES[sid]),
                    initial_qualification=current_clean, initial_balls=current_balls)
                if not current_clean['qualified'] or not current_balls['feasible']:
                    raise ValueError('Fixed RC3 initialization fails hard constraints; no repair')
                cached = nine(current)
                append('iterations.jsonl', dict(source_id=sid, stage='baseline', image=str(initial_path), **cached))
                step, accepted = 0, 0
                while step < 20:
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
                                path = out / 'trials' / f'D2-{sid}-step{step:02d}-proposal{order}.png'
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
                row.setdefault('update_status', 'schedule_completed')
                final = load(state_path)
                for condition in CONDITIONS:
                    budget()
                    if condition == 'clean':
                        transformed = final.copy()
                    else:
                        vae = ev.reader.vae if condition=='sd15_vae' else other
                        # Same float32-input mode roundtrip and numpy rounding as journal_vae_probe.
                        with torch.inference_mode():
                            x = tensor(final)
                            z = vae.encode(x*2-1).latent_dist.mode()
                            y = vae.decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
                        transformed = np.rint(np.clip(y*.5+.5, 0, 1)*255).astype(np.uint8)
                    path = out / 'images' / f'D2-{sid}-C1-{condition}.png'
                    saved = save_rgb(path, transformed)
                    features, latent = ev.features(saved, 7), ev.reader.latent(saved)
                    owner_calls = {owner:rc.detect_rgb(saved, latent, owner, ev.profile, features,
                        binding='soft', roster_size=1) for owner in OWNERS[:2]}
                    c0_path = DISCOVERY / 'images' / f'{sid}-f5-C0-{condition}.png'
                    c0 = load(c0_path)
                    if condition=='clean' and not np.array_equal(c0, source):
                        raise ValueError('Exact discovery clean C0 must equal canonical source')
                    c0_call = calls(ev, c0, OWNERS[0])[0]['combined']
                    intended = owner_calls[OWNERS[0]]
                    semantic = intended['semantic']
                    row['conditions'][condition] = dict(image=str(path), calls=owner_calls,
                        c0_image=str(c0_path), c0_call=c0_call,
                        c0_scope='fresh calls on exact shared discovery pixels; not independent controls',
                        delivery=delivery(intended, q, h),
                        joint_fixed_q=bool(semantic['read'] and int(semantic['decoded_code'], 16)==q and
                            semantic['content_match'] and semantic['found']),
                        quality_source=ev.metrics(source, saved), quality_input=ev.metrics(final, saved))
                    budget()
                row['status'] = 'ok'
            except Exception:
                row.update(status='failed', error=traceback.format_exc())
                raise
            finally:
                row['duration_seconds'] = time.monotonic()-tick
                rows.append(row)
                append('rows.jsonl', row)
                save()
                print(json.dumps(dict(source_id=sid, status=row['status'])), flush=True)
        record.update(outcome='completed', qualification='prerequisites_pass' if summarize(rows)['prerequisite_pass'] else
            'clean_vae_prerequisite_failure')
    except Exception:
        record.update(outcome='failed_or_incomplete', qualification='ineligible', error=traceback.format_exc())
        seen = {r['source_id'] for r in rows}
        for sid in IDS:
            if sid not in seen:
                row = dict(source_id=sid, config='D2', status='unrun', reason='Fatal failure or all-in cap; see run.json')
                rows.append(row)
                append('rows.jsonl', row)
        raise
    finally:
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>CAP)
        if torch is not None and torch.cuda.is_initialized():
            record.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())
        save()
        if record['budget_overrun']:
            record['summary']['prerequisite_pass'] = False
            record.update(qualification='ineligible', outcome='budget_incomplete')
            write(out/'summary.json', record['summary'])
            write(out/'run.json', record)


if __name__ == '__main__':
    main()
