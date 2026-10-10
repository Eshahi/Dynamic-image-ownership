# Independent discovery-package review

2026-10-10. Reviewer: Codex independent agent `journal_discovery_review`, separate from the probe/report author. Scope: changes after `fa27d08` through `02cfd22`, plus the supplied discovery report/statistics, baseline feasibility and evolving roadmap working files. This is a bounded scientific review, not human acceptance, a lifecycle transition, confirmation of publication readiness, or a new experiment.

**Verdict: ACCEPT for exploratory reporting and the proposed bounded development routing, with non-blocking clarifications below.** No blocking error was found in D1–D6 or the reported primary counts. No scientific rerun is required by this review. The two probes supply a negative generalization screen and a narrow physical-delivery binding result; neither establishes journal qualification or a security guarantee.

## Evidence inspected and limits

Read authoritative MAIN STATE once; inspected `journal_vae_probe.py`, `journal_binding_probe.py`, `journal_probe_analysis.py`, their prospective protocols and design decision, relevant existing detector/fallback code, the two original MAIN run manifests and retained JSON rows, and the supplied analysis/report/roadmap/feasibility documents. Original runs are `20261010-0858-journal-binding` at `1e25f5f` and `20261010-0903-journal-vae` at `02cfd22`. Both have committed code and run.json, as required for development. Binding implementation is unchanged between its run commit and the reviewed HEAD; the subsequent VAE change adds the nonidentical-weight check. Analysis code is committed at `d6eafdb`.

Independently counted retained row identities and selected endpoint flags; did not replay image generation, floating-point metrics, or artifact hashes. The actual inventories contain 144/144 unique VAE observations and 31/31 unique binding observations, all status `ok`. Inspected six public donor deliveries and the authorization demonstration directly. No raw held-out data, protected-file edit, download, external communication or new run was used. This single requested file substitutes for the skill's multi-file audit packaging under the task's bounded review instruction.

The baseline review checks the proposed ordering and comparison contract, not every third-party implementation fact. The pinned [WAM README](https://raw.githubusercontent.com/facebookresearch/watermark-anything/2c08af04d037d5667c02f6ddebbda9ff04581c3e/README.md) independently supports the SA-1B MIT checkpoint, its distinction from the paper's COCO checkpoint, 32-bit examples and predicted-mask decoding. The pinned [SDXL VAE card](https://huggingface.co/stabilityai/sdxl-vae/blob/6f5909a7e596173e25d4e97b07fd19cdf9611c76/README.md) supports the same architecture with a changed training recipe and MIT declaration. Neither source proves unrelated training data. Laptop feasibility remains an engineering inference until the proposed smoke run.

## Claim classification

| Claim | Classification | Reason and boundary |
|---|---|---|
| D1: planned observations completed | Verified | Independent identity counts agree with run manifests and analysis. The fixed source/method/control/condition product and six fixed pair arms plus one demonstration account for the stated totals. No failed observations are hidden. |
| D2: F5 12/12 SD1.5 and 10/12 SDXL; v5 12/12 both | Verified | Recounted correct-owner `found AND read AND content_match` agrees. Ten shared SDXL successes and two v5-only successes are descriptive paired outcomes, not evidence of population superiority. |
| D3: two F5 failures are unread rather than binding-rejected | Verified, operational scope | Sources 4795 and 6012 have `found=true`, `read=false`, decoded scores 7.86278/6.74483 below 8.25933, and recomputed scores 6.98957/5.78616 above 4.98203. The returned match is the documented recomputation fallback. The measured LPIPS values satisfy both proxies; human admissibility is absent. This localizes the failed decision stage, not the physical cause. |
| D4: five exact donor q/h deliveries, all rejected | Verified | All five have read flags, zero q/h bit errors, positive content-disabled read-presence and combined `content_mismatch`. Both separately inspected content predicates reject. Sixth attempt has one q-bit error and exact h, and is correctly excluded from the strict subset. Residual arms do not establish binding efficacy because exact delivery is absent. |
| D5: one public recipient construction accepted without authorization | Verified | The fixed first pair uses recipient-recomputed q/h with the public profile; its saved-pixel detector call yields exact readable codes and `both_match`. Construction uses no secret or enrollment authorization. This is an existence counterexample to unrestricted public-profile unforgeability, not a measured default T4 attack rate or legal ownership finding. |
| D6: broad conclusions remain unestablished | Verified | Repeated sources, six selected pairs, absent full independent diffusion, absent matched external execution and coupled component modes support the stated limits. No low-FPR, isolated carrier, synergistic binding or cryptographic claim follows. |

No claim in this bounded inventory was classified conflicting, unsupported or unverifiable. Broader claims explicitly disclaimed in D6 remain unsupported by these probes.

## Blocking findings

None for publishing this package internally as exploratory development evidence or proceeding with the stated bounded next steps. This verdict does not authorize a held-out run or resolve pending human M2 acceptance.

## Non-blocking findings and concrete corrections

1. **Read failure is an endpoint diagnosis, not a carrier mechanism.** The report correctly avoids binding rejection as the observed failure, but a reader could overinterpret the decoding diagnosis as proof of carrier destruction. Add: “This identifies the decision stage; it does not distinguish carrier attenuation, host interference, or changed feature geometry.” The proposed fixed-payload before/after score and bit-error diagnosis is appropriate. The intact SD1.5 control makes a generic preprocessing explanation less supported; it does not eliminate an SDXL-specific implementation issue by logical implication.

2. **Preserve a future generalization test after using SDXL to improve embedding.** This probe is a transfer test for frozen F5. Once its outcomes, transformations or gradients inform a new objective, SDXL is a development target. Add to the amendment: “Report SDXL as a seen development transformation; use separately reserved sources for image generalization and an untouched transformation/backbone for any claim of unseen-model transfer.” New images alone do not restore unseen-model status. This does not prevent the proposed six-configuration development round.

3. **Specify the delivery study's attempt budget before expansion.** Five exact deliveries are a valid conditional mechanism subset, not five random population samples. The report correctly labels the 45.07% bound illustrative and does not pool M2. Before targeting 100 exact pairs, freeze an independent pair-selection rule, total attempt cap and stopping rule; report exact delivery/all attempts and acceptance/all attempts alongside conditional acceptance. Never replace failed deliveries with favorable pairs without retaining them. A 100-delivery mechanism study remains different from the separate simultaneous <=1% error target.

4. **Keep native mode results separate from component causality.** `q_bound` depends on semantic status and native instance status propagates semantic rejection. The stored own-h predicate and disabled read-presence controls therefore support rejection of physically delivered fixed codes, but not independent factor interventions or benefit of combining checks. Existing caveats are correct. In the next component study explicitly define which extracted codes and q-conditioned instance projections stay fixed, and include cases on which component decisions differ; otherwise additional all-reject pairs cannot establish synergy.

## Routing assessment

The >=11/12 SDXL checked screen and <=10/12 diagnosis branch existed before execution. Actual 10/12 follows the declared negative branch without moving thresholds or hiding the two failures. Deferring a broad independent-diffusion grid is consistent with the prospective rule because the full backbone is absent. A failed VAE screen does not prove failed diffusion; the retained conditional .2/seed-0 diagnostic and later .2/.4 three-seed grid preserve that distinction.

Readable-code robustness at unchanged quality/thresholds is a reasonable next hypothesis, not a result already established. Retaining frozen F5 and v5, limiting search, and replicating survivors on new development sources are appropriate. Early WAM execution is justified by an available named checkpoint and relatively simple native inference, provided native and quality-matched arms and presence/identity/binding endpoints stay separate. No observed external superiority is available. No new T5 evidence was collected; the routing should continue to state that explicitly.

The report correctly uses twelve sources rather than 144 images as VAE evidence units, six disjoint pairs rather than 31 rows as binding units, and treats 72 negative calls per method as repeated observations on twelve sources. Strict clean quality is a property of this development panel only. Historical M2 quality shortfalls, human admissibility and confirmation requirements remain unchanged.
