# Evidence synthesis

This report preserves reported evidence; source hashes establish identity, not scientific truth.

- REC-GNRI-MECH: Guided residual inversion is a reconstruction candidate distinct from adding unrelated random noise. [gnri-v5; supporting; agent-inference; confidence medium]. Limitations: Captioned other-model experiments do not establish our SD1.5 empty-prompt profile.

- REC-GNRI-LIMIT: GNRI is not uniformly highest-fidelity: Appendix H2 reports a slower stochastic alternative with higher PSNR. [gnri-v5; contradicting; direct-evidence; confidence high]. Limitations: Different timing and stochastic storage profile; not our experiment.

- REC-TRDI-LIMIT: The inspected SD1.5 table reports ReNoise+TRDI 22.67 dB and GNRI+TRDI 22.32 dB, below the proposal's 35 dB target. [trdi-v1; contradicting; direct-evidence; confidence high]. Limitations: Captioned 1000-pair sample and 50 steps; no numerical equivalence to local single-image result.

- REC-VAE-CAND: Decoder adaptation targets repeated VAE reconstruction degradation; it is relevant if our codec control fails, not guaranteed single-pass success. [reed-vae-v1; inconclusive; agent-inference; confidence medium]. Limitations: Inspected official repository provides no ready code/weights; iterative task differs.
