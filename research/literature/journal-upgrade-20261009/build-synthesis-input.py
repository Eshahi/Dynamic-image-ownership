"""Build a planning-only literature ledger from inspected primary copies.

No scientific runs, data selection, or protected claim-ledger writes.
Metadata reuses existing bibliography keys; the generated subset is not a replacement.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
bib = (ROOT / "research/references.bib").read_text(encoding="utf-8-sig")

records = [
    ("waves", "An2024WAVESv2", "m1-primary-extension/waves-v2.html",
     "Sections 3.1.1-3.1.3, 3.2 and 4",
     "WAVES evaluates detection at 0.1% FPR and performance across attack-quality tradeoffs; detection and identification are distinct endpoints.",
     "Benchmark conventions do not establish universal acceptance thresholds for a thesis; its full attack suite is outside the three-threat scope.",
     "Use fixed-FPR and quality-conditioned evaluation, restricted to T3/T4/T5."),
    ("zodiac", "Zhang2024ZoDiacv2", "m1-primary-extension/zodiac-v2.html",
     "Section 3; Section 4, Tables 1 and 3",
     "ZoDiac optimizes a Fourier ring in an inverted diffusion latent and blends the decoded image with the original; detection uses diffusion inversion. Table 3 reports Zhao23 detection 0.988 at FPR 0.062, or 0.938 at FPR 0.004.",
     "Different detector thresholds, distortion and attack settings prevent comparison of those rates with F5 source-majority counts.",
     "Include as an inversion-based post-hoc baseline, recalibrated on development/calibration data."),
    ("seal", "Arabi2025SEALv4", "m1-primary-extension/seal-v4.html",
     "Section 3, Algorithms 1-3; Section 4, Tables 1-2",
     "SEAL binds initial noise to caption-derived semantic codes using secret-salted projections; detection requires semantic extraction and inversion. Table 1 cat-insertion AUC is 0.551 for the basic method and 0.982 with spatial verification.",
     "AUC for that semantic edit is neither TPR at a fixed FPR nor the thesis copy-paste endpoint; this is a generation-time method.",
     "Semantic binding is prior art; use as a mechanism reference or in a separately defined generative comparison."),
    ("grow", "Luo2026GROW", "m1-primary-extension/grow-cvpr2026.pdf",
     "Sections 3-5.5, Algorithm 1, Tables 1-3",
     "GROW guides generation toward a terminal-latent frequency message and extracts through a VAE encoder without inversion. Its 16-bit COCO results report PSNR 27.54, SSIM 0.85, LPIPS 0.05, DiffPure message accuracy 0.95; extraction is 0.24 seconds on T4.",
     "Generated-image message accuracy and paper-specific hardware are not existing-photo checked detection or a local latency benchmark.",
     "Inversion-free latent extraction alone is not novel; measure total local detector cost."),
    ("ctrlregen", "Liu2024CtrlRegenv2", "m1-primary-extension/ctrlregen-v2.html",
     "Sections 3.2 and 4, Table 1",
     "CtrlRegen regenerates from clean noise using DINOv2 semantic and ControlNet spatial guidance. Table 1 Tree-Ring TPR at 1% FPR is 0.12 under CtrlRegen versus 0.87 under Regen; CtrlRegen PSNR is 19.32.",
     "These attack results are not F5 measurements; learned adapters and substantial distortion require a separate admissibility and resource check.",
     "Test a stronger controlled T3 attack only after the cheap independent-VAE test; do not infer general robustness from DDIM alone."),
    ("wam", "Sander2025WatermarkAnythingv2", "m1-primary-extension/wam-v2.html",
     "Sections 3-5; Appendix G.3, Tables 8-9",
     "Watermark Anything learns localized watermark presence and message decoding. Table 8 gives PSNR 38.3, SSIM 0.99, LPIPS 0.04 and splicing bit accuracy 95.30%; Table 9 shows regeneration bit accuracy falling from 100% to 49.1% over increasing distortion.",
     "Localization and bit accuracy are not whole-image forgery rejection, TPR or content-binding efficacy; pretrained assets are not locally reproduced here.",
     "Use as a neural post-hoc comparator and a donor-delivery diagnostic, separating its localization goal from authentication."),
    ("diffmark", "NguyenLe2026DiffMarkv1", "m1-2026-followup/diffmark-v1.html",
     "Sections 3, 4.1 and 4.6; Table 2; Appendix G.4",
     "DiffMark trains latent consistency bridges and a VAE-based 64-bit extractor without diffusion inversion. Table 2 reports TPR at 0.1% FPR of 0.81 for VAE and 1.00 for diffusion regeneration; Section 4.6 reports 16.4 ms extraction on L40S.",
     "Preprint; training and generation setting differ, exact Table 2 severity is unclear, and latency is not hardware-normalized against F5.",
     "Use as recent context for learned extraction and transfer, not a numeric claim that F5 loses or wins."),
    ("freqmark", "Guo2024FreqMarkv1", "journal-upgrade-20261009/sources/freqmark-v1.html",
     "Sections 4.1-4.5, 5.1-5.4; Table 1",
     "FreqMark optimizes latent-frequency perturbations through a frozen VAE and reads bits with fixed pretrained image features. For 48 bits and 400 optimization steps, Table 1 ImageNet reports PSNR 31.27, SSIM 0.857 and diffusion-regeneration bit accuracy 0.969.",
     "Bit accuracy is not TPR; its 60-step attack and lower fidelity are not matched to F5. Published numbers do not establish performance under our strict quality constraints.",
     "Closest prioritized post-hoc latent-frequency comparator; compare quality frontiers and separately calibrated FPR."),
    ("latent-watermark", "Meng2024LatentWatermarkv3", "journal-upgrade-20261009/sources/latent-watermark-v3.html",
     "Sections 3.1-3.3 and 4.1-4.2; Table 2",
     "Latent Watermark injects a message into the terminal latent and detects with a VAE encoder and trained decoupler. It trains on 50,000 LAION images. Table 2, 48-bit COCO SD2.1 reconstruction gives 99.09% bit accuracy and 100% TPR at 1% FPR.",
     "Generation-time evaluation, a different operating point, and learned modules preclude direct comparison with existing-photo F5; no instance-binding proof follows.",
     "Further prior art against novelty claims based solely on terminal-latent or inversion-free extraction."),
]

papers, evidence = [], []
for pid, key, artifact, locator, direct, limit, inference in records:
    block = re.search(r"@\w+\{" + re.escape(key) + r",(.*?)(?=\n@|\Z)", bib, re.S).group(1)
    def field(name):
        found = re.search(r"\b" + name + r"\s*=\s*\{(.*?)\}", block, re.S)
        return found.group(1) if found else None
    path = ROOT / "research/literature" / artifact
    url = field("url").replace("/abs/", "/html/")
    papers.append({
        "schema_version": "1.0", "paper_id": pid, "citation_key": key,
        "doi": field("doi"), "canonical_url": url, "title": field("title"),
        "authors": field("author").split(" and "), "year": int(field("year")),
        "venue": "CVPR 2026" if pid == "grow" else None,
        "access_date": "2026-10-09", "source_type": "paper" if pid == "grow" else "preprint",
        "verification": "verified", "inspected_content": "full-text",
        "inspection": {"artifact": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "limitations": [limit],
    })
    for kind, claim in (("direct-evidence", direct), ("agent-inference", inference)):
        evidence.append({
            "claim_id": "journal-" + pid + "-" + kind, "claim": claim, "source_id": pid,
            "kind": kind, "stance": "supporting" if kind == "direct-evidence" else "inconclusive",
            "locator": locator, "confidence": "high" if kind == "direct-evidence" else "medium",
            "limitations": [limit], "assumptions": ["Author-reported measurements, not local reproduction." if kind == "direct-evidence" else "The prospective study concerns existing photos, matched quality and separately calibrated detection."],
        })

response = {
    "request_id": "journal-upgrade-20261009", "papers": papers, "evidence": evidence,
    "assumptions": ["Bounded primary-source refresh, not an exhaustive novelty search; all nine citation keys already exist in research/references.bib.", "Existing M2 outputs are historical evidence; no new image inspection or scientific run was performed."],
    "open_questions": ["Can F5 retain checked detection with a genuinely independent VAE at matched image quality?", "Does content verification reject delivered forgeries that a binding-disabled detector accepts?", "Can post-hoc baselines meet the same quality and empirical FPR requirements?", "Does an enrollment-aware endpoint fit the intended claim, or should the paper retain narrower self-consistency semantics?"],
}
(OUT / "response.json").write_text(json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {len(papers)} paper cards and {len(evidence)} evidence entries.")
