"""Frozen Stage S screen analysis of saved JSON journals; standard library only.

No images, artifacts, models, scientific imports, or experiment entrypoints are
opened. Bounds are deterministic completions of missing fixed-seed outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import statistics

import tifs_common as common
import tifs_article_decision as article

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "research/tifs-20261028/stage-s/frozen-config.json"
RULES = ("A", "C", "Q", "J", "H", "D", "F", "D_and_F")
CONDITIONS = ("patch128", "patch256", "patch128-sham", "patch256-sham", "residual0.5", "residual1.0", "unmodified")
INTERNAL = ("f6-noise", "f6-x0", "f6-codec", "f6-generic", "f5-budget", "f5-r2", "v5-r3", "vine-b")


def read_modes(config, method):
    return ("combined",) if method == "vine-b" else config["threats"]["read_modes"]


def merge_journals(paths):
    """Single-writer last-row semantics, but overlapping shards are invalid."""
    merged, tails = {}, []
    for path in sorted(paths):
        journal = common.Journal(path, read_only=True)
        overlap = set(merged).intersection(journal.latest)
        if overlap:
            raise ValueError("Overlapping journal shards: " + str(sorted(overlap)[:5]))
        merged.update(journal.latest)
        if journal.incomplete_tail_bytes:
            tails.append(dict(path=str(path), bytes=journal.incomplete_tail_bytes))
    return merged, tails


def observed(row):
    return row if row and row.get("status") == "ok" else None


def endpoint(call, payload, rule):
    """Unavailable data stays None, including exact-code target unavailability.

    C is read AND content_match. J additionally requires the actually decoded
    original q; no reference-free semantic recomputation can satisfy Q or J.
    """
    call = observed(call)
    if not call or not isinstance(call.get("raw"), dict):
        return None
    d = call["raw"]
    s, h = d.get("semantic"), d.get("instance")
    def conjunction(*values):
        return False if False in values else None if None in values else True
    def flag(record, key):
        value = record.get(key) if isinstance(record, dict) else None
        return value if type(value) is bool else None
    def exact(record, key):
        read = flag(record, "read")
        if read is False:
            return False
        a = common._word(record.get("decoded_code")) if isinstance(record, dict) else None
        b = common._word((payload or {}).get(key))
        return None if read is None or a is None or b is None else a == b
    c = conjunction(flag(s, "read"), flag(s, "content_match"))
    q, hh = exact(s, "q"), exact(h, "h")
    f = d.get("outcome") == "both_match" if isinstance(d.get("outcome"), str) else None
    a = True if True in (flag(s, "found"), flag(h, "found")) else (
        False if flag(s, "found") is False and flag(h, "found") is False else None)
    values = dict(A=a, C=c, Q=q, J=conjunction(q, flag(s, "content_match")), H=hh,
                  D=conjunction(q, hh), F=f, D_and_F=conjunction(q, hh, f))
    return values[rule]


def count_bounds(values):
    values = list(values)
    lower = sum(v is True for v in values)
    return dict(lower=lower, upper=lower + sum(v is None for v in values),
                observed=sum(v is not None for v in values), missing=sum(v is None for v in values),
                denominator=len(values))


def source_bounds(values_by_source):
    bounds = [common.majority_bounds(values) for values in values_by_source]
    return dict(lower=sum(x[0] for x in bounds), upper=sum(x[1] for x in bounds),
                complete_sources=sum(all(v is not None for v in values) for values in values_by_source),
                denominator=len(bounds), missing_seed_outcomes=sum(v is None for values in values_by_source for v in values))


def minimum_gate(name, lower, upper, required, **extra):
    return dict(name=name, status="pass" if lower >= required else "fail" if upper < required else "unknown",
                lower=lower, upper=upper, required_min=required, **extra)


def verdict(gates, inventory_complete, resource_stop):
    # A proved scientific failure cannot be hidden by later resource loss.
    if any(g["status"] == "fail" for g in gates):
        return "SCIENTIFIC_KILL"
    if resource_stop:
        return "RESOURCE_STOP"
    if inventory_complete and all(g["status"] == "pass" for g in gates):
        return "GO"
    return "INCOMPLETE"


def expected_inventory(config, sources, pairs):
    result = dict(clean=common.clean_ids(config, sources), native=common.native_ids(config, sources),
                  secondary=common.secondary_ids(config, sources))
    result["threats"] = [f"threat:{'T5' if t == 'unmodified' else 'T4'}:{p['donor']}:{p['target']}:{arm}:{t}"
                         for p in pairs for arm in config["arms"] for t in CONDITIONS]
    return result


def inventory_row(name, expected, rows, declared_count=None):
    expected = set(expected)
    statuses = Counter(rows.get(uid, {}).get("status", "absent") for uid in expected)
    missing = sorted(uid for uid in expected if not observed(rows.get(uid)))
    unexpected = sorted(set(rows) - expected)
    return dict(stage=name, expected=declared_count if declared_count is not None else len(expected),
                enumerated=len(expected), observed_ok=statuses.get("ok", 0), statuses=dict(statuses),
                unresolved=missing, unexpected=unexpected,
                complete=not missing and not unexpected and (declared_count is None or len(expected) == declared_count))


def _valid_metrics(metrics):
    if not isinstance(metrics, dict):
        return False
    return (common._finite(metrics.get("psnr_db")) or
            (metrics.get("psnr_db") is None and metrics.get("psnr_infinite") is True)) and all(
        common._finite(metrics.get(k)) for k in ("ssim_rgb", "lpips")) and (
            0 <= metrics["ssim_rgb"] <= 1 and metrics["lpips"] >= 0)


def _bound_word(value):
    word = common._word(value)
    return word is not None and 0 <= word < 2**32


def _bound_bits(value):
    return isinstance(value, list) and len(value) == 100 and all(type(v) is int and v in (0, 1) for v in value)


def bound_evidence_complete(row, payload, owners, marked):
    """Required VINE-B observations, including references even after no-read.

    This validates saved-field availability, not neural correctness or a new
    scientific threshold. Exact references are inapplicable to C0/beta calls.
    """
    if marked and (not isinstance(payload, dict) or not all(_bound_word(payload.get(k)) for k in ("q", "h"))
                   or not _bound_bits(payload.get("bits"))):
        return False
    for owner in owners.values():
        call = observed((row or {}).get("calls", {}).get(owner))
        raw = (call or {}).get("raw", {})
        if not isinstance(raw, dict) or not isinstance(raw.get("native"), dict):
            return False
        decoded = raw.get("carrier_decode")
        native = raw["native"].get("raw")
        if not isinstance(decoded, dict) or not isinstance(native, dict) or not _bound_bits(native.get("decoded_message")):
            return False
        probs = native.get("probabilities")
        if not isinstance(probs, list) or len(probs) != 100 or not all(common._finite(v) and 0 <= v <= 1 for v in probs):
            return False
        status, count = decoded.get("status"), decoded.get("candidates")
        if (status not in ("unique", "no_codeword", "ambiguous") or type(count) is not int or not 0 <= count <= 41449
                or decoded.get("candidates_examined") != 41449 or decoded.get("radius") != 4
                or type(decoded.get("unique")) is not bool
                or decoded["unique"] != (count == 1)
                or status != ("unique" if count == 1 else "no_codeword" if count == 0 else "ambiguous")):
            return False
        if decoded["unique"] and (not all(_bound_word(decoded.get(k)) for k in ("q", "h"))
                                  or type(decoded.get("distance")) is not int or not 0 <= decoded["distance"] <= 4):
            return False
        if marked and owner == owners["positive"]:
            delivery = call.get("delivery")
            if not isinstance(delivery, dict):
                return False
            for field, width in (("raw_payload", 100), ("raw_q", 32), ("raw_tag", 36), ("raw_masked_h", 32)):
                errors, accuracy = delivery.get(field+"_bit_errors"), delivery.get(field+"_accuracy")
                if type(errors) is not int or not 0 <= errors <= width or not common._finite(accuracy) or not 0 <= accuracy <= 1:
                    return False
            if any(type(delivery.get(k)) is not bool for k in ("raw_payload_exact", "corrected_payload_exact")):
                return False
            h_errors = delivery.get("decoded_h_bit_errors")
            if decoded["unique"] and (type(h_errors) is not int or not 0 <= h_errors <= 32):
                return False
    return True


def _analyze_profile(config, manifest, prepared, producers, detections, qualities, *, resource_stop=False, tails=()):
    sources = [str(r["source_id"]) for r in manifest["screen_donors"]]
    targets = {str(r["source_id"]) for r in manifest["screen_targets"]}
    if len(sources) != config["screen_n"] or len(set(sources)) != len(sources):
        raise ValueError("Frozen screen source count mismatch")
    pairs = prepared.get("pairs", []) if prepared else []
    selection_ok = (len(pairs) == len(sources) and [str(p.get("donor")) for p in pairs] == sources and
                    {str(p.get("target")) for p in pairs} == targets)
    if prepared and not selection_ok:
        raise ValueError("Prepared pairing does not match frozen development inventory")
    pairs = [dict(p, donor=str(p["donor"]), target=str(p["target"])) for p in pairs]
    expected = expected_inventory(config, sources, pairs)
    all_producers = {}
    inventory = []
    for stage, ids in expected.items():
        rows = producers.get(stage, {})
        inventory.append(inventory_row(stage, ids, rows, len(sources)*len(config["arms"])*7 if stage == "threats" else None))
        overlap = set(all_producers).intersection(rows)
        if overlap:
            raise ValueError("Producer journals overlap")
        all_producers.update(rows)
    methods = [a for a in config["arms"] if a != "unmarked"]
    # Reader inventory is planned independently of successful producer outputs.
    detect_expected = []
    item_arms = {}
    for sid in sources:
        for arm in config["arms"]:
            item_arms[f"clean:{sid}:{arm}"] = arm
            for c in config["cells"]:
                for seed in config["seeds"]:
                    item_arms[f"native:{c['id']}:{sid}:{seed}:{arm}"] = arm
            for t in config["secondary"]["transforms"]:
                item_arms[f"secondary:{t['id']}:{sid}:{arm}"] = arm
    for p in pairs:
        for arm in config["arms"]:
            for condition in CONDITIONS:
                item_arms[f"threat:{'T5' if condition=='unmodified' else 'T4'}:{p['donor']}:{p['target']}:{arm}:{condition}"] = arm
    for uid, arm in item_arms.items():
        detect_expected.extend(f"det:{m}:{uid}" for m in methods if arm in (m, "unmarked"))
    inventory.append(inventory_row("detect", detect_expected, detections))
    inventory.append(inventory_row("quality", ["quality:"+uid for ids in expected.values() for uid in ids], qualities))
    def detection(uid, method):
        item = observed(all_producers.get(uid))
        row = observed(detections.get(f"det:{method}:{uid}"))
        # Hash equality binds a reader to exactly the emitted saved artifact.
        if not item or not row or not item.get("output", {}).get("sha256") or row.get("input_sha256") != item["output"]["sha256"]:
            return None
        return row
    def outcome(uid, method, rule, owner=None, mode=None):
        row = detection(uid, method)
        if not row:
            return None
        owner = owner or config["owners"]["positive"]
        call = row.get("modes", {}).get(mode) if mode else row.get("calls", {}).get(owner)
        return endpoint(call, all_producers[uid].get("payload"), rule)
    def metrics(uid):
        item = observed(all_producers.get(uid))
        row = observed(qualities.get("quality:"+uid))
        if not item or not row or not item.get("output", {}).get("sha256") or row.get("input_sha256") != item["output"]["sha256"]:
            return None
        q = row.get("total")
        return q if _valid_metrics(q) else None
    native, native_sources = [], []
    native_index = {}
    for arm in (a for a in INTERNAL if a in config["arms"]):
        for cell in config["cells"]:
            for rule in RULES:
                values = [[outcome(f"native:{cell['id']}:{s}:{seed}:{arm}", arm, rule) for seed in config["seeds"]] for s in sources]
                for sid, vs in zip(sources, values):
                    lower, upper = common.majority_bounds(vs)
                    native_sources.append(dict(arm=arm, cell=cell["id"], rule=rule, source=sid,
                                               lower=lower, upper=upper, seed_values=vs, seeds=config["seeds"]))
                row = dict(arm=arm, cell=cell["id"], rule=rule, **source_bounds(values))
                row.update(seed_calls=count_bounds(v for vs in values for v in vs))
                native.append(row)
                native_index[arm, cell["id"], rule] = row
    gates, gains = [], []
    candidate = config["candidate"]
    d = config["decision"]
    for rule in d["rules"]:
        for cell in d["foreign_cells"]:
            c = native_index[candidate, cell, rule]
            gates.append(minimum_gate(f"{rule}:{cell}:absolute", c["lower"], c["upper"], d["absolute_foreign_count_min"]))
            for comparator in (*d["gain_comparators"], *d["ablation_arms"]):
                b = native_index[comparator, cell, rule]
                lower, upper = c["lower"]-b["upper"], c["upper"]-b["lower"]
                is_ablation = comparator in d["ablation_arms"]
                required = d["gain_over_each_ablation" if is_ablation else "gain_over_f5"][cell]
                primary = not is_ablation or d["ablation_gains_primary"]
                gate = minimum_gate(f"{rule}:{cell}:gain:{comparator}", lower, upper, required)
                gains.append(dict(rule=rule, cell=cell, candidate=candidate, comparator=comparator,
                                  lower=lower, upper=upper, denominator=len(sources), required=required,
                                  selection_weight=int(primary), status=gate["status"]))
                if primary: gates.append(gate)
        cell = d["retained_cell"]
        c, b = native_index[candidate, cell, rule], native_index["f5-r2", cell, rule]
        lower, upper = c["lower"]-b["upper"], c["upper"]-b["lower"]
        gains.append(dict(rule=rule, cell=cell, candidate=candidate, comparator="f5-r2", lower=lower, upper=upper, denominator=len(sources)))
        gates.append(minimum_gate(f"{rule}:{cell}:retained", lower, upper, -d["max_retained_loss"]))
    clean = []
    for arm in (a for a in INTERNAL if a in config["arms"]):
        f = count_bounds(outcome(f"clean:{s}:{arm}", arm, "F") for s in sources)
        qvals = [metrics(f"clean:{s}:{arm}") for s in sources]
        q = count_bounds(common.strict_quality(v) if v is not None else None for v in qvals)
        clean.append(dict(arm=arm, clean_F=f, strict_quality=q))
        if arm in d["quality_writers"]:
            gates.append(minimum_gate(f"clean_F:{arm}", f["lower"], f["upper"], d["clean_F_count_min_each_new_writer"]))
            gates.append(minimum_gate(f"strict_quality:{arm}", q["lower"], q["upper"], len(sources)))
    paired = []
    for metric in ("psnr_db", "lpips"):
        values = []
        for sid in sources:
            a, b = metrics(f"clean:{sid}:{candidate}"), metrics(f"clean:{sid}:{d['quality_comparator']}")
            # Infinite PSNR identity comparisons cannot yield an unambiguous
            # finite paired delta; retain as unresolved, never invent zero.
            if a and b and common._finite(a.get(metric)) and common._finite(b.get(metric)):
                values.append(a[metric]-b[metric])
        median = statistics.median(values) if values else None
        status = "unknown"
        if len(values) == len(sources):
            passed = median >= d["paired_median_psnr_delta_min"] if metric == "psnr_db" else median <= d["paired_median_lpips_delta_max"]
            status = "pass" if passed else "fail"
        paired.append(dict(metric=metric, candidate=candidate, comparator=d["quality_comparator"], median_observed_delta=median,
                           observed=len(values), denominator=len(sources), status=status))
        gates.append(dict(name="paired_median:"+metric, status=status))
    negatives = []
    # C0/wrong-owner checks cover the whole declared inventory. Secondary
    # outcomes are descriptive and never change the scientific decision.
    primary_uids = expected["clean"] + expected["native"] + expected["threats"]
    for method in (a for a in INTERNAL if a in config["arms"]):
        for kind, arm, owner in (("C0", "unmarked", config["owners"]["positive"]),
                                 ("wrong_owner", method, config["owners"]["wrong"])):
            ids = [uid for uid in primary_uids if item_arms[uid] == arm]
            for rule in ("C", "F"):
                values = [outcome(uid, method, rule, owner) for uid in ids]
                counts = count_bounds(values)
                source_values = []
                for sid in sources:
                    vs = [v for uid, v in zip(ids, values) if (uid.startswith("clean:"+sid+":")) or (uid.startswith(("native:","threat:")) and uid.split(":")[2] == sid)]
                    source_values.append(True if any(v is True for v in vs) else None if any(v is None for v in vs) else False)
                negatives.append(dict(method=method, kind=kind, rule=rule, **counts, source_any_event=count_bounds(source_values)))
                if method == candidate:
                    gates.append(dict(name=f"negative:{kind}:{rule}", status="fail" if counts["lower"] else "unknown" if counts["missing"] else "pass"))
    threats = []
    for method in (a for a in INTERNAL if a in config["arms"]):
        for condition in CONDITIONS:
            for mode in read_modes(config, method):
                eligible, unknown_quality, values, delivery, joint, raw_values = 0, 0, [], [], [], []
                source_status = []
                for p in pairs:
                    uid = f"threat:{'T5' if condition=='unmodified' else 'T4'}:{p['donor']}:{p['target']}:{method}:{condition}"
                    q = metrics(uid)
                    limits = config["threats"]["quality_eligible"]
                    elig = common.quality_eligible(q, limits["psnr_db_gt"], limits["ssim_rgb_gt"], limits["lpips_lt"]) if q else None
                    raw = {r: outcome(uid, method, r, mode=mode) for r in RULES}
                    raw_values.append(raw)
                    delivery.append(raw["Q"])
                    joint.append(raw["D_and_F"])
                    if elig is None:
                        unknown_quality += 1
                        source_status.append(None)
                    elif elig:
                        eligible += 1
                        values.append(raw["D_and_F"])
                        source_status.append(raw["D_and_F"])
                    else:
                        source_status.append(False)
                counts = count_bounds(values)
                # Unresolved quality can conceal an eligible false event.
                threats.append(dict(method=method, condition=condition, mode=mode, pair_denominator=len(sources),
                    eligible=eligible, quality_missing=unknown_quality, ineligible=len(pairs)-eligible-unknown_quality,
                    eligible_false_events=counts, source_any_event=count_bounds(source_status),
                    donor_delivery=count_bounds(delivery), unconditional_pair_success=count_bounds(joint),
                    delivery_conditioned_acceptance=count_bounds(j for q,j in zip(delivery,joint) if q is True),
                    endpoints={r:count_bounds(v[r] for v in raw_values) for r in RULES}))
                if method == candidate and mode == "combined":
                    gates.append(dict(name=f"negative:{condition}:{mode}", status="fail" if counts["lower"] else
                                      "unknown" if unknown_quality or counts["missing"] or len(pairs)!=len(sources) else "pass"))
    # Every standard distortion and external comparator remains descriptive.
    secondary = []
    for arm in (a for a in INTERNAL if a in config["arms"]):
        for t in config["secondary"]["transforms"]:
            for rule in RULES:
                secondary.append(dict(arm=arm, transform=t["id"], control="C1", owner="positive", rule=rule, selection_weight=0,
                    **count_bounds(outcome(f"secondary:{t['id']}:{sid}:{arm}",arm,rule) for sid in sources)))
            for control_arm, owner, label in (("unmarked", config["owners"]["positive"], "C0"),
                                              (arm, config["owners"]["wrong"], "wrong_owner")):
                for rule in ("C", "F"):
                    secondary.append(dict(arm=arm, transform=t["id"], control=label, owner=owner,
                        rule=rule, selection_weight=0,
                        **count_bounds(outcome(f"secondary:{t['id']}:{sid}:{control_arm}",arm,rule,owner) for sid in sources)))
    baselines = []
    for arm in ("wam", "vine-r"):
        fvals, qvals = [], []
        for sid in sources:
            uid = f"clean:{sid}:{arm}"
            row = detection(uid, arm)
            call = observed((row or {}).get("calls",{}).get(config["owners"]["positive"]))
            val = (call or {}).get("presence",{}).get("present")
            fvals.append(val if type(val) is bool else None)
            q = metrics(uid)
            qvals.append(common.strict_quality(q) if q else None)
        clean.append(dict(arm=arm, known_message_presence=count_bounds(fvals), strict_quality=count_bounds(qvals), selection_weight=0))
        for cell in config["cells"]:
            values = []
            wrong = []
            for sid in sources:
                seeds = []
                for seed in config["seeds"]:
                    uid = f"native:{cell['id']}:{sid}:{seed}:{arm}"
                    row = detection(uid, arm)
                    call = observed((row or {}).get("calls",{}).get(config["owners"]["positive"]))
                    value = (call or {}).get("presence",{}).get("present")
                    seeds.append(value if type(value) is bool else None)
                    v = (call or {}).get("wrong_message_presence",{}).get("present")
                    wrong.append(v if type(v) is bool else None)
                values.append(seeds)
            baselines.append(dict(arm=arm, cell=cell["id"], rule="known_message_presence", **source_bounds(values),
                                  wrong_message_calls=count_bounds(wrong), selection_weight=0))
        # Preserve all baseline control, clean, attack and standard-distortion
        # calls. A known-message carrier hit is never relabelled D/F binding.
        for stage, ids in expected.items():
            for control_arm in (arm, "unmarked"):
                selected = [uid for uid in ids if item_arms[uid] == control_arm]
                presence, wrong = [], []
                for uid in selected:
                    row = detection(uid, arm)
                    call = observed((row or {}).get("calls",{}).get(config["owners"]["positive"]))
                    for key, vals in (("presence",presence),("wrong_message_presence",wrong)):
                        v = (call or {}).get(key,{}).get("present")
                        vals.append(v if type(v) is bool else None)
                baselines.append(dict(arm=arm, stage=stage, control="C0" if control_arm=="unmarked" else "C1",
                    rule="known_message_presence", call_presence=count_bounds(presence),
                    wrong_message_calls=count_bounds(wrong), selection_weight=0))
    # A status alone cannot certify valid, hash-bound reader/quality evidence.
    # Inventory coverage includes every descriptive baseline and distortion.
    evidence_issues = []
    for uid, arm in item_arms.items():
        if metrics(uid) is None:
            evidence_issues.append("quality:"+uid)
        for method in methods:
            if arm not in (method, "unmarked"):
                continue
            row = detection(uid, method)
            if method in INTERNAL:
                usable = row and all(outcome(uid,method,r,owner) is not None for owner in config["owners"].values() for r in ("C","F"))
                if method == "vine-b":
                    payload = (all_producers.get(uid) or {}).get("payload")
                    usable = usable and bound_evidence_complete(row, payload, config["owners"], arm == method)
                    if arm == method:
                        usable = usable and all(outcome(uid,method,r) is not None for r in RULES)
                if uid.startswith("threat:"):
                    # Ablation values have zero selection weight, but every
                    # frozen read mode must still have usable observations.
                    usable = usable and all(outcome(uid,method,r,mode=mode) is not None
                        for mode in read_modes(config, method) for r in ("C","F"))
            else:
                call = observed((row or {}).get("calls",{}).get(config["owners"]["positive"]))
                usable = call and all(type(call.get(k,{}).get("present")) is bool for k in ("presence","wrong_message_presence"))
            if not usable:
                evidence_issues.append(f"det:{method}:{uid}")
    inventory_complete = selection_ok and not tails and not evidence_issues and all(r["complete"] for r in inventory)
    label = verdict(gates, inventory_complete, resource_stop)
    numerical_thesis_status = article.conjunction(gates)
    article_report = article.evaluate(config, native, clean, negatives, threats,
        {arm: [metrics(f"clean:{sid}:{arm}") for sid in sources] for arm in (candidate, "vine-b")},
        label, inventory_complete)
    article_report["numerical_thesis_gate_status"] = numerical_thesis_status
    bound_delivery = []
    issue_set = set(evidence_issues)
    for uid, arm in item_arms.items():
        if arm not in ("vine-b", "unmarked"):
            continue
        row = detection(uid, "vine-b")
        call = observed((row or {}).get("calls", {}).get(config["owners"]["positive"]))
        raw = (call or {}).get("raw")
        decoded = raw.get("carrier_decode") if isinstance(raw, dict) else None
        decoded = decoded if isinstance(decoded, dict) else {}
        delivery_status = "missing" if call is None else "invalid" if f"det:vine-b:{uid}" in issue_set else "ok"
        bound_delivery.append(dict(item=uid, arm=arm, status=delivery_status,
            semantic_codeword_status=decoded.get("status"), candidates=decoded.get("candidates"),
            semantic_correction_distance=decoded.get("distance"),
            evaluator_delivery=(call or {}).get("delivery"),
            raw_h_role="conditional unmasked field; no error correction or independent presence test"))
    return dict(schema="tifs-stage-s-analysis-v1", gate_profile=config["gate_profile"], verdict=label, gates=gates, inventory=inventory,
                numerical_thesis_gate_status=numerical_thesis_status,
                numerical_thesis_gate_scope="Fixed F6 numeric gates only; pass does not waive complete inventory or authorize GO.",
                article=article_report, bound_carrier_delivery=bound_delivery,
                inventory_complete=inventory_complete, prepared_selection_available=selection_ok,
                incomplete_journal_tails=list(tails), resource_stop=bool(resource_stop), native=native, native_sources=native_sources, gains=gains,
                unusable_evidence=evidence_issues,
                clean=clean, paired_medians=paired, negatives=negatives, threats=threats,
                secondary=secondary, external_baselines=baselines,
                go_scope=d["go_scope"], source_units=len(sources),
                threat_distinctness_labels=dict(Counter(p.get("distinctness","human_label_missing") for p in pairs)),
                side_information=dict(internal="Public owner label; suspect-derived features; original q/h evaluator references only; unchanged F5 reader for F6.",
                    vine_b="Suspect plus claimed owner and same public-derived profile key, CPU seven-view CLIP, VINE decoder; no original or registry. Public tag is redundancy, not authentication. Raw h field is conditional on semantic read.",
                    external="Known per-source public deterministic payload; wrong-message presence is distinct from a wrong owner.",
                    threats="Donor q/h evaluator reference; whole recipient protected; published patch and known-clean residual access reported separately.",
                    quality="Original donor or recipient reference; not supplied to operational detector."),
                limitations=["Fixed development cohort; no held-out or population security conclusion.",
                    "Human operational-distinctness labels remain missing unless separately supplied; no binding generalization conclusion.",
                    "Zero events do not establish rare-event security; sources, not calls, are independent units.",
                    "Eight distortions and unbound WAM/VINE-R have zero selection weight; VINE-B affects only the separate article screen."],
                zero_event_source_upper_95=1-math.pow(.05, 1/len(sources)))


def analyze(config, manifest, prepared, producers, detections, qualities, *, resource_stop=False, tails=()):
    """Report both prospective profiles; only the pre-output choice is effective."""
    import tifs_gate_profiles as profiles
    effective = config.get("gate_profile", "round1")
    if effective not in profiles.PROFILES:
        raise ValueError("Unknown effective gate profile")
    reports = {name:_analyze_profile(profiles.profile_config(config,name), manifest, prepared,
        producers, detections, qualities, resource_stop=resource_stop, tails=tails) for name in profiles.PROFILES}
    result = reports[effective]
    result["gate_profiles"] = {name:{key:report[key] for key in (
        "gate_profile","verdict","gates","gains","paired_medians","article",
        "numerical_thesis_gate_status","inventory_complete","resource_stop")} for name,report in reports.items()}
    for name, report in result["gate_profiles"].items():
        report["role"] = "effective_pre_output_choice" if name == effective else "counterfactual_diagnostic_only"
    result["execution_choices"] = config.get("execution_choices", {})
    result["profile_policy"] = "Both reported; no outcome-dependent profile switch. Default round1; proposed requires external pre-output choice."
    return result


def mark_provenance_missing(report):
    """Keep numerical results but never export article GO without a run seal."""
    report["inventory_complete"] = False
    report["verdict"] = verdict(report["gates"], False, report["resource_stop"])
    article_report = report["article"]
    article_report["thesis_verdict"] = report["verdict"]
    article_report["verdict"] = "RESOURCE_STOP" if report["verdict"] == "RESOURCE_STOP" else "INCOMPLETE"
    article_report["numerical_parity"] = False
    article_report["numerical_parity_status"] = "unknown"
    article_report["flags"] = [f for f in article_report["flags"] if f != "NUMERICAL_PARITY"]
    for profile in report.get("gate_profiles", {}).values():
        mark_provenance_missing(profile)


def write_report(report, destination):
    destination = Path(destination)
    common.atomic_json(destination/"analysis.json", report)
    common.atomic_json(destination/"article-decision.json", report["article"])
    common.atomic_json(destination/"gate-profile-decisions.json", report["gate_profiles"])
    for name in ("gates", "inventory", "native", "native_sources", "gains", "clean", "paired_medians", "negatives", "threats", "secondary", "external_baselines", "bound_carrier_delivery"):
        rows = report[name]
        if not rows:
            continue
        keys = list(dict.fromkeys(k for row in rows for k in row))
        with (destination/(name+".csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow({k:json.dumps(v,sort_keys=True,allow_nan=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--user-choice", type=Path)
    parser.add_argument("--selection", type=Path)
    args = parser.parse_args(argv)
    import tifs_gate_profiles as profiles
    import tifs_stage_p as stage_p
    config = profiles.load_execution_config(args.config,receipt_path=args.user_choice,selection_path=args.selection)
    if config.get("stage_p"):
        raise ValueError("Use the Stage P selector for Stage P outputs")
    manifest_path = Path(config["source_manifest"])
    if not manifest_path.is_absolute():
        manifest_path = ROOT/manifest_path
    if common.sha256_file(manifest_path) != config["source_manifest_sha256"]:
        raise ValueError("Frozen source manifest hash mismatch")
    manifest = common.load_json(manifest_path)
    prepared = common.load_json(args.out/"prepared.json") if (args.out/"prepared.json").exists() else None
    producers, tails = {}, []
    for stage in ("clean", "native", "secondary", "threats"):
        producers[stage], t = merge_journals([args.out/(stage+".jsonl")])
        tails.extend(t)
    detections, t = merge_journals(args.out.glob("detect-*.jsonl")); tails.extend(t)
    qualities, t = merge_journals(args.out.glob("quality-*.jsonl")); tails.extend(t)
    resource = any(common.load_json(p).get("status") == "RESOURCE_STOP" for p in args.out.glob("RESOURCE_STOP*.json"))
    report = analyze(config, manifest, prepared, producers, detections, qualities, resource_stop=resource, tails=tails)
    seal_path = args.out/"identity.json"
    report["provenance_available"] = seal_path.is_file()
    if seal_path.is_file():
        seal = common.load_json(seal_path)
        if (seal.get("config_sha256") != common.sha256_file(args.config) or
            seal.get("effective_config_sha256") != stage_p.digest(config) or
            seal.get("execution_choices") != config["execution_choices"] or
            seal.get("source_manifest_sha256") != common.sha256_file(manifest_path) or seal.get("rehearsal") is not False):
            raise ValueError("Run provenance does not match frozen screen config/sources")
        pinned = seal.get("code", {})
        own = Path(__file__).resolve()
        if not any(Path(p).name == own.name and value == common.sha256_file(own) for p,value in pinned.items()):
            raise ValueError("Analyzer code does not match run identity")
        report["identity_sha256"] = common.sha256_file(seal_path)
    else:
        mark_provenance_missing(report)
    write_report(report, args.destination or args.out/"analysis")
    print(report["verdict"])
    return {"GO":0,"SCIENTIFIC_KILL":2,"RESOURCE_STOP":3,"INCOMPLETE":4}[report["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
