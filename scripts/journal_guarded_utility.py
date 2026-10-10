"""Prospective D3 feasibility guard screen; saved probes are discarded candidates.

Native gradients are unchanged D2 unvalidated heuristics. Actual source-blind
F5-RC1 calls certify guards; objective margins never certify native detection.
"""
from __future__ import annotations
import time
PROCESS_STARTED = time.monotonic()
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
from journal_readability_probe import Objective, CONDITIONS, DISCOVERY, patterns, payload, load, projected_update
from journal_vae_probe import Evaluator, write, SDXL, SDXL_REV
from journal_read_conditioning_probe import SCREEN, calls
from journal_binding_probe import delivery
from journal_native_writer import strict_quality
from journal_native_utility import BRANCHES
from journal_ddim_channel import DifferentiableDDIM
from f4_transfer_probe import MAIN, ASSETS, SOURCES
from f5_gate import OWNERS
from scripts import journal_read_conditioning as rc

IDS, FRACTIONS = (6012, 468505), (.10, .50, 1.00)
CAP, WRITER_CAP, GRADIENT_FLOOR = 180., 3300., 1.890
FORMULA = 'L + 12*max(P) + 12*max(A) + 240*max(Gt,1.890) + 720*max(V) + 12*max(F) + 30'
PARITY = MAIN / '.thesis-build/dev-runs/20261010-1206-native-utility'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    started = PROCESS_STARTED
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / 'discarded').mkdir()
    rows, torch = [], None
    inventory = [dict(source_id=sid, proposal_order=order, fraction_B=fraction, status='unrun')
        for sid in IDS for order, fraction in enumerate(FRACTIONS)]
    record = dict(schema='journal-guarded-utility-v1', commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=sys.argv,
        sources=list(IDS), seeds=[0, 1, 2], data_split='development', usd=0,
        outcome='running', qualification='pending', selected_candidate=None, proposal_inventory=inventory,
        config=dict(candidate='D3', protocol='research/journal-upgrade-20261009/post-d2-method-decision.md',
            start='RC3 saved RGB8', source_selection='development-adaptive fixed 6012 then 468505',
            detector='source-blind F5-RC1', branches=list(BRANCHES), fractions_B=list(FRACTIONS),
            budget_seconds=CAP, writer_cap_seconds=WRITER_CAP, estimate_formula=FORMULA,
            gradient_floor_seconds=GRADIENT_FLOOR, bookkeeping_seconds=30.,
            added_psnr_db=52., total_psnr_db=35.1, strengths=[.1, .2], seeds=[0, 1, 2],
            num_inference_steps=20, guidance_scale=1., eta=0., sdxl_revision=SDXL_REV,
            searched_threshold=8.259326826136963, recomputed_threshold=4.982033056390042,
            precision='float16 DDIM; float32 reader/SDXL', gradient='first maximum branch; unit scale; unvalidated D2 heuristic',
            guard='both saved/reloaded VAE outputs: semantic read, exact intended q, found, content_match',
            clean_constraints='exact original q/operational h, both_match, strict quality, both distortion balls',
            improvement_rule='baseline_max - proposal_max >= max(1e-6, 1e-4*baseline_max)',
            scope='internal screen only; all images discarded as candidates', human_admissibility='missing',
            parity_evidence=str(PARITY), parity_policy='reuse eight official D2 parity comparisons; no new parity run'))

    def save():
        record['elapsed_seconds'] = time.monotonic()-started
        write(out / 'results.json', dict(rows=rows, qualification=record['qualification']))
        write(out / 'run.json', record)

    def budget():
        if time.monotonic()-started >= CAP:
            raise TimeoutError('D3 inclusive 180-second screen cap exhausted; no retries')

    def sync():
        if torch is not None and torch.cuda.is_initialized():
            torch.cuda.synchronize()

    def stage(name, fn, **identity):
        budget()
        row = dict(stage=name, status='running', **identity)
        rows.append(row)
        entry = next((r for r in inventory if name=='V' and r['source_id']==identity.get('source_id') and
            r['proposal_order']==identity.get('proposal_order')), None)
        if entry is not None:
            entry['status'] = 'running'
        save()
        sync()
        # L includes interpreter-side imports/setup before model loading; no gap
        # in the prospective all-in estimate is hidden in the +30 allowance.
        tick = started if name == 'L' else time.monotonic()
        try:
            value = fn(row)
            sync()
            budget()
            row['status'] = 'ok'
            if entry is not None:
                entry.update(status='ok', eligible=row['eligible'])
            return value
        except Exception:
            row.update(status='failed', error=traceback.format_exc())
            if entry is not None:
                entry.update(status='failed', error=row['error'])
            raise
        finally:
            sync()
            row.update(duration_seconds=time.monotonic()-tick, elapsed_seconds=time.monotonic()-started)
            with (out / 'rows.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(row, allow_nan=False)+'\n')
                handle.flush()
            save()

    save()
    try:
        def models_load(row):
            nonlocal torch
            import torch as torch_module
            import diffusers
            from diffusers import AutoencoderKL
            import three_threat_models as models
            torch = torch_module
            if diffusers.__version__ != '0.35.1':
                raise ValueError('Pinned diffusers 0.35.1 required')
            # Inspect retained evidence without rerunning parity or changing its record.
            evidence = json.loads((PARITY / 'results.json').read_text(encoding='utf-8'))['rows']
            parity = [r for r in evidence if r['stage']=='official_parity']
            expected = {(1675, s, 0) for s in (.1, .2)} | {(468505, s, k) for s in (.1, .2) for k in (0, 1, 2)}
            if len(parity)!=8 or {(r['source_id'], r['strength'], r['seed']) for r in parity}!=expected or not all(
                    r['status']=='ok' and r['parity']['parity_pass'] for r in parity):
                raise ValueError('Eight frozen official D2 parity records required')
            row['reused_parity_comparisons'] = 8
            ev = Evaluator()
            channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
            other = AutoencoderKL.from_pretrained(SDXL, local_files_only=True,
                use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
            record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
                gpu=torch.cuda.get_device_name(0), cpu_threads=torch.get_num_threads(),
                matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
                float32_matmul_precision=torch.get_float32_matmul_precision())
            return ev, channel, other
        ev, channel, other = stage('L', models_load)
        from PIL import Image

        def tensor(rgb):
            return ev.reader.tensor(rgb.astype(np.float32)/255)

        def saved(path, rgb):
            Image.fromarray(rgb).save(path)
            return load(path)

        source_passes = []
        for sid in IDS:
            def setup(row):
                _, q, h, fixed = payload(ev, sid)
                path = SCREEN / f'images/R3-{sid}-C1-clean.png'
                rgb, source = load(path), load(SOURCES[sid])
                if rgb.shape!=(512, 512, 3) or source.shape!=rgb.shape:
                    raise ValueError('Fixed RGB8 512x512 inputs required')
                obj = Objective(ev, other, *patterns(ev.profile, q))
                obj.enable_checkpointing()
                base, clean = tensor(rgb), tensor(source)
                row.update(payload=fixed, input_path=str(path), source_path=str(SOURCES[sid]))
                return rgb, source, q, h, obj, base, clean
            rgb, source, q, h, obj, base, clean = stage('P', setup, source_id=sid)
            B, T = math.sqrt(base.numel())*10**(-52/20), math.sqrt(base.numel())*10**(-35.1/20)

            def balls(x):
                a, t = float((x-base).norm()), float((x-clean).norm())
                box = bool(((x>=0)&(x<=1)).all())
                return dict(added_norm=a, total_norm=t, added_radius=B, total_radius=T,
                    box=box, feasible=box and a<=B and t<=T)

            def qualify(image):
                call = calls(ev, image, OWNERS[0])[0]['combined']
                metrics = ev.metrics(source, image)
                q_ok = bool(call['semantic']['read'] and int(call['semantic']['decoded_code'], 16)==q)
                h_ok = bool(call['instance']['read'] and int(call['instance']['decoded_code'], 16)==h)
                quality = strict_quality(metrics)
                return dict(call=call, metrics=metrics, q_exact=q_ok, h_exact=h_ok,
                    both_match=call['outcome']=='both_match', strict_quality=quality,
                    qualified=q_ok and h_ok and call['outcome']=='both_match' and quality)

            def transform(image, condition, label):
                if condition=='clean':
                    transformed = image.copy()
                else:
                    vae = ev.reader.vae if condition=='sd15_vae' else other
                    with torch.inference_mode():
                        x = tensor(image)
                        z = vae.encode(x*2-1).latent_dist.mode()
                        y = vae.decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
                    transformed = np.rint(np.clip(y*.5+.5, 0, 1)*255).astype(np.uint8)
                path = out / 'discarded' / f'{sid}-{label}-{condition}.png'
                return path, saved(path, transformed)

            def joint(call):
                semantic = call['semantic']
                return bool(semantic['read'] and int(semantic['decoded_code'], 16)==q and
                    semantic['found'] and semantic['content_match'])

            def guard(image, label):
                guards = {}
                for condition in CONDITIONS[1:]:
                    budget()
                    path, pixels = transform(image, condition, label)
                    call = calls(ev, pixels, OWNERS[0])[0]['combined']
                    guards[condition] = dict(image=str(path), call=call, joint_fixed_q=joint(call))
                return dict(conditions=guards, passed=all(g['joint_fixed_q'] for g in guards.values()))

            def branch_loss(x, index):
                if index<3:
                    loss, detail = obj.loss_details(x, BRANCHES[index])
                else:
                    k = index-3
                    loss, detail = obj.loss_details(channel.forward(x, (.1, .2)[k//3], k%3).image, 'clean')
                if not bool(torch.isfinite(loss)) or not detail['finite_forward']:
                    raise ValueError('Nonfinite native branch objective')
                return loss, detail

            def nine(x, row):
                losses, details = {}, {}
                with torch.no_grad():
                    for i, branch in enumerate(BRANCHES):
                        budget()
                        loss, detail = branch_loss(x, i)
                        losses[branch], details[branch] = float(loss), detail
                values = list(losses.values())
                row.update(branch_losses=losses, branch_details=details, max_loss=max(values),
                    worst_index=int(np.argmax(values)))

            def initial(row):
                baseline_rgb = saved(out/'discarded'/f'{sid}-baseline.png', rgb)
                row.update(qualification=qualify(baseline_rgb), balls=balls(tensor(baseline_rgb)),
                    guard=guard(baseline_rgb, 'baseline-guard'))
                nine(tensor(baseline_rgb), row)
                row['baseline_feasible'] = row['qualification']['qualified'] and row['balls']['feasible'] and row['guard']['passed']
                return row
            baseline = stage('A', initial, source_id=sid)
            if not baseline['baseline_feasible']:
                raise ValueError('Fixed RC3 initialization violates D3 constraints; no repair')

            def gradient(row):
                x = base.detach().clone().requires_grad_(True)
                loss, detail = branch_loss(x, baseline['worst_index'])
                g, = torch.autograd.grad(loss, x)
                g = g.detach()
                norm = float(g.norm())
                if not bool(torch.isfinite(g).all()) or not math.isfinite(norm) or norm<=0:
                    raise ValueError('Finite nonzero first-worst native gradient required')
                row.update(branch=BRANCHES[baseline['worst_index']], loss=float(loss.detach()),
                    details=detail, gradient_norm=norm)
                return g
            g = stage('Gt', gradient, source_id=sid)
            margin, eligible = max(1e-6, 1e-4*baseline['max_loss']), []
            for order, fraction in enumerate(FRACTIONS):
                def proposal(row, fraction=fraction, order=order):
                    with torch.no_grad():
                        trial, projection_ok = projected_update(base-fraction*B*g/g.norm(), base, clean, B, T, torch)
                        image = torch.round(trial.clamp(0, 1)*255)[0].permute(1, 2, 0).cpu().numpy().astype(np.uint8)
                        path = out/'discarded'/f'{sid}-proposal{order}.png'
                        image = saved(path, image)
                        rounded = tensor(image)
                        row.update(image=str(path), projected_feasible=projection_ok,
                            continuous_balls=balls(trial), rounded_balls=balls(rounded),
                            changed_rgb_components=int(np.count_nonzero(image!=rgb)),
                            changed_pixels=int(np.count_nonzero(np.any(image!=rgb, axis=2))),
                            qualification=qualify(image))
                        nine(rounded, row)
                        row['guard'] = guard(image, f'proposal{order}-guard')
                    decrease = baseline['max_loss']-row['max_loss']
                    reasons = [name for name, passed in (
                        ('projection', projection_ok), ('continuous_balls', row['continuous_balls']['feasible']),
                        ('rounded_balls', row['rounded_balls']['feasible']),
                        ('clean_qualification', row['qualification']['qualified']), ('G', row['guard']['passed']),
                        ('decrease_margin', decrease>=margin)) if not passed]
                    row.update(loss_decrease=decrease, required_decrease=margin,
                        eligible=not reasons, rejection_reasons=reasons, discarded=True)
                    eligible.append(not reasons)
                stage('V', proposal, source_id=sid, proposal_order=order, fraction_B=fraction)
            del g
            source_passes.append(dict(source_id=sid, utility_pass=any(eligible)))
            record['source_results'] = source_passes

            def final(row):
                # Baseline only: never qualify or retain a successful screen proposal.
                final_rgb = load(out/'discarded'/f'{sid}-baseline.png')
                row.update(conditions={}, final_balls=balls(tensor(final_rgb)))
                for condition in CONDITIONS:
                    budget()
                    path, pixels = transform(final_rgb, condition, 'final-baseline')
                    features, latent = ev.features(pixels, 7), ev.reader.latent(pixels)
                    owner_calls = {owner:rc.detect_rgb(pixels, latent, owner, ev.profile, features,
                        binding='soft', roster_size=1) for owner in OWNERS[:2]}
                    c0_path = DISCOVERY/'images'/f'{sid}-f5-C0-{condition}.png'
                    c0 = load(c0_path)
                    if condition=='clean' and not np.array_equal(c0, source):
                        raise ValueError('Exact shared discovery C0 differs from canonical source')
                    intended = owner_calls[OWNERS[0]]
                    row['conditions'][condition] = dict(image=str(path), calls=owner_calls,
                        c0_image=str(c0_path), c0_call=calls(ev, c0, OWNERS[0])[0]['combined'],
                        c0_scope='fresh call on exact shared D2/discovery pixels; not independent evidence',
                        delivery=delivery(intended, q, h), joint_fixed_q=joint(intended),
                        quality_source=ev.metrics(source, pixels), quality_input=ev.metrics(final_rgb, pixels))
                c = row['conditions']['clean']
                row['qualified'] = bool(row['final_balls']['feasible'] and strict_quality(c['quality_source']) and
                    c['delivery']['both_exact'] and c['calls'][OWNERS[0]]['outcome']=='both_match' and
                    all(row['conditions'][b]['joint_fixed_q'] for b in CONDITIONS[1:]) and
                    not any(row['conditions'][b]['c0_call']['watermark_found'] or
                        row['conditions'][b]['calls'][OWNERS[1]]['watermark_found'] for b in CONDITIONS))
                write(out/f'baseline-final-{sid}.json', row)
            stage('F', final, source_id=sid)
            save()

        components = {name:max(r['duration_seconds'] for r in rows if r['stage']==name)
            for name in ('L', 'P', 'A', 'Gt', 'V', 'F')}
        components['Gt_allowance'] = max(components['Gt'], GRADIENT_FLOOR)
        E = components['L']+12*components['P']+12*components['A']+240*components['Gt_allowance']+720*components['V']+12*components['F']+30
        finals_ok = all(r['qualified'] for r in rows if r['stage']=='F')
        utility_ok = all(r['utility_pass'] for r in source_passes)
        record.update(source_results=source_passes, utility_pass=utility_ok,
            baseline_final_qualification_pass=finals_ok,
            throughput=dict(formula=FORMULA, components_seconds=components, estimated_writer_seconds=E,
                budget_feasible=E<=WRITER_CAP,
                coverage='L all evaluator/SDXL/DDIM loads; P payload/source/objective setup; A saved baseline, clean/balls/nine/G; Gt full worst forward/backward; V projection/PNG/balls/clean/nine/G; F saved clean+both VAE, all owner0/owner1 and fresh shared-C0 calls, both quality comparisons, full record writing; +30 bookkeeping',
                shortcuts_credited=False, caveat='measured extrapolation, not guaranteed runtime bound'),
            outcome='completed_internal_utility_only', qualification=(
                'budget_infeasible' if E>WRITER_CAP else 'utility_negative' if not utility_ok else
                'baseline_final_failure' if not finals_ok else 'utility_pass'))
        budget()
    except Exception:
        record.update(outcome='failed_internal_utility', qualification='ineligible', error=traceback.format_exc())
        raise
    finally:
        record.update(duration_seconds=time.monotonic()-started, budget_overrun=time.monotonic()-started>=CAP,
            rows=len(rows), completed_proposals=sum(r['status']=='ok' for r in inventory),
            missing_or_failed_proposals=sum(r['status']!='ok' for r in inventory))
        if record['budget_overrun']:
            record.update(outcome='budget_incomplete', qualification='ineligible', utility_pass=False)
        save()
        # Include completion-record writing in the actual inclusive cap.
        record['duration_seconds'] = time.monotonic()-started
        if record['duration_seconds']>=CAP:
            record.update(budget_overrun=True, outcome='budget_incomplete', qualification='ineligible', utility_pass=False)
        write(out/'run.json', record)
        write(out/'results.json', dict(rows=rows, qualification=record['qualification']))


if __name__ == '__main__':
    main()
