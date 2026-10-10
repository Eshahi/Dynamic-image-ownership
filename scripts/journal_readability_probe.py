"""Frozen fixed-payload readability refinement; USD 0 development screen only.

The straight-through RGB8 gradient is approximate. All saved-image evaluations
use the unchanged F5 reader and suspect-derived features. No diffusion runs.
"""
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
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from journal_vae_probe import Evaluator, compact as compact_base, F5_RUN, SDXL, SDXL_REV, SOURCES, write
from journal_binding_probe import delivery
from f4_transfer_probe import MAIN
from f5_gate import OWNERS
from scripts import f5_latent_codec as f5
from scripts import revised_watermark_v5 as v5

IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015,
       190676, 468505, 499768)
CONDITIONS = ("clean", "sd15_vae", "sdxl_vae")
CONFIGS = {"R1": (("clean",), 52.), "R2": (("clean", "sdxl_vae"), 52.),
           "R3": (CONDITIONS, 52.), "R4": (CONDITIONS, 46.)}
DISCOVERY = MAIN / ".thesis-build/dev-runs/20261010-0903-journal-vae"
OPTIMIZATION_CAP = 10800.
EVALUATION_CAP = 2700.  # Shared with follow-up work; parent subtracts measured screen cost.


def compact(result):
    if result["binding_mode"] != "combined":
        raise ValueError("This diagnostic wrapper records the native combined rule only")
    other_content = result["semantic"]["found"] and result["semantic"]["content_status"] != "match"
    return dict(compact_base(result), semantic_code=result["semantic_code"],
        perceptual_hash=result["perceptual_hash"],
        native_q_bound=result["semantic"]["decoded_code"] if other_content else result["semantic_code"],
        native_q_bound_rule="decoded_q_on_found_content_mismatch_else_suspect_q")


def load(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB"), np.uint8)


def patterns(profile, q):
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(OWNERS[0])
    table = v5._semantic_table(owner, key, config)
    correct = np.asarray([table[j][v5._bit(q, j)] for j in range(32)], np.float64)
    alternative = np.asarray([table[j][1 - v5._bit(q, j)] for j in range(32)], np.float64)
    return f5.Layout(checked, key, config, owner), correct.reshape(-1), correct - alternative


def projection_stats(p, w, gaps):
    p = np.asarray(p, np.float64)
    norm = float(np.linalg.norm(p))
    raw = (p.reshape(32, 10) * gaps).sum(1)
    return dict(fixed_q_score=float(w @ p / max(norm, 1e-8)),
                projection_norm=norm, raw_bit_gaps=raw.tolist(),
                normalized_bit_gaps=(raw / max(norm / math.sqrt(320), 1e-8)).tolist(),
                minimum_bit_gap=float(raw.min()))


def decompose(host, marked, identity_delta, w, gaps, identity_alpha):
    host, marked = np.asarray(host), np.asarray(marked)
    delta = marked - host
    alpha = float(w @ delta / 320)
    residual = delta - alpha * w
    denom = float(np.linalg.norm(delta) * np.linalg.norm(identity_delta))
    host_gaps = (host.reshape(32, 10) * gaps).sum(1)
    mark_gaps = (delta.reshape(32, 10) * gaps).sum(1)
    return dict(alpha=alpha, host_signed_projection=float(w @ host / 320),
                delta_norm=float(np.linalg.norm(delta)), residual_norm=float(np.linalg.norm(residual)),
                host_norm=float(np.linalg.norm(host)),
                carrier_gain=alpha / identity_alpha if identity_alpha != 0 else None,
                carrier_gain_undefined=identity_alpha == 0,
                displacement_alignment=float(delta @ identity_delta / denom) if denom else None,
                alignment_undefined=denom == 0,
                host_bit_gaps=host_gaps.tolist(), mark_bit_gaps=mark_gaps.tolist(),
                observed_bit_gaps=(host_gaps + mark_gaps).tolist(),
                decomposition_max_error=float(np.max(np.abs(host_gaps + mark_gaps -
                    (marked.reshape(32, 10) * gaps).sum(1)))),
                **projection_stats(marked, w, gaps))


def payload(ev, sid):
    rgb = load(F5_RUN / "images" / f"clean-{sid}-C1.png")
    result = ev.detect(rgb, "f5", OWNERS[0])
    if not (result["semantic"]["read"] and result["instance"]["read"]):
        raise ValueError(f"Saved fixed payload unreadable for {sid}")
    decoded_q, h = (int(result[tier]["decoded_code"], 16) for tier in ("semantic", "instance"))
    original = [json.loads(line) for line in (F5_RUN / "rows.jsonl").read_text().splitlines()]
    reports = [r["report"] for r in original if r.get("id") == f"embed-{sid}"]
    if len(reports) != 1:
        raise ValueError(f"Original recorded semantic payload missing or ambiguous for {sid}")
    q = int(reports[0]["semantic_code"], 16)
    frozen_rows = [json.loads(line) for line in (DISCOVERY / "rows.jsonl").read_text().splitlines()]
    frozen = [r for r in frozen_rows if r["source_id"] == sid and r["method"] == "f5"
              and r["control"] == "C1" and r["condition"] == "clean"]
    if len(frozen) != 1:
        raise ValueError(f"Frozen operational payload missing or ambiguous for {sid}")
    frozen_call = frozen[0]["calls"][OWNERS[0]]
    if (not all(frozen_call[tier]["read"] for tier in ("semantic", "instance")) or
            any(result[tier]["decoded_code"] != frozen_call[tier]["decoded_code"]
                for tier in ("semantic", "instance"))):
        raise ValueError(f"Fresh clean extraction differs from frozen operational payload for {sid}")
    if rgb.shape != (512, 512, 3):
        raise ValueError("Fixed protocol requires RGB 512x512")
    return rgb, q, h, dict(q=f"{q:08x}", h=f"{h:08x}", extraction=compact(result),
                            original_semantic_code=reports[0]["semantic_code"],
                            clean_decoded_q=f"{decoded_q:08x}", clean_q_bit_errors=(q ^ decoded_q).bit_count(),
                            q_target_basis="original recorded intended embedding payload",
                            original_h_known=False, frozen_extraction_confirmed=True,
                            h_target_basis="saved clean C1 native-decoded operational target; original embedded h unrecorded")


class Objective:
    def __init__(self, ev, other, layout, w, gaps):
        self.torch, self.reader, self.other = ev.torch, ev.reader, other
        t, dev = self.torch, self.reader.device
        self.D = t.as_tensor(layout.dct, dtype=t.float32, device=dev)
        self.ch, self.u, self.v = (t.as_tensor(a, device=dev) for a in (layout.ch, layout.u, layout.v))
        self.coeff = t.as_tensor(layout.weights * layout.signs, dtype=t.float32, device=dev)
        self.chip = t.as_tensor(layout.chip, device=dev)
        self.norms = t.as_tensor(layout.norms, dtype=t.float32, device=dev)
        self.w = t.as_tensor(w, dtype=t.float32, device=dev)
        self.gaps = t.as_tensor(gaps, dtype=t.float32, device=dev)
        self.checkpointed = bool(getattr(self.reader.vae, "_readability_checkpointed", False))
        self.memory_errors = []

    def quantize(self, x):
        x = x.clamp(0, 1)
        return x + (self.torch.round(x * 255) / 255 - x).detach()

    def call(self, fn, x):
        if self.checkpointed and self.torch.is_grad_enabled() and x.requires_grad:
            from torch.utils.checkpoint import checkpoint
            return checkpoint(fn, x, use_reentrant=False)
        return fn(x)

    def projection(self, x, condition):
        x = self.quantize(x)
        if condition != "clean":
            vae = self.reader.vae if condition == "sd15_vae" else self.other
            z = self.call(lambda a: vae.encode(a).latent_dist.mode(), x * 2 - 1)
            y = self.call(lambda a: vae.decode(a).sample, z)
            x = self.quantize((y + 1) / 2)
        z = self.call(lambda a: self.reader.vae.encode(a).latent_dist.mode(), x * 2 - 1)[0] * f5.SCALE
        c = self.torch.einsum("ij,cjk,lk->cil", self.D, z, self.D)
        total = self.torch.zeros(320, device=x.device).index_add(0, self.chip, c[self.ch, self.u, self.v] * self.coeff)
        return total / self.norms

    def loss_details(self, x, condition):
        p = self.projection(x, condition)
        norm = p.norm().clamp_min(1e-8)
        score = (self.w * p).sum() / norm
        sigma = (p.norm() / math.sqrt(320)).clamp_min(1e-8)
        gaps = (p.reshape(32, 10) * self.gaps).sum(1) / sigma
        score_hinge, bit_hinges = 9 - score, 1 - gaps
        loss = self.torch.relu(score_hinge).square() + self.torch.relu(bit_hinges).square().mean()
        return loss, dict(score_hinge=float(score_hinge.detach().item()),
            maximum_bit_hinge=float(bit_hinges.detach().max().item()),
            hinges_inactive=bool((score_hinge <= 0).item() and (bit_hinges <= 0).all().item()),
            finite_forward=bool(self.torch.isfinite(score).item() and self.torch.isfinite(gaps).all().item()))

    def loss(self, x, condition):
        return self.loss_details(x, condition)[0]

    def gradient(self, x, branches):
        # Deterministic first maximum breaks ties in clean, SD1.5, SDXL order.
        with self.torch.no_grad():
            evaluations = [self.loss_details(x, b) for b in branches]
            values = [float(loss.item()) for loss, _ in evaluations]
            details = {b: detail for b, (_, detail) in zip(branches, evaluations)}
        if not all(math.isfinite(v) for v in values) or not all(d["finite_forward"] for d in details.values()):
            raise ValueError("Nonfinite branch objective")
        worst = int(np.argmax(values))
        loss, active_details = self.loss_details(x, branches[worst])
        g, = self.torch.autograd.grad(loss, x)
        if not bool(self.torch.isfinite(g).all()):
            raise ValueError("Nonfinite input gradient")
        return g, dict(branch_losses=dict(zip(branches, values)), active_branch=branches[worst],
                       branch_details=details, active_details=active_details,
                       active_loss=float(loss.detach().item()), gradient_norm=float(g.norm().item()),
                       gradient_exact_zero=bool((g == 0).all().item()))

    def enable_checkpointing(self):
        # Diffusers enables checkpoints inside the encoder/decoder blocks; outer
        # checkpoints preserve precisely the same encode/decode forward function.
        for vae in (self.reader.vae, self.other):
            vae.enable_gradient_checkpointing()
            vae._readability_checkpointed = True
        self.checkpointed = True


def projected_update(candidate, reference, source, additional_budget, total_budget, torch):
    """Successive convex projections; reject unresolved numerical feasibility."""
    proposed = candidate.clamp(0, 1)
    for _ in range(100):
        for center, radius in ((reference, additional_budget), (source, total_budget)):
            delta = proposed - center
            proposed = center + delta * (radius / delta.norm().clamp_min(1e-12)).clamp_max(1)
        proposed = proposed.clamp(0, 1)
        if (float((proposed - reference).norm()) <= additional_budget * (1 + 1e-6)
                and float((proposed - source).norm()) <= total_budget * (1 + 1e-6)):
            return proposed, True
    return candidate, False


def exact_stationary(stats, projected_equal, strictly_feasible):
    """No tolerances: underflowed positive hinges or projection drift cannot stop."""
    return bool(projected_equal and strictly_feasible and stats["gradient_exact_zero"] and
        stats["active_loss"] == 0 and stats["active_details"]["finite_forward"] and
        stats["active_details"]["hinges_inactive"] and
        all(value == 0 for value in stats["branch_losses"].values()) and
        all(d["finite_forward"] and d["hinges_inactive"] and d["score_hinge"] <= 0 and
            d["maximum_bit_hinge"] <= 0 for d in stats["branch_details"].values()))


def restore_fragile(rgb, q, h, profile):
    checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(OWNERS[0])
    before = v5.luminance_from_rgb(rgb.tolist())
    marked = [[float(value) for value in row] for row in before]
    height, width = f5.base._check_image(before, int(checked["minimum_side"]))
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    table = v5._instance_table(owner, key, config)
    wi = [chip for j in range(32) for chip in table[j][v5._bit(q, j)][v5._bit(h, j)]]
    report = v5._embed_fragile(marked, fragile, wi, checked, False, True)
    restored = np.clip(np.rint(rgb.astype(float) + (np.asarray(marked) - before)[..., None]), 0, 255).astype(np.uint8)
    return restored, report


def iteration(obj, x, branches):
    failed = False
    try:
        return obj.gradient(x, branches)
    except obj.torch.cuda.OutOfMemoryError as error:
        obj.memory_errors.append(dict(checkpointed=obj.checkpointed, branches=list(branches), error=str(error)))
        if obj.checkpointed:
            raise
        failed = True
    # Leave the exception scope first so its traceback cannot retain the failed graph.
    if failed:
        gc.collect()
        obj.torch.cuda.empty_cache()
        obj.enable_checkpointing()
        return obj.gradient(x, branches)


def refine(ev, other, rgb, source, q, config, remaining, activation_checkpointing=False):
    branches, db = CONFIGS[config]
    t = ev.torch
    layout, w, gaps = patterns(ev.profile, q)
    obj = Objective(ev, other, layout, w, gaps)
    if activation_checkpointing and not obj.checkpointed:
        obj.enable_checkpointing()
    reference, clean = (ev.reader.tensor(a / 255.) for a in (rgb, source))
    budget = math.sqrt(rgb.size) * 10 ** (-db / 20)
    total_budget = math.sqrt(rgb.size) * 10 ** (-35.1 / 20)
    if float((reference - clean).norm()) > total_budget:
        raise ValueError("Starting C1 infeasible at total 35.1 dB continuous constraint")
    x = reference.detach().clone().requires_grad_(True)
    history, rejected, shortcut = [], 0, None
    t.cuda.synchronize()
    tick = time.monotonic()
    t.cuda.reset_peak_memory_stats()
    for step in range(100):
        if time.monotonic() - tick >= remaining:
            return None, dict(status="unrun_budget", completed_steps=step,
                              physical_steps=len(history), logical_steps=step, skipped_stationary_steps=0,
                              optimization_seconds=time.monotonic() - tick, history=history)
        g, stats = iteration(obj, x, branches)
        with t.no_grad():
            lr = budget * (.2 if step < 50 else .05)
            proposal = x - lr * g / (g.norm() + 1e-12)
            proposed, feasible = projected_update(proposal, reference, clean, budget, total_budget, t)
            projection_equal = bool(t.equal(proposed, x))
            strictly_feasible = (feasible and bool(((x >= 0) & (x <= 1)).all().item()) and
                float((x - reference).norm()) <= budget and float((x - clean).norm()) <= total_budget)
            stationary = exact_stationary(stats, projection_equal, strictly_feasible)
            stats.update(projection_exact_fixed_point=projection_equal,
                         stationary_strict_feasibility=strictly_feasible)
            if feasible:
                x.copy_(proposed)
            else:
                rejected += 1
            stats.update(step=step, accepted_update=feasible)
            history.append(stats)
        del g
        if stationary:
            shortcut = dict(step=step, branch_losses=stats["branch_losses"],
                branch_details=stats["branch_details"], projection_exact_fixed_point=projection_equal,
                strictly_feasible=strictly_feasible)
            break
    t.cuda.synchronize()
    result = np.rint(x.detach()[0].permute(1, 2, 0).cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    return result, dict(status="ok", completed_steps=100, optimization_seconds=time.monotonic() - tick,
        physical_steps=len(history), logical_steps=100, skipped_stationary_steps=100-len(history),
        stationary_shortcut=shortcut,
        peak_allocated_bytes=t.cuda.max_memory_allocated(), peak_reserved_bytes=t.cuda.max_memory_reserved(),
        checkpointed=obj.checkpointed, memory_errors=obj.memory_errors, rejected_updates=rejected, history=history,
        continuous_additional_rms=float((x.detach() - reference).square().mean().sqrt()),
        continuous_total_rms=float((x.detach() - clean).square().mean().sqrt()))


def reconstruct(ev, other, rgb, condition):
    if condition == "clean":
        return rgb.copy()
    vae = ev.reader.vae if condition == "sd15_vae" else other
    with ev.torch.inference_mode():
        x = ev.reader.tensor(rgb / 255.)
        z = vae.encode(x * 2 - 1).latent_dist.mode()
        y = vae.decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
    return np.rint(np.clip((y + 1) / 2, 0, 1) * 255).astype(np.uint8)


def evaluate(ev, rgb, source, input_rgb, q, h):
    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
    calls = {o: ev.detect(rgb, "f5", o, features, latent) for o in OWNERS[:2]}
    intended = calls[OWNERS[0]]
    layout, w, gaps = patterns(ev.profile, q)
    return dict(calls={o: compact(c) for o, c in calls.items()}, delivery=delivery(intended, q, h),
        joint_fixed_q=bool(intended["semantic"]["read"] and
            int(intended["semantic"]["decoded_code"], 16) == q and intended["semantic"]["content_match"]),
        quality_source=ev.metrics(source, rgb), quality_input=ev.metrics(input_rgb, rgb),
        diagnostics=projection_stats(layout.projections(latent), w, gaps),
        _projections=np.asarray(layout.projections(latent)))


def summary(rows):
    result = {}
    for config in CONFIGS:
        good = [r for r in rows if r.get("config") == config and r["status"] == "ok"]
        clean = [r["conditions"]["clean"] for r in good]
        strict = sum(c["quality_source"]["psnr_db"] > 35 and c["quality_source"]["ssim_rgb"] > .9 and
                     c["quality_source"]["lpips"] < .1 and c["delivery"]["both_exact"] and
                     c["calls"][OWNERS[0]]["outcome"] == "both_match" for c in clean)
        counts = {b: sum(r["conditions"][b]["joint_fixed_q"] for r in good) for b in CONDITIONS}
        negatives = sum(r["conditions"][b]["calls"][OWNERS[1]]["watermark_found"] or
                        r["conditions"][b]["c0_call"]["watermark_found"] for r in good for b in CONDITIONS)
        c0_any = sum(r["conditions"][b]["c0_call"]["watermark_found"] for r in good for b in CONDITIONS)
        wrong_any = sum(r["conditions"][b]["calls"][OWNERS[1]]["watermark_found"] for r in good for b in CONDITIONS)
        eligible = len(good) == 12 and strict == 12 and negatives == 0 and counts["sd15_vae"] == 12 and counts["sdxl_vae"] >= 11
        result[config] = dict(planned_sources=12, completed=len(good), missing_or_failed=12-len(good),
            strict_clean=strict, joint_fixed_q=counts, negative_any=negatives, survivor=eligible,
            c0_any=c0_any, wrong_owner_any=wrong_any, planned_calls_per_negative_cell=36,
            completed_calls_per_negative_cell=3*len(good),
            minimum_reconstruction_score=min((r["conditions"][b]["diagnostics"]["fixed_q_score"] for r in good for b in CONDITIONS[1:]), default=None),
            mean_clean_lpips=float(np.mean([c["quality_source"]["lpips"] for c in clean])) if clean else None,
            proxy={str(limit): {b: dict(denominator=12,
                qualified=sum(r["conditions"][b]["quality_input"]["lpips"] <= limit for r in good),
                joint_fixed_q=sum(r["conditions"][b]["joint_fixed_q"] and r["conditions"][b]["quality_input"]["lpips"] <= limit for r in good))
                for b in CONDITIONS[1:]} for limit in (.2, .3)})
    result["ranked_survivors"] = sorted([c for c in CONFIGS if result[c]["survivor"]], key=lambda c:
        (-result[c]["joint_fixed_q"]["sdxl_vae"], -result[c]["minimum_reconstruction_score"],
         result[c]["mean_clean_lpips"], list(CONFIGS).index(c)))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase", required=True, choices=("smoke", "diagnostic", "screen"))
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--resume-by-existing-completed-file", action="store_true")
    p.add_argument("--smoke-result", type=Path, help="Optional smoke run.json for prospective timing estimate")
    p.add_argument("--activation-checkpointing", action="store_true",
                   help="Enable identical-forward fp32 VAE activation checkpoints before the first gradient")
    a = p.parse_args()
    if a.resume_by_existing_completed_file and a.phase != "screen":
        p.error("Resume-by-completed-source is only available for the screen phase")
    if tuple(sorted(SOURCES)) != IDS:
        raise ValueError("Frozen development identities have changed")
    smoke_input = json.loads(a.smoke_result.read_text()) if a.smoke_result else None
    checkpoint_from_smoke = bool(a.phase == "screen" and smoke_input and smoke_input["smoke"]["checkpointed"])
    activation_checkpointing = a.activation_checkpointing or checkpoint_from_smoke
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=a.resume_by_existing_completed_file)
    (out / "images").mkdir(exist_ok=a.resume_by_existing_completed_file)
    (out / "completed").mkdir(exist_ok=a.resume_by_existing_completed_file)
    old = json.loads((out / "run.json").read_text()) if a.resume_by_existing_completed_file else None
    if old and (old["phase"] != a.phase or old["sources"] != list(IDS)):
        raise ValueError("Resume phase/source identity mismatch")
    started = time.monotonic()
    record = dict(schema="journal-readability-probe-v1", phase=a.phase,
        commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command=sys.argv, sources=list(IDS), data_split="development", seeds=[],
        config=dict(configurations=CONFIGS, steps=100, learning_rate_fractions=[.2, .05],
            total_psnr_constraint_db=35.1, target_score=9., target_gap=1.,
            precision="float32", straight_through_quantization=True, mask_power=0.,
            sd15_assets="sd15-fp16/vae", sdxl_revision=SDXL_REV,
            optimization_cap_seconds=OPTIMIZATION_CAP, human_admissibility="missing",
            evaluation_and_followup_cap_seconds=EVALUATION_CAP,
            activation_checkpointing=activation_checkpointing,
            activation_checkpointing_choice=("explicit_cli" if a.activation_checkpointing else
                "inherited_smoke" if checkpoint_from_smoke else "ordinary_with_oom_retry"),
            stationary_shortcut="Exact inactive hinges on every branch, exact zero gradient and fixed-point feasible projection only",
            compute_amendment="research/journal-upgrade-20261009/readability-compute-amendment.md",
            payload_amendment="research/journal-upgrade-20261009/readability-payload-amendment.md",
            fixed_marks=str(F5_RUN), frozen_discovery=str(DISCOVERY)),
        optimization_seconds=old.get("optimization_seconds", 0.) if old else 0.,
        evaluation_seconds=old.get("evaluation_seconds", 0.) if old else 0., outcome="running")
    if old:
        record["prior_invocations"] = old.get("prior_invocations", []) + [dict(commit=old["commit"], command=old["command"], outcome=old["outcome"])]
    write(out / "run.json", record)
    rows = []
    def emit(row):
        rows.append(row)
        with (out / "rows.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, allow_nan=False) + "\n")
        if row["status"] == "ok":
            write(out / "completed" / f'{row.get("config", a.phase)}-{row["source_id"]}.json', row)
        write(out / "run.json", record)
        print(json.dumps({k: row[k] for k in ("source_id", "status", "config") if k in row}), flush=True)
    try:
        ev = Evaluator()
        record["profile"] = ev.profile
        if a.phase == "diagnostic":
            for sid in IDS:
                row = dict(source_id=sid, status="running")
                try:
                    _, q, h, row["payload"] = payload(ev, sid)
                    layout, w, gaps = patterns(ev.profile, q)
                    projections, calls = {}, {}
                    for condition in CONDITIONS:
                        projections[condition] = {}
                        for control in ("C0", "C1"):
                            image = load(DISCOVERY / "images" / f"{sid}-f5-{control}-{condition}.png")
                            z = ev.reader.latent(image)
                            projections[condition][control] = np.asarray(layout.projections(z))
                            if control == "C1":
                                calls[condition] = ev.detect(image, "f5", OWNERS[0], latent=z)
                    identity_delta = projections["clean"]["C1"] - projections["clean"]["C0"]
                    alpha = float(w @ identity_delta / 320)
                    row["conditions"] = {b: dict(decomposition=decompose(projections[b]["C0"], projections[b]["C1"], identity_delta, w, gaps, alpha),
                        native=compact(calls[b]), delivery=delivery(calls[b], q, h),
                        joint_fixed_q=bool(calls[b]["semantic"]["read"] and int(calls[b]["semantic"]["decoded_code"],16)==q and calls[b]["semantic"]["content_match"])) for b in CONDITIONS}
                    row["status"] = "ok"
                except Exception:
                    row.update(status="failed", error=traceback.format_exc())
                emit(row)
        else:
            from diffusers import AutoencoderKL
            other = AutoencoderKL.from_pretrained(SDXL, use_safetensors=True, local_files_only=True,
                torch_dtype=ev.torch.float32).eval().requires_grad_(False).to("cuda")
            record["gpu"] = ev.torch.cuda.get_device_name(0)
            if a.phase == "smoke":
                sid = IDS[0]
                rgb, q, _, fixed = payload(ev, sid)
                obj = Objective(ev, other, *patterns(ev.profile, q))
                if activation_checkpointing:
                    obj.enable_checkpointing()
                x = ev.reader.tensor(rgb / 255.).requires_grad_(True)
                ev.torch.cuda.reset_peak_memory_stats()
                ev.torch.cuda.synchronize()
                tick = time.monotonic()
                # Test every active path, then measure the actual worst-branch
                # schedule once. All trial gradients/updates are discarded.
                branch_smoke = {}
                record["smoke"] = dict(branch_feasibility=branch_smoke, memory_errors=obj.memory_errors,
                    trial_update="discarded; no pixels saved or advanced")
                for branch in CONDITIONS:
                    ev.torch.cuda.reset_peak_memory_stats()
                    branch_tick = time.monotonic()
                    try:
                        g, branch_stats = iteration(obj, x, (branch,))
                    except Exception:
                        branch_smoke[branch] = dict(status="failed", error=traceback.format_exc(),
                            checkpointed=obj.checkpointed, memory_errors=list(obj.memory_errors),
                            seconds=time.monotonic()-branch_tick,
                            peak_allocated_bytes=ev.torch.cuda.max_memory_allocated(),
                            peak_reserved_bytes=ev.torch.cuda.max_memory_reserved())
                        write(out / "run.json", record)
                        raise
                    ev.torch.cuda.synchronize()
                    branch_smoke[branch] = dict(**branch_stats,
                        status="ok",
                        seconds=time.monotonic()-branch_tick, checkpointed=obj.checkpointed,
                        peak_allocated_bytes=ev.torch.cuda.max_memory_allocated(),
                        peak_reserved_bytes=ev.torch.cuda.max_memory_reserved())
                    del g
                    write(out / "run.json", record)
                ev.torch.cuda.reset_peak_memory_stats()
                ev.torch.cuda.synchronize()
                tick = time.monotonic()
                g, stats = iteration(obj, x, CONDITIONS)
                ev.torch.cuda.synchronize()
                elapsed = time.monotonic() - tick
                record["smoke"] = dict(**stats, seconds_per_iteration=elapsed, checkpointed=obj.checkpointed,
                    branch_feasibility=branch_smoke, memory_errors=obj.memory_errors,
                    peak_allocated_bytes=ev.torch.cuda.max_memory_allocated(), peak_reserved_bytes=ev.torch.cuda.max_memory_reserved(),
                    trial_update="discarded; no pixels saved or advanced", projected_4800_iterations_seconds=elapsed * 4800)
                del g, x
                emit(dict(source_id=sid, config="R3", status="ok", payload=fixed, smoke=record["smoke"]))
            else:
                from PIL import Image
                if a.smoke_result:
                    smoke = smoke_input["smoke"]
                    record["timing_projection"] = dict(source=str(a.smoke_result),
                        full_screen_seconds=smoke["seconds_per_iteration"] * 4800,
                        exceeds_optimization_cap=smoke["seconds_per_iteration"] * 4800 > OPTIMIZATION_CAP)
                for config in CONFIGS:
                    for sid in IDS:
                        existing = out / "completed" / f"{config}-{sid}.json"
                        if a.resume_by_existing_completed_file and existing.exists():
                            rows.append(json.loads(existing.read_text()))
                            continue
                        row = dict(source_id=sid, config=config, status="running")
                        remaining = OPTIMIZATION_CAP - record["optimization_seconds"]
                        tick = None
                        evaluation_tick = None
                        try:
                            if remaining <= 0 or record["evaluation_seconds"] >= EVALUATION_CAP:
                                row.update(status="unrun_budget", reason="Optimization or shared evaluation cap exhausted")
                            else:
                                rgb, q, h, row["payload"] = payload(ev, sid)
                                source = load(SOURCES[sid])
                                tick = time.monotonic()
                                refined, stats = refine(ev, other, rgb, source, q, config, remaining,
                                                        activation_checkpointing)
                                record["optimization_seconds"] += stats["optimization_seconds"]
                                tick = None
                                row["refinement"] = stats
                                if refined is None:
                                    row.update(status="unrun_budget", reason="100-step refinement not completed; no partial winner")
                                else:
                                    evaluation_tick = time.monotonic()
                                    final, row["fragile_report"] = restore_fragile(refined, q, h, ev.profile)
                                    row["restoration_rms"] = float(np.sqrt(np.mean(((final.astype(float)-refined)/255)**2)))
                                    row["final_c1_relative_rms"] = float(np.sqrt(np.mean(((final.astype(float)-rgb)/255)**2)))
                                    row["conditions"] = {}
                                    decomposition_inputs = {}
                                    for condition in CONDITIONS:
                                        if record["evaluation_seconds"] + time.monotonic()-evaluation_tick >= EVALUATION_CAP:
                                            raise RuntimeError("Shared 45-minute evaluation budget exhausted; incomplete source is unresolved")
                                        transformed = reconstruct(ev, other, final, condition)
                                        image = out / "images" / f"{config}-{sid}-C1-{condition}.png"
                                        Image.fromarray(transformed).save(image)
                                        saved = load(image)
                                        entry = evaluate(ev, saved, source, final, q, h)
                                        entry["image"] = str(image)
                                        c0 = load(DISCOVERY / "images" / f"{sid}-f5-C0-{condition}.png")
                                        if condition == "clean" and not np.array_equal(c0, source):
                                            raise ValueError("Discovery clean C0 differs from canonical source")
                                        c0_latent = ev.reader.latent(c0)
                                        entry["c0_call"] = compact(ev.detect(c0, "f5", OWNERS[0], latent=c0_latent))
                                        layout, w, gaps = patterns(ev.profile, q)
                                        decomposition_inputs[condition] = (np.asarray(layout.projections(c0_latent)), entry.pop("_projections"))
                                        row["conditions"][condition] = entry
                                    b0, p0 = decomposition_inputs["clean"]
                                    identity_delta = p0 - b0
                                    identity_alpha = float(w @ identity_delta / 320)
                                    for condition, (b, p_) in decomposition_inputs.items():
                                        row["conditions"][condition]["decomposition"] = decompose(b, p_, identity_delta, w, gaps, identity_alpha)
                                    row["status"] = "ok"
                        except Exception:
                            if tick is not None:
                                record["optimization_seconds"] += time.monotonic() - tick
                            row.update(status="failed", error=traceback.format_exc())
                            gc.collect()
                            ev.torch.cuda.empty_cache()
                        if evaluation_tick is not None:
                            row["evaluation_seconds"] = time.monotonic() - evaluation_tick
                            record["evaluation_seconds"] += row["evaluation_seconds"]
                        emit(row)
                        write(out / "summary.json", summary(rows))
                record["summary"] = summary(rows)
        record["outcome"] = "completed" if all(r["status"] == "ok" for r in rows) else "completed_with_failures_or_budget_missing"
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
        if a.phase == "screen":
            seen = {(r["config"], r["source_id"]) for r in rows}
            for config in CONFIGS:
                for sid in IDS:
                    if (config, sid) not in seen:
                        emit(dict(config=config, source_id=sid, status="failed", reason="Setup/fatal failure; see run.json"))
        else:
            seen = {r["source_id"] for r in rows}
            for sid in (IDS if a.phase == "diagnostic" else IDS[:1]):
                if sid not in seen:
                    emit(dict(source_id=sid, status="failed", reason="Setup/fatal failure; see run.json"))
        raise
    finally:
        record["duration_seconds"] = time.monotonic() - started
        record["optimization_budget_remaining_seconds"] = max(0., OPTIMIZATION_CAP-record["optimization_seconds"])
        record["evaluation_and_followup_budget_remaining_seconds"] = max(0., EVALUATION_CAP-record["evaluation_seconds"])
        record["rows"] = len(rows)
        write(out / "run.json", record)


if __name__ == "__main__":
    main()
