"""Prospective L1 image-DCT observability screen; development, USD 0, 600 s."""
from __future__ import annotations
import time
STARTED = time.monotonic()  # Includes all subsequent imports and setup.
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
CAP = 600.
VRAM = 10 * 1024**3
IDS = (1675, 468505)
FRACTIONS = (.25, .5, .75, 1.)
CONDITIONS = ("clean", "sd15_vae", "sdxl_vae")
ARMS = ("L", "P")
B = 10 ** (-36 / 20)


class BudgetStop(RuntimeError):
    pass


def guard(torch=None):
    if time.monotonic() - STARTED >= CAP:
        raise BudgetStop("600-second inclusive cap exhausted")
    if torch is not None and torch.cuda.is_available():
        if torch.cuda.max_memory_allocated() > VRAM:
            raise BudgetStop("10 GiB allocated-VRAM cap exceeded")


def native_projection(rgb, owner_id, profile):
    """Recompute all native normalisers/activity weights from this suspect."""
    from scripts import revised_watermark_v5 as v5
    luma = v5.luminance_from_rgb(rgb.tolist())
    checked, key, config = v5._resolve(profile, None)
    v5.base._check_image(luma, int(checked["minimum_side"]))
    owner = v5.canonical_owner(owner_id)
    carrier = v5._robust_carrier(key, config, owner, len(checked["robust_frequencies"]))
    return v5._Robust(v5._coarse(luma), luma, checked, carrier)


def frozen_projection(rgb, owner_id, profile, device="cpu"):
    """Differentiable P_x with native source-frozen slot weights and norms.

    Input is RGB [0,1], output native 320 chip units. 512->128 integer
    area averaging and row-major 8x8 blocks match the native implementation.
    Frozen quantities are used for direction construction only.
    """
    import torch
    import numpy as np
    from scripts import revised_watermark_v5 as v5
    if rgb.shape != (512, 512, 3):
        raise ValueError("Fixed 512-square source required")
    robust = native_projection(rgb, owner_id, profile)
    planes = torch.tensor([v5.base._plane(*uv) for uv in robust.positions],
                          dtype=torch.float32, device=device)
    factor = np.asarray(robust.slot_weights).reshape(256, -1)
    factor *= np.asarray(robust.weights)[None] / np.asarray(robust.normalisers)[:, None]
    factor *= np.asarray(robust.carrier[1]).reshape(256, -1)
    factors = torch.tensor(factor.reshape(-1), dtype=torch.float32, device=device)
    chips = torch.tensor(robust.carrier[0], dtype=torch.long, device=device)
    norms = torch.tensor(robust.norms, dtype=torch.float32, device=device)
    luma_weights = torch.tensor((.299, .587, .114), dtype=torch.float32, device=device)[None, :, None, None]

    def project(x):
        luma = (x * luma_weights).sum(1, keepdim=True) * 255.
        coarse = torch.nn.functional.avg_pool2d(luma, 4, 4)
        blocks = coarse.reshape(1, 1, 16, 8, 16, 8).permute(0, 1, 2, 4, 3, 5).reshape(256, 64)
        values = (blocks @ planes.T).reshape(-1) * factors
        return torch.zeros(320, device=x.device, dtype=x.dtype).scatter_add(0, chips, values) / norms

    return project, robust


def projection_parity(rgb, owner, profile):
    """Cheap CPU fp32 check; disagreement kills construction before GPU work."""
    import numpy as np
    import torch
    project, native = frozen_projection(rgb, owner, profile)
    x = torch.tensor(rgb.transpose(2, 0, 1).copy(), dtype=torch.float32)[None] / 255
    actual = project(x).detach().numpy()
    expected = np.asarray(native.projections)
    error = float(np.max(np.abs(actual - expected)))
    tolerance = 2e-4 + 2e-5 * float(np.max(np.abs(expected)))
    if error > tolerance:
        raise ValueError(f"Frozen fp32/native projection parity failed: {error} > {tolerance}")
    return dict(max_absolute_error=error, tolerance=tolerance, passed=True)


def detect_rgb(rgb, owner_id, profile, semantic_features):
    """Source-blind RC1; only robust provider replaced by native image DCT.

    No VAE, target q, source image, reference residual or writer amplitude is
    accessible here. h is not embedded, but RC1's suspect fragile observation
    and routing are retained to report any-tier negative calls honestly.
    """
    from scripts import journal_read_conditioning as rc
    v5, base = rc.v5, rc.base
    started = time.perf_counter()
    checked, key, config = v5._resolve(profile, None)
    luma = v5.luminance_from_rgb(rgb.tolist())
    height, width = base._check_image(luma, int(checked["minimum_side"]))
    owner = v5.canonical_owner(owner_id)
    decision = checked["decision"]
    target = float(decision["false_positive_target"])
    fragile = v5._Fragile(checked, key, config, owner, height, width)
    means, coefficients = base._analyse(luma, fragile.analysis)
    instance_projections = fragile.projections(coefficients)
    carrier = v5._robust_carrier(key, config, owner, len(checked["robust_frequencies"]))
    robust = v5._Robust(v5._coarse(luma), luma, checked, carrier)
    q_now = v5._semantic(means, checked, key, config, semantic_features, binding=False)
    h_now = base._perceptual_hash(means, coefficients, key, config)
    semantic_limits = (int(decision["semantic_radius"]), int(decision["semantic_mismatch_distance"]))
    instance_limits = (int(decision["instance_radius"]), int(decision["instance_mismatch_distance"]))
    semantic = v5._channel_result(v5._key_test(robust.projections, v5._semantic_table(owner, key, config), q_now), target, 1, q_now)
    if (abs(semantic["decoded_threshold"] - 8.259326826136963) > 1e-12 or
            abs(semantic["recomputed_threshold"] - 4.982033056390042) > 1e-12):
        raise ValueError("Frozen thresholds changed")
    s_found = bool(semantic["found"])
    s_status = soft_distance = None
    if s_found:
        s_status, soft_distance = rc._semantic_status(semantic, semantic_features, key, config, semantic_limits, True, "soft")
    q_bound = int(semantic["decoded_code"], 16) if semantic["read"] else q_now
    routing = "decoded_semantic_read" if semantic["read"] else "suspect_semantic_recomputed"
    table = v5._instance_table(owner, key, config)
    options = [table[j][v5._bit(q_bound, j)] for j in range(v5.CODE_BITS)]
    instance = v5._channel_result(v5._key_test(instance_projections, options, h_now), target, 1, h_now)
    i_found = bool(instance["found"])
    i_status = (max(base._content_status(instance["corrected_distance"], *instance_limits, True),
                    s_status if s_found else "unchecked", key=base._STATUS_RANK.get) if i_found else None)
    outcome, state = base._decide(s_found, s_status, i_found, i_status)
    semantic["soft_distance"] = soft_distance

    def public(result, status):
        return dict(result, content_status=status,
                    content_match=bool(result["found"] and base._STATUS_RANK[status] == 0))

    return dict(outcome=outcome, proposal_state=state, watermark_found=bool(s_found or i_found),
                semantic=public(semantic, s_status), instance=public(instance, i_status),
                semantic_code=f"{q_now:08x}", perceptual_hash=f"{h_now:08x}", binding_mode="combined",
                owner_id=owner.decode("utf-8"), owners_tested=1, binding="soft", method="L1-image-DCT",
                family="image-DCT-RC1", revision=1, detector_config_id=config.hex(),
                routing_revision=1, q_bound=f"{q_bound:08x}", routing=routing,
                instance_own_content_status=base._content_status(instance["corrected_distance"], *instance_limits, True) if i_found else None,
                side_information=["public OwnerID", "profile", "pinned seven-view CLIP weights"],
                fpr_fields_status="legacy_model_based_unvalidated_for_routed_system",
                seconds=time.perf_counter() - started)


def planned_inventory():
    plan = []
    for sid in IDS:
        plan.append(dict(id=f"direction-{sid}", phase="direction", source_id=sid))
        for condition in CONDITIONS:
            plan.append(dict(id=f"baseline-{sid}-{condition}", phase="baseline", source_id=sid, condition=condition, control="C0"))
        for arm in ARMS:
            for fraction in FRACTIONS:
                for condition in CONDITIONS:
                    plan.append(dict(id=f"screen-{sid}-{arm}-{fraction}-{condition}", phase="screen", source_id=sid,
                                     arm=arm, fraction=fraction, condition=condition, control="C1"))
            plan.append(dict(id=f"selection-{sid}-{arm}", phase="selection", source_id=sid, arm=arm))
        for strength in (.1, .2):
            for seed in range(3):
                identity = f"{sid}-{strength}-{seed}"
                plan.append(dict(id=f"T3-{identity}-C0", phase="T3", source_id=sid, strength=strength, seed=seed, control="C0"))
                for arm in ARMS:
                    plan.append(dict(id=f"T3-{identity}-{arm}", phase="T3", source_id=sid, strength=strength, seed=seed, arm=arm, control="C1"))
    return plan


def exact_checked(call, q):
    s = call["semantic"]
    return bool(s["read"] and s["found"] and s["content_match"] and int(s["decoded_code"], 16) == q)


def summarize(rows, selected):
    from f5_gate import OWNERS
    result = dict(selection={f"{sid}/{arm}": selected.get((sid, arm)) for sid in IDS for arm in ARMS},
                  scope="semantic-only intended-q payload screen; no embedded h or full-payload claim",
                  fpr_status="observed negatives only; population FPR not established")
    good = [r for r in rows if r["status"] == "ok"]
    t3 = [r for r in good if r["phase"] == "T3"]
    result["T3_exact_checked"] = {arm: sum(r["exact_checked_q"] for r in t3 if r.get("arm") == arm) for arm in ARMS}
    result["planned_T3_per_arm"] = 12
    result["C0_any"] = sum(bool(r["calls"][OWNERS[0]]["watermark_found"]) for r in good if r.get("control") == "C0")
    result["wrong_owner_any"] = sum(bool(r["calls"][OWNERS[1]]["watermark_found"]) for r in good if r.get("control") == "C1")
    result["completed_T3_C0"] = sum(r["control"] == "C0" for r in t3)
    result["status_counts"] = {s: sum(r["status"] == s for r in rows) for s in ("ok", "failed", "missing", "not_selected")}
    result["primary_success"] = (all(selected.get((sid, "L")) is not None for sid in IDS) and
                                 result["T3_exact_checked"]["L"] == 12 and result["completed_T3_C0"] == 12 and
                                 result["C0_any"] == 0 and result["wrong_owner_any"] == 0)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    images = args.output_dir / "images"
    images.mkdir()
    plan, rows, selected = planned_inventory(), [], {}
    lookup = {r["id"]: r for r in plan}
    record = dict(schema="journal-latent-tangent-probe-v1", method="L1-image-DCT", command=sys.argv,
                  commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  data_split="development-adaptive fixed sources", sources=list(IDS), seeds=[0, 1, 2], usd=0,
                  config=dict(fractions=list(FRACTIONS), arms=list(ARMS), conditions=list(CONDITIONS),
                              budget_rms=B, precision="fp32 posterior mode and unscaled decoder", latent_radius=[4, 32],
                              pilot_e=".001 max(norm(z),1)", seconds_cap=CAP, allocated_vram_cap_bytes=VRAM,
                              semantic_views=7, binding="soft", roster_size=1,
                              thresholds=[8.259326826136963, 4.982033056390042], h_embedded=False,
                              source_selection="1675 then previously observed continuity failure 468505",
                              protocol="research/journal-upgrade-20261009/representation-method-decision.md",
                              no_retry_no_rescaling=True, human_admissibility="missing"),
                  inventory=plan, outcome="running", rows=[])
    torch = None

    def save_record():
        record["rows"] = rows
        record["duration_seconds"] = time.monotonic() - STARTED
        (args.output_dir / "run.json").write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def emit(item, **fields):
        row = dict(lookup[item], **fields)
        row["elapsed_seconds"] = time.monotonic() - STARTED
        rows.append(row)
        with (args.output_dir / "rows.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, allow_nan=False) + "\n")
        print(json.dumps({k: row[k] for k in ("id", "status")}), flush=True)
        save_record()
        return row

    save_record()
    try:
        guard()
        import numpy as np
        import torch
        from PIL import Image
        from diffusers import AutoencoderKL
        from journal_vae_probe import Evaluator, SDXL, SDXL_REV
        from journal_readability_probe import payload, projection_stats
        from f4_transfer_probe import ASSETS, SOURCES
        from f5_gate import OWNERS
        from scripts import revised_watermark_v5 as v5
        from scripts.f5_latent_codec import dct_matrix
        import three_threat_models as models
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.cuda.set_per_process_memory_fraction(min(1., VRAM / torch.cuda.get_device_properties(0).total_memory))
        torch.cuda.reset_peak_memory_stats()
        models.block_network()
        guard(torch)
        ev = Evaluator()
        ev.lpips.to("cpu")
        guard(torch)
        other = AutoencoderKL.from_pretrained(SDXL, use_safetensors=True, local_files_only=True,
                                              torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
        record.update(profile=ev.profile, sdxl_revision=SDXL_REV,
                      detector_scope="native suspect image-DCT with RC1 channels; no VAE reader")
        vae = ev.reader.vae
        sources, targets, templates, baselines, marked = {}, {}, {}, {}, {}

        def save_rgb(name, rgb):
            guard(torch)
            path = images / f"{name}.png"
            Image.fromarray(np.asarray(rgb, np.uint8)).save(path)
            with Image.open(path) as im:
                saved = np.asarray(im.convert("RGB"), np.uint8).copy()
            return saved, str(path)

        def reconstruct(rgb, model):
            guard(torch)
            with torch.inference_mode():
                x = ev.reader.tensor(rgb.astype(np.float32) / 255)
                z = model.encode(x * 2 - 1).latent_dist.mode()
                y = model.decode(z).sample[0].permute(1, 2, 0).cpu().numpy()
            guard(torch)
            return np.rint(np.clip(y * .5 + .5, 0, 1) * 255).astype(np.uint8)

        def measure(rgb, sid, c1, condition):
            guard(torch)
            features = ev.features(rgb, 7)
            calls = {o: detect_rgb(rgb, o, ev.profile, features) for o in (OWNERS[:2] if c1 else OWNERS[:1])}
            result = dict(calls=calls, quality_source=ev.metrics(sources[sid], rgb))
            if c1:
                result["exact_checked_q"] = exact_checked(calls[OWNERS[0]], targets[sid])
                w, gaps = templates[sid]
                p = np.asarray(native_projection(rgb, OWNERS[0], ev.profile).projections)
                p0 = baselines[sid, condition]
                result["analysis_only"] = dict(projection_stats(p, w, gaps),
                    signed_chip_displacement=float(w @ (p-p0) / 320),
                    projection_displacement=(p-p0).tolist(), intended_q=f"{targets[sid]:08x}")
            guard(torch)
            return result

        # Entire clean/VAE screen is completed and selections frozen before any T3.
        for sid in IDS:
            try:
                guard(torch)
                with Image.open(SOURCES[sid]) as im:
                    source = np.asarray(im.convert("RGB"), np.uint8).copy()
                sources[sid] = source
                parity = projection_parity(source, OWNERS[0], ev.profile)
                _, q, _, payload_record = payload(ev, sid)  # Intended q only enters construction/analysis.
                targets[sid] = q
                checked, key, config = v5._resolve(ev.profile, None)
                table = np.asarray(v5._semantic_table(v5.canonical_owner(OWNERS[0]), key, config))
                bits = np.array([v5._bit(q, j) for j in range(32)])
                w = table[np.arange(32), bits].reshape(-1)
                gaps = table[np.arange(32), bits] - table[np.arange(32), 1-bits]
                templates[sid] = w, gaps
                for condition in CONDITIONS:
                    guard(torch)
                    rgb = source if condition == "clean" else reconstruct(source, vae if condition == "sd15_vae" else other)
                    rgb, path = save_rgb(f"baseline-{sid}-{condition}", rgb)
                    baselines[sid, condition] = np.asarray(native_projection(rgb, OWNERS[0], ev.profile).projections)
                    emit(f"baseline-{sid}-{condition}", status="ok", image=path, **measure(rgb, sid, False, condition))
                project, _ = frozen_projection(source, OWNERS[0], ev.profile, "cuda")
                x = ev.reader.tensor(source.astype(np.float32) / 255)
                with torch.no_grad():
                    z = vae.encode(x * 2 - 1).latent_dist.mode()
                    d0 = vae.decode(z).sample * .5 + .5
                px = x.detach().requires_grad_(True)
                tw = torch.tensor(w, device="cuda", dtype=torch.float32)
                a = torch.autograd.grad(tw @ project(px), px)[0].detach()
                zz = z.detach().requires_grad_(True)
                decoded = vae.decode(zz).sample * .5 + .5
                g = torch.autograd.grad(tw @ project(x + decoded - decoded.detach()), zz)[0].detach()
                del zz, decoded, px
                c = torch.tensor(dct_matrix(64), device="cuda", dtype=torch.float32)
                uv = torch.arange(64, device="cuda", dtype=torch.float32)
                radius = torch.sqrt(uv[:, None]**2 + uv[None, :]**2)
                g = c.T @ ((c @ g @ c.T) * ((radius >= 4) & (radius <= 32))) @ c
                gn, ar = float(g.norm()), float(a.square().mean().sqrt())
                if not math.isfinite(gn) or gn == 0 or not math.isfinite(ar) or ar == 0:
                    raise ValueError("Zero/nonfinite projected direction")
                g /= gn
                e = .001 * max(float(z.norm()), 1.)
                with torch.no_grad():
                    residual = vae.decode(z + e*g).sample * .5 + .5 - d0
                rr = float(residual.square().mean().sqrt())
                if not math.isfinite(rr) or rr == 0:
                    raise ValueError("Zero/nonfinite pilot RMS")
                t = e * B / rr
                if not math.isfinite(t):
                    raise ValueError("Nonfinite pilot-derived step")
                guard(torch)
                emit(f"direction-{sid}", status="ok", parity=parity, intended_q=f"{q:08x}",
                     q_origin=payload_record["q_target_basis"], latent_norm=float(z.norm()),
                     projected_gradient_norm=gn, pixel_gradient_rms=ar, pilot_e=e, pilot_rms=rr, step_t=t)
                for arm in ARMS:
                    for fraction in FRACTIONS:
                        guard(torch)
                        with torch.no_grad():
                            y = x + (vae.decode(z + fraction*t*g).sample * .5 + .5 - d0) if arm == "L" else x + fraction*B*a/ar
                            rgb = np.rint(np.clip(y[0].permute(1, 2, 0).cpu().numpy(), 0, 1)*255).astype(np.uint8)
                        del y
                        for condition in CONDITIONS:
                            item = f"screen-{sid}-{arm}-{fraction}-{condition}"
                            tick = time.monotonic()
                            try:
                                guard(torch)
                                suspect = rgb if condition == "clean" else reconstruct(rgb, vae if condition == "sd15_vae" else other)
                                suspect, path = save_rgb(item, suspect)
                                fields = measure(suspect, sid, True, condition)
                                if condition == "clean":
                                    marked[sid, arm, fraction] = suspect
                                emit(item, status="ok", image=path, duration_seconds=time.monotonic()-tick, **fields)
                            except BudgetStop:
                                raise
                            except torch.OutOfMemoryError:
                                raise
                            except Exception:
                                emit(item, status="failed", error=traceback.format_exc(), duration_seconds=time.monotonic()-tick)
                del x, z, d0, a, g, residual, project
                torch.cuda.empty_cache()
            except (BudgetStop, torch.OutOfMemoryError):
                raise
            except Exception:
                error = traceback.format_exc()
                done = {r["id"] for r in rows}
                if f"direction-{sid}" not in done:
                    emit(f"direction-{sid}", status="failed", error=error)
                for item in plan:
                    if item["source_id"] == sid and item["phase"] in ("baseline", "screen") and item["id"] not in done:
                        emit(item["id"], status="missing", error="Source construction failed; " + error)
                torch.cuda.empty_cache()
        by_id = {r["id"]: r for r in rows}
        for sid in IDS:
            for arm in ARMS:
                eligible = []
                for fraction in FRACTIONS:
                    group = [by_id.get(f"screen-{sid}-{arm}-{fraction}-{condition}", {}) for condition in CONDITIONS]
                    if all(r.get("status") == "ok" and r.get("exact_checked_q") for r in group):
                        quality = group[0]["quality_source"]
                        if quality["psnr_db"] > 35 and quality["ssim_rgb"] > .9 and quality["lpips"] < .1:
                            eligible.append(fraction)
                selected[sid, arm] = min(eligible) if eligible else None
                emit(f"selection-{sid}-{arm}", status="ok", qualifying_fractions=eligible,
                     selected_fraction=selected[sid, arm], screen_pass=bool(eligible), selection_before_any_T3=True)
        record["frozen_selection"] = {f"{s}/{a}": f for (s, a), f in selected.items()}
        save_record()
        # Release both writer VAEs before loading the official fp16 regenerator.
        ev.reader.vae.to("cpu")
        other.to("cpu")
        del vae, other
        torch.cuda.empty_cache()
        pipe = None
        if any(f is not None for f in selected.values()):
            guard(torch)
            pipe = models.load_regenerator(ASSETS)
            guard(torch)
        for item in (r for r in plan if r["phase"] == "T3"):
            sid = item["source_id"]
            arm = item.get("arm")
            eligible = selected.get((sid, arm)) if arm else any(selected.get((sid, a)) is not None for a in ARMS)
            if eligible is None or eligible is False:
                emit(item["id"], status="not_selected", error="No qualifying image; planned denominator retained")
                continue
            tick = time.monotonic()
            try:
                guard(torch)
                rgb = sources[sid] if arm is None else marked[sid, arm, selected[sid, arm]]
                kwargs = models.regeneration_kwargs(item["strength"], item["seed"], Image.fromarray(rgb), torch.Generator)
                with torch.inference_mode():
                    result = pipe(**kwargs)
                guard(torch)
                generated = models.validate_generated(result)
                suspect, path = save_rgb(item["id"], np.asarray(generated, np.uint8))
                # T3 diagnostics compare to clean C0 projections without cancelling them in detection.
                fields = measure(suspect, sid, arm is not None, "clean")
                emit(item["id"], status="ok", image=path, selected_fraction=selected.get((sid, arm)),
                     duration_seconds=time.monotonic()-tick, safety_checker_passed=True, **fields)
            except (BudgetStop, torch.OutOfMemoryError):
                raise
            except Exception:
                emit(item["id"], status="failed", error=traceback.format_exc(), duration_seconds=time.monotonic()-tick)
        record["outcome"] = "completed" if all(r["status"] in ("ok", "not_selected") for r in rows) else "completed_with_failures"
    except Exception:
        record.update(outcome="failed", error=traceback.format_exc())
    finally:
        done = {r["id"] for r in rows}
        for item in plan:
            if item["id"] not in done:
                emit(item["id"], status="missing", error="Not reached; inclusive budget/setup/fatal failure. See run.json")
        record["budget_overrun"] = time.monotonic()-STARTED > CAP
        if torch is not None and torch.cuda.is_available():
            record["gpu_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
            record["gpu_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        try:
            record["summary"] = summarize(rows, selected)
            if record["budget_overrun"] or record.get("gpu_peak_allocated_bytes", 0) > VRAM:
                record["summary"]["primary_success"] = False
                record["outcome"] = "failed_budget"
            (args.output_dir/"summary.json").write_text(json.dumps(record["summary"], indent=2, allow_nan=False)+"\n", encoding="utf-8")
        except Exception:
            record["summary_error"] = traceback.format_exc()
        record["full_inventory"] = [dict(item, status=next(r["status"] for r in rows if r["id"] == item["id"])) for item in plan]
        record["failed_or_missing"] = [r["id"] for r in rows if r["status"] in ("failed", "missing")]
        save_record()
    return 0 if record["outcome"].startswith("completed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
