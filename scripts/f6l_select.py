"""Lean F6 decisions from saved journals; standard library only.

Exit codes: 0 advance or a GO label, 2 observed scientific stop, 3 resource stop,
4 incomplete. J is reported in every table and takes part in no rule. A missing
row stays missing: it is never counted as a success or as an observed failure.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import glob
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as common
import tifs_stage_s_analyze as analyze
import f6l_common as lean_common

ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
CONDITIONS = analyze.CONDITIONS


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load_phase(out):
    out = Path(out)
    detections, _ = analyze.merge_journals(glob.glob(str(out / "detect-*.jsonl")))
    qualities, _ = analyze.merge_journals(glob.glob(str(out / "quality-*.jsonl")))
    producers = {name: common.Journal(out / (name + ".jsonl"), read_only=True).latest
                 for name in ("clean", "native", "threats", "secondary")}
    return dict(detections=detections, qualities=qualities, producers=producers)


def call(detections, method, item, owner=ALPHA):
    row = detections.get(f"det:{method}:{item}")
    if not row or row.get("status") != "ok":
        return None
    result = row.get("calls", {}).get(owner)
    return result if isinstance(result, dict) and result.get("status", "ok") == "ok" else None


def rule(result, name):
    """The recorded endpoint, or None when it is unavailable."""
    if result is None or not isinstance(result.get("endpoints"), dict):
        return None
    value = result["endpoints"].get(name)
    return value if type(value) is bool else None


def decoded(result):
    if result is None or not isinstance(result.get("raw"), dict):
        return None
    value = (result["raw"].get("semantic") or {}).get("decoded_score")
    return float(value) if common._finite(value) else None


def majority(values):
    """Lower and upper source outcome. Stage 1 has one seed, so the seed is the outcome."""
    if len(values) == 1:
        return values[0] is True, values[0] is not False
    return common.majority_bounds(values)


def summarize_arm(data, arm, method, cells, seeds, sources):
    detections, qualities = data["detections"], data["qualities"]
    summary = dict(arm=arm, method=method, cells={}, n=len(sources))
    for cell in cells:
        c_bounds, j_bounds, scores, missing = [], [], [], 0
        for sid in sources:
            c_values, j_values = [], []
            for seed in seeds:
                result = call(detections, method, f"native:{cell}:{sid}:{seed}:{arm}")
                c_values.append(rule(result, "C"))
                j_values.append(rule(result, "J"))
                score = decoded(result)
                if score is None:
                    missing += 1
                else:
                    scores.append(score)
            c_bounds.append(majority(c_values))
            j_bounds.append(majority(j_values))
        summary["cells"][cell] = dict(c_lower=sum(x[0] for x in c_bounds), c_upper=sum(x[1] for x in c_bounds),
            j_lower=sum(x[0] for x in j_bounds), j_upper=sum(x[1] for x in j_bounds),
            c_sources=[x[0] for x in c_bounds], mean_decoded=statistics.fmean(scores) if scores else None,
            missing_calls=missing, calls=len(sources) * len(seeds))
    metrics, strict, clean_f = [], [], []
    for sid in sources:
        row = qualities.get(f"quality:clean:{sid}:{arm}")
        total = row.get("total") if row and row.get("status") == "ok" else None
        strict.append(None if total is None else common.strict_quality(total))
        if total is not None:
            metrics.append(total)
        clean_f.append(rule(call(detections, method, f"clean:{sid}:{arm}"), "F"))
    def med(key):
        values = [m[key] for m in metrics if common._finite(m.get(key))]
        return statistics.median(values) if values else None
    summary["quality"] = dict(strict_pass=sum(v is True for v in strict), strict_fail=sum(v is False for v in strict),
        strict_missing=sum(v is None for v in strict), lpips_median=med("lpips"), psnr_median=med("psnr_db"),
        ssim_median=med("ssim_rgb"), lpips_max=max((m["lpips"] for m in metrics if common._finite(m.get("lpips"))), default=None),
        psnr_min=min((m["psnr_db"] for m in metrics if common._finite(m.get("psnr_db"))), default=None))
    summary["clean_f"] = dict(lower=sum(v is True for v in clean_f), upper=sum(v is not False for v in clean_f))
    events, unknown = 0, 0
    items = [f"clean:{sid}:{arm}" for sid in sources]
    items += [f"native:{cell}:{sid}:{seed}:{arm}" for cell in cells for sid in sources for seed in seeds]
    for item in items:
        result = call(detections, method, item, BETA)
        c, f = rule(result, "C"), rule(result, "F")
        events += bool(c or f)
        # A safety-blocked native has no image, so it has no wrong-owner read either.
        row = data["producers"]["native"].get(item) if item.startswith("native") else None
        blocked = row is not None and row.get("status") == "safety_blocked"
        unknown += not blocked and (c is None or f is None)
    summary["wrong_owner"] = dict(events=events, unresolved=unknown)
    return summary


def c0_events(data, method, cells, seeds, sources):
    events, unknown = 0, 0
    items = [f"clean:{sid}:unmarked" for sid in sources]
    items += [f"native:{cell}:{sid}:{seed}:unmarked" for cell in cells for sid in sources for seed in seeds]
    for item in items:
        row = data["producers"]["native"].get(item) if item.startswith("native") else None
        if row is not None and row.get("status") == "safety_blocked":
            continue
        for owner in (ALPHA, BETA):
            result = call(data["detections"], method, item, owner)
            c, f = rule(result, "C"), rule(result, "F")
            events += bool(c or f)
            unknown += c is None or f is None
    return dict(events=events, unresolved=unknown)


def _complete_scores(arm, cells, minimum):
    return all(arm["cells"][cell]["calls"] - arm["cells"][cell]["missing_calls"] >= minimum for cell in cells)


def decide_stage1(summaries, c0, config, missing=()):
    """Rank by the weakest foreign cell. Advance at most two finalists."""
    cells, gates = config["lean"]["cells"], config["lean"]["gates"]
    threshold, rule1 = gates["decoded_threshold"], gates["stage1"]
    foreign, home = cells["foreign"], cells["home"]
    result = dict(schema="f6-lean-stage1-v1", arms={}, c0=c0, finalists=[], rejected={},
                  incomplete={name: "clean write or quality row missing" for name in missing})
    for name, arm in summaries.items():
        result["arms"][name] = arm
        if name == "f5-r2":
            continue
        n = arm["n"]
        if not _complete_scores(arm, [*foreign, home], n - 1) or arm["quality"]["strict_missing"] or arm["clean_f"]["upper"] - arm["clean_f"]["lower"]:
            result["incomplete"][name] = "missing reads or quality rows"
            continue
        reasons = []
        if arm["quality"]["strict_pass"] != n:
            reasons.append("strict clean quality")
        if arm["clean_f"]["lower"] != n:
            reasons.append("clean F")
        if arm["wrong_owner"]["events"]:
            reasons.append("wrong-owner event")
        if arm["wrong_owner"]["unresolved"]:
            result["incomplete"][name] = "unresolved wrong-owner reads"
            continue
        if arm["cells"][home]["mean_decoded"] < rule1["home_mean_decoded_min"]:
            reasons.append("home family below the decoded threshold")
        if any(arm["cells"][cell]["mean_decoded"] < threshold for cell in rule1["advance_mean_decoded_on"]):
            reasons.append("SDXL .1 or K3 below the decoded threshold")
        if reasons:
            result["rejected"][name] = reasons
    if "f5-r2" not in summaries or not _complete_scores(summaries["f5-r2"], [*foreign, home], summaries["f5-r2"]["n"] - 1):
        result["status"] = "INCOMPLETE"
        result["reason"] = "retained F5 control incomplete"
        return result
    if c0["events"]:
        result["status"] = "SCIENTIFIC_STOP"
        result["reason"] = "C0 event under the unchanged reader; needs review"
        return result
    if c0["unresolved"]:
        result["status"] = "INCOMPLETE"
        result["reason"] = "unresolved C0 reads"
        return result
    eligible = [name for name in summaries if name != "f5-r2" and name not in result["rejected"] and name not in result["incomplete"]]
    def key(name):
        arm = summaries[name]
        scores = [arm["cells"][cell]["mean_decoded"] for cell in foreign]
        q = arm["quality"]
        return (-min(scores), -sum(scores), -arm["cells"][home]["mean_decoded"], q["lpips_median"], -q["psnr_median"], -q["ssim_median"], name)
    ranked = sorted(eligible, key=key)
    result["ranking"] = ranked
    result["finalists"] = ranked[:rule1["finalists"]]
    if result["finalists"]:
        result["status"] = "ADVANCE"
    elif result["incomplete"]:
        result["status"] = "INCOMPLETE"
        result["reason"] = "no eligible arm, but missing arms could change that"
    else:
        result["status"] = "SCIENTIFIC_STOP"
        result["reason"] = "no arm reaches the decoded threshold on SDXL .1 and K3 with strict quality"
    return result


def decide_stage2(summaries, c0, config):
    """Fixed ranking on C, then measured quality. One winner goes to Stage 3 or the study stops."""
    cells, rule2 = config["lean"]["cells"], config["lean"]["gates"]["stage2"]
    foreign, home = cells["foreign"], cells["home"]
    control = summaries.get("f5-r2")
    result = dict(schema="f6-lean-stage2-v1", arms=summaries, c0=c0, rejected={}, incomplete={}, finalists=config["lean"]["finalists"], winner=None)
    if control is None or any(control["cells"][cell]["missing_calls"] == control["cells"][cell]["calls"] for cell in [*foreign, home]):
        result.update(status="INCOMPLETE", reason="retained F5 control incomplete")
        return result
    if c0["events"]:
        result.update(status="SCIENTIFIC_STOP", reason="C0 event under the unchanged reader; needs review")
        return result
    if c0["unresolved"]:
        result.update(status="INCOMPLETE", reason="unresolved C0 reads")
        return result
    eligible = []
    for name in config["lean"]["finalists"]:
        arm = summaries.get(name)
        if arm is None or arm["quality"]["strict_missing"] or arm["wrong_owner"]["unresolved"]:
            result["incomplete"][name] = "missing quality or wrong-owner rows"
            continue
        reasons = []
        if arm["quality"]["strict_pass"] != arm["n"]:
            reasons.append("strict clean quality")
        if arm["clean_f"]["upper"] < rule2["clean_f_min"]:
            reasons.append("clean F")
        if arm["wrong_owner"]["events"]:
            reasons.append("wrong-owner event")
        if reasons:
            result["rejected"][name] = reasons
        elif arm["clean_f"]["lower"] < rule2["clean_f_min"]:
            result["incomplete"][name] = "clean F unresolved"
        else:
            eligible.append(name)
    def key(name):
        arm = summaries[name]
        q = arm["quality"]
        foreign_c = [arm["cells"][cell]["c_lower"] for cell in foreign]
        return (-min(foreign_c), -sum(foreign_c), -arm["cells"][home]["c_lower"], q["lpips_median"], -q["psnr_median"], -q["ssim_median"], name)
    ranked = sorted(eligible, key=key)
    result["ranking"] = ranked
    if not ranked:
        result.update(status="INCOMPLETE" if result["incomplete"] else "SCIENTIFIC_STOP",
                      reason="no eligible finalist")
        return result
    winner = summaries[ranked[0]]
    result["nominee"] = ranked[0]
    uppers = [winner["cells"][cell]["c_upper"] for cell in rule2["core_cells"]]
    lowers = [winner["cells"][cell]["c_lower"] for cell in rule2["core_cells"]]
    home_arm, home_f5 = winner["cells"][home], control["cells"][home]
    loss_lower = home_f5["c_lower"] - home_arm["c_upper"]
    loss_upper = home_f5["c_upper"] - home_arm["c_lower"]
    if min(uppers) < rule2["c_min"] or home_arm["c_upper"] < rule2["home_c_min"] or loss_lower > rule2["home_loss_max"]:
        result.update(status="SCIENTIFIC_STOP", reason="nominee below the C or home-family bar")
    elif min(lowers) < rule2["c_min"] or home_arm["c_lower"] < rule2["home_c_min"] or loss_upper > rule2["home_loss_max"]:
        result.update(status="INCOMPLETE", reason="safety-blocked or missing seeds decide the C bar")
    else:
        result.update(status="ADVANCE", winner=ranked[0])
    return result


gate = analyze.minimum_gate


def zero_gate(name, events, unresolved):
    status = "fail" if events else "unknown" if unresolved else "pass"
    return dict(name=name, status=status, events=events, unresolved=unresolved)


def threat_summary(data, method, arm, pairs):
    """Every condition is read. An event is C in combined mode on a quality-eligible image."""
    detections, qualities = data["detections"], data["qualities"]
    events, unresolved, by_condition = [], 0, {}
    for pair in pairs:
        for condition in CONDITIONS:
            kind = "T5" if condition == "unmodified" else "T4"
            item = f"threat:{kind}:{pair['donor']}:{pair['target']}:{arm}:{condition}"
            quality = qualities.get("quality:" + item)
            eligible = quality.get("recipient_eligible") if quality and quality.get("status") == "ok" else None
            result = call(detections, method, item)
            c, d_f = rule(result, "C"), rule(result, "D_and_F")
            row = by_condition.setdefault(condition, dict(reads=0, c=0, d_and_f=0, delivered=0, eligible=0))
            row["reads"] += result is not None
            row["c"] += c is True
            row["d_and_f"] += d_f is True
            row["delivered"] += bool(result and (result["raw"].get("semantic") or {}).get("read"))
            row["eligible"] += eligible is True
            if eligible is True and c is True:
                events.append(item)
            elif (c is None and eligible is not False) or (c is True and eligible is None):
                unresolved += 1
    return dict(events=events, unresolved=unresolved, by_condition=by_condition)


def verdict_stage3(summaries, threats, c0, config, resource_stop=False):
    """FULL_GO needs every foreign cell. CORE_GO names a pass on SDXL .1 and K3 only."""
    lean = config["lean"]
    cells, rule3 = lean["cells"], lean["gates"]["stage3"]
    winner_name, control_name = lean["winner"], lean.get("control")
    winner, f5 = summaries.get(winner_name), summaries.get("f5-r2")
    if winner is None or f5 is None:
        return dict(schema="f6-lean-stage3-v1", status="INCOMPLETE", reason="winner or F5 rows missing", arms=summaries)
    control = summaries.get(control_name) if control_name else None
    per_cell, core = {}, []
    for cell in cells["foreign"]:
        rows = [gate(f"C {cell}", winner["cells"][cell]["c_lower"], winner["cells"][cell]["c_upper"], rule3["c_min"]),
                gate(f"gain over F5 {cell}", winner["cells"][cell]["c_lower"] - f5["cells"][cell]["c_upper"],
                     winner["cells"][cell]["c_upper"] - f5["cells"][cell]["c_lower"], rule3["gains"][cell])]
        if control_name:
            if control is None:
                rows.append(dict(name=f"gain over matched control {cell}", status="unknown"))
            else:
                rows.append(gate(f"gain over matched control {cell}", winner["cells"][cell]["c_lower"] - control["cells"][cell]["c_upper"],
                                 winner["cells"][cell]["c_upper"] - control["cells"][cell]["c_lower"], rule3["gains"][cell]))
        per_cell[cell] = rows
        if cell in cells["core_foreign"]:
            core.extend(rows)
    home = cells["home"]
    home_w, home_f = winner["cells"][home], f5["cells"][home]
    common_gates = [gate("C home", home_w["c_lower"], home_w["c_upper"], rule3["home_c_min"]),
        gate("home loss over F5, negated", home_w["c_lower"] - home_f["c_upper"], home_w["c_upper"] - home_f["c_lower"], -rule3["home_loss_max"]),
        gate("strict clean quality", winner["quality"]["strict_pass"], winner["n"] - winner["quality"]["strict_fail"], winner["n"]),
        gate("clean F", winner["clean_f"]["lower"], winner["clean_f"]["upper"], rule3["clean_f_min"]),
        zero_gate("C0 events", c0["events"], c0["unresolved"]),
        zero_gate("wrong-owner events", winner["wrong_owner"]["events"], winner["wrong_owner"]["unresolved"]),
        zero_gate("T4 and T5 C events", len(threats["events"]), threats["unresolved"])]
    core = core + common_gates
    full = core + [row for cell in cells["foreign"] if cell not in cells["core_foreign"] for row in per_cell[cell]]
    status_of = lambda rows: "fail" if any(r["status"] == "fail" for r in rows) else "unknown" if any(r["status"] == "unknown" for r in rows) else "pass"
    core_status, full_status = status_of(core), status_of(full)
    if core_status == "fail":
        status = "SCIENTIFIC_KILL"
    elif resource_stop:
        status = "RESOURCE_STOP"
    elif core_status == "unknown":
        status = "INCOMPLETE"
    elif full_status == "pass":
        status = "FULL_GO"
    elif full_status == "fail":
        status = "CORE_GO"
    else:
        status = "CORE_GO_FULL_UNRESOLVED"
    return dict(schema="f6-lean-stage3-v1", status=status, winner=winner_name, control=control_name,
                gates=full, arms=summaries, threats=threats, c0=c0, j_role="reported; takes part in no rule",
                claim_limits=["development screen, not confirmation", "image-domain writer, not latent insertion",
                              "human visual review missing", "K3 is selection-seen but excluded from gradients"])


def rule_counts(data, method, arm, cells, seeds, sources, name):
    """Lower and upper source-majority counts of one recorded endpoint, per cell."""
    table = {}
    for cell in cells:
        bounds = [majority([rule(call(data["detections"], method, f"native:{cell}:{sid}:{seed}:{arm}"), name) for seed in seeds])
                  for sid in sources]
        table[cell] = dict(lower=sum(b[0] for b in bounds), upper=sum(b[1] for b in bounds))
    return table


def f7_fit(args):
    """After the rehearsal: does the screen fit? Rehearsal unit times scaled from 2 to 16 sources, times the margin."""
    lean = lean_common.load_lean()
    rehearsal = load_phase(args.root / "f7" / "rehearsal")
    total = 0.0
    for name in ("clean", "native", "threats", "secondary"):
        total += sum(r["seconds"] for r in rehearsal["producers"][name].values() if common._finite(r.get("seconds")))
    total += sum(r["seconds"] for r in rehearsal["detections"].values() if common._finite(r.get("seconds"))) / 4
    total += sum(r["seconds"] for r in rehearsal["qualities"].values() if common._finite(r.get("seconds")))
    remaining = lean["fit"]["margin"] * total * 16 / 2
    elapsed = time.time() - datetime.fromisoformat(args.instance_start_utc.replace("Z", "+00:00")).timestamp()
    cap = lean_common.hours_cap(lean, args.hourly_usd) * 3600
    required = elapsed + remaining + lean["caps"]["retrieval_reserve_seconds"]
    report = dict(phase="f7", elapsed_seconds=elapsed, remaining_seconds=remaining, cap_seconds=cap,
                  required_seconds=required, fits=required <= cap, rehearsal_unit_seconds=total)
    common.atomic_json(args.root / "f7-fit.json", report)
    return report


def verdict_f7(summaries, threats, c0, config, data, resource_stop=False):
    """GO needs C at least 12/16 in the three core cells, at most 2 sources below the better single mark, and no false event."""
    rules = config["lean"]["gates"]["f7"]
    f7, f5, v5 = (summaries.get(a) for a in ("f7", "f5-r2", "v5-r3"))
    if f7 is None or f5 is None or v5 is None:
        return dict(schema="f7-test-v1", status="INCOMPLETE", reason="an arm has no rows", arms=summaries)
    gates = []
    for cell in rules["core_cells"]:
        mine = f7["cells"][cell]
        best_upper = max(f5["cells"][cell]["c_upper"], v5["cells"][cell]["c_upper"])
        best_lower = max(f5["cells"][cell]["c_lower"], v5["cells"][cell]["c_lower"])
        gates.append(gate(f"C {cell}", mine["c_lower"], mine["c_upper"], rules["c_min"]))
        gates.append(gate(f"loss to the better single mark {cell}, negated", mine["c_lower"] - best_upper,
                          mine["c_upper"] - best_lower, -rules["loss_to_better_single_max"]))
    gates += [gate("strict clean quality", f7["quality"]["strict_pass"], f7["n"] - f7["quality"]["strict_fail"], f7["n"]),
              gate("clean F", f7["clean_f"]["lower"], f7["clean_f"]["upper"], rules["clean_f_min"]),
              zero_gate("C0 events under the F7 reader", c0["events"], c0["unresolved"]),
              zero_gate("wrong-owner events", f7["wrong_owner"]["events"], f7["wrong_owner"]["unresolved"]),
              zero_gate("T4 and T5 C events", len(threats["events"]), threats["unresolved"])]
    if any(g["status"] == "fail" for g in gates):
        status = "SCIENTIFIC_KILL"
    elif resource_stop:
        status = "RESOURCE_STOP"
    elif any(g["status"] == "unknown" for g in gates):
        status = "INCOMPLETE"
    else:
        status = "GO"
    cells, seeds, sources = [c["id"] for c in config["cells"]], config["seeds"], data["sources"]
    carriers = {name: rule_counts(data, "f7", "f7", cells, seeds, sources, name)
                for name in ("C_f5", "C_v5", "C_f5_alpha", "C_v5_alpha", "C_combined", "J")}
    return dict(schema="f7-test-v1", status=status, gates=gates, arms=summaries, threats=threats, c0=c0,
                f7_carriers=carriers, reported_cells=rules["reported_cells"], j_role="reported; takes part in no rule",
                claim_limits=["development screen, not confirmation", "image-domain writer, not latent insertion",
                              "two readers: heavier extraction", "human visual review missing"])


def phase_summaries(config, data, arms=None):
    sources = data["sources"]
    seeds, cells = config["seeds"], [c["id"] for c in config["cells"]]
    summaries = {}
    for arm in arms or config["arms"]:
        spec = config["lean"]["arms"][arm]
        if spec["kind"] in ("unmarked", "vine-r"):
            continue
        summaries[arm] = summarize_arm(data, arm, arm, cells, seeds, sources)
    return summaries


def presence_table(config, data):
    """VINE-R is a known-message presence read, kept apart from C and J."""
    table = {}
    for cell in [c["id"] for c in config["cells"]]:
        lower = 0
        for sid in data["sources"]:
            values = []
            for seed in config["seeds"]:
                result = call(data["detections"], "vine-r", f"native:{cell}:{sid}:{seed}:vine-r")
                presence = result.get("presence") if result else None
                values.append(presence.get("present") if isinstance(presence, dict) else None)
            lower += majority(values)[0]
        table[cell] = lower
    return table


def secondary_table(config, data, arms):
    """Distortion results for the article section; they enter no rule."""
    table = {}
    for arm in arms:
        rows = table.setdefault(arm, {})
        for transform in config["secondary"]["transforms"]:
            c = j = reads = 0
            for sid in data["sources"]:
                result = call(data["detections"], arm, f"secondary:{transform['id']}:{sid}:{arm}")
                reads += result is not None
                c += rule(result, "C") is True
                j += rule(result, "J") is True
            rows[transform["id"]] = dict(reads=reads, c=c, j=j)
    return table


def clean_gate(out, config):
    """An arm that fails strict clean quality gets no regeneration. Controls always continue."""
    data = load_phase(out)
    prepared = common.load_json(Path(out) / "prepared.json")
    active, removed, missing = [], {}, {}
    for arm in config["arms"]:
        spec = config["lean"]["arms"][arm]
        if spec["kind"] != "lean":
            active.append(arm)
            continue
        failed, absent = [], []
        for sid in prepared["donors"]:
            row = data["qualities"].get(f"quality:clean:{sid}:{arm}")
            total = row.get("total") if row and row.get("status") == "ok" else None
            if total is None:
                absent.append(sid)
            elif not common.strict_quality(total):
                failed.append(sid)
        # An observed failure removes the arm. An absent image cannot regenerate either, but it stays missing.
        if failed:
            removed[arm] = failed
        elif absent:
            missing[arm] = absent
        else:
            active.append(arm)
    report = dict(active=active, removed=removed, missing=missing)
    common.atomic_json(Path(out) / "arm-gate.json", report)
    return report


def seconds(rows):
    values = [r["seconds"] for r in rows if r.get("status") == "ok" and common._finite(r.get("seconds"))]
    return statistics.median(values) if values else None


def fit(args):
    """Before each paid phase: does the rest fit, from measured unit times?"""
    root = Path(args.root)
    lean = lean_common.load_lean()
    stage1 = load_phase(root / "stage1")
    arms = lean["arms"]
    clean = {}
    for row in stage1["producers"]["clean"].values():
        if row.get("status") == "ok" and common._finite(row.get("seconds")):
            clean.setdefault(row["arm"], []).append(row["seconds"])
    write = {arm: statistics.median(v) for arm, v in clean.items()}
    native = seconds(stage1["producers"]["native"].values())
    detect = seconds(stage1["detections"].values())
    quality = seconds(stage1["qualities"].values())
    if None in (native, detect, quality):
        raise ValueError("Stage 1 lacks measured unit times")
    decision = common.load_json(args.previous)
    selected = decision["finalists"] if args.phase == "stage2" else [decision["winner"]]
    # An arm first written in this phase, such as a matched control, gets the F5 time.
    f5_write = write["f5-r2"]
    controls = {lean_common.control_arm(arm, arms[arm])[0] for arm in selected} - {None}
    candidate = sum(write[arm] for arm in selected)
    cells, seeds, workers = 4, 3, 4
    if args.phase == "stage2":
        count, sources = len(selected) + len(controls) + 2, 12
        marks = sources * (candidate + (len(controls) + 1) * f5_write)
        extra_reads = 0
    else:
        count, sources = len(selected) + len(controls) + 5, 18
        marks = sources * (candidate + (len(controls) + 1) * f5_write + 10)
        extra_reads = sources * count * (len(CONDITIONS) + 8)
    units = count * sources * cells * seeds
    reads = units + count * sources + extra_reads
    remaining = lean["fit"]["margin"] * (marks + units * native + reads * (detect / workers) + reads * quality)
    start = datetime.fromisoformat(args.instance_start_utc.replace("Z", "+00:00")).timestamp()
    elapsed = time.time() - start
    cap = lean_common.hours_cap(lean, args.hourly_usd) * 3600
    required = elapsed + remaining + lean["caps"]["retrieval_reserve_seconds"]
    report = dict(phase=args.phase, elapsed_seconds=elapsed, remaining_seconds=remaining, cap_seconds=cap, required_seconds=required,
                  fits=required <= cap, unit_seconds=dict(native=native, detect=detect, quality=quality, write=write))
    common.atomic_json(root / (args.phase + "-fit.json"), report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True, choices=("clean-gate", "decide", "fit"))
    parser.add_argument("--phase", required=True, choices=("stage1", "stage2", "stage3", "f7"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--instance-start-utc")
    parser.add_argument("--hourly-usd", type=float)
    args = parser.parse_args(argv)
    if args.action == "fit":
        report = f7_fit(args) if args.phase == "f7" else fit(args)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["fits"] else 3
    config = common.load_json(args.out / "config.json")
    if args.action == "clean-gate":
        print(json.dumps(clean_gate(args.out, config), sort_keys=True))
        return 0
    if (config["owners"]["positive"], config["owners"]["wrong"]) != (ALPHA, BETA):
        raise ValueError("Config owners differ from the owners these rules read")
    data = load_phase(args.out)
    prepared = common.load_json(args.out / "prepared.json")
    data["sources"] = prepared["donors"]
    arms = lean_common.active_arms(args.out, config)
    gate_path = args.out / "arm-gate.json"
    gate_report = common.load_json(gate_path) if gate_path.exists() else {}
    stopped = bool(glob.glob(str(args.out / "RESOURCE_STOP*.json")))
    summaries = phase_summaries(config, data, arms)
    cells = [c["id"] for c in config["cells"]]
    c0 = c0_events(data, "f5-r2", cells, config["seeds"], data["sources"])
    if args.phase == "stage1":
        result = decide_stage1(summaries, c0, config, gate_report.get("missing", {}))
    elif args.phase == "stage2":
        result = decide_stage2(summaries, c0, config)
    elif args.phase == "f7":
        pairs = prepared["pairs"]
        result = verdict_f7(summaries, threat_summary(data, "f7", "f7", pairs),
                            c0_events(data, "f7", cells, config["seeds"], data["sources"]), config, data, resource_stop=stopped)
        result["c0_by_reader"] = {method: c0_events(data, method, cells, config["seeds"], data["sources"]) for method in ("f5-r2", "v5-r3")}
        clean_rows = [r for r in data["producers"]["clean"].values() if r.get("arm") == "f7" and r.get("status") == "ok"]
        result["f7_writer"] = dict(rows=len(clean_rows),
            same_q=sum(bool((r.get("embedding_report") or {}).get("same_q")) for r in clean_rows),
            v5_scales=sorted((r.get("embedding_report") or {}).get("v5_scale") for r in clean_rows))
        result["threats_by_arm"] = {arm: threat_summary(data, arm, arm, pairs) for arm in summaries}
        result["secondary"] = secondary_table(config, data, list(summaries))
    else:
        pairs = prepared["pairs"]
        threats = threat_summary(data, config["lean"]["winner"], config["lean"]["winner"], pairs)
        result = verdict_stage3(summaries, threats, c0, config, resource_stop=stopped)
        result["vine_r_presence"] = presence_table(config, data)
        result["threats_by_arm"] = {arm: threat_summary(data, arm, arm, pairs) for arm in summaries}
        result["secondary"] = secondary_table(config, data, list(summaries))
    if args.phase in ("stage1", "stage2") and stopped and result["status"] in ("ADVANCE", "INCOMPLETE"):
        result["status"] = "RESOURCE_STOP"
    result["removed_by_clean_gate"] = gate_report.get("removed", {})
    result["digest"] = digest({k: v for k, v in result.items() if k != "digest"})
    common.atomic_json(args.out / "decision.json", result)
    print(json.dumps({k: result.get(k) for k in ("status", "reason", "finalists", "winner", "ranking")}, sort_keys=True))
    status = result["status"]
    if status in ("ADVANCE", "FULL_GO", "CORE_GO", "CORE_GO_FULL_UNRESOLVED", "GO"):
        return 0
    if status in ("SCIENTIFIC_STOP", "SCIENTIFIC_KILL"):
        return 2
    return 3 if status == "RESOURCE_STOP" else 4


if __name__ == "__main__":
    raise SystemExit(main())
