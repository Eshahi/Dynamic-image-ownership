"""Final-study Phase B under amendment B1: acquisition, clean marking, sealed forecasts, marked outcomes, B-codec.

Written by Claude (Opus 5.5) on 2026-10-26. The user decided in chat (2026-10-26): run Phase B; law derivatives for
SD1.5 only as a declared exploratory amendment; a 50 instance-hour cap; held-out acquisition approved after a
development rehearsal. The frozen scope is research/encoder-transfer-20261019/final-study-20261025/phase-b/AMENDMENT-B1.md.

Stages (each resumable from its append-only journal, last row per id):
  acquire   manifest originals -> size/SHA1/licence/canonical/exact-hash checks -> sources/{id}.png, phase-b-sources.json
  clean     C0 input and the four marked inputs per source (stage-2 adapters and payloads), d(u,x) quality
  forecast  C0 native output of all 7 cells x 3 seeds with its noise tape stored; B1 law forecast for the R0 cells;
            ends by writing forecast-seal.json (journal SHA256 and complete inventory)
  outcome   refuses without a valid seal; marked native outputs replaying C0 tapes; B-codec control on five inputs
Detector release, quality and analysis: scripts/et_final_phase_b_read.py and phase-b/analyze_phase_b.py.

Rehearsal: --rehearsal 1790,1822 uses those development smoke sources' canonical PNGs instead of acquisition.

Usage: python scripts/et_final_phase_b.py --stage acquire|clean|forecast|outcome --assets /workspace/assets \
           --out /workspace/runs/et-phase-b [--rehearsal 1790,1822]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import encoder_transfer_runtime as rt  # noqa: E402
import et_final_pilot as pilot  # noqa: E402
import et_final_phase_a as pa  # noqa: E402
from encoder_transfer_test import ALPHA, ROOT, message  # noqa: E402

FS = ROOT / "research/encoder-transfer-20261019/final-study-20261025"
ARMS = ["unmarked", "f5-r2", "v5-r3", "wam", "vine-r"]
MARKS = ARMS[1:]
CELLS = [("R0", .1), ("R0", .2), ("R0", .4), ("R1", .1), ("R1", .2), ("R1", .4), ("K3", .2)]
LAW_CELLS = {("R0", .1), ("R0", .2), ("R0", .4)}
SEEDS = pa.SEEDS
UA = "ImageOwnershipThesisResearch/1.0 (academic watermark-robustness study; low-rate scripted download of POTD originals)"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=1, default=str), encoding="utf-8")


def sources(args):
    return [s["source_id"] for s in read(args.out / "phase-b-sources.json")["sources"]]


def source_png(args, s):
    return args.out / "sources" / f"{s}.png"


def clean_png(args, s, arm):
    return args.out / "clean" / f"clean_{s}_{arm}_None_None.png"


# ---------------------------------------------------------------- acquire

def http_get(url, retries=3):
    import urllib.request
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as exc:  # transient network errors only; the identical request is retried
            last = exc
            time.sleep(5 * (attempt + 1))
    raise last


def licence_now(titles):
    """Current Commons licence label and SHA1 for up to 50 file titles (one API request)."""
    import urllib.parse
    q = urllib.parse.urlencode(dict(action="query", prop="imageinfo", iiprop="sha1|size|extmetadata", titles="|".join(titles),
                                    format="json", formatversion="2", iiextmetadatafilter="LicenseShortName|License"))
    data = json.loads(http_get("https://commons.wikimedia.org/w/api.php?" + q))
    out = {}
    for page in data["query"]["pages"]:
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        out[page["title"]] = dict(sha1=info.get("sha1"), size=info.get("size"),
                                  licence=(meta.get("LicenseShortName") or {}).get("value"), missing=page.get("missing", False))
    for n in data["query"].get("normalized", []):  # the API reports requested titles it normalized
        if n["to"] in out:
            out[n["from"]] = out[n["to"]]
    return out, q


def acquire(args):
    import m1b_canonical_source as canon
    manifest = read(FS / "heldout-manifest.json")
    excl = set(read(FS / "phase-b/exclusion-sha256.json")["sha256_tokens"])
    journal = pa.Journal(args.out / "acquire.jsonl")
    (args.out / "originals").mkdir(parents=True, exist_ok=True)
    entries = sorted(manifest["sources"], key=lambda e: e["selection_index"])
    titles = [e["canonical_file_title"] for e in entries]
    current = {}
    for i in range(0, len(titles), 50):
        got, query = licence_now(titles[i:i + 50])
        current.update(got)
        journal.append(dict(id=f"licence-query:{i}", kind="licence_query", status="ok", query=query, utc_request=time.time()))
        time.sleep(1.1)
    seen = {}
    for e in entries:
        uid = f"acquire:{e['commons_page_id']}"
        if journal.done(uid):
            r = journal.latest[uid]
            if r["status"] == "ok":
                seen.setdefault(r["raw_sha256"], e["commons_page_id"])
                seen.setdefault(r["rgb8_sha256"], e["commons_page_id"])
            continue
        row = dict(id=uid, kind="acquire", source_id=e["commons_page_id"], assignment=e["assignment"],
                   selection_index=e["selection_index"], title=e["canonical_file_title"])
        try:
            now = current.get(e["canonical_file_title"]) or {}
            if now.get("missing") or now.get("licence") != e["licence_label"]:
                raise ValueError(f"licence persistence failed: manifest {e['licence_label']!r}, now {now.get('licence')!r}")
            if now.get("sha1") != e["sha1"]:
                raise ValueError("current Commons file SHA1 differs from the manifest (file revised since selection)")
            raw = http_get(e["original_file_url"])
            time.sleep(1.1)
            row["raw_bytes"] = len(raw)
            if len(raw) != e["size_bytes"] or hashlib.sha1(raw).hexdigest() != e["sha1"]:
                raise ValueError("downloaded size/SHA1 differs from the manifest")
            raw_sha = sha256(raw)
            (args.out / "originals" / f"{e['commons_page_id']}.jpg").write_bytes(raw)
            rgb, receipt = canon.canonicalize(raw, raw_sha)
            saved = rt.save_rgb(source_png(args, e["commons_page_id"]), rgb)
            hits = {raw_sha, receipt["rgb8_sha256"], saved["sha256"]} & excl
            if hits:
                raise ValueError(f"exact recorded-hash overlap: {sorted(hits)}")
            dup = seen.get(raw_sha) or seen.get(receipt["rgb8_sha256"])
            if dup:
                raise ValueError(f"exact duplicate of accepted source {dup}")
            seen[raw_sha] = seen[receipt["rgb8_sha256"]] = e["commons_page_id"]
            row.update(status="ok", raw_sha256=raw_sha, rgb8_sha256=receipt["rgb8_sha256"], canonical_png=saved, receipt=receipt,
                       licence_now=now["licence"])
        except Exception as exc:
            row.update(status="error_terminal", reason=str(exc)[-500:], error=traceback.format_exc()[-1500:])
            source_png(args, e["commons_page_id"]).unlink(missing_ok=True)
        journal.append(row)
        print(f"[{time.strftime('%H:%M:%S')}] {uid} {row['status']} {row.get('reason', '')[:100]}", flush=True)
    # Final 200: primaries in order, each failed primary replaced by the next unused ok reserve (frozen order).
    ok = {e["commons_page_id"] for e in entries if journal.latest[f"acquire:{e['commons_page_id']}"]["status"] == "ok"}
    primaries = [e for e in entries if e["assignment"] == "primary"]
    reserves = [e for e in entries if e["assignment"] == "reserve" and e["commons_page_id"] in ok]
    final, replacements = [], []
    for e in primaries:
        if e["commons_page_id"] in ok:
            final.append(e)
        elif reserves:
            r = reserves.pop(0)
            final.append(r)
            replacements.append(dict(failed=e["commons_page_id"], reason=journal.latest[f"acquire:{e['commons_page_id']}"]["reason"],
                                     reserve=r["commons_page_id"]))
    record = dict(schema="et-final-phase-b-sources-v1", frozen_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  n=len(final), complete=len(final) == 200, canonicalization=canon.VERSION, replacements=replacements,
                  failures=[dict(source_id=r["source_id"], assignment=r["assignment"], reason=r["reason"])
                            for r in journal.latest.values() if r.get("kind") == "acquire" and r["status"] != "ok"],
                  acquire_journal_sha256=sha256((args.out / "acquire.jsonl").read_bytes()),
                  sources=[dict(source_id=e["commons_page_id"], selection_index=e["selection_index"], assignment=e["assignment"],
                                title=e["canonical_file_title"], licence=e["licence_label"], attribution=e["attribution_plain"],
                                raw_sha256=journal.latest[f"acquire:{e['commons_page_id']}"]["raw_sha256"],
                                rgb8_sha256=journal.latest[f"acquire:{e['commons_page_id']}"]["rgb8_sha256"]) for e in final])
    path = args.out / "phase-b-sources.json"
    if path.exists():
        raise SystemExit("phase-b-sources.json already frozen; it is immutable")
    write(path, record)
    print(json.dumps(dict(n=record["n"], complete=record["complete"], replacements=len(replacements), failures=len(record["failures"]))))


def rehearsal_sources(args, ids):
    path = args.out / "phase-b-sources.json"
    if not path.exists():
        for s in ids:
            src = args.assets / "sources" / f"{s}.png"
            rt.save_rgb(source_png(args, s), rt.load_rgb(src))
        write(path, dict(schema="et-final-phase-b-sources-v1", rehearsal=True, data_split="development", n=len(ids),
                         sources=[dict(source_id=s) for s in ids]))


# ---------------------------------------------------------------- clean

def clean(args):
    import os
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import torch
    # The stage-2 runner's determinism settings, under which the development clean inputs were embedded.
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    config, _ = pilot.channel_specs()
    journal = pa.Journal(args.out / "clean.jsonl")
    ids = sources(args)
    for arm in ARMS:
        pending = [s for s in ids if not journal.done(f"clean:{s}:{arm}:None:None")]
        if not pending:
            continue
        adapter = rt.Internal(args.assets, config) if arm in ("f5-r2", "v5-r3") else rt.Wam(args.assets) if arm == "wam" else \
            rt.Vine(args.assets, encoding=True) if arm == "vine-r" else None
        for s in pending:
            uid = f"clean:{s}:{arm}:None:None"
            row = dict(id=uid, kind="clean", channel="clean", source_id=s, arm=arm, control="C0" if arm == "unmarked" else "C1")
            tick = time.monotonic()
            try:
                rt.seed_everything(config["implementation_seed"])
                rgb = rt.load_rgb(source_png(args, s))
                payload, report = None, None
                if arm in ("f5-r2", "v5-r3"):
                    marked, payload, report = adapter.embed(rgb, arm)
                elif arm == "unmarked":
                    marked = rgb
                else:
                    bits = message(s, config["payload_bits"][arm], config["message_seed"])
                    marked = adapter.embed(rgb, bits)
                    payload = dict(bits=bits)
                row.update(status="ok", output=rt.save_rgb(clean_png(args, s, arm), marked), payload=payload, embedding_report=report)
            except Exception:
                row.update(status="error_terminal", error=traceback.format_exc()[-2000:])
            row["seconds"] = time.monotonic() - tick
            journal.append(row)
            print(f"[{time.strftime('%H:%M:%S')}] {uid} {row['status']} {row['seconds']:.1f}s", flush=True)
        adapter = None
        rt.release()
    # Clean embedding quality d(u,x): permitted before forecasting (no detector output is read).
    from m1_latent_reconstruction import quality
    import three_threat_models as models
    import importlib.metadata
    lp = models.load_lpips(args.assets / "a6", Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
    for s in ids:
        for arm in MARKS:
            r = journal.latest.get(f"clean:{s}:{arm}:None:None")
            if not r or r["status"] != "ok" or "distortion" in r:
                continue
            x, u = rt.load_rgb(source_png(args, s)), rt.load_rgb(r["output"]["path"])
            r = dict(r, distortion=dict(status="ok", **quality(x, u), lpips=models.lpips_score(lp, x, u)))
            journal.append(r)


# ---------------------------------------------------------------- forecast

def forecast(args):
    import numpy as np
    import torch
    import f5_latent_codec as f5
    import revised_watermark_v5 as v5
    import et_final_phase_a_fit as fitmod
    if (args.out / "forecast-seal.json").exists():
        raise SystemExit("forecast already sealed")
    amendment = read(FS / "phase-b/amendment-b1.json")
    kappa = amendment["kappa_R0"]["value"]
    config, specs = pilot.channel_specs()
    profile = pilot.read(ROOT / config["profile_file"])
    checked, key, cfg = v5._resolve(profile, None)
    layout = f5.Layout(checked, key, cfg, v5.canonical_owner(ALPHA))
    reader = f5.Reader(args.assets / "a6", device="cuda")
    resize = pilot.Resize(1024, 512, torch)
    journal = pa.Journal(args.out / "forecast.jsonl")
    cleanj = pa.Journal(args.out / "clean.jsonl")
    ids = sources(args)
    (args.out / "tapes").mkdir(parents=True, exist_ok=True)

    def inp(s, arm):
        r = cleanj.latest.get(f"clean:{s}:{arm}:None:None")
        return rt.load_rgb(r["output"]["path"]) if r and r["status"] == "ok" else None

    for fam in ("R0", "R1", "K3"):
        todo = [(st, s, seed) for f, st in CELLS if f == fam for s in ids for seed in SEEDS
                if not journal.done(f"c0:{fam}-{st}:{s}:{seed}")]
        if not todo:
            continue
        regen = rt.Regenerator(args.assets, specs[fam])
        modules = [regen.pipe.unet, regen.pipe.movq if fam == "K3" else regen.pipe.vae]
        with pilot.ClassicAttention(*modules):  # option (a)
            for strength, s, seed in todo:
                cell = f"{fam}-{strength}"
                uid = f"c0:{cell}:{s}:{seed}"
                row = dict(id=uid, kind="c0", cell=cell, family=fam, strength=strength, source=s, seed=seed)
                tick = time.monotonic()
                tape, hooks = pilot.Tape(), pilot.Hooks(regen.pipe)

                def keep_tape():
                    # Stored even when C0 itself is safety-blocked: as in Phase A, the marked trajectories still replay it.
                    tape_path = args.out / "tapes" / f"{cell}_{s}_{seed}.pt"
                    torch.save([d.cpu() for d in tape.draws], tape_path)
                    row["tape"] = dict(path=str(tape_path), draws=len(tape.draws), sha256=sha256(tape_path.read_bytes()), receipt=tape.receipt())
                try:
                    x = inp(s, "unmarked")
                    if x is None:
                        raise RuntimeError("clean C0 input unavailable")
                    try:
                        out = pa.run_native(fam, regen, x, strength, seed, tape.record(), hooks)
                    except Exception:
                        if tape.draws:
                            keep_tape()
                        raise
                    row["output"] = rt.save_rgb(args.out / "native" / f"{cell}_{s}_unmarked_{seed}.png", out)
                    keep_tape()
                    row["status"] = "ok"
                    if (fam, strength) in LAW_CELLS:
                        u = inp(s, "f5-r2")
                        if u is None:
                            row["law"] = dict(status="unavailable", reason="F5 marked input unavailable")
                        else:
                            calls = [(pilot.detach_tree(a), pilot.detach_tree(k)) for a, k in hooks.calls]
                            try:
                                v, diag = pa.law_tangent(fam, regen, reader, layout, resize, calls, hooks.states, tape.draws,
                                                         pilot.native_input(fam, x), pilot.native_input(fam, u))
                                b = np.asarray(layout.projections(reader.latent(out)))
                                if not (np.isfinite(v).all() and np.isfinite(b).all()):
                                    raise FloatingPointError("nonfinite law vector")
                                diag.pop("chips_float")
                                row["law"] = dict(status="ok", v=v.tolist(), b=b.tolist(), max_primal_err=max(diag["step_primal_rel_err"]),
                                                  **{k: diag[k] for k in ("start_state_rel_err", "displacement_norm", "decode_precision")})
                            except Exception:
                                row["law"] = dict(status="unavailable", error=traceback.format_exc()[-1500:])
                except Exception as exc:
                    row["status"] = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                    row["error"] = traceback.format_exc()[-1500:]
                row["seconds"] = time.monotonic() - tick
                journal.append(row)
                print(f"[{time.strftime('%H:%M:%S')}] {uid} {row['status']} law={row.get('law', {}).get('status', '-')} "
                      f"{row['seconds']:.1f}s", flush=True)
                del tape, hooks
                rt.release()
        regen = modules = None
        rt.release()
    # B1 forecasts: C0 seven-view descriptor (the semantic proxy) and the reader decision on b + kappa v.
    internal = rt.Internal(args.assets, config)
    for r in list(journal.latest.values()):
        if r.get("kind") != "c0" or r.get("status") != "ok" or (r["family"], r["strength"]) not in LAW_CELLS or "forecast" in r:
            continue
        law = r.get("law") or {}
        try:
            if law.get("status") != "ok":
                raise RuntimeError("law vector unavailable")
            f0 = [float(z) for z in internal.features(rt.load_rgb(r["output"]["path"]), 7)]
            pred = fitmod.semantic_predict(np.asarray(law["b"]) + kappa * np.asarray(law["v"]), f0, profile)
            fc = dict(status="ok", f0=f0, **pred)
        except Exception:
            fc = dict(status="unavailable", error=traceback.format_exc()[-800:])
        journal.append(dict(r, forecast=fc))
    internal = None
    rt.release()
    # Seal: the complete inventory of planned trajectories and the journal hash, before any marked output exists.
    marked = list((args.out / "native").glob("*_f5-r2_*.png")) + list((args.out / "native").glob("*_v5-r3_*.png"))
    if marked:
        raise SystemExit("marked native outputs exist before the seal; refusing")
    latest = pa.Journal(args.out / "forecast.jsonl").latest
    planned = [f"c0:{f}-{st}:{s}:{seed}" for f, st in CELLS for s in ids for seed in SEEDS]
    missing = [p for p in planned if p not in latest]
    if missing:
        raise SystemExit(f"{len(missing)} planned C0 trajectories have no row; rerun forecast")
    from collections import Counter
    inv = Counter((latest[p]["cell"], latest[p]["status"]) for p in planned)
    finv = Counter((latest[p]["cell"], (latest[p].get("forecast") or {}).get("status", "none")) for p in planned
                   if (latest[p]["family"], latest[p]["strength"]) in LAW_CELLS)
    seal = dict(sealed_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), amendment_sha256=sha256((FS / "phase-b/AMENDMENT-B1.md").read_bytes()),
                amendment_values_sha256=sha256((FS / "phase-b/amendment-b1.json").read_bytes()), kappa_R0=kappa,
                forecast_journal_sha256=sha256((args.out / "forecast.jsonl").read_bytes()),
                sources_sha256=sha256((args.out / "phase-b-sources.json").read_bytes()), planned_trajectories=len(planned),
                c0_status={f"{c}|{st}": n for (c, st), n in sorted(inv.items())},
                forecast_status={f"{c}|{st}": n for (c, st), n in sorted(finv.items())})
    write(args.out / "forecast-seal.json", seal)
    print(json.dumps(seal, indent=1))


# ---------------------------------------------------------------- outcome

def outcome(args):
    import torch
    seal_path = args.out / "forecast-seal.json"
    if not seal_path.exists():
        raise SystemExit("outcome requires forecast-seal.json (AMENDMENT-B1 section 5)")
    seal = read(seal_path)
    if sha256((args.out / "forecast.jsonl").read_bytes()) != seal["forecast_journal_sha256"]:
        raise SystemExit("forecast journal changed after the seal")
    _, specs = pilot.channel_specs()
    fj = pa.Journal(args.out / "forecast.jsonl")
    cleanj = pa.Journal(args.out / "clean.jsonl")
    journal = pa.Journal(args.out / "outcome.jsonl")
    ids = sources(args)
    for fam in ("K3", "R0", "R1"):  # K3 first: its load peak comes before the parallel detector release starts
        todo = [(st, s, seed, arm) for f, st in CELLS if f == fam for s in ids for seed in SEEDS for arm in MARKS
                if not journal.done(f"native:{fam}-{st}:{s}:{seed}:{arm}")]
        if not todo:
            continue
        regen = rt.Regenerator(args.assets, specs[fam])
        modules = [regen.pipe.unet, regen.pipe.movq if fam == "K3" else regen.pipe.vae]
        with pilot.ClassicAttention(*modules):
            for strength, s, seed, arm in todo:
                cell = f"{fam}-{strength}"
                uid = f"native:{cell}:{s}:{seed}:{arm}"
                row = dict(id=uid, kind="native", cell=cell, family=fam, strength=strength, source=s, seed=seed, arm=arm)
                tick = time.monotonic()
                try:
                    c0 = fj.latest.get(f"c0:{cell}:{s}:{seed}")
                    if not c0 or not c0.get("tape"):
                        raise RuntimeError(f"C0 trajectory has no recorded draws ({(c0 or {}).get('status')})")
                    cr = cleanj.latest.get(f"clean:{s}:{arm}:None:None")
                    if not cr or cr["status"] != "ok":
                        raise RuntimeError("marked input unavailable")
                    tape_path = Path(c0["tape"]["path"])
                    if sha256(tape_path.read_bytes()) != c0["tape"]["sha256"]:
                        raise RuntimeError("noise tape hash mismatch")
                    tape = pilot.Tape()
                    tape.draws = [d.cuda() for d in torch.load(tape_path)]
                    out = pa.run_native(fam, regen, rt.load_rgb(cr["output"]["path"]), strength, seed + 1000, tape.replay())
                    if tape.cursor != len(tape.draws):
                        raise RuntimeError(f"replay consumed {tape.cursor} of {len(tape.draws)} draws")
                    row["output"] = rt.save_rgb(args.out / "native" / f"{cell}_{s}_{arm}_{seed}.png", out)
                    row["status"] = "ok"
                except Exception as exc:
                    row["status"] = "safety_blocked" if "safety" in str(exc).lower() or "nsfw" in str(exc).lower() else "error_terminal"
                    row["error"] = traceback.format_exc()[-1500:]
                row["seconds"] = time.monotonic() - tick
                journal.append(row)
                if arm == "vine-r":
                    print(f"[{time.strftime('%H:%M:%S')}] {cell}:{s}:{seed} {row['status']} {row['seconds']:.1f}s", flush=True)
                rt.release()
        regen = modules = None
        rt.release()
    # B-codec control: the frozen deterministic codec of attack B (no selection needed), one output per input.
    import et_final_phase_a_attacks as atk
    r0 = rt.Regenerator(args.assets, specs["R0"])  # AttackB keeps it for inversion; the codec uses its own fp32 VAE
    contexts = [pilot.ClassicAttention(r0.pipe.unet, r0.pipe.vae)]
    for c in contexts:
        c.__enter__()
    try:
        codec = atk.AttackB(args.assets, r0)
        for s in ids:
            for arm in ARMS:
                uid = f"ctrlB-codec:{s}:{arm}"
                if journal.done(uid):
                    continue
                row = dict(id=uid, kind="ctrlB-codec", source=s, arm=arm)
                tick = time.monotonic()
                try:
                    cr = cleanj.latest.get(f"clean:{s}:{arm}:None:None")
                    if not cr or cr["status"] != "ok":
                        raise RuntimeError("input unavailable")
                    row["output"] = rt.save_rgb(args.out / "control" / f"Bcodec_{s}_{arm}.png", codec.codec(rt.load_rgb(cr["output"]["path"])))
                    row["status"] = "ok"
                except Exception:
                    row.update(status="error_terminal", error=traceback.format_exc()[-1500:])
                row["seconds"] = time.monotonic() - tick
                journal.append(row)
    finally:
        for c in reversed(contexts):
            c.__exit__(None, None, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("acquire", "clean", "forecast", "outcome"), required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rehearsal", default="", help="comma-separated development source IDs instead of acquisition")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.rehearsal:
        if args.stage == "acquire":
            raise SystemExit("a rehearsal never acquires held-out data")
        rehearsal_sources(args, [int(x) for x in args.rehearsal.split(",")])
    elif args.stage != "acquire" and read(args.out / "phase-b-sources.json").get("rehearsal"):
        raise SystemExit("this output folder is a rehearsal folder")
    dict(acquire=acquire, clean=clean, forecast=forecast, outcome=outcome)[args.stage](args)


if __name__ == "__main__":
    main()
