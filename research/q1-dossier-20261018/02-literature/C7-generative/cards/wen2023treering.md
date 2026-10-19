# Tree-Ring — V2 refresh

- Authors: Yuxin Wen; John Kirchenbauer; Jonas Geiping; Tom Goldstein.
- Title/version: *Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust*, arXiv 2305.20030v3, 2023. NeurIPS 2023 published title: *Tree-Rings Watermarks: Invisible Fingerprints for Diffusion Images*.
- Primary: https://arxiv.org/html/2305.20030v3 ; venue: https://papers.neurips.cc/paper_files/paper/2023/hash/b54d1757c190ba20dbc4f9e4a2f54149-Abstract-Conference.html . DOI: 10.48550/arXiv.2305.20030. Access: 2026-10-18.
- Setting/mechanism: control generation's initial Gaussian noise; impose a Fourier-ring key. No arbitrary-photo encoder/writer is supplied.
- Detector/access/side information: diffusion model and key; DDIM inversion with empty prompt. SD2 evaluation uses 50 generation and 50 inversion steps; radius 10.
- Payload/data/count: primarily watermark presence/key matching; COCO prompts and generated images. Main attack-table sample count not re-extracted in this refresh; do not infer it from quality-set size.
- Threat/evidence: §4.1–4.2/Table 1 evaluate ordinary manipulations; those averages are not a matched regeneration-strength sweep or content authentication.
- Limits/relevance: useful initial-noise comparator with substantial inversion cost; surviving a copied signal does not authenticate depicted content.
- Inspection: freshly read §§3.2–3.4, 4.1–4.2/Table 1; inherited locator trail also at `research/literature/m1-latent-survey/cards/tree-ring.md`. V2 means inspected method/evaluation, not reproduced.
