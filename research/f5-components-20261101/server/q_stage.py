"""Future Q-STAGE server diagnostic. --plan/--self-test are stdlib-only.

No scientific fidelity claim follows from local compilation. The first fixed
DESIGN pair is the measured pilot, is retained, and is never replaced. The
approved F6 package and historical runtime are read-only dependencies.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
import traceback

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as co

ARMS = ("A", "B", "unmarked")
CELLS = ("R0", "R1", "R3")
SNAPS = ("proposal_before_box", "after_box", "after_l2", "robust_rgb8",
         "first_fragile_rgb8", "refined_rgb8", "final_second_fragile_rgb8")
ENDPOINTS = ("C", "J", "O", "O_U", "O_Q", "Bs", "Bi", "B", "C_or_B", "sf", "sc", "sr", "if", "ic", "ir", "io", "H", "H_intended_reference")
SOURCE_HASHES = {
    "robust_pgd": "b60c7c5d0b775da5d77023b09946b3a74ba79ba6afcc5f0e1dc9e870cb0da0e3",
    "embed_rgb": "c349f45ec9b9ff8a59402a9164ad146b1ed1b2f76468801d7f5dd6207b511787",
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def uid(source, arm, channel="clean", seed=None):
    return f"Q-STAGE:{source}:{arm}:{channel}:{seed}"


def units(ids=None):
    for source in co.S12 if ids is None else ids:
        for arm in ARMS:
            yield dict(id=uid(source, arm), source_id=source, arm=arm,
                       channel="clean", seed=None, control="C0" if arm == "unmarked" else "C1")
        for channel in CELLS:
            for seed in co.SEEDS:
                for arm in ARMS:
                    yield dict(id=uid(source, arm, channel, seed), source_id=source, arm=arm,
                               channel=channel, strength=.2, seed=seed,
                               control="C0" if arm == "unmarked" else "C1")


def inventory():
    native = list(units())
    return dict(marks=24, snapshots=132, final_snapshots=24, additional_snapshot_probes=108,
                scalar_trace_rows=3600, regenerations=324, marked_regenerations=216,
                c0_regenerations=108, native_reader_calls=600, marked_regeneration_calls=432,
                c0_regeneration_calls=108, clean_reader_calls=60,
                intrinsic_ArmA_writer_verifications=12, native_units=native,
                snapshot_units=[dict(source_id=s, arm=a, stage=k,
                                     final=k == (SNAPS[-1] if a == "A" else SNAPS[3]))
                                for s in co.S12 for a in ("A", "B")
                                for k in (SNAPS if a == "A" else SNAPS[:4])])


def plan():
    base = 24 * 119 + 12 * 3 * 3 * (.54 + 1.24 + 1.98) + 600 * 1.5
    extra = 108 * 1.5
    return dict(queue="Q-STAGE", status="PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION",
                source_ids=list(co.S12), seeds=list(co.SEEDS), inventory=inventory(),
                pilot=dict(source_id=co.S12[0], split="DESIGN", included=True,
                           marks=2, snapshots=11, regenerations=27, native_reader_calls=50,
                           additional_snapshot_probes=9, scalar_trace_rows=300),
                writer=dict(A="Exact pinned F5 r2: 150 robust steps, fragile, 50 refinement steps at58dB, second fragile",
                            B="One 150-step robust-only attempt, PSNR allowance from A final realized RGB MSE",
                            source_contract=SOURCE_HASHES, final_psnr_match_tolerance_db=.1,
                            scalar_trace="Existing pre-update objective and margins; no additional model passes",
                            no_retry=True, no_quality_search=True),
                channels=[dict(id=c, strength=.2, resolution=512 if c == "R0" else 1024)
                          for c in CELLS],
                scenarios=[dict(label="historical_anchor_without_snapshot_probes", seconds=base,
                                hours=base/3600, historical_usd=base/3600*.551),
                           dict(label="anchor_plus_assumed_snapshot_cost", seconds=base+extra,
                                hours=(base+extra)/3600, historical_usd=(base+extra)/3600*.551),
                           dict(label="double_regeneration_plus_assumed_snapshot_cost",
                                seconds=base+extra+406.08, hours=(base+extra+406.08)/3600,
                                historical_usd=(base+extra+406.08)/3600*.551)],
                costs_unknown=["setup", "quality metrics", "trace and snapshot I/O", "retrieval", "human inspection"],
                native_call_accounting="600 frozen own-image-feature reads;108 separate one-owner snapshot probes;12 original writer verifications are intrinsic writer overhead and are not native endpoints",
                required_paid_inputs=["actual instance start UTC", "actual hourly USD", "max instance hours", "max USD"],
                human_visibility="MISSING", t4_t5="ABSENT: promotion prohibited",
                fidelity="Source-contract and observational instrumentation only; no scientific rehearsal has run",
                continuation="Default execution ends after included pilot; --continue-after-pilot uses measured cost forecast and actual remaining caps")


class Journal:
    """Terminal failures are immutable; torn tails fail closed via common."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.latest = co.journal_rows(self.path) if self.path.exists() else {}

    def append(self, row):
        row = dict(row, recorded_utc=utc())
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.latest[row["id"]] = row

    def claim(self, unit):
        if unit["id"] in self.latest:
            return False
        self.append(dict(unit, status="attempt_started"))
        return True


def strict_quality(row):
    q = row.get("quality", {})
    values = (q.get("psnr_db"), q.get("ssim_rgb"), q.get("lpips"))
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values) and \
        values[0] > 35 and values[1] > .9 and values[2] < .1


def source_functions():
    """Parse and hash source as text, without importing its scientific modules."""
    source = (co.ROOT / "scripts/f5_latent_codec.py").read_text(encoding="utf-8")
    found = {node.name: ast.get_source_segment(source, node) for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name in SOURCE_HASHES}
    for name, expected in SOURCE_HASHES.items():
        if name not in found or hashlib.sha256(found[name].encode()).hexdigest() != expected:
            raise ValueError(f"Pinned writer source changed: {name}; new review required")
    return found


def instrumented_sources():
    functions = source_functions()

    def inject(text, needle, replacement):
        if text.count(needle) != 1:
            raise ValueError("Instrumentation anchor not unique: " + needle)
        return text.replace(needle, replacement)

    pgd = functions["robust_pgd"]
    pgd = inject(pgd, "    for step in range(steps):", "    _qs.begin(steps)\n    for step in range(steps):")
    pgd = inject(pgd, "        g, = torch.autograd.grad(loss, eta)",
                 "        _qs.trace(step, steps, loss, m, mask * eta)\n        g, = torch.autograd.grad(loss, eta)")
    pgd = inject(pgd, "            delta = (x + mask * eta).clamp(0, 1) - x",
                 "            _qs.tensor_snapshot('proposal_before_box', x + mask * eta, step, steps)\n"
                 "            delta = (x + mask * eta).clamp(0, 1) - x\n"
                 "            _qs.tensor_snapshot('after_box', x + delta, step, steps)")
    pgd = inject(pgd, "            eta.copy_(delta / mask)",
                 "            eta.copy_(delta / mask)\n"
                 "            _qs.tensor_snapshot('after_l2', x + mask * eta, step, steps)")
    emb = functions["embed_rgb"]
    emb = inject(emb, "    fragile_report = None", "    _qs.snapshot('robust_rgb8', current / 255.0, 'RGB8')\n    fragile_report = None")
    emb = inject(emb, "        itable = v5._instance_table(owner, key, config)",
                 "        _qs.targets(q, h, round_index)\n        itable = v5._instance_table(owner, key, config)")
    emb = inject(emb, "        if round_index < refine_rounds:",
                 "        _qs.snapshot('first_fragile_rgb8' if round_index == 0 else 'final_second_fragile_rgb8', current / 255.0, 'RGB8')\n"
                 "        if round_index < refine_rounds:")
    emb = inject(emb, "            current = np.clip(np.rint(refined * 255), 0, 255)",
                 "            current = np.clip(np.rint(refined * 255), 0, 255)\n"
                 "            _qs.snapshot('refined_rgb8', current / 255.0, 'RGB8')")
    return pgd, emb


@contextmanager
def instrument(f5, recorder):
    """Execute source-checked observational clones; restore original functions."""
    namespace = dict(f5.__dict__, _qs=recorder)
    for code in instrumented_sources():
        exec(compile(code, "<Q-STAGE observational instrumentation>", "exec"), namespace)
    old_pgd, old_embed = f5.robust_pgd, f5.embed_rgb
    f5.robust_pgd, f5.embed_rgb = namespace["robust_pgd"], namespace["embed_rgb"]
    try:
        yield
    finally:
        f5.robust_pgd, f5.embed_rgb = old_pgd, old_embed


class Recorder:
    """All arrays/norms are diagnostic observations, detached from optimization."""
    def __init__(self, root, source, arm, original, traces, budget):
        import numpy as np
        from scipy.ndimage import uniform_filter
        self.np, self.root, self.source, self.arm = np, Path(root), source, arm
        self.original = original.astype(np.float64) / 255
        self.traces, self.budget, self.initial = traces, budget, False
        self.snapshots, self.target_words = {}, []
        y = self.original @ np.array([.299, .587, .114])
        activity = np.sqrt(np.maximum(uniform_filter(y*y, 5)-uniform_filter(y, 5)**2, 0))
        # Fixed, C0-only 25% low/high activity pixels; stable tie breaking.
        order = np.argsort(activity.ravel(), kind="stable")
        n = activity.size // 4
        self.masks = {}
        for label, chosen in (("flat", order[:n]), ("textured", order[-n:])):
            mask = np.zeros(activity.size, dtype=bool)
            mask[chosen] = True
            self.masks[label] = mask.reshape(activity.shape)
        self.root.mkdir(parents=True, exist_ok=True)
        np.savez(self.root / "c0_masks.npz", **self.masks)
        self.mask_artifact = dict(path=str(self.root / "c0_masks.npz"), sha256=co.digest(self.root / "c0_masks.npz"),
                                  definition="C0 5px local luma SD, stable lowest/highest quartile; no outcome-derived masks")
        self.patch_centers = {}
        width = activity.shape[1]
        for label, index in (("flat", int(order[0])), ("textured", int(order[-1]))):
            self.patch_centers[label] = [index // width, index % width]

    def begin(self, steps):
        self.initial = steps == 150

    def trace(self, step, steps, loss, margins, residual):
        self.budget.check(reserve=5)
        if not self.initial:
            return
        m = margins.detach().double().cpu().numpy()
        self.traces.append(dict(id=f"trace:{self.source}:{self.arm}:{step}", source_id=self.source, arm=self.arm,
                                iteration=step, timing="pre-update existing objective", objective=float(loss.detach().cpu()),
                                margin_median=float(self.np.median(m)), margin_min=float(m.min()),
                                negative_chips=int((m < 0).sum()), residual_l2=float(residual.detach().norm().cpu())))

    def tensor_snapshot(self, name, tensor, step, steps):
        if self.initial and step == steps-1:
            self.snapshot(name, tensor.detach()[0].permute(1, 2, 0).double().cpu().numpy(), "float")

    def targets(self, q, h, round_index):
        self.target_words.append(dict(q=f"{q:08x}", h=f"{h:08x}", fragile_write=round_index+1))

    def snapshot(self, name, array, representation):
        np = self.np
        array = np.asarray(array, np.float64).copy()
        if not np.isfinite(array).all():
            raise ValueError("Nonfinite snapshot; refuse quantization")
        path = self.root / (name + ".npy")
        np.save(path, array, allow_pickle=False)
        delta = array-self.original
        local = {}
        for label, mask in self.masks.items():
            values = delta[mask]
            cy, cx = self.patch_centers[label]
            y, x = max(0, min(cy-32, array.shape[0]-64)), max(0, min(cx-32, array.shape[1]-64))
            patch = self.root / (name + "_" + label + "_native_patch.npz")
            np.savez(patch, c0=self.original[y:y+64, x:x+64], stage=array[y:y+64, x:x+64],
                     residual=delta[y:y+64, x:x+64])
            local[label] = dict(rms=float(np.sqrt(np.mean(values**2))), max_abs=float(np.max(np.abs(values))),
                                patch=dict(path=str(patch), sha256=co.digest(patch), xy=[x, y], native_pixels=True))
        self.snapshots[name] = dict(path=str(path), sha256=co.digest(path), representation=representation,
                                   min=float(array.min()), max=float(array.max()),
                                   out_of_box_components=int(((array < 0) | (array > 1)).sum()),
                                   residual_l2=float(np.linalg.norm(delta)), mse01=float(np.mean(delta**2)),
                                   local=local, human_visibility="MISSING")

    def finish(self):
        np = self.np
        transitions = []
        previous = self.original
        previous_name = "C0"
        for name in SNAPS if self.arm == "A" else SNAPS[:4]:
            item = self.snapshots[name]
            array = np.load(item["path"], allow_pickle=False)
            increment, residual = array-previous, previous-self.original
            transitions.append(dict(before=previous_name, after=name,
                                    increment_l2=float(np.linalg.norm(increment)),
                                    increment_mse01=float(np.mean(increment**2)),
                                    signed_cross_mse01=float(2*np.mean(residual*increment)),
                                    realized_mse_change01=float(np.mean((array-self.original)**2)-np.mean(residual**2)),
                                    interpretation={"after_box": "box clipping", "after_l2": "L2 projection",
                                                    "robust_rgb8": "rounding to RGB8"}.get(name, "named operation; earlier iterations not decomposed")))
            previous, previous_name = array, name
        return dict(snapshots=self.snapshots, transitions=transitions, target_words=self.target_words,
                    c0_masks=self.mask_artifact, human_visibility="MISSING")


def checked_rgb(runtime, artifact):
    path = Path(artifact["path"])
    if co.digest(path) != artifact["sha256"]:
        raise ValueError("Output hash mismatch: " + str(path))
    return runtime.load_rgb(path)


def diagnostic(adapter, array, payload, *, rgb8=False, features=None, latent=None, raw=None):
    """One-owner probe; float values are retained separately, never quantized away."""
    import numpy as np
    f5, v5 = adapter.f5, adapter.v5
    projected = np.clip(array, 0, 1)
    proxy = np.clip(np.rint(projected*255), 0, 255).astype(np.uint8)
    if features is None:
        features = adapter.features(proxy, 7)
    if latent is None:
        with adapter.torch.inference_mode():
            latent = adapter.reader.encode(adapter.reader.tensor(projected)).double().cpu().numpy()
    if raw is None:
        raw = f5.detect_rgb(proxy if rgb8 else projected*255, latent, co.ALPHA, adapter.profile,
                            features, binding="soft")
    checked, key, config = v5._resolve(adapter.profile, None)
    owner = v5.canonical_owner(co.ALPHA)
    q, h = int(payload["q"], 16), int(payload["h"], 16)
    table = v5._semantic_table(owner, key, config)
    ws = [chip for j in range(v5.CODE_BITS) for chip in table[j][v5._bit(q, j)]]
    luma = v5.luminance_from_rgb((proxy if rgb8 else projected*255).tolist())
    fragile = v5._Fragile(checked, key, config, owner, len(luma), len(luma[0]))
    _, coefficients = f5.base._analyse(luma, fragile.analysis)
    table = v5._instance_table(owner, key, config)
    wi = [chip for j in range(v5.CODE_BITS) for chip in table[j][v5._bit(q, j)][v5._bit(h, j)]]
    robust = np.asarray(ws)*np.asarray(f5.Layout(checked, key, config, owner).projections(latent))
    instance = np.asarray(wi)*np.asarray(fragile.projections(coefficients))
    margins = {label: dict(median=float(np.median(m)), minimum=float(m.min()),
                          negative_chips=int((m < 0).sum()), target_q=payload["q"], target_h=payload["h"])
               for label, m in (("robust", robust), ("instance", instance))}
    return dict(raw=raw, margins=margins, encoder_projection="clip(float01,0,1), no RGB8 quantization",
                clip_features="native RGB8" if rgb8 else "clipped RGB8 proxy; float probe diagnostic only")


def append_failure(journal, unit, exc, started):
    message = str(exc)
    status = "safety_blocked" if "safety" in message.lower() else "error"
    journal.append(dict(unit, status=status, error=traceback.format_exc(), seconds=time.monotonic()-started))


def make_marks(ids, config, args, budget, runtime, images, traces):
    import numpy as np
    if all(uid(source, arm) in images.latest for source in ids for arm in ARMS):
        return
    sources = co.clean_inputs(args.stage2a, args.stage2b, ids, ["unmarked"])
    budget.check()
    adapter = runtime.Internal(Path(args.assets), config)
    try:
        for source in ids:
            c0unit = next(u for u in units([source]) if u["arm"] == "unmarked" and u["channel"] == "clean")
            c0row = sources[(source, "unmarked")]
            c0artifact = dict(path=str(c0row["local_path"]), sha256=c0row["output"]["sha256"])
            if images.claim(c0unit):
                images.append(dict(c0unit, status="generated", output=c0artifact, seconds=0,
                                   source_stage2_row=c0row["id"], source_stage2_sha256=c0artifact["sha256"]))
            original = checked_rgb(runtime, c0artifact)
            for arm in ("A", "B"):
                unit = next(u for u in units([source]) if u["arm"] == arm and u["channel"] == "clean")
                if unit["id"] in images.latest:
                    continue
                budget.check()
                if not images.claim(unit):
                    continue
                started = time.monotonic()
                try:
                    runtime.seed_everything(config["implementation_seed"])
                    recorder = Recorder(Path(args.out)/"stages"/str(source)/arm, source, arm, original, traces, budget)
                    params = dict(config["f5"])
                    views = params.pop("semantic_views")
                    if (params["steps"], params["psnr_db"], params["refine_rounds"], params["mask_power"]) != (150, 52, 1, 0):
                        raise ValueError("Expected exact F5 r2 writer configuration")
                    features = adapter.features(original, views)
                    with instrument(adapter.f5, recorder):
                        if arm == "A":
                            marked, report = adapter.f5.embed_rgb(original, co.ALPHA, adapter.profile,
                                                                 features, adapter.reader, **params)
                            intended = dict(recorder.target_words[-1], h_target_basis="actual second fragile write intended h")
                            payload = dict(q=report["semantic_code"], h=report["verification"]["instance"].get("decoded_code"),
                                           h_target_basis="historical native clean decoded h proxy from original writer verification")
                        else:
                            parent = images.latest.get(uid(source, "A"), {})
                            if parent.get("status") != "generated":
                                raise ValueError("ArmA final unavailable: ArmB has no matched-budget attempt")
                            a = checked_rgb(runtime, parent["output"])
                            mse = float(np.mean(((a.astype(np.float64)-original)/255)**2))
                            if mse <= 0:
                                raise ValueError("No positive realized ArmA distortion allowance")
                            psnr = -10*math.log10(mse)
                            f5, v5 = adapter.f5, adapter.v5
                            checked, key, cfg = v5._resolve(adapter.profile, None)
                            owner = v5.canonical_owner(co.ALPHA)
                            luma = v5.luminance_from_rgb(original.tolist())
                            q, ws = f5._semantic_pattern(checked, key, cfg, owner, features, luma)
                            layout = f5.Layout(checked, key, cfg, owner, params["band"], params["whitening"])
                            float_rgb = f5.robust_pgd(adapter.reader, original.astype(np.float64)/255, layout, ws,
                                                     psnr, 150, params["target_margin"], params["mask_power"])
                            marked = np.clip(np.rint(float_rgb*255), 0, 255).astype(np.uint8)
                            recorder.snapshot("robust_rgb8", marked.astype(np.float64)/255, "RGB8")
                            payload = dict(q=f"{q:08x}", h=parent["payload"]["h"],
                                           h_target_basis="paired ArmA historical clean decoded h reference; ArmB embeds no h")
                            intended = dict(q=f"{q:08x}", h=parent["intended_payload"]["h"],
                                            h_target_basis="paired ArmA second-write intended h reference; ArmB embeds no h")
                            recorder.target_words = [intended]
                            report = dict(arm="B", psnr_target_db=psnr, steps=150,
                                          matched_to_A_final_mse01=mse, no_second_tier=True, one_attempt=True)
                    quality = adapter.metrics(original, marked)
                    output = runtime.save_rgb(Path(args.out)/"images"/f"{source}-{arm}-clean.png", marked)
                    stage = recorder.finish()
                    images.append(dict(unit, status="generated", output=output, input_sha256=c0artifact["sha256"],
                                       quality=quality, payload=payload, intended_payload=intended, embedding_report=report, stages=stage,
                                       seconds=time.monotonic()-started))
                except Exception as exc:
                    append_failure(images, unit, exc, started)
                    if isinstance(exc, TimeoutError):
                        raise
    finally:
        del adapter
        runtime.release()


def regenerate(ids, config, args, budget, runtime, images):
    for channel in CELLS:
        pending = [u for u in units(ids) if u["channel"] == channel and u["id"] not in images.latest]
        if not pending:
            continue
        budget.check()
        spec = next(c for c in config["channels"] if c["id"] == channel)
        generator = runtime.Regenerator(Path(args.assets), spec)
        try:
            for unit in pending:
                budget.check()
                if not images.claim(unit):
                    continue
                started = time.monotonic()
                try:
                    dependency = images.latest.get(uid(unit["source_id"], unit["arm"]), {})
                    if dependency.get("status") != "generated":
                        images.append(dict(unit, status="input_missing", dependency=dependency.get("id"), seconds=0))
                        continue
                    rgb = checked_rgb(runtime, dependency["output"])
                    runtime.seed_everything(config["implementation_seed"])
                    if spec["resolution"] != 512:
                        rgb = runtime.resize_rgb(rgb, spec["resolution"])
                    result = generator(rgb, .2, unit["seed"])
                    if spec["resolution"] != 512:
                        result = runtime.resize_rgb(result, 512)
                    path = Path(args.out)/"images"/f'{unit["source_id"]}-{unit["arm"]}-{channel}-{unit["seed"]}.png'
                    images.append(dict(unit, status="generated", output=runtime.save_rgb(path, result),
                                       payload=dependency.get("payload"), input_sha256=dependency["output"]["sha256"],
                                       seconds=time.monotonic()-started))
                except Exception as exc:
                    append_failure(images, unit, exc, started)
                    if isinstance(exc, TimeoutError):
                        raise
        finally:
            del generator
            runtime.release()


def read_outputs(ids, config, args, budget, runtime, images, reads, probes):
    import numpy as np
    from encoder_transfer_test import endpoints
    pending_native = any(u["id"]+":"+o not in reads.latest for u in units(ids)
                         for o in ((co.ALPHA,) if u["arm"] == "unmarked" else (co.ALPHA, co.BETA)))
    pending_probes = any(f"probe:{s}:{a}:{k}" not in probes.latest for s in ids for a in ("A", "B")
                         for k in (SNAPS[:-1] if a == "A" else SNAPS[:3]))
    if not pending_native and not pending_probes:
        return
    budget.check()
    adapter = runtime.Internal(Path(args.assets), config)
    try:
        for unit in units(ids):
            owners = (co.ALPHA,) if unit["arm"] == "unmarked" else (co.ALPHA, co.BETA)
            pending = [o for o in owners if unit["id"]+":"+o not in reads.latest]
            if not pending:
                continue
            budget.check()
            row = images.latest.get(unit["id"], {})
            # Claim before feature/encoder work so an interrupted attempt is not replayed.
            for owner in pending:
                reads.claim(dict(unit, id=unit["id"]+":"+owner, owner=owner))
            started = time.monotonic()
            try:
                if row.get("status") != "generated":
                    for owner in pending:
                        reads.append(dict(unit, id=unit["id"]+":"+owner, owner=owner,
                                          status="input_missing", seconds=0))
                    continue
                rgb = checked_rgb(runtime, row["output"])
                feature_start = time.monotonic()
                features, latent = adapter.features(rgb, 7), adapter.reader.latent(rgb)
                feature_encoder_seconds = time.monotonic()-feature_start
                for owner in pending:
                    call_start = time.monotonic()
                    raw = adapter._detect(rgb, "f5", owner, features, latent)
                    ep = endpoints(raw, row.get("payload") if owner == co.ALPHA and unit["arm"] != "unmarked" else None)
                    extra = {}
                    if unit["channel"] == "clean" and unit["arm"] != "unmarked" and owner == co.ALPHA:
                        # Reuse this native pass's latent/features; no extra encoder or CLIP call.
                        diag = diagnostic(adapter, rgb.astype(np.float64)/255, row["intended_payload"],
                                          rgb8=True, features=features, latent=latent, raw=raw)
                        extra["final_margins"] = diag["margins"]
                    fields = co.reader_fields(raw, ep)
                    fields.update(sc=bool(raw["semantic"]["content_match"]), sr=bool(raw["semantic"]["read"]),
                                  ic=bool(raw["instance"]["content_match"]), ir=bool(raw["instance"]["read"]))
                    intended = images.latest.get(uid(unit["source_id"], unit["arm"]), {}).get("intended_payload")
                    fields["H_intended_reference"] = endpoints(raw, intended if owner == co.ALPHA else None)["H"]
                    reads.append(dict(unit, id=unit["id"]+":"+owner, owner=owner, status="ok",
                                      raw=raw, endpoints=ep, fields=fields,
                                      output_sha256=row["output"]["sha256"], seconds=time.monotonic()-call_start,
                                      shared_feature_encoder_seconds=feature_encoder_seconds,
                                      shared_feature_encoder_timing_unit=unit["id"],
                                      **extra))
                # Quality independent of read outcomes, relative to clean and C0.
                if unit["channel"] != "clean":
                    dependency = images.latest[uid(unit["source_id"], unit["arm"])]
                    c0 = images.latest[uid(unit["source_id"], "unmarked")]
                    quality = adapter.metrics(checked_rgb(runtime, dependency["output"]), rgb)
                    total_quality = adapter.metrics(checked_rgb(runtime, c0["output"]), rgb)
                    images.append(dict(row, attack_quality=quality, total_quality=total_quality))
            except Exception as exc:
                if row.get("status") == "generated":
                    images.append(dict(row, read_or_quality_error=traceback.format_exc()))
                for owner in pending:
                    rid = unit["id"]+":"+owner
                    if reads.latest[rid].get("status") == "attempt_started":
                        append_failure(reads, dict(unit, id=rid, owner=owner), exc, started)
                if isinstance(exc, TimeoutError):
                    raise
        for source in ids:
            for arm in ("A", "B"):
                row = images.latest.get(uid(source, arm), {})
                for name in (SNAPS[:-1] if arm == "A" else SNAPS[:3]):
                    unit = dict(id=f"probe:{source}:{arm}:{name}", source_id=source, arm=arm, stage=name)
                    if unit["id"] in probes.latest:
                        continue
                    budget.check()
                    if not probes.claim(unit):
                        continue
                    started = time.monotonic()
                    try:
                        if row.get("status") != "generated":
                            probes.append(dict(unit, status="input_missing", seconds=0))
                            continue
                        snap = row["stages"]["snapshots"][name]
                        if co.digest(snap["path"]) != snap["sha256"]:
                            raise ValueError("Snapshot hash mismatch")
                        array = np.load(snap["path"], allow_pickle=False)
                        diag = diagnostic(adapter, array, row["intended_payload"], rgb8=snap["representation"] == "RGB8")
                        probes.append(dict(unit, status="ok", snapshot_sha256=snap["sha256"], **diag,
                                           target_basis="Common final ArmA intended q/h, with stage-specific write targets retained in image journal",
                                           seconds=time.monotonic()-started))
                    except Exception as exc:
                        append_failure(probes, unit, exc, started)
                        if isinstance(exc, TimeoutError):
                            raise
    finally:
        del adapter
        runtime.release()


def value(reads, source, arm, channel, seed, endpoint, owner=None):
    row = reads.get(uid(source, arm, channel, seed)+":"+(co.ALPHA if owner is None else owner), {})
    return row.get("fields", {}).get(endpoint) if row.get("status") == "ok" else None


def majority_bounds(values):
    success = sum(v is True for v in values)
    missing = sum(v is None for v in values)
    return success >= 2, success+missing >= 2, missing


def analyze(images, reads, probes):
    counts, vectors = {}, {}
    for group in ("DESIGN", "EVALUATE"):
        ids = [s for s in co.S12 if co.split(s) == group]
        for arm in ("A", "B"):
            for channel in CELLS:
                for endpoint in ENDPOINTS:
                    per = {s: majority_bounds([value(reads, s, arm, channel, seed, endpoint) for seed in co.SEEDS]) for s in ids}
                    key = f"{group}/{arm}/{channel}/{endpoint}"
                    counts[key] = dict(planned_sources=len(ids), lower=sum(v[0] for v in per.values()),
                                       upper_missing_as_success=sum(v[1] for v in per.values()),
                                       missing_calls=sum(v[2] for v in per.values()))
                    vectors[key] = {s for s, v in per.items() if v[0]}
    quality = {}
    for source in co.S12:
        a, b = images.get(uid(source, "A"), {}), images.get(uid(source, "B"), {})
        pa, pb = a.get("quality", {}).get("psnr_db"), b.get("quality", {}).get("psnr_db")
        matched = isinstance(pa, (int, float)) and isinstance(pb, (int, float)) and abs(pa-pb) <= .1
        snaps = a.get("stages", {}).get("snapshots", {})
        slack = (snaps.get(SNAPS[-1], {}).get("mse01", 0)-snaps.get("robust_rgb8", {}).get("mse01", 0)) if snaps else None
        quality[str(source)] = dict(A_strict=strict_quality(a), B_strict=strict_quality(b),
                                    match_within_point1dB=matched, feasible=matched and strict_quality(a) and strict_quality(b),
                                    realized_late_stage_mse01=slack)
    stage = []
    eval_ids = [s for s in co.S12 if co.split(s) == "EVALUATE"]
    for source in eval_ids:
        early = probes.get(f"probe:{source}:A:robust_rgb8", {})
        final = reads.get(uid(source, "A")+":"+co.ALPHA, {})
        if early.get("status") == final.get("status") == "ok":
            a = early["raw"]["semantic"]["decoded_score"]
            b = final["raw"]["semantic"]["decoded_score"]
            e = early["margins"]["robust"]["negative_chips"]
            f = final["final_margins"]["robust"]["negative_chips"]
            stage.append(dict(source_id=source, robust_decoded_score_loss=a-b, negative_chip_increase=f-e))
    losses = [r["robust_decoded_score_loss"] for r in stage]
    median = statistics.median(losses) if losses else None
    stage_unsupported = len(stage) == len(eval_ids) and median < .25 and not any(r["negative_chip_increase"] > 0 for r in stage)
    negatives = {}
    for endpoint in ENDPOINTS:
        vals = []
        for unit in units():
            if unit["arm"] == "unmarked":
                vals.append(value(reads, unit["source_id"], unit["arm"], unit["channel"], unit["seed"], endpoint))
            else:
                vals.append(value(reads, unit["source_id"], unit["arm"], unit["channel"], unit["seed"], endpoint, co.BETA))
        negatives[endpoint] = dict(planned_calls=len(vals), events=sum(v is True for v in vals), missing=sum(v is None for v in vals))
    gains = sum(len(vectors[f"EVALUATE/B/{c}/C"]-vectors[f"EVALUATE/A/{c}/C"]) for c in ("R1", "R3"))
    r0_loss = vectors["EVALUATE/A/R0/C"]-vectors["EVALUATE/B/R0/C"]
    ou_losses = {c: sorted(vectors[f"EVALUATE/A/{c}/O_U"]-vectors[f"EVALUATE/B/{c}/O_U"]) for c in CELLS}
    kills = []
    if not gains:
        kills.append("no EVALUATE C gain in either foreign cell")
    if r0_loss:
        kills.append("any EVALUATE SD1.5 C source loss")
    if any(ou_losses.values()):
        kills.append("any EVALUATE O_U source loss")
    if not all(q["feasible"] for q in quality.values()):
        kills.append("strict clean quality or matched-quality gate failed/unresolved")
    if any(negatives[e]["events"] or negatives[e]["missing"] for e in ("C", "J", "O_U")):
        kills.append("available C/J/O_U negative gate failed/unresolved")
    if any(v["missing_calls"] for k, v in counts.items() if k.startswith("EVALUATE/")):
        kills.append("incomplete EVALUATE native calls; positive inference unavailable")
    no_slack = not any(q["realized_late_stage_mse01"] is not None and q["realized_late_stage_mse01"] > 0 for q in quality.values())
    no_feasible = not any(q["feasible"] for q in quality.values())
    return dict(status="PROPOSED_EXPLORATORY_DIAGNOSTIC", source_majority=counts,
                negative_calls=negatives, quality=quality, stage_damage=dict(rows=stage, median_loss=median,
                missing_sources=len(eval_ids)-len(stage), explanation="UNSUPPORTED" if stage_unsupported else "UNKNOWN_OR_NOT_KILLED"),
                spendable_budget=dict(killed=no_slack or no_feasible, no_realized_slack=no_slack, no_feasible_matched_B=no_feasible),
                robust_only=dict(promotion="PROHIBITED_T4_T5_ABSENT", native_diagnostic_killed=bool(kills),
                                 kill_reasons=kills, foreign_C_gains=gains, R0_C_losses=sorted(r0_loss), O_U_losses=ou_losses),
                missingness="Missing is unsuccessful; separate source-majority upper bounds treat missing as success",
                B="Failed diagnostic endpoint, never production replacement", human_visibility="MISSING")


def validate_journals(images, reads, probes, traces):
    expected_images = {u["id"]: u for u in units()}
    expected_reads = {u["id"]+":"+owner: dict(u, owner=owner) for u in units()
                      for owner in ((co.ALPHA,) if u["arm"] == "unmarked" else (co.ALPHA, co.BETA))}
    expected_probes = {f"probe:{s}:{a}:{k}": dict(source_id=s, arm=a, stage=k)
                       for s in co.S12 for a in ("A", "B") for k in (SNAPS[:-1] if a == "A" else SNAPS[:3])}
    expected_traces = {f"trace:{s}:{a}:{i}": dict(source_id=s, arm=a, iteration=i)
                       for s in co.S12 for a in ("A", "B") for i in range(150)}
    identity_fields = ("source_id", "arm", "channel", "seed", "control", "owner", "stage", "iteration")
    for actual, expected in ((images, expected_images), (reads, expected_reads),
                              (probes, expected_probes), (traces, expected_traces)):
        for rid, row in actual.items():
            if rid not in expected or row.get("id") != rid:
                raise ValueError("Unknown/mismatched resumed row: " + rid)
            target = expected[rid]
            if any(row.get(k) != target[k] for k in identity_fields if k in target):
                raise ValueError("Resumed row identity fields differ: " + rid)


def execute(args):
    config, budget = co.execution_context(args, "Q-STAGE")
    source_functions()
    sys.path.insert(0, str(co.ROOT / "scripts"))
    import encoder_transfer_runtime as runtime
    out = Path(args.out)
    identity_path = out / "run-identity.json"
    if out.exists() and any(out.iterdir()) and not identity_path.exists():
        raise ValueError("Nonempty output directory has no Q-STAGE identity; refuse adopting files")
    frozen_inputs = co.clean_inputs(args.stage2a, args.stage2b, co.S12, ["unmarked"])
    identity = dict(queue="Q-STAGE", provenance=co.provenance("Q-STAGE"), plan=plan(), assets=str(Path(args.assets).resolve()),
                    stage2a=str(Path(args.stage2a).resolve()), stage2b=str(Path(args.stage2b).resolve()), config=config,
                    source_inputs=[dict(source_id=s, id=frozen_inputs[(s, "unmarked")]["id"],
                                        sha256=frozen_inputs[(s, "unmarked")]["output"]["sha256"],
                                        payload=frozen_inputs[(s, "unmarked")].get("payload")) for s in co.S12],
                    paid_contract=dict(instance_start=args.instance_start, hourly=args.hourly,
                                       max_hours=args.max_hours, max_usd=args.max_usd))
    if identity_path.exists() and co.read(identity_path) != identity:
        raise ValueError("Resume identity changed; refuse mixing revisions/assets/source journals")
    co.write(identity_path, identity)
    images, reads = Journal(out/"images.jsonl"), Journal(out/"native-reads.jsonl")
    probes, traces = Journal(out/"snapshot-probes.jsonl"), Journal(out/"scalar-traces.jsonl")
    validate_journals(images.latest, reads.latest, probes.latest, traces.latest)
    # A crash after claim is an unsuccessful terminal attempt, never a new random draw.
    for journal in (images, reads, probes):
        for row in list(journal.latest.values()):
            if row.get("status") == "attempt_started":
                journal.append(dict(row, status="interrupted", missing=True, no_retry=True))
    pilot_path = out/"pilot.json"
    try:
        if not pilot_path.exists():
            start = time.monotonic()
            ids = [co.S12[0]]
            make_marks(ids, config, args, budget, runtime, images, traces)
            regenerate(ids, config, args, budget, runtime, images)
            read_outputs(ids, config, args, budget, runtime, images, reads, probes)
            elapsed = time.monotonic()-start
            completeness = all(r.get("status") == "generated" for r in images.latest.values()) and \
                len(images.latest) == 30 and len(reads.latest) == 50 and len(probes.latest) == 9 and \
                len(traces.latest) == 300 and all(r.get("status") == "ok" for r in reads.latest.values()) and \
                all(r.get("status") == "ok" for r in probes.latest.values())
            co.write(pilot_path, dict(source_id=co.S12[0], included=True, seconds=elapsed,
                                     full_forecast_seconds=elapsed*12, remaining_forecast_seconds=elapsed*11,
                                     successful_complete_pilot=completeness, budget=budget.record(),
                                     fidelity="Pinned source observational instrumentation; numeric equivalence to an uninstrumented rerun NOT TESTED"))
        pilot = co.read(pilot_path)
        if args.continue_after_pilot:
            if not pilot["successful_complete_pilot"]:
                raise ValueError("Incomplete/failed pilot: stop without replacements or retries")
            # Conservative full remaining estimate, including setup overhead already measured.
            budget.check(reserve=pilot["remaining_forecast_seconds"])
            ids = list(co.S12[1:])
            make_marks(ids, config, args, budget, runtime, images, traces)
            regenerate(ids, config, args, budget, runtime, images)
            read_outputs(ids, config, args, budget, runtime, images, reads, probes)
        co.write(out/"analysis.json", analyze(images.latest, reads.latest, probes.latest))
        co.write(out/"run-status.json", dict(status="COMPLETE_ATTEMPT_INVENTORY" if args.continue_after_pilot else "PILOT_COMPLETE_REVIEW_REQUIRED",
                                           budget=budget.record(), actual_images=len(images.latest), native_calls=len(reads.latest),
                                           probes=len(probes.latest), scalar_trace_rows=len(traces.latest), human_visibility="MISSING"))
    finally:
        co.write(out/"budget-last.json", budget.record())


def self_test():
    assert len(list(units())) == 360
    inv = inventory()
    assert len(inv["snapshot_units"]) == 132
    assert sum(1 if u["arm"] == "unmarked" else 2 for u in units()) == 600
    assert len([u for u in units() if u["channel"] != "clean"]) == 324
    assert all(sum(u["source_id"] == s for u in units()) == 30 for s in co.S12)
    assert sum(s["arm"] == "A" for s in inv["snapshot_units"]) == 84
    assert sum(s["arm"] == "B" for s in inv["snapshot_units"]) == 48
    assert majority_bounds([True, None, False]) == (False, True, 1)
    assert majority_bounds([True, True, None]) == (True, True, 1)
    assert not strict_quality({"quality": dict(psnr_db=35, ssim_rgb=.95, lpips=.05)})
    assert strict_quality({"quality": dict(psnr_db=36, ssim_rgb=.95, lpips=.05)})
    for code in instrumented_sources():
        compile(code, "<stdlib-only instrumentation syntax>", "exec")
    result = analyze({}, {}, {})
    assert result["robust_only"]["promotion"] == "PROHIBITED_T4_T5_ABSENT"
    assert result["robust_only"]["native_diagnostic_killed"]
    assert result["spendable_budget"]["killed"]
    assert result["source_majority"]["EVALUATE/A/R0/C"]["lower"] == 0
    assert result["source_majority"]["EVALUATE/A/R0/C"]["upper_missing_as_success"] == 6
    assert result["source_majority"]["EVALUATE/A/R0/C"]["missing_calls"] == 18
    validate_journals({}, {}, {}, {})
    try:
        validate_journals({"unknown": dict(id="unknown")}, {}, {}, {})
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown resumed row was accepted")
    return dict(status="PASS", scope="stdlib plan, source-checked instrumentation syntax, missingness and kill logic; no science execution")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--continue-after-pilot", action="store_true")
    co.add_execution_args(parser)
    args = parser.parse_args(argv)
    if sum((args.plan, args.self_test, args.execute)) != 1:
        parser.error("Choose exactly one of --plan, --self-test, --execute")
    if args.plan:
        print(json.dumps(plan(), indent=2, allow_nan=False))
    elif args.self_test:
        print(json.dumps(self_test()))
    else:
        execute(args)


if __name__ == "__main__":
    main()
