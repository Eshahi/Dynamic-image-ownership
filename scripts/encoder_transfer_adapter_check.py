"""Pipeline-correctness check of the amendment-1d adapters on one reserved smoke source.

Written by Claude (Opus 5.5), 2026-10-23. It embeds and reads back on clean images only
(TrustMark Q and Pixel Seal), and runs one MoVQ round trip. No regeneration, no study source,
no outcome: like the smoke phase, it can only reveal implementation faults.

Usage: python scripts/encoder_transfer_adapter_check.py --manifest <stage2a-config.json> --assets-root <dir> --out <json>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
import traceback

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import encoder_transfer_test as et


def psnr(a, b):
    import numpy as np
    mse = float(((a.astype("float64") - b.astype("float64")) ** 2).mean())
    return float("inf") if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--assets-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config, sources = et.load_contract(args.manifest)
    import encoder_transfer_runtime as rt
    smoke_id = sources["smoke"][0]["source_id"]
    rgb = rt.load_rgb(args.assets_root / "sources" / f"{smoke_id}.png")
    report = dict(source_id=smoke_id, role="reserved smoke source; pipeline correctness only", checks={})
    ok = True
    for arm, cls in (("trustmark-q", rt.TrustMarkQ), ("pixelseal", rt.PixelSeal)):
        tick = time.monotonic()
        try:
            adapter = cls(args.assets_root)
            bits = et.message(smoke_id, config["payload_bits"][arm], config["message_seed"])
            marked = adapter.embed(rgb, bits)
            on_marked = adapter.detect(marked, bits)
            on_clean = adapter.detect(rgb, bits)
            entry = dict(status="ok", psnr_marked_vs_source=psnr(rgb, marked),
                         marked_presence=on_marked["presence"], unmarked_presence=on_clean["presence"],
                         marked_native=on_marked.get("native"), unmarked_native=on_clean.get("native"),
                         seconds=time.monotonic() - tick)
            if not on_marked["presence"]["present"] or on_clean["presence"]["present"]:
                entry["status"] = "implementation_suspect"
                ok = False
            report["checks"][arm] = entry
            del adapter
            rt.release()
        except Exception:
            report["checks"][arm] = dict(status="error", error=traceback.format_exc())
            ok = False
    tick = time.monotonic()
    try:
        movq = rt.MoVQ(args.assets_root)
        back = rt.resize_rgb(movq.roundtrip(rt.resize_rgb(rgb, 1024)), 512)
        report["checks"]["movq"] = dict(status="ok", psnr_roundtrip_vs_source=psnr(rgb, back), seconds=time.monotonic() - tick)
        if psnr(rgb, back) < 20:
            report["checks"]["movq"]["status"] = "implementation_suspect"
            ok = False
    except Exception:
        report["checks"]["movq"] = dict(status="error", error=traceback.format_exc())
        ok = False
    report["passed"] = ok
    et.write(args.out, report)
    print(json.dumps(dict(passed=ok, **{k: v.get("status") for k, v in report["checks"].items()})))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
