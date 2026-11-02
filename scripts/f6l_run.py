"""SERVER ONLY: lean F6 stages. Native, threat, secondary, reader and quality units are
the reviewed Stage S functions, called on a lean config. This file adds the writer
stage, the probe and the paid-cap checks. The plan action alone is standard library.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f6l_common as lean_common
import f7_dual
import tifs_common as common
import tifs_stage_s as stage
import tifs_stage_s_read as read

ROOT = lean_common.ROOT
STAGE_S_MANIFEST = ROOT / "research/tifs-20261028/stage-s/source-manifest.json"
STAGE_P_MANIFEST = ROOT / "research/tifs-20261028/stage-p/source-manifest.json"
BASE_CONFIG = ROOT / "research/tifs-20261028/stage-s/frozen-config.json"
CODE = ("f6l_common.py", "f6l_writer.py", "f6l_run.py", "f6l_select.py", "f6l_driver.sh", "f6l_setup.py",
        "tifs_common.py", "tifs_stage_s.py", "tifs_stage_s_read.py", "tifs_writer.py", "tifs_denoiser.py", "tifs_vine_b.py",
        "encoder_transfer_runtime.py", "encoder_transfer_test.py", "et_final_pilot.py", "et_final_phase_a.py",
        "et_final_phase_a_attacks.py", "f5_latent_codec.py", "revised_watermark_v5.py", "f5_gate.py",
        "three_threat_models.py", "journal_vae_probe.py", "a6_clip_visual.py", "m1_latent_reconstruction.py",
        "tifs_stage_p.py", "tifs_stage_s_analyze.py", "f7_dual.py")


def plan(args):
    """Fix one phase's arms and inventory before its first output. Stage 2 and 3 read the last decision."""
    lean = lean_common.load_lean()
    base = common.load_json(BASE_CONFIG)
    previous = common.load_json(args.previous) if args.previous else None
    if previous is not None and previous.get("status") != "ADVANCE":
        raise ValueError("The previous stage did not advance")
    config = lean_common.stage_config(lean, base, args.phase, previous=previous)
    path = args.out / "config.json"
    if path.exists():
        if common.load_json(path) != config:
            raise ValueError("A phase config cannot change after it is fixed")
    else:
        common.atomic_json(path, config)
    print(json.dumps(dict(phase=args.phase, arms=config["arms"], seeds=config["seeds"])), flush=True)


def active_config(args, config):
    """Arms removed by the clean quality gate get no regeneration or reads."""
    return dict(config, arms=lean_common.active_arms(args.out, config))


def start(args):
    args.out = args.out.resolve()
    lean = lean_common.load_lean()
    config = common.load_json(args.out / "config.json")
    args.max_hours = lean_common.hours_cap(lean, args.hourly_usd)
    instant = datetime.fromisoformat(args.instance_start_utc.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.timestamp() > time.time():
        raise ValueError("Instance start must be a past timezone-aware UTC instant")
    if list(args.out.glob("RESOURCE_STOP*.json")):
        raise common.ResourceStop("A resource stop already exists; the phase needs a person to review it")
    if not lean_common.disk_ok(lean, shutil.disk_usage(args.out).free):
        raise common.ResourceStop("Free disk is below the fixed floor; no output is deleted to make room")
    stage.install_deadline(args, config, instant)
    ready = common.load_json(args.assets / "f6l-setup-ready.json")
    if ready.get("status") != "complete" or ready.get("instance_start_utc") != instant.astimezone(timezone.utc).isoformat():
        raise ValueError("Lean setup receipt is missing or from another instance start")
    import encoder_transfer_runtime as rt
    import et_final_pilot as pilot
    base, specs = pilot.channel_specs()
    identity = common.runtime_identity(args.out / "config.json", STAGE_S_MANIFEST,
        [ROOT / "scripts" / name for name in CODE] + [lean_common.LEAN_CONFIG, ROOT / "research/encoder-transfer-20261019/stage2b-config.json"],
        [stage.resolve_repo(base["profile_file"])])
    identity.update(instance_start_utc=instant.astimezone(timezone.utc).isoformat(), hourly_usd=args.hourly_usd,
                    max_hours=args.max_hours, setup_receipt_sha256=common.sha256_file(args.assets / "f6l-setup-ready.json"))
    seal = args.out / "identity.json"
    if seal.exists():
        if common.load_json(seal) != identity:
            raise ValueError("Resume changed code, config, price or instance start")
    else:
        common.atomic_json(seal, identity)
    budget = common.Budget(args.max_hours * 3600, start_time=instant.timestamp(), clock=time.time,
                           reserve_seconds=lean["caps"]["retrieval_reserve_seconds"])
    config["_runtime_bounds"] = None
    return lean, config, base, specs, budget, rt


def prepare(args, lean, config, base, specs, budget, rt, torch):
    if config["lean"]["phase"] in ("stage3", "f7"):
        return stage.prepare(args, config, base, specs, budget, rt, torch)
    import tifs_stage_p as stage_p
    manifest = stage_p.load_manifest(STAGE_P_MANIFEST)
    rows = lean_common.partition_sources(lean, config["lean"]["phase"], manifest)
    records = {}
    for row in rows:
        sid = str(row["source_id"])
        path = stage.source_path(row, args.assets)
        if common.sha256_file(path) != row["canonical_png_sha256"]:
            raise ValueError("Canonical PNG hash mismatch: " + sid)
        records[sid] = {**row, "path": str(path)}
    sealed = dict(sources=records, donors=[str(r["source_id"]) for r in rows], targets=[], pairs=[], original_features={},
                  selection="committed Stage P tuning order; lean partition " + config["lean"]["phase"])
    seal = args.out / "prepared.json"
    if seal.exists() and common.load_json(seal) != sealed:
        raise ValueError("Prepared lean partition changed")
    common.atomic_json(seal, sealed)


def load_policy(args):
    # RUN_ROOT/stage1 or RUN_ROOT/stage3/screen: the probe folder is always RUN_ROOT/probe.
    root = args.out.parents[1] if args.phase == "stage3" else args.out.parent
    return common.load_json(root / "probe" / "policy.json")


def build_writer(args, lean, config, base, policy):
    import et_final_phase_a_attacks as attacks
    from f6l_writer import LeanWriter
    import torch
    frozen = common.load_json(BASE_CONFIG)
    policy = dict(policy, offload=lean_common.needs_offload(torch.cuda.mem_get_info()[1]))
    return LeanWriter(args.assets, base, frozen, settings=lean["writer"], policy=policy, metric=attacks.Quality(args.assets),
                      within_cushion=lambda metrics: lean_common.within_cushion(lean, metrics))


def clean(args, lean, config, base, specs, budget, rt, torch):
    p, donors, _ = stage.prepared(args)
    journal = common.Journal(args.out / "clean.jsonl")
    from encoder_transfer_test import message
    writer = internal = metric = None
    try:
        for arm in config["arms"]:
            spec = config["lean"]["arms"][arm]
            kind = spec["kind"]
            todo = [sid for sid in donors if not journal.done(f"clean:{sid}:{arm}")]
            if not todo:
                continue
            budget.require(stage.estimate(config, "load_" + kind, 300))
            loaded = time.monotonic()
            if kind == "lean":
                adapter = None
            elif kind in ("retained", "dual"):
                # One Internal serves every retained and dual arm of this invocation.
                internal = internal or rt.Internal(args.assets, base)
                adapter = internal
                if kind == "dual":
                    import et_final_phase_a_attacks as attacks
                    f7_dual.check_threshold(adapter.v5)
                    metric = metric or attacks.Quality(args.assets)
            elif kind == "vine-b":
                from tifs_vine_b import VineB
                adapter = VineB(args.assets, base, encoding=True)
            elif kind == "vine-r":
                adapter = rt.Vine(args.assets, encoding=True)
            else:
                adapter = None
            stage.model_ready(args, "load_" + kind, loaded, torch)
            for sid in todo:
                if kind == "lean" and (writer is None or writer._closed):
                    # A failed unit closes the writer. It stays terminal and later sources get a fresh one.
                    writer = build_writer(args, lean, config, base, load_policy(args))
                uid = f"clean:{sid}:{arm}"
                def work(sid=sid, uid=uid):
                    rgb = rt.load_rgb(p["sources"][sid]["path"])
                    payload = report = None
                    if kind == "unmarked":
                        marked = rgb
                    elif kind == "lean":
                        marked, payload, report = writer.embed_arm(rgb, spec, sid)
                    elif kind == "retained":
                        marked, payload, report = adapter.embed(rgb, arm)
                    elif kind == "dual":
                        marked, payload, report = f7_dual.embed(adapter, rgb, base, config["owners"]["positive"], metric=metric)
                    elif kind == "vine-b":
                        marked, payload, report = adapter.embed(rgb, config["owners"]["positive"])
                    else:
                        bits = message(sid, base["payload_bits"][arm], base["message_seed"])
                        marked = adapter.embed(rgb, bits)
                        payload = dict(bits=bits)
                    return dict(output=stage.output(args, rt, uid, marked), payload=payload, embedding_report=report)
                stage.execute_unit(args, config, budget, rt, torch, journal,
                    dict(id=uid, kind="clean", source=sid, source_id=sid, arm=arm, control="C0" if stage.c0(arm) else "C1"),
                    work, "clean_" + kind)
            adapter = None
            if kind not in ("retained", "dual"):
                rt.release()
    finally:
        if writer is not None:
            writer.close()
        writer = internal = metric = None
        rt.release()


def probe(args, lean, config, base, specs, budget, rt, torch):
    """Timing, memory and gradient agreement fix the writer policy before any mark is read."""
    p, donors, _ = stage.prepared(args)
    writer = build_writer(args, lean, config, base, dict(checkpoint=True))
    try:
        checks = [writer.validate_rehearsal(rt.load_rgb(p["sources"][donors[0]]["path"]), donors[0],
                                            variants=("f6-noise", "f6-x0", "f6-generic"))]
        common.atomic_json(args.out / "writer-checks.json", checks)
        measures = [writer.measure(rt.load_rgb(p["sources"][sid]["path"]), sid) for sid in donors]
    finally:
        writer.close()
        rt.release()
    common.atomic_json(args.out / "probe-measure.json", measures)
    policy = lean_common.decide_policy(lean["probe_rules"], measures)
    common.atomic_json(args.out / "policy.json", policy)
    print(json.dumps(dict(event="PROBE_POLICY", policy=policy)), flush=True)


def native(args, lean, config, base, specs, budget, rt, torch):
    stage.native(args, active_config(args, config), base, specs, budget, rt, torch)


def threats(args, lean, config, base, specs, budget, rt, torch):
    stage.threats(args, active_config(args, config), base, specs, budget, rt, torch)


def secondary(args, lean, config, base, specs, budget, rt, torch):
    stage.secondary(args, active_config(args, config), base, specs, budget, rt, torch)


def detect_dual(args, config, base, budget, rt, torch, method):
    """F7 reads its own marks and the shared C0 with both unchanged readers; the union is F7's reader."""
    from encoder_transfer_test import ALPHA, BETA
    rows = [r for r in read.items(args) if (r["arm"] == method or stage.c0(r["arm"])) and read.partition(r["id"], args.worker)]
    journal = common.Journal(read.shard_path(args, method))
    expected = [f"det:{method}:{r['id']}" for r in rows]
    pending = [r for r in rows if not journal.done(f"det:{method}:{r['id']}")]
    if pending:
        budget.require(stage.estimate(config, "load_reader", 300))
        loaded = time.monotonic()
        adapter = rt.Internal(args.assets, base)
        f7_dual.check_threshold(adapter.v5)
        stage.model_ready(args, "load_reader", loaded, torch)
        try:
            for item in pending:
                def work(item=item):
                    common.validate_output(item, args.out)
                    rgb = rt.load_rgb(item["output"]["path"])
                    payload = item.get("payload") if item["arm"] == method else None
                    features, latent = adapter.features(rgb, 7), adapter.reader.latent(rgb)
                    calls = {}
                    for owner in (ALPHA, BETA):
                        tick = time.monotonic()
                        raw = f7_dual.read(adapter, rgb, owner, features, latent)
                        calls[owner] = dict(status="ok", raw=f7_dual.summary_raw(raw), seconds=time.monotonic() - tick,
                                            endpoints=f7_dual.endpoints(raw, payload if owner == ALPHA else None))
                    modes = {"combined": calls[ALPHA]} if item["kind"] in ("T4", "T5") else {}
                    return dict(calls=calls, modes=modes, dispatch="f7-dual", input_sha256=item["output"]["sha256"],
                                artifact_required=False, payload_role="evaluator reference only")
                stage.execute_unit(args, config, budget, rt, torch, journal,
                    dict(id=f"det:{method}:{item['id']}", kind="detect", method=method, item=item["id"], arm=item["arm"],
                         source=item["source"], control=item["control"], producer_kind=item["kind"],
                         **{k: item[k] for k in ("cell", "family", "strength", "seed", "target", "condition", "transform") if k in item}),
                    work, "detect_" + method)
        finally:
            adapter = None
            rt.release()
    read.snapshot(args, journal, expected)


def detect(args, lean, config, base, specs, budget, rt, torch):
    """Every lean arm uses the exact F5 dispatch. F5 r2 reads the shared C0 once for all of them."""
    effective = active_config(args, config)
    lean_arms = tuple(a for a in effective["arms"] if config["lean"]["arms"][a]["kind"] == "lean")
    stage.NEW = (*stage.NEW, *lean_arms)
    all_items = read.items
    try:
        for method in [a for a in effective["arms"] if not stage.c0(a)]:
            args.method = method
            if config["lean"]["arms"][method]["kind"] == "dual":
                read.items = all_items
                detect_dual(args, effective, base, budget, rt, torch, method)
                continue
            read.items = (lambda a: [r for r in all_items(a) if not stage.c0(r["arm"])]) if method in lean_arms else all_items
            read.detect(args, effective, base, specs, budget, rt, torch)
    finally:
        read.items = all_items
        args.method = None


def quality(args, lean, config, base, specs, budget, rt, torch):
    read.quality(args, active_config(args, config), base, specs, budget, rt, torch)


STAGES = dict(prepare=prepare, clean=clean, probe=probe, native=native, threats=threats, secondary=secondary,
              detect=detect, quality=quality)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", required=True, choices=("plan", *STAGES))
    p.add_argument("--phase", required=True, choices=lean_common.PHASES)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--previous", type=Path)
    p.add_argument("--assets", type=Path)
    p.add_argument("--instance-start-utc")
    p.add_argument("--hourly-usd", type=float)
    p.add_argument("--rehearsal", action="store_true")
    p.add_argument("--family", choices=("K3", "R0", "R1"))
    p.add_argument("--worker", default="")
    p.add_argument("--threads", type=int, default=4)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.stage == "plan":
        return plan(args)
    args.method = None
    args.out = args.out.resolve()
    with stage.Invocation(args):
        torch = stage.environment_guard()
        torch.set_num_threads(args.threads)
        try:
            lean, config, base, specs, budget, rt = start(args)
            STAGES[args.stage](args, lean, config, base, specs, budget, rt, torch)
        except common.ResourceStop as exc:
            common.atomic_json(args.out / f"RESOURCE_STOP-{args.stage}{'-' + args.worker.replace('/', '-of-') if args.worker else ''}.json",
                               dict(status="RESOURCE_STOP", reason=str(exc), stage=args.stage))
            raise SystemExit(3)
        except torch.cuda.OutOfMemoryError:
            common.atomic_json(args.out / f"RESOURCE_STOP-{args.stage}.json",
                               dict(status="RESOURCE_STOP", reason="CUDA OOM outside a unit", stage=args.stage, error=traceback.format_exc()))
            raise SystemExit(3)
        # A failed unit stays terminal. Exit 4 lets the driver finish the fixed inventory and know about it.
        if args.stage in ("clean", "native", "threats", "secondary"):
            paths = [args.out / (args.stage + ".jsonl")]
        elif args.stage in ("detect", "quality"):
            suffix = "-" + args.worker.replace("/", "-of-") if args.worker else ""
            paths = list(args.out.glob(f"{args.stage}-*{suffix}.jsonl"))
        else:
            paths = []
        for path in paths:
            if any(row.get("status") == "error_terminal" for row in common.Journal(path, read_only=True).latest.values()):
                raise SystemExit(4)


if __name__ == "__main__":
    main()
