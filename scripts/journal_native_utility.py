"""D2 native-measured utility screen; all proposals are discarded internal probes."""
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
from journal_readability_probe import Objective, patterns, payload, load, projected_update
from journal_vae_probe import Evaluator, write, SDXL, SDXL_REV
from journal_read_conditioning_probe import SCREEN as READABILITY, calls
from f4_transfer_probe import ASSETS, SOURCES
from f5_gate import OWNERS
from journal_ddim_channel import DifferentiableDDIM, official_parity

CAP, WRITER_CAP, SID = 300., 3300., 468505
BRANCHES = ('clean', 'sd15_vae', 'sdxl_vae') + tuple(
    f'ddim_{s}_seed{k}' for s in (.1, .2) for k in (0, 1, 2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    started, rows, torch = time.monotonic(), [], None
    record = dict(schema='journal-native-utility-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        config=dict(candidate='D2', source_id=SID, start='fixed RC3 final RGB8',
            branches=list(BRANCHES), strengths=[.1, .2], num_inference_steps=20,
            guidance_scale=1., eta=0., budget_seconds=CAP, writer_cap_seconds=WRITER_CAP,
            native_precision='float16 DDIM, float32 reader/SDXL', backward_loss_scale=1.,
            fractions_B=[.10, .50, 1.00], added_psnr_db=52., total_psnr_db=35.1,
            improvement_rule='baseline_max - proposal_max >= max(1e-6, 1e-4*baseline_max)',
            clean_constraints='exact operational q/h, both_match, PSNR>35, SSIM>.9, LPIPS<.1',
            parity_coverage='source 1675 seed 0 both strengths plus all six source 468505 identities',
            scope='internal utility only; no attack outcomes or retained candidate',
            human_admissibility='missing'), seeds=[0, 1, 2], sources=[SID],
        data_split='development', usd=0, outcome='running', qualification='pending')

    def save():
        record['elapsed_seconds'] = time.monotonic() - started
        write(out / 'results.json', dict(rows=rows, qualification=record['qualification']))
        write(out / 'run.json', record)

    def budget():
        if time.monotonic() - started >= CAP:
            raise TimeoutError('300-second native utility screen cap exhausted')

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
            budget()
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
            row.update(duration_seconds=time.monotonic()-tick,
                       elapsed_seconds=time.monotonic()-started)
            with (out / 'rows.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(row, allow_nan=False)+'\n')
            save()

    save()
    try:
        import torch
        import diffusers
        from diffusers import AutoencoderKL
        import three_threat_models as models
        record.update(torch_version=torch.__version__, diffusers_version=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0), original_flags=dict(
                matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
                cudnn_benchmark=torch.backends.cudnn.benchmark,
                cudnn_deterministic=torch.backends.cudnn.deterministic,
                float32_matmul_precision=torch.get_float32_matmul_precision(),
                cpu_threads=torch.get_num_threads()))
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')

        def prepare(row):
            ev = Evaluator()
            frozen, q, h, fixed = payload(ev, SID)
            path = READABILITY / f'images/R3-{SID}-C1-clean.png'
            rgb, source = load(path), load(SOURCES[SID])
            if rgb.shape != (512, 512, 3) or source.shape != rgb.shape:
                raise ValueError('Fixed RGB8 512x512 inputs required')
            channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
            other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True,
                use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
            obj = Objective(ev, other, *patterns(ev.profile, q))
            obj.enable_checkpointing()
            record.update(payload=fixed, input_path=str(path), source_path=str(SOURCES[SID]),
                          sdxl_revision=SDXL_REV, effective_cpu_threads=torch.get_num_threads())
            row.update(reader_dtype=str(ev.reader.vae.dtype), channel_dtype=str(channel.pipe.vae.dtype),
                       sdxl_dtype=str(other.dtype), checkpointing='nonreentrant full path and reader')
            return ev, rgb, source, q, h, channel, obj

        ev, rgb, source, q, h, channel, obj = stage('load', prepare)
        base = ev.reader.tensor(rgb.astype(np.float32)/255)
        clean = ev.reader.tensor(source.astype(np.float32)/255)
        B, T = math.sqrt(base.numel())*10**(-52/20), math.sqrt(base.numel())*10**(-35.1/20)

        def balls(x):
            added, total = float((x-base).norm()), float((x-clean).norm())
            box = bool(((x >= 0) & (x <= 1)).all())
            return dict(added_norm=added, total_norm=total, added_radius=B, total_radius=T,
                        box=box, feasible=box and added <= B and total <= T)

        def qualify(image):
            new, _, _ = calls(ev, image, OWNERS[0])  # Suspect-only detector; no source features.
            call, metrics = new['combined'], ev.metrics(source, image)
            q_ok = bool(call['semantic']['read'] and int(call['semantic']['decoded_code'], 16) == q)
            h_ok = bool(call['instance']['read'] and int(call['instance']['decoded_code'], 16) == h)
            psnr_ok = bool(metrics['psnr_infinite'] or
                           (metrics['psnr_db'] is not None and metrics['psnr_db'] > 35))
            quality_ok = psnr_ok and metrics['ssim_rgb'] > .9 and metrics['lpips'] < .1
            return dict(call=call, metrics=metrics, q_exact=q_ok, h_exact=h_ok,
                both_match=call['outcome'] == 'both_match', strict_quality=quality_ok,
                qualified=q_ok and h_ok and call['outcome'] == 'both_match' and quality_ok)

        def initial(row):
            row.update(qualification=qualify(rgb), balls=balls(base))
            if not row['qualification']['qualified'] or not row['balls']['feasible']:
                raise ValueError('Fixed RC3 initialization infeasible; no repair or substitution')
        stage('initial_clean', initial)
        operator_rgb = load(READABILITY / 'images/R3-1675-C1-clean.png')
        operator_base = ev.reader.tensor(operator_rgb.astype(np.float32)/255)
        for strength in (.1, .2):
            def operator_parity(row, strength=strength):
                row['parity'] = official_parity(channel, operator_rgb, operator_base, strength, 0)
                if not row['parity']['parity_pass']:
                    raise ValueError('Exact operator-source official parity failed')
            stage('official_parity', operator_parity, source_id=1675, strength=strength, seed=0)
        for strength in (.1, .2):
            for seed in (0, 1, 2):
                def parity(row, strength=strength, seed=seed):
                    row['parity'] = official_parity(channel, rgb, base, strength, seed)
                    if not row['parity']['parity_pass']:
                        raise ValueError('Exact native official parity failed')
                stage('official_parity', parity, source_id=SID, strength=strength, seed=seed)

        def branch_loss(x, index):
            if index < 3:
                loss, detail = obj.loss_details(x, BRANCHES[index])
            else:
                k = index - 3
                loss, detail = obj.loss_details(channel.forward(x, (.1, .2)[k//3], k%3).image, 'clean')
            if not bool(torch.isfinite(loss)) or not detail['finite_forward']:
                raise ValueError('Nonfinite native branch objective')
            detail.update(fixed_q_score=9-detail['score_hinge'],
                          minimum_normalized_bit_gap=1-detail['maximum_bit_hinge'])
            return loss, detail

        def nine(x, row):
            row.update(branch_losses={}, branch_details={}, branch_seconds={})
            with torch.no_grad():
                for i, branch in enumerate(BRANCHES):
                    budget()
                    torch.cuda.synchronize()
                    tick = time.monotonic()
                    loss, detail = branch_loss(x, i)
                    row['branch_losses'][branch], row['branch_details'][branch] = float(loss), detail
                    torch.cuda.synchronize()
                    row['branch_seconds'][branch] = time.monotonic()-tick
                    save()
            values = list(row['branch_losses'].values())
            row.update(max_loss=max(values), worst_index=int(np.argmax(values)))
            return row

        baseline = stage('nine_branch_baseline', lambda row: nine(base, row))
        if baseline['max_loss'] <= 0 or all(d['hinges_inactive'] for d in baseline['branch_details'].values()):
            raise ValueError('Unexpected inactive baseline despite prior lost-q identity')

        def gradient(row):
            x = base.detach().clone().requires_grad_(True)
            loss, detail = branch_loss(x, baseline['worst_index'])
            g, = torch.autograd.grad(loss, x)  # Unit loss scale; heuristic only.
            g = g.detach()
            if not bool(torch.isfinite(g).all()) or not bool(torch.isfinite(g.norm())) or float(g.norm()) <= 0:
                raise ValueError('Finite nonzero native gradient required')
            row.update(loss=float(loss.detach()), details=detail, gradient_norm=float(g.norm()),
                       gradient_rms=float(g.square().mean().sqrt()), gradient_scalar='native positive worst loss')
            if not bool(torch.isfinite(g).all()) or row['gradient_norm'] <= 0:
                raise ValueError('Finite nonzero native gradient required')
            return g
        g = stage('initial_worst_gradient', gradient, branch=BRANCHES[baseline['worst_index']])
        margin, useful = max(1e-6, 1e-4*baseline['max_loss']), []
        for fraction in (.10, .50, 1.00):
            def proposal(row, fraction=fraction):
                with torch.no_grad():
                    from PIL import Image
                    trial, projection_ok = projected_update(base-fraction*B*g/g.norm(), base, clean, B, T, torch)
                    image = torch.round(trial.clamp(0, 1)*255)[0].permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                    path = out / f'discarded-internal-proposal-{fraction:.2f}B.png'
                    Image.fromarray(image).save(path)
                    image = load(path)  # Saved PNG pixels are authoritative for all checks.
                    rounded = ev.reader.tensor(image.astype(np.float32)/255)
                    row.update(image=str(path), projected_feasible=projection_ok, continuous_balls=balls(trial), rounded_balls=balls(rounded),
                        changed_rgb_components=int(np.count_nonzero(image != rgb)),
                        changed_pixels=int(np.count_nonzero(np.any(image != rgb, axis=2))))
                    tick = time.monotonic()
                    row['qualification'] = qualify(image)
                    row['clean_check_seconds'] = time.monotonic()-tick
                    nine(rounded, row)
                    decrease = baseline['max_loss']-row['max_loss']
                    row.update(loss_delta=-decrease, loss_decrease=decrease, required_decrease=margin,
                        branch_deltas={b: row['branch_losses'][b]-baseline['branch_losses'][b] for b in BRANCHES})
                    reasons = [name for name, passed in (
                        ('projection', projection_ok), ('continuous_balls', row['continuous_balls']['feasible']),
                        ('rounded_balls', row['rounded_balls']['feasible']),
                        ('clean_qualification', row['qualification']['qualified']), ('decrease_margin', decrease >= margin)) if not passed]
                    row.update(useful=not reasons, rejection_reasons=reasons, discarded=True)
                    useful.append(not reasons)
            stage('rounded_local_proposal', proposal, fraction_B=fraction)
        forwards = max(sum(r['branch_seconds'].values()) for r in rows if 'branch_seconds' in r)
        gradient_s = next(r['duration_seconds'] for r in rows if r['stage'] == 'initial_worst_gradient')
        clean_s = max([r['clean_check_seconds'] for r in rows if 'clean_check_seconds' in r] +
                      [r['duration_seconds'] for r in rows if r['stage'] == 'initial_clean'])
        per_iteration = forwards + gradient_s + 3*(forwards+clean_s)
        projected = rows[0]['duration_seconds'] + 240*per_iteration + 24*(forwards+clean_s)
        record['throughput'] = dict(nine_forward_seconds=forwards, forward_backward_seconds=gradient_s,
            clean_check_seconds=clean_s, conservative_iteration_seconds=per_iteration,
            twenty_by_twelve_seconds=projected, budget_feasible=projected <= WRITER_CAP,
            includes='load + 240*(current nine + gradient + three*(proposal nine + clean)) + 24 baseline/final qualifications')
        record.update(utility_pass=any(useful), qualification=('utility_negative' if not any(useful) else
            'utility_pass' if projected <= WRITER_CAP else 'budget_infeasible'), outcome='completed_internal_utility_only')
    except Exception:
        record.update(outcome='failed_internal_utility', qualification='ineligible', error=traceback.format_exc())
        raise
    finally:
        record.update(duration_seconds=time.monotonic()-started, rows=len(rows))
        save()


if __name__ == '__main__':
    main()
