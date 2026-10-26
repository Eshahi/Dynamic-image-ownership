"""Final-study Phase B under amendment B1: detector release and T7 quality on every executed output.

Written by Claude (Opus 5.5) on 2026-10-26 (user decisions in scripts/et_final_phase_b.py). Both stages require the
forecast seal, so no detector or quality value of a marked native output can exist before the forecasts are frozen.
They only read outputs that already exist and can be rerun while the outcome stage is still producing; every row is
journaled once per id.

detect: the unchanged stage-2 detectors (F5 r2, v5 r3, WAM, VINE-R adapters). Each arm's own outputs with its own
    detector and every C0 output with all four, for the clean inputs, the seven native cells and the B-codec control.
    F5/v5 marked items carry the correct-owner and wrong-owner calls; WAM/VINE-R carry the known and the wrong message.
quality: T7 distortions with the Phase-A quality implementation (PSNR/SSIM, GPU LPIPS): attack distortion d(y,u)
    against the item's own input u and total distortion d(y,x) against the canonical source x.

Usage: python scripts/et_final_phase_b_read.py --stage detect|quality --assets /workspace/assets --out /workspace/runs/et-phase-b
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
import et_final_phase_a as pa  # noqa: E402
import et_final_phase_b as pb  # noqa: E402
from encoder_transfer_test import ALPHA, message  # noqa: E402


def items(args):
    """(item id, image path, arm, control, source, input path) for every executed output that exists."""
    out = []
    clean = pa.Journal(args.out / "clean.jsonl").latest
    for r in clean.values():
        if r.get("kind") == "clean" and r.get("status") == "ok":
            out.append((r["id"], r["output"]["path"], r["arm"], r["control"], r["source_id"], None))
    inp = {(r["source_id"], r["arm"]): r["output"]["path"] for r in clean.values() if r.get("kind") == "clean" and r.get("status") == "ok"}
    for r in pa.Journal(args.out / "forecast.jsonl").latest.values():
        if r.get("kind") == "c0" and r.get("status") == "ok":
            out.append((f"native:{r['cell']}:{r['source']}:{r['seed']}:unmarked", r["output"]["path"], "unmarked", "C0", r["source"],
                        inp.get((r["source"], "unmarked"))))
    for r in pa.Journal(args.out / "outcome.jsonl").latest.values():
        if r.get("status") == "ok" and r.get("kind") in ("native", "ctrlB-codec"):
            out.append((r["id"], r["output"]["path"], r["arm"], "C0" if r["arm"] == "unmarked" else "C1", r["source"],
                        inp.get((r["source"], r["arm"]))))
    return out, clean


def detect(args):
    import torch
    torch.set_num_threads(args.threads)
    config, _ = pilot.channel_specs()
    journal = pa.Journal(args.out / "detect.jsonl")
    todo_all, clean = items(args)
    for method in pb.MARKS:
        todo = [it for it in todo_all if (it[2] == method or it[2] == "unmarked") and not journal.done(f"det:{method}:{it[0]}")]
        if not todo:
            continue
        adapter = rt.Internal(args.assets, config) if method in ("f5-r2", "v5-r3") else rt.Wam(args.assets) if method == "wam" else rt.Vine(args.assets)
        for n, (uid, path, arm, control, source, _) in enumerate(todo):
            row = dict(id=f"det:{method}:{uid}", kind="detect", method=method, item=uid, arm=arm, control=control, source=source)
            tick = time.monotonic()
            try:
                rgb = rt.load_rgb(path)
                if method in ("f5-r2", "v5-r3"):
                    payload = clean[f"clean:{source}:{method}:None:None"].get("payload") if control == "C1" else None
                    calls = adapter.detect(rgb, method, payload, control)
                else:
                    bits = message(source, config["payload_bits"][method], config["message_seed"])
                    calls = {ALPHA: adapter.detect(rgb, bits)}
                    wrong = message(source, config["payload_bits"][method], config["wrong_message_seed"])
                    calls[ALPHA]["wrong_message_presence"] = rt.presence(calls[ALPHA]["raw"].get("decoded_message"), wrong)
                row["calls"] = calls
                row["status"] = "ok"
            except Exception:
                row["status"] = "error_terminal"
                row["error"] = traceback.format_exc()[-2000:]
            row["seconds"] = time.monotonic() - tick
            journal.append(row)
            if n % 500 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] {method} {n}/{len(todo)}", flush=True)
        adapter = None
        rt.release()


def quality(args):
    import torch
    import et_final_phase_a_attacks as atk
    torch.set_num_threads(args.threads)
    qual = atk.Quality(args.assets)
    journal = pa.Journal(args.out / "quality.jsonl")
    todo, _ = items(args)
    for n, (uid, path, arm, control, source, inp) in enumerate(todo):
        qid = f"q:{uid}"
        if uid.startswith("clean:") or journal.done(qid):
            continue  # clean d(u,x) is in clean.jsonl
        row = dict(id=qid, kind="quality", item=uid, arm=arm, source=source)
        tick = time.monotonic()
        try:
            y, x = rt.load_rgb(path), rt.load_rgb(pb.source_png(args, source))
            row["total"] = qual(x, y)
            row["attack"] = row["total"] if arm == "unmarked" else qual(rt.load_rgb(inp), y)
            row["status"] = "ok"
        except Exception:
            row.update(status="error_terminal", error=traceback.format_exc()[-1500:])
        row["seconds"] = time.monotonic() - tick
        journal.append(row)
        if n % 2000 == 0:
            print(f"[{time.strftime('%H:%M:%S')}] quality {n}/{len(todo)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("detect", "quality"), required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=12)
    args = parser.parse_args()
    if not (args.out / "forecast-seal.json").exists():
        raise SystemExit("detector release and quality require the forecast seal")
    dict(detect=detect, quality=quality)[args.stage](args)


if __name__ == "__main__":
    main()
