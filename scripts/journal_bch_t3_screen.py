"""Conditional E1 two-source official T3 falsifier; no model loads or runner."""
from __future__ import annotations

import json
from pathlib import Path
import time
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
