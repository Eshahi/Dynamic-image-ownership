"""
PhaseMark – quick watermark embed + detect on arbitrary images.

Usage:
    # From a folder
    python fast_try.py --input_dir my_images/ --method sps

    # From specific files
    python fast_try.py --images photo1.png photo2.jpg --method sps --num_embed_ch 4

Output is saved to --output_dir (default: fast_try_output/).
Both the watermarked image and its Hermitian-symmetric variant are saved.
"""
import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from diffusers import AutoencoderKL
from PIL import Image
from tqdm import tqdm

from utils import (
    transform_img, decode_vae_to_pil, enforce_hermitian_symmetry,
    get_bit_blocks, set_random_seed,
    embed_dft_qim, detect_dft_qim,
    embed_latent_fft_quantization, detect_latent_fft_quantization,
    embed_latent_fft_relative_pattern, detect_latent_fft_relative_pattern,
    embed_latent_fft_relative_pulling, detect_latent_fft_relative_pulling,
    get_psnr, compute_verification_thresholds,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TORCH_DTYPE = torch.float32
BLOCK_SIZE = 2
NUM_BITS = 32
R_MIN = 10

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def parse_args():
    parser = argparse.ArgumentParser(description="PhaseMark fast try: embed + detect on arbitrary images")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input_dir", type=str, help="Directory containing input images")
    src.add_argument("--images", nargs="+", type=str, help="One or more image file paths")

    parser.add_argument("--method", type=str, default="ips",
                        choices=["apm", "pcq", "ips", "sps"],
                        help="Watermark method (default: ips)")
    parser.add_argument("--num_embed_ch", type=int, default=4, choices=[1, 2, 3, 4],
                        help="Number of VAE channels to embed in (default: 4)")
    parser.add_argument("--axis_offset", type=int, default=1, choices=[0, 1])
    parser.add_argument("--output_dir", type=str, default="fast_try_output",
                        help="Directory to save watermarked images (default: fast_try_output/)")
    parser.add_argument("--message", type=str, default=None,
                        help="Unicode message to embed. Max length is num_embed_ch * 4 characters "
                             "(4 / 8 / 12 / 16 chars for 1 / 2 / 3 / 4 channels). "
                             "Longer strings are silently truncated. Defaults to a fixed demo string.")
    parser.add_argument("--fpr", type=float, default=1e-2,
                        help="Target false positive rate for hypothesis-testing thresholds (default: 1e-2)")
    parser.add_argument("--user_number", type=int, default=1_000_000,
                        help="Number of users for Bonferroni correction in user attribution (default: 1000000)")
    # VAE model: HuggingFace repo ID or local path
    # Local path example: /mnt/models/stable-diffusion-2-1-base
    parser.add_argument("--vae_model_id", type=str, default="Manojb/stable-diffusion-2-1-base",
                        help="HuggingFace model ID or local path for the VAE "
                             "(default: Manojb/stable-diffusion-2-1-base). "
                             "Local example: /mnt/models/stable-diffusion-2-1-base")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_cfg(args):
    r_max = 18 if args.axis_offset else 17
    ch_map = {1: [3], 2: [2, 3], 3: [1, 2, 3], 4: [0, 1, 2, 3]}
    embed_channels = ch_map[args.num_embed_ch]

    method_map = {
        "apm": (embed_dft_qim, detect_dft_qim),
        "pcq": (embed_latent_fft_quantization, detect_latent_fft_quantization),
        "ips": (embed_latent_fft_relative_pattern, detect_latent_fft_relative_pattern),
        "sps": (embed_latent_fft_relative_pulling, detect_latent_fft_relative_pulling),
    }
    embed_fn, detect_fn = method_map[args.method]

    blocks = get_bit_blocks(shape=(22, 22), num_bits=NUM_BITS, block_size=BLOCK_SIZE,
                            r_min=R_MIN, r_max=r_max, axis_offset=args.axis_offset)
    assert NUM_BITS == len(blocks)

    return SimpleNamespace(
        embed_channels=embed_channels, num_bits=NUM_BITS,
        axis_offset=args.axis_offset, r_min=R_MIN, r_max=r_max,
        embed_latent_fft=embed_fn, detect_latent_fft=detect_fn,
        blocks=blocks,
    )


def make_message_bits(message_str, num_channels, num_bits, device, dtype):
    """
    Encode a Unicode message string into a ±1 bit tensor of length num_channels * num_bits.

    The message is truncated to num_channels * 4 characters before encoding so that
    ASCII-only messages of that length exactly fill num_channels * 32 bits.
    If the encoded bits are shorter than the required total, the leading (MSB) positions
    are filled with uniformly random 0/1 bits. Multi-byte Unicode characters may exceed
    the bit budget; excess bits are dropped from the front.
    """
    max_chars = num_channels * 4
    if len(message_str) > max_chars:
        message_str = message_str[:max_chars]
    raw = message_str.encode("utf-8")
    bits = [int(b) for b in "".join(format(byte, "08b") for byte in raw)]
    total = num_channels * num_bits
    if len(bits) < total:
        pad = torch.randint(0, 2, (total - len(bits),)).tolist()
        bits = pad + bits
    bits = bits[:total]
    return torch.tensor(bits, dtype=dtype, device=device) * 2 - 1


def collect_images(args):
    if args.input_dir:
        folder = Path(args.input_dir)
        paths = sorted(p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXTS)
        if not paths:
            sys.exit(f"No supported images found in {folder}")
    else:
        paths = [Path(p) for p in args.images]
        missing = [p for p in paths if not p.exists()]
        if missing:
            sys.exit(f"Files not found: {missing}")
    return paths


def main():
    args = parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required. CPU-only execution is not supported.")
    device = "cuda"

    set_random_seed(args.seed)
    cfg = build_cfg(args)

    image_paths = collect_images(args)
    print(f"Found {len(image_paths)} image(s). Method: {args.method}, channels: {cfg.embed_channels}")

    # Verification thresholds
    marklength = len(cfg.embed_channels) * cfg.num_bits
    tau_onebit, tau_bits = compute_verification_thresholds(marklength, args.fpr, args.user_number)
    print(f"Thresholds  tau_verification={tau_onebit:.4f}  tau_attribution={tau_bits:.4f}"
          f"  (FPR={args.fpr:.0e}, N={args.user_number:,})")

    # Validate and resolve message
    max_chars = args.num_embed_ch * 4
    default_msg = "PhaseMark2026"
    msg = args.message if args.message else default_msg
    if len(msg) > max_chars:
        print(f"[Warning] --message length ({len(msg)}) exceeds limit ({max_chars} chars) "
              f"for num_embed_ch={args.num_embed_ch}. Truncating to first {max_chars} characters.")
        msg = msg[:max_chars]

    # Output directories
    out_root = Path(args.output_dir)
    out_wm   = out_root / "watermarked"
    out_hs   = out_root / "watermarked_hermitian"
    out_wm.mkdir(parents=True, exist_ok=True)
    out_hs.mkdir(parents=True, exist_ok=True)

    # Load VAE
    print(f"Loading VAE from {args.vae_model_id} ...")
    vae = AutoencoderKL.from_pretrained(args.vae_model_id, subfolder="vae", torch_dtype=TORCH_DTYPE).to(device)
    vae.eval()

    message_bits = make_message_bits(msg, len(cfg.embed_channels), cfg.num_bits, device, TORCH_DTYPE)
    print(f"Message: {repr(msg)} ({len(msg)} chars → {len(cfg.embed_channels) * cfg.num_bits} bits)")

    results = []

    with torch.no_grad():
        for img_path in tqdm(image_paths, desc="Processing"):
            image_pil = Image.open(img_path).convert("RGB")
            input_tensor = transform_img(image_pil).unsqueeze(0).to(device, dtype=TORCH_DTYPE)

            # Encode
            vae_latent = vae.encode(input_tensor).latent_dist.mean
            ldm_latent = vae_latent * vae.config.scaling_factor
            ldm_wm_real = ldm_latent.clone()
            ldm_wm_hs   = ldm_latent.clone()

            # Embed
            for ch_order, ch_idx in enumerate(cfg.embed_channels):
                ch_bit = message_bits[ch_order * cfg.num_bits : (ch_order + 1) * cfg.num_bits]
                fft_ch = torch.fft.fft2(ldm_latent[0, ch_idx, 10:54, 10:54])
                fft_wm = cfg.embed_latent_fft(fft_ch, ch_bit, cfg.blocks)
                fft_hs = torch.fft.ifftshift(
                    enforce_hermitian_symmetry(
                        torch.fft.fftshift(fft_wm.unsqueeze(0).unsqueeze(0))
                    )[0, 0]
                )
                ldm_wm_real[0, ch_idx, 10:54, 10:54] = torch.fft.ifft2(fft_wm).real
                ldm_wm_hs[0, ch_idx, 10:54, 10:54]   = torch.fft.ifft2(fft_hs).real

            # Decode
            out_real = vae.decode(ldm_wm_real / vae.config.scaling_factor).sample.detach()
            out_hs_t = vae.decode(ldm_wm_hs   / vae.config.scaling_factor).sample.detach()
            pil_wm   = decode_vae_to_pil(out_real)
            pil_hs   = decode_vae_to_pil(out_hs_t)

            # Instant detection on watermarked image
            def detect_from_pil(pil_img):
                t = transform_img(pil_img).unsqueeze(0).to(device, dtype=TORCH_DTYPE)
                lat = vae.encode(t).latent_dist.mean * vae.config.scaling_factor
                bits_list = []
                for ch_idx in cfg.embed_channels:
                    fft_ch = torch.fft.fft2(lat[0, ch_idx, 10:54, 10:54])
                    bits_list.append(cfg.detect_latent_fft(fft_ch, cfg.blocks))
                return torch.cat(bits_list, dim=0)

            det_real = detect_from_pil(pil_wm)
            det_hs   = detect_from_pil(pil_hs)
            total_bits = len(cfg.embed_channels) * cfg.num_bits
            acc_real = (message_bits.cpu() == det_real.cpu()).sum().item() / total_bits
            acc_hs   = (message_bits.cpu() == det_hs.cpu()).sum().item() / total_bits

            psnr_val = get_psnr(image_pil, pil_wm)

            # Save
            stem = img_path.stem
            pil_wm.save(out_wm / f"{stem}_wm.png")
            pil_hs.save(out_hs / f"{stem}_wm_hs.png")

            results.append({
                "file": img_path.name,
                "bit_acc": acc_real,
                "bit_acc_hs": acc_hs,
                "psnr": psnr_val,
                "verified":      acc_real >= tau_onebit,
                "attributed":    acc_real >= tau_bits,
                "verified_hs":   acc_hs   >= tau_onebit,
                "attributed_hs": acc_hs   >= tau_bits,
            })

    # Summary
    W = 78
    print("\n" + "=" * W)
    print(f"{'File':<26} {'BA':>6} {'BA(HS)':>8} {'PSNR':>7}  {'V':>2} {'A':>2}  {'V(HS)':>5} {'A(HS)':>5}")
    print("-" * W)
    for r in results:
        v  = "Y" if r["verified"]      else "."
        a  = "Y" if r["attributed"]    else "."
        vh = "Y" if r["verified_hs"]   else "."
        ah = "Y" if r["attributed_hs"] else "."
        print(f"{r['file']:<26} {r['bit_acc']:>6.3f} {r['bit_acc_hs']:>8.3f} {r['psnr']:>7.2f}  {v:>2} {a:>2}  {vh:>5} {ah:>5}")
    print("=" * W)
    print(f"Mean BA                : {np.mean([r['bit_acc']    for r in results]):.4f}")
    print(f"Mean BA (HS)           : {np.mean([r['bit_acc_hs'] for r in results]):.4f}")
    print(f"Mean PSNR              : {np.mean([r['psnr']       for r in results]):.4f} dB")
    print(f"Verification  TPR      : {np.mean([r['verified']      for r in results]):.4f}"
          f"  (tau={tau_onebit:.4f}, FPR={args.fpr:.0e})")
    print(f"Verification  TPR (HS) : {np.mean([r['verified_hs']   for r in results]):.4f}")
    print(f"Attribution   TPR      : {np.mean([r['attributed']     for r in results]):.4f}"
          f"  (tau={tau_bits:.4f}, FPR={args.fpr:.0e}, N={args.user_number:,})")
    print(f"Attribution   TPR (HS) : {np.mean([r['attributed_hs']  for r in results]):.4f}")
    print(f"\nV=Verification  A=Attribution (Y=pass, .=fail)")
    print(f"Watermarked images saved to: {out_root.resolve()}")


if __name__ == "__main__":
    main()
