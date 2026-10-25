# Finite-bit null resolution and rare-FPR portability

Status: original theoretical author supplement, 2026-10-25. No new measurement, acceptance criterion, protocol amendment or experiment. This note concerns the detector's decision contract, not the validity of a reported empirical table.

## Source premise and scope

The parent researcher's inspected ROAR main/supplement passages report a 32-bit RivaGAN baseline, a nominal FPR of 10^-10 and clean TPR .95. Supplement Section 3 describes known-message bit accuracy with an inclusive threshold, while its printed binomial tail uses a strict inequality and ambiguous integer/fraction notation. These are source premises supplied for this derivation, not independently reverified empirical facts. [Official ROAR supplement, Section 3](https://openaccess.thecvf.com/content/ICCV2025/supplemental/Wang_ROAR_Reducing_Inversion_ICCV_2025_supplemental.pdf). This author's direct-open attempt returned HTTP 403; see the parent inspection record in [the ROAR card](../literature/roar-2025-primary.md).

The analysis below states what those premises would imply **if** the detector used only a deterministic hard-word comparison under a uniform, fixed-key null. It does not establish that ROAR's implementation satisfies that contract or that its observed TPR is incorrect.

## Proposition 1: the finite observation boundary

Fix a key and every reference message before observing a null image. Suppose the entire decision input is Z in {0,1}^k, with Z uniformly distributed under that key's null, and detection is deterministic. Its acceptance set A has

    FPR = |A| / 2^k.

Thus an accepting detector has FPR at least 2^-k. Empty acceptance gives FPR zero and TPR zero for this decision rule. This is an exact counting result; no asymptotic approximation or independence across images is needed. Independent fair bits are sufficient for the uniform-word premise, but marginally fair bits alone are insufficient.

For k=32, 2^-32 = 1/4,294,967,296, approximately 2.3283064 × 10^-10. Therefore deterministic, nonempty acceptance cannot reach FPR ≤ 10^-10 under this null. Even exact agreement is above the target. At least 34 uniform bits are needed for *some* nonempty acceptance region at that target: 2^-33 ≈ 1.1641532 × 10^-10, whereas 2^-34 ≈ 5.8207661 × 10^-11. This is necessary, not sufficient for useful detection.

For a fixed reference word, let B count matching bits. Under the same null,

    P(B ≥ b) = 2^-k Σ[j=b..k] binom(k,j).

At k=32, accepting B≥31 gives 33/2^32 ≈ 7.6834112 × 10^-9; accepting B>31 gives 1/2^32. Accepting bit accuracy ≥1 gives exact agreement; accepting >1 gives none. A tie convention cannot create a positive mass below 2^-32. Threshold documentation must distinguish match count from match fraction and strict from inclusive inequalities.

## Different contracts that evade the premise

**Nonuniform or key-conditional null.** A finite alphabet does not itself imply atom mass 2^-k. An accepted word may have probability 10^-12, or zero, under a nonuniform null. Conversely, correlated bits can greatly enlarge its mass. If Z is always the all-zero word and the reference K is independently uniform, exact-match FPR averaged over K is 2^-k, but it is one for the all-zero deployed key and zero for the others. A random-key average therefore does not certify every deployed key. Uniformity of Z averaged over keys also does not establish conditional uniformity or independence from K.

**Auxiliary evidence.** Retaining continuous decoder confidence, image evidence, or a second independently calibrated check changes the observation space and acceptance event. Multiplying separate FPRs requires the stated joint-null assumptions; it is not automatic.

**Randomization.** Accepting an exact 32-bit match with independent probability .4294967296 yields FPR exactly 10^-10 under the uniform null. This is a different, randomized detector, with a corresponding TPR reduction; it does not reconcile a high TPR without additional information. Merely displaying an interpolated ROC point does not implement that randomization.

## Proposition 2: searched keys and coding

If a detector accepts whenever any of M fixed key/message tests accepts, its event is the union of their acceptance events. Always,

    max_j p_j ≤ P(any accept) ≤ min(1, Σ_j p_j).

The expression 1−(1−p)^M additionally requires independent acceptance events. For M distinct exact reference words compared with the same uniform k-bit observation, the exact union probability is M/2^k, not the independence expression. Searches over transformations, candidate messages or adaptive candidates must include the complete selection procedure in the null contract; reporting only the finally selected test's nominal FPR omits selection.

Error-correcting codes change acceptance geometry, not counting principles. For 2^m codewords of length n under a uniform raw n-bit null:

- Exact match to one fixed codeword has probability 2^-n.
- Exact membership in the whole codebook has probability 2^(m−n).
- Accepting within radius r of one codeword has probability V(n,r)/2^n, where V(n,r)=Σ[j=0..r] binom(n,j). The whole-codebook union has probability 2^m V(n,r)/2^n only when these balls are disjoint.
- A nearest-codeword decoder that always returns a message makes “some valid decoded message” certain. A particular decoded message has the probability mass of its entire decoding basin; it is 2^-m only if the basins have equal null mass.

Consequently, payload length, encoded length, valid-codeword density and decoder-output length are not interchangeable null denominators. ECC redundancy can support rejection if actually checked; unconditional decoding may remove that rejection. Bit dependence and key conditioning must be specified at the raw or decoded layer where calibration is asserted.

## Continuous scores and empirical resolution

A genuinely continuous Gaussian null score has no positive atom size, so thresholds can theoretically attain tails below 2^-32. This does not validate a Gaussian tail model, its extreme-tail accuracy, or its portability across keys and image populations. Quantization or additional search changes the contract again.

For N independent, representative null trials with zero false positives, the exact one-sided 95% binomial upper confidence bound is 1−.05^(1/N). At N=1,000 it is approximately .002991; a bound of 10^-10 requires approximately 3.0 × 10^10 zero-event independent trials. Correlated variants are not independent trials, and positive-image TPR evaluation supplies no such null evidence. Analytical calibration at 10^-10 and empirically demonstrated FPR at 10^-10 must therefore remain distinct statements.
