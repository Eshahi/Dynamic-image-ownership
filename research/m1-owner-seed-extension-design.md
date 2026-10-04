# Public-owner extension and explicit seed semantics for A-C

Version `m1-owner-seed-extension-design-v1`, 2026-10-04. Method decision by gpt-6-astra/xhigh; prospective interface amendment conditional on selection of `m1-terminal-continuous-e2e-v1`. This file authorizes no held-out access and changes no executable, protected acceptance record, threshold or retained result. It must appear in the final M1 amendment summary and candidate specification before the user's single confirmatory decision.

## Decision

Extend the exact accepted public-owner strings from the four development fixtures to their union with the sixteen A4 identities. Preserve **every byte of the existing map domain and every numeric operation for the four old owners**. Give the input-domain extension its own interface version; do not bump the string currently used inside the map hash. The existing development roster and its condition inventory remain four-owner experiments.

For this deterministic A-C candidate, the A4 per-source uint64 is **schedule metadata, not a consumed scientific embedding seed**. Keep it exact and reproducible, but never claim that it generated noise or changed a latent. Use the already specified fixed execution seed0 at each fresh initialization/embedding phase, and restore saved RNG on resume. T3 attack seeds remain separately consumed attack parameters. This explicitly amends A4's seed-consumption requirement for this candidate; it is not compliance with that older requirement by silently ignoring an argument.

## Inspected compatibility boundary

The current [core](../scripts/m1_blind_noise_core.py) has `VERSION="m1-blind-noise-template-v1"`, and `_prefix` includes `frame(VERSION)`. `_owner` accepts only `qim-pilot-owner-alpha`, `qim-pilot-owner-beta`, `qim-pilot-owner-gamma` and `qim-pilot-owner-delta`; its cache capacity is four. The core's last modifying commit is `fe02a466b5ba33f7a9fd7d5a4df0080098defaf2`, and its inspected file SHA256 is `df3e7140ee910519a1f57d8ea564d55636671c7404ca574fd40695e8514bccef`. Pin this source as the executable legacy reference for compatibility tests before editing it. A candidate implementation must not regenerate its own expected answers from the new code.

The [A4 acceptance record](acceptance.md), section “Study primary outcome and decision,” specifies exactly `thesis:owner:00` through `thesis:owner:15`. [a4_protocol_reference.py](../scripts/a4_protocol_reference.py) derives the enrolled index and next-index wrong owner from the source UID, and separately derives an exact uint64 from `a4-seed-v1`. A4 additionally requires `embedding.noise_seed` and `embed_existing(..., seed)` to equal that uint64 and describes its use in A5's base-noise construction. A-C instead uses posterior mode, deterministic latent optimization, public owner-derived maps and no random base-noise draw. It cannot honestly inherit that consumption claim.

The [current narrow confirmatory draft](m1-confirmatory-draft.md) and [interface](m1-confirmatory-interface.md) still describe the A4 embedding seed, while the new [end-to-end design](m1-end-to-end-initialization-design.md) explicitly seeds fresh execution phases with0. Reconcile these candidate-facing documents and worker metadata under this amendment before final freeze. Preserve the historical A4 record and source plan unchanged. Do not open held-out data to resolve this interface issue.

## Exact domain-preserving owner extension

The mechanical extension is deliberately small:

| Name | Frozen meaning |
|---|---|
| `MAP_VERSION` | Literal `m1-blind-noise-template-v1`; the domain inside hashes, unchanged |
| `VERSION` | Retain the same legacy literal for compatibility; do not reinterpret it as the owner-interface version |
| `OWNER_INTERFACE_VERSION` | New literal `m1-public-owner-interface-v1`; metadata only, never included in a map prefix |
| `OWNERS` | Keep the original four-owner tuple, in its original order, so old imports/manifests/gates retain their inventory |
| `A4_OWNERS` | Tuple `thesis:owner:00`, ..., `thesis:owner:15` in increasing two-digit decimal order |
| `ACCEPTED_OWNERS` | Exact union `OWNERS + A4_OWNERS`, twenty distinct strings |

`_owner` checks membership in `ACCEPTED_OWNERS`, without stripping, lowercasing, Unicode normalization, aliases, implicit string conversion or modulo mapping of an unknown identity. Empty, non-string, non-ASCII lookalike, unpadded `thesis:owner:0`, uppercase, whitespace-suffixed, `thesis:owner:16` and unknown owner inputs remain invalid. These are synthetic public identifiers, never a claim about real people. Accepting this fixed twenty-string union does not make an arbitrary user-supplied owner namespace supported.

Preserve `frame(s)=uint32be(len(UTF8(s))) || UTF8(s)` and:

`prefix(domain,owner) = frame("m1-blind-noise-template-v1") || frame(domain) || frame(owner)`.

Keep the six literal domains `coordinates`, `semantic-columns`, `instance-pre-signs`, `instance-rows`, `semantic-row-signs`, `instance-row-signs`; SHA256 sorting with integer tie-break; SHAKE256 MSB-first signs; array ordering/dtypes; FWHT order/normalization; tensor-product hash-bit order; SRHT row selection/normalization; threshold4 inclusive; denominator/invalid handling; and state classification. No source UID, schedule seed, interface version, roster index, roster size or secret is added to these prefixes. Each new owner gets the **same published map construction applied to its own exact owner bytes**. Do not map the sixteen owners onto the four fixture owners or intentionally choose maps with better geometry.

The owner-map cache may hold all twenty immutable maps. Changing its capacity from4 to20 is explicitly an execution-only change; cache eviction/reconstruction must not affect values. Cache no `E`, `H`, template, image or score under an owner alone. Do not rewrite the algebra into a second independently evolving implementation solely to bypass validation. Prefer this small validated extension plus separate interface metadata; if an implementation reorganizes functions, exact parity remains mandatory.

The scientific worker selects `A4_OWNERS` explicitly and validates source-UID-derived enrolled/wrong identities against the unchanged A4 reference. A single-claim detector still accepts one candidate owner. Supporting sixteen possible claims does not mean querying all sixteen in the primary experiment: primary C2 remains the exactly next roster index, `K=1`. Existing four-owner development controls stay recorded as such. Retain same-roster source/recipient flags in T4/T5; the same public owner on two images is not a wrong-owner contrast.

## Mandatory CPU compatibility and geometry evidence

Create a new, versioned CPU-only extension audit with a committed manifest and unique output receipt. No models, images, image paths, held-out schedule members, GPU initialization or descriptor extraction are needed. Use the pinned NumPy/Python runtime and record both old/new source hashes. The immutable old core may be a small test fixture copied verbatim from the pinned Git object and SHA-verified; do not depend on an unpinned installed module or mutate the old module's globals to make tests pass.

Bound the audit at600 seconds,2GiB process RAM,64MiB retained output and USD0. Store fixture definitions/values, raw scalar matrices and canonical array digests instead of duplicating every full template array. A resource interruption retains completed/missing cells and is operational incompleteness, not a failed owner or grounds to shorten the fixed inventory. This is a CPU software/geometry check, not another image experiment.

**Exact old-domain parity.** Evaluate all four old owners on the existing32 synthetic descriptor pairs, rather than assigning only one owner per pair. Generate pairs with `Generator(PCG64(0))`: per pair, draw two512-dimensional standard-normal vectors, normalize each, then draw two uint32 hashes using the existing reference's uint64 sampling convention. Generate32 independent latent fixtures from a separate `Generator(PCG64(1))`, length16384 each. The separate generator keeps the existing descriptor fixture sequence unchanged.

For all128 owner/pair cells, compare old and extended arrays `coords_s`, `coords_i`, `v_s`, `v_i`, `r_s`, `r_i`, `T` with exact shape/dtype/array equality. Compare every projection ancillary, every `projection_diagnostic` field, and `scores` raw values, denominators, flags/state on the same latent exactly. Repeat after clearing caches and after mixed calls to every new owner to catch mutable-cache/order errors. Retain canonical array/value digests and a mismatch ledger. A changed map, score or projection float is a failed compatibility test, not acceptable numerical drift.

Run the prior core tests unchanged except the explicitly documented cache-capacity assertion. Preserve FWHT/reference arithmetic, zero/nonfinite rejection, API signatures and threshold-boundary tests. Add exact classification fixtures at4, the adjacent representable floats below/above4, invalid and instance-only cases. For previously invalid strings that remain invalid, exception/result category and null/invalid semantics must match; explanatory error text may now describe twenty accepted strings. The sixteen newly valid strings are the intentional domain change, not an old-output regression. Existing production `template(E,H,owner)`, `scores(zflat,E,H,owner)` and `projection_diagnostic(...)` signatures keep no source/enrollment/seed arguments.

**Fixed sixteen-owner synthetic audit.** Reuse the same32 descriptor pairs and latent fixtures, applying every one of the16 new owners. Do not choose a subset after inspection. Save these bounded outputs:

- 512 owner/pair projection diagnostics, including actual norm errors, normalized kernel error, exact tensor-product kernel, conditional variances and deterministic normalization-error bound. Verify semantic cosine preservation, disjoint coordinate partition, finite/unit template norms, RMS1, valid hash order and the independent formula for each variance. Use the existing algebraic test tolerance of about1e-12 where comparing mathematically equivalent expressions with different floating summation order; this tolerance does **not** relax exact old/new execution parity.
- A32 x16 x16 synthetic alignment matrix: for fixture `j`, construct latent `T(E_j,H_j,donor_owner)` and score it against every candidate owner using the same `E_j,H_j`. This yields8192 two-score cells:512 diagonal and7680 cross-owner. Retain every score/state, diagonal score range, each row's maximum cross-owner scores, and any cross-owner score reaching4. All diagonal fixtures must be finite and `both_match`; exact aliasing of distinct owners' maps/templates is a defect requiring diagnosis.
- A32 x16 independent synthetic-null matrix using the separately generated latent fixtures, giving512 two-score queries. Report each channel's threshold exceedances, joint states, invalids, per-owner extrema and any unusual alignment. Do not require zero false positives as a new empirical calibration gate, do not search alternative owners/seeds, and do not adjust threshold4. A nonzero finite tail event is a measured synthetic result; implementation aliasing, invalid geometry, an incorrect score or a provenance mismatch is a technical failure.

Also verify all twenty owners have distinct full map digests and validate prefix framing directly against independent `hashlib` expressions for each domain. Collision absence here is a finite implementation observation, not a cryptographic theorem. A surprising cross-owner/null pattern receives a cheap algebraic/cache/reference diagnosis; it cannot be cured by deleting an owner or relabeling the off-diagonal cells.

If retained development arrays `E,H,z` are available through already admitted development receipts, run the old and extended core against those same arrays for all four old owners and require exact scores/decisions. This cheap CPU replay directly ties compatibility to observed model outputs without re-encoding images or rerunning optimization. It is optional when the arrays do not exist; the exhaustive changed-code review plus exact synthetic parity remains the minimum, and absence of a real-array replay is stated. Any subsequent change to reader/model/embedding math is outside this extension and cannot use this compatibility argument to avoid its own validation.

These tests support code/domain extension and preservation of previous four-owner results. They do **not** establish sixteen-owner image quality, empirical photograph FPR or equal optimization difficulty across owners. Development efficacy remains measured for the fixture embedding owner; confirmatory results under the fixed A4 owner schedule will estimate a different declared owner mix. This limitation is transparent and does not require rerunning the complete twelve-source development/attack program merely to change an allowed input set. Candidate-identical synthetic worker rehearsals must exercise all16 owner strings, owner propagation into both embedding/readout, and next-index wraparound, without selecting a favorable owner. A byte-changing map/algebra regression, rather than the input extension alone, would invalidate that no-rerun conclusion.

## Seed amendment and actual consumption

The scientific method is `J = Embed_AC(I, OwnerID; frozen model/configuration)`. Its source-dependent initialization is posterior mode followed by200 fixed MSE updates; embedding uses100 fixed Adam updates. Public template pseudo-randomness comes from the owner/domain hash construction above, not from a per-image noise seed. There is no stochastic augmentation, posterior sampling, random start, diffusion sampling or seed search in clean A-C embedding. A-C's fixed seed0 is execution/recovery hygiene, not a source of independent scientific repetitions.

Preserve the unchanged A4 schedule function on a validated source UID:

`D(tag,u)=SHA256(ASCII(tag) || 0x00 || uint32be(len(u)) || u)`;

enrolled index `uint64be(D("a4-owner-v1",u)[:8]) mod16`, wrong index `(index+1) mod16`, and schedule uint64 `uint64be(D("a4-seed-v1",u)[:8])`. UID NFC/UTF8/length and duplicate validation remain upstream. Do not change or resample actual source UIDs to get an owner. Owner derivation is consumed by A-C; the seed derivation is retained for schedule compatibility and auditing but is not a method input.

Every resolved candidate/condition receipt distinguishes:

| Field | Exact meaning for A-C e2e |
|---|---|
| `owner_interface_version` | `m1-public-owner-interface-v1` |
| `map_version` | `m1-blind-noise-template-v1` |
| `owner`, `wrong_owner` | Actual A4-derived identities; wrong owner is next modulo16 |
| `seed_uint64_decimal`, `seed_uint64_hex` | Unchanged A4 metadata: canonical decimal string and exactly16 lowercase hex digits |
| `schedule_seed_role` | `metadata_only_not_consumed_by_ac_e2e` |
| `scientific_embedding_seed` | JSON null, because no stochastic scientific embedding seed exists |
| `execution_phase_seed` | Integer0 for every fresh200-step initialization and fresh100-step embedding phase |
| `execution_rng_policy` | `fresh_phase_zero_resume_restores_saved_rng` |
| `attack_seed` | null for clean/deterministic VAE; actual integer0,1 or2 for the corresponding T3 diffusion attack |

The existing schedule/unit field name `seed_uint64_hex` may remain for schema compatibility, but its role is explicit in the candidate policy and results. Never fill `embedding.noise_seed` with the A4 value, pass it as a scientifically consumed `seed` argument, and then ignore it silently. The new candidate adapter should have no stochastic-seed parameter; if a generic worker receives the schedule field, it separates and records metadata before invoking the method. A generic schema requiring an A5 noise-seed field needs an explicit candidate-specific extension, not a fabricated consumption receipt. Final official manifests list actual consumed execution/attack seeds with their roles; retained A4 schedule seeds are separately identified as informational. A wrapper's synthetic image-generation seed is also separate from the candidate's embedding semantics.

Use Python integers or exact strings throughout validation/transport; no JavaScript-number conversion, float parsing, signed64 narrowing, modulo2^32 truncation or `abs` conversion. Verify `int(decimal)==int(hex,16)` within[0,2^64-1] and canonical formatting. Preserve leading hex zeroes. The documentary parity vector `coco:000000000001` -> owner09, wrong10, decimal`4369173439443558334`, hex`3ca26c18241adfbe` is a **synthetic string test only**, not permission to resolve/read that source.

Mandatory seed/interface tests cover0,1,2^32-1,2^32,2^53-1,2^53,2^63,2^64-1; malformed/noncanonical decimal/hex, booleans/floats, overflow and disagreement; A4 reference parity and15->00 wrong-owner wraparound; explicit candidate invocation without schedule seed; fixed phase seed0; and restoration instead of reseeding on resume. A spy or analytic CPU codec can prove the metadata field never reaches method inputs and that source/owner/configuration propagation is unchanged. It must not claim that different GPU RNG seeds yield identical scientific trajectories: this design never runs the real method under different phase seeds. If code inspection discovers a genuine random draw inside a scientific phase, fail this consumption assertion and resolve it prospectively; do not hide it as “irrelevant bookkeeping.”

Do not interpret a repeated deterministic output or many public owners as extra independent source observations. Clean A-C gets one fixed output for a given source/owner/configuration in the pinned repeatable execution environment. T3 deliberately consumes its own declared random seeds and retains paired source clustering. Native GS/generated baselines retain their own real noise-seed/nonce semantics and are not rewritten by this A-C amendment.

## Freeze, evidence reuse and milestone disclosure

Keep current development execution files unchanged while live runs are in progress. Implement and test the extension as a later committed scientific-core revision before final worker freeze; record the old/new hashes and compatibility receipt. Existing four-owner numerical results may be cited under that proven compatible extension, with original run provenance retained. No full development rerun is required if the only changes are exact accepted-owner validation, cache capacity and metadata, all parity checks pass, and the called numeric/model/source operations are unchanged. The separately required deterministic initializer/end-to-end validation remains mandatory; this interface amendment does not waive it.

Before confirmatory readiness, the candidate spec, method adapter, narrow draft, worker contract/result schema and final manifest must agree on: sixteen-owner schedule but K=1 wrong-owner testing; preserved map domain; continuous thresholds/state rule; deterministic200+100 method; seed metadata versus execution seed versus attack seed; actual model/operator side information; and the limits of four-owner development efficacy. Update only candidate-facing amendment documents/implementation, retaining protected historical records unchanged. No held-out values are needed to do this.

The M1 package should disclose in plain terms: “A-C uses the A4 public owner schedule. Its embedding is deterministic and does not consume the A4 noise-seed schedule; those uint64 values remain audit metadata. We retained fixed execution seed0 and separately declared attack seeds. The original four public maps are bit-identical, and the sixteen-owner extension passed the documented CPU compatibility and synthetic geometry checks.” The final clause is conditional until the actual receipt exists; never present the planned tests as passed. The user can accept this transparent method amendment in the same milestone decision as the rest of the frozen confirmatory package.

Finally, supporting sixteen public owners is not authentication or an adaptive-forgery defense. Under the **ideal random-map, fixed-image independent-of-claim-signs** argument, one channel's tail at4 is bounded by `exp(-8)`; a union over both channels of16 owners is at most`32*exp(-8)`, about.010735. This is not a new calibrated FPR and is not the K=1 joint-primary event. Native content correlations, fixed public maps, selected/adaptively optimized images, finite development samples and public re-embedding prevent treating that ideal bound as observed security. Report the actual scheduled K=1 empirical strata separately; never adjust the threshold or select an owner to make a many-owner synthetic count look better.
