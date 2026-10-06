"""Endpoints of an M1b COCO512 run, from its journal only (pure; re-runnable on a retained run).

    python scripts/m1b_coco512_analysis.py --run-dir <artifact dir>   # writes metrics/endpoints-reanalysis.json

Pre-declared roles (research/m1b-package.md section 3):
- clean positive (primary): C1 correct-owner `both_match`, 300 sources, one-sided 95% lower bound >= .80;
- clean negatives (primary rule `any_found`, secondary `both_match`): C0 correct, C0 wrong-owner,
  C1 wrong-owner, 300 sources each, one-sided 95% upper bound <= .01;
- T3/T4/T5: descriptive, 30 independent units; repeats (seeds, sizes, claims) are clustered;
  `meets_numerical_target` is not applicable to them.
Missing or invalid observations count adversely; a None metric never passes a target.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import m1b_coco512_worker as W  # noqa: E402

VERSION = "m1b-coco512-analysis-v1"
RULES = ("both_match", "any_found", "delivered", "semantic", "semantic_checked", "semantic_assumed")


def event(det: dict | None, rule: str) -> bool:
    """Event of one detection under a named rule."""
    if rule not in RULES:
        raise ValueError("unknown rule " + rule)
    det = det or {}
    sem, inst = det.get("semantic") or {}, det.get("instance") or {}
    if rule == "both_match":
        return det.get("outcome") == "both_match"
    if rule in ("any_found", "delivered"):
        return bool(sem.get("found") or inst.get("found"))
    ok = bool(sem.get("found") and sem.get("content_match"))
    if rule == "semantic":
        return ok
    if rule == "semantic_checked":
        return ok and bool(sem.get("read"))
    return ok and not sem.get("read")


def inventory(planned: list[str], rows: dict[str, dict]) -> dict:
    counts: dict[str, int] = {}
    for rid in planned:
        state = rows.get(rid, {}).get("outcome", "not_attempted")
        counts[state] = counts.get(state, 0) + 1
    extra = sorted(set(rows) - set(planned))
    return dict(planned=len(planned), states=counts, extra_rows=extra,
                complete=counts.get("not_attempted", 0) == 0 and not extra)


def sign_test(a: int, b: int) -> float | None:
    n = a + b
    if n == 0:
        return None
    k = min(a, b)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def _num(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def _mean(values):
    values = [v for v in (_num(x) for x in values) if v is not None]
    return sum(values) / len(values) if values else None


def quality_summary(qs: list[dict | None], planned: int) -> dict:
    """Counts against PSNR > 35 dB, SSIM > .9, LPIPS < .1; a missing/None metric fails its target."""
    def psnr_ok(q):
        return bool(q) and (q.get("psnr_infinite") is True or (_num(q.get("psnr_db")) or 0) > 35.0)

    def ssim_ok(q):
        return bool(q) and (_num(q.get("ssim_rgb")) or 0) > 0.9

    def lpips_ok(q):
        v = _num((q or {}).get("lpips"))
        return v is not None and v < 0.1
    valid = [q for q in qs if q]
    count = lambda pred: dict(count=sum(1 for q in qs if pred(q)), valid=len(valid), planned=planned)
    lp = [_num(q.get("lpips")) for q in valid]
    return dict(psnr_gt_35=count(psnr_ok), ssim_gt_0_9=count(ssim_ok), lpips_lt_0_1=count(lpips_ok),
                joint=count(lambda q: psnr_ok(q) and ssim_ok(q) and lpips_ok(q)),
                psnr_mean=_mean(q.get("psnr_db") for q in valid), ssim_mean=_mean(q.get("ssim_rgb") for q in valid),
                lpips_mean=_mean(lp), lpips_max=max([v for v in lp if v is not None], default=None))


def analyse(plan: dict, sources: list[dict], rows: dict[str, dict], selected: list[dict] | None) -> dict:
    from m1_confirmatory_endpoints import cell

    planned = W.planned_ids(plan, sources, selected)
    has_det = lambda rid: rows.get(rid, {}).get("outcome") == "completed" and "detection" in rows[rid]

    def obs(rid: str, rule: str):
        return event(rows[rid]["detection"], rule) if has_det(rid) else None

    def rowcell(ids, rule, kind, descriptive=True, role=None):
        value = cell(sorted(ids), {i: obs(i, rule) for i in ids}, event_kind=kind)
        value["event_rule"] = rule
        if role:
            value["role"] = role
        if descriptive:
            value["meets_numerical_target"] = None
            value["unit_note"] = "rows are clustered repeats, not independent units"
        return value

    def cluster(units: dict[str, list[str]], rule: str, kind: str, need: str) -> dict:
        """One observation per independent unit from its repeated rows; missing rows count adversely."""
        per = {}
        for unit, ids in units.items():
            vals = [obs(i, rule) for i in ids]
            vals = [(v if v is not None else kind == "negative_error") for v in vals]
            hits = sum(vals)
            per[unit] = (hits * 2 >= len(vals)) if need == "majority" else (all(vals) if need == "all" else any(vals))
        value = cell(sorted(per), per, event_kind=kind)
        value.update(event_rule=rule, unit_rule=need, independent_units=len(per), meets_numerical_target=None)
        return value

    uids = [s["uid"] for s in sources]
    owner_of = {s["uid"]: s["owner"] for s in sources}
    methods = {}
    for m in W.METHODS:
        out: dict[str, Any] = {}
        clean = dict(C1_correct_both_match=rowcell([f"src:{u}:{m}:clean:C1:correct" for u in uids], "both_match",
                                                   "positive_success", descriptive=False, role="primary"))
        for arm, claim in (("C0", "correct"), ("C0", "wrong"), ("C1", "wrong")):
            ids = [f"src:{u}:{m}:clean:{arm}:{claim}" for u in uids]
            clean[f"{arm}_{claim}_any_found"] = rowcell(ids, "any_found", "negative_error", descriptive=False, role="primary")
            clean[f"{arm}_{claim}_both_match"] = rowcell(ids, "both_match", "negative_error", descriptive=False, role="secondary")
        embeds = [rows.get(f"src:{u}:{m}:embed") for u in uids]
        ok = [r for r in embeds if r and r.get("outcome") == "completed"]
        clean["quality"] = quality_summary([r.get("quality") for r in ok], len(uids))
        clean["quality"]["embed_seconds_mean"] = _mean(r.get("seconds") for r in ok)
        clean["self_verification_both_match"] = sum(1 for r in ok if r.get("self_verification") == "both_match")
        clean["c0_reconstruction"] = "identity for this pixel-additive method: C0-reconstruction cells equal C0-source cells"
        out["clean"] = clean

        t3 = {}
        groups = [("vae", ["vae"])] + [(f"ddim-{s}", [f"ddim-{s}-{sd}" for sd in W.SEEDS]) for s in W.STRENGTHS]
        flat = lambda d: [i for ids in d.values() for i in ids]
        for name, doses in groups:
            pos = {u: [f"t3:{u}:{m}:C1:{d}:correct" for d in doses] for u in plan["t3_uids"]}
            neg_w = {u: [f"t3:{u}:{m}:C1:{d}:wrong" for d in doses] for u in plan["t3_uids"]}
            neg_0 = {u: [f"t3:{u}:{m}:C0:{d}:correct" for d in doses] for u in plan["t3_uids"]}
            entry = dict(rows={r: rowcell(flat(pos), r, "positive_success")
                               for r in ("semantic", "semantic_checked", "semantic_assumed", "both_match")})
            entry["per_seed"] = {d: {r: rowcell([f"t3:{u}:{m}:C1:{d}:correct" for u in plan["t3_uids"]], r, "positive_success")
                                     for r in ("semantic", "semantic_checked")} for d in doses}
            entry["source_majority_semantic"] = cluster(pos, "semantic", "positive_success", "majority")
            entry["source_majority_semantic_checked"] = cluster(pos, "semantic_checked", "positive_success", "majority")
            entry["wrong_owner_any_found_rows"] = rowcell(flat(neg_w), "any_found", "negative_error")
            entry["wrong_owner_any_found_source_any"] = cluster(neg_w, "any_found", "negative_error", "any")
            entry["C0_any_found_rows"] = rowcell(flat(neg_0), "any_found", "negative_error")
            entry["C0_any_found_source_any"] = cluster(neg_0, "any_found", "negative_error", "any")
            t3[name] = entry
        out["t3"] = t3

        pairs = plan["t4_pairs"]
        diff = [p["pair_index"] for p in pairs if owner_of[p["donor_uid"]] != owner_of[p["recipient_uid"]]]
        same = [p["pair_index"] for p in pairs if owner_of[p["donor_uid"]] == owner_of[p["recipient_uid"]]]
        all_k = [p["pair_index"] for p in pairs]
        mk = lambda arm, claim, ks: {str(k): [f"t4:{k}:{m}:{s}:{arm}:{claim}" for s in W.PATCH_SIZES] for k in ks}
        t4 = dict(different_owner_pairs=len(diff), same_owner_pairs=same)
        t4["false_donor_full_attribution_pair_any"] = cluster(mk("marked", "donor", diff), "both_match", "negative_error", "any")
        t4["false_donor_full_attribution_rows"] = rowcell(flat(mk("marked", "donor", diff)), "both_match", "negative_error")
        t4["donor_semantic_consistent_rows"] = rowcell(flat(mk("marked", "donor", diff)), "semantic", "negative_error")
        t4["recipient_claim_any_found_rows"] = rowcell(flat(mk("marked", "recipient", diff)), "any_found", "negative_error")
        t4["donor_delivery_witness_pair_any"] = cluster(mk("marked", "donor", all_k), "delivered", "positive_success", "any")
        t4["sham_any_found_rows"] = rowcell([i for c in ("donor", "recipient") for i in flat(mk("sham", c, all_k))],
                                            "any_found", "negative_error")
        t4["same_owner_pairs_descriptive"] = {str(k): {f"{s}:{c}": (rows.get(f"t4:{k}:{m}:{s}:marked:{c}") or {}).get("detection", {}).get("outcome")
                                                       for s in W.PATCH_SIZES for c in ("donor", "recipient")} for k in same}
        states: dict[str, int] = {}
        for k in all_k:
            for s in W.PATCH_SIZES:
                r = rows.get(f"t4:{k}:{m}:{s}:marked:donor") or {}
                st = (r.get("detection") or {}).get("outcome") if r.get("outcome") == "completed" else r.get("outcome", "absent")
                states[str(st)] = states.get(str(st), 0) + 1
        t4["marked_donor_claim_states"] = states
        out["t4"] = t4

        t5: dict[str, Any] = dict(selected_pairs=None if selected is None else len(selected))
        if selected is not None:
            diff5 = [k for k, p in enumerate(selected) if owner_of[p["left"]] != owner_of[p["right"]]]
            t5["different_owner_pairs"] = len(diff5)
            t5["same_owner_pairs"] = [k for k in range(len(selected)) if k not in diff5]
            for arm in ("C0", "C1"):
                units = {str(k): [f"t5:{k}:{m}:{e}:{arm}" for e in ("a", "b")] for k in diff5}
                t5[f"{arm}_false_full_match_pair_any"] = cluster(units, "both_match", "negative_error", "any") if units else None
                t5[f"{arm}_any_found_pair_any"] = cluster(units, "any_found", "negative_error", "any") if units else None
            desc = []
            for k, p in enumerate(selected):
                d = dict(pair=k, phash_distance=p.get("phash_distance"))
                d.update((rows.get(f"t5desc:{k}") or {}).get("descriptors") or {})
                ra, rb = rows.get(f"t5:{k}:{m}:a:C0") or {}, rows.get(f"t5:{k}:{m}:b:C0") or {}
                for field, name in (("semantic_code", "semantic_code_distance"), ("perceptual_hash", "instance_hash_distance")):
                    ca, cb = (ra.get("detection") or {}).get(field), (rb.get("detection") or {}).get(field)
                    d[name] = bin(int(ca, 16) ^ int(cb, 16)).count("1") if ca and cb else None
                desc.append(d)
            t5["collision_descriptors"] = desc
        out["t5"] = t5
        methods[m] = out

    paired = {}
    for rule in ("semantic", "semantic_checked"):
        table = {}
        for s in W.STRENGTHS:
            doses = [f"ddim-{s}-{sd}" for sd in W.SEEDS]
            a_only = b_only = both = neither = 0
            for u in plan["t3_uids"]:
                maj = []
                for m in W.METHODS:
                    vals = [obs(f"t3:{u}:{m}:C1:{d}:correct", rule) for d in doses]
                    maj.append(sum(bool(v) for v in vals) * 2 >= len(vals))
                both += maj[0] and maj[1]
                neither += not maj[0] and not maj[1]
                a_only += maj[0] and not maj[1]
                b_only += maj[1] and not maj[0]
            table[f"ddim-{s}"] = dict(f5_only=a_only, v5_only=b_only, both=both, neither=neither,
                                      exact_sign_test_p_two_sided=sign_test(a_only, b_only))
        paired[rule] = table
    return dict(analysis_version=VERSION, inventory=inventory(planned, rows), methods=methods,
                paired_t3_source_majority=paired,
                caveat="Clean cells use 300 independent sources. T3/T4/T5 are descriptive with 30 independent units; "
                       "repeats are clustered. Per-cell bounds have no simultaneous coverage. No human visual or semantic verdict.")


def reanalyse(run_dir: Path) -> dict:
    run = json.loads((run_dir / "outputs" / "run.json").read_text(encoding="utf-8"))
    plan = json.loads(Path(run["plan_path"]).read_text(encoding="utf-8"))
    plan, sources = W.validate_plan(plan)
    rows = W.Journal(run_dir).rows
    sel = rows.get("t5:selection")
    selected = sel["selection"]["pairs"] if sel and sel.get("outcome") == "completed" else None
    return W.finite(analyse(plan, sources, rows, selected))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-dir", type=Path, required=True)
    a = ap.parse_args()
    result = reanalyse(a.run_dir)
    W.atomic_json(a.run_dir / "metrics" / "endpoints-reanalysis.json", result)
    print(json.dumps(result["inventory"], indent=1))


if __name__ == "__main__":
    main()
