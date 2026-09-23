# Baseline readiness — preliminary, not selection or execution approval

Issue #8; downstream RQ-03, HYP-03, METRIC-07. Inspected 2026-09-23 UTC.

| Role | Candidate | Evidence | Remaining blocker |
| --- | --- | --- | --- |
| Neural-decoder comparison | InvisMark v2 | Targeted methods in literature/inspections/invismark-v2-method.md | Checkpoint provenance/configuration, environment and resource preflight, common evaluation endpoints |
| Inversion comparison | SEAL | Existing seal-v4 inspection | Proposal-era comparison, pinned code/checkpoint and resource inspection |

These are distinct roles; neither paper proves the proposed image-domain DCT detector works. Candidate status does not approve model acquisition or scientific compute.

## InvisMark upstream preflight (read-only)

Repository: https://github.com/microsoft/InvisMark
Inspected commit: `8d5ce55705ada1c2daf642c97f7ff3ae6dbd1825`.
Read README, LICENSE, requirements.txt, configs.py; inspected model.py decoder fragment and Demo.ipynb code cells without executing them. All code URLs can be pinned under `https://github.com/microsoft/InvisMark/blob/8d5ce55705ada1c2daf642c97f7ff3ae6dbd1825/`.

- README links a 100-bit checkpoint without ECC. This is not the paper's separate 256-bit/ECC configuration; the paper also evaluates 100-bit watermarks. Download link not followed and checkpoint not verified.
- LICENSE is MIT for repository software; this does not independently establish checkpoint/dataset rights.
- requirements.txt pins torch 2.4.1 and torchvision 0.19.1 with CUDA-package dependencies. Do not install wholesale into the current environment; Windows/GPU compatibility remains untested.
- Demo imports `datasets` and `matplotlib`, absent from requirements.txt. It initiates a dataset download and loads a checkpoint via `torch.load`; do not run it as an ordinary smoke test. Verify checkpoint provenance and safe loading first.
- configs.py defaults to 128 encoded bits, whereas the demo slices 100 bits and restores checkpoint configuration. The adapter must validate payload/configuration rather than infer defaults.
- model.py requests pretrained ConvNeXT weights. Account for implicit downloads before a compute manifest is approved.

Next bounded implementation-preparation work: define an isolated adapter contract with explicit checkpoint hash, payload, ECC, preprocessing, timing boundaries and null controls. Measure runtime/memory only under the applicable execution authorization. No package, weight or dataset downloaded and no experiment run in this checkpoint.

Attack-access caution: the paper's residual-transfer case uses public encoder access and pre/post-watermark pairs. It is not the default donor-only T4 access regime. Proxy-model optimization likewise does not authorize expanding the excluded adaptive scenarios. Record these as limitations or separately preregistered stronger-access variants, not silently enabled attacks.
