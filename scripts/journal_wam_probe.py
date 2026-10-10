"""Exploratory official WAM SA-1B MIT clean/VAE probe; no F5 binding endpoint."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
REVISION = '2c08af04d037d5667c02f6ddebbda9ff04581c3e'
ASSET = MAIN / '.thesis-build/assets/journal-wam-2c08af04'
ARMS = {'native_w2': 2.0, 'quality_w0p5': 0.5}
CONDITIONS = ('clean', 'sd15_vae', 'sdxl_vae')


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def message(source_id):
    """Fixed public payload schedule, independent of pixels and measured outcomes."""
    digest = hashlib.sha256(f'journal-wam-dev-v1:{source_id}'.encode()).digest()[:4]
    return [(byte >> shift) & 1 for byte in digest for shift in range(7, -1, -1)]


class Adapter:
    def __init__(self, repo, checkpoint, device):
        import torch
        from omegaconf import OmegaConf
        from watermark_anything.models import Wam, build_embedder, build_extractor
        from watermark_anything.modules.jnd import JND
        from watermark_anything.data.transforms import default_transform, normalize_img, unnormalize_img
        from watermark_anything.data.metrics import msg_predict_inference
        self.torch, self.device = torch, device
        self.transform, self.unnormalize = default_transform, unnormalize_img
        self.decode_message = msg_predict_inference
        params = json.loads((repo / 'checkpoints/params.json').read_text())
        ec = OmegaConf.load(repo / params['embedder_config'])
        xc = OmegaConf.load(repo / params['extractor_config'])
        ac = OmegaConf.load(repo / params['attenuation_config'])
        if (params['nbits'], params['scaling_w'], params['scaling_i']) != (32, 2.0, 1.0):
            raise ValueError('Unexpected pinned native configuration')
        embedder = build_embedder(params['embedder_model'], ec[params['embedder_model']], params['nbits'])
        extractor = build_extractor(xc.model, xc[params['extractor_model']], params['img_size'], params['nbits'])
        attenuation = JND(**ac[params['attenuation']], preprocess=unnormalize_img, postprocess=normalize_img)
        # Training-only augmentation is unused by official embed/detect. No random training masks.
        model = Wam(embedder, extractor, torch.nn.Identity(), attenuation,
                    params['scaling_w'], params['scaling_i'], img_size_extractor=params['img_size_extractor'])
        state = torch.load(checkpoint, map_location='cpu', weights_only=True)
        if not isinstance(state, dict) or not all(isinstance(k, str) and isinstance(v, torch.Tensor) for k, v in state.items()):
            raise ValueError('Expected a flat tensor state_dict; unsafe pickle fallback forbidden')
        model.load_state_dict(state, strict=True)
        self.model = model.eval().requires_grad_(False).to(device)
        self.params = params

    def tensor(self, rgb):
        from PIL import Image
        return self.transform(Image.fromarray(rgb)).unsqueeze(0).to(self.device)

    def embed(self, rgb, bits, scaling):
        import numpy as np
        self.model.scaling_w = scaling
        t = self.torch.tensor([bits], dtype=self.torch.float32, device=self.device)
        with self.torch.inference_mode():
            y = self.model.embed(self.tensor(rgb), t)['imgs_w']
            y = self.unnormalize(y)[0].permute(1, 2, 0).cpu().numpy()
        return np.rint(np.clip(y, 0, 1) * 255).astype(np.uint8)

    def detect(self, rgb, bits):
        with self.torch.inference_mode():
            p = self.model.detect(self.tensor(rgb))['preds']
            if p.shape[1] != 33 or not bool(self.torch.isfinite(p).all()):
                raise ValueError('Invalid native 32-bit detector output')
            mask = p[:, :1].sigmoid()
            positive = int((mask > .5).sum().item())
            decoded = self.decode_message(p[:, 1:], mask).cpu()[0].tolist() if positive else None
        target = [bool(b) for b in bits]
        return {'native_mask_positive_pixels': positive, 'native_mask_pixels': mask.numel(),
                'native_mask_fraction': positive / mask.numel(), 'native_mask_mean': float(mask.mean().item()),
                'native_mask_nonempty_diagnostic': bool(positive), 'decoded_message': decoded,
                'bit_accuracy': sum(a == b for a, b in zip(decoded, target)) / 32 if decoded is not None else None,
                'wrong_message_bit_accuracy': sum(a != b for a, b in zip(decoded, target)) / 32 if decoded is not None else None,
                'exact_message_match': decoded == target if decoded is not None else False,
                'wrong_message_exact_match': decoded == [not b for b in target] if decoded is not None else False}


def summarize(rows):
    result = {}
    for arm in ARMS:
        for condition in CONDITIONS:
            group = [r for r in rows if r['arm'] == arm and r['condition'] == condition]
            good = [r for r in group if r['status'] == 'ok']
            c1 = [r for r in good if r['control'] == 'C1']
            c0 = [r for r in good if r['control'] == 'C0']
            result[f'{arm}/{condition}'] = {'planned_c1': sum(r['control'] == 'C1' for r in group),
                'completed_c1': len(c1), 'failed_rows': len(group) - len(good),
                'exact_message_c1': sum(r['detection']['exact_message_match'] for r in c1),
                'bit_accuracy_c1_mean': sum(r['detection']['bit_accuracy'] or 0 for r in c1) / len(c1) if c1 else None,
                'empty_mask_c1': sum(not r['detection']['native_mask_nonempty_diagnostic'] for r in c1),
                'strict_quality_c1': sum(r['strict_quality_source'] for r in c1),
                'c0_exact_message_diagnostic': sum(r['detection']['exact_message_match'] for r in c0),
                'wrong_message_exact_diagnostic': sum(r['detection']['wrong_message_exact_match'] for r in c1)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--repo-dir', type=Path, default=ASSET / 'source')
    parser.add_argument('--checkpoint', type=Path, default=ASSET / 'wam_mit.pth')
    parser.add_argument('--deps-dir', type=Path, default=MAIN / '.thesis-build/journal-wam-deps')
    parser.add_argument('--scope', choices=('smoke', 'full'), default='smoke')
    parser.add_argument('--conditions', choices=('clean', 'all'), default='all')
    parser.add_argument('--device', choices=('cuda', 'cpu'), default='cuda')
    args = parser.parse_args()
    sys.path[:0] = [str(args.deps_dir), str(args.repo_dir), str(ROOT), str(ROOT / 'scripts')]
    import numpy as np
    from PIL import Image
    from f4_transfer_probe import SOURCES, ASSETS
    from m1_latent_reconstruction import quality
    import torch
    import three_threat_models as models
    started = time.monotonic()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / 'images').mkdir()
    ids = sorted(SOURCES)[:1] if args.scope == 'smoke' else sorted(SOURCES)
    conditions = ('clean',) if args.conditions == 'clean' else CONDITIONS
    record = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': sys.argv, 'data_split': 'development', 'sources': ids, 'seeds': [],
        'config': {'official_revision': REVISION, 'checkpoint': str(args.checkpoint), 'checkpoint_sha256': sha(args.checkpoint),
                   'arms': ARMS, 'conditions': conditions, 'precision': 'float32', 'size': [512, 512],
                   'payload_bits': 32, 'message_schedule': 'sha256(journal-wam-dev-v1:source_id) first 32 bits MSB first',
                   'wrong_message': 'bitwise complement', 'mask_threshold': .5, 'native_decoder': 'semihard/default',
                   'training_augmenter': 'Identity, unused during inference', 'human_admissibility': 'missing'},
        'outcome': 'running', 'duration_seconds': None}
    write(args.output_dir / 'run.json', record)
    rows = []
    try:
        torch.set_num_threads(4)
        if args.device == 'cuda': torch.cuda.reset_peak_memory_stats()
        init = time.monotonic()
        adapter = Adapter(args.repo_dir, args.checkpoint, args.device)
        record['initialization_seconds'] = time.monotonic() - init
        record['native_params'] = adapter.params
        lpips = models.load_lpips(ASSETS, Path(importlib.metadata.distribution('lpips').locate_file('lpips')))
        def metrics(x, y):
            return {**quality(x, y), 'lpips': models.lpips_score(lpips, x, y)}
        vaes = {}
        if len(conditions) > 1:
            from diffusers import AutoencoderKL
            for name, path in [('sd15_vae', ASSETS / 'sd15-fp16/vae'),
                               ('sdxl_vae', MAIN / '.thesis-build/assets/journal-sdxl-vae-6f5909a7')]:
                variant = {'variant': 'fp16'} if name == 'sd15_vae' else {}
                vaes[name] = AutoencoderKL.from_pretrained(path, local_files_only=True, use_safetensors=True,
                      torch_dtype=torch.float32, **variant).eval().requires_grad_(False).to(args.device)
        record['environment'] = {n: importlib.metadata.version(n) for n in ('torch', 'torchvision', 'numpy', 'omegaconf', 'einops')}
        write(args.output_dir / 'run.json', record)
        for sid in ids:
            source = np.asarray(Image.open(SOURCES[sid]).convert('RGB'), np.uint8)
            if source.shape != (512, 512, 3): raise ValueError('Canonical development dimensions changed')
            bits = message(sid)
            for arm, scaling in ARMS.items():
                for control in ('C0', 'C1'):
                    embed_error = None
                    begin = time.monotonic()
                    try:
                        rgb = source.copy() if control == 'C0' else adapter.embed(source, bits, scaling)
                        if args.device == 'cuda': torch.cuda.synchronize()
                        embed_seconds = time.monotonic() - begin
                        clean_path = args.output_dir / 'images' / f'{sid}-{arm}-{control}-input.png'
                        Image.fromarray(rgb).save(clean_path)
                        rgb = np.asarray(Image.open(clean_path).convert('RGB'), np.uint8)
                    except Exception:
                        embed_error = traceback.format_exc()
                    for condition in conditions:
                        row = {'source_id': sid, 'arm': arm, 'control': control, 'condition': condition,
                               'status': 'running', 'message': bits}
                        try:
                            if embed_error: raise RuntimeError(embed_error)
                            if condition == 'clean': attacked = rgb.copy()
                            else:
                                x = torch.from_numpy(rgb.astype(np.float32) / 255).permute(2, 0, 1).unsqueeze(0).to(args.device)
                                with torch.inference_mode():
                                    z = vaes[condition].encode(x * 2 - 1).latent_dist.mode()
                                    y = vaes[condition].decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
                                attacked = np.rint(np.clip(y * .5 + .5, 0, 1) * 255).astype(np.uint8)
                            path = args.output_dir / 'images' / f'{sid}-{arm}-{control}-{condition}.png'
                            Image.fromarray(attacked).save(path)
                            saved = np.asarray(Image.open(path).convert('RGB'), np.uint8)
                            begin = time.monotonic()
                            detection = adapter.detect(saved, bits)
                            if args.device == 'cuda': torch.cuda.synchronize()
                            detect_seconds = time.monotonic() - begin
                            q = metrics(source, saved)
                            strict = (q['psnr_infinite'] or q['psnr_db'] > 35) and q['ssim_rgb'] > .9 and q['lpips'] < .1
                            row.update(status='ok', image=str(path), input_path=str(clean_path), quality_source=q,
                                       quality_input=metrics(rgb, saved), strict_quality_source=bool(strict),
                                       detection=detection, embed_seconds=embed_seconds, detect_seconds=detect_seconds)
                        except Exception:
                            row.update(status='failed', error=traceback.format_exc())
                        rows.append(row)
                        with (args.output_dir / 'rows.jsonl').open('a', encoding='utf-8') as handle:
                            handle.write(json.dumps(row, allow_nan=False) + '\n')
                        print(json.dumps({k: row[k] for k in ('source_id', 'arm', 'control', 'condition', 'status')}), flush=True)
                        if row['status'] == 'failed': print(row['error'], flush=True)
            write(args.output_dir / 'summary.json', summarize(rows))
        record.update(outcome='completed' if all(r['status'] == 'ok' for r in rows) else 'completed_with_failures',
                      rows=len(rows), summary=summarize(rows))
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc())
        raise
    finally:
        record['duration_seconds'] = time.monotonic() - started
        if args.device == 'cuda' and torch.cuda.is_initialized():
            record['peak_cuda_allocated_bytes'] = torch.cuda.max_memory_allocated()
        write(args.output_dir / 'run.json', record)


if __name__ == '__main__':
    main()
