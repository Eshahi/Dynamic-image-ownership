"""Descriptive source/pair analysis of the two fixed journal-development probes."""
from __future__ import annotations
import argparse
import json
import statistics
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from journal_vae_probe import SOURCES, OWNERS, checked, write
from journal_binding_probe import pairs, ARMS, summary as binding_summary


def distribution(values):
    values = list(values)
    return dict(n=len(values), mean=statistics.mean(values), median=statistics.median(values),
                sd=statistics.stdev(values) if len(values) > 1 else None, min=min(values), max=max(values)) if values else dict(n=0)


def inventory(rows, expected, fields):
    keys = [tuple(r[f] for f in fields) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate scientific observation")
    if set(keys) - set(expected):
        raise ValueError("Unexpected scientific observation")
    return dict(planned=len(expected), present=len(rows), missing=[list(k) for k in sorted(set(expected) - set(keys))],
                failed=[list(k) for k, r in zip(keys, rows) if r["status"] != "ok"])


def analyze(vae, binding):
    vr = [json.loads(line) for line in (vae / "rows.jsonl").read_text().splitlines()]
    br = [json.loads(line) for line in (binding / "rows.jsonl").read_text().splitlines()]
    conditions = ("clean", "sd15_vae", "sdxl_vae")
    ve = [(s, m, c, a) for s in SOURCES for m in ("f5", "v5") for c in ("C0", "C1") for a in conditions]
    be = [(d, r, a) for d, r in pairs() for a in ARMS] + [(*pairs()[0], "public_recipient_authorization_demo")]
    result = dict(scope="exploratory development; sources and disjoint pairs are the units; no hypothesis test",
                  runs={"vae": str(vae), "binding": str(binding)},
                  inventory={"vae": inventory(vr, ve, ("source_id", "method", "control", "condition")),
                             "binding": inventory(br, be, ("donor_id", "recipient_id", "arm"))},
                  vae={}, paired={}, binding=binding_summary(br))
    for method in ("f5", "v5"):
        for condition in conditions:
            group = [r for r in vr if r["method"] == method and r["condition"] == condition and r["status"] == "ok"]
            marked = [r for r in group if r["control"] == "C1"]
            negatives = [r for r in group if r["control"] == "C0"]
            calls = [r["calls"][OWNERS[0]] for r in marked]
            result["vae"][f"{method}/{condition}"] = dict(denominator=12, completed=len(marked),
                checked=sum(checked(c) for c in calls), found=sum(bool(c["semantic"]["found"]) for c in calls),
                unread=sum(bool(c["semantic"]["found"] and not c["semantic"]["read"]) for c in calls),
                read_rejected=sum(bool(c["semantic"]["read"] and not c["semantic"]["content_match"]) for c in calls),
                both_match=sum(c["outcome"] == "both_match" for c in calls),
                c0_any=sum(bool(r["calls"][OWNERS[0]]["watermark_found"]) for r in negatives), c0_completed=len(negatives),
                wrong_any=sum(bool(r["calls"][OWNERS[1]]["watermark_found"]) for r in marked),
                input_metrics={k: distribution(r["quality_input"][k] for r in marked if r["quality_input"][k] is not None)
                               for k in ("psnr_db", "ssim_rgb", "lpips")},
                source_metrics={k: distribution(r["quality_source"][k] for r in marked if r["quality_source"][k] is not None)
                                for k in ("psnr_db", "ssim_rgb", "lpips")},
                proxy={str(limit): {"qualified": sum(r["quality_input"]["lpips"] <= limit for r in marked),
                    "checked": sum(checked(r["calls"][OWNERS[0]]) for r in marked if r["quality_input"]["lpips"] <= limit)} for limit in (.2, .3)},
                failures=[dict(source_id=r["source_id"], call=r["calls"][OWNERS[0]], quality=r["quality_input"])
                          for r in marked if not checked(r["calls"][OWNERS[0]])])
            if condition == "clean":
                result["vae"][f"{method}/{condition}"]["strict_quality"] = sum(
                    (r["quality_source"]["psnr_infinite"] or r["quality_source"]["psnr_db"] > 35)
                    and r["quality_source"]["ssim_rgb"] > .9 and r["quality_source"]["lpips"] < .1 for r in marked)
    lookup = {(r["source_id"], r["method"], r["condition"]): checked(r["calls"][OWNERS[0]])
              for r in vr if r["control"] == "C1" and r["status"] == "ok"}
    for condition in conditions:
        complete = [(lookup[(s, "f5", condition)], lookup[(s, "v5", condition)]) for s in SOURCES
                    if (s, "f5", condition) in lookup and (s, "v5", condition) in lookup]
        result["paired"][condition] = dict(complete_sources=len(complete), both=sum(a and b for a,b in complete),
                f5_only=sum(a and not b for a,b in complete), v5_only=sum(b and not a for a,b in complete),
                neither=sum(not a and not b for a,b in complete))
    for arm, stats in result["binding"].items():
        good = [r for r in br if r["arm"] == arm and r["status"] == "ok"]
        stats["recipient_metrics"] = {k: distribution(r["quality_recipient"][k] for r in good if r["quality_recipient"][k] is not None)
                                      for k in ("psnr_db", "ssim_rgb", "lpips")}
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vae-run", required=True, type=Path)
    p.add_argument("--binding-run", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("Use a fresh analysis output")
    write(args.output, analyze(args.vae_run, args.binding_run))
