"""Frozen E3-S1 endpoints from journal dictionaries only; never opens image/data files.

Intervals describe hypothetical exchangeable source/pair sampling. This fixed,
source-selected cohort supports neither population security nor cryptographic claims.
"""
from __future__ import annotations

from collections import Counter
import math
import numpy as np
from scipy.stats import beta, binom

VERSION = "e3-s1-analysis-v1"
METHODS = ("e3-s1", "v5-r3")
OWNERS = tuple("qim-pilot-owner-"+owner for owner in ("alpha", "beta", "gamma", "delta"))
STRENGTHS = ("0.1", "0.2")
SEEDS = (3, 4, 5)
MODES = ("combined", "semantic_only", "perceptual_only", "none")
CONDITIONS = ("residual-0.5", "residual-1.0", "public", "public-sham")
RULES = ("S", "C", "Q", "J", "H", "D", "F", "A")


def planned_ids(plan, sources, selected):
    """Literal protocol schedule; independent of runtime/worker imports."""
    ids = [f"src:{source['uid']}:canon" for source in sources]
    ids.append("t5:selection")
    for source in sources:
        u = source["uid"]
        ids.append(f"src:{u}:e3-s1:supplier")
        for m in METHODS:
            ids.append(f"src:{u}:{m}:embed")
            ids.extend(f"src:{u}:{m}:clean:{arm}:{o}" for arm in ("C0", "C1") for o in OWNERS)
        for s in STRENGTHS:
            for seed in SEEDS:
                dose = f"ddim-{s}-{seed}"
                ids.extend(f"atk:{u}:{arm}:{dose}" for arm in ("C0", "C1-e3-s1", "C1-v5-r3"))
                ids.extend(f"t3:{u}:{m}:{arm}:{dose}:{o}" for m in METHODS for arm in ("C0", "C1") for o in OWNERS)
    for k,p in enumerate(plan.get("t4_pairs", [])):
        for m in METHODS:
            for c in CONDITIONS:
                ids.append(f"t4img:{k}:{m}:{c}")
                ids.extend(f"t4:{k}:{m}:{c}:{mode}" for mode in MODES)
    for k, _ in enumerate(selected or []):
        ids.append(f"t5desc:{k}")
        for m in METHODS:
            for c in ("public", "public-sham"):
                ids.append(f"t5img:{k}:{m}:{c}")
                ids.extend(f"t5:{k}:{m}:{c}:{mode}" for mode in MODES)
    return ids


def intervals(k, n):
    if not n:
        return dict(two_sided_95=None, upper_one_sided_95=None, model="hypothetical exchangeable units")
    return dict(two_sided_95=[0.0 if k == 0 else float(beta.ppf(.025, k, n-k+1)),
                              1.0 if k == n else float(beta.ppf(.975, k+1, n-k))],
                upper_one_sided_95=1.0 if k == n else float(beta.ppf(.95, k+1, n-k)),
                model="hypothetical exchangeable units")


def _word(value):
    if isinstance(value, bool):
        return None
    try:
        return int(value, 16) if isinstance(value, str) else int(value) if isinstance(value, int) else None
    except ValueError:
        return None


def predicates(detection, payload=None):
    d, target = detection or {}, payload or {}
    s, h = d.get("semantic") or {}, d.get("instance") or {}
    qword, hword = _word(s.get("decoded_code")), _word(h.get("decoded_code"))
    qtarget, htarget = _word(target.get("q")), _word(target.get("h"))
    q = bool(s.get("read") and qword is not None and qtarget is not None and qword == qtarget)
    exact_h = bool(h.get("read") and hword is not None and htarget is not None and hword == htarget)
    result = dict(S=bool(s.get("found") and s.get("content_match")),
                  C=bool(s.get("read") and s.get("content_match")), Q=q,
                  J=bool(q and s.get("content_match")), H=exact_h, D=q and exact_h,
                  F=d.get("outcome") == "both_match", A=bool(s.get("found") or h.get("found")))
    result["recomputed_only_S"] = result["S"] and not bool(s.get("read"))
    result["q_bit_errors"] = (qword ^ qtarget).bit_count() if s.get("read") and qword is not None and qtarget is not None else None
    result["h_bit_errors"] = (hword ^ htarget).bit_count() if h.get("read") and hword is not None and htarget is not None else None
    return result


def _number(x):
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def strict_quality(q):
    q = q or {}
    return (q.get("psnr_infinite") is True or (_number(q.get("psnr_db")) or 0) > 35) and \
        (_number(q.get("ssim_rgb")) or 0) > .9 and _number(q.get("lpips")) is not None and q["lpips"] < .1


def availability(values, *, independent=False):
    n = len(values)
    positives = sum(v is True for v in values)
    missing = sum(v is None for v in values)
    out = dict(planned=n, observed=n-missing, positives=positives, unresolved=missing,
               planned_rate_bounds=[positives/n, (positives+missing)/n] if n else None)
    if independent:
        out["independent_units"] = n
        out["observed_event_interval"] = intervals(positives, n-missing)
        out["conservative_upper_one_sided_95"] = intervals(positives+missing, n)["upper_one_sided_95"]
    else:
        out["unit_note"] = "repeated calls; no independent-call confidence bound"
    return out


def clustered_negative(units):
    observations = []
    complete = 0
    unavailable = 0
    for calls in units:
        complete += all(v is not None for v in calls)
        unavailable += any(v is None for v in calls)
        observations.append(True if any(v is True for v in calls) else None if any(v is None for v in calls) else False)
    out = availability(observations, independent=True)
    out.update(completely_evaluated_sources=complete, sources_with_unavailable_calls=unavailable)
    return out


def paired(a, b, *, bootstrap=False):
    if len(a) != len(b):
        raise ValueError("paired source denominators differ")
    n = len(a)
    wins = sum(x and not y for x, y in zip(a, b))
    losses = sum(y and not x for x, y in zip(a, b))
    p = float(binom.sf(wins-1, wins+losses, .5)) if wins+losses else 1.0
    out = dict(n=n, e3_only=wins, v5_only=losses, both=sum(x and y for x, y in zip(a, b)),
               neither=sum(not x and not y for x, y in zip(a, b)),
               risk_difference=(wins-losses)/n if n else None, exact_mcnemar_one_sided_p=p,
               e3_success=sum(a), v5_success=sum(b), e3_interval=intervals(sum(a), n), v5_interval=intervals(sum(b), n))
    if bootstrap:
        estimates = []
        rng = np.random.Generator(np.random.PCG64(61010))
        delta = np.asarray(a, dtype=np.int8)-np.asarray(b, dtype=np.int8)
        if n:
            for _ in range(100):
                estimates.append(delta[rng.integers(0, n, size=(1000, n))].mean(axis=1))
            out["approximate_paired_source_bootstrap_95"] = np.quantile(np.concatenate(estimates), [.025, .975]).tolist()
        else:
            out["approximate_paired_source_bootstrap_95"] = None
        out["bootstrap"] = dict(resamples=100000, generator="PCG64", seed=61010, unit="complete source cluster", interval="approximate percentile")
    return out


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    result = [None]*len(ps)
    previous = 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, (len(ps)-rank)*ps[i]))
        result[i] = previous
    return result


def analyse(plan, sources, rows, selected):
    uids = [s["uid"] for s in sources]
    if len(set(uids)) != len(uids):
        raise ValueError("duplicate source UID")
    planned = planned_ids(plan, sources, selected)
    if len(set(planned)) != len(planned):
        raise ValueError("duplicate planned identifier")
    def observed(rid):
        row = rows.get(rid, {})
        return row if row.get("outcome") == "completed" and isinstance(row.get("detection"), dict) else None
    def obs(rid, rule, payload=None):
        row = observed(rid)
        return predicates(row["detection"], payload if payload is not None else row.get("payload"))[rule] if row else None
    def target(u, m):
        return rows.get(f"src:{u}:{m}:embed", {}).get("payload") or {}
    def cell(ids, rule):
        result = availability([obs(rid,rule) for rid in ids])
        states = Counter(rows.get(rid,{}).get("outcome","not_attempted") for rid in ids)
        result.update(states=dict(states),attempted=len(ids)-states["not_attempted"])
        return result
    methods, admission = {}, {}
    for m in METHODS:
        clean_units, t3_units, cells, coverage_rows = [], [], {}, []
        admitted = {}
        for u in uids:
            r = rows.get(f"src:{u}:{m}:embed", {})
            q = r.get("quality") or {}
            rid = f"src:{u}:{m}:clean:C1:{OWNERS[0]}"
            exact = {rule: obs(rid, rule, target(u, m)) is True for rule in ("Q", "H", "F")}
            native_admitted = bool(r.get("admitted", (r.get("admission") or {}).get("accepted", False)))
            admitted[u] = native_admitted and strict_quality(q) and all(exact.values())
            supplier = (r.get("report") or {}).get("supplier") or {}
            supplier_success = r.get("supplier_success", supplier.get("status")=="ok" if m=="e3-s1" else r.get("outcome")=="completed")
            coverage_rows.append(dict(uid=u, supplier_success=supplier_success, returned_final_pixels=r.get("returned_final_pixels",bool(r.get("image"))),
                                      admitted=native_admitted, strict_quality=bool(strict_quality(q)), **exact,
                                      primary_clean_admission=admitted[u], quality=q, outcome=r.get("outcome", "not_attempted")))
            clean_units.append([obs(f"src:{u}:{m}:clean:{arm}:{o}", "A") for arm in ("C0", "C1") for o in OWNERS if arm == "C0" or o != OWNERS[0]])
            t3_units.append([obs(f"t3:{u}:{m}:{arm}:ddim-{s}-{seed}:{o}", "A") for s in STRENGTHS for seed in SEEDS for arm in ("C0", "C1") for o in OWNERS if arm == "C0" or o != OWNERS[0]])
        for stage in ("clean", "t3"):
            for arm in ("C0", "C1"):
                for o in OWNERS:
                    if arm == "C1" and o == OWNERS[0]:
                        continue
                    for s in ((None,) if stage == "clean" else STRENGTHS):
                        ids = [f"src:{u}:{m}:clean:{arm}:{o}" for u in uids] if s is None else [f"t3:{u}:{m}:{arm}:ddim-{s}-{seed}:{o}" for u in uids for seed in SEEDS]
                        cells[f"{stage}:{arm}:{o}:{s}"] = cell(ids,"A")
        metrics = {}
        for metric in ("psnr_db", "ssim_rgb", "lpips"):
            values = [_number(r["quality"].get(metric)) for r in coverage_rows]
            present = [x for x in values if x is not None]
            infinite = sum(r["quality"].get("psnr_infinite") is True for r in coverage_rows) if metric=="psnr_db" else 0
            metrics[metric] = dict(observed=len(present), infinite=infinite, absent=sum(v is None and not(metric=="psnr_db" and r["quality"].get("psnr_infinite") is True) for v,r in zip(values,coverage_rows)), minimum=min(present) if present else None,
                                   maximum=max(present) if present else None, median=float(np.median(present)) if present else None)
        counts = {key: sum(r[key] is True for r in coverage_rows) for key in ("supplier_success", "returned_final_pixels", "admitted", "strict_quality", "Q", "H", "F", "primary_clean_admission")}
        for keys in (("Q","H"),("Q","H","F"),("admitted","strict_quality"),("strict_quality","Q","H","F")):
            counts["joint_"+"_".join(keys)] = sum(all(r[key] is True for key in keys) for r in coverage_rows)
        for key, pred in (("psnr_gt35", lambda q: q.get("psnr_infinite") is True or (_number(q.get("psnr_db")) or 0)>35),
                          ("ssim_gt0_9", lambda q: (_number(q.get("ssim_rgb")) or 0)>.9),
                          ("lpips_lt0_1", lambda q: _number(q.get("lpips")) is not None and q["lpips"]<.1)):
            counts[key] = sum(pred(r["quality"]) for r in coverage_rows)
        if m=="v5-r3":
            counts["supplier_success"]=None
        methods[m] = dict(clean_coverage=dict(N=len(uids), counts=counts, intervals={key: intervals(n, len(uids)) if n is not None else None for key,n in counts.items()},
                                             supplier_applicable=m=="e3-s1",
                                             metrics=metrics, per_source=coverage_rows, strict_quality_all_sources=bool(uids) and counts["strict_quality"]==len(uids)),
                          negatives=dict(cells=cells, clean_source_any=clustered_negative(clean_units), t3_source_any=clustered_negative(t3_units)))
        admission[m] = admitted
    primary, secondary = {}, {}
    for s in STRENGTHS:
        values = {m: {rule: [] for rule in RULES} for m in METHODS}
        for m in METHODS:
            per_seed = {}
            bit_errors = []
            for seed in SEEDS:
                per_seed[str(seed)] = {rule: availability([obs(f"t3:{u}:{m}:C1:ddim-{s}-{seed}:{OWNERS[0]}", rule, target(u,m)) for u in uids]) for rule in RULES}
            for u in uids:
                for rule in RULES:
                    calls = [obs(f"t3:{u}:{m}:C1:ddim-{s}-{seed}:{OWNERS[0]}", rule, target(u,m)) for seed in SEEDS]
                    values[m][rule].append(sum(v is True for v in calls)>=2)
                for seed in SEEDS:
                    rid = f"t3:{u}:{m}:C1:ddim-{s}-{seed}:{OWNERS[0]}"
                    row = observed(rid)
                    bit_errors.append(dict(uid=u, seed=seed, available=row is not None, **(predicates(row["detection"], target(u,m)) if row else {"q_bit_errors":None,"h_bit_errors":None})))
            methods[m].setdefault("t3", {})[s] = dict(per_seed=per_seed, raw_read_results=bit_errors)
        primary[s] = paired(
            [admission[METHODS[0]][u] and values[METHODS[0]]["S"][i] for i,u in enumerate(uids)],
            [admission[METHODS[1]][u] and values[METHODS[1]]["S"][i] for i,u in enumerate(uids)], bootstrap=True)
        secondary[s] = {rule: paired(values[METHODS[0]][rule], values[METHODS[1]][rule]) for rule in RULES}
    adjusted = holm([primary[s]["exact_mcnemar_one_sided_p"] for s in STRENGTHS])
    for s, p in zip(STRENGTHS, adjusted):
        primary[s]["holm_individual_p"] = p
    transfers = {}
    for stage, pairs, conditions in (("t4",plan.get("t4_pairs",[]),CONDITIONS), ("t5",selected or [],("public","public-sham"))):
        transfers[stage] = {}
        for c in conditions:
            by_method = {}
            for m in METHODS:
                records = []
                for i,p in enumerate(pairs):
                    k = i
                    base = f"{stage}:{k}:{m}:{c}"
                    combined, none = observed(base+":combined"), observed(base+":none")
                    donor = p.get("donor_uid",p.get("left"))
                    payload = (combined or none or {}).get("payload") or target(donor,m)
                    result = dict(pair_index=k, A=obs(base+":combined","A"), F=obs(base+":combined","F"),
                                  Q=obs(base+":none","Q",payload), H=obs(base+":none","H",payload), D=obs(base+":none","D",payload),
                                  native_modes={mode: {rule: obs(base+":"+mode,rule,payload) for rule in RULES} for mode in MODES},
                                  same_call_predicates=(combined or {}).get("same_call_predicates"),
                                  detection=(combined or {}).get("detection"), quality_vs_recipient=(combined or {}).get("quality_vs_recipient"),
                                  content_diagnostics=(combined or {}).get("content_diagnostics"))
                    if c=="public-sham":
                        for rule in ("Q","H","D"):
                            result[rule]=None
                            for native in result["native_modes"].values():
                                native[rule]=None
                        result["delivery_applicable"]=False
                    else:
                        result["delivery_applicable"]=True
                    records.append(result)
                delivered = [r for r in records if r["D"] is True]
                delivered_observed = [r for r in delivered if r["F"] is not None]
                same = [r["same_call_predicates"] if isinstance(r["same_call_predicates"],dict) else {} for r in records]
                by_method[m] = dict(planned_pairs=len(pairs), events={rule: availability([r[rule] for r in records],independent=True) for rule in ("A","F","Q","H","D")},
                    conditional_observed_D=None if c=="public-sham" else dict(n=len(delivered), observed_F=len(delivered_observed), F=sum(r["F"] is True for r in delivered), rejection=sum(r["F"] is False for r in delivered),
                        F_rate=sum(r["F"] is True for r in delivered_observed)/len(delivered_observed) if delivered_observed else None,
                        F_bounds=availability([r["F"] for r in delivered])["planned_rate_bounds"]),
                    delivery_applicable=c!="public-sham",
                    same_call_discordance={key:dict(discordant=sum(r[key]!=r["combined"] for r in same if isinstance(r.get(key),bool) and isinstance(r.get("combined"),bool)),
                        known=sum(isinstance(r.get(key),bool) and isinstance(r.get("combined"),bool) for r in same),
                        unknown=sum(not(isinstance(r.get(key),bool) and isinstance(r.get("combined"),bool)) for r in same)) for key in ("semantic_only","perceptual_only")},
                    same_call_acceptance={key:dict(accepted=sum(r.get(key) is True for r in same),known=sum(isinstance(r.get(key),bool) for r in same),unknown=sum(not isinstance(r.get(key),bool) for r in same)) for key in ("combined","semantic_only","perceptual_only")},
                    native_mode_acceptance={mode:availability([r["native_modes"][mode]["F"] for r in records]) for mode in MODES},
                    lpips_descriptive={str(limit):dict(observed=sum(_number((r["quality_vs_recipient"] or {}).get("lpips")) is not None for r in records),
                       subset_pairs=[r["pair_index"] for r in records if _number((r["quality_vs_recipient"] or {}).get("lpips")) is not None and r["quality_vs_recipient"]["lpips"]<=limit]) for limit in (.2,.3)},
                    per_pair=records)
                if c=="public-sham":
                    for rule in ("Q","H","D"):
                        by_method[m]["events"][rule]=None
            complete_pairs = [(a["F"],b["F"]) for a,b in zip(by_method[METHODS[0]]["per_pair"],by_method[METHODS[1]]["per_pair"]) if a["F"] is not None and b["F"] is not None]
            transfers[stage][c] = dict(methods=by_method, paired_observed_F=paired([a for a,b in complete_pairs],[b for a,b in complete_pairs]),
                                      paired_unavailable=len(pairs)-len(complete_pairs),
                                      note="descriptive jointly observed F pairs; planned outcomes bracketed separately; no pooling conditions")
    states = Counter(rows.get(rid,{}).get("outcome","not_attempted") for rid in planned)
    return dict(analysis_version=VERSION, inventory=dict(planned=len(planned),states=dict(states),extra_rows=sorted(set(rows)-set(planned)),
                attempted=len(planned)-states["not_attempted"], available=states["completed"], complete=states["not_attempted"]==0 and not(set(rows)-set(planned))),
        primary=primary, conjunction_superiority=all(primary[s]["risk_difference"] is not None and primary[s]["risk_difference"]>0 and primary[s]["exact_mcnemar_one_sided_p"]<.05 for s in STRENGTHS),
        secondary_source_majority=secondary, methods=methods, transfers=transfers,
        t5_selection=dict(selected_pairs=None if selected is None else len(selected),cap=(plan.get("t5") or {}).get("max_pairs",30),
            shortfall=None if selected is None else max(0,(plan.get("t5") or {}).get("max_pairs",30)-len(selected)),ledger=selected,
            source_descriptors=[dict(pair_index=k, outcome=rows.get(f"t5desc:{k}",{}).get("outcome","not_attempted"),
                descriptors=rows.get(f"t5desc:{k}",{}).get("descriptors"),
                phash_distance=rows.get(f"t5desc:{k}",{}).get("phash_distance")) for k in range(len(selected or []))]),
        interpretation="Fixed cohort, alpha-only image-domain method. No matched-FPR, combined-binding advantage, reference-instance, human-admissibility or cryptographic security claim.")
