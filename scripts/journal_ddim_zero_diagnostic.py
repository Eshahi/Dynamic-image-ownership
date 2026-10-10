"""Fixed unit-scale diagnosis after the first D1 zero-gradient smoke."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from journal_vae_probe import Evaluator, write
from journal_readability_probe import Objective, load, payload, patterns
from journal_read_conditioning_probe import SCREEN
from journal_ddim_channel import DifferentiableDDIM, continuous_projection
from f4_transfer_probe import ASSETS

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--convergence', action='store_true')
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    record = dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, config=dict(source=1675, strength=.1, multipliers=[1/1024, 1, 1024],
            scalar='mean(w * p)', cap_seconds=120, counts_against='D1 aggregate 900-second smoke',
            reason='diagnose zero at the downscaled inactive-hinge scalar; no candidate updates'),
        seeds=[0], data_split='development', usd=0, outcome='running', rows=[])
    write(a.output_dir / 'run.json', record)
    try:
        import torch
        import three_threat_models as models
        ev = Evaluator()
        _, q, _, _ = payload(ev, 1675)
        rgb = load(SCREEN / 'images/R3-1675-C1-clean.png')
        channel = DifferentiableDDIM(models.load_regenerator(ASSETS))
        obj = Objective(ev, None, *patterns(ev.profile, q))
        ev.reader.vae.enable_gradient_checkpointing()
        obj.checkpointed = True
        base = ev.reader.tensor(rgb.astype(np.float32)/255)
        if a.convergence:
            record['config'].update(strengths=[.1, .2], epsilons=[1e-4, 3e-5, 1e-5, 3e-6],
                reason='fixed small-step convergence after failed large-step derivative criterion',
                precision='promoted fp32 with TF32 explicitly disabled; no RGB8')
            record['backend_before'] = dict(matmul_tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_tf32=torch.backends.cudnn.allow_tf32)
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            channel.set_precision(torch.float32, diagnostic=True)
            for strength in (.1, .2):
                tick = time.monotonic()
                torch.cuda.reset_peak_memory_stats()
                x = base.detach().clone().requires_grad_(True)
                v = channel.forward(x, strength, 0, quantize_input=False, quantize_output=False)
                scalar = (obj.w*continuous_projection(obj, v.continuous)).mean()
                g, = torch.autograd.grad(scalar, x)
                if not bool(torch.isfinite(g).all()) or float(g.norm()) == 0:
                    raise ValueError('Invalid continuous gradient')
                direction = -g.detach()/g.square().mean().sqrt()
                ad = float((g*direction).sum())
                row = dict(strength=strength, scalar=float(scalar.detach()), autograd=ad,
                    gradient_norm=float(g.norm()), direction_max_abs=float(direction.abs().max()), fd=[])
                del x, v, g, scalar
                with torch.no_grad():
                    for eps in (1e-4, 3e-5, 1e-5, 3e-6):
                        if time.monotonic()-started > 120:
                            raise TimeoutError('diagnostic cap')
                        values=[]
                        for sign in (-1, 1):
                            v = channel.forward(base+sign*eps*direction, strength, 0,
                                quantize_input=False, quantize_output=False)
                            scalar = (obj.w*continuous_projection(obj, v.continuous)).mean()
                            values.append(float(scalar))
                            del v, scalar
                        fd = (values[1]-values[0])/(2*eps)
                        row['fd'].append(dict(eps=eps, minus=values[0], plus=values[1], fd=fd,
                            relative_discrepancy=abs(ad-fd)/max(abs(ad),abs(fd),1e-8)))
                row.update(duration_seconds=time.monotonic()-tick,
                    peak_allocated_bytes=torch.cuda.max_memory_allocated())
                record['rows'].append(row)
                write(a.output_dir / 'run.json', record)
                print(json.dumps(row), flush=True)
            record['outcome'] = 'completed_convergence_diagnostic_only'
            return
        for scale in (1/1024, 1., 1024.):
            if time.monotonic()-started > 120:
                raise TimeoutError('diagnostic cap')
            torch.cuda.reset_peak_memory_stats()
            tick = time.monotonic()
            x = base.detach().clone().requires_grad_(True)
            value = channel.forward(x, .1, 0)
            projection = obj.projection(value.image, 'clean')
            scalar = (obj.w*projection).mean()
            output_grad, = torch.autograd.grad(scalar*scale, value.image, retain_graph=True)
            g, = torch.autograd.grad(scalar*scale, x)
            finite = bool(torch.isfinite(g).all())
            row = dict(multiplier=scale, scalar=float(scalar.detach()), input_finite=finite,
                input_nonzero=int(torch.count_nonzero(g)),
                input_norm_rescaled=float((g/scale).norm()) if finite else None,
                output_norm_rescaled=float((output_grad/scale).norm()),
                peak_allocated_bytes=torch.cuda.max_memory_allocated(), duration_seconds=time.monotonic()-tick)
            record['rows'].append(row)
            write(a.output_dir / 'run.json', record)
            print(json.dumps(row), flush=True)
            del x, value, projection, scalar, g, output_grad
        record['outcome'] = 'completed_diagnostic_only'
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc())
        raise
    finally:
        record['duration_seconds'] = time.monotonic()-started
        write(a.output_dir / 'run.json', record)

if __name__ == '__main__':
    main()
