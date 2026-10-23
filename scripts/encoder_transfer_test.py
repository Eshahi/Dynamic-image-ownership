"""Frozen development encoder-transfer study; plan/analyze are CPU/stdlib only.

Scientific execution is a separate, explicitly requested stage-2 action. Nothing
imports torch, opens an image or downloads a model at module import time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
RULES = ("S", "C", "Q", "J", "H", "D", "F", "A")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def write(path, value):
    # Same atomic replacement convention as registry_step1_transfer.write.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def binomial_threshold(bits, numerator=1, denominator=10000):
    """Smallest k with exact P[Bin(bits,.5)>=k] <= numerator/denominator."""
    if type(bits) is not int or bits < 1 or not 0 < numerator < denominator:
        raise ValueError("Positive bit count and probability strictly between 0 and 1 required")
    for k in range(bits + 2):
        tail = sum(math.comb(bits, j) for j in range(k, bits + 1))
        if tail * denominator <= numerator * 2**bits:
            return k
    raise AssertionError("unreachable")


def message(source_id, bits, seed=20261019):
    """Public, fixed per-source payload, independent of pixels and outcomes."""
    raw = hashlib.shake_256(f"encoder-transfer-v1:{seed}:{source_id}".encode()).digest((bits + 7) // 8)
    return [(byte >> shift) & 1 for byte in raw for shift in range(7, -1, -1)][:bits]


def presence(decoded, expected):
    if decoded is None:
        return dict(matches=None, bits=len(expected), accuracy=None, present=False)
    if len(decoded) != len(expected) or any(x not in (0, 1, False, True) for x in decoded):
        raise ValueError("Native binary payload length/value mismatch")
    k = sum(bool(a) == bool(b) for a, b in zip(decoded, expected))
    return dict(matches=k, bits=len(expected), accuracy=k / len(expected),
                threshold=binomial_threshold(len(expected)), present=k >= binomial_threshold(len(expected)))


def endpoints(detection, payload=None):
    # Reuse the frozen historical predicates literally, including C's definition.
    from m1b_e3_s1_analysis import predicates
    return predicates(detection, payload)


def majority(seed_values, seeds=(12, 13, 14)):
    if len(seeds) != 3 or len(set(seeds)) != 3 or set(seed_values) - set(seeds):
        raise ValueError("Exactly the three frozen seed identities required")
    return sum(seed_values.get(seed) is True for seed in seeds) >= 2


def decision(n, f5, c0_false, wrong_false, unresolved_negatives, external_counts):
    if type(n) is not int or not 60 <= n <= 120 or any(type(v) is not int or not 0 <= v <= n for v in [f5, *external_counts.values()]):
        raise ValueError("Invalid fixed-source decision counts")
    if any(type(v) is not int or v < 0 for v in (c0_false, wrong_false, unresolved_negatives)):
        raise ValueError("Invalid negative-call inventory")
    transfer_cut, margin = (3*n + 3)//4, (n + 19)//20
    if 2*f5 < n:
        label, route = "FAILS", "ROUTE C"
    elif f5 >= transfer_cut and c0_false == wrong_false == unresolved_negatives == 0:
        label = "TRANSFERS"
        route = ("ROUTE UNDECIDED" if not external_counts else
                 "ROUTE A" if f5 >= max(external_counts.values()) - margin else "ROUTE B")
    else:
        label, route = "PARTIAL", "ROUTE UNDECIDED"
    return dict(label=label, route=route, n=n, f5=f5, transfer_cut=transfer_cut,
                fail_below=n/2, margin=margin, best_external=max(external_counts.values(), default=None),
                c0_false=c0_false, wrong_owner_false=wrong_false, unresolved_negatives=unresolved_negatives)


def cp_interval(k, n, alpha=.05):
    """Exact binomial-tail inversion by bisection; source units, not seed calls."""
    if type(k) is not int or type(n) is not int or not 0 < alpha < 1:
        raise ValueError("Integer counts and alpha strictly between zero and one required")
    if not 0 <= k <= n or n < 1:
        return None
    def tail(p, start, stop):
        return math.fsum(math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(start, stop))
    def solve(target, start, stop, increasing):
        low, high = 0., 1.
        for _ in range(65):
            mid = (low + high)/2
            if (tail(mid, start, stop) < target) == increasing:
                low = mid
            else:
                high = mid
        return (low+high)/2
    return [0. if k == 0 else solve(alpha/2, k, n+1, True),
            1. if k == n else solve(alpha/2, 0, k+1, False)]


def sign_test(left, right):
    if len(left) != len(right):
        raise ValueError("Paired source vectors required")
    if any(type(v) is not bool for v in [*left,*right]):
        raise ValueError("Paired binary source indicators required")
    wins = sum(a and not b for a,b in zip(left,right))
    losses = sum(b and not a for a,b in zip(left,right))
    d = wins+losses
    return dict(wins=wins, losses=losses, ties=len(left)-d,
                both_success=sum(a and b for a,b in zip(left,right)),
                both_failure=sum(not a and not b for a,b in zip(left,right)),
                paired_difference=(wins-losses)/len(left) if left else None,
                p_two_sided=min(1., 2*sum(math.comb(d,k) for k in range(min(wins,losses)+1))/2**d) if d else 1.,
                status="exploratory, no decision-rule override")


class Journal:
    """Historical newline-event resume convention; retain failures and torn tails."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.latest = {}
        if self.path.exists():
            raw = self.path.read_bytes()
            if raw and not raw.endswith(b"\n"):
                cut = raw.rfind(b"\n")+1
                self.path.with_name(f"interrupted-journal-{time.time_ns()}.bin").write_bytes(raw[cut:])
                self.path.write_bytes(raw[:cut])
            for line in self.path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                self.latest[row["id"]] = row

    def append(self, row):
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, allow_nan=False)+"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.latest[row["id"]] = row.copy()

    def done(self, rid):
        # Scientific errors and safety blocks are terminal, never outcome-selected retries.
        return self.latest.get(rid, {}).get("status") in ("ok", "error", "safety_blocked", "input_missing")


def unit_id(source_id, channel, strength, seed, arm):
    return f"{channel}:{source_id}:{arm}:{strength}:{seed}"


def channel_arms(config, channel):
    """Arms evaluated on a channel; a channel without an `arms` list keeps every arm.

    Amendment 1d (stage 2a) scopes the approved extra baselines to their proposal cells.
    The frozen core config has no per-channel lists, so its schedule is unchanged.
    """
    if channel is None or channel.get("id") == "clean" or channel.get("arms") is None:
        return list(config["arms"])
    return [arm for arm in config["arms"] if arm in channel["arms"]]


def channel_spec(config, cid):
    if cid == "clean":
        return {"id": "clean"}
    return next(c for c in config["channels"] if c["id"] == cid)


def read_methods(config, unit):
    """Detectors that read a saved output: C0 is shared by every in-scope detector."""
    return channel_arms(config, channel_spec(config, unit["channel"])) if unit["arm"] == "unmarked" else [unit["arm"]]


def plan(config, sources, smoke=False):
    selected = sources["smoke" if smoke else "sources"]
    arms = ["unmarked", *config["arms"]]
    for source in selected:
        for arm in arms:
            yield dict(id=unit_id(source["source_id"], "clean", None, None, arm),
                       source_id=source["source_id"], channel="clean", strength=None, seed=None,
                       arm=arm, control="C0" if arm == "unmarked" else "C1")
    for channel in config["channels"]:
        if not channel.get("enabled", True):
            continue
        arms = ["unmarked", *channel_arms(config, channel)]
        for strength in channel.get("strengths", [None]):
            for source in selected:
                for seed in channel.get("seeds", [None]):
                    for arm in arms:
                        yield dict(id=unit_id(source["source_id"], channel["id"], strength, seed, arm),
                                   source_id=source["source_id"], channel=channel["id"], strength=strength,
                                   seed=seed, arm=arm, control="C0" if arm == "unmarked" else "C1")


def load_contract(path):
    config = read(path)
    if config.get("data_split") != "development" or config.get("schema") != "encoder-transfer-v1":
        raise ValueError("Only the frozen development contract is accepted")
    source_path = ROOT / config["sources_file"]
    if digest(source_path) != config["sources_sha256"]:
        raise ValueError("Frozen source list hash mismatch")
    for name in ("asset_plan","profile"):
        if digest(ROOT/config[name+"_file"])!=config[name+"_sha256"]:
            raise ValueError(f"Frozen {name} hash mismatch")
    sources = read(source_path)
    if len(sources["sources"]) != config["n"] or not 60 <= config["n"] <= 120:
        raise ValueError("Frozen n mismatch")
    all_sources = sources["sources"] + sources["smoke"]
    if len({r["source_id"] for r in all_sources}) != len(all_sources):
        raise ValueError("Duplicate or overlapping smoke source")
    if any(s.get("data_split") != "development" for s in all_sources):
        raise ValueError("Non-development source refused")
    return config, sources


def call_value(row, method, owner, key):
    # Detector calls are journaled before the independent quality pass. Keep
    # observed calls after an interruption even if row-level work is incomplete.
    if not row or row.get("status") not in ("generated", "ok"):
        return None
    call = row.get("detections", {}).get(method, {}).get(owner)
    if not call or call.get("status") != "ok":
        return None
    if key == "presence":
        return call.get("presence", {}).get("present")
    return call.get("endpoints", {}).get(key)


LEGACY_REDUCTIONS = ("R2", "D2", "strength_0.1")


def reduction_steps(config):
    """Ordered, preregistered budget reductions (legacy core order unless amended)."""
    return tuple(config.get("budget", {}).get("reduction_steps", LEGACY_REDUCTIONS))


def apply_reduction(config, step):
    """Apply one preregistered reduction in place; never chosen from outcomes."""
    if step == "strength_0.1":
        for channel in config["channels"]:
            if channel.get("kind") == "rinse":
                channel["enabled"] = False
            if "strengths" in channel:
                channel["strengths"] = [x for x in channel["strengths"] if x != .1]
    elif step.startswith("arm:"):
        arm = step[4:]
        if arm in config.get("protected_arms", ()):
            raise ValueError(f"Protected arm cannot be dropped: {arm}")
        config["arms"] = [a for a in config["arms"] if a != arm]
        for channel in config["channels"]:
            if channel.get("arms") is not None:
                channel["arms"] = [a for a in channel["arms"] if a != arm]
    else:
        cid = step[8:] if step.startswith("channel:") else step
        if cid in config.get("protected_channels", ()):
            raise ValueError(f"Protected channel cannot be dropped: {cid}")
        for channel in config["channels"]:
            if channel["id"] == cid:
                channel["enabled"] = False
    return config


def validate_effective(original, effective):
    """Only the preregistered, timing-driven reductions, applied in order, may differ."""
    import copy
    candidate = copy.deepcopy(original)
    if candidate == effective:
        return
    for stage in reduction_steps(original):
        apply_reduction(candidate, stage)
        if candidate == effective:
            return
    raise ValueError("Effective configuration is not a permitted frozen budget reduction")


def contract_status(config):
    """Execution gate: the reviewed freeze, or a recorded pre-outcome user amendment of it."""
    status = config.get("status")
    if status == "frozen-after-independent-review":
        return status
    if status == "user-amended-pre-outcome":
        amendment = config.get("amendment") or {}
        base = ROOT / amendment.get("base_config_file", "")
        if not base.is_file() or digest(base) != amendment.get("base_config_sha256"):
            raise ValueError("Amended contract does not match its recorded reviewed base")
        if read(base).get("status") != "frozen-after-independent-review":
            raise ValueError("Amendment base is not the independently reviewed freeze")
        if amendment.get("pre_outcome") is not True:
            raise ValueError("Only pre-outcome amendments may execute")
        return status
    raise ValueError("Scientific execution requires the reviewed freeze or a recorded pre-outcome amendment of it")


def analyze(config, sources, rows):
    # Inventory is generated from the frozen plan, never from observed survivors.
    expected = list(plan(config, sources))
    known = {r["id"] for r in expected}
    if set(rows)-known:
        raise ValueError("Rows outside the frozen full-run schedule")
    ids = [s["source_id"] for s in sources["sources"]]
    cells, vectors = {}, {}
    for channel in [{"id":"clean"},*config["channels"]]:
        if not channel.get("enabled", True):
            continue
        cid = channel["id"]
        for strength in channel.get("strengths", [None]):
            seeds = channel.get("seeds", [None])
            for method in channel_arms(config, channel):
                keys = RULES if method in ("f5-r2", "v5-r3") else ("presence",)
                for key in keys:
                    successful, optimistic, missing, observed_successes = [], [], 0, 0
                    for sid in ids:
                        values = {seed: call_value(rows.get(unit_id(sid,cid,strength,seed,method)),method,ALPHA,key) for seed in seeds}
                        missing += sum(v is None for v in values.values())
                        observed_successes += sum(v is True for v in values.values())
                        successful.append(majority(values, tuple(seeds)) if len(seeds)==3 else values[None] is True)
                        optimistic.append(sum(v is not False for v in values.values()) >= (2 if len(seeds)==3 else 1))
                    name=f"{method}/{cid}/{strength}/{key}"
                    vectors[name]=successful
                    k=sum(successful)
                    cells[name]=dict(positive_sources=k, planned_sources=len(ids), missing_calls=missing,
                                    observed_positive_calls=observed_successes,planned_calls=len(ids)*len(seeds),
                                    optimistic_sources_missing_as_success=sum(optimistic),
                                    proportion=k/len(ids), cp95=cp_interval(k,len(ids)),
                                    interval_scope="hypothetical independent exchangeable sources; development convenience cohort")
    negatives = {}
    r1_arms = channel_arms(config, channel_spec(config, "R1"))
    for method in r1_arms:
        endpoint = "A" if method in ("f5-r2", "v5-r3") else "presence"
        for control in ("C0", "wrong_owner"):
            if control == "wrong_owner" and method not in ("f5-r2", "v5-r3"):
                continue
            selected = [u for u in expected if u["channel"] == "R1" and
                        u["arm"] == ("unmarked" if control == "C0" else method)]
            values=[call_value(rows.get(u["id"]),method,ALPHA if control=="C0" else BETA,endpoint) for u in selected]
            negatives[f"{method}/{control}"]=dict(planned=len(values), observed=sum(v is not None for v in values),
                                                 positives=sum(v is True for v in values), unresolved=sum(v is None for v in values))
    # The route maximum B uses only the frozen external arms (WAM, VINE-R); amendment-1d
    # baselines are reported beside them and never enter the label.
    decision_arms=config.get("decision_external_arms",["wam","vine-r"])
    external={m:cells[f"{m}/R1/0.2/presence"]["positive_sources"] for m in r1_arms if m in decision_arms}
    c0, wrong = negatives["f5-r2/C0"], negatives["f5-r2/wrong_owner"]
    primary = cells["f5-r2/R1/0.2/C"]
    verdict = decision(config["n"], primary["positive_sources"],c0["positives"],wrong["positives"],c0["unresolved"]+wrong["unresolved"],external)
    def paired(method):
        name=f"{method}/R1/0.2/{'C' if method=='v5-r3' else 'presence'}"
        result=sign_test(vectors["f5-r2/R1/0.2/C"],vectors[name])
        result["observed_calls"]={"f5-r2":primary["planned_calls"]-primary["missing_calls"],
                                  method:cells[name]["planned_calls"]-cells[name]["missing_calls"]}
        return result
    holm_arms=[m for m in config.get("holm_arms",[m for m in config["arms"] if m!="f5-r2"]) if m in r1_arms]
    comparisons={}
    for method in holm_arms:
        result=paired(method)
        available=all(result["observed_calls"].values())
        result["holm_internal_p"]=result["p_two_sided"] if available else 1.
        if not available:
            result.update(status="not_estimable_wholly_unavailable_comparison",p_two_sided=None)
        comparisons[method]=result
    family=len(comparisons)
    previous=0.
    for rank,(method,result) in enumerate(sorted(comparisons.items(),key=lambda pair:pair[1]["holm_internal_p"])):
        previous=max(previous,min(1.,(family-rank)*result["holm_internal_p"]))
        result["holm_adjusted_p"]=previous if result["p_two_sided"] is not None else None
        result["holm_family_size"]=family
    descriptive={m:{**paired(m),"status":"descriptive amendment-1d baseline; outside the Holm family and the route rule"}
                 for m in r1_arms if m!="f5-r2" and m not in comparisons}
    from encoder_transfer_reporting import reporting
    return dict(schema="encoder-transfer-metrics-v1", decision=verdict, cells=cells, primary_negatives=negatives,
                reporting=reporting(config,sources,rows,vectors),
                paired_primary_comparisons=comparisons, descriptive_comparisons=descriptive,
                stage=config.get("amendment",{}).get("stage"),
                not_run_by_design=config.get("amendment",{}).get("not_run_by_design",[]),
                planned_units=len(expected), observed_units=len(rows),
                missing_units=len(known-set(rows)),
                terminal_status_counts={s:sum(r.get("status")==s for r in rows.values()) for s in ("ok","generated","error","safety_blocked","input_missing","running")})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--phase",choices=("plan","analyze","prepare","smoke","run"),default="plan")
    parser.add_argument("--assets-root",type=Path)
    parser.add_argument("--instance-start-utc")
    parser.add_argument("--hourly-usd",type=float)
    parser.add_argument("--smoke-dir",type=Path)
    parser.add_argument("--bugfix-note",help="Required provenance when resuming after a committed implementation-only fix")
    args=parser.parse_args()
    config,sources=load_contract(args.manifest)
    if args.phase == "plan":
        units=list(plan(config,sources))
        write(args.output_dir/"planned-units.json",dict(execution=False,manifest_sha256=digest(args.manifest),units=units))
        print(json.dumps(dict(execution=False,planned_units=len(units))))
    elif args.phase == "analyze":
        effective=args.output_dir/"effective-config.json"
        if effective.exists():
            candidate=read(effective)
            validate_effective(config,candidate)
            config=candidate
        journal=Journal(args.output_dir/"rows.jsonl")
        metrics=analyze(config,sources,journal.latest)
        write(args.output_dir/"metrics.json",metrics)
        print(json.dumps(metrics["decision"]))
    else:
        if not args.assets_root or not args.instance_start_utc or not args.hourly_usd:
            parser.error("Stage 2 requires --assets-root, --instance-start-utc and --hourly-usd")
        from encoder_transfer_runtime import execute
        execute(args,config,sources)


if __name__ == "__main__":
    main()
