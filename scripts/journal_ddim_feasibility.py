"""Prospective D1 smoke; internal tensors never count as attack outcomes."""
from __future__ import annotations
import argparse
import gc
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
from journal_readability_probe import Objective, patterns, payload, load, projected_update
from journal_vae_probe import Evaluator, write, SDXL, SDXL_REV
from journal_read_conditioning_probe import SCREEN as READABILITY, calls
from f4_transfer_probe import ASSETS, SOURCES
from f5_gate import OWNERS
from journal_ddim_channel import DifferentiableDDIM, continuous_projection, official_parity
CAP = 900.
BRANCHES = ('clean', 'sd15_vae', 'sdxl_vae') + tuple(
    f'ddim_{s}_seed{k}' for s in (.1, .2) for k in (0, 1, 2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    started, rows = time.monotonic(), []
    record = dict(schema='journal-ddim-feasibility-v2', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        config=dict(candidate='D1', start='fixed RC3 final RGB8', branches=list(BRANCHES),
            strengths=[.1, .2], smoke_seeds=[0], num_inference_steps=20,
            guidance_scale=1., eta=0., budget_seconds=CAP, optimization_cap_seconds=8100,
            checkpointing='nonreentrant full channel and fp32 reader',
            native_precision='float16 DDIM, float32 reader/SDXL', backward_loss_scale=1/1024,
            diagnostic_precision='float32 promoted native weights; no RGB8 rounding',
            diagnostic_scalar='fixed mean(w * projections), prospectively all cases',
            derivative_eps=[.003, .001], derivative_direction='negative unit RGB RMS gradient',
            derivative_max_relative_discrepancy=.35, probe_step_fractions=[.10, .50, 1.00],
            operator_source=1675, utility_source=468505,
            added_psnr_db=52., total_continuous_psnr_db=35.1,
            scope='diagnostic only; smoke trials never enter D1', human_admissibility='missing'),
        seeds=[0, 1, 2], sources=[1675, 468505], data_split='development', usd=0, outcome='running')
    write(out / 'run.json', record)
    torch = None

    def budget():
        if time.monotonic() - started >= CAP:
            raise TimeoutError('900-second aggregate smoke cap exhausted')

    def save():
        write(out / 'results.json', dict(rows=rows, qualification=record.get('qualification', 'pending')))
        write(out / 'run.json', record)

    def stage(name, fn, **identity):
        budget()
        row = dict(stage=name, status='running', **identity)
        rows.append(row)
        save()
        if torch is not None and torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        tick = time.monotonic()
        try:
            value = fn(row)
            row['status'] = 'ok'
            return value
        except Exception:
            row.update(status='failed', error=traceback.format_exc())
            raise
        finally:
            if torch is not None and torch.cuda.is_initialized():
                torch.cuda.synchronize()
                row.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved())
            row.update(duration_seconds=time.monotonic()-tick, elapsed_seconds=time.monotonic()-started)
            with (out / 'rows.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(row, allow_nan=False)+'\n')
            save()

    try:
        import torch
        from diffusers import AutoencoderKL
        import diffusers
        import three_threat_models as models
        record.update(torch_version=torch.__version__, diffusers_version=diffusers.__version__,
                      gpu=torch.cuda.get_device_name(0))
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')

        def prepare(row):
            ev = Evaluator()
            frozen, q, h, fixed = payload(ev, 1675)
            path = READABILITY / 'images/R3-1675-C1-clean.png'
            rgb = load(path)
            if rgb.shape != (512, 512, 3):
                raise ValueError('RC3 must be RGB8 512x512')
            source = load(SOURCES[1675])
            channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
            other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True,
                use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
            obj = Objective(ev, other, *patterns(ev.profile, q))
            obj.enable_checkpointing()
            record.update(payload=fixed, input_path=str(path), source_path=str(SOURCES[1675]),
                          sdxl_revision=SDXL_REV)
            row.update(input_shape=list(rgb.shape), reader_dtype=str(ev.reader.vae.dtype),
                channel_dtype=str(channel.pipe.vae.dtype), sdxl_dtype=str(other.dtype))
            return ev, frozen, rgb, source, q, h, channel, obj, other

        ev, frozen, rgb, source, q, h, channel, obj, other = stage('load', prepare)
        base = ev.reader.tensor(rgb.astype(np.float32)/255)
        clean = ev.reader.tensor(source.astype(np.float32)/255)
        B, T = math.sqrt(base.numel())*10**(-52/20), math.sqrt(base.numel())*10**(-35.1/20)

        def finite(value):
            if not bool(torch.isfinite(value).all()):
                raise ValueError('Nonfinite loss or gradient')

        def qualify(image):
            new, _, _ = calls(ev, image, OWNERS[0])
            call = new['combined']
            q_ok = bool(call['semantic']['read'] and int(call['semantic']['decoded_code'], 16) == q)
            h_ok = bool(call['instance']['read'] and int(call['instance']['decoded_code'], 16) == h)
            metrics = ev.metrics(source, image)
            psnr = metrics['psnr_db']
            psnr_ok = bool(metrics['psnr_infinite'] or (psnr is not None and psnr > 35))
            return dict(q_exact=q_ok, h_exact=h_ok, both_match=call['outcome'] == 'both_match',
                psnr=psnr, qualified=q_ok and h_ok and call['outcome'] == 'both_match' and psnr_ok)

        def initial(row):
            row.update(qualification=qualify(rgb), added_norm=0., total_norm=float((base-clean).norm()),
                       added_radius=B, total_radius=T)
            if not row['qualification']['qualified'] or row['total_norm'] > T:
                raise ValueError('RC3 initialization infeasible; no repair allowed')
        stage('initial_clean', initial)

        def branch_loss(x, index):
            if index < 3:
                return obj.loss_details(x, BRANCHES[index])
            k = index - 3
            value = channel.forward(x, (.1, .2)[k//3], k%3)
            return obj.loss_details(value.image, 'clean')

        def gradient(index, row, allow_inactive=True):
            x = base.detach().clone().requires_grad_(True)
            loss, detail = branch_loss(x, index)
            finite(loss)
            row.update(loss=float(loss.detach()), details=detail)
            scalar = loss
            row['gradient_scalar'] = 'native branch loss'
            if allow_inactive and detail['hinges_inactive']:
                del scalar, loss
                if index < 3:
                    p = obj.projection(x, BRANCHES[index])
                else:
                    k = index - 3
                    p = obj.projection(channel.forward(x, (.1, .2)[k//3], k%3).image, 'clean')
                scalar = (obj.w*p).mean()
                row['gradient_scalar'] = 'fixed linear diagnostic; inactive hinges'
            g, = torch.autograd.grad(scalar/1024, x)
            g = g.detach()*1024
            finite(g)
            row.update(gradient_norm=float(g.norm()), gradient_rms=float(g.square().mean().sqrt()),
                       gradient_exact_zero=bool((g == 0).all()))
            if row['gradient_exact_zero']:
                raise ValueError('Finite nonzero native input gradient required')
            return g

        for strength in (.1, .2):
            def parity(row, strength=strength):
                row['parity'] = official_parity(channel, rgb, base, strength, 0)
                if not row['parity']['parity_pass']:
                    raise ValueError('Exact RNG/timestep/RGB8 parity failed')
            stage('official_parity', parity, strength=strength, seed=0)
            stage('native_gradient', lambda row, s=strength: gradient(3 if s == .1 else 6, row),
                  strength=strength, seed=0)

        other.to('cpu')
        ev.lpips.to('cpu')
        gc.collect()
        torch.cuda.empty_cache()
        stage('fp32_prepare', lambda row: channel.set_precision(torch.float32, diagnostic=True))
        for strength in (.1, .2):
            def derivative(row, strength=strength):
                x = base.detach().clone().requires_grad_(True)
                value = channel.forward(x, strength, 0, quantize_input=False, quantize_output=False)
                scalar = (obj.w*continuous_projection(obj, value.continuous)).mean()
                finite(scalar)
                row.update(loss=float(scalar.detach()), scalar='fixed linear projection diagnostic all cases',
                           timesteps=value.timesteps, output_dtype=str(value.continuous.dtype))
                grad, = torch.autograd.grad(scalar, x)
                finite(grad)
                rms = float(grad.square().mean().sqrt())
                row.update(gradient_norm=float(grad.norm()), gradient_rms=rms)
                if rms == 0:
                    raise ValueError('Zero fp32 diagnostic gradient')
                direction = -grad.detach()/rms
                ad = float((grad*direction).sum())
                del scalar, grad, x, value
                row.update(autograd_directional_derivative=ad, finite_differences=[])
                save()
                with torch.no_grad():
                    for eps in (.003, .001):
                        vals = []
                        for sign in (-1, 1):
                            budget()
                            trial = channel.forward(base+sign*eps*direction, strength, 0,
                                quantize_input=False, quantize_output=False)
                            scalar = (obj.w*continuous_projection(obj, trial.continuous)).mean()
                            finite(scalar)
                            vals.append(float(scalar))
                            del trial, scalar
                        fd = (vals[1]-vals[0])/(2*eps)
                        relative = abs(ad-fd)/max(abs(ad), abs(fd), 1e-8)
                        passed = bool(math.isfinite(fd) and ad*fd > 0 and relative <= .35)
                        row['finite_differences'].append(dict(epsilon_rms=eps, minus=vals[0], plus=vals[1],
                            autograd=ad, finite_difference=fd, relative_discrepancy=relative, passed=passed))
                        save()
                if not any(v['passed'] for v in row['finite_differences']):
                    raise ValueError('Continuous fp32 derivative criterion failed')
            stage('fp32_derivative', derivative, strength=strength, seed=0)
        stage('native_restore', lambda row: channel.set_precision(torch.float16))
        for strength in (.1, .2):
            def restored_parity(row, strength=strength):
                row['parity'] = official_parity(channel, rgb, base, strength, 0)
                if not row['parity']['parity_pass']:
                    raise ValueError('Native parity failed after fp32 restore')
            stage('native_restore_parity', restored_parity, strength=strength, seed=0)
        other.to('cuda')

        # Fixed before any outcome: the prior RC3 lost-q identity, not a source
        # selected by this smoke. Operator diagnostics above remain on 1675.
        frozen, q, h, fixed = payload(ev, 468505)
        utility_path = READABILITY / 'images/R3-468505-C1-clean.png'
        rgb = load(utility_path)
        source = load(SOURCES[468505])
        obj = Objective(ev, other, *patterns(ev.profile, q))
        obj.enable_checkpointing()
        base = ev.reader.tensor(rgb.astype(np.float32)/255)
        clean = ev.reader.tensor(source.astype(np.float32)/255)
        record.update(utility_payload=fixed, utility_input_path=str(utility_path),
                      utility_source_path=str(SOURCES[468505]))
        stage('utility_initial_clean', initial, source_id=468505)

        def nine(x, row):
            values, details, seconds = [], [], []
            row.update(branch_losses={}, branch_details={}, branch_seconds={})
            with torch.no_grad():
                for index in range(9):
                    budget()
                    torch.cuda.synchronize()
                    tick = time.monotonic()
                    loss, detail = branch_loss(x, index)
                    finite(loss)
                    values.append(float(loss))
                    details.append(detail)
                    torch.cuda.synchronize()
                    seconds.append(time.monotonic()-tick)
                    row['branch_losses'][BRANCHES[index]] = values[-1]
                    row['branch_details'][BRANCHES[index]] = detail
                    row['branch_seconds'][BRANCHES[index]] = seconds[-1]
                    save()
            row.update(max_loss=max(values), worst_index=int(np.argmax(values)))
            return row.copy()
        baseline = stage('nine_branch_baseline', lambda row: nine(base, row), source_id=468505)
        g = stage('initial_worst_gradient', lambda row: gradient(baseline['worst_index'], row, False),
                  branch=BRANCHES[baseline['worst_index']])
        utility = []
        for fraction in (.10, .50, 1.00):
            def probe(row, fraction=fraction):
                with torch.no_grad():
                    trial, feasible = projected_update(base-fraction*B*g/g.norm(), base, clean, B, T, torch)
                    image = torch.round(trial.clamp(0, 1)*255)[0].permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                    row.update(projected_feasible=feasible, rgb8_unchanged=bool(np.array_equal(rgb, image)),
                        qualification=qualify(image), added_norm=float((trial-base).norm()),
                        total_norm=float((trial-clean).norm()), total_frozen_rms=float(np.sqrt(np.mean(
                            ((image.astype(np.float64)-frozen.astype(np.float64))/255)**2))))
                    nine(ev.reader.tensor(image.astype(np.float32)/255), row)
                    row.update(loss_delta=row['max_loss']-baseline['max_loss'],
                        useful=bool(feasible and row['qualification']['qualified'] and row['max_loss'] < baseline['max_loss']))
                    utility.append(row['useful'])
            stage('rounded_local_probe', probe, fraction_B=fraction)
        del g
        if not any(utility):
            raise ValueError('No fixed rounded nine-branch proposal is useful')

        native_grads = [r['duration_seconds'] for r in rows if r['stage'] in ('native_gradient', 'initial_worst_gradient')]
        clean_seconds = max(r['duration_seconds'] for r in rows if r['stage'] in ('initial_clean', 'utility_initial_clean'))
        forward_seconds = sum(baseline['branch_seconds'].values())
        per_iteration = forward_seconds+max(native_grads)+clean_seconds
        projected = 480*per_iteration+rows[0]['duration_seconds']+12*forward_seconds+12*clean_seconds
        record['throughput'] = dict(nine_forward_seconds=forward_seconds,
            worst_forward_backward_seconds=max(native_grads), clean_check_seconds=clean_seconds,
            conservative_iteration_seconds=per_iteration, full_40_by_12_seconds=projected,
            includes='loads + 480*(nine forwards + worst measured forward/backward + clean check) + final clean/nine qualification',
            budget_feasible=projected <= 8100)
        record['qualification'] = 'smoke_pass' if projected <= 8100 else 'budget_infeasible'
        record['outcome'] = 'completed_feasibility_only'
        budget()
    except Exception:
        record.update(outcome='smoke_infeasible', qualification='smoke_infeasible', error=traceback.format_exc())
        raise
    finally:
        record.update(duration_seconds=time.monotonic()-started, rows=len(rows))
        save()


if __name__ == '__main__':
    main()
