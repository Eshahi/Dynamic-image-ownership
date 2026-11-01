"""Q-RES: frozen crossed-resolution diagnostic; no science imports before --execute.

The default --execute phase is the included 24-image pilot. A later invocation
with --continue-after-pilot is an explicit continuation under the supplied actual
paid ceiling. This file neither provisions a server nor downloads assets.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

METHODS = ("f5-r2", "v5-r3", "vine-r")
ARMS = (*METHODS, "unmarked")
CELLS = (("sd15-1024", "R0", 1024), ("sdxl-512", "R1", 512))
NATIVE = (("sd15-512", "R0", 512), ("sdxl-1024", "R1", 1024))
METRICS = ("C", "J", "A", "sf", "sc", "sr", "if", "ic", "io", "ir", "H", "O", "O_U", "O_Q",
           "Bs", "Bi", "B", "C_or_B", "presence")
TERMINAL = {"ok", "error", "safety_blocked", "interrupted", "input_missing"}


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def units(sources=None, cells=CELLS):
    """Source-major ordering guarantees that the first source is the full pilot."""
    for source in common.S60 if sources is None else sources:
        for cell, channel, size in cells:
            for arm in ARMS:
                for seed in common.SEEDS:
                    yield dict(id=f"{cell}:{source}:{arm}:0.2:{seed}", source_id=source,
                               split=common.split(source), cell=cell, channel=channel,
                               resolution=size, arm=arm, strength=.2, seed=seed,
                               control="C0" if arm == "unmarked" else "C1")


def call_slots(unit):
    methods = METHODS if unit["arm"] == "unmarked" else (unit["arm"],)
    owners = (common.ALPHA,) if unit["control"] == "C0" else (common.ALPHA, common.BETA)
    return [(method, owner) for method in methods for owner in owners]


def plan():
    inventory = list(units())
    scenarios = {}
    for label, sd15, sdxl in (("unscaled_anchors", .54, 1.24),
                             ("area_scaled_assumption", 2.16, .31),
                             ("doubled_area_scaled_regeneration", 4.32, .62)):
        generation = 720 * (sd15 + sdxl)
        total = generation + 3240 * 1.5
        scenarios[label] = dict(regeneration_seconds=generation, reader_seconds=4860.,
                                total_seconds=total, hours=total / 3600,
                                historical_usd_at_0_551=total / 3600 * .551,
                                measured_resolution_latencies=False)
    return dict(queue="Q-RES", schema="q-res-v1", sources=list(common.S60),
                split={s: [x for x in common.S60 if common.split(x) == s]
                       for s in ("DESIGN", "EVALUATE")},
                seeds=list(common.SEEDS), arms=list(ARMS),
                images=len(inventory), marked_images=1080, c0_images=360,
                reader_calls=sum(len(call_slots(u)) for u in inventory),
                marked_correct_calls=1080, marked_wrong_calls=1080, c0_calls=1080,
                native_baseline_images_reused=1440, new_marks=0,
                pilot=dict(source=common.S60[0], images=24, reader_calls=54,
                           included_in_total=True, continuation_flag="--continue-after-pilot"),
                units=inventory, scenarios=scenarios,
                resize="LANCZOS in/out; canonical RGB8 512 reader input",
                sdxl_conditioning=dict(original_size=[1024, 1024], target_size=[1024, 1024],
                                       crops_coords_top_left=[0, 0]),
                fixed_scale_kill="EVALUATE F5 second-found SD15 gain >=6/30 AND SDXL loss >=6/30; otherwise kill strong scale explanation",
                aggregation="2 of 3 fixed seeds; missing fails; missing-as-success upper separate",
                overhead="Setup, quality, retrieval and I/O unmeasured; scenarios are not paid ceilings",
                limits="Exploratory development diagnostic. No safety/efficacy promotion or encoder-only attribution. B remains failed and diagnostic.")


def call_metrics(row, method, owner):
    """All missing calls stay unknown; VINE has no semantic/instance endpoints."""
    call = (row or {}).get("detections", {}).get(method, {}).get(owner)
    if method == "vine-r" and owner == common.BETA and not call:
        alpha = (row or {}).get("detections", {}).get(method, {}).get(common.ALPHA, {})
        if alpha.get("status") == "ok" and "wrong_message_presence" in alpha:
            call = dict(status="ok", presence=alpha["wrong_message_presence"],
                        basis="saved native decoded bits; no extra physical baseline read")
    if not call or call.get("status") != "ok":
        return {k: None for k in METRICS}
    if method == "vine-r":
        return {k: call.get("presence", {}).get("present") if k == "presence" else None
                for k in METRICS}
    raw = call.get("raw", {})
    fields = common.reader_fields(raw, call.get("endpoints", {}))
    fields.update(sc=bool(raw.get("semantic", {}).get("content_match")),
                  sr=bool(raw.get("semantic", {}).get("read")),
                  ir=bool(raw.get("instance", {}).get("read")),
                  ic=bool(raw.get("instance", {}).get("content_match")),
                  A=bool(raw.get("semantic", {}).get("found") or raw.get("instance", {}).get("found")),
                  presence=None)
    return {k: fields.get(k) for k in METRICS}


def majority(values):
    if len(values) != 3 or any(v is not None and type(v) is not bool for v in values):
        raise ValueError("Three boolean/unknown seed outcomes required")
    positive = sum(v is True for v in values)
    missing = sum(v is None for v in values)
    return dict(success=positive >= 2, upper=positive + missing >= 2,
                positive_calls=positive, missing_calls=missing)


def distribution(values):
    values = sorted(float(v) for v in values if isinstance(v, (float, int))
                    and not isinstance(v, bool) and math.isfinite(v))
    if not values:
        return dict(n=0, min=None, q25=None, median=None, q75=None, p95=None, max=None)
    def quantile(p):
        pos = p * (len(values) - 1)
        low = int(pos)
        return values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (pos - low)
    return dict(n=len(values), min=values[0], q25=quantile(.25), median=quantile(.5),
                q75=quantile(.75), p95=quantile(.95), max=values[-1])


def native_inventory(rows):
    """Reuse only named original cells, retaining missing/error/safety-blocked rows."""
    selected = {}
    for unit in units(cells=NATIVE):
        rid = f'{unit["channel"]}:{unit["source_id"]}:{unit["arm"]}:0.2:{unit["seed"]}'
        original = rows.get(rid)
        if original is not None:
            if original.get("id") != rid or any(original.get(k) != unit[k]
                    for k in ("source_id", "channel", "arm", "strength", "seed", "control")):
                raise ValueError(f"Native baseline row identities disagree: {rid}")
            selected[unit["id"]] = {**copy.deepcopy(original), **unit,
                                    "native_row_id": rid, "native_reused": True}
    return selected


def scale_decision(sd15_native, sd15_crossed, sdxl_native, sdxl_crossed, complete=True):
    if any(type(value) is not int or not 0 <= value <= 30
           for value in (sd15_native, sd15_crossed, sdxl_native, sdxl_crossed)):
        raise ValueError("Four EVALUATE source counts /30 required")
    gain, loss = sd15_crossed - sd15_native, sdxl_native - sdxl_crossed
    verdict = "SURVIVES_STRONG_SCALE_KILL" if gain >= 6 and loss >= 6 else "KILL_STRONG_SCALE_EXPLANATION"
    return dict(sd15_gain=gain, sdxl_loss=loss, verdict=verdict if complete else "PENDING_FIXED_INVENTORY")


def analyze(rows, native=None, clean=None):
    all_rows = {**(native or {}), **rows}
    source_results, negatives, quality = [], [], []
    for cell, channel, size in (*NATIVE, *CELLS):
        for method in METHODS:
            keys = ("presence",) if method == "vine-r" else tuple(k for k in METRICS if k != "presence")
            for split in ("DESIGN", "EVALUATE"):
                ids = [x for x in common.S60 if common.split(x) == split]
                for key in keys:
                    per_source = []
                    for source in ids:
                        values = [call_metrics(all_rows.get(f"{cell}:{source}:{method}:0.2:{seed}"),
                                               method, common.ALPHA)[key] for seed in common.SEEDS]
                        per_source.append(dict(source=source, seeds=dict(zip(map(str, common.SEEDS), values)),
                                               **majority(values)))
                    source_results.append(dict(cell=cell, method=method, split=split, endpoint=key,
                                               n=len(ids), success=sum(x["success"] for x in per_source),
                                               upper=sum(x["upper"] for x in per_source), sources=per_source))
                for role, arm, owner in (("C0", "unmarked", common.ALPHA),
                                         ("wrong_owner", method, common.BETA)):
                    for key in keys:
                        values = [call_metrics(all_rows.get(f"{cell}:{s}:{arm}:0.2:{seed}"),
                                               method, owner)[key] for s in ids for seed in common.SEEDS]
                        negatives.append(dict(cell=cell, method=method, split=split, role=role,
                                              endpoint=key, calls=len(values), positives=sum(v is True for v in values),
                                              missing=sum(v is None for v in values),
                                              upper=sum(v is not False for v in values)))
        for arm in ARMS:
            for split in ("DESIGN", "EVALUATE"):
                items = [all_rows.get(u["id"], {}) for u in units(cells=((cell, channel, size),))
                         if u["arm"] == arm and u["split"] == split]
                quality.append(dict(cell=cell, arm=arm, split=split, planned=len(items),
                    generation_status=dict(Counter(r.get("status", "missing") for r in items)),
                    attack={key: distribution(r.get("distortion", {}).get(key) for r in items)
                            for key in ("psnr_db", "ssim_rgb", "lpips")},
                    total={key: distribution(r.get("total_distortion", {}).get(key) for r in items)
                           for key in ("psnr_db", "ssim_rgb", "lpips")},
                    attack_psnr_infinite=sum(r.get("distortion", {}).get("psnr_infinite") is True for r in items),
                    total_psnr_infinite=sum(r.get("total_distortion", {}).get("psnr_infinite") is True for r in items),
                    attack_quality_missing=sum(r.get("distortion", {}).get("status") != "ok" for r in items),
                    total_quality_missing=sum(r.get("total_distortion", {}).get("status") != "ok" for r in items)))
    endpoint = {(r["cell"], r["method"], r["split"], r["endpoint"]): r for r in source_results}
    def f5(cell):
        return endpoint[(cell, "f5-r2", "EVALUATE", "if")]
    complete = all(rows.get(u["id"], {}).get("final") is True for u in units())
    decision = scale_decision(f5("sd15-512")["success"], f5("sd15-1024")["success"],
                              f5("sdxl-1024")["success"], f5("sdxl-512")["success"], complete)
    return dict(schema="q-res-analysis-v1", source_majorities=source_results,
                negative_calls=negatives, quality_distributions=quality,
                clean_quality=[dict(source=s, arm=a, strict_quality=r.get("strict_quality"),
                                    distortion=r.get("distortion"), retained_without_filtering=True)
                               for (s, a), r in sorted((clean or {}).items())],
                scale=dict(endpoint="frozen instance.found", split="EVALUATE", denominator=30,
                           **decision, required_each=6,
                           sd15_gain_missing_bounds=[f5("sd15-1024")["success"]-f5("sd15-512")["upper"],
                                                     f5("sd15-1024")["upper"]-f5("sd15-512")["success"]],
                           sdxl_loss_missing_bounds=[f5("sdxl-1024")["success"]-f5("sdxl-512")["upper"],
                                                     f5("sdxl-1024")["upper"]-f5("sdxl-512")["success"]],
                           complete=complete),
                vine_endpoints="Native 100-bit presence only; C/J/found/content/exact-h/O/Bs/Bi/B N/A",
                endpoint_names=dict(sf="robust found", sc="robust content_match", sr="robust read",
                                    **{"if": "second found"}, ic="second content_match", io="second found AND content_match",
                                    ir="second read", H="exact h against retained clean target", A="either native tier found"),
                interpretation="Exploratory. B failed previously and is diagnostic only. No safety/efficacy claim; no encoder-only attribution.",
                human_visibility="MISSING")


class Journal:
    def __init__(self, path, expected, inputs):
        self.path = Path(path)
        self.latest = common.journal_rows(self.path) if self.path.exists() else {}
        for rid, row in self.latest.items():
            if rid not in expected or any(row.get(k) != v for k, v in expected[rid].items()):
                raise ValueError(f"Unknown or changed Q-RES unit: {rid}")
            source, arm = row["source_id"], row["arm"]
            if row.get("input_sha256") != inputs[(source, arm)]["output"]["sha256"]:
                raise ValueError(f"Changed clean input: {rid}")
            if row.get("payload") != inputs[(source, arm)].get("payload"):
                raise ValueError(f"Changed payload: {rid}")
            if row.get("status") not in TERMINAL | {"generated", "running"}:
                raise ValueError(f"Unknown generation status: {rid}")
            if row.get("output"):
                output = Path(row["output"]["path"]).resolve()
                if not output.is_relative_to(self.path.parent.resolve()) or common.digest(output) != row["output"]["sha256"]:
                    raise ValueError(f"Changed/escaped output: {rid}")
            allowed = set(call_slots(row))
            if any((m, o) not in allowed for m, calls in row.get("detections", {}).items() for o in calls):
                raise ValueError(f"Unknown call slot: {rid}")
            if any(c.get("status") not in TERMINAL | {"running"}
                   for calls in row.get("detections", {}).values() for c in calls.values()):
                raise ValueError(f"Unknown reader status: {rid}")
            if row.get("final") and any(o not in row.get("detections", {}).get(m, {}) for m, o in allowed):
                raise ValueError(f"Final row has omitted call slots: {rid}")
            if row.get("final") and (row.get("status") == "running" or
                    any(c.get("status") == "running" for calls in row.get("detections", {}).values()
                        for c in calls.values()) or row.get("distortion", {}).get("status") == "running"):
                raise ValueError(f"Final row contains a nonfinal attempt: {rid}")

    def append(self, row):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.latest[row["id"]] = copy.deepcopy(row)


def error_record(exc):
    return dict(status="safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error",
                error=traceback.format_exc())


def validate_sd15(result, size):
    """Historical safety checks, with the declared working geometry as sole change."""
    if len(result.images) != 1 or result.nsfw_content_detected is None or len(result.nsfw_content_detected) != 1:
        raise RuntimeError("generation/safety result incomplete")
    flag = result.nsfw_content_detected[0]
    if type(flag) is not bool:
        raise RuntimeError("malformed safety verdict")
    if flag:
        raise RuntimeError("safety_checker_blocked_output")
    image = result.images[0]
    if image.mode != "RGB" or image.size != (size, size):
        raise RuntimeError("generated image differs from declared working geometry")
    return image


def regenerate(generator, rgb, strength, seed, size):
    if generator.spec["family"] != "sd15":
        # The existing SDXL adapter retains its fixed 1024 conditioning verbatim.
        return generator(rgb, strength, seed)
    # Regenerator.__call__ routes SD15 through a 512-only validator. Preserve the
    # pipeline/scheduler/safety policy while allowing this preregistered 1024 cell.
    import numpy as np
    from PIL import Image
    torch, spec = generator.torch, generator.spec
    rng = torch.Generator(device="cuda").manual_seed(seed)
    with torch.inference_mode():
        result = generator.pipe(prompt=spec["prompt"], image=Image.fromarray(rgb),
                                strength=strength, num_inference_steps=spec["steps"],
                                guidance_scale=spec["guidance_scale"], generator=rng,
                                output_type="pil", return_dict=True, negative_prompt="", eta=0.)
    return np.asarray(validate_sd15(result, size), dtype=np.uint8).copy()


def interrupted(row):
    """An interrupted started attempt is a failure, never an automatic retry."""
    row = copy.deepcopy(row)
    changed = False
    if row.get("status") == "running":
        row.update(status="interrupted", error="Generation interrupted after attempt was journaled")
        changed = True
    for calls in row.get("detections", {}).values():
        for call in calls.values():
            if call.get("status") == "running":
                call.update(status="interrupted", error="Reader attempt interrupted; not replayed")
                changed = True
    if row.get("distortion", {}).get("status") == "running":
        row["distortion"] = dict(status="interrupted", error="Quality attempt interrupted; not replayed")
        changed = True
    return row, changed


def finalize(row):
    """Fill unavailable calls explicitly, including blocked generation attempts."""
    row = copy.deepcopy(row)
    for method, owner in call_slots(row):
        calls = row.setdefault("detections", {}).setdefault(method, {})
        if owner not in calls:
            calls[owner] = dict(status="input_missing", error="No successful generated input")
    row.setdefault("distortion", dict(status="input_missing"))
    row.setdefault("total_distortion", dict(status="input_missing"))
    row["final"] = True
    return row


def pilot_timing(rows):
    items = [rows.get(u["id"], {}) for u in units((common.S60[0],))]
    generation = {cell: distribution(r.get("generation_seconds") for r in items if r.get("cell") == cell)
                  for cell, _, _ in CELLS}
    successful = {cell: [r["generation_seconds"] for r in items if r.get("cell") == cell and r.get("output")]
                  for cell, _, _ in CELLS}
    method_seconds = {method: [r["detection_seconds"][method] / len(r["detections"][method]) for r in items
                              if method in r.get("detection_seconds", {})
                              and r.get("detections", {}).get(method)
                              and all(c.get("status") == "ok" for c in r["detections"][method].values())]
                      for method in METHODS}
    quality_seconds = [r["metrics_seconds"] for r in items if r.get("distortion", {}).get("status") == "ok"
                       and r.get("total_distortion", {}).get("status") == "ok"]
    ready = bool(quality_seconds) and all(successful.values()) and all(method_seconds.values()) and all(r.get("final") for r in items)
    projection = None
    if ready:
        # Scale measured whole-source work; include observed loading/setup overhead separately.
        generation_seconds = sum(720 * statistics.mean(v) for v in successful.values())
        # Allocate the full remaining call/quality inventory even if a pilot image
        # was blocked; failure-induced skipped work must not make the forecast cheap.
        read_seconds = sum(1080 * statistics.mean(v) for v in method_seconds.values())
        metric_seconds = 1440 * statistics.mean(quality_seconds)
        projection = dict(generation_seconds=generation_seconds, reader_seconds=read_seconds,
                          quality_seconds=metric_seconds,
                          total_work_seconds=generation_seconds + read_seconds + metric_seconds,
                          caveat="Single-source measured projection; setup/retrieval overhead and source variability remain")
    return dict(source=common.S60[0], included_images=24, included_reader_slots=54,
                complete=all(r.get("final") for r in items), estimable=ready,
                generation_seconds=generation, measured_projection=projection,
                missing_call_slots=sum(call.get("status") != "ok" for r in items
                                       for calls in r.get("detections", {}).values() for call in calls.values()))


def execute(args):
    config, budget = common.execution_context(args, "Q-RES")
    out, assets = Path(args.out).resolve(), Path(args.assets).resolve()
    clean = common.clean_inputs(args.stage2a, args.stage2b, common.S60, ARMS)
    native = native_inventory(common.native_rows(args.stage2a, args.stage2b))
    manifest = dict(schema="q-res-manifest-v1", plan=plan(), config=config,
                    provenance=common.provenance("Q-RES"),
                    inputs=[dict(source=s, arm=a, row_id=r["id"], sha256=r["output"]["sha256"],
                                 payload=r.get("payload"), strict_quality=r.get("strict_quality"))
                            for (s, a), r in sorted(clean.items())],
                    native_sha256=canonical(native), assets=str(assets))
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        if common.read(manifest_path) != manifest:
            raise ValueError("Resume manifest changed: parameters, provenance, assets or saved inputs differ")
    else:
        if out.exists() and any(out.iterdir()):
            raise ValueError("Nonempty output without Q-RES manifest refused")
        common.write(manifest_path, manifest)
        common.write(out / "native-baseline-rows.json", native)
    journal = Journal(out / "journal.jsonl", {u["id"]: u for u in units()}, clean)
    for row in list(journal.latest.values()):
        recovered, changed = interrupted(row)
        if changed:
            journal.append(recovered)
    # Actual budget arguments are receipts of explicit invocations, never protocol defaults.
    with (out / "execution-invocations.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(time_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    continuation=args.continue_after_pilot, budget=budget.record())) + "\n")
    pilot_before = pilot_timing(journal.latest)
    if args.continue_after_pilot:
        if not pilot_before["complete"] or not pilot_before["estimable"]:
            raise ValueError("Complete estimable retained pilot required before explicit continuation")
        remaining = pilot_before["measured_projection"]["total_work_seconds"] * 59 / 60
        budget.check(reserve=remaining)
    selected = list(units() if args.continue_after_pilot else units((common.S60[0],)))
    # Only this explicit execution path imports scientific adapters.
    sys.path[:0] = [str(common.ROOT), str(common.ROOT / "scripts")]
    import encoder_transfer_runtime as rt
    from encoder_transfer_test import message

    for source in common.S60:
        if clean[(source, "vine-r")].get("payload", {}).get("bits") != message(source, 100, config["message_seed"]):
            raise ValueError(f"Saved VINE payload differs from frozen 100-bit message: {source}")

    started = time.monotonic()
    phase_timings = {}
    for cell, channel, size in CELLS:
        pending = [u for u in selected if u["cell"] == cell and u["id"] not in journal.latest]
        if not pending:
            continue
        budget.check()
        tick = time.monotonic()
        spec = copy.deepcopy(next(s for s in config["channels"] if s["id"] == channel))
        spec["resolution"] = size
        generator = rt.Regenerator(assets, spec)
        phase_timings["load_" + cell] = time.monotonic() - tick
        try:
            for unit in pending:
                budget.check()
                dependency = clean[(unit["source_id"], unit["arm"])]
                row = {**unit, "status": "running", "input_sha256": dependency["output"]["sha256"],
                       "input_row_id": dependency["id"], "payload": dependency.get("payload")}
                journal.append(row)
                tick = time.monotonic()
                try:
                    rt.seed_everything(config["implementation_seed"])
                    rgb = rt.load_rgb(dependency["local_path"])
                    if size != 512:
                        rgb = rt.resize_rgb(rgb, size)
                    rgb = regenerate(generator, rgb, .2, unit["seed"], size)
                    if tuple(rgb.shape[:2]) != (size, size):
                        raise ValueError("Generator returned unexpected working resolution")
                    if size != 512:
                        rgb = rt.resize_rgb(rgb, 512)
                    output = out / "images" / (unit["id"].replace(":", "_") + ".png")
                    row.update(status="generated", output=rt.save_rgb(output, rgb))
                except Exception as exc:
                    row.update(error_record(exc))
                row["generation_seconds"] = time.monotonic() - tick
                journal.append(row)
        finally:
            del generator
            rt.release()
    for method in METHODS:
        pending = [u for u in selected if journal.latest.get(u["id"], {}).get("output")
                   and method in {m for m, _ in call_slots(u)}
                   and method not in journal.latest[u["id"]].get("detections", {})]
        if not pending:
            continue
        budget.check()
        tick = time.monotonic()
        adapter = rt.Vine(assets, encoding=False) if method == "vine-r" else rt.Internal(assets, config)
        phase_timings["load_reader_" + method] = time.monotonic() - tick
        try:
            for unit in pending:
                budget.check()
                row = copy.deepcopy(journal.latest[unit["id"]])
                owners = [owner for m, owner in call_slots(unit) if m == method]
                row.setdefault("detections", {})[method] = {o: dict(status="running") for o in owners}
                journal.append(row)
                tick = time.monotonic()
                try:
                    rgb = rt.load_rgb(row["output"]["path"])
                    if method == "vine-r":
                        # Two actual marked-image reads; each tests its fixed public message.
                        for owner in owners:
                            call_tick = time.monotonic()
                            try:
                                seed = config["message_seed" if owner == common.ALPHA else "wrong_message_seed"]
                                call = adapter.detect(rgb, message(unit["source_id"], 100, seed))
                                call.update(seconds=time.monotonic() - call_tick, expected_message_seed=seed)
                            except Exception as exc:
                                call = {**error_record(exc), "seconds": time.monotonic() - call_tick}
                            row["detections"][method][owner] = call
                            journal.append(row)
                    else:
                        row["detections"][method] = adapter.detect(rgb, method, row.get("payload"), unit["control"])
                        if set(row["detections"][method]) != set(owners):
                            raise ValueError("Frozen reader owner-call inventory mismatch")
                except Exception as exc:
                    for owner in owners:
                        if row["detections"][method].get(owner, {}).get("status") == "running":
                            row["detections"][method][owner] = error_record(exc)
                row.setdefault("detection_seconds", {})[method] = time.monotonic() - tick
                journal.append(row)
        finally:
            del adapter
            rt.release()
    pending = [u for u in selected if journal.latest.get(u["id"], {}).get("output")
               and "distortion" not in journal.latest[u["id"]]]
    if pending:
        # The existing quality routine uses the frozen CPU LPIPS weights; no new marks.
        import importlib.metadata
        import three_threat_models as models
        from m1_latent_reconstruction import quality
        budget.check()
        tick = time.monotonic()
        lpips = models.load_lpips(assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
        phase_timings["load_quality"] = time.monotonic() - tick
        for unit in pending:
            budget.check()
            row = copy.deepcopy(journal.latest[unit["id"]])
            row["distortion"] = dict(status="running")
            journal.append(row)
            tick = time.monotonic()
            try:
                rgb = rt.load_rgb(row["output"]["path"])
                dependency = clean[(unit["source_id"], unit["arm"])]
                source = clean[(unit["source_id"], "unmarked")]
                for field, reference in (("distortion", dependency), ("total_distortion", source)):
                    original = rt.load_rgb(reference["local_path"])
                    row[field] = dict(status="ok", reference_sha256=reference["output"]["sha256"],
                                      **quality(original, rgb), lpips=models.lpips_score(lpips, original, rgb))
            except Exception as exc:
                row["distortion"] = error_record(exc)
            row["metrics_seconds"] = time.monotonic() - tick
            row["status"] = "ok"
            journal.append(row)
        del lpips
        rt.release()
    for unit in selected:
        row = journal.latest.get(unit["id"])
        if row is not None and not row.get("final"):
            journal.append(finalize(row))
    pilot = pilot_timing(journal.latest)
    pilot.update(invocation_seconds=time.monotonic() - started, phase_load_seconds=phase_timings,
                 actual_budget=budget.record(), continuation_executed=args.continue_after_pilot)
    common.write(out / ("continuation-timing.json" if args.continue_after_pilot else "pilot.json"), pilot)
    summary = analyze(journal.latest, native, clean)
    summary.update(actual_budget=budget.record(), attempted_images=len(journal.latest),
                   generated_images=sum(bool(r.get("output")) for r in journal.latest.values()),
                   reader_slot_status=dict(Counter(c.get("status", "missing") for r in journal.latest.values()
                                                   for calls in r.get("detections", {}).values() for c in calls.values())))
    common.write(out / "summary.json", summary)
    return dict(output=str(out), final_units=sum(r.get("final") is True for r in journal.latest.values()),
                pilot=pilot, scale=summary["scale"])


def self_test():
    from types import SimpleNamespace
    from unittest.mock import patch
    p = plan()
    assert len(p["units"]) == 1440 and len({u["id"] for u in p["units"]}) == 1440
    assert sum(len(call_slots(u)) for u in units()) == 3240
    assert len(list(units((common.S60[0],)))) == 24
    assert sum(len(call_slots(u)) for u in units((common.S60[0],))) == 54
    assert all(common.split(u["source_id"]) == "DESIGN" for u in list(units())[:24])
    assert math.isclose(p["scenarios"]["area_scaled_assumption"]["total_seconds"], 6638.4)
    assert majority([True, None, False]) == dict(success=False, upper=True, positive_calls=1, missing_calls=1)
    assert majority([True, True, None])["success"]
    try:
        majority([True, False])
    except ValueError:
        pass
    else:
        raise AssertionError("Nonfixed seed inventory accepted")
    vine = dict(detections={"vine-r": {common.ALPHA: dict(status="ok", presence=dict(present=True),
                                                          wrong_message_presence=dict(present=False))}})
    assert call_metrics(vine, "vine-r", common.ALPHA)["presence"] is True
    assert call_metrics(vine, "vine-r", common.ALPHA)["B"] is None
    assert call_metrics(vine, "vine-r", common.BETA)["presence"] is False
    row = {**next(units()), "status": "running", "detections": {"f5-r2": {common.ALPHA: dict(status="running")}}}
    recovered, changed = interrupted(row)
    assert changed and recovered["status"] == "interrupted"
    assert recovered["detections"]["f5-r2"][common.ALPHA]["status"] == "interrupted"
    final = finalize(recovered)
    assert final["final"] and len(final["detections"]["f5-r2"]) == 2
    expected_unit = next(units())
    saved = {**final, "input_sha256": "saved-clean-hash", "payload": None}
    expected = {expected_unit["id"]: expected_unit}
    inputs = {(expected_unit["source_id"], expected_unit["arm"]):
              dict(output=dict(sha256="saved-clean-hash"), payload=None)}
    fake_path = common.RD / "server" / "self-test-memory-only" / "journal.jsonl"
    with patch.object(Path, "exists", return_value=True):
        with patch.object(common, "journal_rows", return_value={saved["id"]: saved}):
            assert Journal(fake_path, expected, inputs).latest[saved["id"]]["status"] == "interrupted"
        invalid = []
        for field, value in (("input_sha256", "changed"), ("seed", 15),
                             ("payload", {"h": "changed"}), ("status", "unregistered")):
            invalid.append({**saved, field: value})
        invalid.append({**saved, "detections": {}})
        invalid.append({**saved, "detections": {"unregistered": {common.ALPHA: dict(status="ok")}}})
        for bad in invalid:
            with patch.object(common, "journal_rows", return_value={bad["id"]: bad}):
                try:
                    Journal(fake_path, expected, inputs)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Altered resume row accepted")
    assert native_inventory({}) == {}
    fake_image = SimpleNamespace(mode="RGB", size=(1024, 1024))
    fake_result = SimpleNamespace(images=[fake_image], nsfw_content_detected=[False])
    assert validate_sd15(fake_result, 1024) is fake_image
    native_image = SimpleNamespace(mode="RGB", size=(512, 512))
    assert validate_sd15(SimpleNamespace(images=[native_image], nsfw_content_detected=[False]), 512) is native_image
    for malformed in (SimpleNamespace(images=[fake_image], nsfw_content_detected=[True]),
                      SimpleNamespace(images=[fake_image], nsfw_content_detected=None),
                      SimpleNamespace(images=[fake_image], nsfw_content_detected=[0]),
                      SimpleNamespace(images=[SimpleNamespace(mode="RGB", size=(512, 512))], nsfw_content_detected=[False])):
        try:
            validate_sd15(malformed, 1024)
        except RuntimeError:
            pass
        else:
            raise AssertionError("SD15 malformed safety/geometry accepted")
    summary = analyze({})
    assert summary["scale"]["verdict"] == "PENDING_FIXED_INVENTORY"
    assert all(x["success"] == 0 and x["upper"] == 30 for x in summary["source_majorities"])
    assert all(x["missing"] == 90 and x["positives"] == 0 for x in summary["negative_calls"])
    assert scale_decision(1, 7, 20, 14)["verdict"] == "SURVIVES_STRONG_SCALE_KILL"
    assert scale_decision(1, 6, 20, 14)["verdict"] == "KILL_STRONG_SCALE_EXPLANATION"
    assert scale_decision(1, 7, 20, 15)["verdict"] == "KILL_STRONG_SCALE_EXPLANATION"
    assert scale_decision(1, 7, 20, 14, False)["verdict"] == "PENDING_FIXED_INVENTORY"
    pilot_rows = {}
    for unit in units((common.S60[0],)):
        calls = {}
        for method, owner in call_slots(unit):
            calls.setdefault(method, {})[owner] = dict(status="ok", seconds=1.5)
        pilot_rows[unit["id"]] = {**unit, "status": "ok", "final": True, "output": {"sha256": "synthetic"},
                                  "generation_seconds": 2. if unit["cell"] == "sd15-1024" else .5,
                                  "detections": calls, "detection_seconds": {m: 1.5 * len(c) for m, c in calls.items()},
                                  "distortion": dict(status="ok"), "total_distortion": dict(status="ok"),
                                  "metrics_seconds": 10.}
    timing = pilot_timing(pilot_rows)
    assert timing["estimable"] and timing["measured_projection"]["reader_seconds"] == 4860.
    blocked = pilot_rows[next(iter(pilot_rows))]
    blocked.pop("output")
    blocked["detections"] = {}
    blocked["detection_seconds"] = {}
    blocked["distortion"] = dict(status="input_missing")
    pilot_rows[blocked["id"]] = finalize(blocked)
    assert pilot_timing(pilot_rows)["measured_projection"]["reader_seconds"] == 4860.
    assert not any(name in sys.modules for name in ("torch", "numpy", "PIL", "diffusers", "encoder_transfer_runtime"))
    return dict(status="PASS", scope="stdlib plan, exact inventory, missing bounds, native VINE N/A, scale kill, safety/geometry, resume integrity/no-retry, full-slot pilot projection; no science execution")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="Print full fixed inventory and three cost scenarios; stdlib only")
    parser.add_argument("--self-test", action="store_true", help="Run pure-logic assertions; no saved-data/pixel/model access")
    parser.add_argument("--continue-after-pilot", action="store_true", help="Explicitly continue after retained pilot under supplied actual ceiling")
    common.add_execution_args(parser)
    args = parser.parse_args()
    if sum(bool(x) for x in (args.plan, args.self_test, args.execute)) != 1:
        parser.error("Choose exactly one of --plan, --self-test, --execute")
    if args.continue_after_pilot and not args.execute:
        parser.error("--continue-after-pilot requires --execute")
    try:
        result = plan() if args.plan else self_test() if args.self_test else execute(args)
    except BaseException:
        # Preserve process/setup/budget failures as well as individual scientific rows.
        # Do not write anything if execution did not establish its own manifest.
        if args.execute and args.out and (Path(args.out) / "manifest.json").is_file():
            with (Path(args.out) / "failures.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(dict(time_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                            error=traceback.format_exc())) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        raise
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
