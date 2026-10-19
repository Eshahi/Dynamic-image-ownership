# goonatilake2026forensicstealth — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Yevin Nikhel Goonatilake and Giuseppe Ateniese. *Removing the Watermark Is Not Enough: Forensic Stealth in Generative-AI Watermark Removal*. arXiv 2605.09203v1, 2026-05-09; venue unverified. [Full text](https://arxiv.org/html/2605.09203v1). Inspection: §2.3, §§3–4 Table 3 and §6.

**Setting/mechanism.** A per-remover ResNet-50 classifier distinguishes processed from unprocessed images after six removal families, including CtrlRegen+, UnMarker and other attacks. This detects processing traces, not an owner's identity.

**Evaluation.** 78,992 underlying sources form 157,984 clean/processed samples, with 40,000 further tampered samples. Splits are 70/15/15 by source, keeping variants together. Table 3 reports CtrlRegen+ forensic TPR 99.97% at 1% FPR and 99.64% at 0.1% FPR.

**Limits.** Attack-conditioned classification and paired source corpora do not establish universal cross-attack deployment performance. Counting both halves of a pair as independent source images would misstate the sample size. A forensic detector cannot reconstruct a missing ownership association merely by identifying processing.

**Thesis implication.** Removal success, forensic stealth and record attribution are three different outcomes. This work adds a useful evaluation distinction but does not cure the frozen E2 false matches or prove the F5 carrier survives regeneration.

