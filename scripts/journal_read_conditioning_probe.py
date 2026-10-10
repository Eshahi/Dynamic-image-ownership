"""Paired cached-pixel F5-RC1 screen/binding probe; development only, USD 0."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from journal_vae_probe import Evaluator, F5_RUN, SOURCES, write
from journal_readability_probe import CONDITIONS, IDS, DISCOVERY, load, patterns, projection_stats, decompose
from journal_binding_probe import MODES, pairs, ARMS, delivery, extracted_controls
from f4_transfer_probe import MAIN
from f5_gate import OWNERS
from scripts import journal_read_conditioning as rc

SCREEN = MAIN / ".thesis-build/dev-runs/20261010-0951-readability-screen"
BINDING = MAIN / ".thesis-build/dev-runs/20261010-0858-journal-binding"
CONFIGS = {"RC2": "R2", "RC3": "R3"}
CAP = 1800.


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def original_complete(screen):
    record = json.loads((screen / "run.json").read_text(encoding="utf-8"))
    rows = read_rows(screen / "rows.jsonl")
    if record["outcome"] != "completed":
        raise ValueError("Original screen must complete without missing/failed sources before activation")
    from journal_readability_probe import summary
    if len(rows) != 48 or len({(r["config"], r["source_id"]) for r in rows}) != 48:
        raise ValueError("Original screen requires exactly the 48 unique fixed rows")
    counts = summary(rows)
    if counts["ranked_survivors"] or any(counts[c]["completed"] != 12 for c in ("R1", "R2", "R3", "R4")):
        raise ValueError("Read-conditioning activation requires no original survivor and all four complete")
    return rows


def calls(ev, rgb, owner, modes=("combined",), native=False):
    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
    new = {mode: rc.detect_rgb(rgb, latent, owner, ev.profile, features,
        binding_mode=mode, binding="soft", roster_size=1) for mode in modes}
    old = {mode: ev.detect(rgb, "f5", owner, features, latent, mode) for mode in modes} if native else None
    return new, old, latent


def screen_row(ev, old, config, screen, row):
    sid, payload = old["source_id"], old["payload"]
    q, h = int(payload["q"], 16), int(payload["h"], 16)
    row.update(config=config, writer_config=CONFIGS[config], source_id=sid,
        payload=payload, source_record=str(screen / "rows.jsonl"), conditions={})
    projection_pairs = {}
    for condition in CONDITIONS:
        source_entry = old["conditions"][condition]
        rgb = load(source_entry["image"])
        # Share only suspect features/latent, never targets or source features, across owner calls.
        features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
        new = {o: rc.detect_rgb(rgb, latent, o, ev.profile, features,
            binding="soft", roster_size=1) for o in OWNERS[:2]}
        native = {o: ev.detect(rgb, "f5", o, features, latent) for o in OWNERS[:2]}
        c0_path = DISCOVERY / "images" / f"{sid}-f5-C0-{condition}.png"
        c0 = load(c0_path)
        c0_calls, native_c0, c0_latent = calls(ev, c0, OWNERS[0], native=True)
        intended = new[OWNERS[0]]
        layout, w, gaps = patterns(ev.profile, q)
        p, b = (np.asarray(layout.projections(z), np.float64) for z in (latent, c0_latent))
        projection_pairs[condition] = (b, p)
        row["conditions"][condition] = dict(image=source_entry["image"], c0_image=str(c0_path),
            calls=new, c0_call=c0_calls["combined"], native_calls=native,
            native_c0_call=native_c0["combined"], original_calls=source_entry["calls"],
            original_c0_call=source_entry["c0_call"], native_output_scope="fresh full native paired outputs; original compact retained",
            delivery=delivery(intended, q, h),
            joint_fixed_q=bool(intended["semantic"]["read"] and
                int(intended["semantic"]["decoded_code"], 16) == q and intended["semantic"]["content_match"]),
            quality_source=source_entry["quality_source"], quality_input=source_entry["quality_input"],
            quality_origin="reused exact cached pixel quality; linked source record", diagnostics=projection_stats(p, w, gaps))
    b0, p0 = projection_pairs["clean"]
    delta = p0-b0
    alpha = float(w @ delta / 320)
    for condition, (b, p) in projection_pairs.items():
        row["conditions"][condition]["decomposition"] = decompose(b, p, delta, w, gaps, alpha)
    row["status"] = "ok"
    return row


def screen_summary(rows):
    result = {}
    for config in CONFIGS:
        good = [r for r in rows if r.get("config") == config and r["status"] == "ok"]
        clean = [r["conditions"]["clean"] for r in good]
        quality = sum(c["quality_source"]["psnr_db"] > 35 and c["quality_source"]["ssim_rgb"] > .9 and
            c["quality_source"]["lpips"] < .1 for c in clean)
        strict = sum(c["quality_source"]["psnr_db"] > 35 and c["quality_source"]["ssim_rgb"] > .9 and
            c["quality_source"]["lpips"] < .1 and c["delivery"]["both_exact"] and
            c["calls"][OWNERS[0]]["outcome"] == "both_match" for c in clean)
        counts = {b: sum(r["conditions"][b]["joint_fixed_q"] for r in good) for b in CONDITIONS}
        c0 = sum(r["conditions"][b]["c0_call"]["watermark_found"] for r in good for b in CONDITIONS)
        wrong = sum(r["conditions"][b]["calls"][OWNERS[1]]["watermark_found"] for r in good for b in CONDITIONS)
        result[config] = dict(planned_sources=12, completed=len(good), missing_or_failed=12-len(good),
            strict_clean=strict, strict_clean_quality=quality, joint_fixed_q=counts, c0_any=c0, wrong_owner_any=wrong,
            planned_negative_calls=72, completed_negative_calls=6*len(good),
            survivor=len(good)==12 and strict==12 and counts["sd15_vae"]==12 and counts["sdxl_vae"]>=11 and c0+wrong==0,
            minimum_reconstruction_score=min((r["conditions"][b]["diagnostics"]["fixed_q_score"] for r in good for b in CONDITIONS[1:]), default=None),
            mean_clean_lpips=sum(c["quality_source"]["lpips"] for c in clean)/len(clean) if clean else None)
    complete = all(result[c]["completed"]==12 for c in CONFIGS)
    result["ranked_survivors"] = sorted([c for c in CONFIGS if result[c]["survivor"]], key=lambda c:
        (-result[c]["joint_fixed_q"]["sdxl_vae"], -result[c]["minimum_reconstruction_score"],
         result[c]["mean_clean_lpips"], list(CONFIGS).index(c))) if complete else []
    result["selection_allowed"] = complete
    compatibility = [r for r in rows if r.get("arm")=="frozen_clean_compatibility" and r["status"]=="ok"]
    result["frozen_clean_compatibility"] = dict(planned=12, completed=len(compatibility),
        both_match=sum(r["calls"]["combined"]["outcome"]=="both_match" for r in compatibility),
        exact_both=sum(r["delivery"]["both_exact"] for r in compatibility))
    result["negative_interpretation"] = "observed development counts, not calibrated FPR"
    return result


def binding_row(ev, old):
    payload = old["intended_payload"]
    q, h = (None if payload[k] is None else int(payload[k], 16) for k in ("q", "h"))
    new, native, _ = calls(ev, load(old["image"]), OWNERS[0], MODES, native=True)
    combined = new["combined"]
    return dict(donor_id=old["donor_id"], recipient_id=old["recipient_id"], arm=old["arm"],
        image=old["image"], intended_payload=payload, payload_origin=old["payload_origin"],
        source_record=str(BINDING / "rows.jsonl"), calls=new, native_calls=native,
        original_calls=old["calls"], native_output_scope="fresh full native paired outputs",
        delivery=delivery(combined,q,h), original_delivery=old["delivery"],
        extracted_controls=extracted_controls(combined,ev.profile),
        native_extracted_controls=extracted_controls(native["combined"],ev.profile),
        quality_recipient=old["quality_recipient"], quality_donor=old["quality_donor"],
        combined_both_match=combined["outcome"]=="both_match", status="ok")


def binding_summary(rows):
    good = [r for r in rows if r["status"]=="ok"]
    donor = [r for r in good if r["arm"]=="public_donor_synthesis"]
    old_delivered = [r for r in donor if r["original_delivery"]["both_exact"]]
    retained = sum(r["delivery"]["both_exact"] and r["extracted_controls"]["both_disabled_read_presence"] for r in old_delivered)
    old_rejected = [r for r in good if r["arm"]!="public_recipient_authorization_demo" and r["original_calls"]["combined"]["outcome"]!="both_match"]
    new_accept = sum(r["combined_both_match"] for r in old_rejected)
    return dict(planned_images=31, completed=len(good), missing_or_failed=31-len(good),
        original_exact_donor_deliveries=len(old_delivered), retained_exact_donor_deliveries=retained,
        old_rejected_count=len(old_rejected), newly_accepted_old_rejected=new_accept,
        continuity_pass=len(good)==31 and len(old_delivered)==5 and retained==5 and new_accept==0,
        public_recipient_demo=[r for r in good if r["arm"]=="public_recipient_authorization_demo"],
        negative_interpretation="zero observed acceptance is not a calibrated FPR")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase",required=True,choices=("screen","cached-binding"))
    p.add_argument("--output-dir",required=True,type=Path)
    p.add_argument("--screen-run",type=Path,default=SCREEN)
    p.add_argument("--screen-result",type=Path,help="Completed RC screen run.json; required for shared binding budget")
    a=p.parse_args()
    originals=original_complete(a.screen_run)
    prior=0.
    if a.phase=="cached-binding":
        if a.screen_result is None:
            p.error("cached-binding requires --screen-result for shared 1800-second accounting")
        prior_record=json.loads(a.screen_result.read_text(encoding="utf-8"))
        if prior_record.get("phase")!="screen" or prior_record.get("method")!="F5-RC1" or prior_record.get("outcome")!="completed":
            raise ValueError("Require a completed F5-RC1 screen record")
        prior=float(prior_record["duration_seconds"])
    started=time.monotonic()
    a.output_dir.mkdir(parents=True,exist_ok=False)
    record=dict(schema="journal-read-conditioning-probe-v1",phase=a.phase,method="F5-RC1",routing_revision=1,
        commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),command=sys.argv,
        data_split="development",seeds=[],usd=0,screen_run=str(a.screen_run),
        config=dict(configurations=CONFIGS,conditions=CONDITIONS,owners=list(OWNERS[:2]),semantic_views=7,
            roster_size=1,binding="soft",thresholds="frozen profile",shared_seconds_cap=CAP),
        prior_screen_seconds=prior, screen_result=None if a.screen_result is None else str(a.screen_result),
        fpr_status="legacy fields unvalidated for routed system",outcome="running",rows=[])
    rows=record["rows"]
    write(a.output_dir/"run.json",record)
    if a.phase=="screen":
        lookup={(r["config"],r["source_id"]):r for r in originals}
        plan=[dict(config=c,source_id=sid) for c in CONFIGS for sid in IDS]
        plan += [dict(arm="frozen_clean_compatibility",source_id=sid) for sid in IDS]
    else:
        old_binding=read_rows(BINDING/"rows.jsonl")
        expected={(d,r,arm) for d,r in pairs() for arm in ARMS}|{(*pairs()[0],"public_recipient_authorization_demo")}
        if len(old_binding)!=31 or {(r["donor_id"],r["recipient_id"],r["arm"]) for r in old_binding}!=expected or any(r["status"]!="ok" for r in old_binding):
            raise ValueError("Cached binding input must contain all 31 fixed complete unique rows")
        plan=old_binding
    summarizer=screen_summary if a.phase=="screen" else binding_summary
    try:
        ev=Evaluator()
        record["profile"]=ev.profile
        for item in plan:
            tick=time.monotonic()
            row={k:item[k] for k in ("config","source_id","arm","donor_id","recipient_id") if k in item}
            try:
                if prior+time.monotonic()-started>=CAP:
                    raise RuntimeError("Shared local screen+binding 1800-second cap exhausted; no dropped denominator")
                if a.phase=="cached-binding":
                    row=binding_row(ev,item)
                elif "config" in item:
                    row=screen_row(ev,lookup[(CONFIGS[item["config"]],item["source_id"])],item["config"],a.screen_run,row)
                else:
                    sid=item["source_id"]
                    old=lookup[("R2",sid)]
                    new,native,_=calls(ev,load(F5_RUN/"images"/f"clean-{sid}-C1.png"),OWNERS[0],native=True)
                    row.update(calls=new,native_calls=native,payload=old["payload"],
                        delivery=delivery(new["combined"],int(old["payload"]["q"],16),int(old["payload"]["h"],16)),status="ok")
            except Exception:
                row.update(status="failed",error=traceback.format_exc())
                ev.torch.cuda.empty_cache()
            row["duration_seconds"]=time.monotonic()-tick
            rows.append(row)
            with (a.output_dir/"rows.jsonl").open("a",encoding="utf-8") as handle:
                handle.write(json.dumps(row,allow_nan=False)+"\n")
            record["summary"]=summarizer(rows)
            write(a.output_dir/"summary.json",record["summary"])
            write(a.output_dir/"run.json",record)
            print(json.dumps({k:row[k] for k in ("config","source_id","arm","status") if k in row}),flush=True)
        record["outcome"]="completed" if all(r["status"]=="ok" for r in rows) else "completed_with_failures"
        record["gpu_peak_allocated_bytes"]=ev.torch.cuda.max_memory_allocated()
        record["gpu_peak_reserved_bytes"]=ev.torch.cuda.max_memory_reserved()
    except Exception:
        record.update(outcome="failed",error=traceback.format_exc())
        for item in plan[len(rows):]:
            row={k:item[k] for k in ("config","source_id","arm","donor_id","recipient_id") if k in item}
            row.update(status="failed",error="Setup/fatal failure; see run.json")
            rows.append(row)
            with (a.output_dir/"rows.jsonl").open("a",encoding="utf-8") as handle:
                handle.write(json.dumps(row)+"\n")
        raise
    finally:
        record["duration_seconds"]=time.monotonic()-started
        record["shared_duration_seconds"]=prior+record["duration_seconds"]
        record["budget_overrun"]=record["shared_duration_seconds"]>CAP
        record["summary"]=summarizer(rows)
        if record["budget_overrun"]:
            record["summary"]["advancement_blocked_reason"]="Shared cached-probe time cap exceeded"
            if a.phase=="screen":
                record["summary"]["ranked_survivors"]=[]
                record["summary"]["selection_allowed"]=False
            else:
                record["summary"]["continuity_pass"]=False
        write(a.output_dir/"summary.json",record["summary"])
        write(a.output_dir/"run.json",record)


if __name__=="__main__":
    main()
