# Schedule and conditional detection bounds

Analytical double-precision calculations from pinned schedule constants. These are not a local scheduler/model execution or a bit-exact replay. R0/R1 share a schedule but not latent units or their reverse response.

| Family | Strength | Start | Updates | alpha_bar | a/b | log SNR |
|---|---:|---:|---:|---:|---:|---:|
| R0/R1 | 0.1 | 51 | 2 | 0.950524 | 4.383144 | 2.955533 |
| R0/R1 | 0.2 | 151 | 4 | 0.826399 | 2.181821 | 1.560320 |
| R0/R1 | 0.4 | 351 | 8 | 0.504819 | 1.009684 | 0.019275 |
| R3 | 0.2 | 151 | 4 | 0.939257 | 3.932269 | 2.738433 |

A scalar a/b orders input Gaussian distinguishability only when the encoded displacement and covariance are held fixed. It does not order the nonlinear reader output, nor compare differently scaled encoders.

For a fully specified equal-covariance Gaussian location shift with Mahalanobis displacement mu, the optimal level-alpha test has TPR=Phi(mu-Phi^-1(1-alpha)); any downstream detector can do no better under those assumptions. The model here is a conditional information bound, not an empirical F5 guarantee.

| FPR alpha | mu required for TPR .90 | TPR upper at mu=2 | TPR upper at mu=4 |
|---:|---:|---:|---:|
| 0.05 | 2.9264 | 0.638760 | 0.990742 |
| 0.001 | 4.3718 | 0.137805 | 0.818527 |
| 1e-06 | 6.0350 | 0.002949 | 0.225597 |

Zero events in 60 independent source clusters give the exact one-sided 95% upper bound 4.8703%. Treating 180 seeds or 540 correlated calls as independent sources would wrongly yield the smaller bounds stored in the JSON. At 200 genuinely independent sources the upper bound is 1.4867%; a nominal 1e-6 analytic detector threshold is not empirically validated by either sample.

Source text: local scripts/three_threat_models.py DDIM_CONFIG; scripts/encoder_transfer_amend_2b.py native R3 contract; diffusers v0.35.1 scheduling_ddim.py, scheduling_ddpm.py and pipeline_stable_diffusion_img2img.py, inspected online as text. Full-chain derivation and assumptions: theory-design.md.
