"""Pure-stdlib conservative full-inventory forecast; no scientific imports."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as common
import tifs_stage_s as stage
import tifs_gate_profiles as profiles


def finite(value):
    return type(value) in (int,float) and math.isfinite(value) and value >= 0


def calculate(elapsed, one_time, variable, ceiling=54000, reserve=3600):
    if not all(finite(x) for x in (elapsed,one_time,variable,ceiling,reserve)):
        raise ValueError("Finite nonnegative timing required")
    total=elapsed+one_time+1.5*variable+reserve
    return dict(status="GO" if total <= ceiling else "RESOURCE_STOP", elapsed_instance_seconds=elapsed,
                measured_one_time_seconds=one_time, full_variable_seconds=variable,
                factor=1.5, retrieval_reserve_seconds=reserve, forecast_seconds=total, ceiling_seconds=ceiling)


GPU_MARGIN_BYTES = 1536 * 1024**2  # 1.5 GiB, independent of advertised card class.
MINIMUM_GPU_BYTES = 24_000_000_000  # 24 GB class minimum; not a tested-fit claim.


def capacity(rehearsal_bytes, ratio, free_bytes, total_bytes, peak_device_bytes, device_total_bytes):
    """Keep 20% disk free and 1.5 GiB below measured device capacity."""
    if not all(finite(x) for x in (rehearsal_bytes, ratio, free_bytes, total_bytes, peak_device_bytes, device_total_bytes)):
        raise ValueError("Invalid capacity measurement")
    if not total_bytes or ratio < 1 or not peak_device_bytes:
        raise ValueError("Missing capacity measurement")
    projected = 1.5 * rehearsal_bytes * ratio
    disk_ok = projected + .2 * total_bytes <= free_bytes
    gpu_limit = device_total_bytes - GPU_MARGIN_BYTES
    gpu_ok = device_total_bytes >= MINIMUM_GPU_BYTES and peak_device_bytes <= gpu_limit
    return dict(status="GO" if disk_ok and gpu_ok else "RESOURCE_STOP",
                rehearsal_bytes=rehearsal_bytes, full_artifact_bytes_with_margin=projected,
                free_bytes=free_bytes, total_bytes=total_bytes, disk_ok=disk_ok,
                peak_device_bytes=peak_device_bytes, device_total_bytes=device_total_bytes,
                gpu_margin_bytes=GPU_MARGIN_BYTES, gpu_limit_bytes=gpu_limit,
                gpu_ok=gpu_ok, minimum_gpu_bytes=MINIMUM_GPU_BYTES,
                gpu_policy="measured-total-minus-1.5GiB-v1")


def measured_device_total(memory_rows):
    """Fail closed on missing telemetry or mixed-device rehearsal receipts."""
    totals = [row.get("device_total_bytes") for row in memory_rows]
    if not totals or any(not finite(value) or value <= 0 for value in totals):
        raise ValueError("Missing measured GPU total capacity")
    if len(set(totals)) != 1:
        raise ValueError("Rehearsal GPU total capacity changed")
    return totals[0]


def measured_peak(memory):
    """Allocator high-water plus non-allocator device use, including load peaks."""
    keys = ("device_used_bytes", "reserved_bytes", "max_reserved_bytes")
    if any(not finite(memory.get(k)) for k in keys):
        raise ValueError("Missing device/allocator memory telemetry")
    return max(memory["device_used_bytes"],
               max(0, memory["device_used_bytes"] - memory["reserved_bytes"]) + memory["max_reserved_bytes"])


def timings(path):
    result=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        try: row=json.loads(line)
        except json.JSONDecodeError: continue
        if row.get("event")=="STAGE_DONE": result.append(row)
    if not result or not finite(result[-1].get("seconds")) or result[-1]["seconds"] <= 0:
        raise ValueError("Missing valid measured STAGE_DONE: "+str(path))
    return max(row["seconds"] for row in result if finite(row.get("seconds")))


def invocation_measurements(path, now, rows):
    """Cumulative invocation overhead survives partial runs and resumed journals.

    An invocation killed without a final receipt is charged through the next
    start (or now). Actual paid elapsed time independently includes all idle,
    setup and interrupted work; no timing is subtracted from that clock.
    """
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A hard kill may leave one partial append; the paid clock still
            # charges its time and an unmatched START is bounded below.
            continue
    starts = [r for r in events if r.get("event") == "INVOCATION_START"]
    ends = {r["invocation"]: r for r in events if r.get("event") == "INVOCATION_END"}
    if not starts:
        raise ValueError("Missing invocation timing receipts")
    start_ids = {r.get("invocation") for r in starts}
    if None in start_ids or len(start_ids) != len(starts):
        raise ValueError("Missing or duplicate invocation timing identity")
    units = {}
    bounds = {}
    for row in rows:
        duration = row.get("seconds")
        if not finite(duration) or duration <= 0 or not row.get("operation") or row.get("invocation") not in start_ids:
            raise ValueError("Missing measured operation timing/identity")
        units[row["invocation"]] = units.get(row["invocation"], 0) + duration
        label = row["operation"]
        bounds[label] = max(bounds.get(label, 0), 1.5 * duration)
    loads = {}
    for row in events:
        if row.get("event") == "MODEL_READY":
            value = row.get("load_seconds")
            if not finite(value) or value <= 0 or row.get("invocation") not in start_ids:
                raise ValueError("Missing measured model-load time")
            loads[row["label"]] = max(loads.get(row["label"], 0), value)
    overhead = 0
    prepare_seconds = 0
    for index, start in enumerate(starts):
        end = ends.get(start["invocation"])
        duration = end["seconds"] if end else max(0, (starts[index+1]["epoch"] if index+1 < len(starts) else now) - start["epoch"])
        if not finite(duration):
            raise ValueError("Invalid invocation duration")
        if start["stage"] == "prepare":
            prepare_seconds += duration
            bounds["prepare"] = max(bounds.get("prepare", 0), 1.5 * duration)
        else:
            overhead += max(0, duration - units.get(start["invocation"], 0))
    bounds.update({label: 1.5 * value for label, value in loads.items()})
    # Full-screen projection reserves all observed invocation overhead and an
    # additional full set of worst measured model loads, conservatively.
    return prepare_seconds, overhead + 1.5 * sum(loads.values()), bounds


def forecast(out, config, instance_start, now, *, receipt_path=None, selection_path=None):
    out=Path(out)
    if list(out.glob("RESOURCE_STOP*.json")):
        return dict(status="RESOURCE_STOP",reason="Rehearsal resource stop retained")
    identity=common.load_json(out/"identity.json")
    instant=datetime.fromisoformat(instance_start.replace("Z","+00:00"))
    if instant.tzinfo is None or instant.timestamp()>now:
        raise ValueError("Actual instance start must be past and timezone-aware")
    canonical=instant.astimezone(timezone.utc).isoformat()
    if identity.get("instance_start_utc") != canonical or identity.get("rehearsal") is not True:
        raise ValueError("Rehearsal identity/start mismatch")
    if identity.get("config_sha256") != common.sha256_file(config):
        raise ValueError("Rehearsal config mismatch")
    for path, digest in {**identity.get("code", {}), **identity.get("profiles", {})}.items():
        if common.sha256_file(path)!=digest:
            raise ValueError("Rehearsal code changed: "+path)
    config=profiles.load_execution_config(config, receipt_path=receipt_path, selection_path=selection_path)
    import tifs_stage_p as stage_p
    if identity.get("effective_config_sha256") != stage_p.digest(config):
        raise ValueError("Rehearsal effective profile/selection/choice mismatch")
    hours = identity.get("max_hours")
    if not finite(hours) or hours <= 0 or hours > config["budget"]["max_instance_hours"]:
        raise ValueError("Rehearsal hour ceiling exceeds the prospectively chosen cap")
    manifest=common.load_json(stage.manifest_path(config))
    if common.sha256_file(stage.manifest_path(config))!=identity["source_manifest_sha256"]:
        raise ValueError("Rehearsal source manifest mismatch")
    p=common.load_json(out/"prepared.json")
    if p["donors"] != [str(r["source_id"]) for r in manifest["rehearsal_donors"]] or p["targets"] != [str(r["source_id"]) for r in manifest["rehearsal_targets"]]:
        raise ValueError("Rehearsal must use exactly the two frozen donors and targets")
    if len(p["pairs"])!=2 or {r["donor"] for r in p["pairs"]}!=set(p["donors"]) or {r["target"] for r in p["pairs"]}!=set(p["targets"]):
        raise ValueError("Missing complete sealed rehearsal pairs")
    expected=stage.expected_ids(config,p)
    groups={}
    for name, ids in expected.items():
        rows=common.Journal(out/(name+".jsonl"),read_only=True).latest
        if set(rows)!=set(ids) or any(rows[uid].get("status")!="ok" for uid in ids):
            raise ValueError("Incomplete/failed rehearsal inventory: "+name)
        for row in rows.values(): common.validate_output(row,out)
        groups[name]=rows
    checks=common.Journal(out/"rehearsal-checks.jsonl",read_only=True).latest
    for sid in p["donors"]:
        row=checks.get("writer-check:"+sid,{})
        if row.get("status")!="ok": raise ValueError("Missing writer gradient/projection checks")
        common.validate_output(row,out)
        receipt=common.load_json(row["output"]["path"])
        gradient = receipt.get("clean_input_gradient_norm")
        if receipt.get("status")!="ok" or not receipt.get("gradient_checks") or not finite(gradient) or gradient <= 0:
            raise ValueError("Invalid writer gradient receipt")
    for row in groups["native"].values():
        if stage.c0(row["arm"]) and row.get("native_parity",{}).get("exact_rgb8") is not True:
            raise ValueError("Missing exact native capture/replay parity")
        if (stage.c0(row["arm"]) and row["family"] in ("R0", "R1")
                and row["seed"] == config["seeds"][0]):
            parity = row.get("x0_native_first_step_parity", {})
            if parity.get("status") != "ok" or parity.get("exact_conditioning") is not True:
                raise ValueError("Missing x0 native first-step conditioning/epsilon parity")
    producers=[r for rows in groups.values() for r in rows.values()]
    for method in (a for a in config["arms"] if not stage.c0(a)):
        name="detect-"+method
        rows=common.Journal(out/(name+"-0-of-1.jsonl"),read_only=True).latest
        ids={"det:"+method+":"+r["id"] for r in producers if r["arm"]==method or stage.c0(r["arm"])}
        if set(rows)!=ids or any(r.get("status")!="ok" for r in rows.values()):
            raise ValueError("Incomplete/failed rehearsal reader: "+method)
        groups[name]=rows
    rows=common.Journal(out/"quality-0-of-1.jsonl",read_only=True).latest
    if set(rows)!={"quality:"+r["id"] for r in producers} or any(r.get("status")!="ok" for r in rows.values()):
        raise ValueError("Incomplete/failed rehearsal quality")
    groups["quality"]=rows
    measured_rows = [r for group in groups.values() for r in group.values()]
    # Retain failed/retried row costs in the invocation receipts. The current
    # successful rows alone define full-screen operation bounds.
    variable, overhead, bounds = invocation_measurements(out/"invocations.jsonl", now, measured_rows)
    variable += sum(r["seconds"] for r in measured_rows)
    ratio=config["screen_n"]/config["rehearsal_n"]
    result=calculate(now-instant.timestamp(),overhead,variable*ratio,
        identity["max_hours"]*3600,config["budget"]["retrieval_reserve_seconds"])
    result.update(schema="tifs-stage-s-forecast-v1", config_sha256=identity["config_sha256"],
                  instance_start_utc=canonical, rehearsal_identity=common.sha256_file(out/"identity.json"),
                  operation_bounds_seconds=bounds, timing_accounting="cumulative-invocations-paid-clock-v1",
                  complete_inventory_required=True, full_sources=config["screen_n"], measurement_groups=list(groups))
    usage=shutil.disk_usage(out)
    artifact_bytes=sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    memory_rows = [r["memory"] for rows in groups.values() for r in rows.values()]
    # execute_unit resets allocator peaks per operation. A diagnostic's double
    # backward graph can peak above later embeds, so its validated telemetry
    # must survive even though diagnostics are not screen producer identities.
    memory_rows.extend(checks["writer-check:" + sid]["memory"] for sid in p["donors"])
    for path in [out/"invocations.jsonl", *out.glob("*.log")]:
        for line in path.read_text(encoding="utf-8").splitlines():
            try: event = json.loads(line)
            except json.JSONDecodeError: continue
            if event.get("event") in ("MODEL_READY", "STAGE_DONE", "STAGE_START") and "memory" in event:
                memory_rows.append(event["memory"])
    peaks = [measured_peak(memory) for memory in memory_rows]
    if not peaks or min(peaks) <= 0:
        raise ValueError("Missing rehearsal memory telemetry")
    device_total = measured_device_total(memory_rows)
    if identity.get("device", {}).get("total_bytes") != device_total:
        raise ValueError("Rehearsal device identity differs from measured capacity")
    result["capacity"]=capacity(artifact_bytes,ratio,usage.free,usage.total,max(peaks),device_total)
    if result["capacity"]["status"]!="GO": result["status"]="RESOURCE_STOP"
    return result


def stage_p_allocation(bounds):
    """Upper allocation for all eight trials, including maximum finalist controls.

    Bounds already carry the 1.5 timing factor. Use the slower measured candidate
    for all 72 candidate writes and the slower of that and F5 for all 40 budget
    controls. The latter has 200 reader gradients versus candidates' 350; its
    exact wall time is still unmeasured. Nothing is silently treated as free.
    """
    required = ("clean_f6-noise", "clean_f6-x0", "clean_f5-r2", "clean_unmarked",
                "native_R0", "native_R1", "native_K3", "detect_f6-noise",
                "detect_f6-x0", "detect_f5-r2", "quality", "prepare")
    if any(not finite(bounds.get(k)) or bounds[k] <= 0 for k in required):
        raise ValueError("Incomplete positive Stage P operation timing bounds")
    candidate = max(bounds["clean_f6-noise"], bounds["clean_f6-x0"])
    budget = max(candidate, bounds["clean_f5-r2"])
    reader = max(bounds["detect_" + a] for a in ("f6-noise", "f6-x0", "f5-r2"))
    counts = dict(candidate_clean=72, retained_clean=24, budget_clean=40, c0_clean=136,
                  native_R0=816, native_R1=1632, native_K3=816, detect=3536, quality=3536,
                  prepare_invocations=24, model_load_cycles=24)
    costs = dict(candidate_clean=72*candidate, retained_clean=24*bounds["clean_f5-r2"],
                 budget_clean=40*budget, c0_clean=136*bounds["clean_unmarked"],
                 detect=3536*reader, quality=3536*bounds["quality"],
                 prepare=24*bounds["prepare"])
    for label in ("native_R0", "native_R1", "native_K3"):
        costs[label] = counts[label]*bounds[label]
    load_keys = ("load_f6-noise", "load_f6-x0", "load_f5-r2", "load_R0", "load_R1", "load_K3", "load_reader", "load_quality")
    if any(not finite(bounds.get(k)) or bounds[k] <= 0 for k in load_keys):
        raise ValueError("Incomplete Stage P model-load timing bounds")
    # Twenty-four full cycles exceed the 23 post-calibration trial invocations.
    # A cycle includes every candidate type's load, a conservative overcount.
    costs["model_loads"] = 24*sum(bounds[k] for k in load_keys)
    expanded = dict(bounds, **{"clean_f5-budget": budget, "detect_f5-budget": reader,
                               "load_f5-budget": max(bounds[k] for k in load_keys[:3])})
    return counts, costs, expanded


def forecast_stage_p(root, config_path, receipt_path, instance_start, now):
    """Forecast P alone from its first two tuning sources; S needs its own test."""
    import tifs_stage_p as stage_p
    root = Path(root).resolve()
    if any(root.rglob("RESOURCE_STOP*.json")):
        return dict(status="RESOURCE_STOP", reason="Stage P resource stop retained")
    config_path = Path(config_path)
    receipt = common.load_json(receipt_path)
    profiles.validate_decision_receipt(receipt, common.sha256_file(config_path))
    if receipt["stage_p"] != "run":
        raise ValueError("Stage P was not chosen")
    instant = datetime.fromisoformat(instance_start.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.timestamp() > now:
        raise ValueError("Actual past timezone-aware instance start required")
    canonical = instant.astimezone(timezone.utc).isoformat()
    bounds, identities, memory_rows = {}, {}, []
    identity_reference = None
    excess_overhead = 0
    artifact_bytes = 0
    for trial in ("retained-f5", "f6-noise-p52", "f6-x0-p52"):
        out = root / "tune" / trial
        config = common.load_json(out / "config.json")
        meta = config["stage_p"]
        if (meta["base_config_sha256"] != common.sha256_file(config_path)
                or meta["user_choice_sha256"] != common.sha256_file(receipt_path)):
            raise ValueError("Calibration base/choice mismatch")
        summary = stage_p.summarize_trial(out, config, count=2, calibration=True)
        if summary["missing"] or summary["status"] in ("INCOMPLETE", "RESOURCE_STOP"):
            raise ValueError("Incomplete calibration inventory: " + trial)
        identity = common.load_json(out / "identity.json")
        if identity.get("effective_config_sha256") != stage_p.digest(config):
            raise ValueError("Calibration effective configuration mismatch")
        if (identity["instance_start_utc"] != canonical or identity["rehearsal"]
                or identity["max_hours"] != receipt["max_instance_hours"]):
            raise ValueError("Calibration clock/cap identity mismatch")
        shared = {k:identity[k] for k in ("code", "profiles", "packages", "device")}
        if identity_reference is not None and shared != identity_reference:
            raise ValueError("Calibration code/profile/package/device differs")
        identity_reference = shared
        for path, digest in {**identity["code"], **identity["profiles"]}.items():
            if common.sha256_file(path) != digest:
                raise ValueError("Calibration code/profile changed: " + path)
        identities[trial] = common.sha256_file(out / "identity.json")
        rows = []
        for path in (out / "clean.jsonl", out / "native.jsonl", *out.glob("detect-*-0-of-1.jsonl"), out / "quality-0-of-1.jsonl"):
            group = common.Journal(path, read_only=True).latest
            if not group or any(r.get("status") != "ok" for r in group.values()):
                raise ValueError("Calibration has unresolved producer/reader/quality row")
            rows.extend(group.values())
        checks = common.Journal(out / "rehearsal-checks.jsonl", read_only=True).latest
        if trial != "retained-f5":
            for sid in summary["sources"]:
                check = checks.get("writer-check:" + sid, {})
                if check.get("status") != "ok" or not common.validate_output(check, out):
                    raise ValueError("Missing successful Stage P writer check")
                value = common.load_json(check["output"]["path"])
                gradient = value.get("clean_input_gradient_norm")
                if value.get("status") != "ok" or not value.get("gradient_checks") or not finite(gradient) or gradient <= 0:
                    raise ValueError("Missing Stage P calibrated writer gradients")
            rows.extend(checks.values())
        for row in rows:
            if row.get("kind") == "native" and stage.c0(row["arm"]):
                if row.get("native_parity", {}).get("exact_rgb8") is not True:
                    raise ValueError("Missing Stage P exact native replay")
                if row["family"] in ("R0", "R1") and row["seed"] == 0:
                    parity = row.get("x0_native_first_step_parity", {})
                    if parity.get("status") != "ok" or parity.get("exact_conditioning") is not True:
                        raise ValueError("Missing Stage P native x0 parity")
        _, overhead, measured = invocation_measurements(out / "invocations.jsonl", now, rows)
        excess_overhead = max(excess_overhead, overhead)
        for key, value in measured.items(): bounds[key] = max(bounds.get(key, 0), value)
        memory_rows.extend(r["memory"] for r in rows)
        for line in (out / "invocations.jsonl").read_text().splitlines():
            event = json.loads(line)
            if "memory" in event: memory_rows.append(event["memory"])
        artifact_bytes += sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    counts, costs, bounds = stage_p_allocation(bounds)
    # Entire P allocation, including calibration again, is deliberately charged
    # in addition to actual elapsed. Each upper operation bound includes 1.5.
    projected = sum(costs.values()) + 24*excess_overhead
    reserve = common.load_json(config_path)["budget"]["retrieval_reserve_seconds"]
    ceiling = receipt["max_instance_hours"]*3600
    total = now-instant.timestamp()+projected+reserve
    usage = shutil.disk_usage(root)
    device_total = measured_device_total(memory_rows)
    if identity_reference["device"].get("total_bytes") != device_total:
        raise ValueError("Stage P device identity differs from measured capacity")
    cap = capacity(artifact_bytes, 136/6, usage.free, usage.total,
                   max(measured_peak(m) for m in memory_rows), device_total)
    return dict(schema="tifs-stage-p-forecast-v1", status="GO" if total <= ceiling and cap["status"] == "GO" else "RESOURCE_STOP",
                stage_p_root=str(root), config_sha256=common.sha256_file(config_path),
                source_manifest_sha256=meta["source_manifest_sha256"], user_choice_sha256=common.sha256_file(receipt_path),
                identity_profiles=identity_reference["profiles"], identity_code=identity_reference["code"],
                identity_packages=identity_reference["packages"], device=identity_reference["device"],
                instance_start_utc=canonical, ceiling_seconds=ceiling, forecast_seconds=total,
                elapsed_instance_seconds=now-instant.timestamp(), projected_stage_p_seconds=projected,
                operation_bounds_seconds=bounds, calibration_identity_sha256=identities, capacity=cap,
                upper_inventory=counts, upper_cost_seconds=costs, factor_in_operation_bounds=1.5,
                overhead_cycles=24, retrieval_reserve_seconds=reserve,
                scope="Stage P only; Stage S requires complete separate rehearsal and forecast on the same paid clock",
                conservative_overcounts="Full P charged after calibration; slower writer used for all candidate/budget marks; full load cycles and overhead both reserved")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rehearsal-out",type=Path)
    group.add_argument("--stage-p-root",type=Path)
    parser.add_argument("--user-choice",type=Path)
    parser.add_argument("--selection",type=Path)
    parser.add_argument("--config",type=Path,default=stage.ROOT/"research/tifs-20261028/stage-s/frozen-config.json")
    parser.add_argument("--instance-start-utc",required=True)
    parser.add_argument("--destination",required=True,type=Path)
    args=parser.parse_args()
    try:
        if args.stage_p_root:
            if args.user_choice is None: raise ValueError("Stage P requires the external pre-output choice")
            result=forecast_stage_p(args.stage_p_root,args.config,args.user_choice,args.instance_start_utc,time.time())
        else:
            result=forecast(args.rehearsal_out,args.config,args.instance_start_utc,time.time(),receipt_path=args.user_choice,selection_path=args.selection)
    except (ValueError,KeyError,OSError) as exc: result=dict(status="INCOMPLETE",reason=str(exc))
    common.atomic_json(args.destination,result)
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result["status"]=="GO" else 3 if result["status"]=="RESOURCE_STOP" else 4)


if __name__=="__main__": main()
