"""Frozen Stage P plans and saved-journal analysis; pure standard library.

This module does not import the experiment runtime or open source images.
Materializing a check identity requires a prior tuning nomination. Analysis is
not authorization; only the external, pre-output user choice selects a profile.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

import tifs_common as common
import tifs_gate_profiles as profiles
from tifs_stage_s_analyze import endpoint, merge_journals, _valid_metrics

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research/tifs-20261028/stage-p"
BASE = ROOT / "research/tifs-20261028/stage-s/frozen-config.json"
CELLS = ("R0-0.2", "R1-0.1", "R1-0.2", "K3-0.2")
FOREIGN = CELLS[1:]
BUDGETS = (52, 46, 42, 38)
CANDIDATES = tuple(f"{arm}-p{budget}" for arm in ("f6-noise", "f6-x0") for budget in BUDGETS)
RUNGS = {4: 4, 8: 2, 16: 1}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def load_manifest(path):
    path = Path(path)
    expected = path.with_suffix(".sha256").read_text(encoding="utf-8").split()[0]
    if common.sha256_file(path) != expected:
        raise ValueError("Stage P source-manifest sidecar mismatch")
    manifest = common.load_json(path)
    if (manifest.get("schema") != "tifs-stage-p-sources-v1"
            or manifest.get("data_split") != "development" or manifest.get("held_out_allowed") is not False):
        raise ValueError("Invalid Stage P development manifest")
    rows = []
    for partition, n in (("tune", 16), ("check", 8)):
        part = manifest.get(partition + "_sources", [])
        if len(part) != n:
            raise ValueError("Wrong Stage P partition size")
        for row in part:
            if row.get("data_split") != "development":
                raise ValueError("Nondevelopment source")
            for key in ("raw_sha256", "canonical_png_sha256", "rgb8_sha256"):
                if not isinstance(row.get(key), str) or len(row[key]) != 64 or any(c not in "0123456789abcdef" for c in row[key]):
                    raise ValueError("Invalid source hash")
            if not row.get("source_uid") or not row.get("filename") or not row.get("license"):
                raise ValueError("Source provenance missing")
        rows.extend(part)
    for key in ("source_id", "source_uid", "raw_sha256", "canonical_png_sha256", "rgb8_sha256"):
        if len({str(r[key]) for r in rows}) != 24:
            raise ValueError("Stage P sources overlap: " + key)
    expected_rungs = [(4, 8, 4), (8, 4, 2), (16, 2, 1)]
    actual = [(r["cumulative_sources"], r["configurations_entering_max"], r["survivors_max"]) for r in manifest["tuning_rungs"]]
    if actual != expected_rungs:
        raise ValueError("Stage P rung allocation changed")
    return manifest


def trial_parameters(trial_id):
    if trial_id in CANDIDATES:
        arm, budget = trial_id.rsplit("-p", 1)
        return dict(candidate=arm, writer_psnr_db=int(budget), role="candidate")
    if trial_id == "retained-f5":
        return dict(candidate="f5-r2", writer_psnr_db=52, role="retained-f5")
    if trial_id in tuple("f5-budget-p" + str(b) for b in BUDGETS):
        return dict(candidate="f5-budget", writer_psnr_db=int(trial_id.rsplit("-p", 1)[1]), role="budget-f5")
    raise ValueError("Undeclared Stage P configuration: " + str(trial_id))


def materialize(base_path, manifest_path, receipt_path, trial_id, partition="tune", nomination=None):
    """Return a full16/full8 immutable config, never a rung-specific config."""
    base_path, manifest_path = Path(base_path), Path(manifest_path)
    parent = common.sha256_file(base_path)
    receipt = common.load_json(receipt_path)
    profile = profiles.validate_decision_receipt(receipt, parent)
    if receipt["stage_p"] != "run":
        raise ValueError("External choice did not select Stage P")
    manifest = load_manifest(manifest_path)
    params = trial_parameters(trial_id)
    if partition not in ("tune", "check"):
        raise ValueError("Invalid partition")
    if partition == "check":
        if (not nomination or nomination.get("status") != "NOMINATED"
                or nomination.get("candidate_id") not in CANDIDATES
                or nomination.get("base_config_sha256") != parent
                or nomination.get("source_manifest_sha256") != common.sha256_file(manifest_path)
                or nomination.get("user_choice_sha256") != common.sha256_file(receipt_path)
                or nomination.get("gate_profile") != profile):
            raise ValueError("Check requires matching pre-check tuning nomination")
        winner = trial_parameters(nomination["candidate_id"])
        allowed = (nomination["candidate_id"], "retained-f5", "f5-budget-p" + str(winner["writer_psnr_db"]))
        if trial_id not in allowed:
            raise ValueError("No runner-up or other budget may enter check")
    config = profiles.profile_config(common.load_json(base_path), profile)
    config.update(candidate=params["candidate"], arms=[params["candidate"], "unmarked"],
                  new_writers=[params["candidate"]] if params["candidate"] != "f5-r2" else [],
                  source_manifest=str(manifest_path.resolve()), source_manifest_sha256=common.sha256_file(manifest_path),
                  screen_n=len(manifest[partition + "_sources"]), execution_authorized=False)
    config["writer"].update(psnr_db=params["writer_psnr_db"], refine_psnr_db=58)
    config["budget"]["max_instance_hours"] = receipt["max_instance_hours"]
    config["budget"]["max_seconds"] = receipt["max_instance_hours"] * 3600
    complete_parameters = dict(**params, writer=config["writer"], owners=config["owners"],
        cells=config["cells"], seeds=config["seeds"], payload=config["payload"], base_config_sha256=parent)
    config["stage_p"] = dict(schema="tifs-stage-p-trial-v1", configuration_id=trial_id,
        parameters=params, complete_parameters=complete_parameters, parameter_sha256=digest(complete_parameters), partition=partition,
        sources=manifest[partition + "_sources"], gate_profile=profile,
        base_config_sha256=parent, source_manifest_sha256=common.sha256_file(manifest_path),
        protocol_sha256=common.sha256_file(HERE / "PROTOCOL.md"),
        search_config_sha256=common.sha256_file(HERE / "search-config.json"),
        user_choice_sha256=common.sha256_file(receipt_path),
        k3_optimization="excluded", nomination_sha256=digest(nomination) if nomination else None)
    return config


def active_sources(config, count=None, calibration=False):
    """Runtime hook: immutable source identity with a fixed cumulative prefix."""
    meta = config["stage_p"]
    rows = meta["sources"]
    n = len(rows) if count is None else count
    if calibration:
        if (meta["partition"] != "tune" or meta["configuration_id"] not in
                ("retained-f5", "f6-noise-p52", "f6-x0-p52") or n != 2):
            raise ValueError("Calibration is fixed to first2 tuning sources and three declared trials")
        allowed = (2,)
    else:
        allowed = (8,) if meta["partition"] == "check" else (4, 8, 16)
    if n not in allowed or len(rows) != (8 if meta["partition"] == "check" else 16):
        raise ValueError("Invalid Stage P cumulative source prefix")
    return rows[:n]


def immutable_json(path, value):
    path = Path(path)
    if path.exists():
        if common.load_json(path) != value:
            raise ValueError("Refusing to change frozen Stage P record: " + str(path))
    else:
        common.atomic_json(path, value)


def _journal_paths(out, prefix):
    return sorted(Path(out).glob(prefix + "-*.jsonl"))


def _finite_metrics(metrics, candidate_clean=False):
    return bool(_valid_metrics(metrics) and (not candidate_clean or common._finite(metrics.get("psnr_db"))))


def summarize_trial(out, config, source_rows=None, count=None, calibration=False):
    """Recompute endpoints from raw calls, validate every frozen producer/read.

    No aggregate success flag is accepted as evidence. Artifact hashes are read
    as bytes, never decoded. Torn journal tails and missing calls stay missing.
    All attempts, including superseded resource/error rows, contribute cost.
    """
    out = Path(out)
    meta = config["stage_p"]
    rows = active_sources(config, count, calibration=calibration)
    if source_rows is not None and rows != list(source_rows):
        raise ValueError("Summary source prefix mismatch")
    sources = [str(r["source_id"]) for r in rows]
    arm = config["candidate"]
    identity = common.load_json(out / "identity.json")
    # Config bytes are bound by the runtime; a caller cannot substitute a dict.
    config_path = out / "config.json"
    if (common.load_json(config_path) != config or identity.get("config_sha256") != common.sha256_file(config_path)
            or identity.get("source_manifest_sha256") != meta["source_manifest_sha256"]):
        raise ValueError("Stage P runtime identity/configuration mismatch")
    if not isinstance(identity.get("profiles"), dict) or not identity["profiles"] or not isinstance(identity.get("code"), dict) or not identity["code"]:
        raise ValueError("Stage P runtime reader/profile/code identity missing")
    prepared = common.load_json(out / "prepared.json")
    if prepared.get("donors") != [str(r["source_id"]) for r in meta["sources"]] or prepared.get("targets"):
        raise ValueError("Prepared Stage P partition identity mismatch")
    for row in rows:
        if any(prepared.get("sources", {}).get(str(row["source_id"]), {}).get(k) != row[k]
               for k in ("source_uid", "canonical_png_sha256", "rgb8_sha256")):
            raise ValueError("Prepared source metadata mismatch")
    clean = common.Journal(out / "clean.jsonl", read_only=True)
    native = common.Journal(out / "native.jsonl", read_only=True)
    det, det_tails = merge_journals(_journal_paths(out, "detect"))
    qual, qual_tails = merge_journals(_journal_paths(out, "quality"))
    expected = common.clean_ids(config, sources) + common.native_ids(config, sources)
    full_ids = set(common.clean_ids(config, [str(r["source_id"]) for r in meta["sources"]]) + common.native_ids(config, [str(r["source_id"]) for r in meta["sources"]]))
    producers = {**clean.latest, **native.latest}
    if set(producers) - full_ids:
        raise ValueError("Undeclared producer output")
    if set(det) - {f"det:{arm}:{uid}" for uid in full_ids} or set(qual) - {"quality:" + uid for uid in full_ids}:
        raise ValueError("Undeclared detector or quality output")
    missing, rejection, evidence, negatives, metrics, clean_f = [], [], {}, [], {}, 0
    calls_by_id = {}
    tapes = {}
    for uid in expected:
        producer = producers.get(uid)
        if not producer or producer.get("status") != "ok":
            missing.append(uid)
            continue
        common.validate_output(producer, out)
        _, *parts = uid.split(":")
        expected_source = parts[0] if uid.startswith("clean:") else parts[1]
        expected_arm = parts[-1]
        if producer.get("source") != expected_source or producer.get("arm") != expected_arm:
            raise ValueError("Producer identity fields disagree with frozen ID")
        marked = expected_arm == arm
        payload = producer.get("payload") if marked else None
        if marked and (not isinstance(payload, dict) or any(common._word(payload.get(k)) is None or not 0 <= common._word(payload.get(k)) < 2**32 for k in ("q", "h"))):
            missing.append("payload:" + uid)
        if uid.startswith("native:"):
            _, cell, sid, seed, _ = uid.split(":")
            if producer.get("cell") != cell or producer.get("seed") != int(seed):
                raise ValueError("Native identity fields disagree")
            clean_row = clean.latest.get(f"clean:{sid}:{expected_arm}", {})
            if producer.get("input") != clean_row.get("output") or producer.get("payload") != clean_row.get("payload"):
                raise ValueError("Native input/payload is not paired clean producer")
            c0 = native.latest.get(f"native:{cell}:{sid}:{seed}:unmarked", {})
            tape = c0.get("tape_receipt")
            if not isinstance(tape, list) or not tape or any(not isinstance(t, dict) or not isinstance(t.get("sha256"), str) or len(t["sha256"]) != 64 for t in tape):
                missing.append("tape:" + uid)
            else:
                tapes[f"{cell}:{sid}:{seed}"] = tape
                if marked and producer.get("replay_tape_receipt") != tape:
                    missing.append("replay_tape_receipt:" + uid)
                if marked and producer.get("replay_tape_consumed") is not True:
                    missing.append("replay_tape_consumed:" + uid)
        detection = det.get(f"det:{arm}:{uid}", {})
        quality = qual.get("quality:" + uid, {})
        expected_sha = producer["output"]["sha256"]
        for name, read in (("detect", detection), ("quality", quality)):
            if read.get("status") != "ok" or read.get("input_sha256") != expected_sha:
                missing.append(name + ":" + uid)
            elif read.get("item") != uid or read.get("source") != expected_source or read.get("arm") != expected_arm:
                raise ValueError("Reader identity differs from producer")
        if detection.get("status") == "ok" and detection.get("input_sha256") == expected_sha:
            calls = detection.get("calls", {})
            values = {}
            for role, owner in config["owners"].items():
                call = calls.get(owner)
                target = payload if marked and role == "positive" else None
                values[role] = {r: endpoint(call, target, r) for r in ("C", "J", "F")}
                if any(values[role][r] is None for r in ("C", "F")) or (marked and role == "positive" and values[role]["J"] is None):
                    missing.append("calls:" + owner + ":" + uid)
                if not marked or role == "wrong":
                    for rule in ("C", "F"):
                        v = values[role][rule]
                        negatives.append(dict(item=uid, owner=owner, rule=rule, value=v))
                        if v is True:
                            rejection.append("forbidden_event:" + owner + ":" + rule + ":" + uid)
            calls_by_id[uid] = values
            if marked and uid.startswith("clean:"):
                clean_f += values["positive"]["F"] is True
        total = quality.get("total")
        if quality.get("status") == "ok" and quality.get("input_sha256") == expected_sha:
            if not _finite_metrics(total, candidate_clean=marked and uid.startswith("clean:")):
                missing.append("finite_quality:" + uid)
            elif quality.get("reference_source") != expected_source:
                raise ValueError("Quality reference differs from source")
            elif marked and uid.startswith("clean:"):
                metrics[expected_source] = total
                if not common.strict_quality(total):
                    rejection.append("strict_quality:" + expected_source)
        evidence[uid] = dict(producer=producer, detection=detection, quality=quality)
    if clean_f < math.ceil(15 * len(sources) / 16) and not missing:
        rejection.append("clean_F")
    counts = {}
    for cell in CELLS:
        counts[cell] = {}
        for rule in ("C", "J"):
            outcomes = [[calls_by_id.get(f"native:{cell}:{sid}:{seed}:{arm}", {}).get("positive", {}).get(rule) for seed in (0, 1, 2)] for sid in sources]
            bounds = [common.majority_bounds(v) for v in outcomes]
            counts[cell][rule] = dict(lower=sum(b[0] for b in bounds), upper=sum(b[1] for b in bounds),
                source_values=[b[0] if b[0] == b[1] else None for b in bounds])
    paths = [out / n for n in ("identity.json", "prepared.json", "config.json", "clean.jsonl", "native.jsonl") if (out / n).exists()] + _journal_paths(out, "detect") + _journal_paths(out, "quality")
    cost = dict(attempts=0, seconds=0., marked_clean=0, c0_clean=0, native_attempts=0, c0_native_attempts=0)
    for path in [out / "clean.jsonl", out / "native.jsonl", *_journal_paths(out, "detect"), *_journal_paths(out, "quality")]:
        if not path.exists():
            continue
        for line in path.read_bytes().splitlines(keepends=True):
            if not line.endswith(b"\n"):
                continue
            attempt = common._loads(line.decode())
            cost["attempts"] += 1
            seconds = attempt.get("seconds")
            if common._finite(seconds) and seconds >= 0:
                cost["seconds"] += seconds
            if attempt.get("kind") == "clean":
                cost["c0_clean" if attempt.get("arm") == "unmarked" else "marked_clean"] += 1
            if attempt.get("kind") == "native":
                cost["native_attempts"] += 1
                cost["c0_native_attempts"] += attempt.get("arm") == "unmarked"
    tails = bool(clean.incomplete_tail_bytes or native.incomplete_tail_bytes or det_tails or qual_tails)
    if tails:
        missing.append("uncommitted_journal_tail")
    resource = bool(list(out.glob("RESOURCE_STOP*.json"))) or any(r.get("status") == "resource_stop" for r in producers.values())
    timing = out / "invocations.jsonl"
    cost.update(invocation_seconds=0., model_load_seconds=0., unfinished_invocations=[])
    if timing.exists():
        started, ended = set(), set()
        for line in timing.read_bytes().splitlines(keepends=True):
            if not line.endswith(b"\n"):
                continue
            event = common._loads(line.decode())
            if event.get("event") == "INVOCATION_START":
                started.add(event["invocation"])
            if event.get("event") == "INVOCATION_END":
                ended.add(event["invocation"])
                if common._finite(event.get("seconds")):
                    cost["invocation_seconds"] += event["seconds"]
            if event.get("event") == "MODEL_READY" and common._finite(event.get("load_seconds")):
                cost["model_load_seconds"] += event["load_seconds"]
        cost["unfinished_invocations"] = sorted(started - ended)
        paths.append(timing)
    control_diagnostics = rejection if meta["parameters"]["role"] != "candidate" else []
    # Controls provide observed comparisons, not a hidden clean-performance
    # threshold. Their strict quality/F/false-event diagnostics stay visible.
    if control_diagnostics:
        rejection = []
    # An observed failure does not excuse missing trials or hide a resource
    # stop. Keep its rejection reasons, but do not rank the contender away.
    status = "RESOURCE_STOP" if resource else "INCOMPLETE" if missing else "REJECTED" if rejection else "COMPLETE"
    return dict(configuration_id=meta["configuration_id"], parameters=meta["parameters"], parameter_sha256=meta["parameter_sha256"],
        partition=meta["partition"], sources=sources, source_uids=[r["source_uid"] for r in rows],
        status=status, rejection_reasons=sorted(set(rejection)), missing=sorted(set(missing)),
        control_diagnostics=sorted(set(control_diagnostics)),
        expected=len(expected), observed=len(evidence), clean_F=clean_f, clean_metrics=metrics,
        counts=counts, negative_calls=len(negatives), negative_events=sum(r["value"] is True for r in negatives),
        evidence_sha256=digest(evidence), evidence_files={str(p): common.sha256_file(p) for p in paths},
        pairing=dict(owners=config["owners"], cells=config["cells"], seeds=config["seeds"],
                     reader_profiles=identity["profiles"], native_and_reader_code=identity["code"], packages=identity.get("packages"),
                     sources=[{k:r[k] for k in ("source_id", "source_uid", "raw_sha256", "canonical_png_sha256", "rgb8_sha256")} for r in rows], tapes=tapes),
        compute=cost)


def comparison(candidate, comparator):
    """Source-paired achieved quality and fixed native gaps; no nominal match."""
    if any(item is not None and item["status"] == "RESOURCE_STOP" for item in (candidate, comparator)):
        return dict(status="RESOURCE_STOP")
    if candidate["status"] != "COMPLETE" or comparator is None or comparator["status"] != "COMPLETE":
        return dict(status="INCOMPLETE")
    if candidate["pairing"] != comparator["pairing"]:
        raise ValueError("Comparator source/native/owner/tape identities differ")
    sources = candidate["sources"]
    if any(s not in candidate["clean_metrics"] or s not in comparator["clean_metrics"] for s in sources):
        return dict(status="INCOMPLETE")
    delta = {key: statistics.median(candidate["clean_metrics"][s][key] - comparator["clean_metrics"][s][key] for s in sources) for key in ("lpips", "psnr_db", "ssim_rgb")}
    gains = {cell: {rule: candidate["counts"][cell][rule]["lower"] - comparator["counts"][cell][rule]["upper"] for rule in ("C", "J")} for cell in CELLS}
    return dict(status="COMPLETE", paired_median_delta=delta, gains=gains,
                quality_parity=delta["lpips"] <= .005 and delta["psnr_db"] >= -1,
                retained_R0=all(gains["R0-0.2"][r] >= -1 for r in ("C", "J")))


def rank_key(summary):
    foreign = [summary["counts"][c][r]["lower"] for c in FOREIGN for r in ("C", "J")]
    home = [summary["counts"]["R0-0.2"][r]["lower"] for r in ("C", "J")]
    quality = list(summary["clean_metrics"].values())
    return (-min(foreign), -sum(foreign), -min(home), -sum(home), statistics.median(q["lpips"] for q in quality),
            -statistics.median(q["psnr_db"] for q in quality), -statistics.median(q["ssim_rgb"] for q in quality), summary["configuration_id"])


def eligibility(summary, retained, budget, n, profile, final=False):
    if profile not in profiles.PROFILES:
        raise ValueError("Unknown gate profile")
    status = summary["status"]
    reports = dict(round1=comparison(summary, retained), proposed=comparison(summary, budget) if final else dict(status="NOT_REQUIRED_AT_RUNG"))
    reasons = list(summary["rejection_reasons"])
    # Required controls remain part of the allocated experiment even when a
    # candidate has already failed a scientific criterion. A resource stop or
    # missing control cannot turn into a scientific rejection through filtering.
    evidence = [("candidate", summary), ("retained_f5_control", retained)]
    if final:
        evidence.append(("budget_f5_control", budget))
    resource = [name for name, item in evidence if item is not None and item["status"] == "RESOURCE_STOP"]
    unresolved = [name for name, item in evidence if item is None or item["status"] == "INCOMPLETE"
                  or (name != "candidate" and item["status"] not in ("COMPLETE", "RESOURCE_STOP"))]
    if resource or unresolved:
        details = {name: dict(status=item["status"], missing=item.get("missing", []),
                             rejection_reasons=item.get("rejection_reasons", []),
                             control_diagnostics=item.get("control_diagnostics", []))
                   if item is not None else dict(status="MISSING") for name, item in evidence}
        return dict(status="RESOURCE_STOP" if resource else "INCOMPLETE",
                    reasons=list(dict.fromkeys(reasons + summary["missing"] + resource + unresolved)),
                    evidence_status=details, compatibility=reports)
    if status == "REJECTED":
        return dict(status="REJECTED", reasons=reasons, compatibility=reports)
    if status != "COMPLETE":
        return dict(status=status, reasons=summary["missing"], compatibility=reports)
    required = reports["round1"]
    if required["status"] != "COMPLETE":
        return dict(status="INCOMPLETE", reasons=["retained_f5_control"], compatibility=reports)
    if profile == "round1" and not required["quality_parity"]:
        reasons.append("retained_f5_quality_parity")
    if final:
        # Even in round1 the prospectively required budget control is a
        # diagnostic that must actually exist before nomination/check passes.
        if reports["proposed"]["status"] != "COMPLETE":
            return dict(status="INCOMPLETE", reasons=["budget_f5_control"], compatibility=reports)
        if not required["retained_R0"]:
            reasons.append("retained_R0_loss")
        # Retained F5 gains belong to the chosen proposed profile only here;
        # round1 Stage P compatibility does not replace the later Stage S gates.
        if profile == "round3-proposed":
            if reports["proposed"]["status"] != "COMPLETE":
                return dict(status="INCOMPLETE", reasons=["budget_f5_control"], compatibility=reports)
            if not reports["proposed"]["quality_parity"]:
                reasons.append("budget_f5_quality_parity")
            if any(reason == "clean_F" or reason.startswith("strict_quality:") for reason in budget.get("control_diagnostics", [])):
                reasons.append("budget_f5_absolute_clean_gate")
            for report_name in ("round1", "proposed"):
                for cell, gain in (("R1-0.1", 4), ("R1-0.2", 4), ("K3-0.2", 3)):
                    required_gain = math.ceil(n * gain / 16)
                    if any(reports[report_name]["gains"][cell][r] < required_gain for r in ("C", "J")):
                        reasons.append(report_name + "_gain:" + cell)
    return dict(status="REJECTED" if reasons else "ELIGIBLE", reasons=reasons, compatibility=reports)


def select_rung(summaries, retained, budget_controls, n, profile, entrants):
    """Pure allocation/nomination; unknown contenders cannot be ranked away."""
    if n not in RUNGS or len(entrants) > {4: 8, 8: 4, 16: 2}[n] or len(set(entrants)) != len(entrants) or any(e not in CANDIDATES for e in entrants):
        raise ValueError("Invalid rung entrants")
    assessed = {}
    for candidate in entrants:
        summary = summaries[candidate]
        if summary["configuration_id"] != candidate or len(summary["sources"]) != n or summary["partition"] != "tune":
            raise ValueError("Rung summary identity mismatch")
        budget = trial_parameters(candidate)["writer_psnr_db"]
        assessed[candidate] = eligibility(summary, retained, budget_controls.get(budget), n, profile, final=n == 16)
    unresolved = [k for k, v in assessed.items() if v["status"] in ("INCOMPLETE", "RESOURCE_STOP")]
    eligible = [summaries[k] for k, v in assessed.items() if v["status"] == "ELIGIBLE"]
    eligible.sort(key=rank_key)
    status = "RESOURCE_STOP" if any(assessed[k]["status"] == "RESOURCE_STOP" for k in unresolved) else "INCOMPLETE" if unresolved else "ADVANCE" if eligible else "SCIENTIFIC_STOP"
    survivors = [s["configuration_id"] for s in eligible[:RUNGS[n]]] if status == "ADVANCE" else []
    futility = None
    if n == 16 and survivors:
        winner = summaries[survivors[0]]
        foreign_min = min(winner["counts"][c][r]["lower"] for c in FOREIGN for r in ("C", "J"))
        home_min = min(winner["counts"]["R0-0.2"][r]["lower"] for r in ("C", "J"))
        if min(foreign_min, home_min) < 12:
            status, survivors = "SCIENTIFIC_STOP", []
            futility = "CLEARLY_BELOW_STAGE_S_BAR" if foreign_min <= 9 else "BELOW_SCREEN_BAR" if foreign_min < 12 else "R0_BELOW_SCREEN_BAR"
    return dict(schema="tifs-stage-p-progression-v1", status=status, n=n, gate_profile=profile,
        entrants=list(entrants), survivors=survivors, assessed=assessed, futility=futility,
        candidate_evidence={k: summaries[k]["evidence_sha256"] for k in entrants},
        retained_evidence=retained["evidence_sha256"] if retained else None,
        budget_evidence={str(k): v["evidence_sha256"] for k, v in budget_controls.items()})


def check_winner(summary, retained, budget, profile):
    if summary["partition"] != "check" or len(summary["sources"]) != 8:
        raise ValueError("Check requires exactly eight untouched Stage P sources")
    result = eligibility(summary, retained, budget, 8, profile, final=True)
    if result["status"] == "ELIGIBLE":
        foreign_min = min(summary["counts"][c][r]["lower"] for c in FOREIGN for r in ("C", "J"))
        home_min = min(summary["counts"]["R0-0.2"][r]["lower"] for r in ("C", "J"))
        if min(foreign_min, home_min) < 6:
            result.update(status="REJECTED", reasons=["check_absolute_bar"],
                futility="CLEARLY_BELOW_STAGE_S_BAR" if foreign_min <= 3 else "BELOW_SCREEN_BAR" if foreign_min < 6 else "R0_BELOW_SCREEN_BAR")
    result["check_status"] = "PASS" if result["status"] == "ELIGIBLE" else "FAIL" if result["status"] == "REJECTED" else result["status"]
    return result
