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
    units = {}
    bounds = {}
    for row in rows:
        duration = row.get("seconds")
        if not finite(duration) or duration <= 0 or not row.get("operation") or not row.get("invocation"):
            raise ValueError("Missing measured operation timing/identity")
        units[row["invocation"]] = units.get(row["invocation"], 0) + duration
        label = row["operation"]
        bounds[label] = max(bounds.get(label, 0), 1.5 * duration)
    loads = {}
    for row in events:
        if row.get("event") == "MODEL_READY":
            value = row.get("load_seconds")
            if not finite(value) or value <= 0:
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


def forecast(out, config, instance_start, now):
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
    for path, digest in identity.get("code",{}).items():
        if common.sha256_file(path)!=digest:
            raise ValueError("Rehearsal code changed: "+path)
    config=common.load_json(config)
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
        if receipt.get("status")!="ok" or not receipt.get("gradient_checks") or not receipt.get("clean_input_gradient_norm",0)>0:
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
        min(54000,identity["max_hours"]*3600),config["budget"]["retrieval_reserve_seconds"])
    result.update(schema="tifs-stage-s-forecast-v1", config_sha256=identity["config_sha256"],
                  instance_start_utc=canonical, rehearsal_identity=common.sha256_file(out/"identity.json"),
                  operation_bounds_seconds=bounds, timing_accounting="cumulative-invocations-paid-clock-v1",
                  complete_inventory_required=True, full_sources=config["screen_n"], measurement_groups=list(groups))
    usage=shutil.disk_usage(out)
    artifact_bytes=sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    memory_rows = [r["memory"] for rows in groups.values() for r in rows.values()]
    for path in [out/"invocations.jsonl", *out.glob("*.log")]:
        for line in path.read_text(encoding="utf-8").splitlines():
            try: event = json.loads(line)
            except json.JSONDecodeError: continue
            if event.get("event") in ("MODEL_READY", "STAGE_DONE", "STAGE_START") and "memory" in event:
                memory_rows.append(event["memory"])
    peaks = [measured_peak(memory) for memory in memory_rows]
    if not peaks or min(peaks) <= 0:
        raise ValueError("Missing rehearsal memory telemetry")
    result["capacity"]=capacity(artifact_bytes,ratio,usage.free,usage.total,max(peaks),
                                measured_device_total(memory_rows))
    if result["capacity"]["status"]!="GO": result["status"]="RESOURCE_STOP"
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rehearsal-out",required=True,type=Path)
    parser.add_argument("--config",type=Path,default=stage.ROOT/"research/tifs-20261028/stage-s/frozen-config.json")
    parser.add_argument("--instance-start-utc",required=True)
    parser.add_argument("--destination",required=True,type=Path)
    args=parser.parse_args()
    try: result=forecast(args.rehearsal_out,args.config,args.instance_start_utc,time.time())
    except (ValueError,KeyError,OSError) as exc: result=dict(status="INCOMPLETE",reason=str(exc))
    common.atomic_json(args.destination,result)
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result["status"]=="GO" else 3 if result["status"]=="RESOURCE_STOP" else 4)


if __name__=="__main__": main()
