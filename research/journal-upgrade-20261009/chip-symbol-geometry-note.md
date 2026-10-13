# Chip and symbol geometry: an interpretation guard

Codex agent, 2026-10-13. Exploratory mathematical note for the fixed H1 protocol, not a new experiment, novelty claim or finalized thesis section. No thresholds, endpoints or selection rules change. Evidence: committed `scripts/journal_bch_readout.py:semantic_channel`, `scripts/journal_bch_carrier.py`, and the prospective `fresh-mechanism-protocol.md`.

Let p contain the 320 carrier projections and w the intended bipolar codeword pattern, including the public chip signs. Set m = w elementwise-times p. Because every w entry is +1 or -1, ||m|| = ||p||. Let P replace each of the 59 segments of m by its own mean. P is an orthogonal projector, including when segment lengths differ.

The actual intended-message score in `semantic_channel` is

    R = sum(m) / ||m||.

It is sqrt(320) times a cosine, not a unit-range cosine. The actual raw codeword decisions use the sign of each chip-sign-demodulated segment sum. Holding Pm fixed holds those decisions and the intended-message numerator fixed. Decompose m = Pm + v, where v = (I-P)m. Then

    ||m||^2 = ||Pm||^2 + ||v||^2,
    H = ||v||^2 / ||m||^2,
    R = [sum(Pm) / ||Pm||] sqrt(1-H),

provided ||Pm|| > 0. For a positive intended-message numerator, reducing within-segment variation raises R without changing any raw codeword bit. It can therefore cross the reader's score threshold without improving symbol decoding. This is an algebraic property of this reader, not evidence of channel robustness. The case ||Pm|| = 0 is undefined in the displayed factorization; the implemented zero-norm convention remains unchanged.

The chipwise and length-weighted symbol objectives also satisfy a pointwise inequality. For the convex function f(t) = max(0, 4-t)^2, Jensen's inequality gives

    mean_k f(m_k) >= sum_i L_i f(mean_i(m)) / 320.

Equal segment margins are sufficient for equality; they are not necessary when margins lie in the inactive flat region. This inequality does not order the optimized outputs, their final saved-image energy, or their regenerated recovery.

Under a hypothetical additive isotropic projection-noise channel, the noise distribution of a segment sum depends on its length, not on within-segment variation; equal original segment sums therefore have equal raw-symbol error distributions. Actual VAE/diffusion regeneration is nonlinear and image-dependent. A local linearization may mix within-segment residuals into segment means, but that observation predicts neither the sign nor size of an advantage.

Consequently H1 must show lower regenerated raw coded errors in addition to its preregistered exact-recovery separation and clean shaping diagnostic. A score-only gain is reported as a threshold/geometry effect. Even lower bit error on six development images would be a mechanism lead requiring transfer and external comparison, not a new theorem about diffusion or a validated mediation claim. Update after the fixed run: chipwise shaping lowered clean within-symbol heterogeneity on all six sources, but both objectives recovered exact q on all 36 regeneration identities and had identical checked-q results (18/18 at .2 and 16/18 at .4). H1 is not supported. See [the complete negative result](fresh-mechanism-results.md); this geometric identity does not establish a regeneration benefit.
