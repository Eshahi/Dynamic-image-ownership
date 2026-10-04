"""Read-only C mechanism diagnostic: scheduler algebra and synthetic CPU arrays.

No pretrained weights, image pixels, GPU tensors, external source execution or
retained-output writes. The retained run is read only for metadata/word counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
DEFAULT_RUN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261004-0031-progressive/run.json")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def diagnose(source_run):
    import numpy as np
    import torch
    from diffusers import DDIMScheduler
    import m1_progressive_latent as candidate
    from three_threat_models import DDIM_CONFIG

    torch.set_num_threads(1)
    run = json.loads(source_run.read_text(encoding="utf-8"))
    if digest(ROOT / "scripts/m1_progressive_latent.py") != run["script_sha256"]:
        raise ValueError("Current candidate source differs from the retained source receipt")
    if run["config"] != candidate.CONFIG or run["outcome"] != "completed":
        raise ValueError("This diagnostic requires the completed original fixed configuration")
    scheduler = DDIMScheduler(**DDIM_CONFIG)
    scheduler.set_timesteps(50)
    table = []
    for i, timestep in enumerate(scheduler.timesteps):
        t = int(timestep)
        a = float(scheduler.alphas_cumprod[t])
        a_prev = float(scheduler.alphas_cumprod[t-20] if t >= 20 else scheduler.final_alpha_cumprod)
        q = math.sqrt(a_prev) - math.sqrt(a * (1-a_prev) / (1-a))
        table.append({"index": i, "timestep": t, "a": a, "a_prev": a_prev,
                      "epsilon_gain": math.sqrt(a / (1-a)), "ddim_z0_gain": q})

    # Synthetic, correlated noisy state/noise pair; this is not a model trajectory.
    rng = torch.Generator(device="cpu").manual_seed(670)
    latent = torch.randn((1, 4, 64, 64), generator=rng).half()
    clean_fixture = .2 * torch.randn((1, 4, 64, 64), generator=rng)
    basis = candidate.dct_matrix(64, device="cpu")
    target, mask = candidate.target_and_mask(.5, basis)
    fixtures = []
    for index in (0, 24, 25, 48, 49):
        item = table[index]; t = item["timestep"]
        a = scheduler.alphas_cumprod[t].float()
        eps = ((latent.float()-a.sqrt()*clean_fixture)/(1-a).sqrt()).half()
        pred = (latent.float()-(1-a).sqrt()*eps.float())/a.sqrt()
        coef = candidate.dct2(pred[0,0], basis)
        for eta in (25., 64., 100.):
            guided = pred.clone()
            guided[0,0] -= eta*candidate.analytic_gradient(pred[0,0], target, mask, basis)
            guided_eps = (latent.float()-a.sqrt()*guided)/(1-a).sqrt()
            supplied_eps = guided_eps.half()
            recovered = (latent.float()-(1-a).sqrt()*supplied_eps.float())/a.sqrt()
            residual_before = (coef-target)[mask.bool()]
            ideal_residual = (candidate.dct2(guided[0,0],basis)-target)[mask.bool()]
            actual_residual = (candidate.dct2(recovered[0,0],basis)-target)[mask.bool()]
            base32 = scheduler.step(eps.float(),t,latent.float(),eta=0.,return_dict=False)[0]
            marked32 = scheduler.step(guided_eps,t,latent.float(),eta=0.,return_dict=False)[0]
            expected_delta = item["ddim_z0_gain"]*(guided-pred)
            error = (marked32-base32)-expected_delta
            norm = float(torch.linalg.vector_norm(expected_delta))
            fixtures.append({"index":index,"timestep":t,"eta":eta,
                "residual_factor":1-2*eta/128,
                "ideal_loss_ratio_measured":float(ideal_residual.square().mean()/residual_before.square().mean()),
                "fp16_epsilon_loss_ratio_measured":float(actual_residual.square().mean()/residual_before.square().mean()),
                "fp16_epsilon_changed_fraction":float((supplied_eps[0,0]!=eps[0,0]).float().mean()),
                "fp16_epsilon_off_channel_changed":int((supplied_eps[:,1:]!=eps[:,1:]).sum()),
                "ddim_float32_transition_relative_error":float(torch.linalg.vector_norm(error))/norm,
                "expected_next_state_delta_l2":norm})

    # Derive the operative ReFFT issue from independent NumPy algebra; never import upstream code.
    np_rng = np.random.default_rng(0)
    x = np_rng.normal(size=(64,64))
    inverse_proxy = np.fft.ifft2(np.fft.fft2(x,norm="ortho").real,norm="ortho").real
    reflected = x[np.ix_((-np.arange(64)) % 64, (-np.arange(64)) % 64)]
    real_fft = {"inverse_relative_error":float(np.linalg.norm(inverse_proxy-x)/np.linalg.norm(x)),
        "even_projection_identity_max_error":float(np.max(np.abs(inverse_proxy-(x+reflected)/2)))}

    target_word = candidate.CONFIG["payload"]
    counts = {}
    for row in run["rows"]:
        if row["outcome"] != "completed":
            raise ValueError("Unexpected non-completed source row")
        key = row["control"] if row["control"] == "C0" else f"a{row['alpha']}-eta{row['eta']}"
        for channel, result in row["conditions"].items():
            for extractor in ("native_vae_dct","image_dct_diagnostic"):
                bits = result[extractor]["bits"]
                matches = sum(a == b for a,b in zip(bits,target_word))
                cell = counts.setdefault(f"{key}/{channel}/{extractor}", [])
                cell.append(matches)
    return {"kind":"CPU algebra and retained-metadata diagnostic, not a model experiment",
        "source_run":str(source_run),"source_run_sha256":digest(source_run),
        "source_script_sha256":run["script_sha256"],"diagnostic_script_sha256":digest(__file__),
        "torch_version":torch.__version__,"numpy_version":np.__version__,
        "scheduler_config":DDIM_CONFIG,"schedule":table,
        "early_q_sum":sum(r["ddim_z0_gain"] for r in table[:25]),
        "late_q_sum":sum(r["ddim_z0_gain"] for r in table[25:]),
        "synthetic_seed":670,"fixtures":fixtures,"real_fft_identity":real_fft,
        "payload_ones":target_word.count("1"),
        "complement_in_original_wrong_hypotheses":''.join('1' if b=='0' else '0' for b in target_word) in candidate.wrong_payloads(),
        "retained_match_vectors":counts}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-run",type=Path,default=DEFAULT_RUN)
    args=parser.parse_args()
    print(json.dumps(diagnose(args.source_run),indent=2,allow_nan=False))
