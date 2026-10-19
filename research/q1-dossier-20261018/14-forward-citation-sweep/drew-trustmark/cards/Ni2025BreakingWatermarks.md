# Ni2025BreakingWatermarks — inspected, quantitative claims quarantined

**Source:** Yunyi Ni, Finn Carter, Ze Niu, Emily Davis, Bo Zhang. *Diffusion-Based Image Editing for Breaking Robust Watermarks*. [arXiv:2510.05978v1](https://arxiv.org/html/2510.05978v1), 7 October 2025. Accessed 2026-10-19. **V2 inspection only:** methods §4, theoretical argument, evaluation §6/Table 1 and references read. V2 does not mean endorsed evidence.

**Verified edge:** bibliography Bui et al. (2023) cites the older TrustMark preprint; not final ICCV2025 TrustMark.

**Direct evidence:** §4 describes diffusion regeneration with optional white-box decoder guidance. Table 1 reports TrustMark recovery 12% unguided and 3% guided, at PSNR 30.0/27.8 dB. The introductory under-5% TrustMark assertion does not match the unguided table entry. §4.2 describes minimizing log(1−P(correct)) as suppressing the correct payload.

**Agent assessment:** minimizing that expression instead favors larger P(correct), so the stated optimization direction is internally inconsistent. The theoretical claim also relies on a watermark-independent content assumption. Quarantine numerical/theoretical conclusions pending a corrected source and reproducible specification; retain only the verified citation edge. Similar later arXiv titles remain unresolved leads, not established duplicates or misconduct evidence.

**Artifact:** MAIN `.thesis-build/q1-research-20261018/cache/ni-2510.05978v1.html`; SHA256 `6241712DAA1DEE469A12B70D270A296BC9F484FC907FDEA72C7CE2FE9DBA10A4`.
