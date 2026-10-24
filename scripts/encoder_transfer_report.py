"""Render the binding T7 tables and figures for the encoder-transfer stage-2a run.

Written by Claude (Opus 5.5) on 2026-10-24, after the stage-2a label was fixed. It reads only the
saved run outputs and the frozen contract, and recomputes no endpoint: every count comes from
`metrics.json` or from the persisted per-call results in `rows.jsonl`. The T7 reporting plan is in
research/encoder-transfer-20261019/design-research/T7-fair-reporting/synthesis.md.

Usage (needs matplotlib, numpy and Pillow):
  python scripts/encoder_transfer_report.py --run <dev-run>/results --out research/encoder-transfer-20261019/report
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
CHANNELS = ["clean", "X1", "X2", "D1", "D3", "R0", "R1"]
CHANNEL_LABEL = {"clean": "clean", "X1": "X1 resize x1", "X2": "X2 resize x2", "D1": "D1 SDXL VAE",
                 "D3": "D3 Kandinsky MoVQ", "R0": "R0 SD1.5 .2", "R1": "R1 SDXL .2"}
NOT_RUN = "not run by design (stage 2a result)"
# Step-1 context, copied from research/journal-upgrade-20261009/unseen-regenerator-results.md
# (source-majority endpoints, 24 development sources, seeds 0-2 as defined there).
STEP1 = [("SD1.5 img2img .2", "SD1.x", "f5-r2", 22, 24), ("SD1.5 img2img .2", "SD1.x", "v5-r3", 5, 24),
         ("SD2.1-base img2img .2", "SD1.x (shared encoder)", "f5-r2", 24, 24),
         ("SD2.1-base img2img .2", "SD1.x (shared encoder)", "v5-r3", 5, 24)]


def strength_key(channel):
    return "0.2" if channel in ("R0", "R1") else "None"


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


class Run:
    def __init__(self, results):
        self.dir = Path(results)
        full = self.dir / "stage2a-full"
        self.metrics = read(full / "metrics.json")
        self.record = read(full / "run.json")
        self.config = read(full / "effective-config.json")
        self.memory = read(full / "memory-phases.json")
        self.smoke = read(self.dir / "stage2a-smoke/run.json")
        self.smoke_timing = read(self.dir / "stage2a-smoke/smoke-timing.json")
        self.driver_log = (self.dir / "driver.log").read_text(encoding="utf-8")
        self.rows = {}
        with open(full / "rows.jsonl", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                self.rows[row["id"]] = row
        self.images = full / "images"
        self.cells = self.metrics["cells"]
        self.rep = self.metrics["reporting"]
        self.sources = read(ROOT / self.config["sources_file"])["sources"]

    def channel_arms(self, channel):
        if channel == "clean":
            return list(self.config["arms"])
        spec = next(c for c in self.config["channels"] if c["id"] == channel)
        return list(spec.get("arms", []))

    def cell(self, arm, channel, pred=None):
        return self.cells.get(f"{arm}/{channel}/{strength_key(channel)}/{pred or endpoint(arm)}")

    def ext(self, arm, channel):
        return self.rep["external_operating_points"].get(f"{arm}/{channel}/{strength_key(channel)}")

    def quality(self, arm, channel):
        return self.rep["quality"].get(f"{arm}/{channel}/{strength_key(channel)}")

    def unit_rows(self, arm=None, channel=None):
        for row in self.rows.values():
            if (arm is None or row["arm"] == arm) and (channel is None or row["channel"] == channel):
                yield row


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
    channel_rows = []
    for spec in c["channels"]:
        cid = spec["id"]
        if spec.get("enabled") is False:
            channel_rows.append((cid, spec.get("kind", ""), spec.get("family", ""), "—", "—", "—", "—", "—", f"disabled: {spec.get('reason', '')}"))
            continue
        kind = spec["kind"]
        if kind == "diffusion":
            model = "SD1.5 (451f4fe)" if spec["family"] == "sd15" else "SDXL base 1.0 (4621659)"
            res = f"{spec['resolution']} internal / 512 output"
            steps = f"DDIM {spec['steps']} scheduled × strength .2 = {int(spec['steps'] * .2)} executed"
            prompt = f"empty prompt, CFG {spec['guidance_scale']:g}"
            strengths, seeds = ", ".join(str(s) for s in spec["strengths"]), ", ".join(str(s) for s in spec["seeds"])
        elif kind == "vae":
            model = "SDXL VAE, posterior mode, fp32" if spec["family"] == "sdxl" else "Kandinsky 3 MoVQ (bf79e6c), fp32 from fp16 weights"
            res, steps, prompt, strengths, seeds = f"{spec['resolution']} internal / 512 output", "encode-decode only", "—", "—", "deterministic"
        else:
            model = f"PIL Lanczos 512→1024→512, {spec['passes']} pass(es)"
            res, steps, prompt, strengths, seeds = "1024 internal / 512 output", "—", "—", "—", "deterministic"
        arms_text = ", ".join(LABEL[a] for a in spec["arms"]) + ", C0"
        channel_rows.append((cid, kind, model, res, steps, prompt, strengths, seeds, arms_text))
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
        cell = run.cell(arm, "R1")
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
    negative = (f"F5 R1 .2 negatives (endpoint A, every call, no majority): C0 {neg['f5-r2/C0']['positives']}/{neg['f5-r2/C0']['observed']} observed of {neg['f5-r2/C0']['planned']}, "
                f"wrong owner {neg['f5-r2/wrong_owner']['positives']}/{neg['f5-r2/wrong_owner']['observed']} of {neg['f5-r2/wrong_owner']['planned']}; unresolved {d['unresolved_negatives']}.")
    rule = (f"Rule (BRIEF section 3): TRANSFERS needs F5 ≥ {d['transfer_cut']} and zero F5 false detections; FAILS is F5 < {d['fail_below']:g}. "
            f"B = max(WAM, VINE-R) = {d['best_external']}, margin {d['margin']}. **Decision: {d['label']}, {d['route']}.**")
    return "\n\n".join(["### Table 2. Primary decision cell (R1 SDXL img2img, strength .2)",
                        table(["Arm", "Role", "Endpoint", "Sources k/60", "Outputs k/180", "Missing calls", "CP95 (sources)", "Paired vs F5 (exact sign test)"], rows),
                        negative, rule,
                        "Intervals are model-based and exploratory, assuming independent exchangeable sources in a development convenience cohort."])


def table3(run):
    internal_rows = []
    for arm in INTERNAL:
        for ch in CHANNELS:
            if ch != "clean" and arm not in run.channel_arms(ch):
                continue
            internal_rows.append([LABEL[arm], CHANNEL_LABEL[ch]] + [cell_text(run.cell(arm, ch, p)) for p in ("S", "C", "Q", "J", "A")]
                                 + [run.cell(arm, ch, "C")["missing_calls"]])
        internal_rows.append([LABEL[arm], "R1 rinse; R0/R1 .1 and .4", NOT_RUN, "", "", "", "", ""])
    external_rows = []
    for arm in EXTERNAL:
        for ch in CHANNELS:
            if ch != "clean" and arm not in run.channel_arms(ch):
                continue
            cell, ext = run.cell(arm, ch), run.ext(arm, ch)
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
            external_rows.append((LABEL[arm], CHANNEL_LABEL[ch], cell_text(cell), exact, native, bits, empty, cell["missing_calls"]))
        external_rows.append((LABEL[arm], "R1 rinse; R0/R1 .1 and .4", NOT_RUN, "", "", "", "", ""))
    return "\n\n".join([
        "### Table 3. Full endpoint grid",
        "Each entry gives source majority k/60 (at least 2 of seeds 12, 13 and 14; deterministic channels have one output per source) · per-output k/planned. Missing or safety-blocked positives count as failures.",
        "**3a. Image-domain arms** (predicates of `m1b_e3_s1_analysis`: S semantic found and content match; C semantic read and content match; Q exact q; J Q and content match; A either tier found).",
        table(["Arm", "Channel", "S", "C", "Q", "J", "A", "Missing calls"], internal_rows),
        "**3b. External arms.** Common = known-message presence; for TrustMark it also requires the native BCH flag. Bit accuracy: median [Q1, Q3] (decoded calls/planned). Abstentions are calls with no decoded message: an empty WAM mask, or a failed TrustMark BCH decode.",
        table(["Arm", "Channel", "Common", "Exact message", "Native", "Bit accuracy", "Abstentions", "Missing calls"], external_rows),
    ])


def table4(run):
    rows = []
    for arm in ["unmarked", *ARMS]:
        for ch in CHANNELS:
            q = run.quality(arm, ch)
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
            for kind, key in (("attack (output vs its input)", "distortion"), ("total (output vs source)", "total_distortion")):
                block = q.get(key)
                rows.append((LABEL[arm], CHANNEL_LABEL[ch], kind, metric_summary(block, "psnr_db"), metric_summary(block, "ssim_rgb"), metric_summary(block, "lpips"), strict))
    return "\n\n".join([
        "### Table 4. Quality",
        "Each value is the median [Q1, Q3] over complete sources (observed/planned sources). Stochastic cells use each source's median over its three seeds. Strict clean gate: PSNR > 35 dB, SSIM > .9 and LPIPS < .1. Human ratings are missing. C0 clean is the source itself (infinite PSNR).",
        table(["Arm", "Channel", "Distortion", "PSNR dB", "SSIM", "LPIPS", "Strict gate"], rows),
    ])


def table5(run):
    neg = run.rep["negatives"]
    rows = []
    for key, v in neg.items():
        parts = key.split("/")
        arm, ch, control, pred = parts[0], parts[1], parts[3], parts[4]
        if arm in INTERNAL and pred not in ("A", "C"):
            continue
        rows.append((LABEL.get(arm, arm), ch if ch != "None" else "clean", control, pred, f"{v['positives']}/{v['observed']} of {v['planned']}",
                     v["unresolved"], f"{v['source_any_positive']}/{v['planned_sources']}"))
    wrong = []
    for arm in EXTERNAL:
        for ch in CHANNELS:
            ext = run.ext(arm, ch)
            if ext is None:
                continue
            wrong.append((LABEL[arm], CHANNEL_LABEL[ch], f"{ext['independent_wrong_message_present']}/{ext['planned']}", f"{ext['wrong_message_complement_present']}/{ext['planned']}"))
    roc_rows = []
    for key, v in run.rep["empirical_roc"].items():
        arm, ch, _, kind, view = key.split("/")
        if "strict_fpr_targets" not in v:
            roc_rows.append((LABEL[arm], ch, kind, view, "both", f"not estimable: {v['unresolved']} unresolved C0 negatives (safety blocks)", "", "", ""))
            continue
        for target, point in v["strict_fpr_targets"].items():
            if point is None:
                roc_rows.append((LABEL[arm], ch, kind, view, f"FPR < {target}", "not estimable", "", "", ""))
                continue
            thr = "reject all" if point.get("threshold") is None else fmt(point["threshold"], 4)
            roc_rows.append((LABEL[arm], ch, kind, view, f"FPR < {target}", thr, f"{point['tp']}/{v['positive_planned']}",
                             f"{point['fp']}/{v['negative_planned']}", f"1/{v['negative_planned']}"))
    return "\n\n".join([
        "### Table 5. Negatives and empirical ROC",
        "**5a. Fixed-operating-point negatives.** C0 = unmarked image read with the arm's detector; wrong owner = marked image read with owner beta (image-domain arms). Image-domain arms: endpoints A (the negative-gate endpoint) and C. Counts are per call; source-any counts a source with any positive call.",
        table(["Arm", "Channel", "Control", "Endpoint", "Positives/observed of planned", "Unresolved", "Source-any positive"], rows),
        "**5b. Wrong-message presence** (marked outputs read with an independent wrong message or its bitwise complement).",
        table(["Arm", "Channel", "Independent wrong message", "Complement"], wrong),
        "**5c. Outcome-selected empirical ROC (descriptive only; not a calibration).** Score ≥ cutoff; among cutoffs whose empirical FPR is strictly below the target, the one with maximum TPR, then fewest false positives, then highest cutoff. Resolution is one negative. At 60 sources a zero-of-60 count has a one-sided 95% upper limit of about .049, far above .001.",
        table(["Arm", "Channel", "Score", "View", "Target", "Cutoff", "TP/positives", "FP/negatives", "Resolution"], roc_rows),
    ])


def table6(run):
    rows = []
    for comp, bins in run.rep["matched_distortion"].items():
        for b in bins:
            lo, hi = b["lpips_bin"]
            am, em = b["attack_match"], b["embedding_and_attack_match"]
            pairs = Counter(f"{p['left_strength']}/{p['right_strength']}" for p in b["selected_pairs"])
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
        "Within source, fixed LPIPS bins, calipers |ΔLPIPS| ≤ .02, |ΔPSNR| ≤ 1 dB and |ΔSSIM| ≤ .02, at most one pair per source and bin, chosen blind to detection. Stage 2a has one strength per channel (.2), so every selected pair is .2/.2. Left and right are source-majority successes of the two sides. Discordant counts are left-only/right-only. The last column is the stricter subset that also matches native embedding quality (≤ 1 dB, .01 SSIM, .01 LPIPS). No inferential tests.",
        table(["Comparison (left vs right)", "LPIPS bin", "Matched m", "Left success", "Right success", "(L−R)/m", "Discordant L/R", "Status", "Strength pairs", "Median |Δ| PSNR/SSIM/LPIPS", "Embedding-qualified m"], rows),
    ])


def driver_events(text):
    events = []
    for line in text.splitlines():
        m = re.match(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (.*)$", line)
        if m:
            events.append((m.group(1), m.group(2)))
    return events


def table7(run):
    rec = run.record
    gen = defaultdict(list)
    det = defaultdict(list)
    for row in run.rows.values():
        if row.get("status") != "ok":
            continue
        gen[(row["arm"] if row["channel"] == "clean" else row["channel"])].append(row.get("generation_seconds") or 0)
        for method, seconds in (row.get("detection_seconds") or {}).items():
            det[method].append(seconds)
    embed_rows = [(LABEL[a], len(gen[a]), f"{statistics.median(gen[a]):.2f}", f"{sum(gen[a]) / 3600:.2f}") for a in ["unmarked", *ARMS] if gen[a]]
    channel_rows = [(CHANNEL_LABEL[c], len(gen[c]), f"{statistics.median(gen[c]):.2f}", f"{sum(gen[c]) / 3600:.2f}") for c in CHANNELS[1:] if gen[c]]
    detect_rows = [(LABEL[a], len(det[a]), f"{statistics.median(det[a]):.3f}", f"{sum(det[a]) / 3600:.2f}") for a in ARMS if det[a]]
    memory_rows = [(m["phase"], m["started_utc"][11:19], f"{m['peak_allocated_bytes'] / 2**30:.2f}") for m in run.memory]
    events = [(t, e.replace("|", "\\|")) for t, e in driver_events(run.driver_log)]
    budget = rec["budget"]
    env = rec["environment"]
    pins = ", ".join(f"{k} {v}" for k, v in env.items() if k in ("torch", "torchvision", "diffusers", "transformers", "numpy", "Pillow", "lpips", "av", "lightning", "torchmetrics"))
    return "\n\n".join([
        "### Table 7. Cost and provenance",
        f"Hardware: {rec['gpu']} (vast.ai container 57402655), Python 3.11.17. Pins: {pins}; full list in `run.json`. Precision: SD1.5 and SDXL UNets in fp16, SDXL VAE in full fp32, MoVQ in fp32. Run commit: server {rec['commit'][:7]}, blob-identical to laptop b4b2810.",
        f"Full run: {rec['created_utc'][:19]}Z, {rec['duration_seconds'] / 3600:.2f} h; smoke {run.smoke['duration_seconds'] / 60:.1f} min of compute over its attempts; projection {run.smoke_timing['projected_full_seconds'] / 3600:.2f} h against {rec['projection']['available_seconds'] / 3600:.2f} h available, nothing dropped.",
        f"Budget clock: {budget['instance_seconds'] / 3600:.1f} h from the first instance creation (2026-10-23 17:28Z, including the stopped period), USD {budget['projected_charged_usd']:.2f} at an assumed USD {budget['hourly_usd']}/h; ceiling {budget['max_instance_hours']} h / USD {budget['max_usd']}. The billed amount is lower and is on the vast.ai invoice.",
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
    for ch, name, enc in (("R0", "SD1.5 img2img .2", "SD1.x"), ("R1", "SDXL img2img .2", "independent SDXL encoder")):
        for arm in INTERNAL:
            seeds = defaultdict(int)
            for row in run.unit_rows(arm, ch):
                ep = ((row.get("detections") or {}).get(arm, {}).get(ALPHA) or {}).get("endpoints") or {}
                if row.get("status") == "ok" and ep.get("C"):
                    seeds[row["source_id"]] += 1
            overlap = sum(1 for s in step1 if seeds[s] >= 2)
            rest = sum(1 for s in seeds if s not in step1 and seeds[s] >= 2)
            total = run.cell(arm, ch, "C")["positive_sources"]
            rows.append((name, enc, LABEL[arm], frac(total, 60), f"this study: step-1 sources {overlap}/24, new sources {rest}/36"))
    return "\n\n".join([
        "### Table 8. Historical context (source-majority C at strength .2)",
        "Step 1 used 24 development sources, all of which are among this study's 60; on them, R0 reproduces step 1 exactly. Do not pool the 24-source SD2.1 cell with the 60-source SDXL cell, and do not attribute the difference to the encoder alone: R1 also changes the model family, resolution and pipeline.",
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
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight")


def figure1(run, plt, out):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), gridspec_kw={"width_ratios": [1, 1, 1.6]})
    offsets = {a: (i - 2.5) * .012 for i, a in enumerate(ARMS)}
    for ax, ch in zip(axes[:2], ("R0", "R1")):
        ax.axvspan(.05, .15, color="#eeeeee", zorder=0)
        ax.axvspan(.35, .45, color="#eeeeee", zorder=0)
        for x in (.1, .4):
            ax.text(x, .5, NOT_RUN.replace(" (", "\n("), ha="center", va="center", fontsize=6.5, color="#777777", rotation=90)
        for arm in run.channel_arms(ch):
            cell = run.cell(arm, ch)
            p, (lo, hi) = cell["positive_sources"] / 60, cell["cp95"]
            x = .2 + offsets[arm]
            ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], fmt=MARKER[arm], color=COLOR[arm], ms=5, capsize=2, lw=1,
                        label=f"{LABEL[arm]} ({endpoint(arm)})")
        if ch == "R1":
            ax.annotate("primary cell\n(F5 C, R1 .2)", xy=(.2 + offsets["f5-r2"], 0), xytext=(.27, .22), fontsize=7,
                        arrowprops=dict(arrowstyle="->", lw=.7, color="#333333"))
        ax.set_xlim(.05, .45)
        ax.set_xticks([.1, .2, .4])
        ax.set_ylim(-.04, 1.04)
        ax.set_xlabel("img2img strength")
        ax.set_title(CHANNEL_LABEL[ch].replace(" .2", "") + " img2img")
    axes[0].set_ylabel("source-majority success rate (k/60)")
    ax = axes[2]
    diag = ["clean", "X1", "X2", "D1", "D3"]
    for arm in ARMS:
        xs, ys, los, his = [], [], [], []
        for i, ch in enumerate(diag):
            if ch != "clean" and arm not in run.channel_arms(ch):
                continue
            cell = run.cell(arm, ch)
            p = cell["positive_sources"] / 60
            xs.append(i + offsets[arm] * 8)
            ys.append(p)
            los.append(p - cell["cp95"][0])
            his.append(cell["cp95"][1] - p)
        ax.errorbar(xs, ys, yerr=[los, his], fmt=MARKER[arm], color=COLOR[arm], ms=4.5, capsize=1.5, lw=.8, ls="none")
    ax.set_xticks(range(len(diag)))
    ax.set_xticklabels([CHANNEL_LABEL[c] for c in diag], rotation=20, ha="right")
    ax.set_ylim(-.04, 1.04)
    ax.set_title("Deterministic controls and diagnostics (one output per source)")
    handles = [plt.Line2D([], [], marker=MARKER[a], color=COLOR[a], ls="none", label=f"{LABEL[a]} ({endpoint(a)})") for a in ARMS]
    fig.suptitle("Figure 1. Source-majority success with 95% Clopper-Pearson bars, n = 60 development sources (stage 2a)", fontsize=9, y=1.03)
    fig.tight_layout()
    fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False, bbox_to_anchor=(.5, -.08))
    save(fig, out, "fig1-success-by-strength")
    plt.close(fig)


def figure2(run, plt, out):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), sharey=True)
    counts = defaultdict(set)
    for ax, (metric, label) in zip(axes, (("psnr_db", "attack PSNR dB (output vs its input)"), ("ssim_rgb", "attack SSIM"), ("lpips", "attack LPIPS"))):
        for arm in ARMS:
            for ch in ("R0", "R1"):
                if arm not in run.channel_arms(ch):
                    continue
                q = run.quality(arm, ch)["distortion"][metric]["complete_source_medians"]
                cell = run.cell(arm, ch)
                ax.plot(q["median"], cell["positive_sources"] / 60, MARKER[arm], color=COLOR[arm], ms=5,
                        mfc=COLOR[arm] if ch == "R1" else "white", mew=1.2)
                counts[ch].add(q["observed"])
        ax.set_xlabel(label)
    axes[0].set_ylabel("source-majority success rate (k/60)")
    handles = [plt.Line2D([], [], marker=MARKER[a], color=COLOR[a], ls="none", label=LABEL[a]) for a in ARMS]
    handles += [plt.Line2D([], [], marker="o", color="#555555", mfc="white", ls="none", label="R0 SD1.5 .2 (open)"),
                plt.Line2D([], [], marker="o", color="#555555", ls="none", label="R1 SDXL .2 (filled)")]
    axes[2].legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, .5), frameon=False)
    span = lambda s: f"{min(s)}–{max(s)}" if len(s) > 1 else f"{min(s)}"
    fig.text(.5, -.04, f"Quality sources with three complete seeds: R0 {span(counts['R0'])}/60 (safety blocks), R1 {span(counts['R1'])}/60. "
             "Success counts all 60 sources (blocked = failure).", ha="center", fontsize=7, color="#444444")
    fig.suptitle("Figure 2. Robustness against achieved attack distortion (median over sources of within-source seed medians); one strength per channel, so no segments", fontsize=9, y=1.03)
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
             "Stage 2a has one strength per channel, so every pair is .2/.2.", ha="center", fontsize=7, color="#444444")
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
            ax.set_title(f"{CHANNEL_LABEL[ch]}, {'output-level, 180/180' if view == 'outputs' else 'source-median, 60/60'}; resolution 1/{n}")
            if r == 1:
                ax.set_xlabel("empirical FPR on C0 (symlog; dashed .001 and .01)")
            if c == 0:
                ax.set_ylabel("empirical TPR")
    fig.legend(*axes[1, 1].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(.5, -.04))
    fig.suptitle("Figure 5. Outcome-selected empirical ROC of external score kinds (descriptive only, not a calibration). F5 has no continuous surrogate; its fixed point is in Table 2", fontsize=9, y=1.01)
    fig.tight_layout()
    save(fig, out, "fig5-empirical-roc")
    plt.close(fig)


def figure6(run, plt, out):
    diag = ["clean", "X1", "X2", "D1", "D3"]
    arms = [a for a in ARMS if a != "pixelseal"]
    fig, ax = plt.subplots(figsize=(9.5, 3.4))
    width = .15
    for i, arm in enumerate(arms):
        for j, ch in enumerate(diag):
            if ch != "clean" and arm not in run.channel_arms(ch):
                continue
            cell = run.cell(arm, ch)
            x = i + (j - 2) * width
            ax.bar(x, cell["positive_sources"], width * .92, color=COLOR[arm], alpha=.35 + .13 * j, edgecolor="black", lw=.3)
            q = run.quality(arm, ch)["distortion"]["lpips"]["complete_source_medians"]
            label = f"{cell['positive_sources']}" + ("" if ch == "clean" else f"\n{q['median']:.3f}")
            ax.text(x, cell["positive_sources"] + 1, label, ha="center", va="bottom", fontsize=5.2)
    ax.set_xticks(range(len(arms)))
    ax.set_xticklabels([LABEL[a] for a in arms])
    ax.set_ylim(0, 68)
    ax.set_ylabel("sources k/60 (fixed endpoint)")
    fig.text(.5, -.03, "Bars per arm, left to right: clean, X1, X2, D1, D3 (gaps are out of scope). Label: k, then the median attack LPIPS. "
             f"R1 rinse: {NOT_RUN}. Pixel Seal is clean and R1 only.", ha="center", fontsize=7, color="#444444")
    fig.suptitle("Figure 6. Deterministic controls against their clean parent (one output per source)", fontsize=9, y=1.02)
    fig.tight_layout()
    save(fig, out, "fig6-controls")
    plt.close(fig)


def figure7(run, out, tiles_out=None, tile=144):
    import numpy as np
    from PIL import Image, ImageDraw
    first_six = [s["source_id"] for s in run.sources[:6]]
    arms = ["unmarked", *ARMS]
    # ASCII only: PIL's default bitmap font has no minus or multiplication sign.
    cols = ["clean mark", "|mark - source| x10", "R0 SD1.5 .2 seed 12", "R1 SDXL .2 seed 12"]

    def load(unit_id):
        row = run.rows.get(unit_id)
        if not row or row.get("status") != "ok" or not row.get("output"):
            return None
        return Image.open(run.images / Path(row["output"]["path"]).name).convert("RGB")

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
                tiles = [mark, residual, load(f"R0:{sid}:{arm}:0.2:12"), load(f"R1:{sid}:{arm}:0.2:12")]
                for j, img in enumerate(tiles):
                    x0, y0 = label_w + j * size, head_h + i * size
                    if img is None:
                        draw.rectangle([x0 + 1, y0 + 1, x0 + size - 2, y0 + size - 2], outline="#bbbbbb")
                        reason = "not in scope" if (j >= 2 and arm not in run.channel_arms("R0" if j == 2 else "R1")) else "blocked/missing"
                        draw.text((x0 + 8, y0 + size // 2 - 6), reason, fill="#888888")
                        continue
                    canvas.paste(img.resize((size, size), Image.LANCZOS), (x0, y0))
            canvas.save(dest / f"fig7-source-{sid}-{scale_name}.png", optimize=True)
    return first_six


def figure_a1(run, plt, out):
    import numpy as np
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), sharey=True)
    channels = ["clean", "X1", "X2", "D1", "D3", "R0", "R1"]
    for ax, (arm, tier, title) in zip(axes, (("f5-r2", "semantic", "F5 semantic tier"), ("f5-r2", "instance", "F5 instance tier"), ("v5-r3", "semantic", "v5 semantic tier"))):
        for i, ch in enumerate(channels):
            for who, color, dx in ((arm, COLOR[arm], -.15), ("unmarked", COLOR["unmarked"], .15)):
                if who == "unmarked" and ch == "clean":
                    continue
                vals = []
                for row in run.unit_rows(who, ch):
                    raw = (((row.get("detections") or {}).get(arm) or {}).get(ALPHA) or {}).get("raw") or {}
                    t = raw.get(tier) or {}
                    if row.get("status") == "ok" and t.get("threshold"):
                        vals.append(t["score"] / t["threshold"])
                if not vals:
                    continue
                parts = ax.violinplot([vals], positions=[i + dx], widths=.28, showmedians=True)
                for body in parts["bodies"]:
                    body.set_facecolor(color)
                    body.set_alpha(.5)
                for key in ("cbars", "cmins", "cmaxes", "cmedians"):
                    parts[key].set_color(color)
                    parts[key].set_linewidth(.7)
        ax.axhline(1, color="black", lw=.7, ls="--")
        ax.set_xticks(range(len(channels)))
        ax.set_xticklabels([CHANNEL_LABEL[c] for c in channels], rotation=35, ha="right")
        ax.set_title(title)
    axes[0].set_ylabel("score / threshold (1 = threshold)")
    fig.text(.5, -.06, "Coloured: the arm's own marked outputs; grey: C0 (unmarked) outputs of the same channel, read with the same detector and owner alpha. "
             "R0 and R1 pool three seeds.", ha="center", fontsize=7, color="#444444")
    fig.suptitle("Figure A1 (post-hoc, descriptive). Detector margin by channel; not used to choose any setting", fontsize=9, y=1.03)
    fig.tight_layout()
    save(fig, out, "figA1-signal-margins")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True, help="dev-run results folder holding stage2a-full and stage2a-smoke")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-tiles", type=Path, help="optional folder for full-resolution Figure 7 panels")
    args = parser.parse_args()
    run = Run(args.run)
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
    header = ["# Encoder-transfer stage 2a: T7 tables and figures",
              "",
              "Generated by `scripts/encoder_transfer_report.py` from the saved stage-2a outputs (run commit "
              f"{run.record['commit'][:7]}, contract sha {run.record['manifest_sha256'][:8]}…). Every count is read from `metrics.json` or from the persisted per-call results in `rows.jsonl`; nothing is recomputed from images. "
              "Development evidence on 60 sources; exploratory throughout.",
              "",
              "## Figures",
              "",
              "| Figure | File | Content |",
              "|---|---|---|",
              "| 1 | `figures/fig1-success-by-strength.png` | Source-majority success with CP95 bars at R0/R1 .2 and the deterministic controls; .1 and .4 not run by design |",
              "| 2 | `figures/fig2-robustness-vs-distortion.png` | Success rate against achieved attack PSNR, SSIM and LPIPS |",
              "| 3 | `figures/fig3-clean-quality.png` | Clean native quality per source, median and IQR |",
              "| 4 | `figures/fig4-matched-bins.png` | Matched-bin overlap and paired differences, empty bins explicit |",
              "| 5 | `figures/fig5-empirical-roc.png` | Empirical ROC step plots, output and source-median views |",
              "| 6 | `figures/fig6-controls.png` | Clean, resize, SDXL VAE and MoVQ controls against the clean parent |",
              f"| 7 | `figures/fig7-source-<id>-preview.png` | Fixed illustration: the first six sources of the frozen list ({', '.join(str(s) for s in first_six)}), all arms, seed 12; the rinse pair is {NOT_RUN}. Full-resolution panels are kept in the run folder |",
              "| A1 | `figures/figA1-signal-margins.png` | Post-hoc detector margins by channel (descriptive) |",
              "",
              "## Tables",
              ""]
    body = "\n\n".join(t(run) for t in (table1, table2, table3, table4, table5, table6, table7, table8))
    (args.out / "tables.md").write_text("\n".join(header) + body + "\n", encoding="utf-8")
    print(f"wrote {args.out / 'tables.md'} and {len(list(figures.iterdir()))} figure files")


if __name__ == "__main__":
    main()
