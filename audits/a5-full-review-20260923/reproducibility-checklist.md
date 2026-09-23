# Reproducibility checklist for A5 documentary review

| Item | Status | Evidence or limitation |
| --- | --- | --- |
| Reviewer differs from author | Checked | `/root/a5_full_review` reviewed `/root` artifacts. |
| Exact four A5 artifact bytes | Checked | SHA-256 values in `audit-report.md`; rehash after any change. |
| A5 task and proposal route | Checked | `guide-plan-38.json` A5 and proposal extraction Table 8. |
| Source/scope contracts | Checked | A3 IO, scope guard and research contract inspected. |
| Feature/code/key/owner serialization | Specified | CLIP, q, pHash, domain separation, byte packing, Hamming search. |
| Initial-noise and image shape path | Specified | Original grid separated from padded model grid; matched C0. |
| Template/DCT score and common-q decision | Specified | Detector input boundary and error states retained. |
| Final RGB8 PNG verification path | Specified | Saved bytes are decoded before final signatures/score. |
| Config schema and cross-field validator | Checked | Eight synthetic tests passed with verified Windows Python. |
| Scalar DDIM reference | Checked | Six standard-library tests passed. |
| Original dataset bytes/versions/splits | Not supplied | A4/data work; no dataset result can be verified. |
| Diffusion/CLIP weights and artifact receipts | Not supplied | Exact runtime acquisition and verification remain pending. |
| Scientific run manifests, seeds and failed runs | Not supplied | No scientific compute occurred in this review. |
| Analysis tables/figures and hypotheses | Not supplied | No empirical claims accepted. |
| Compute authorization and plan gate | Not supplied | Both retain separate approvals. |
| Original offline HTML | Preserved | Modified user file untouched; hash recorded in report. |

Commands run from repository root:

```powershell
& '.\.thesis-build\venv\Scripts\python.exe' -m unittest discover -s scripts -p 'test_validate_method_config.py' -v
& '.\.thesis-build\venv\Scripts\python.exe' -m unittest discover -s scripts -p 'test_noise_path_reference.py' -v
```

The first passed 8/8 and the second 6/6. Both are ordinary checks; neither is a model/image feasibility trial.
