"""Conditional E1 two-source official T3 falsifier; no model loads or runner."""
from __future__ import annotations

import time
_PROCESS_STARTED = time.monotonic()
import json
from pathlib import Path
import traceback

MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
D2_ROWS = MAIN / ".thesis-build/dev-runs/20261010-1330-d2-descriptive-t3/rows.jsonl"
IDS = (1675, 499768)
STRENGTHS = (.1, .2)
SEEDS = (0, 1, 2)
ALPHA = "qim-pilot-owner-alpha"
BETA = "qim-pilot-owner-beta"
PLAN = tuple((sid, strength, seed) for sid in IDS for strength in STRENGTHS for seed in SEEDS)


def _identity(row):
    return int(row["source_id"]), float(row["strength"]), int(row["seed"])


def _text(identity):
    return f"{identity[0]}|{identity[1]}|{identity[2]}"


def _coded_target(q):
    shifted = int(q, 16) << 27
    remainder = shifted
    while remainder.bit_length() >= 28:
        remainder ^= 0x086e8113 << (remainder.bit_length() - 28)
    return shifted ^ remainder


def _endpoint(call, payload, coded=False):
    """Targets enter only after a complete source-blind detector call."""
    semantic, instance = call["semantic"], call["instance"]
    decoded = semantic.get("decoded_code")
    exact = bool(semantic["read"] and decoded == payload["q"])
    result = dict(A=bool(semantic["found"] or instance["found"]),
        S=bool(semantic["found"] and semantic["content_match"]), Q=exact,
        J=bool(exact and semantic["content_match"]), R=bool(semantic["read"]),
        H=bool(instance["read"] and instance.get("decoded_code") == payload["h"]),
        F=call["outcome"] == "both_match",
        q_bit_errors=None if decoded is None else (int(decoded, 16) ^ int(payload["q"], 16)).bit_count())
    if coded:
        raw = semantic.get("raw_coded_word")
        if not isinstance(raw, str) or len(raw) != 15 or int(raw, 16) >= 1 << 59:
            raise ValueError("E1 detector must expose a 59-bit raw_coded_word as 15 hex digits")
        result.update(raw_coded_word=raw,
            raw_coded_bit_errors=(int(raw, 16) ^ _coded_target(payload["q"])).bit_count(),
            decoded_q=decoded)
    return result


def _summarize(rows, comparisons, error=None):
    candidate = {_identity(r): r for r in rows if r["arm"] == "candidate_C1"}
    strengths = {}
    for strength, minimum in ((.1, 6), (.2, 5)):
        keys = [key for key in PLAN if key[1] == strength]
        counts = {e: sum(bool(candidate.get(k, {}).get("endpoints", {}).get(e)) for k in keys)
                  for e in ("S", "Q", "J")}
        retention = {}
        for method in ("D2", "frozen_F5"):
            retention[method] = {}
            for endpoint in ("S", "Q", "J"):
                positive = [k for k in keys if comparisons[k][method][endpoint]]
                lost = [k for k in positive if not candidate.get(k, {}).get("endpoints", {}).get(endpoint)]
                gained = [k for k in keys if not comparisons[k][method][endpoint]
                          and candidate.get(k, {}).get("endpoints", {}).get(endpoint)]
                retention[method][endpoint] = dict(old_positive=len(positive),
                    lost=list(map(_text, lost)), gained=list(map(_text, gained)))
        strengths[str(strength)] = dict(planned=6, successes=counts, retention=retention,
            count_pass=counts["Q"] >= minimum and counts["J"] >= minimum,
            preservation_pass=not any(retention[m][e]["lost"] for m in retention for e in ("S", "Q", "J")))
    negative_calls = []
    for row in rows:
        owner = ALPHA if row["arm"] == "shared_C0" else BETA
        if owner in row.get("calls", {}):
            call = row["calls"][owner]
            negative_calls.append(dict(identity=_text(_identity(row)), arm=row["arm"], owner=owner,
                any_detection=bool(call["semantic"]["found"] or call["instance"]["found"])))
    expected = {(arm, key) for arm in ("shared_C0", "candidate_C1") for key in PLAN}
    actual = [(r["arm"], _identity(r)) for r in rows]
    complete = len(actual) == 24 and set(actual) == expected and all(r["status"] == "ok" for r in rows)
    calls = sum(len(r.get("calls", {})) for r in rows)
    result = dict(method="E1-BCH59-A", sources=list(IDS), strengths=strengths,
        planned_image_rows=24, planned_full_calls=36, observed_full_calls=calls,
        planned_negative_calls=24, observed_negative_calls=len(negative_calls),
        negative_any_detections=sum(r["any_detection"] for r in negative_calls), negative_calls=negative_calls,
        recorded_image_rows=len(rows), complete=complete,
        unavailable_rows=[dict(arm=r["arm"], identity=_text(_identity(r)), status=r["status"])
                          for r in rows if r["status"] != "ok"], error=error,
        comparisons=[dict(identity=_text(k), **comparisons[k]) for k in PLAN],
        comparison_record=str(D2_ROWS),
        scope="exploratory paired development screen; repeated-source calls; no population FPR or M1a verdict")
    result["pass"] = bool(not error and complete and calls == 36 and len(negative_calls) == 24
        and not result["negative_any_detections"]
        and all(s["count_pass"] and s["preservation_pass"] for s in strengths.values()))
    result["stage_a_t3_pass"] = result["pass"]
    return result


def run_stage_a_t3(ev, pipe, source_rows, output_dir: Path, budget: callable) -> dict:
    """Use an existing native fp16 SD1.5 pipe; budget() enforces caller's inclusive cap.

    Caller must invoke only after the two-source clean/VAE/negative prerequisite.
    Final marked paths and q/h targets come exclusively from source_rows.
    """
    budget()
    from PIL import Image
    import numpy as np
    from scripts.journal_bch_readout import detect_rgb
    # Official validation preserves checker verdicts and fixed RGB geometry.
    from scripts.three_threat_models import validate_generated

    source_rows = list(source_rows)
    if len(source_rows) != 2 or {int(r["source_id"]) for r in source_rows} != set(IDS):
        raise ValueError("Stage A T3 requires the two fixed source IDs, once each")
    sources = {int(r["source_id"]): r for r in source_rows}
    retained = [json.loads(line) for line in D2_ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
    panels = {}
    for arm in ("candidate_C1", "frozen_C1_enrichment", "shared_C0"):
        selected = [r for r in retained if r["arm"] == arm and _identity(r) in PLAN]
        if len(selected) != 12 or {_identity(r) for r in selected} != set(PLAN):
            raise ValueError(f"Incomplete or duplicate retained {arm} panel")
        panels[arm] = {_identity(r): r for r in selected}
    comparisons = {}
    for key in PLAN:
        payload = sources[key[0]]["payload"]
        entries = {}
        for method, arm, field in (("D2", "candidate_C1", "calls"),
                                   ("frozen_F5", "frozen_C1_enrichment", "native_calls")):
            row = panels[arm][key]
            if row["payload"]["q"] != payload["q"] or row["payload"]["h"] != payload["h"]:
                raise ValueError("Original target differs from frozen comparator target")
            if row["status"] != "ok":
                raise ValueError("Fixed comparator full call unavailable")
            entries[method] = _endpoint(row[field][ALPHA], payload)
            entries[method + "_image"] = row["image"]
        comparisons[key] = entries
    budget()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True)
    rows_path = output_dir / "e1-t3-rows.jsonl"
    if rows_path.exists():
        raise ValueError("E1 T3 rows already exist; no replay or append")
    rows, fatal = [], None

    def load(path):
        with Image.open(path) as image:
            if image.mode != "RGB" or image.size != (512, 512):
                raise ValueError("Suspect must be saved RGB8 512x512")
            return np.asarray(image, dtype=np.uint8).copy()

    def emit(row):
        rows.append(row)
        with rows_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, allow_nan=False) + "\n")

    plan = [(arm, key) for arm in ("shared_C0", "candidate_C1") for key in PLAN]
    try:
        for arm, key in plan:
            budget()
            sid, strength, seed = key
            tick = time.monotonic()
            row = dict(arm=arm, source_id=sid, strength=strength, seed=seed, calls={},
                attack=dict(model="pinned SD1.5 fp16", scheduler="DDIM", num_inference_steps=20,
                    prompt="", negative_prompt="", guidance_scale=1., eta=0., safety_checker=True))
            try:
                if arm == "shared_C0":
                    old = panels[arm][key]
                    row.update(retained_source_record=str(D2_ROWS), retained_status=old["status"],
                        retained_source_path=old.get("image"), reuse="exact cached C0 pixels; fresh E1 alpha call")
                    if old["status"] != "ok":
                        row.update(status="safety_blocked" if old["status"] == "safety_blocked" else "failed",
                            error=old.get("error", "Retained C0 unavailable; no resampling"))
                    else:
                        row["image"] = old["image"]
                        rgb = load(row["image"])
                else:
                    mark = sources[sid]["conditions"]["clean"]["image"]
                    row["marked_input"] = str(mark)
                    # Same whitelist adaptation as journal_rc_t3_probe: .1/.2 only;
                    # all official kwargs and safety checks stay fixed.
                    if pipe.safety_checker is None or pipe.feature_extractor is None:
                        raise RuntimeError("Required official safety components missing")
                    budget()
                    with ev.torch.inference_mode():
                        result = pipe(prompt="", negative_prompt="", image=Image.fromarray(load(mark)),
                            strength=strength, num_inference_steps=20, eta=0., guidance_scale=1.,
                            generator=ev.torch.Generator(device="cuda").manual_seed(seed),
                            num_images_per_prompt=1, output_type="pil", return_dict=True)
                    budget()
                    rgb = np.asarray(validate_generated(result), dtype=np.uint8)
                    path = image_dir / f"E1-{sid}-{strength}-{seed}.png"
                    Image.fromarray(rgb).save(path)
                    row["image"] = str(path)
                    rgb = load(path)
                if "status" not in row:
                    budget()
                    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
                    budget()
                    for owner in ((ALPHA,) if arm == "shared_C0" else (ALPHA, BETA)):
                        budget()
                        call = detect_rgb(rgb, latent, owner, ev.profile, features, binding="soft")
                        row["calls"][owner] = call
                        budget()
                    if arm == "candidate_C1":
                        row["payload"] = sources[sid]["payload"]
                        row["endpoints"] = _endpoint(row["calls"][ALPHA], row["payload"], coded=True)
                    row["status"] = "ok"
            except Exception as error:
                row.update(status="safety_blocked" if "safety_checker_blocked_output" in str(error) else "failed",
                    error=traceback.format_exc())
                if hasattr(ev, "torch"):
                    ev.torch.cuda.empty_cache()
            row["duration_seconds"] = time.monotonic() - tick
            emit(row)
            budget()
    except Exception:
        fatal = traceback.format_exc()
        for arm, key in plan[len(rows):]:
            emit(dict(arm=arm, source_id=key[0], strength=key[1], seed=key[2], status="failed",
                calls={}, duration_seconds=0., error="Caller budget/setup stop; see summary error"))
    summary = _summarize(rows, comparisons, fatal)
    (output_dir / "e1-t3-summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    try:
        budget()
    except Exception:
        summary.update(error=traceback.format_exc(), stage_a_t3_pass=False, **{"pass": False})
        (output_dir / "e1-t3-summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return summary


def _stage_c_summary(rows, comparisons, plan, sets, v5, error=None,
                     method='E1-BCH59-A', stage='C', pass_key='stage_c_pass'):
    """Separate full-grid summary: Stage A's dictionary remains unchanged."""
    candidate = {_identity(r): r for r in rows if r['arm'] == 'candidate_C1'}
    strengths = {}
    for strength, minimum in ((.1, 36), (.2, 31)):
        keys = [k for k in plan if k[1] == strength]
        counts = {e: sum(bool(candidate.get(k, {}).get('endpoints', {}).get(e)) for k in keys)
                  for e in ('S', 'Q', 'J')}
        retention = {}
        methods = ('D2', 'frozen_F5') + (('E1_A',) if any('E1_A' in comparisons[k] for k in keys) else ())
        for baseline in methods:
            retention[baseline] = {}
            for endpoint in ('S', 'Q', 'J'):
                baseline_keys = [k for k in keys if baseline in comparisons[k]]
                positive = [k for k in baseline_keys if comparisons[k][baseline].get(endpoint)]
                lost = [k for k in positive if not candidate.get(k, {}).get('endpoints', {}).get(endpoint)]
                gained = [k for k in baseline_keys if not comparisons[k][baseline].get(endpoint)
                          and candidate.get(k, {}).get('endpoints', {}).get(endpoint)]
                retention[baseline][endpoint] = dict(old_positive=len(positive),
                    lost=list(map(_text, lost)), gained=list(map(_text, gained)))
        fixed = list(map(tuple, sets[str(strength)]['I']))
        intersection = dict(fixed_identities=len(fixed), identities=list(map(_text, fixed)),
            candidate_S=sum(bool(candidate.get(k, {}).get('endpoints', {}).get('S')) for k in fixed),
            v5_S=sum(v5[k] for k in fixed), frozen_F5_S=len(fixed))
        strengths[str(strength)] = dict(planned=36, successes=counts, retention=retention,
            count_pass=counts['Q'] >= minimum and counts['J'] >= minimum,
            preservation_pass=not any(retention[m][e]['lost'] for m in retention for e in ('S', 'Q', 'J')),
            intersection=intersection,
            fixed_I_pass=intersection['candidate_S'] == len(fixed) and intersection['candidate_S'] > intersection['v5_S'])
    expected = {(arm, k) for arm in ('candidate_C1', 'shared_C0') for k in plan}
    actual = [(r['arm'], _identity(r)) for r in rows]
    complete = len(actual) == 144 and set(actual) == expected
    operational = []
    negatives = []
    unavailable = []
    histogram = {}
    for row in rows:
        owners = (ALPHA, BETA) if row['arm'] == 'candidate_C1' else (ALPHA,)
        if row['status'] == 'ok':
            if set(row.get('calls', {})) != set(owners):
                operational.append(dict(arm=row['arm'], identity=_text(_identity(row)), reason='missing full calls'))
            owner = BETA if row['arm'] == 'candidate_C1' else ALPHA
            if owner in row.get('calls', {}):
                call = row['calls'][owner]
                negatives.append(dict(arm=row['arm'], identity=_text(_identity(row)), owner=owner,
                    any_detection=bool(call['semantic']['found'] or call['instance']['found'])))
            if row['arm'] == 'candidate_C1':
                errors = row['endpoints']['raw_coded_bit_errors']
                label = str(errors)
                histogram[label] = histogram.get(label, 0) + 1
        else:
            unavailable.append(dict(arm=row['arm'], identity=_text(_identity(row)), status=row['status'],
                error=row.get('error'), unavailable_negative_owner=BETA if row['arm']=='candidate_C1' else ALPHA))
            if row['status'] != 'safety_blocked' or row.get('calls'):
                operational.append(dict(arm=row['arm'], identity=_text(_identity(row)), reason=row['status']))
    result = dict(method=method, stage=stage, sources=sorted({k[0] for k in plan}), strengths=strengths,
        planned_image_rows=144, recorded_image_rows=len(rows), planned_full_calls=216,
        observed_full_calls=sum(len(r.get('calls', {})) for r in rows),
        planned_negative_calls=144, observed_negative_calls=len(negatives), negative_calls=negatives,
        negative_any_detections=sum(n['any_detection'] for n in negatives), unavailable_rows=unavailable,
        raw_59_bit_error_histogram=histogram, raw_59_bit_errors_observed=sum(histogram.values()),
        complete=complete, operational_failures=operational, error=error,
        comparisons=[dict(identity=_text(k), **comparisons[k]) for k in plan],
        comparison_record=str(D2_ROWS), m1a_pass=False, candidate_eligible=False,
        scope='Exploratory in-sample image-domain selection; blocked planned slots count as failures; '
              'repeated-source negatives, no population FPR, latent-method, T4/T5 or M1a inference')
    result[pass_key] = bool(not error and complete and not operational and not result['negative_any_detections']
        and all(s['count_pass'] and s['preservation_pass'] and s['fixed_I_pass'] for s in strengths.values()))
    return result


def main():
    # Clock starts before any scientific imports/model startup in this CLI.
    import argparse
    import subprocess
    import sys
    started = _PROCESS_STARTED
    parser = argparse.ArgumentParser(description='E1 Stage C or E3 Stage B full official matched development T3')
    prerequisite = parser.add_mutually_exclusive_group(required=True)
    prerequisite.add_argument('--stage-b-dir', type=Path)
    prerequisite.add_argument('--e3-stage-a-dir', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    e3 = args.e3_stage_a_dir is not None
    method, stage, pass_key = ('E3-BCH59-Q080', 'B', 'stage_b_pass') if e3 else ('E1-BCH59-A', 'C', 'stage_c_pass')
    label = f'{method} Stage {stage}'
    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root), str(root/'scripts')]
    cap, gpu_cap = 900., 10*1024**3
    torch = None

    def budget():
        if time.monotonic()-started >= cap:
            raise TimeoutError(f'{label} 900-second inclusive hard cap exhausted')
        if torch is not None and torch.cuda.is_initialized() and torch.cuda.max_memory_allocated() > gpu_cap:
            raise torch.cuda.OutOfMemoryError(f'{label} 10-GiB allocated GPU cap exceeded')

    def read_rows(path):
        return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

    def write(path, value):
        path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')

    budget()
    from journal_bch_probe import ALL_IDS, summarize_b, stage_config, D2_WRITER, validate_stage_a
    from journal_rc_t3_probe import frozen_sets
    if e3:
        from journal_bch_quality_select import validate_stage_a as validate_e3_stage_a
        selected_dir = args.e3_stage_a_dir.resolve()
        sources_list, selected_run = validate_e3_stage_a(selected_dir)
        bdir = Path(selected_run['e1_stage_b_dir']).resolve()
    else:
        bdir = args.stage_b_dir.resolve()
    brun = json.loads((bdir/'run.json').read_text(encoding='utf-8'))
    bsummary = json.loads((bdir/'summary.json').read_text(encoding='utf-8'))
    if not e3:
        sources_list = read_rows(bdir/'rows.jsonl')
        bcheck = summarize_b(sources_list, read_rows(D2_WRITER/'rows.jsonl'))
    if not e3 and (brun.get('schema') != 'journal-e1-bch-stage-b-v1' or brun.get('outcome') != 'completed'
        or brun.get('qualification') != 'stage_b_pass' or bsummary != brun.get('summary')
        or bsummary.get('stage_b_pass') is not True or not bcheck['stage_b_evidence_pass']
        or brun.get('config') != stage_config(3300., True) or brun.get('data_split') != 'development'
        or brun.get('usd') != 0 or brun.get('seeds') != [0, 1, 2]
        or brun.get('budget_overrun') is not False or not 0 < brun.get('duration_seconds', float('inf')) <= 3300.
        or not 0 < brun.get('peak_allocated_bytes', float('inf')) <= gpu_cap):
        raise ValueError('Stage C requires complete passing fixed Stage B evidence')
    if e3 and (brun.get('schema') != 'journal-e1-bch-stage-b-v1' or brun.get('outcome') != 'completed'
        or brun.get('config') != stage_config(3300., True) or brun.get('data_split') != 'development'
        or brun.get('usd') != 0 or brun.get('seeds') != [0, 1, 2]
        or brun.get('budget_overrun') is not False
        or not 0 < brun.get('duration_seconds', float('inf')) <= 3300.
        or not 0 < brun.get('peak_allocated_bytes', float('inf')) <= gpu_cap):
        raise ValueError('E3 requires completed fixed E1 B ancestry, without its quality gate')
    adir = Path(brun['stage_a_provenance']['folder'])
    a_sources, arun = validate_stage_a(adir)
    sources = {int(r['source_id']): r for r in sources_list}
    for a in a_sources if not e3 else ():
        b = sources[a['source_id']]
        if b['payload'] != a['payload'] or b['conditions'] != a['conditions']:
            raise ValueError('Stage B inherited Stage A mark or full calls differ')
    plan = tuple((sid, s, seed) for sid in ALL_IDS for s in STRENGTHS for seed in SEEDS)
    retained = read_rows(D2_ROWS)
    panels = {arm: {_identity(r): r for r in retained if r['arm']==arm}
              for arm in ('candidate_C1', 'frozen_C1_enrichment', 'shared_C0')}
    old, v5, sets = frozen_sets()
    if e3:
        for strength, fixed_count, v5_count in ((.1, 29, 27), (.2, 28, 18)):
            fixed = list(map(tuple, sets[str(strength)]['I']))
            if (len(fixed) != fixed_count or len(set(fixed)) != fixed_count
                or not set(fixed) <= set(plan) or sum(v5[k] for k in fixed) != v5_count):
                raise ValueError('E3 requires the frozen 29/28 intersection and v5 27/18 counts')
    for arm in panels:
        selected = [r for r in retained if r['arm']==arm]
        expected_keys = (set(plan) if arm != 'frozen_C1_enrichment' else
            {k for k in plan if old['C1'][k]['outcome']=='completed'})
        if len(selected) != len(expected_keys) or set(panels[arm]) != expected_keys:
            raise ValueError('Duplicate or incomplete retained Stage C comparator panel')
    comparisons = {}
    for k in plan:
        comparisons[k] = {}
        for method, arm, field in (('D2', 'candidate_C1', 'calls'),
                                   ('frozen_F5', 'frozen_C1_enrichment', 'native_calls')):
            r = panels[arm].get(k)
            if r is None:
                if method != 'frozen_F5' or old['C1'][k]['outcome'] != 'safety_blocked':
                    raise ValueError('Missing frozen full comparison call')
                comparisons[k][method] = dict(S=False, Q=False, J=False, unavailable='safety_blocked')
            elif r['status'] == 'ok':
                payload = sources[k[0]]['payload']
                if r['payload']['q'] != payload['q'] or r['payload']['h'] != payload['h']:
                    raise ValueError('Stage C original comparison payload differs')
                comparisons[k][method] = _endpoint(r[field][ALPHA], payload)
                comparisons[k][method+'_image'] = r['image']
            elif r['status'] == 'safety_blocked':
                comparisons[k][method] = dict(S=False, Q=False, J=False, unavailable='safety_blocked')
            else:
                raise ValueError('Operationally missing comparator is not an available baseline')
        if k not in panels['shared_C0'] or panels['shared_C0'][k]['status'] not in ('ok', 'safety_blocked'):
            raise ValueError('Full same-D2 C0 panel must preserve all blocks')
    if e3 and sum(r['status'] == 'safety_blocked' for r in panels['shared_C0'].values()) != 6:
        raise ValueError('E3 must retain the six fixed C0 safety-checker blocks')
    inherited = read_rows(adir/'e1-t3-rows.jsonl')
    if e3:
        a_panel = [r for r in inherited if r['arm'] == 'candidate_C1']
        if len(a_panel) != len(PLAN) or {_identity(r) for r in a_panel} != set(PLAN):
            raise ValueError('E3 E1 A retention requires all twelve original C1 identities')
        for r in a_panel:
            k = _identity(r)
            payload = sources[k[0]]['payload']
            if r['status'] != 'ok' or r['payload'] != payload or set(r.get('calls', {})) != {ALPHA, BETA}:
                raise ValueError('E3 E1 A retention full calls or original targets differ')
            comparisons[k]['E1_A'] = _endpoint(r['calls'][ALPHA], payload, coded=True)
            comparisons[k]['E1_A_image'] = r['image']
    inherited_keys = set() if e3 else {(r['arm'], _identity(r)) for r in inherited}
    budget()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out/'images').mkdir()
    rows, fatal = [], None
    record = dict(schema='journal-e3-bch-quality-select-stage-b-v1' if e3 else 'journal-e1-bch-stage-c-v1', method=method, stage=stage,
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        command=sys.argv, seeds=list(SEEDS), strengths=list(STRENGTHS), sources=list(ALL_IDS),
        data_split='development', usd=0, stage_b_dir=str(bdir), stage_b_commit=brun['commit'],
        stage_a_dir=str(adir), stage_a_commit=arun['commit'], comparison_record=str(D2_ROWS),
        comparison_sets=sets, config=dict(cap_seconds=cap, gpu_allocated_cap_bytes=gpu_cap,
            num_inference_steps=20, guidance_scale=1., eta=0., prompt='', negative_prompt='',
            scheduler='DDIM', safety_checker=True, semantic_views=7, binding='soft', roster_size=1),
        inherited_image_rows=0 if e3 else 24, new_c1_generations_planned=72 if e3 else 60,
        new_c0_calls_planned=72 if e3 else 60,
        budget_scope='900 seconds inclusive of imports/startup, validation, new generation/calls and final summaries; cached prerequisite cost excluded',
        outcome='running', qualification='pending', human_admissibility_verdict=None)
    if e3:
        record.update(e3_stage_a_dir=str(selected_dir), e3_stage_a_commit=selected_run['commit'],
            e1_stage_b_dir=str(bdir), e2_stage_a_dir=selected_run['e2_stage_a_dir'],
            selected_mark_record=str(selected_dir/'rows.jsonl'), inherited_full_calls=0,
            detector='E1-BCH59-A', quality_rule='retain_if_strict_else_contract_once', factor=.8,
            e1_a_retention_record=str(adir/'e1-t3-rows.jsonl'))
        record['config'].update(detector='E1-BCH59-A', quality_rule='retain_if_strict_else_contract_once', factor=.8)

    def emit(row):
        rows.append(row)
        with (out/'rows.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, allow_nan=False)+'\n')
            handle.flush()
        print(json.dumps({k:row[k] for k in ('arm', 'source_id', 'strength', 'seed', 'status')}), flush=True)

    write(out/'run.json', record)
    for index, row in enumerate(inherited if not e3 else ()):
        emit(dict(row, inherited_provenance=dict(stage='A', commit=arun['commit'],
            run_json=str(adir/'run.json'), rows_jsonl=str(adir/'e1-t3-rows.jsonl'), row_index=index,
            reuse='Exact Stage A C1 pixels/full alpha+beta calls and C0 pixels/fresh E1 alpha call; not a replicate')))
    fresh_plan = [(arm, k) for arm in ('shared_C0', 'candidate_C1') for k in plan
                  if (arm, k) not in inherited_keys]
    try:
        import torch as torch_module
        torch = torch_module
        budget()
        torch.cuda.set_per_process_memory_fraction(gpu_cap/torch.cuda.get_device_properties(0).total_memory)
        torch.cuda.reset_peak_memory_stats()
        from PIL import Image
        import numpy as np
        import diffusers
        from journal_vae_probe import Evaluator
        from f4_transfer_probe import ASSETS, SOURCES
        from scripts.journal_bch_readout import detect_rgb
        if diffusers.__version__ != '0.35.1':
            raise ValueError('Pinned diffusers 0.35.1 required')
        ev = Evaluator()
        budget()
        pipe = ev.models.load_regenerator(ASSETS)
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise RuntimeError('Mandatory official safety checker/components missing')
        budget()
        record['startup_seconds'] = time.monotonic()-started
        record['environment'] = dict(torch=torch.__version__, diffusers=diffusers.__version__,
            gpu=torch.cuda.get_device_name(0))

        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512, 512):
                    raise ValueError('Saved RGB8 512x512 suspect required')
                return np.asarray(image, dtype=np.uint8).copy()

        for arm, key in fresh_plan:
            budget()
            sid, strength, seed = key
            tick = time.monotonic()
            row = dict(arm=arm, source_id=sid, strength=strength, seed=seed, calls={})
            try:
                if arm == 'shared_C0':
                    prior = panels[arm][key]
                    row.update(retained_source_record=str(D2_ROWS), retained_status=prior['status'],
                        retained_source_path=prior.get('image'), reuse='Exact same D2 C0 pixels; fresh E1 alpha call')
                    if prior['status'] == 'safety_blocked':
                        row.update(status='safety_blocked', error=prior.get('error', 'Retained checker block; no replacement'))
                    else:
                        row['image'] = prior['image']
                        rgb = load(row['image'])
                else:
                    mark = sources[sid]['conditions']['clean']['image']
                    row.update(marked_input=mark,
                        target_source_record=str((selected_dir if e3 else bdir)/'rows.jsonl'), attack=record['config'])
                    budget()
                    with torch.inference_mode():
                        result = pipe(prompt='', negative_prompt='', image=Image.fromarray(load(mark)),
                            strength=strength, num_inference_steps=20, eta=0., guidance_scale=1.,
                            generator=torch.Generator(device='cuda').manual_seed(seed),
                            num_images_per_prompt=1, output_type='pil', return_dict=True)
                    budget()
                    rgb = np.asarray(ev.models.validate_generated(result), dtype=np.uint8)
                    path = out/'images'/f'{"E3" if e3 else "E1"}-{sid}-{strength}-{seed}.png'
                    Image.fromarray(rgb).save(path)
                    row['image'] = str(path)
                    rgb = load(path)
                    row.update(quality_input=ev.metrics(load(mark), rgb), quality_source=ev.metrics(load(SOURCES[sid]), rgb),
                        quality_interpretation='Descriptive attack distortion; no filtering or extra quality gate',
                        human_admissibility_verdict=None)
                if 'status' not in row:
                    budget()
                    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
                    for owner in ((ALPHA,) if arm=='shared_C0' else (ALPHA, BETA)):
                        budget()
                        row['calls'][owner] = detect_rgb(rgb, latent, owner, ev.profile, features,
                            binding='soft', roster_size=1)
                    budget()
                    if arm == 'candidate_C1':
                        row['payload'] = sources[sid]['payload']
                        row['endpoints'] = _endpoint(row['calls'][ALPHA], row['payload'], coded=True)
                    row['status'] = 'ok'
            except (TimeoutError, torch.cuda.OutOfMemoryError):
                row.update(status='failed', error=traceback.format_exc())
                row['duration_seconds'] = time.monotonic()-tick
                emit(row)
                raise
            except Exception as exc:
                row.update(status='safety_blocked' if 'safety_checker_blocked_output' in str(exc) else 'failed',
                    error=traceback.format_exc())
                torch.cuda.empty_cache()
            row['duration_seconds'] = time.monotonic()-tick
            emit(row)
            budget()
        record['outcome'] = 'completed'
    except Exception:
        fatal = traceback.format_exc()
        record.update(outcome='failed', error=fatal)
    finally:
        seen = {(r['arm'], _identity(r)) for r in rows}
        for arm, key in fresh_plan:
            if (arm, key) not in seen:
                emit(dict(arm=arm, source_id=key[0], strength=key[1], seed=key[2], status='failed',
                    calls={}, duration_seconds=0., error='Unrun after startup/runtime hard stop; see run.json'))
        peak = torch.cuda.max_memory_allocated() if torch is not None and torch.cuda.is_initialized() else None
        summary = _stage_c_summary(rows, comparisons, plan, sets, v5, fatal,
            method=method, stage=stage, pass_key=pass_key)
        record.update(peak_allocated_bytes=peak, summary=summary, duration_seconds=time.monotonic()-started)
        write(out/'summary.json', summary)
        write(out/'run.json', record)
        record.update(duration_seconds=time.monotonic()-started,
            budget_overrun=time.monotonic()-started >= cap, gpu_budget_overrun=peak is None or peak > gpu_cap)
        summary[pass_key] = bool(summary[pass_key] and record['outcome']=='completed'
            and not record['budget_overrun'] and not record['gpu_budget_overrun'])
        record['qualification'] = pass_key if summary[pass_key] else 'ineligible'
        write(out/'summary.json', summary)
        write(out/'run.json', record)
        if time.monotonic()-started >= cap and not record['budget_overrun']:
            record.update(duration_seconds=time.monotonic()-started, budget_overrun=True, qualification='ineligible')
            summary[pass_key] = False
            write(out/'summary.json', summary)
            write(out/'run.json', record)
    return 0 if record['outcome']=='completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
