"""Render the binding T7 tables and figures for the encoder-transfer study (stage 2a, or the union of 2a and 2b).

Written by Claude (Opus 5.5) on 2026-10-24, after the stage-2a label was fixed; extended on 2026-10-25 to the
stage-2b union (strengths .1/.2/.4, the R1 rinse, P5 smoothing and its control, full Kandinsky 3). It reads only
the saved run outputs and the frozen contract, and recomputes no endpoint: every count comes from `metrics.json`
or from the persisted per-call results in `rows.jsonl`. The stage-2b journal holds every stage-2a row (copied
byte for byte), so its `metrics.json` covers the union. The T7 reporting plan is in
research/encoder-transfer-20261019/design-research/T7-fair-reporting/synthesis.md.

Usage (needs matplotlib, numpy and Pillow):
  python scripts/encoder_transfer_report.py --run <dev-run>/results --out research/encoder-transfer-20261019/report
  python scripts/encoder_transfer_report.py --run <stage-2b dev-run>/results --prior-run <stage-2a dev-run>/results \
      --out research/encoder-transfer-20261019/report
--prior-run supplies the inherited stage-2a images (Figure 7) and the stage-2a provenance (Table 7).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "research/encoder-transfer-20261019"
ALPHA = "qim-pilot-owner-alpha"
ARMS = ["f5-r2", "v5-r3", "wam", "vine-r", "trustmark-q", "pixelseal"]
INTERNAL = ["f5-r2", "v5-r3"]
EXTERNAL = ["wam", "vine-r", "trustmark-q", "pixelseal"]
LABEL = {"f5-r2": "F5 r2", "v5-r3": "v5 r3", "wam": "WAM", "vine-r": "VINE-R", "trustmark-q": "TrustMark Q",
         "pixelseal": "Pixel Seal", "unmarked": "C0 (unmarked)"}
# Okabe-Ito, colour-blind safe; C0 in grey.
COLOR = {"f5-r2": "#D55E00", "v5-r3": "#E69F00", "wam": "#56B4E9", "vine-r": "#009E73",
         "trustmark-q": "#CC79A7", "pixelseal": "#0072B2", "unmarked": "#7F7F7F"}
MARKER = {"f5-r2": "o", "v5-r3": "s", "wam": "^", "vine-r": "D", "trustmark-q": "v", "pixelseal": "P"}
STRENGTHS = (.1, .2, .4)
# Every (channel, strength) cell of the frozen grid, in report order; a cell absent from metrics.json was not run.
CELLS = [("clean", None), ("X1", None), ("X2", None), ("D1", None), ("D3", None),
         ("R0", .1), ("R0", .2), ("R0", .4), ("R1", .1), ("R1", .2), ("R1", .4),
         ("R1-rinse", .1), ("R1-smooth", .2), ("R1-mode", .2), ("R3", .2)]
DIAG = ["clean", "X1", "X2", "D1", "D3"]
VARIANTS = [("R1", .1), ("R1-rinse", .1), ("R1", .2), ("R1-smooth", .2), ("R1-mode", .2), ("R3", .2)]
CHANNEL_LABEL = {"clean": "clean", "X1": "X1 resize x1", "X2": "X2 resize x2", "D1": "D1 SDXL VAE",
                 "D3": "D3 Kandinsky MoVQ", "R0": "R0 SD1.5", "R1": "R1 SDXL", "R1-rinse": "R1 rinse .1+.1",
                 "R1-smooth": "R1-smooth (P5)", "R1-mode": "R1-mode (P5 control)", "R3": "R3 Kandinsky 3"}
# Per-stage provenance that the run records do not carry (vast.ai container, laptop commit, budget clock).
PROVENANCE = {
    "stage2a": dict(container="57402655", laptop="b4b2810",
                    clock="from the first instance creation (2026-10-23 17:28Z, including the stopped period)"),
    "stage2b": dict(container="57583551", laptop="66d6944",
                    clock="from the instance start (2026-10-25 00:11:36Z)"),
}
# Step-1 context, copied from research/journal-upgrade-20261009/unseen-regenerator-results.md
# (source-majority endpoints, 24 development sources, seeds 0-2 as defined there).
STEP1 = [("SD1.5 img2img .2", "SD1.x", "f5-r2", 22, 24), ("SD1.5 img2img .2", "SD1.x", "v5-r3", 5, 24),
         ("SD2.1-base img2img .2", "SD1.x (shared encoder)", "f5-r2", 24, 24),
         ("SD2.1-base img2img .2", "SD1.x (shared encoder)", "v5-r3", 5, 24)]


def skey(strength):
    return "None" if strength is None else str(strength)


def sfmt(strength):
    return "" if strength is None else f"{strength:g}".lstrip("0")


def cell_label(channel, strength):
    if channel in ("R0", "R1", "R3"):
        return f"{CHANNEL_LABEL[channel]} {sfmt(strength)}"
    if channel in ("R1-smooth", "R1-mode"):
        return f"{CHANNEL_LABEL[channel]} .2"
    return CHANNEL_LABEL[channel]


def endpoint(arm):
    return "C" if arm in INTERNAL else "presence"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frac(k, n):
    return f"{k}/{n}"


def fmt(x, digits=3):
    if x is None:
        return "NA"
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    return str(x)


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


class Stage:
    """One stage's own records: run, smoke, memory and driver log."""

    def __init__(self, results, tag):
        self.tag = tag
        self.dir = Path(results)
        full = self.dir / f"{tag}-full"
        self.record = read(full / "run.json")
        self.memory = read(full / "memory-phases.json")
        self.smoke = read(self.dir / f"{tag}-smoke/run.json")
        self.smoke_timing = read(self.dir / f"{tag}-smoke/smoke-timing.json")
        self.driver_log = (self.dir / "driver.log").read_text(encoding="utf-8")
        self.images = full / "images"


class Run:
    def __init__(self, results, prior=None):
        self.dir = Path(results)
        self.tag = "stage2b" if (self.dir / "stage2b-full").exists() else "stage2a"
        self.stage = Stage(self.dir, self.tag)
        self.prior = Stage(prior, "stage2a") if prior else None
        self.stages = [s for s in (self.prior, self.stage) if s is not None]
        full = self.dir / f"{self.tag}-full"
        self.metrics = read(full / "metrics.json")
        self.record = self.stage.record
        self.config = read(full / "effective-config.json")
        self.rows = {}
        with open(full / "rows.jsonl", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                self.rows[row["id"]] = row
        self.image_dirs = [s.images for s in reversed(self.stages)]
        self.cells = self.metrics["cells"]
        self.rep = self.metrics["reporting"]
        self.sources = read(ROOT / self.config["sources_file"])["sources"]
        present = {tuple(k.split("/")[1:3]) for k in self.cells}
        self.cells_run = [(c, s) for c, s in CELLS if (c, skey(s)) in present]
        self.union = self.tag == "stage2b"
        self.scope = "stages 2a and 2b (union)" if self.union else "stage 2a"

    def ran(self, channel, strength):
        return (channel, strength) in self.cells_run

    def not_run(self):
        return [cell_label(c, s) for c, s in CELLS if not self.ran(c, s)]

    def channel_arms(self, channel, strength=None):
        if channel == "clean":
            return list(self.config["arms"])
        spec = next(c for c in self.config["channels"] if c["id"] == channel)
        return list(spec.get("arms_by_strength", {}).get(str(strength), spec.get("arms", [])))

    def cell(self, arm, channel, strength=None, pred=None):
        return self.cells.get(f"{arm}/{channel}/{skey(strength)}/{pred or endpoint(arm)}")

    def ext(self, arm, channel, strength=None):
        return self.rep["external_operating_points"].get(f"{arm}/{channel}/{skey(strength)}")

    def quality(self, arm, channel, strength=None):
        return self.rep["quality"].get(f"{arm}/{channel}/{skey(strength)}")

    def unit_rows(self, arm=None, channel=None, strength="any"):
        for row in self.rows.values():
            if ((arm is None or row["arm"] == arm) and (channel is None or row["channel"] == channel)
                    and (strength == "any" or row.get("strength") == strength)):
                yield row

    def image(self, row):
        name = Path(row["output"]["path"]).name
        for folder in self.image_dirs:
            if (folder / name).exists():
                return folder / name
        return None


NOT_RUN = "not run by design (stage 2a result)"


def cell_text(cell, outputs=True):
    if cell is None:
        return "—"
    text = frac(cell["positive_sources"], cell["planned_sources"])
    if outputs:
        text += f" · {frac(cell['observed_positive_calls'], cell['planned_calls'])}"
    return text


def cp(cell):
    lo, hi = cell["cp95"]
    return f"[{lo:.3f}, {hi:.3f}]"


def metric_summary(block, name):
    if not block or name not in block:
        return "NA"
    m = block[name]["complete_source_medians"]
    if not m.get("observed"):
        inf = block[name].get("infinite_outputs", 0)
        return f"∞ ({inf} identical)" if inf else "NA"
    digits = 2 if name == "psnr_db" else 3
    return f"{m['median']:.{digits}f} [{m['q1']:.{digits}f}, {m['q3']:.{digits}f}] ({m['observed']}/{block[name].get('planned_sources', 60)})"


# ---------------------------------------------------------------- tables

def table1(run):
    c = run.config
    f5 = c["f5"]
    arms = [
        ("F5 r2", "content-derived q32 (robust latent-read tier) and H32 (fragile tier); 320 chips per tier; not an arbitrary-message scheme",
         f"PSNR target {f5['psnr_db']:g} dB, {f5['steps']} steps, margin {f5['target_margin']:g}, mask power {f5['mask_power']:g}, DCT band {f5['band']}, whitening {f5['whitening']:g}, {f5['refine_rounds']} refinement, {f5['binding']} binding, {f5['semantic_views']} semantic views",
         "C = semantic read and content match; 2 of 3 seeds", "frozen S/C/Q/J/H/F/A predicates", "claimed owner, public profile, pinned CLIP ViT-B/32, SD1.5 VAE"),
        ("v5 r3", "same two structured 32-bit codes; 320 chips per tier", "historical v5 r3 embed, one semantic view",
         "C; 2 of 3 seeds", "frozen predicates", "owner, profile, CLIP"),
        ("WAM (MIT, 2c08af04)", "32 arbitrary message bits", "native setting, frozen",
         "known-message matches ≥ 27/32", "mask fraction > .07 at pixel probability > .5 (paper rule; calibration transfer to the MIT model unverified)", "candidate message"),
        ("VINE-R (d72f11a)", "100 arbitrary message bits", "native setting, SD-Turbo b261bac",
         "known-message matches ≥ 69/100", "no fixed native threshold (descriptive ROC)", "candidate message"),
        ("TrustMark Q (6df5a0a)", f"{c['trustmark']['payload_bits']} payload bits, {c['trustmark']['encoding']} (100-bit codeword)",
         f"strength {c['trustmark']['wm_strength']:g}, {c['trustmark']['wm_merge']} merge; {c['trustmark']['decode']}",
         "native BCH detected and matches ≥ 46/61", "BCH_5 decode success", "candidate message"),
        ("Pixel Seal (videoseal 870ca7f)", f"{c['pixelseal']['nbits']} message bits", f"{c['pixelseal']['card']}, {c['pixelseal']['img_size_proc']} px processing, {c['pixelseal']['mode']}",
         "matches ≥ 159/256", "none", "candidate message"),
    ]
    models = {"sd15": "SD1.5 (451f4fe)", "sdxl": "SDXL base 1.0 (4621659)", "kandinsky3": "Kandinsky 3 (bf79e6c), fp16 variant"}
    channel_rows = []
    for spec in c["channels"]:
        cid = spec["id"]
        if spec.get("enabled") is False:
            channel_rows.append((cid, spec.get("kind", ""), spec.get("family", ""), "—", "—", "—", "—", "—", f"disabled: {spec.get('reason', '')}"))
            continue
        kind = spec["kind"]
        strengths = spec.get("strengths") or []
        if kind in ("diffusion", "smoothing", "mode", "rinse"):
            model = models[spec["family"]]
            if kind == "diffusion" and spec["family"] == "sdxl":
                model += "; img2img samples the posterior of the fp16-rounded input"
            elif spec["family"] == "kandinsky3":
                model += "; shipped DDPM cosine schedule (squaredcos_cap_v2), so .2 noises less than the scaled-linear R0/R1 schedule"
            if kind == "smoothing":
                model += "; input = mean SDXL posterior mode over 4 antithetic Gaussian pairs (σ = 2/255)"
            elif kind == "mode":
                model += "; input = SDXL posterior mode of the unperturbed image (P5 matched control)"
            elif kind == "rinse":
                model += "; second .1 pass on the R1 .1 output"
            res = f"{spec['resolution']} internal / 512 output"
            if kind == "rinse":
                steps = "DDIM 20 × .1 = 2 executed, twice"
            else:
                sched = "DDPM (native)" if spec["family"] == "kandinsky3" else "DDIM"
                steps = "; ".join(f"{sched} {spec['steps']} × {sfmt(s)} = {int(spec['steps'] * s)} executed" for s in strengths)
            prompt = f"empty prompt, CFG {spec.get('guidance_scale', 1):g}"
            seeds = ", ".join(str(s) for s in spec["seeds"])
            if kind == "rinse":
                seeds = ", ".join(f"({s}, {s + spec.get('seed_offset', 100)})" for s in spec["seeds"])
            strengths_text = ", ".join(sfmt(s) for s in strengths)
        elif kind == "vae":
            model = "SDXL VAE, posterior mode, fp32" if spec["family"] == "sdxl" else "Kandinsky 3 MoVQ (bf79e6c), fp32 from fp16 weights"
            res, steps, prompt, strengths_text, seeds = f"{spec['resolution']} internal / 512 output", "encode-decode only", "—", "—", "deterministic"
        else:
            model = f"PIL Lanczos 512→1024→512, {spec['passes']} pass(es)"
            res, steps, prompt, strengths_text, seeds = "1024 internal / 512 output", "—", "—", "—", "deterministic"
        arms_text = ", ".join(LABEL[a] for a in spec["arms"]) + ", C0"
        scoped = spec.get("arms_by_strength") or {}
        if scoped:
            arms_text += "; " + "; ".join(f"at {sfmt(float(s))} only {', '.join(LABEL[a] for a in v)}, C0" for s, v in sorted(scoped.items()))
        if not run.ran(cid, strengths[0] if strengths else None):
            arms_text += f" ({NOT_RUN})"
        channel_rows.append((cid, kind, model, res, steps, prompt, strengths_text, seeds, arms_text))
    return "\n\n".join([
        "### Table 1. Design and operating points",
        "Arms, at their frozen or native settings. The common thresholds are one-sided binomial random-message rules, not measured image false-positive rates.",
        table(["Arm (revision)", "Embedded representation", "Embedding setting", "Common operating point", "Native rule", "Readout side information"], arms),
        "Channels. Every regeneration resizes the 512 RGB8 mark to the internal resolution with PIL Lanczos and back to 512 afterwards. Executed steps follow the diffusers img2img convention int(steps × strength).",
        table(["Channel", "Kind", "Model", "Resolution", "Steps", "Prompt", "Strengths", "Seeds", "Arms read"], channel_rows),
        f"Sources: n = {c['n']} development sources (`{c['sources_file']}`, SHA-256 {c['sources_sha256'][:8]}…); smoke sources 1790 and 1822 are disjoint. Message seed {c['message_seed']}, wrong-message seed {c['wrong_message_seed']}.",
    ])


def table2(run):
    d = run.metrics["decision"]
    paired = run.metrics["paired_primary_comparisons"]
    desc = run.metrics["descriptive_comparisons"]
    rows = []
    for arm in ARMS:
        cell = run.cell(arm, "R1", .2)
        comp = paired.get(arm) or desc.get(arm)
        if arm == "f5-r2":
            test = "—"
        elif arm in paired:
            test = f"F5 wins {comp['wins']}, losses {comp['losses']}, ties {comp['ties']}; Holm p = {comp['holm_adjusted_p']:.2g}"
        else:
            test = f"F5 wins {comp['wins']}, losses {comp['losses']}, ties {comp['ties']}; descriptive, outside Holm"
        role = "primary" if arm == "f5-r2" else ("B candidate" if arm in run.config["decision_external_arms"] else ("Holm comparator" if arm in run.config["holm_arms"] else "descriptive"))
        rows.append((LABEL[arm], role, endpoint(arm), frac(cell["positive_sources"], 60), frac(cell["observed_positive_calls"], cell["planned_calls"]),
                     cell["missing_calls"], cp(cell), test))
    neg = run.metrics["primary_negatives"]
    scope = run.config["primary"].get("negative_scope", "R1 .2")
    negative = (f"F5 R1 negatives (endpoint A, every call; scope: {scope}): C0 {neg['f5-r2/C0']['positives']}/{neg['f5-r2/C0']['observed']} observed of {neg['f5-r2/C0']['planned']}, "
                f"wrong owner {neg['f5-r2/wrong_owner']['positives']}/{neg['f5-r2/wrong_owner']['observed']} of {neg['f5-r2/wrong_owner']['planned']}; unresolved {d['unresolved_negatives']}.")
    rule = (f"Rule (BRIEF section 3): TRANSFERS needs F5 ≥ {d['transfer_cut']} and zero F5 false detections; FAILS is F5 < {d['fail_below']:g}. "
            f"B = max(WAM, VINE-R) = {d['best_external']}, margin {d['margin']}. **Decision: {d['label']}, {d['route']}.**")
    if run.union:
        rule += " The label was fixed by stage 2a; the stage-2b analysis reproduces it from the inherited rows, and stage 2b is descriptive."
    return "\n\n".join(["### Table 2. Primary decision cell (R1 SDXL img2img, strength .2)",
                        table(["Arm", "Role", "Endpoint", "Sources k/60", "Outputs k/180", "Missing calls", "CP95 (sources)", "Paired vs F5 (exact sign test)"], rows),
                        negative, rule,
                        "Intervals are model-based and exploratory, assuming independent exchangeable sources in a development convenience cohort."])


def table3(run):
    missing = run.not_run()
    internal_rows = []
    for arm in INTERNAL:
        for ch, st in run.cells_run:
            if ch != "clean" and arm not in run.channel_arms(ch, st):
                continue
            internal_rows.append([LABEL[arm], cell_label(ch, st)] + [cell_text(run.cell(arm, ch, st, p)) for p in ("S", "C", "Q", "J", "A")]
                                 + [run.cell(arm, ch, st, "C")["missing_calls"]])
        if missing:
            internal_rows.append([LABEL[arm], "; ".join(missing), NOT_RUN, "", "", "", "", ""])
    external_rows = []
    for arm in EXTERNAL:
        for ch, st in run.cells_run:
            if ch != "clean" and arm not in run.channel_arms(ch, st):
                continue
            cell, ext = run.cell(arm, ch, st), run.ext(arm, ch, st)
            ops = ext["source_operating_points"]
            exact = f"{ops['exact_message']['positive_sources']}/60 · {ext['exact_message']}/{ext['planned']}"
            native = "—"
            if "native_mask_presence" in ops:
                native = f"mask {ops['native_mask_presence']['positive_sources']}/60 · {ext['native_mask_present']}/{ext['planned']}"
            elif "native_bch_detected" in ops:
                native = f"BCH {ops['native_bch_detected']['positive_sources']}/60"
            ba = ext["bit_accuracy"]
            bits = "no decoded bits" if not ba.get("observed") else f"{ba['median']:.3f} [{ba['q1']:.3f}, {ba['q3']:.3f}] ({ba['observed']}/{ext['planned']})"
            empty = ext.get("empty_mask_abstentions", 0)
            external_rows.append((LABEL[arm], cell_label(ch, st), cell_text(cell), exact, native, bits, empty, cell["missing_calls"]))
        if missing and arm in ("wam", "vine-r"):
            external_rows.append((LABEL[arm], "; ".join(missing), NOT_RUN, "", "", "", "", ""))
    return "\n\n".join([
        "### Table 3. Full endpoint grid",
        "Each entry gives source majority k/60 (at least 2 of seeds 12, 13 and 14; deterministic channels have one output per source) · per-output k/planned. Missing or safety-blocked positives count as failures. TrustMark Q and Pixel Seal are read only in their approved cells (R1 .2; TrustMark also D1).",
        "**3a. Image-domain arms** (predicates of `m1b_e3_s1_analysis`: S semantic found and content match; C semantic read and content match; Q exact q; J Q and content match; A either tier found).",
        table(["Arm", "Channel", "S", "C", "Q", "J", "A", "Missing calls"], internal_rows),
        "**3b. External arms.** Common = known-message presence; for TrustMark it also requires the native BCH flag. Bit accuracy: median [Q1, Q3] (decoded calls/planned). Abstentions are calls with no decoded message: an empty WAM mask, or a failed TrustMark BCH decode.",
        table(["Arm", "Channel", "Common", "Exact message", "Native", "Bit accuracy", "Abstentions", "Missing calls"], external_rows),
    ])


def table4(run):
    rows = []
    for arm in ["unmarked", *ARMS]:
        for ch, st in run.cells_run:
            q = run.quality(arm, ch, st)
            if q is None:
                continue
            strict = ""
            if ch == "clean":
                s = q.get("strict_quality") or {}
                strict = f"{s.get('pass_count', 'NA')}/{s.get('planned', 60)}" if s else ""
                kind = "embedding (mark vs source)"
                block = q["distortion"]
                rows.append((LABEL[arm], ch, kind, metric_summary(block, "psnr_db"), metric_summary(block, "ssim_rgb"), metric_summary(block, "lpips"), strict))
                continue
            kinds = [("attack (output vs its input)", "distortion"), ("total (output vs source)", "total_distortion")]
            if ch == "R1-rinse":
                kinds = [("attack (second-pass output vs the original mark)", "distortion"), ("total (output vs source)", "total_distortion"),
                         ("incremental (second pass vs first pass)", "incremental_distortion")]
            for kind, key in kinds:
                block = q.get(key)
                rows.append((LABEL[arm], cell_label(ch, st), kind, metric_summary(block, "psnr_db"), metric_summary(block, "ssim_rgb"), metric_summary(block, "lpips"), strict))
    return "\n\n".join([
        "### Table 4. Quality",
        "Each value is the median [Q1, Q3] over complete sources (observed/planned sources). Stochastic cells use each source's median over its three seeds. Strict clean gate: PSNR > 35 dB, SSIM > .9 and LPIPS < .1. Human ratings are missing. C0 clean is the source itself (infinite PSNR). R1-smooth and R1-mode take the mark as their input, so their attack distortion includes the smoothing or posterior-mode step.",
        table(["Arm", "Channel", "Distortion", "PSNR dB", "SSIM", "LPIPS", "Strict gate"], rows),
    ])


def table5(run):
    neg = run.rep["negatives"]
    rows = []
    for key, v in neg.items():
        parts = key.split("/")
        arm, ch, st, control, pred = parts[0], parts[1], parts[2], parts[3], parts[4]
        if arm in INTERNAL and pred not in ("A", "C"):
            continue
        where = "clean" if ch == "clean" else cell_label(ch, None if st == "None" else float(st))
        rows.append((LABEL.get(arm, arm), where, control, pred, f"{v['positives']}/{v['observed']} of {v['planned']}",
                     v["unresolved"], f"{v['source_any_positive']}/{v['planned_sources']}"))
    wrong = []
    for arm in EXTERNAL:
        for ch, st in run.cells_run:
            ext = run.ext(arm, ch, st)
            if ext is None:
                continue
            wrong.append((LABEL[arm], cell_label(ch, st), f"{ext['independent_wrong_message_present']}/{ext['planned']}", f"{ext['wrong_message_complement_present']}/{ext['planned']}"))
    roc_rows = []
    for key, v in run.rep["empirical_roc"].items():
        arm, ch, st, kind, view = key.split("/")
        where = "clean" if ch == "clean" else cell_label(ch, None if st == "None" else float(st))
        if "strict_fpr_targets" not in v:
            roc_rows.append((LABEL[arm], where, kind, view, "both", f"not estimable: {v['unresolved']} unresolved C0 negatives (safety blocks)", "", "", ""))
            continue
        for target, point in v["strict_fpr_targets"].items():
            if point is None:
                roc_rows.append((LABEL[arm], where, kind, view, f"FPR < {target}", "not estimable", "", "", ""))
                continue
            thr = "reject all" if point.get("threshold") is None else fmt(point["threshold"], 4)
            roc_rows.append((LABEL[arm], where, kind, view, f"FPR < {target}", thr, f"{point['tp']}/{v['positive_planned']}",
                             f"{point['fp']}/{v['negative_planned']}", f"1/{v['negative_planned']}"))
    return "\n\n".join([
        "### Table 5. Negatives and empirical ROC",
        "**5a. Fixed-operating-point negatives.** C0 = unmarked image read with the arm's detector; wrong owner = marked image read with owner beta (image-domain arms). Image-domain arms: endpoints A (the negative-gate endpoint) and C. Counts are per call; source-any counts a source with any positive call.",
        table(["Arm", "Channel", "Control", "Endpoint", "Positives/observed of planned", "Unresolved", "Source-any positive"], rows),
        "**5b. Wrong-message presence** (marked outputs read with an independent wrong message or its bitwise complement; denominators are planned calls, and safety blocks at R0 leave fewer observed).",
        table(["Arm", "Channel", "Independent wrong message (of planned)", "Complement (of planned)"], wrong),
        "**5c. Outcome-selected empirical ROC (descriptive only; not a calibration).** Score ≥ cutoff; among cutoffs whose empirical FPR is strictly below the target, the one with maximum TPR, then fewest false positives, then highest cutoff. Resolution is one negative. At 60 sources a zero-of-60 count has a one-sided 95% upper limit of about .049, far above .001.",
        table(["Arm", "Channel", "Score", "View", "Target", "Cutoff", "TP/positives", "FP/negatives", "Resolution"], roc_rows),
    ])


def strength_note(run):
    if all(run.ran(ch, s) for ch in ("R0", "R1") for s in STRENGTHS):
        return ("Each side's candidate strengths are .1, .2 and .4 (all run; TrustMark Q and Pixel Seal: .2 only), "
                "so a selected pair may join different strengths.")
    return "Stage 2a has one strength per channel (.2), so every selected pair is .2/.2."


def table6(run):
    rows = []
    for comp, bins in run.rep["matched_distortion"].items():
        for b in bins:
            lo, hi = b["lpips_bin"]
            am, em = b["attack_match"], b["embedding_and_attack_match"]
            pairs = Counter(f"{sfmt(p['left_strength'])}/{sfmt(p['right_strength'])}" for p in b["selected_pairs"])
            deltas = {k: statistics.median(abs(p["delta"][k]) for p in b["selected_pairs"]) for k in ("psnr_db", "ssim_rgb", "lpips")} if b["selected_pairs"] else None
            status = {"no_matched_overlap": "no matched overlap; not estimable", "descriptive_subset": "descriptive", "sparse_descriptive": "sparse; descriptive counts only", "sparse_descriptive_subset": "sparse (m < 20); descriptive counts only"}.get(am["status"], am["status"])
            diff = "—" if am["paired_difference"] is None else f"{am['paired_difference']:+.2f}"
            rows.append((comp, f"[{lo:g}, {'∞' if hi is None else f'{hi:g}'})", f"{am['n']}/60", f"{am['left']}/{am['n']}" if am["n"] else "—",
                         f"{am['right']}/{am['n']}" if am["n"] else "—", diff, f"{am['wins']}/{am['losses']}", status,
                         ", ".join(f"{k} ×{v}" for k, v in sorted(pairs.items())) or "—",
                         "—" if deltas is None else f"{deltas['psnr_db']:.2f} / {deltas['ssim_rgb']:.3f} / {deltas['lpips']:.3f}",
                         f"{em['n']}/60"))
    return "\n\n".join([
        "### Table 6. Finite-grid approximate matching on attack distortion",
        "Within source, fixed LPIPS bins, calipers |ΔLPIPS| ≤ .02, |ΔPSNR| ≤ 1 dB and |ΔSSIM| ≤ .02, at most one pair per source and bin, chosen blind to detection. "
        + strength_note(run) + " Left and right are source-majority successes of the two sides. Discordant counts are left-only/right-only. The last column is the stricter subset that also matches native embedding quality (≤ 1 dB, .01 SSIM, .01 LPIPS). No inferential tests. The rinse, P5 and R3 cells are outside this grid by design (T7).",
        table(["Comparison (left vs right)", "LPIPS bin", "Matched m", "Left success", "Right success", "(L−R)/m", "Discordant L/R", "Status", "Strength pairs", "Median |Δ| PSNR/SSIM/LPIPS", "Embedding-qualified m"], rows),
    ])


def driver_events(text):
    events = []
    for line in text.splitlines():
        m = re.match(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (.*)$", line)
        if m:
            events.append((m.group(1), m.group(2)))
    return events


def stage_lines(stage):
    rec, prov = stage.record, PROVENANCE[stage.tag]
    budget = rec.get("budget") or stage.smoke_timing["budget"]
    name = "Stage 2a" if stage.tag == "stage2a" else "Stage 2b"
    projection = rec["projection"]
    dropped = ", ".join(projection.get("dropped") or []) or "nothing dropped"
    clock = (f"budget clock at the end of the run {budget['instance_seconds'] / 3600:.1f} h, USD {budget['projected_charged_usd']:.2f} at USD {budget['hourly_usd']}/h, counted {prov['clock']}; limits {budget['max_instance_hours']} h / USD {budget['max_usd']}"
             if rec.get("budget") else
             f"budget clock {prov['clock']}; limits {budget['max_instance_hours']} h / USD {budget['max_usd']} (the remainder of the 35 h / USD 30 ceiling after the conservative stage-2a clock); compute deadline {budget['compute_deadline_utc'][:16]}Z")
    return (f"{name}: {rec['gpu']} (vast.ai container {prov['container']}), run commit server {rec['commit'][:7]} (blob-identical to laptop {prov['laptop']}); "
            f"full run {rec['created_utc'][:19]}Z, {rec['duration_seconds'] / 3600:.2f} h; smoke {stage.smoke['duration_seconds'] / 60:.1f} min of compute; "
            f"projection {stage.smoke_timing['projected_full_seconds'] / 3600:.2f} h against {projection['available_seconds'] / 3600:.2f} h available, {dropped}; {clock}.")


def table7(run):
    gen = defaultdict(list)
    det = defaultdict(list)
    for row in run.rows.values():
        if row.get("status") != "ok":
            continue
        key = row["arm"] if row["channel"] == "clean" else (row["channel"], row.get("strength"))
        gen[key].append(row.get("generation_seconds") or 0)
        for method, seconds in (row.get("detection_seconds") or {}).items():
            det[method].append(seconds)
    embed_rows = [(LABEL[a], len(gen[a]), f"{statistics.median(gen[a]):.2f}", f"{sum(gen[a]) / 3600:.2f}") for a in ["unmarked", *ARMS] if gen[a]]
    channel_rows = [(cell_label(c, s), len(gen[(c, s)]), f"{statistics.median(gen[(c, s)]):.2f}", f"{sum(gen[(c, s)]) / 3600:.2f}") for c, s in run.cells_run[1:] if gen[(c, s)]]
    detect_rows = [(LABEL[a], len(det[a]), f"{statistics.median(det[a]):.3f}", f"{sum(det[a]) / 3600:.2f}") for a in ARMS if det[a]]
    multi = len(run.stages) > 1
    memory_rows, events = [], []
    for stage in run.stages:
        tag = stage.tag.replace("stage", "")
        memory_rows += [((tag + " ") * multi + m["phase"], m["started_utc"][11:19], f"{m['peak_allocated_bytes'] / 2**30:.2f}") for m in stage.memory]
        events += [(t, (tag + ": ") * multi + e.replace("|", "\\|")) for t, e in driver_events(stage.driver_log)]
    env = run.record["environment"]
    pins = ", ".join(f"{k} {v}" for k, v in env.items() if k in ("torch", "torchvision", "diffusers", "transformers", "numpy", "Pillow", "lpips", "av", "lightning", "torchmetrics", "sentencepiece", "protobuf"))
    if run.union and run.prior is None:
        provenance = [stage_lines(run.stage), "Stage-2a provenance: pass --prior-run."]
    else:
        provenance = [stage_lines(s) for s in run.stages]
    timing_note = ("Timings come from the persisted rows; inherited stage-2a rows keep their stage-2a timings." if run.union else "")
    return "\n\n".join([
        "### Table 7. Cost and provenance",
        f"Python 3.11.17. Pins: {pins}; full list in `run.json`. Precision: SD1.5 and SDXL UNets in fp16, SDXL VAE in full fp32, MoVQ in fp32; Kandinsky 3 UNet and MoVQ in its fp16 variant.",
        *provenance,
        "The billed amounts are on the vast.ai invoice." + (" " + timing_note if timing_note else ""),
        "**7a. Embedding (clean units)**", table(["Arm", "Units", "Median s/unit", "Total h"], embed_rows),
        "**7b. Channel regeneration (all arms and C0)**", table(["Channel", "Units", "Median s/unit", "Total h"], channel_rows),
        "**7c. Extraction (all calls by detector, both owners where applicable)**", table(["Detector", "Calls", "Median s/call", "Total h"], detect_rows),
        "**7d. Peak CUDA allocation by phase**", table(["Phase", "Started (UTC)", "Peak GiB"], memory_rows),
        "**7e. Driver events, attempts and retries**", table(["UTC", "Event"], events),
    ])


def table8(run):
    rows = [(r, enc, LABEL[a], frac(k, n), "step 1 (24 sources, `unseen-regenerator-results.md`)") for r, enc, a, k, n in STEP1]
    selection = read(ROOT / "research/journal-upgrade-20261009/fresh-development-selection.json")
    entries = next(selection[k] for k in ("sources", "selection", "selected") if k in selection)
    step1 = {s["source_id"] if isinstance(s, dict) else s for s in entries}
    for ch, name, enc in (("R0", "SD1.5 img2img .2", "SD1.x"), ("R1", "SDXL img2img .2", "independent SDXL encoder"),
                          ("R3", "Kandinsky 3 img2img .2", "Kandinsky 3 MoVQ (independence qualified)")):
        if not run.ran(ch, .2):
            continue
        for arm in INTERNAL:
            seeds = defaultdict(int)
            for row in run.unit_rows(arm, ch, .2):
                ep = ((row.get("detections") or {}).get(arm, {}).get(ALPHA) or {}).get("endpoints") or {}
                if row.get("status") == "ok" and ep.get("C"):
                    seeds[row["source_id"]] += 1
            overlap = sum(1 for s in step1 if seeds[s] >= 2)
            rest = sum(1 for s in seeds if s not in step1 and seeds[s] >= 2)
            total = run.cell(arm, ch, .2, "C")["positive_sources"]
            rows.append((name, enc, LABEL[arm], frac(total, 60), f"this study: step-1 sources {overlap}/24, new sources {rest}/36"))
    return "\n\n".join([
        "### Table 8. Historical context (source-majority C at strength .2)",
        "Step 1 used 24 development sources, all of which are among this study's 60; on them, R0 reproduces step 1 exactly. Do not pool the 24-source SD2.1 cell with the 60-source SDXL or Kandinsky 3 cells, and do not attribute the difference to the encoder alone: R1 and R3 also change the model family, resolution and pipeline.",
        table(["Regenerator", "Encoder family", "Arm", "C", "Cohort"], rows),
    ])


# ---------------------------------------------------------------- figures

def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "legend.fontsize": 7.5,
                         "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200,
                         "font.family": "DejaVu Sans", "pdf.fonttype": 42})
    return plt


def save(fig, out, name):
    fig.savefig(out / f"{name}.png", bbox_inches="tight")
    # No creation date, so that rerunning on the same outputs gives identical files.
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})


def errorbar_cell(ax, x, cell, arm, ms=5, **kw):
    p, (lo, hi) = cell["positive_sources"] / 60, cell["cp95"]
    ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], fmt=MARKER[arm], color=COLOR[arm], ms=ms, capsize=2, lw=1, **kw)
    return p


def figure1(run, plt, out):
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.6), gridspec_kw={"width_ratios": [1, 1, 1.3, 1.5]})
    offsets = {a: (i - 2.5) * .012 for i, a in enumerate(ARMS)}
    for ax, ch in zip(axes[:2], ("R0", "R1")):
        for x in STRENGTHS:
            if not run.ran(ch, x):
                ax.axvspan(x - .05, x + .05, color="#eeeeee", zorder=0)
                ax.text(x, .5, NOT_RUN.replace(" (", "\n("), ha="center", va="center", fontsize=6.5, color="#777777", rotation=90)
        for arm in ARMS:
            xs, ys = [], []
            for s in STRENGTHS:
                if run.ran(ch, s) and arm in run.channel_arms(ch, s):
                    xs.append(s + offsets[arm])
                    ys.append(errorbar_cell(ax, s + offsets[arm], run.cell(arm, ch, s), arm))
            if len(xs) > 1:
                ax.plot(xs, ys, color=COLOR[arm], lw=.7, alpha=.7)
        if ch == "R1":
            ax.annotate("primary cell\n(F5 C, R1 .2)", xy=(.2 + offsets["f5-r2"], 0), xytext=(.25, .3), fontsize=7,
                        arrowprops=dict(arrowstyle="->", lw=.7, color="#333333"))
        ax.set_xlim(.03, .47)
        ax.set_xticks(STRENGTHS)
        ax.set_ylim(-.04, 1.04)
        ax.set_xlabel("img2img strength")
        ax.set_title(CHANNEL_LABEL[ch] + " img2img")
    axes[0].set_ylabel("source-majority success rate (k/60)")
    ax = axes[2]
    for arm in ARMS:
        for i, ch in enumerate(DIAG):
            if ch != "clean" and arm not in run.channel_arms(ch):
                continue
            errorbar_cell(ax, i + offsets[arm] * 8, run.cell(arm, ch), arm, ms=4.5, ls="none")
    ax.set_xticks(range(len(DIAG)))
    ax.set_xticklabels([CHANNEL_LABEL[c] for c in DIAG], rotation=20, ha="right")
    ax.set_ylim(-.04, 1.04)
    ax.set_title("Deterministic controls (one output per source)")
    ax = axes[3]
    for i, (ch, st) in enumerate(VARIANTS):
        if not run.ran(ch, st):
            ax.text(i, .5, "not run", ha="center", va="center", fontsize=6.5, color="#777777", rotation=90)
            continue
        for arm in run.channel_arms(ch, st):
            errorbar_cell(ax, i + offsets[arm] * 8, run.cell(arm, ch, st), arm, ms=4.5, ls="none")
    ax.set_xticks(range(len(VARIANTS)))
    ax.set_xticklabels([cell_label(c, s) for c, s in VARIANTS], rotation=25, ha="right")
    ax.set_ylim(-.04, 1.04)
    ax.set_title("Rinse, P5 smoothing and control, full Kandinsky 3")
    handles = [plt.Line2D([], [], marker=MARKER[a], color=COLOR[a], ls="none", label=f"{LABEL[a]} ({endpoint(a)})") for a in ARMS]
    fig.suptitle(f"Figure 1. Source-majority success with 95% Clopper-Pearson bars, n = 60 development sources, {run.scope}; "
                 "thin segments join measured strengths only", fontsize=9, y=1.03)
    fig.tight_layout()
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, bbox_to_anchor=(.5, -.1))
    save(fig, out, "fig1-success-by-strength")
    plt.close(fig)


def figure2(run, plt, out):
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6), sharey=True)
    counts = defaultdict(set)
    for ax, (metric, label) in zip(axes, (("psnr_db", "attack PSNR dB (output vs its input)"), ("ssim_rgb", "attack SSIM"), ("lpips", "attack LPIPS"))):
        for arm in ARMS:
            for ch in ("R0", "R1"):
                xs, ys = [], []
                for s in STRENGTHS:
                    if not run.ran(ch, s) or arm not in run.channel_arms(ch, s):
                        continue
                    q = run.quality(arm, ch, s)["distortion"][metric]["complete_source_medians"]
                    y = run.cell(arm, ch, s)["positive_sources"] / 60
                    ax.plot(q["median"], y, MARKER[arm], color=COLOR[arm], ms=5, mfc=COLOR[arm] if ch == "R1" else "white", mew=1.2)
                    ax.annotate(sfmt(s), (q["median"], y), xytext=(3, 2), textcoords="offset points", fontsize=5, color="#555555")
                    xs.append(q["median"])
                    ys.append(y)
                    counts[(ch, s)].add(q["observed"])
                if len(xs) > 1:
                    ax.plot(xs, ys, color=COLOR[arm], lw=.6, alpha=.6, ls="-" if ch == "R1" else ":")
        ax.set_xlabel(label)
    axes[0].set_ylabel("source-majority success rate (k/60)")
    handles = [plt.Line2D([], [], marker=MARKER[a], color=COLOR[a], ls="none", label=LABEL[a]) for a in ARMS]
    handles += [plt.Line2D([], [], marker="o", color="#555555", mfc="white", ls=":", label="R0 SD1.5 (open, dotted)"),
                plt.Line2D([], [], marker="o", color="#555555", ls="-", label="R1 SDXL (filled, solid)")]
    axes[2].legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, .5), frameon=False)
    span = lambda s: f"{min(s)}–{max(s)}" if len(s) > 1 else f"{min(s)}"
    observed = "; ".join(f"{cell_label(c, s)} {span(v)}/60" for (c, s), v in sorted(counts.items(), key=lambda kv: (kv[0][0], kv[0][1])))
    fig.text(.5, -.07, f"Point labels give the strength. Quality sources with three complete seeds: {observed}. "
             "Success counts all 60 sources (blocked = failure).", ha="center", fontsize=6.5, color="#444444", wrap=True)
    fig.suptitle("Figure 2. Robustness against achieved attack distortion (median over sources of within-source seed medians); segments join measured strengths, no interpolation", fontsize=9, y=1.03)
    fig.tight_layout()
    save(fig, out, "fig2-robustness-vs-distortion")
    plt.close(fig)


def figure3(run, plt, out):
    import numpy as np
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    rng = np.random.default_rng(20261024)
    for ax, (metric, label, ref) in zip(axes, (("psnr_db", "PSNR dB (mark vs source)", 35), ("ssim_rgb", "SSIM", .9), ("lpips", "LPIPS", .1))):
        for i, arm in enumerate(ARMS):
            vals = [row["distortion"][metric] for row in run.unit_rows(arm, "clean") if row.get("distortion", {}).get("status") == "ok"]
            x = i + rng.uniform(-.18, .18, len(vals))
            ax.scatter(x, vals, s=6, color=COLOR[arm], alpha=.55, lw=0)
            q1, med, q3 = np.percentile(vals, [25, 50, 75])
            ax.plot([i - .3, i + .3], [med, med], color="black", lw=1.2)
            ax.plot([i, i], [q1, q3], color="black", lw=2.5, alpha=.6)
        ax.axhline(ref, color="#999999", ls="--", lw=.8)
        ax.text(len(ARMS) - .5, ref, "strict gate", fontsize=6, color="#777777", va="bottom", ha="right")
        ax.set_xticks(range(len(ARMS)))
        ax.set_xticklabels([LABEL[a] for a in ARMS], rotation=30, ha="right")
        ax.set_ylabel(label)
    fig.suptitle("Figure 3. Clean native embedding quality, one dot per source (n = 60), median bar and IQR; payloads and endpoints differ (Table 1), so this is no equal-quality claim", fontsize=9, y=1.03)
    fig.tight_layout()
    save(fig, out, "fig3-clean-quality")
    plt.close(fig)


def figure4(run, plt, out):
    comps = list(run.rep["matched_distortion"].keys())
    bins = [tuple(b["lpips_bin"]) for b in run.rep["matched_distortion"][comps[0]]]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for ax, which, title in ((axes[0], "attack_match", "attack-distortion match"), (axes[1], "embedding_and_attack_match", "native embedding + attack approximate match")):
        for j, comp in enumerate(comps):
            for i, b in enumerate(run.rep["matched_distortion"][comp]):
                m = b[which]
                if m["n"] == 0:
                    ax.text(i, j, "0", ha="center", va="center", fontsize=6.5, color="#aaaaaa")
                    continue
                d = m["paired_difference"]
                ax.scatter(i, j + .12, s=12 + 3 * m["n"], color=plt.cm.RdBu((d + 1) / 2), edgecolors="black", lw=.5)
                ax.text(i, j - .3, f"m={m['n']}  {d:+.2f}", fontsize=5.5, ha="center", va="center")
        ax.set_xticks(range(len(bins)))
        ax.set_xticklabels([f"[{lo:g},{'∞' if hi is None else f'{hi:g}'})" for lo, hi in bins], rotation=30, ha="right")
        ax.set_xlabel("attack LPIPS bin")
        ax.set_title(title)
        ax.set_xlim(-.5, len(bins) - .2)
        ax.set_ylim(-.8, len(comps) - .5)
    axes[0].set_yticks(range(len(comps)))
    axes[0].set_yticklabels(comps)
    fig.text(.5, -.03, "Marker area grows with m; colour: blue = left arm succeeds more, red = right arm succeeds more, white = tie. "
             + strength_note(run), ha="center", fontsize=7, color="#444444")
    fig.suptitle("Figure 4. Matched-bin paired difference (left − right successes)/m, with overlap m/60; grey 0 = empty bin, not estimable; no pooled effect, no tests", fontsize=9, y=1.02)
    fig.tight_layout()
    save(fig, out, "fig4-matched-bins")
    plt.close(fig)


def figure5(run, plt, out):
    roc = run.rep["empirical_roc"]
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 6.4), sharex=True, sharey=True)
    styles = {("wam", "agreement"): ("-", "WAM known-message"), ("wam", "mask"): (":", "WAM native mask"),
              ("vine-r", "agreement"): ("-", "VINE-R known-message"), ("trustmark-q", "agreement"): ("--", "TrustMark Q (descriptive)"),
              ("pixelseal", "agreement"): ("-.", "Pixel Seal (descriptive)")}
    for r, ch in enumerate(("R0", "R1")):
        for c, view in enumerate(("outputs", "sources")):
            ax = axes[r, c]
            missing = []
            for (arm, kind), (ls, label) in styles.items():
                v = roc.get(f"{arm}/{ch}/0.2/{kind}/{view}")
                if v is None:
                    continue
                if "points" not in v:
                    missing.append(label)
                    unresolved = v["unresolved"]
                    continue
                if len(v["points"]) == 1:
                    missing.append(f"{label}: no decoded scores (reject-all point only)")
                    continue
                pts = sorted(v["points"], key=lambda p: (p["fpr"], p["tpr"]))
                ax.step([p["fpr"] for p in pts], [p["tpr"] for p in pts], where="post", ls=ls, color=COLOR[arm], lw=1.2, label=label)
            for x in (.001, .01):
                ax.axvline(x, color="#999999", lw=.7, ls="--")
            n = 180 if view == "outputs" else 60
            if missing and ch == "R0":
                ax.text(.5, .5, f"not estimable: {unresolved} unresolved C0 negatives\n(R0 safety blocks)\n\n" + "\n".join(missing),
                        transform=ax.transAxes, fontsize=7, color="#aa3333", ha="center", va="center")
            elif missing:
                ax.text(.98, .42, "\n".join(missing), transform=ax.transAxes, fontsize=6.5, color="#aa3333", ha="right")
            ax.set_xscale("symlog", linthresh=1e-3)
            ax.set_xlim(0, 1)
            ax.set_ylim(-.02, 1.02)
            ax.set_title(f"{cell_label(ch, .2)}, {'output-level, 180/180' if view == 'outputs' else 'source-median, 60/60'}; resolution 1/{n}")
            if r == 1:
                ax.set_xlabel("empirical FPR on C0 (symlog; dashed .001 and .01)")
            if c == 0:
                ax.set_ylabel("empirical TPR")
    fig.legend(*axes[1, 1].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, -.04))
    other = " Every other cell's ROC summary is in Table 5c." if run.union else ""
    fig.suptitle("Figure 5. Outcome-selected empirical ROC of external score kinds at R0/R1 .2 (descriptive only, not a calibration). F5 has no continuous surrogate; its fixed point is in Table 2." + other, fontsize=9, y=1.01, wrap=True)
    fig.tight_layout()
    save(fig, out, "fig5-empirical-roc")
    plt.close(fig)


def figure6(run, plt, out):
    groups = [(c, None) for c in DIAG] + [("R1", .1), ("R1-rinse", .1)]
    arms = [a for a in ARMS if a != "pixelseal"]
    fig, ax = plt.subplots(figsize=(10.5, 3.6))
    width = .12
    for i, arm in enumerate(arms):
        for j, (ch, st) in enumerate(groups):
            if not run.ran(ch, st) or (ch != "clean" and arm not in run.channel_arms(ch, st)):
                continue
            cell = run.cell(arm, ch, st)
            x = i + (j - (len(groups) - 1) / 2) * width
            hatch = "///" if ch == "R1-rinse" else None
            ax.bar(x, cell["positive_sources"], width * .92, color=COLOR[arm], alpha=.3 + .1 * j, edgecolor="black", lw=.3, hatch=hatch)
            q = run.quality(arm, ch, st)["distortion"]["lpips"]["complete_source_medians"]
            label = f"{cell['positive_sources']}" + ("" if ch == "clean" else f"\n{q['median']:.3f}")
            ax.text(x, cell["positive_sources"] + 1, label, ha="center", va="bottom", fontsize=4.8)
    ax.set_xticks(range(len(arms)))
    ax.set_xticklabels([LABEL[a] for a in arms])
    ax.set_ylim(0, 70)
    ax.set_ylabel("sources k/60 (fixed endpoint)")
    rinse = ("R1 .1 is the rinse's parent (first pass); the hatched rinse bar is its second .1 pass, with LPIPS against the original mark. "
             if run.ran("R1-rinse", .1) else f"R1 rinse: {NOT_RUN}. ")
    fig.text(.5, -.05, "Bars per arm, left to right: clean, X1, X2, D1, D3, R1 .1, R1 rinse (gaps are out of scope). Label: k, then the median attack LPIPS. "
             + rinse + "Pixel Seal is clean and R1 .2 only.", ha="center", fontsize=6.5, color="#444444", wrap=True)
    fig.suptitle("Figure 6. Deterministic controls and the rinse against their parents (controls: one output per source; R1 .1 and rinse: source majority of three seeds)", fontsize=9, y=1.02)
    fig.tight_layout()
    save(fig, out, "fig6-controls")
    plt.close(fig)


def figure7(run, out, tiles_out=None, tile=144):
    import numpy as np
    from PIL import Image, ImageDraw
    first_six = [s["source_id"] for s in run.sources[:6]]
    arms = ["unmarked", *ARMS]
    # ASCII only: PIL's default bitmap font has no minus or multiplication sign.
    cols = ["clean mark", "|mark - source| x10", "R0 SD1.5 .2 s12", "R1 SDXL .2 s12", "R1 .1 s12", "rinse .1+.1 s12,112"]
    col_cells = [None, None, ("R0", .2), ("R1", .2), ("R1", .1), ("R1-rinse", .1)]

    def load(unit_id):
        row = run.rows.get(unit_id)
        if not row or row.get("status") != "ok" or not row.get("output"):
            return None
        path = run.image(row)
        return None if path is None else Image.open(path).convert("RGB")

    for scale_name, size, dest in (("preview", tile, out), ("full", 512, tiles_out)):
        if dest is None:
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for sid in first_six:
            label_w, head_h = 92, 30
            canvas = Image.new("RGB", (label_w + len(cols) * size, head_h + len(arms) * size), "white")
            draw = ImageDraw.Draw(canvas)
            for j, col in enumerate(cols):
                draw.text((label_w + j * size + 4, 8), col, fill="black")
            source = load(f"clean:{sid}:unmarked:None:None")
            for i, arm in enumerate(arms):
                draw.text((4, head_h + i * size + size // 2 - 6), LABEL[arm], fill="black")
                mark = load(f"clean:{sid}:{arm}:None:None")
                residual = None
                if mark is not None and source is not None:
                    diff = np.abs(np.asarray(mark, dtype=np.int16) - np.asarray(source, dtype=np.int16)) * 10
                    residual = Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8))
                tiles = [mark, residual] + [load(f"{ch}:{sid}:{arm}:{st}:12") for ch, st in col_cells[2:]]
                for j, img in enumerate(tiles):
                    x0, y0 = label_w + j * size, head_h + i * size
                    if img is None:
                        draw.rectangle([x0 + 1, y0 + 1, x0 + size - 2, y0 + size - 2], outline="#bbbbbb")
                        reason = "blocked/missing"
                        if j >= 2:
                            ch, st = col_cells[j]
                            reason = "not run" if not run.ran(ch, st) else ("not in scope" if arm != "unmarked" and arm not in run.channel_arms(ch, st) else reason)
                        draw.text((x0 + 8, y0 + size // 2 - 6), reason, fill="#888888")
                        continue
                    canvas.paste(img.resize((size, size), Image.LANCZOS), (x0, y0))
            canvas.save(dest / f"fig7-source-{sid}-{scale_name}.png", optimize=True)
    return first_six


def figure_a1(run, plt, out):
    cells = run.cells_run
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.6), sharex=True)
    for ax, (arm, tier, title) in zip(axes, (("f5-r2", "semantic", "F5 semantic tier"), ("f5-r2", "instance", "F5 instance tier"), ("v5-r3", "semantic", "v5 semantic tier"))):
        for i, (ch, st) in enumerate(cells):
            for who, color, dx in ((arm, COLOR[arm], -.17), ("unmarked", COLOR["unmarked"], .17)):
                if who == "unmarked" and ch == "clean":
                    continue
                vals = []
                for row in run.unit_rows(who, ch, st):
                    raw = (((row.get("detections") or {}).get(arm) or {}).get(ALPHA) or {}).get("raw") or {}
                    t = raw.get(tier) or {}
                    if row.get("status") == "ok" and t.get("threshold"):
                        vals.append(t["score"] / t["threshold"])
                if not vals:
                    continue
                parts = ax.violinplot([vals], positions=[i + dx], widths=.3, showmedians=True)
                for body in parts["bodies"]:
                    body.set_facecolor(color)
                    body.set_alpha(.5)
                for key in ("cbars", "cmins", "cmaxes", "cmedians"):
                    parts[key].set_color(color)
                    parts[key].set_linewidth(.7)
        ax.axhline(1, color="black", lw=.7, ls="--")
        ax.set_ylabel("score / threshold")
        ax.set_title(title, loc="left")
    axes[-1].set_xticks(range(len(cells)))
    axes[-1].set_xticklabels([cell_label(c, s) for c, s in cells], rotation=35, ha="right")
    fig.text(.5, -.03, "Coloured: the arm's own marked outputs; grey: C0 (unmarked) outputs of the same cell, read with the same detector and owner alpha; 1 = threshold. "
             "Stochastic cells pool three seeds.", ha="center", fontsize=7, color="#444444")
    fig.suptitle("Figure A1 (post-hoc, descriptive). Detector margin by cell; not used to choose any setting", fontsize=9, y=1.0)
    fig.tight_layout()
    save(fig, out, "figA1-signal-margins")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True, help="dev-run results folder holding <stage>-full and <stage>-smoke")
    parser.add_argument("--prior-run", type=Path, help="stage-2a dev-run results folder (inherited images and provenance)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-tiles", type=Path, help="optional folder for full-resolution Figure 7 panels")
    args = parser.parse_args()
    run = Run(args.run, args.prior_run)
    figures = args.out / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt = setup_matplotlib()
    figure1(run, plt, figures)
    figure2(run, plt, figures)
    figure3(run, plt, figures)
    figure4(run, plt, figures)
    figure5(run, plt, figures)
    figure6(run, plt, figures)
    figure_a1(run, plt, figures)
    first_six = figure7(run, figures, args.full_tiles)
    if run.union:
        title = "# Encoder-transfer stages 2a and 2b (union): T7 tables and figures"
        origin = (f"Generated by `scripts/encoder_transfer_report.py` from the saved stage-2b outputs, whose journal holds every stage-2a row "
                  f"(stage-2b run commit {run.record['commit'][:7]}, contract sha {run.record['manifest_sha256'][:8]}…; stage-2a contract sha 87e4142f…). ")
        fig1 = "Source-majority success with CP95 bars at R0/R1 .1/.2/.4, the deterministic controls, and the rinse, P5 and R3 cells"
        fig7 = f"Fixed illustration: the first six sources of the frozen list ({', '.join(str(s) for s in first_six)}), all arms, seed 12 for R0/R1 .2 and the prescribed rinse pair (R1 .1 seed 12, rinse seeds 12 and 112)"
    else:
        title = "# Encoder-transfer stage 2a: T7 tables and figures"
        origin = (f"Generated by `scripts/encoder_transfer_report.py` from the saved stage-2a outputs (run commit "
                  f"{run.record['commit'][:7]}, contract sha {run.record['manifest_sha256'][:8]}…). ")
        fig1 = "Source-majority success with CP95 bars at R0/R1 .2 and the deterministic controls; .1 and .4 not run by design"
        fig7 = f"Fixed illustration: the first six sources of the frozen list ({', '.join(str(s) for s in first_six)}), all arms, seed 12; the rinse pair is {NOT_RUN}"
    header = [title,
              "",
              origin + "Every count is read from `metrics.json` or from the persisted per-call results in `rows.jsonl`; nothing is recomputed from images. "
              "Development evidence on 60 sources; exploratory throughout.",
              "",
              "## Figures",
              "",
              "| Figure | File | Content |",
              "|---|---|---|",
              f"| 1 | `figures/fig1-success-by-strength.png` | {fig1} |",
              "| 2 | `figures/fig2-robustness-vs-distortion.png` | Success rate against achieved attack PSNR, SSIM and LPIPS |",
              "| 3 | `figures/fig3-clean-quality.png` | Clean native quality per source, median and IQR |",
              "| 4 | `figures/fig4-matched-bins.png` | Matched-bin overlap and paired differences, empty bins explicit |",
              "| 5 | `figures/fig5-empirical-roc.png` | Empirical ROC step plots at R0/R1 .2, output and source-median views |",
              "| 6 | `figures/fig6-controls.png` | Clean, resize, SDXL VAE and MoVQ controls, and the rinse against its R1 .1 parent |",
              f"| 7 | `figures/fig7-source-<id>-preview.png` | {fig7}. Full-resolution panels are kept in the run folder |",
              "| A1 | `figures/figA1-signal-margins.png` | Post-hoc detector margins by cell (descriptive) |",
              "",
              "## Tables",
              ""]
    body = "\n\n".join(t(run) for t in (table1, table2, table3, table4, table5, table6, table7, table8))
    with open(args.out / "tables.md", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(header) + body + "\n")
    print(f"wrote {args.out / 'tables.md'} and {len(list(figures.iterdir()))} figure files")


if __name__ == "__main__":
    main()
