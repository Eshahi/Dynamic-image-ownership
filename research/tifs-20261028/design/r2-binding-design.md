# R2 pre-output design: VINE-B as a content-bound carrier comparator

Status: IMPLEMENTED AND ACCEPTED AS PREPARATION after Round 2 independent review, fixed before Stage S outputs. Original author: Codex design agent, 2026-10-29; status updated by the session lead. No image, scientific model, metric, timing or experiment was run. Stdlib arithmetic verified the code-volume counts below. This document is one scoped design deliverable for R2-2, not an amendment to retained F5 or a claim of novelty. The final architecture is q32 + q-tag36 + masked-h32, with radius4 decoding of q+tag only. Runtime scientific compatibility remains a later server-rehearsal obligation; see `r2-independent-review.md` for the bounded preparation verdict.

## Decision and inspected implementation

Add one `vine-b` arm. Keep VINE-R and WAM as presence-only controls. Do not add WAM-B. VINE-B uses the retained VINE writer and hard bit decoder, a new 100-bit content payload, and the unchanged F5 semantic and instance **content functions**. It does not reproduce F5 carrier statistics or its independently fragile instance channel.

The inspected files are `scripts/f5_latent_codec.py`, `scripts/revised_watermark_v5.py`, `scripts/revised_watermark_v4.py`, `scripts/encoder_transfer_runtime.py`, `scripts/tifs_stage_s_read.py`, `scripts/tifs_common.py`, the Stage S protocol/config, and the retained profile `experiments/c4-v5-two-tier-regeneration-v1/profile.json`. Relevant facts:

- `v5.CODE_BITS` is 32. Both q and h are 32-bit integers.
- F5 `_semantic_status` invokes `soft_angle(decoded_q, semantic_projections(suspect_features), decoding_error_rate)`, then expresses its angle as `theta * 32 / pi` and applies the profile radii.
- The retained semantic and instance match radii are 6, with mismatch at 10; intermediate values abstain.
- F5 instance status is the worse of its instance content status and its semantic content status. `base._decide` determines the outcome.
- The retained profile is **public-derived**, and its resolved key is public. This is crucial: neither that profile nor the proposed public tag authenticates an owner against an attacker who can create a new mark.
- The VINE adapter outputs 100 finite decoder probabilities, rounds with the retained `numpy.round` rule, and currently compares against an externally supplied known message. VINE-B must obtain those hard bits without supplying donor q/h to its operational decision.

## Exact message, encoding and references

Resolve the same retained profile using `checked, key, config = v5._resolve(profile, None)` and the same `v5.canonical_owner(owner_id)` bytes. Do not add a private key or new detector secret silently: that would change the access model and favor this arm.

Before embedding, on the original donor RGB8 image:

1. Compute the unchanged seven-view semantic features. Let `q = v5._semantic(means, checked, key, config, features, binding=True)`.
2. Obtain luminance and dimensions through the retained helpers. Compute `means, coefficients = base._analyse(luma, base._DETAIL_PLANES)` and `h = base._perceptual_hash(means, coefficients, key, config)`. This is exactly the retained public `v5.perceptual_hash` helper's computation. `_Fragile.analysis` starts with the same detail planes and adds carrier planes; `_perceptual_hash` consumes only the first `len(HASH_DETAIL_POSITIONS)` coefficients, so those unused carrier planes need not be computed or instantiated. This equivalence was inspected in source, not established by a local image run.
3. Fix the intended q/h once. Do not replace h with a hash recomputed after VINE output, select a favorable payload, or iterate the writer after seeing its clean detector result.

Define the byte string

```
tag_input = base._pack(b"tifs-vine-b/v1/q-tag", config,
                       canonical_owner_bytes, q.to_bytes(4, "big"))
mask_input = base._pack(b"tifs-vine-b/v1/h-mask", config,
                        canonical_owner_bytes, q.to_bytes(4, "big"))
digest = HMAC_SHA256(key, tag_input)
tag36 = int.from_bytes(digest[:5], "big") >> 4
mask32 = int.from_bytes(HMAC_SHA256(key, mask_input)[:4], "big")
masked_h = h ^ mask32
word100 = (q << 68) | (tag36 << 32) | masked_h
```

`base._pack` supplies unambiguous length framing: each field is prefixed by its unsigned4-byte big-endian byte length. The inspected new codec uses the equivalent `struct.pack(">I",len(field))` framing. The VINE payload is the100 most-significant-first bits of `word100`: q[32], tag[36], masked_h[32]. This is exactly100 bits. The tag checks domain, owner, detector configuration and q; h is associated with owner/q by the separate mask, but has no independent check tag or correction redundancy. A36-bit truncated tag is not a digital signature. With the retained public key it is an error-detecting code/check value, not a MAC security claim. The mask is public and reversible; it is not encryption or authentication of h.

Call the retained `Vine.embed(rgb, bits)` exactly once, with its existing residual resizing and RGB8 quantization. The evaluator payload stores q and h as eight-hex-digit strings, all 100 message bits for required delivery diagnostics, and `h_target_basis = "original donor hash before VINE embedding"`. Original references may enter Q/H/D/J and raw-bit diagnostics only after the operational detector result exists. The reader must accept no source ID, donor image, original message, q/h reference or registry as an operational argument.

The h reference differs transparently from F5's retained clean-decoded-h reference and F6's intended post-robust-tier h. Do not retrofit F5 or claim the references are identical. VINE may perturb the original h enough to fail clean F; that is an observed clean binding failure, not a reason to rewrite its intended h.

## Blind bounded-distance payload decoder

Fix radius **r = 4 on q+tag only** before outputs. Read the 100 bits with the retained VINE decoder and its hard rounding rule. Let the first32 raw bits define `q_hat`, the next36 `tag_hat`, and the last32 `masked_h_hat`.

Enumerate each 32-bit q value obtained by flipping 0, 1, 2, 3 or4 distinct positions of `q_hat`, exactly once. For each candidate q value, recompute tag36 under the queried owner and profile. Its 68-bit semantic-field distance is

```
popcount(candidate_q XOR q_hat) + popcount(candidate_tag XOR tag_hat).
```

Retain candidates at distance <=4. Read q if and only if **exactly one** semantic codeword qualifies; then read h as `masked_h_hat XOR mask32(decoded_q)`. The h field does not participate in the q read decision. Zero q candidates means `PAYLOAD_NO_CODEWORD`; two or more means `PAYLOAD_AMBIGUOUS`. Both are observed no-read outcomes, not missing detector results. Malformed/nonfinite decoder output, execution failure or missing artifact instead means missing/error and must never be recoded as a negative.

There are `sum(comb(32,i), i=0..4) = 41,449` candidate q words per owner query. For uniqueness, finding a candidate does not permit early acceptance; one may stop after the second candidate only to reject. Cache HMAC context state and reuse each successful owner decode across binding-mode diagnostics. Do not search q values derived from the suspect, a donor candidate list, or the original q: the full fixed search is the only authorized decoder. Do not choose nearest among several valid words or relax the radius for a difficult image.

For q+tag68, radius3 would require5,489 q candidates, radius4 requires41,449, and radius5 requires242,825. Under a uniform independent68-bit null, the radius4 union-of-balls bound is `sum(comb(68,i),i=0..4)/2**36 = 866848/2**36`, about1.26e-5 per owner query. Radius5 gives11290976/2**36, about1.64e-4, exceeding the retained1e-4 descriptive target. These are elementary code-volume bounds under that explicitly idealized uniform-bit null; they are not bounds for correlated neural decoder outputs on photographs, a public-key adaptive attacker, or the whole study. A secret ideal-PRF interpretation would require an additional access assumption absent here. Report empirical C0/wrong-owner events and source clustering regardless. No rare-error guarantee follows from sixteen donors.

Choose radius4 because it is the largest full Hamming radius satisfying that idealized per-query target with36 redundancy bits, at bounded cost. Reader cost is not measured here and must enter rehearsal. If radius4 fails, retain that result; any later decoding redesign is a separately named development method.

An earlier proposed q32+h32+joint-tag36 code with radius3 is explicitly **rejected before outputs**. It made semantic C/J fail whenever h accumulated errors, whereas F5 semantic C/J does not depend on its fragile h carrier. That comparison could manufacture an F6 advantage from payload architecture. The final separate q code gives the VINE baseline semantic survival independent of h. Adding an independent tag for h would exceed the100-bit budget unless the q code lost redundancy; the unchanged h content-radius test supplies its stated consistency check instead.

VINE-R's known-message threshold69/100 can tolerate31 errors because the evaluator supplies a full candidate message. It is a hypothesis test, not blind recovery of an arbitrary q/h message. A32-data/68-total semantic code cannot uniquely correct every31-error pattern: the Hamming sphere-packing requirement exceeds the available36 redundancy bits. Treating69 matching bits as successful VINE-B decoding would leak the evaluator target. Presence success therefore does not imply content-payload success. Report raw full-message accuracy, raw q accuracy, masked-h accuracy, tag accuracy,0/1/multiple qualifying q codewords, semantic correction distance, and exact q/unmasked-h after decoding separately. This limitation is part of the baseline's honest capacity tradeoff, not evidence that the published VINE carrier itself failed its presence task.

## Operational content decision

The operational API receives only suspect RGB8, claimed owner, retained profile/key/config and the fixed radius. It may reuse a previously computed raw VINE bit vector from that same suspect. It recomputes suspect seven-view features, q_now and h_now by the retained F5/v5 helpers.

If payload decoding rejects, both semantic and instance have found=false, read=false, content_match=false, decoded_code=null; their status is null and the outcome is `base._decide(False,None,False,None)`. Preserve raw tentative bits separately; they are not decoded codes for Q/H.

If q decoding uniquely succeeds, set both found=true and read=true. Semantic decoded_code is corrected q; instance decoded_code is the unmasked **uncorrected** observed h field. Set semantic corrected_distance to `base._distance(q,q_now)`, instance corrected_distance to literal `base._distance(h,h_now)`, semantic decoding_error_rate to0 and instance decoding_error_rate to null. For semantic soft likelihood, zero is the residual-error model conditional on a successfully decoded q codeword, not a measured neural bit-error estimate or a claim that miscorrection is impossible. For h, null records no calibrated error model: no error-rate subtraction occurs and its literal Hamming distance remains. The q codeword may be wrong and h bits may be corrupted, which Q/H and negative controls can reveal. Do not feed correction_distance/68 as a semantic code error rate after correcting q. Label instance read/found `conditional_raw_h_field_after_q_read`; there is no independently calibrated h-presence test or h error correction.

For combined mode, use exactly the same retained content decision below. Its explicit mode variables show the retained rule being reused; VINE-B Stage S evaluates combined mode only.

```
check_semantic = mode in ("combined", "semantic_only")
check_instance = mode in ("combined", "perceptual_only")
s_status, soft_distance = f5._semantic_status(
    semantic, suspect_features, key, config, semantic_limits,
    check_semantic, "soft")
i_status = max(
    base._content_status(instance_corrected_distance,
                         instance_radius, instance_mismatch_distance,
                         check_instance),
    s_status, key=base._STATUS_RANK.get)
outcome, proposal_state = base._decide(True,s_status,True,i_status)
```

As in F5, content_match means found and status rank zero; `unchecked` is rank zero in diagnostic modes. Combined mode alone is operational. Use the same output schema and endpoint extractor as internal readers, while identifying this as the VINE-B carrier with reused F5 content decisions. Never populate invented F5 carrier scores, thresholds or Gaussian false-positive bounds; use null/inapplicable plus explicit payload distance diagnostics instead.

This preserves the **content predicate conditional on the decoded fields**, with zero error correction for the raw h distance. It does not preserve the entire F5 detector: F5 chooses its instance pattern using q_now or decoded q depending on semantic status, has carrier-specific score thresholds and possible recomputed-only reads, and can lose h while retaining q. VINE-B has no recomputed-only route; it can retain q while h becomes wrong, but its h-presence flag is conditional on q rather than independently tested. Thus `semantic_only` as an outcome no longer identifies regeneration in this arm. Robust h may increase F after regeneration if the suspect's h is still within radius; corrupted h may cause content_mismatch even while C survives. Report both without claiming equivalent tamper-state semantics. The prototype's inherited `authentic` proposal_state is merely its operational state label, not authentication or lawful ownership.

## Endpoints and negative queries

All C/Q/J/H/D/F/A endpoints apply with the stated conditional h-read convention. For the intended owner with an available evaluator reference: C is read and semantic content match; Q is exact q and read; J is Q and semantic content match; H is exact unmasked h and conditional read; D is Q and H; F is both_match; A is either channel found. Also report full100 exact raw recovery and exact q+h after semantic correction and h unmasking. Do not call h corrected. The same C/J definitions as F6 make the primary comparison possible; common definitions do not make their physical carriers identical.

Wrong-owner calls rerun the bounded decoder using beta in the tag context, on the same raw100 bits. They must not compare an alpha message against a random beta message. C0 calls use the suspect and each specified owner with no source payload. Original q/h fields are unavailable for C0 and wrong-owner exact-reference endpoints, rather than observed exact-recovery failures; C/F/A still apply. In T4/T5, the donor q/h remain evaluator references only.

Run the complete existing clean/native/T4/T5/secondary grid for `vine-b`, including both owner calls. VINE-B T4/T5 use combined mode only, as requested for R2; the existing internal arms retain their four diagnostic modes. Apply the same combined-mode D AND F false-instance predicate, recipient quality eligibility, genuine-component caveat and operational-distinctness labels. Require the same observed-negative and missing-negative accounting as for F6 when qualifying VINE-B as an article comparator. Delivery Q/D and delivery-conditioned acceptance must remain visible: low carrier delivery cannot masquerade as strong binding.

The public-derived profile permits anyone with the implementation and carrier encoder to produce a valid newly marked claim. The proposed experiment tests content consistency under the frozen T3/T4/T5 manipulations, not identity authentication, anti-re-embedding security, or proof of rights. This is a common limitation of the comparison, not a new untested attack to add to Stage S.

## WAM-B decision

Do not add WAM-B to this screen. Its retained 32-bit message cannot independently carry the full q32, h32 and any nonzero check redundancy. q-only consumes all 32 bits and drops the instance check and claimed-owner validation; truncating q/h changes the F5 rule; hashing q/h destroys the fields required by the soft semantic check; searching evaluator originals leaks side information. Repeated embedding, tiling, changing the model capacity or an external registry would create a new method with altered distortion, task or side information. Keep WAM as the required published presence comparator and state the payload-capacity incompatibility. A separately designed semantic-only WAM arm would not answer the combined-mode question and is not necessary here.

## Pre-output article decision, separate from the unchanged thesis gate

Do not change any F6 thesis gate, clean threshold, ablation gain or F5 comparison. Adding VINE-B cannot rescue a failed F6 thesis gate. The following is a **development-screen recommendation for choosing a fresh-confirmation claim**, not a significance test, TIFS-readiness verdict or authorization for held-out work.

Let `L_a(e,c)` and `U_a(e,c)` be conservative lower and upper source-majority counts for arm a, endpoint e in {C,J}, and the four existing cells. Define directed noninferiority `NI(a,b)` as `L_a(e,c) - U_b(e,c) >= -1` in every one of these eight comparisons. Require paired clean LPIPS median(a-b)<=.005 and paired clean PSNR median(a-b)>=-1 dB for directed quality noninferiority `QNI(a,b)`. All sixteen paired clean metrics must exist; no complete-case median is allowed.

A viable VINE-B arm has all sixteen strict-clean quality passes, clean F>=15/16, at least12/16 C and J majorities in all four cells, complete required specificity evidence with zero applicable C0/wrong-owner C/F and zero qualifying combined D AND F threat events, and a complete required secondary inventory. Missing human operational-distinctness labels remain a separate `BINDING_GENERALIZATION_UNRESOLVED` flag for both arms; this numerical qualification cannot support a false-attribution or semantic-collision security claim without those labels. VINE-B does not receive F6's ablation-gain requirements. Viability gates a VINE-B dominance/protocol claim, not whether a fully observed but weak VINE-B can be compared with F6.

For an F6 article advantage, require the unchanged F6 numerical thesis GO including its numerical security gates, complete paired evidence and full required inventories of both bound arms, `NI(F6,VINE-B)` and `QNI(F6,VINE-B)`, plus at least one of two predeclared advantages. VINE-B quality/security failures must be reported separately; they are not an automatic F6 advantage, but do not make its complete measurements disappear.

1. **T3 advantage:** in at least one foreign cell, both C and J have `L_F6-U_VINE-B >= 3`.
2. **Clean-quality advantage:** paired median LPIPS(F6-VINE-B)<=-.002 **and** paired median PSNR(F6-VINE-B)>=+1 dB. Both are required; one favorable quality metric cannot compensate for another.

These are two exploratory selection routes fixed before data. They are not two independent confirmatory discoveries; Stage C must freeze the surviving route and a multiplicity-controlled hypothesis family. T4/T5 and reader cost are reported, but cannot become a post-hoc alternative winning dimension in this screen.

For VINE-B numerical dominance, require its viability, complete paired evidence, `NI(VINE-B,F6)` and `QNI(VINE-B,F6)`, and the analogous strict T3 or clean-quality advantage in VINE-B's direction. The word dominance here is this frozen practical-margin screen, not exact Pareto dominance or statistical superiority. If neither direction has a strict advantage and both satisfy NI/QNI, report numerical parity. Any contradictory automatic flags indicate a rule/integration error to resolve from the frozen definitions, not select the favorable label.

The machine-readable verdict names are authoritative in `stage-s/frozen-config.json` under `article_decision.verdicts`; the following table aligns with that vocabulary. More specific quality/security/binding descriptions are separate flags, not substitutes for those verdicts:

| Observed state | Article disposition |
|---|---|
| F6 thesis GO and F6 article advantage | `F6_GO_ARTICLE_CONDITIONAL_GO`; propose confirmation of the fixed winning route, with novelty and human-binding caveats |
| F6 thesis GO and VINE-B numerical dominance | `F6_GO_VINE_B_DOMINATES_ARTICLE_NO_GO`; root's R2-1 assessment finds generic bound-carrier novelty pre-empted, so report the additional `BOUND_CARRIER_ONLY_NOT_NOVEL` flag rather than automatic article rescue |
| F6 thesis GO, numerical parity | `F6_GO_NO_ARTICLE_EDGE`; F6 feasibility alone is insufficient for its article claim |
| F6 thesis GO, mixed tradeoffs or neither strict rule | `F6_GO_NO_ARTICLE_EDGE` with tradeoff details; do not select a new winning metric |
| F6 fails and viable VINE-B passes | `F6_KILL_VINE_B_VIABLE_NOT_NOVEL`; F6 thesis failure stays, and the already-preempted generic protocol is not an article contribution |
| Both fail their numerical scientific criteria | `BOTH_FAIL` |
| VINE-B violates strict clean quality | retain F6 thesis verdict plus `VINE_B_QUALITY_INELIGIBLE`; quality tradeoff is visible, not an automatic F6 article GO |
| VINE-B has a qualifying negative event | retain F6 thesis verdict plus `VINE_B_SECURITY_SCREEN_FAIL`; it cannot dominate, and its failure does not prove rare-error superiority for F6 |
| Required VINE-B or paired evidence missing | retain any established F6 thesis result plus article `INCOMPLETE`; never dominance, parity or article GO from incomplete observations |
| Resource gate fails | `RESOURCE_STOP` alongside scientific/missingness flags; no reduced arm/grid after outcomes |

Keep novelty (`NOT_ESTABLISHED`, `PREEMPTED`, or bounded candidate novelty), human-binding status, human quality status, observed-negative completeness, and numerical screen disposition as separate fields. A prior-art pre-emption can veto an article route even when the numerical screen passes. A public check-tag construction by itself is not a novelty claim.

## Integration and review checklist

One new marked arm makes the screen 16*9*4*3=1,728 native units, 128 marked clean plus16 C0, 16*9*8=1,152 secondary units and16*9*7=1,008 threat units. Rehearsal has216 native,16 marked clean plus2 C0,144 secondary and126 threat units. The number of F6-family optimization marks remains48 screen plus6 rehearsal. Update every inventory/forecast loop, dispatch choice and expected-reader coverage, not only headline counts. Keep15 hours as the cap; VINE-B writer time, blind decoder work for both owners, semantic/hash work, reads, metrics, storage and all new units must be included in the measured rehearsal forecast. No local timing estimate is licensed as measurement.

The pure-logic decoder should be independently testable without importing the scientific runtime. Tests should cover message layout/field bounds, owner/domain sensitivity, deterministic payload generation, all radius-boundary logic, tag-only and q-only errors, a constructed ambiguous codebook through an injectable check function, malformed bits, and absence of donor references from operational APIs. Flipping all32 h-field bits must leave q decoding unchanged while inverting recovered h. Content-rule adapters need fixed-call tests for combined mode, the semantic-status maximum in instance status, literal uncorrected h distance, and read failure vs execution missingness; existing internal-arm mode tests remain unchanged. Do not import retained ML modules into laptop pure-logic tests. Server rehearsal must test actual helpers, dimensions, raw decoder extraction, saved RGB8 reads and runtime memory/cost before scientific output collection.
