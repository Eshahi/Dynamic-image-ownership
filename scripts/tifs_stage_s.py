"""Server-only Stage S producer. No acquisition, hidden data, or laptop execution.

All science imports are behind the Linux/CUDA environment guard. Every artifact
is hashed before its terminal journal row. A single producer owns each journal.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tifs_common as common

C0 = "unmarked"
NEW = ("f6-noise", "f6-codec", "f6-generic")
TRANSFORMS = ("jpeg90", "jpeg50", "resize384", "crop90", "noise002", "blur1", "brightness12", "contrast12")


def environment_guard():
    readiness = common.load_json(ROOT / "research/tifs-20261028/stage-s/READINESS.json")
    if readiness.get("status") != "COMPLETE":
        raise RuntimeError("Stage S package is INCOMPLETE. See research/tifs-20261028/FINAL-REPORT.md; do not run science or rent compute for this snapshot.")
    if platform.system() != "Linux" or Path("/mnt/c/Users").exists():
        raise RuntimeError("Stage S science requires the rented Linux CUDA server; laptop execution prohibited")
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA server required")
    return torch


def resolve_repo(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def manifest_path(config):
    value = config.get("source_manifest", "research/tifs-20261028/stage-s/source-manifest.json")
    return resolve_repo(value["path"] if isinstance(value, dict) else value)


def c0(arm):
    return arm in ("C0", "unmarked", "c0")


def start(args):
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    config = common.load_json(args.config)
    if args.stage != "manifest" and list(args.out.glob("RESOURCE_STOP*.json")):
        raise common.ResourceStop("A resource stop already exists; intact run requires user review")
    if common.sha256_file(manifest_path(config)) != config["source_manifest_sha256"]:
        raise ValueError("Frozen source manifest digest mismatch")
    if args.max_hours > 15 or args.max_hours <= 0 or not .45 <= args.hourly_usd <= .60:
        raise ValueError("Stage S ceiling is 15 hours at USD .45-.60/hour")
    instant = datetime.fromisoformat(args.instance_start_utc.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.timestamp() > time.time():
        raise ValueError("Instance start must be a past timezone-aware UTC instant")
    import encoder_transfer_runtime as rt
    import et_final_pilot as pilot
    base, specs = pilot.channel_specs()
    identity = common.runtime_identity(args.config, manifest_path(config),
        [ROOT / "scripts" / f for f in ("tifs_common.py", "tifs_stage_s.py", "tifs_stage_s_read.py", "tifs_writer.py",
         "encoder_transfer_runtime.py", "encoder_transfer_test.py", "et_final_pilot.py", "et_final_phase_a.py", "et_final_phase_a_attacks.py",
         "f5_latent_codec.py", "revised_watermark_v5.py", "f5_gate.py", "three_threat_models.py", "journal_vae_probe.py")]
         + [ROOT / "research/encoder-transfer-20261019/stage2b-config.json"],
        [resolve_repo(base["profile_file"])])
    identity["packages"] = {name: importlib.metadata.version(name) for name in ("torch","diffusers","transformers","numpy","Pillow","lpips")}
    identity.update(instance_start_utc=instant.astimezone(timezone.utc).isoformat(), max_hours=args.max_hours,
                    hourly_usd=args.hourly_usd, rehearsal=args.rehearsal)
    seal = args.out / "identity.json"
    if seal.exists():
        if common.load_json(seal) != identity:
            raise ValueError("Resume identity/config/code/profile/source/start/price mismatch")
    else:
        common.atomic_json(seal, identity)
    # Epoch clock carries all previous stages, idle time and resumes.
    budget = common.Budget(args.max_hours * 3600, start_time=instant.timestamp(), clock=time.time,
                           reserve_seconds=config.get("budget", {}).get("retrieval_reserve_seconds", 1800))
    for name in ("clean", "native", "threats", "secondary", "rehearsal-checks"):
        for row in common.Journal(args.out / (name + ".jsonl"), read_only=args.stage in ("detect","quality")).latest.values():
            if row.get("status") == "ok":
                common.validate_output(row, args.out)
            elif row.get("tape"):
                common.validate_output({"status": "ok", "output": row["tape"]}, args.out)
    return config, base, specs, budget, rt


def telemetry(torch):
    free, total = torch.cuda.mem_get_info()
    return dict(device_total_bytes=total, device_free_bytes=free, device_used_bytes=total-free,
                allocated_bytes=torch.cuda.memory_allocated(), reserved_bytes=torch.cuda.memory_reserved(),
                max_allocated_bytes=torch.cuda.max_memory_allocated(), max_reserved_bytes=torch.cuda.max_memory_reserved())


def estimate(config, label, fallback=600):
    return config.get("budget", {}).get("unit_estimates_seconds", {}).get(label, fallback)


def prepared(args):
    p = common.load_json(args.out / "prepared.json")
    return p, p["donors"], p["targets"]


def source_path(row, assets):
    for key in ("canonical_path", "canonical_png_path", "path"):
        if key in row:
            return resolve_repo(row[key])
    return assets / "sources" / (str(row["source_id"])+".png")


def prepare(args, config, base, specs, budget, rt, torch):
    seal = args.out / "prepared.json"
    if seal.exists():
        for row in common.load_json(seal)["sources"].values():
            if common.sha256_file(row["path"]) != row["canonical_png_sha256"]:
                raise ValueError("Prepared original hash changed")
        return
    manifest = common.load_json(manifest_path(config))
    common.validate_sources(manifest)
    prefix = "rehearsal" if args.rehearsal else "screen"
    donors, targets = manifest[prefix + "_donors"], manifest[prefix + "_targets"]
    import three_threat_models as models
    from a6_clip_visual import load_visual_encoder
    from f5_gate import semantic_feature
    clip, transform = load_visual_encoder(args.assets / "a6/clip/ViT-B-32.pt", device="cpu")
    records, features = {}, {}
    for row in [*donors, *targets]:
        budget.require(estimate(config, "prepare", 120))
        sid, path = str(row["source_id"]), source_path(row, args.assets)
        if common.sha256_file(path) != row["canonical_png_sha256"]:
            raise ValueError("Canonical PNG hash mismatch: " + sid)
        rgb = rt.load_rgb(path)
        if hashlib.sha256(rgb.tobytes()).hexdigest() != row["rgb8_sha256"]:
            raise ValueError("Canonical RGB8 pixel hash mismatch: " + sid)
        v = [float(x) for x in semantic_feature(models, clip, transform, rgb, 7)]
        norm = math.sqrt(sum(x*x for x in v))
        if norm <= 0:
            raise ValueError("Zero semantic feature")
        features[sid] = [x/norm for x in v]
        records[sid] = {**row, "path": str(path)}
    available = {str(t["source_id"]) for t in targets}
    pairs = []
    for donor in donors:
        sid = str(donor["source_id"])
        scored = [(sum(a*b for a,b in zip(features[sid], features[t])), t) for t in sorted(available)]
        similarity, target = sorted(scored, key=lambda x: (-x[0], int(x[1])))[0]
        available.remove(target)
        pairs.append(dict(donor=sid, target=target, cosine=similarity, distinctness="human_label_missing"))
    common.atomic_json(seal, dict(sources=records, donors=[str(r["source_id"]) for r in donors],
        targets=[str(r["source_id"]) for r in targets], pairs=pairs, original_features=features,
        selection="original-only seven-view CPU CLIP greedy maximum cosine; donor order fixed; target ID tie-break"))
    del clip, transform


def output(args, rt, uid, rgb):
    return rt.save_rgb(args.out / "images" / (hashlib.sha256(uid.encode()).hexdigest() + ".png"), rgb)


def execute_unit(args, config, budget, rt, torch, journal, row, fn, label):
    if journal.done(row["id"]):
        return
    budget.require(estimate(config, label))
    tick = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    try:
        row.update(fn())
        row["status"] = "ok"
    except torch.cuda.OutOfMemoryError:
        row.update(status="resource_stop", error=traceback.format_exc())
        row["seconds"] = time.monotonic()-tick
        row["memory"] = telemetry(torch)
        journal.append(row)
        raise common.ResourceStop("CUDA OOM: serial design does not fit; no reduced run or retry")
    except Exception as exc:
        row.update(status="safety_blocked" if str(exc) == "safety_checker_blocked_output" else "error_terminal",
                   error=traceback.format_exc())
    row["seconds"] = time.monotonic()-tick
    row["memory"] = telemetry(torch)
    journal.append(row)
    print(json.dumps(dict(event="UNIT_DONE", id=row["id"], status=row["status"], seconds=row["seconds"], memory=row["memory"])), flush=True)


def clean(args, config, base, specs, budget, rt, torch):
    p, donors, _ = prepared(args)
    journal = common.Journal(args.out / "clean.jsonl")
    from encoder_transfer_test import message
    for arm in config["arms"]:
        todo = [s for s in donors if not journal.done(f"clean:{s}:{arm}")]
        if not todo:
            continue
        budget.require(estimate(config, "load_" + arm, 900))
        loadtick=time.monotonic()
        if arm in NEW:
            from tifs_writer import F6Writer
            adapter = F6Writer(args.assets, base, config)
        else:
            adapter = None if c0(arm) else rt.Internal(args.assets, base) if arm in ("f5-r2", "v5-r3") else rt.Wam(args.assets) if arm == "wam" else rt.Vine(args.assets, encoding=True)
        print(json.dumps(dict(event="MODEL_READY",arm=arm,load_seconds=time.monotonic()-loadtick,memory=telemetry(torch))),flush=True)
        try:
            for sid in todo:
                if args.rehearsal and arm in NEW:
                    checkj=common.Journal(args.out / "rehearsal-checks.jsonl")
                    checkid="writer-check:"+sid
                    def check():
                        receipt=adapter.validate_rehearsal(rt.load_rgb(p["sources"][sid]["path"]),sid)
                        cp=args.out/"rehearsal-checks"/(sid+".json")
                        common.atomic_json(cp,receipt)
                        return dict(output=dict(path=str(cp),sha256=common.sha256_file(cp)))
                    execute_unit(args,config,budget,rt,torch,checkj,dict(id=checkid,kind="writer-rehearsal",source=sid),check,"writer_rehearsal")
                    if checkj.latest[checkid].get("status")!="ok":
                        raise RuntimeError("Writer rehearsal gradient/projection validation failed; cannot mark")
                uid = f"clean:{sid}:{arm}"
                def work(sid=sid, uid=uid):
                    rgb = rt.load_rgb(p["sources"][sid]["path"])
                    payload, report = None, None
                    if c0(arm):
                        marked = rgb
                    elif arm in NEW:
                        marked, payload, report = adapter.embed(rgb, arm, sid)
                    elif arm in ("f5-r2", "v5-r3"):
                        marked, payload, report = adapter.embed(rgb, arm)
                    else:
                        bits = message(sid, base["payload_bits"][arm], base["message_seed"])
                        marked = adapter.embed(rgb, bits)
                        payload = dict(bits=bits)
                    return dict(output=output(args, rt, uid, marked), payload=payload, embedding_report=report)
                execute_unit(args, config, budget, rt, torch, journal,
                    dict(id=uid, kind="clean", source=sid, source_id=sid, arm=arm, control="C0" if c0(arm) else "C1"), work, "clean_"+arm)
        finally:
            if arm in NEW:
                adapter.close()
            adapter = None
            rt.release()


def cells(config):
    return config["cells"]


def native(args, config, base, specs, budget, rt, torch):
    import et_final_pilot as pilot
    import et_final_phase_a as pa
    _, donors, _ = prepared(args)
    cleanj = common.Journal(args.out / "clean.jsonl")
    journal = common.Journal(args.out / "native.jsonl")
    unmarked = next(a for a in config["arms"] if c0(a))
    for family in ("K3", "R0", "R1"):
        if args.family and args.family != family:
            continue
        selected = [c for c in cells(config) if c["family"] == family]
        expected = [f"native:{c['id']}:{s}:{seed}:{a}" for c in selected for s in donors for seed in config["seeds"] for a in config["arms"]]
        if all(journal.done(uid) for uid in expected):
            continue
        budget.require(estimate(config, "load_"+family, 900))
        loadtick=time.monotonic()
        regen = rt.Regenerator(args.assets, specs[family])
        modules = [regen.pipe.unet, regen.pipe.movq if family == "K3" else regen.pipe.vae]
        common.atomic_json(args.out / (family + "-ready.json"), dict(ready=True, memory=telemetry(torch), concurrency_authorized=False))
        print(json.dumps(dict(event="MODEL_READY",family=family,load_seconds=time.monotonic()-loadtick,memory=telemetry(torch))),flush=True)
        try:
            with pilot.ClassicAttention(*modules):
                for cell in selected:
                    for sid in donors:
                        for seed in config["seeds"]:
                            controlid = f"native:{cell['id']}:{sid}:{seed}:{unmarked}"
                            for arm in [unmarked, *[a for a in config["arms"] if a != unmarked]]:
                                uid = f"native:{cell['id']}:{sid}:{seed}:{arm}"
                                def work(arm=arm, uid=uid):
                                    cr = cleanj.latest.get(f"clean:{sid}:{arm}", {})
                                    if cr.get("status") != "ok":
                                        raise RuntimeError("clean dependency unavailable")
                                    rgb = rt.load_rgb(cr["output"]["path"])
                                    tape = pilot.Tape()
                                    if arm == unmarked:
                                        try:
                                            generated = pa.run_native(family, regen, rgb, cell["strength"], seed, tape.record())
                                        finally:
                                            if tape.draws:
                                                tp = args.out / "tapes" / (hashlib.sha256(controlid.encode()).hexdigest()+".pt")
                                                tp.parent.mkdir(parents=True, exist_ok=True)
                                                torch.save([d.cpu() for d in tape.draws], tp)
                                                row["tape"] = dict(path=str(tp), sha256=common.sha256_file(tp))
                                                row["tape_receipt"] = tape.receipt()
                                    else:
                                        control = journal.latest.get(controlid, {})
                                        if not control.get("tape"):
                                            raise RuntimeError("C0 noise tape unavailable; missing outcome retained")
                                        common.validate_output({"status":"ok", "output":control["tape"]}, args.out)
                                        tape.draws = [d.cuda() for d in torch.load(control["tape"]["path"], weights_only=True)]
                                        generated = pa.run_native(family, regen, rgb, cell["strength"], seed, tape.replay())
                                        if tape.cursor != len(tape.draws):
                                            raise RuntimeError("Native noise tape not fully consumed")
                                    return dict(output=output(args, rt, uid, generated), payload=cr.get("payload"), input=cr["output"])
                                row = dict(id=uid, kind="native", source=sid, arm=arm, cell=cell["id"], family=family,
                                    strength=cell["strength"], seed=seed, control="C0" if c0(arm) else "C1")
                                execute_unit(args, config, budget, rt, torch, journal, row, work, "native_"+family)
        finally:
            modules = regen = None
            rt.release()


def threats(args, config, base, specs, budget, rt, torch):
    import numpy as np
    p, _, _ = prepared(args)
    cleanj = common.Journal(args.out / "clean.jsonl")
    journal = common.Journal(args.out / "threats.jsonl")
    conditions = ("patch128", "patch256", "patch128-sham", "patch256-sham", "residual0.5", "residual1.0", "unmodified")
    for pair in p["pairs"]:
        donor, target = pair["donor"], pair["target"]
        for arm in config["arms"]:
            for condition in conditions:
                kind = "T5" if condition == "unmodified" else "T4"
                uid = f"threat:{kind}:{donor}:{target}:{arm}:{condition}"
                def work():
                    cr = cleanj.latest.get(f"clean:{donor}:{arm}", {})
                    if cr.get("status") != "ok":
                        raise RuntimeError("donor clean dependency unavailable")
                    donor_rgb = rt.load_rgb(cr["output"]["path"])
                    original = rt.load_rgb(p["sources"][donor]["path"])
                    recipient = rt.load_rgb(p["sources"][target]["path"])
                    marked = recipient.copy()
                    if condition.startswith("patch"):
                        width = int(condition[5:8]); lo = (512-width)//2; hi = lo+width
                        marked[lo:hi, lo:hi] = (original if condition.endswith("-sham") else donor_rgb)[lo:hi, lo:hi]
                    elif condition.startswith("residual"):
                        scale = .5 if condition == "residual0.5" else 1.
                        marked = np.floor(np.clip(recipient.astype(np.float64)+scale*(donor_rgb.astype(np.float64)-original), 0, 255)+.5).astype(np.uint8)
                    return dict(output=output(args, rt, uid, marked), payload=cr.get("payload"),
                        recipient=target, donor=donor, reference=dict(path=p["sources"][target]["path"], sha256=p["sources"][target]["canonical_png_sha256"]),
                        access="known-clean residual diagnostic" if condition.startswith("residual") else "published-images nonadaptive",
                        distinctness=pair["distinctness"])
                execute_unit(args, config, budget, rt, torch, journal,
                    dict(id=uid, kind=kind, source=donor, target=target, donor=donor, arm=arm, condition=condition, control="C0" if c0(arm) else "C1"), work, "threat",)


def transform(rgb, name, seed):
    import io
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    image = Image.fromarray(rgb)
    if name.startswith("jpeg"):
        stream = io.BytesIO(); image.save(stream, format="JPEG", quality=int(name[4:]), subsampling=2)
        stream.seek(0); image = Image.open(stream).convert("RGB")
    elif name == "resize384":
        image = image.resize((384,384), Image.Resampling.LANCZOS).resize((512,512), Image.Resampling.LANCZOS)
    elif name == "crop90":
        side = math.floor(512*math.sqrt(.9)); lo = (512-side)//2
        image = image.crop((lo,lo,lo+side,lo+side)).resize((512,512), Image.Resampling.LANCZOS)
    elif name == "noise002":
        rng = np.random.default_rng(seed)
        return np.floor(np.clip(rgb.astype(np.float64)/255+rng.normal(0,.02,rgb.shape),0,1)*255+.5).astype(np.uint8)
    elif name == "blur1":
        image = image.filter(ImageFilter.GaussianBlur(1))
    elif name == "brightness12":
        image = ImageEnhance.Brightness(image).enhance(1.2)
    elif name == "contrast12":
        image = ImageEnhance.Contrast(image).enhance(1.2)
    else:
        raise ValueError("Unknown frozen secondary transform: "+name)
    return np.asarray(image, dtype=np.uint8).copy()


def secondary(args, config, base, specs, budget, rt, torch):
    _, donors, _ = prepared(args)
    cleanj = common.Journal(args.out / "clean.jsonl")
    journal = common.Journal(args.out / "secondary.jsonl")
    for sid in donors:
        for arm in config["arms"]:
            for name in TRANSFORMS:
                uid = f"secondary:{name}:{sid}:{arm}"
                def work():
                    cr = cleanj.latest.get(f"clean:{sid}:{arm}", {})
                    if cr.get("status") != "ok":
                        raise RuntimeError("clean dependency unavailable")
                    p, _, _ = prepared(args)
                    generated = transform(rt.load_rgb(cr["output"]["path"]), name, common.stable_seed("secondary-noise",p["sources"][sid]["source_uid"]))
                    return dict(output=output(args, rt, uid, generated), payload=cr.get("payload"), input=cr["output"])
                execute_unit(args, config, budget, rt, torch, journal,
                    dict(id=uid, kind="secondary", source=sid, arm=arm, transform=name, control="C0" if c0(arm) else "C1"), work, "secondary")


def expected_ids(config, p):
    donors = p["donors"]
    result = dict(clean=[f"clean:{s}:{a}" for s in donors for a in config["arms"]],
        native=[f"native:{c['id']}:{s}:{seed}:{a}" for c in cells(config) for s in donors for seed in config["seeds"] for a in config["arms"]],
        secondary=[f"secondary:{t}:{s}:{a}" for t in TRANSFORMS for s in donors for a in config["arms"]])
    result["threats"] = [f"threat:{'T5' if t=='unmodified' else 'T4'}:{pair['donor']}:{pair['target']}:{a}:{t}"
        for pair in p["pairs"] for a in config["arms"] for t in ("patch128","patch256","patch128-sham","patch256-sham","residual0.5","residual1.0","unmodified")]
    return result


def seal_manifest(args, config, *unused):
    p, _, _ = prepared(args)
    report = dict(stages={}, status="complete", journals={})
    for stage, expected in expected_ids(config,p).items():
        path = args.out / (stage+".jsonl")
        rows = common.Journal(path).latest
        missing = [uid for uid in expected if uid not in rows or rows[uid].get("status") != "ok"]
        for row in rows.values():
            if row.get("status") == "ok": common.validate_output(row,args.out)
            elif row.get("tape"): common.validate_output({"status":"ok","output":row["tape"]},args.out)
        report["stages"][stage] = dict(expected=len(expected), observed=len(rows), unresolved=missing)
        if missing: report["status"]="incomplete"
        if path.exists(): report["journals"][stage]=common.sha256_file(path)
    common.atomic_json(args.out / "producer-manifest.json", report)
    if report["status"] != "complete":
        raise RuntimeError("INCOMPLETE: producer inventory contains missing/blocked/error outcomes")


def parser(stages):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", required=True, choices=stages)
    p.add_argument("--assets", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--config", type=Path, default=ROOT/"research/tifs-20261028/stage-s/frozen-config.json")
    p.add_argument("--rehearsal", action="store_true")
    p.add_argument("--family", choices=("K3","R0","R1"))
    p.add_argument("--instance-start-utc", required=True)
    p.add_argument("--max-hours", type=float, default=15)
    p.add_argument("--hourly-usd", type=float, required=True)
    return p


def main():
    args = parser(("prepare","clean","native","threats","secondary","manifest")).parse_args()
    stage_tick=time.monotonic()
    torch = environment_guard()
    values = start(args)
    print(json.dumps(dict(event="STAGE_START",stage=args.stage,memory=telemetry(torch))),flush=True)
    try:
        dict(prepare=prepare,clean=clean,native=native,threats=threats,secondary=secondary,manifest=seal_manifest)[args.stage](args,*values[:4],values[4],torch)
    except common.ResourceStop as exc:
        common.atomic_json(args.out / "RESOURCE_STOP.json",dict(status="RESOURCE_STOP",reason=str(exc),stage=args.stage,memory=telemetry(torch)))
        raise SystemExit(3)
    except torch.cuda.OutOfMemoryError:
        common.atomic_json(args.out / "RESOURCE_STOP.json",dict(status="RESOURCE_STOP",reason="CUDA OOM during model load/stage",stage=args.stage,memory=telemetry(torch),error=traceback.format_exc()))
        raise SystemExit(3)
    if args.stage in ("clean","native","threats","secondary"):
        p,_,_=prepared(args)
        expected=expected_ids(values[0],p)[args.stage]
        if args.stage=="native" and args.family:
            cellids={c["id"] for c in values[0]["cells"] if c["family"]==args.family}
            expected=[uid for uid in expected if uid.split(":")[1] in cellids]
        rows=common.Journal(args.out/(args.stage+".jsonl")).latest
        missing=[uid for uid in expected if rows.get(uid,{}).get("status")!="ok"]
        if missing:
            common.atomic_json(args.out/(args.stage+("-"+args.family if args.family else "")+"-incomplete.json"),dict(status="INCOMPLETE",unresolved=missing))
            raise SystemExit(4)
    elapsed=time.monotonic()-stage_tick
    count=len(common.Journal(args.out/(args.stage+".jsonl")).latest) if args.stage in ("clean","native","threats","secondary") else None
    print(json.dumps(dict(event="STAGE_DONE",stage=args.stage,seconds=elapsed,terminal_count=count,
        units_per_second=count/elapsed if count is not None else None,memory=telemetry(torch))),flush=True)


if __name__ == "__main__":
    main()
