# Attack evidence for the final server study

The ten V2 cards here support a bounded attack taxonomy. They do not establish the cause of F5's SDXL failure.

| Mechanism | Primary evidence | Fit to a generic no-feedback F5 attack | Main measurement needed |
|---|---|---|---|
| Single partial diffusion / noising | Zhao §§3–5; DiffPure §3 (different defense task) | Directly executable on server through an approved regenerator; already represented by study cells | Pre/post F5 score margin, latent signal gain and quality at matched noise/distortion |
| Multiple partial diffusion passes | WAVES §3.2/Figure 3 and §4; contradicts Zhao's Tree-Ring Appendix E result under different settings | Strong, simple attack if pass count and strength are fixed globally on development data | Every pass's score, LPIPS, PSNR, source-majority survival; schedule and seed control |
| Fresh-noise controlled reconstruction | CtrlRegen §§3–4 | Potentially stronger but trained control networks and high cost; side information from marked image may leak signal | Attack quality, retained content, and whether controls carry a mark |
| Spectral / latent-frequency suppression | UnMarker §§V–VI; LFM §§III–V | Candidate only if the F5 residual is concentrated in a measured band or channel; LFM tuned mask per scheme | Predeclared energy map and quality-matched gain versus generic mask |
| Proxy latent manipulation | MarkNull §§4–7 and Appendix E.2 | Closest inspected informed no-box attack. Its post-hoc images originate from SDXL and it uses SD1.5 proxy; key/detector-free. | Test F5 with *fixed global settings* and no target detector feedback; distinguish VAE round trip from optimized NLAS effect |
| Learned sparsification | DeMark §§IV–V | Relevant to VINE-R, but training data and a separate network make it a costly extension | Detection at quality match, source-majority outcome, training separation |
| Verifier-guided stochastic resampling | DRIFT §§3–5 | Base variant is no-query; adaptive variant violates the proposed no-feedback attacker model | Do not import adaptive ASR as evidence for fixed global attack; track fidelity (Table 1 fixed-λ PSNR 14.31 dB) |

**Priority inference:** A globally fixed two-pass partial diffusion attack and a fixed proxy-latent attack are the best-supported development candidates. The server study should include matched quality and a pure VAE round-trip control to identify what the proxy optimization adds. MarkNull's "on-manifold" account is a hypothesis, not a proof of F5 failure; its post-hoc theorem assumes marks predominantly lie off the data manifold. Its Assumption 2 requires proxy and target to share a latent parameterization and inversion scheme, so the theorem does not establish independent-encoder transfer. The reported FLUX-proxy cross-backbone success is empirical, comes with acknowledged fidelity cost, and does not identify the causal effect of autoencoder independence.

**Conflicts to preserve:** Zhao reports Tree-Ring TPR 0.998 after its 60-step diffusion attack (generated-image set, 1% FPR); WAVES finds two-pass rinsing effective under its separate settings and 0.1% FPR. UnMarker reports semantic-mark success from low-frequency optimization plus cropping, whereas Zhao's simple regeneration leaves Tree-Ring mostly intact. These are differences of method and operating point, not necessarily failed replications.
