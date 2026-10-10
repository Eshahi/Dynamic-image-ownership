"""Frozen alpha-only E3 supplied-payload writer; no model loading or historical lookup.

The E1 scientific body is extracted from journal_bch_probe.py at 4bbc427.
S1 below is a prospective fresh-F5 supplier, separately timed and labelled.
Caller owns pinned models, development provenance and the budget callback.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import time
import traceback

import numpy as np

from scripts.journal_bch_probe import (Objective, patterns, projected_update,
    restore_fragile, coded_diagnostics, delivery, load, BRANCHES)
from scripts import journal_bch_readout as rc
from scripts import f5_latent_codec as f5

ALPHA = 'qim-pilot-owner-alpha'


def strict_quality(metrics):
    """Missing/nonfinite metrics are execution failures; boundaries are strict."""
    infinite = metrics['psnr_infinite']
    psnr, ssim, lpips = (metrics[k] for k in ('psnr_db', 'ssim_rgb', 'lpips'))
    if not isinstance(infinite, (bool, np.bool_)):
        raise ValueError('Invalid PSNR infinity flag')
    if (not all(isinstance(v, (int, float, np.integer, np.floating)) and
            math.isfinite(float(v)) for v in (ssim, lpips)) or
            (not infinite and (not isinstance(psnr, (int, float, np.integer, np.floating))
                or not math.isfinite(float(psnr)))) or
            (infinite and psnr is not None)):
        raise ValueError('Missing or nonfinite clean quality metrics')
    return bool((infinite or psnr > 35) and ssim > .9 and lpips < .1)


def exact_read(call, tier, target):
    word = call[tier].get('decoded_code')
    return bool(call[tier]['read'] and word is not None and int(word, 16) == target)


def contract(rgb, source):
    delta = rgb.astype(np.int32) - source.astype(np.int32)
    return (source.astype(np.int32) + np.sign(delta) *
        ((4 * np.abs(delta) + 2) // 5)).astype(np.uint8)


def _source(source):
    source = np.asarray(source)
    if source.dtype != np.uint8 or source.shape != (512, 512, 3):
        raise ValueError('Canonical 512x512 RGB8 source required')
    return source.copy()


def _target(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not 0 <= int(value) < 2**32:
        raise ValueError('Targets must be unsigned 32-bit integers')
    return int(value)


def _save_rgb(path, rgb):
    from PIL import Image
    Image.fromarray(rgb).save(path)
    return load(path)


class _BoundedReader:
    def __init__(self, reader, budget):
        self.reader, self.budget = reader, budget
    def __getattr__(self, name):
        return getattr(self.reader, name)
    def encode(self, x):
        self.budget()
        return self.reader.encode(x)
    def latent(self, rgb):
        self.budget()
        return self.reader.latent(rgb)


def embed(source, owner, q, h, evaluator, sdxl_vae, ddim_channel, output_dir, budget):
    """Return saved output and admission status, including construction failures.

    budget is a no-argument callable raising on its caller-owned time/memory cap.
    Detection receives suspect pixels/features only; supplied q/h are compared
    outside the source-blind reader. A rejected initializer still reaches E3.
    """
    if owner != ALPHA:
        raise ValueError('Frozen E3 supports only qim-pilot-owner-alpha')
    source, q, h = _source(source), _target(q), _target(h)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=False)
    (out/'images').mkdir()
    (out/'trials').mkdir()
    started = time.monotonic()
    ev, other, channel, torch = evaluator, sdxl_vae, ddim_channel, evaluator.torch
    row = dict(method='E3-BCH59-Q080', status='running', owner=ALPHA,
        payload=dict(q=f'{q:08x}', h=f'{h:08x}', basis='caller-supplied fixed targets'),
        supplied_targets=dict(q=q, h=h), conditions={}, human_admissibility='missing',
        model_loading_seconds=0., model_loading_scope='caller supplied; excluded')
    bounded_reader = _BoundedReader(ev.reader, budget)
    def sync():
        if torch.cuda.is_initialized():
            torch.cuda.synchronize()
    def tensor(rgb):
        return ev.reader.tensor(rgb.astype(np.float32)/255)
    def save_rgb(path, rgb):
        return _save_rgb(path, rgb)
    def append(name, value):
        with (out/name).open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(value, allow_nan=False)+'\n')
            handle.flush()
    try:
        budget()
        ev.reader.vae.enable_gradient_checkpointing()
        construction_tick = time.monotonic()
        if source.shape != (512, 512, 3):
            raise ValueError('Fixed 512x512 RGB8 inputs required')
        layout, w, gaps = patterns(ev.profile, q)
        budget()
        first = f5.robust_pgd(bounded_reader, source.astype(np.float64)/255., layout, w, 46., 150, 4., 0.)
        original_rgb = np.clip(np.rint(first*255), 0, 255).astype(np.uint8)
        original_rgb, first_restore = restore_fragile(original_rgb, q, h, ev.profile)
        first_path = out/'images'/f'E1-initial-46-restored.png'
        original_rgb = save_rgb(first_path, original_rgb)
        budget()
        second = f5.robust_pgd(bounded_reader, original_rgb.astype(np.float64)/255., layout, w, 52., 50, 4., 0.)
        original_rgb = np.clip(np.rint(second*255), 0, 255).astype(np.uint8)
        original_rgb, second_restore = restore_fragile(original_rgb, q, h, ev.profile)
        initial_path = out/'images'/f'E1-initializer.png'
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
            call = rc.detect_rgb(rgb, ev.reader.latent(rgb), ALPHA, ev.profile,
                ev.features(rgb, 7), binding='soft', roster_size=1)
            metrics = ev.metrics(source, rgb)
            q_ok = exact_read(call, 'semantic', q)
            h_ok = exact_read(call, 'instance', h)
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

        state_path = out / 'images' / f'E1-state.png'
        current_rgb = save_rgb(state_path, original_rgb)
        current = tensor(current_rgb)
        current_clean, current_balls = qualify(current_rgb), balls(current)
        row.update(start_image=str(initial_path), initial_qualification=current_clean, initial_balls=current_balls)
        initializer_valid = current_clean['qualified'] and current_balls['feasible']
        cached = nine(current) if initializer_valid else None
        append('iterations.jsonl', dict(stage='baseline', image=str(initial_path), **(cached or {})))
        step, accepted = 0, 0
        while initializer_valid and step < 20:
            budget()
            phase_end = 10 if step < 10 else 20
            inactive = cached['max_loss']==0 and all(v==0 for v in cached['branch_losses'].values()) and all(
                d['finite_forward'] and d['hinges_inactive'] and d['score_hinge']<=0 and
                d['maximum_bit_hinge']<=0 for d in cached['branch_details'].values())
            if inactive and current_clean['qualified'] and current_balls['feasible']:
                append('iterations.jsonl', dict(stage='exact_inactive_noops',
                    logical_start=step, logical_end_exclusive=20, max_loss=cached['max_loss']))
                step = 20
                row['update_status'] = 'exact_inactive'
                break
            worst = cached['worst_index']
            iteration = dict(stage='iteration', logical_step=step,
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
                trial_record = dict(stage='proposal', logical_step=step,
                    proposal_order=order, fraction_B=fraction, status='running')
                try:
                    with torch.no_grad():
                        trial, projection_ok = projected_update(current-fraction*B*gradient/norm, base, clean, B, T, torch)
                        rgb = torch.round(trial.clamp(0, 1)*255)[0].permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                        path = out / 'trials' / f'E1-step{step:02d}-proposal{order}.png'
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
        row.update(planned_logical_iterations=20, completed_logical_iterations=step,
            accepted_updates=accepted,
            final_state_image=str(state_path), final_loss_vector=cached,
            final_balls=balls(tensor(load(state_path))))
        sync()
        row['refinement_seconds'] = time.monotonic()-refinement_tick
        row.setdefault('update_status', 'schedule_completed' if initializer_valid else 'invalid_initializer_no_refinement')

        quality_tick = time.monotonic()
        e1_final = load(state_path)
        e1_metrics = ev.metrics(source, e1_final)
        retain = strict_quality(e1_metrics)
        row['quality_branch'] = 'retain' if retain else 'contract_0.8'
        row['e1_final_quality'] = e1_metrics
        final_path = out/'images'/'E3-final.png'
        final = save_rgb(final_path, e1_final if retain else contract(e1_final, source))
        row['final_image'] = str(final_path)
        budget()
        final_qualification = qualify(final)
        row['selected_final_balls'] = balls(tensor(final))
        call = final_qualification['call']
        row['conditions']['clean'] = dict(image=str(final_path), calls={ALPHA:call},
            quality_source=final_qualification['metrics'],
            delivery=delivery(call, q, h),
            coded_diagnostics=final_qualification['coded_diagnostics'])
        row['final_qualification'] = final_qualification
        row['quality_qualification_seconds'] = time.monotonic()-quality_tick
        row['admitted'] = final_qualification['qualified']
        row['status'] = 'ok' if row['admitted'] else 'admission_failed'
        row['admission'] = dict(accepted=row['admitted'],
            strict_quality=final_qualification['strict_quality'],
            exact_q=final_qualification['q_exact'], exact_h=final_qualification['h_exact'],
            both_match=final_qualification['both_match'],
            no_retry=True)
        budget()
    except Exception:
        row.update(status='construction_failed', admitted=False,
            error=traceback.format_exc(), admission=dict(accepted=False, reason='execution_failure'))
    finally:
        sync()
        row['duration_seconds'] = time.monotonic()-started
        (out/'result.json').write_text(json.dumps(row, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return row


def supply_f5(source, evaluator, output_dir, budget):
    """E3-S1 prospective supplier: one frozen F5 r2 bootstrap, native h route.

    No F5 quality/full-match/exact-q inclusion filter is added. Bootstrap pixels
    are provenance only and must never replace the canonical E3 source.
    """
    source = _source(source)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    ev = evaluator
    row = dict(supplier='E3-S1-fresh-F5-r2', status='running',
        original_h_known=False, q_target_basis='bootstrap intended semantic word',
        h_target_basis='saved bootstrap native-decoded operational instance word',
        prospective=True)
    try:
        budget()
        rgb, report = f5.embed_rgb(source, ALPHA, ev.profile, ev.features(source, 7),
            _BoundedReader(ev.reader, budget), psnr_db=52., steps=150,
            target_margin=4., mask_power=0., band=(4, 32), whitening=1.,
            refine_rounds=1, binding='soft')
        rgb = _save_rgb(out/'F5-bootstrap.png', rgb)
        row.update(bootstrap_image=str(out/'F5-bootstrap.png'), report=report,
            bootstrap_seconds=time.monotonic()-started)
        budget()
        call = f5.detect_rgb(rgb, ev.reader.latent(rgb), ALPHA, ev.profile,
            ev.features(rgb, 7), binding_mode='combined', roster_size=1,
            band=(4, 32), whitening=1., binding='soft')
        row['native_call'] = call
        if not all(call[tier]['read'] and call[tier].get('decoded_code') is not None
                for tier in ('semantic', 'instance')):
            raise ValueError('Fresh F5 bootstrap native channels unreadable')
        q, h = _target(int(report['semantic_code'], 16)), _target(int(call['instance']['decoded_code'], 16))
        row.update(status='ok', q=q, h=h, payload=dict(q=f'{q:08x}', h=f'{h:08x}'),
            clean_decoded_q=call['semantic']['decoded_code'])
        budget()
    except Exception:
        row.update(status='supplier_failed', error=traceback.format_exc())
    finally:
        row['duration_seconds'] = time.monotonic()-started
        (out/'supplier.json').write_text(json.dumps(row, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return row
