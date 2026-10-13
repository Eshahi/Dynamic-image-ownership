"""Fixed FM-R48-Eq10-SD2community feasibility; never native FreqMark.

No model import, download or execution on import/--help. Run only after all other
GPU work exits. Resume is permitted only at an unstarted source boundary, inside
the original absolute deadline (idle time is conservatively charged).
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
PROTOCOL = ROOT / 'research/journal-upgrade-20261009/freqmark-reconstruction-protocol.md'
AMENDMENT = ROOT / 'research/journal-upgrade-20261009/freqmark-memory-amendment.md'
SERIAL_HELPER = ROOT / 'scripts/freqmark_serial_gradient.py'
CAP = 1800
GPU_CAP, RSS_CAP, FREE_RAM = 9*1024**3, 10*1024**3, 3*1024**3
ASSETS = (
    ('facebook/dinov2-small', 'ed25f3a31f01632728cabb09d1542f84ab7b0056', 'dino',
     'Apache-2.0', (('model.safetensors', 88249960,
     'ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1'),
     ('config.json', 547, None), ('preprocessor_config.json', 436, None), ('README.md', None, None))),
    ('sd2-community/stable-diffusion-2-1-base', '4e63672c03103b6c636b8fb4119ba982469b2955',
     'sd2', 'CreativeML Open RAIL++-M', (('vae/diffusion_pytorch_model.safetensors', 334643276,
     'a1d993488569e928462932c8c38a0760b874d166399b14414135bd9c42df5815'),
     ('vae/config.json', 553, None), ('README.md', None, None))))
CONFIG = dict(name='FM-R48-Eq10-SD2community', sources=[30, 72], bits=48, steps=400,
    lr=2., betas=[.9, .999], eps=1e-8, margin=1., latent_noise=.25, pixel_noise=.06,
    psnr_weight=.05, lpips_weight=.25, dtype='float32', fft_norm='backward',
    posterior='mode, raw latent, no scaling', feature='final LayerNorm CLS[:48]',
    preprocessing='bicubic antialias 256, center crop 224, ImageNet normalization',
    routing='Eq10 three hinges; no appendix rotation/crop routing',
    output='update400, floor(255*x+.5), reload PNG', cpu_threads=4,
    interpretation='Independent v1-equation reconstruction; community VAE equivalence unknown; no FPR/security/comparative claim')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    temp.replace(path)


class Stop(RuntimeError):
    def __init__(self, outcome, message):
        self.outcome = outcome
        super().__init__(message)


def inside(path, root):
    path = Path(path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path outside explicit MAIN .thesis-build: {path}')
    return path


def other_gpu_processes(desktop_pids=()):
    output = subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid',
                                     '--format=csv,noheader,nounits'], text=True)
    return [line.strip() for line in output.splitlines()
            if line.strip() and line.strip() != str(os.getpid())
            and int(line.strip()) not in desktop_pids]


def processor_check(c):
    expected = dict(do_resize=True, do_center_crop=True, do_rescale=True, do_normalize=True,
        size={'shortest_edge': 256}, crop_size={'height': 224, 'width': 224},
        resample=3, rescale_factor=1/255, image_mean=[.485, .456, .406], image_std=[.229, .224, .225])
    for key, value in expected.items():
        if c.get(key) != value:
            raise Stop('prerequisite_failed', f'Pinned processor disagreement: {key}')


def acquire(asset_dir, downloads, check, remaining, record, cached_only=False):
    # Operator supplies the project-wide remaining allowance with a dated ledger
    # attestation; counting only this directory would miss earlier downloads.
    required = sum(s or 1024*1024 for _, _, _, _, files in ASSETS for _, s, _ in files)
    if not cached_only and (remaining < required or shutil.disk_usage(asset_dir).free < 2*required):
        raise Stop('prerequisite_failed', 'Insufficient documented download allowance/disk')
    for repo, revision, folder, license_label, files in ASSETS:
        for filename, size, expected in files:
            check()
            path = asset_dir / folder / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            url = f'https://huggingface.co/{repo}/resolve/{revision}/{filename}'
            if not path.exists():
                if cached_only:
                    raise Stop('prerequisite_failed', f'Serial attempt requires cached asset: {path}')
                partial = path.with_suffix(path.suffix + '.partial')
                if partial.exists():
                    raise Stop('prerequisite_failed', f'Retained interrupted acquisition: {partial}')
                request = urllib.request.Request(url, headers={'User-Agent': 'Thesis-FreqMark-reconstruction/1'})
                with urllib.request.urlopen(request, timeout=15) as response, partial.open('xb') as target:
                    transferred = 0
                    while chunk := response.read(1024*1024):
                        check(); transferred += len(chunk)
                        if transferred > (size or 1024*1024):
                            raise Stop('prerequisite_failed', 'Unexpected asset size')
                        target.write(chunk)
                actual = sha(partial)
                if (size is not None and partial.stat().st_size != size) or (expected and actual != expected):
                    raise Stop('prerequisite_failed', 'Pinned asset size/SHA mismatch; partial retained')
                partial.rename(path)
            actual = sha(path)
            if (size is not None and path.stat().st_size != size) or (expected and actual != expected):
                raise Stop('prerequisite_failed', 'Cached asset size/SHA mismatch')
            receipt = dict(path=str(path), url=url, revision=revision, license=license_label,
                           bytes=path.stat().st_size, sha256=actual)
            record['assets'].append(receipt)
            marker = f'FreqMark {revision} {filename} SHA-256 `{actual}`'
            if marker not in downloads.read_text(encoding='utf-8-sig'):
                if cached_only:
                    raise Stop('prerequisite_failed', f'Cached asset differs from acquisition ledger: {filename}')
                with downloads.open('a', encoding='utf-8') as f:
                    f.write(f'\n- {marker}; {url}; {receipt["bytes"]} bytes; {license_label}; local `{path}`. Actual bytes verified; pinned card retained.\n')
    processor_check(read(asset_dir/'dino/preprocessor_config.json'))
    for folder, license_id in (('dino', 'apache-2.0'), ('sd2', 'openrail++')):
        card = (asset_dir/folder/'README.md').read_text(encoding='utf-8')
        if not re.search(r'^license:\s*[\"\']?' + re.escape(license_id) + r'[\"\']?\s*$', card, re.MULTILINE):
            raise Stop('prerequisite_failed', 'Pinned model-card license metadata disagrees')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main', type=Path, required=True)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--assets-dir', type=Path, required=True)
    p.add_argument('--lpips-assets', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--downloads-ledger', type=Path, required=True)
    p.add_argument('--dev-log', type=Path, required=True)
    p.add_argument('--remaining-download-bytes', type=int, required=True)
    p.add_argument('--allowance-attestation', required=True, help='Dated project-wide ledger check and arithmetic')
    p.add_argument('--desktop-pids', type=int, nargs='*', default=[], help='Observed Windows desktop-only PID snapshot, recorded in command')
    p.add_argument('--resource-start-epoch', type=float, help='Preserve earlier failed infrastructure preflight start; never extend budget')
    p.add_argument('--execution-schedule', choices=('joint', 'serial-validated'), default='joint')
    args = p.parse_args()
    started = time.time()
    serial = args.execution_schedule == 'serial-validated'
    if serial:
        os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        if args.resource_start_epoch is not None:
            p.error('Serial amendment requires one fresh inclusive execution; no earlier start/resume')
    if args.resource_start_epoch is not None:
        if not 0 <= started-args.resource_start_epoch < CAP:
            p.error('Earlier inclusive start must be within the original resource cap')
        started = args.resource_start_epoch
    build = args.main.resolve()/'.thesis-build'
    out, assets = inside(args.output_dir, build), inside(args.assets_dir, build)
    lpassets = inside(args.lpips_assets, build)
    if not 0 <= args.remaining_download_bytes <= 30_000_000_000:
        p.error('Documented remaining project allowance must be within 30 GB')
    # No scientific work before run identity and its original deadline exist.
    out.mkdir(parents=True, exist_ok=True); assets.mkdir(parents=True, exist_ok=True)
    path = out/'run.json'
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    identity = dict(commit=commit, script_sha256=sha(__file__), protocol_sha256=sha(PROTOCOL),
                    sources_receipt_sha256=sha(args.sources), config=CONFIG,
                    assets_dir=str(assets), lpips_assets=str(lpassets))
    if serial:
        identity.update(execution_schedule=args.execution_schedule,
            amendment_sha256=sha(AMENDMENT), helper_sha256=sha(SERIAL_HELPER))
        identity['config'] = dict(CONFIG, name=CONFIG['name']+'-serial',
                                 execution_schedule=args.execution_schedule)
    if path.exists():
        if serial:
            raise ValueError('Serial amendment is a new single attempt; no resume or relaunch')
        record = read(path)
        if record['identity'] != identity:
            raise ValueError('Resume identity changed')
        if record['outcome'] not in ('boundary_paused', 'running') or any(s['status'] == 'running' for s in record['sources']):
            raise ValueError('No retry of started source or terminal run; retained results immutable')
        started = record['started_epoch']
    else:
        if any(out.iterdir()):
            raise ValueError('New run requires empty output directory')
        cohort = read(args.sources)
        if cohort['data_split'] != 'development-reserved':
            raise ValueError('Reserved development receipt required')
        if serial and (cohort.get('raw_overlap_count') != 0 or
                       any(s.get('raw_overlap') is not False for s in cohort['sources'])):
            raise ValueError('Serial mode requires retained zero-overlap development selection receipt')
        byid = {s['source_id']: s for s in cohort['sources']}
        sources = [dict(input=byid[s], status='not_started') for s in (30, 72)]
        record = dict(schema='freqmark-reconstruction-v1', identity=identity,
            command=sys.argv, started_epoch=started, started_at_utc=datetime.now(timezone.utc).isoformat(),
            deadline_epoch=started+CAP, duration_seconds=0., outcome='running',
            sources=sources, assets=[], data_split='development', usd=0,
            download_allowance=dict(bytes=args.remaining_download_bytes, attestation=args.allowance_attestation))
    torch = None
    done = threading.Event()

    def save():
        record['duration_seconds'] = time.time()-started
        write(path, record)

    def check():
        if time.time() >= record['deadline_epoch']:
            raise Stop('budget_inconclusive', 'Original inclusive 1800-second cap reached')
        from fresh_e3_simplification import memory
        rss, peak, available = memory()
        allocated = int(torch.cuda.max_memory_allocated()) if torch is not None and torch.cuda.is_initialized() else 0
        record['peak_rss_bytes'] = max(record.get('peak_rss_bytes', 0), peak, rss)
        record['peak_gpu_allocated_bytes'] = max(record.get('peak_gpu_allocated_bytes', 0), allocated)
        if rss > RSS_CAP or available < FREE_RAM or allocated > GPU_CAP:
            raise Stop('resource_limit', 'RAM/GPU/headroom cap reached')

    def watchdog():
        # Covers blocking acquisition, CUDA kernels and serialization as well as
        # normal cooperative checks. Emergency receipt never overwrites run.json.
        while not done.wait(.25):
            try:
                check()
            except BaseException as e:
                emergency = dict(outcome=getattr(e, 'outcome', 'resource_monitor_failed'),
                    error=str(e), duration_seconds=time.time()-started)
                with (out/'emergency-stop.json').open('x', encoding='utf-8') as f:
                    json.dump(emergency, f)
                os._exit(3)

    save()
    threading.Thread(target=watchdog, daemon=True).start()
    try:
        check()
        tracked_paths = (Path(__file__), PROTOCOL, AMENDMENT, SERIAL_HELPER) if serial else (Path(__file__), PROTOCOL)
        for tracked in tracked_paths:
            relative = tracked.relative_to(ROOT).as_posix()
            committed = subprocess.check_output(['git', 'show', f'HEAD:{relative}'], cwd=ROOT)
            # Git's Windows CRLF checkout conversion does not change executable source semantics.
            if committed.replace(b'\r\n', b'\n') != tracked.read_bytes().replace(b'\r\n', b'\n'):
                raise Stop('prerequisite_failed', 'Implementation/protocol must be committed before execution')
        processes = other_gpu_processes(args.desktop_pids)
        if processes:
            raise Stop('prerequisite_failed', 'Other GPU compute process present before acquisition; defer')
        for s in record['sources']:
            r = s['input']; source_path = inside(r['canonical_path'], build)
            if not r.get('development_reserved') or sha(source_path) != r['sha256']:
                raise Stop('prerequisite_failed', 'Canonical reserved input/hash mismatch')
        if (out/'emergency-stop.json').exists():
            raise Stop('budget_inconclusive', 'Retained prior emergency stop prohibits continuation')
        acquisition = time.monotonic()
        acquire(assets, args.downloads_ledger, check, args.remaining_download_bytes, record, cached_only=serial)
        record['acquisition_seconds'] = time.monotonic()-acquisition; save()
        import numpy as np
        import torch as torch_module
        torch = torch_module
        import torch.nn.functional as F
        from PIL import Image
        from diffusers import AutoencoderKL
        from transformers import Dinov2Model
        import lpips
        from three_threat_models import load_lpips
        from m1_latent_reconstruction import quality
        torch.set_num_threads(4)
        if serial:
            torch.use_deterministic_algorithms(True, warn_only=False)
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            torch.set_float32_matmul_precision('highest')
            record['execution_flags'] = dict(dtype='float32',
                deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
                deterministic_warn_only=torch.is_deterministic_algorithms_warn_only_enabled(),
                matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
                cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
                cudnn_benchmark=torch.backends.cudnn.benchmark,
                cudnn_deterministic=torch.backends.cudnn.deterministic,
                float32_matmul_precision=torch.get_float32_matmul_precision(),
                cublas_workspace_config=os.environ['CUBLAS_WORKSPACE_CONFIG'],
                hf_hub_offline=os.environ['HF_HUB_OFFLINE'],
                transformers_offline=os.environ['TRANSFORMERS_OFFLINE'])
            fixture = np.random.Generator(np.random.PCG64(2026101301)).uniform(.1, .9, (128,128,3)).astype(np.float32)
            np.save(out/'numerical-fixture.npy', fixture)
            record['numerical_fixture'] = dict(path=str(out/'numerical-fixture.npy'),
                sha256=sha(out/'numerical-fixture.npy'), seed=2026101301,
                noise_seed=2026101302, rgb_shape=[128,128,3], dtype='float32', distribution='uniform [.1,.9]')
            record['numerical_fixture']['target_signs'] = [1 if k % 2 == 0 else -1 for k in range(48)]
            save()  # Frozen RGB artifact and flags exist before model setup/calls.
        if not torch.cuda.is_available():
            raise Stop('prerequisite_failed', 'CUDA GPU required; no CPU scientific fallback')
        processes = other_gpu_processes(args.desktop_pids)
        if processes:
            raise Stop('prerequisite_failed', 'Other GPU compute process present; defer')
        free, total = torch.cuda.mem_get_info()
        if free < GPU_CAP:
            raise Stop('prerequisite_failed', 'Less than 9 GiB free GPU')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        loading = time.monotonic(); check()
        vae = AutoencoderKL.from_pretrained(assets/'sd2', subfolder='vae', local_files_only=True,
            use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        check()
        dino = Dinov2Model.from_pretrained(assets/'dino', local_files_only=True,
            use_safetensors=True, torch_dtype=torch.float32).eval().requires_grad_(False).to('cuda')
        check()
        metric = load_lpips(lpassets, Path(lpips.__file__).parent).to('cuda')
        record['loading_seconds'] = time.monotonic()-loading
        record['environment'] = {p: importlib.metadata.version(p) for p in ('numpy', 'torch', 'diffusers', 'transformers', 'Pillow', 'lpips')}
        record['environment'].update(python=sys.version, gpu=torch.cuda.get_device_name(), threads=torch.get_num_threads())
        record['lpips_hashes'] = dict(alexnet=sha(lpassets/'alexnet/alexnet-owt-7be5be79.pth'),
            learned=sha(Path(lpips.__file__).parent/'weights/v0.1/alex.pth'))
        mean = torch.tensor([.485,.456,.406], device='cuda')[None,:,None,None]
        std = torch.tensor([.229,.224,.225], device='cuda')[None,:,None,None]

        def features(x):
            x = F.interpolate(x, size=(256,256), mode='bicubic', align_corners=False, antialias=True)
            result = dino(pixel_values=(x[:,:,16:240,16:240]-mean)/std).last_hidden_state[:,0,:128]
            finite(result)
            return result[:,:48]

        def finite(*values):
            if not all(bool(torch.isfinite(v).all()) for v in values):
                raise Stop('numeric_failed', 'Nonfinite tensor/loss/gradient/parameter')

        def signs(x):
            f = features(x)
            return (f >= 0).to(torch.int64).flatten().cpu().tolist()

        def decode(z):
            x = (vae.decode(z).sample+1)/2
            finite(x)
            return x.clamp(0,1)

        def assess(x, reference, rgb, target):
            with torch.no_grad():
                extraction = time.monotonic()
                bits = signs(x)
                extraction_seconds = time.monotonic()-extraction
                scoring = time.monotonic()
                q = quality(reference, rgb)
                lp = metric(x*2-1, tensor(reference)*2-1).item()
                if not np.isfinite(lp):
                    raise Stop('numeric_failed', 'Nonfinite assessment LPIPS')
            q['lpips'] = lp
            q['strict_quality'] = (q['psnr_infinite'] or q['psnr_db'] > 35) and q['ssim_rgb'] > .9 and lp < .1
            return dict(bits=bits, hamming_matches=sum(a==b for a,b in zip(bits,target)), exact=bits==target, quality=q,
                        extraction_seconds=extraction_seconds, quality_assessment_seconds=time.monotonic()-scoring)

        def tensor(rgb):
            return torch.from_numpy(rgb.copy()).permute(2,0,1).unsqueeze(0).to('cuda', dtype=torch.float32)/255

        def rgb8(x):
            return torch.floor(x.detach().clamp(0,1)*255+.5).byte().squeeze(0).permute(1,2,0).cpu().numpy()

        if serial:
            from freqmark_serial_gradient import backward_step, numerical_gate
            def encode_fixture(x):
                z = vae.encode(x*2-1).latent_dist.mode().detach()
                finite(z)
                return z
            try:
                record['numerical_validation'] = numerical_gate(torch, np, fixture, decode,
                    features, metric, finite, encode_fixture, out, write, check, Stop)
            except BaseException as e:
                validation_path = out/'numerical-validation.json'
                partial = read(validation_path) if validation_path.exists() else dict(comparisons=[], passed=False)
                partial.update(passed=False, error=str(e), error_type=type(e).__name__)
                write(validation_path, partial)
                record['numerical_validation'] = partial
                save()
                if isinstance(e, torch.cuda.OutOfMemoryError) or (isinstance(e, Stop) and e.outcome in ('resource_limit', 'budget_inconclusive')):
                    raise
                raise Stop('numeric_gate_failed', f'Numerical validation incomplete or failed: {e}') from e
            save()
            torch.cuda.empty_cache()

        for index, s in enumerate(record['sources']):
            if s['status'] == 'completed':
                continue
            check(); sid = s['input']['source_id']; begin = time.monotonic()
            s.update(status='running', started_at_utc=datetime.now(timezone.utc).isoformat(), diagnostics=[])
            target = np.random.Generator(np.random.PCG64(np.random.SeedSequence([20261013,sid,48]))).integers(0,2,size=48).tolist()
            s.update(message_bits=target, noise_seed=2026101300+sid,
                     draw_order='Every step: latent Gaussian then independent pixel Gaussian; 400 fresh pairs')
            save()  # Target fixed and retained before any FreqMark forward pass.
            with Image.open(s['input']['canonical_path']) as image:
                if image.mode != 'RGB' or image.size != (512,512):
                    raise Stop('prerequisite_failed', 'RGB8 512-square canonical source required')
                reference = np.asarray(image, np.uint8).copy()
            source = tensor(reference)
            message = torch.tensor(target, device='cuda', dtype=torch.float32)[None]*2-1
            rng = torch.Generator(device='cuda').manual_seed(s['noise_seed'])
            with torch.no_grad():
                bits = signs(source)
                s['unmarked'] = dict(bits=bits, target_matches=sum(a==b for a,b in zip(bits,target)),
                    complement_matches=sum(a!=b for a,b in zip(bits,target)), interpretation='Descriptive only; no FPR')
                z = vae.encode(source*2-1).latent_dist.mode().detach(); finite(z)
                frequency = torch.fft.fft2(z, dim=(-2,-1), norm='backward')
                clean = decode(z)
                s['zero_perturbation'] = assess(clean, reference, rgb8(clean), target)
                s['diagnostics'].append(dict(step=0, bits=signs(clean)))
            a = torch.zeros_like(z, requires_grad=True); b = torch.zeros_like(z, requires_grad=True)
            optimizer = torch.optim.Adam([a,b], lr=2., betas=(.9,.999), eps=1e-8, weight_decay=0)
            embedding = time.monotonic(); step_times = []
            for step in range(1,401):
                check(); tick = time.monotonic(); optimizer.zero_grad(set_to_none=True)
                if serial:
                    latent_noise = torch.randn(z.shape, generator=rng, device='cuda', dtype=torch.float32)*.25
                    pixel_noise = torch.randn(source.shape, generator=rng, device='cuda', dtype=torch.float32)*.06
                    scalars = backward_step(a, b, frequency, source, message,
                        (latent_noise, pixel_noise), decode, features, metric, finite, args.execution_schedule)
                else:
                    latent = torch.fft.ifft2(frequency+torch.complex(a,b), dim=(-2,-1), norm='backward').real
                    clean = decode(latent)
                    latent_noise = torch.randn(latent.shape, generator=rng, device='cuda', dtype=torch.float32)*.25
                    noisy = decode(latent+latent_noise)
                    pixel_noise = torch.randn(clean.shape, generator=rng, device='cuda', dtype=torch.float32)*.06
                    pixel = (clean+pixel_noise).clamp(0,1)
                    hinges = [torch.relu(1-message*features(x)).mean() for x in (clean,noisy,pixel)]
                    psnr = -10*torch.log10((clean-source).square().mean().clamp_min(1e-12))
                    perceptual = metric(clean*2-1, source*2-1).mean()
                    loss = sum(hinges)-.05*psnr+.25*perceptual
                    finite(*hinges, psnr, perceptual, loss)
                    loss.backward(); finite(a.grad,b.grad)
                    scalars = dict(loss=loss.item(), clean_hinge=hinges[0].item(),
                        latent_hinge=hinges[1].item(), pixel_hinge=hinges[2].item(), psnr=psnr.item(), lpips=perceptual.item())
                gradient_tensor = torch.sqrt(a.grad.square().sum()+b.grad.square().sum())
                finite(gradient_tensor)
                gradient = float(gradient_tensor.item())
                if gradient == 0:
                    raise Stop('numeric_failed', 'Zero total optimization gradient')
                before_a, before_b = a.detach().clone(), b.detach().clone()
                optimizer.step(); finite(a,b)
                changed = not (torch.equal(a,before_a) and torch.equal(b,before_b))
                if step == 1 and not changed:
                    raise Stop('numeric_failed', 'First Adam update did not change parameters')
                torch.cuda.synchronize(); latency = time.monotonic()-tick; step_times.append(latency)
                s['updates_completed'] = step
                check()
                if step in (1,10,100,400):
                    with torch.no_grad():
                        observed = decode(torch.fft.ifft2(frequency+torch.complex(a,b), dim=(-2,-1), norm='backward').real)
                        diagnostic = dict(step=step, bits=signs(observed), loss=scalars['loss'],
                            hinges=[scalars[k] for k in ('clean_hinge','latent_hinge','pixel_hinge')], psnr=scalars['psnr'], lpips=scalars['lpips'],
                            gradient_norm=gradient, parameter_changed=changed, latency_seconds=latency,
                            peak_gpu_bytes=int(torch.cuda.max_memory_allocated()))
                    s['diagnostics'].append(diagnostic); save()
                if step == 10:
                    remaining_steps = 400-step+400*(1-index)
                    estimate = sum(step_times)/len(step_times)*remaining_steps+120
                    s['ten_step_remaining_estimate_seconds'] = estimate
                    if time.time()+estimate >= record['deadline_epoch']:
                        raise Stop('budget_inconclusive', 'Ten-step estimate fails fixed remaining work plus 120-second scoring reserve')
            s['embedding_seconds'] = time.monotonic()-embedding
            with torch.no_grad():
                final = decode(torch.fft.ifft2(frequency+torch.complex(a,b), dim=(-2,-1), norm='backward').real)
                extraction = time.monotonic(); s['final_tensor_bits'] = signs(final)
                s['tensor_extraction_seconds'] = time.monotonic()-extraction
                png = out/f'{sid}-update400.png'
                if png.exists():
                    raise Stop('prerequisite_failed', 'Refusing overwrite of retained result')
                Image.fromarray(rgb8(final)).save(png)
                with Image.open(png) as delivered:
                    rgb = np.asarray(delivered, np.uint8).copy()
                assessment = time.monotonic(); s['final_png'] = assess(tensor(rgb), reference, rgb, target)
                s['assessment_seconds'] = time.monotonic()-assessment
                s['quantization_sign_flips'] = sum(a!=b for a,b in zip(s['final_tensor_bits'],s['final_png']['bits']))
                s['output'] = dict(path=str(png), sha256=sha(png))
            s.update(status='completed', total_source_seconds=time.monotonic()-begin)
            check(); record['outcome'] = 'boundary_paused'; save()
            del a,b,optimizer,clean,final,observed,latent_noise,pixel_noise
            if not serial:
                del noisy,pixel,latent,loss,hinges,psnr,perceptual
            torch.cuda.empty_cache()
        complete = all(s['status']=='completed' for s in record['sources'])
        useful = complete and all(s['final_png']['exact'] for s in record['sources'])
        strict = useful and all(s['final_png']['quality']['strict_quality'] for s in record['sources'])
        record.update(outcome='completed', useful_feasibility_success=useful, strict_budget_readiness=strict)
        check()
    except BaseException as e:
        record.update(outcome=getattr(e, 'outcome', 'prerequisite_failed'), error=str(e), traceback=traceback.format_exc())
        if torch is not None and isinstance(e, torch.cuda.OutOfMemoryError):
            record['outcome'] = 'allocation_failed'
        for s in record['sources']:
            if s['status'] == 'running':
                s.update(status='incomplete', error=str(e))
    finally:
        save(); done.set()
        with args.dev_log.open('a', encoding='utf-8') as log:
            log.write(f'\n- {datetime.now(timezone.utc).isoformat()} Codex agent: {identity["config"]["name"]}; commit {commit}; run `{path}`; inclusive {record["duration_seconds"]:.3f} s; outcome {record["outcome"]}; development, USD 0, no attacks or native-equivalence claim.\n')
    print(json.dumps(dict(outcome=record['outcome'], run_json=str(path))))
    return 0 if record['outcome']=='completed' else 3


if __name__ == '__main__':
    raise SystemExit(main())
