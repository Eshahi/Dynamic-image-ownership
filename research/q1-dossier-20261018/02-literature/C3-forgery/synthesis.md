# C3 synthesis: ownership ambiguity and forgery

Access cut-off: 2026-10-18. Ten V2 primary-paper cards; the timestamp standard is supplemental context. V2 means the specified method and experiments, or formal security argument, were inspected. It does not mean independent reproduction.

## What is already known

Passive **regenerate-and-enroll** is best described as fraudulent registration or competing-claim ambiguity within a watermark protocol. This is a conceptual relationship to Craver's ownership-ambiguity analysis, not proof that the exact registry procedure appeared in 1998. Craver constructs counterfeit evidence and distinguishes invertibility from quasi-invertibility; noninvertibility alone is insufficient [craver1998ownership, §§IV–VIII](cards/craver1998ownership.md). The searches did not establish an earlier paper using the exact phrase “regenerate-and-enroll.” That limited finding cannot support a first-ever attack claim.

Three active operations require separate names and evaluations:

1. **Victim-mark copying:** transfer somebody else's mark to unrelated content, creating false evidence against that victim. Kutter estimates and copies a residual; Souček modernizes one-image residual estimation using a learned preference model [kutter2000copy, §§3–6](cards/kutter2000copy.md); [soucek2025oneshot, §§3–4](cards/soucek2025oneshot.md).
2. **Victim-noise forging:** manipulate a cover or reuse recovered noise so it passes a victim's detector. Müller and Jain need only one marked reference but different proxy-model access [muller2025forgery, §§3–4](cards/muller2025forgery.md); [jain2025single, §§4–5](cards/jain2025single.md).
3. **Attacker re-embedding:** write the attacker's own publicly available owner-conditioned pointer into copied/regenerated content and enroll it. This does not require breaking victim-key secrecy. It is a proposed stronger adversary for this thesis, not a result established by the passive enrollment test.

WMCopier supplies another copying regime: thousands of images sharing a target message [dong2025wmcopier, §§3–5](cards/dong2025wmcopier.md). Its access cost must not be conflated with one-shot attacks.

## Closest work and novelty pressure

SEAL §3.1 explicitly discusses checking a suspect against a database of previous generations before proposing database-free semantic binding. Generic registry-assisted checking and generic binding of semantics to a mark are therefore poor novelty claims [arabi2025seal](cards/arabi2025seal.md). SemBind additionally masks watermark noise using private semantic codes [zhang2026sembind](cards/zhang2026sembind.md).

The thesis's defensible comparison concerns an **existing-photo image-domain writer plus a trusted descriptor registry**, with all side information declared. SEAL/SemBind instead change generation-time noise and require inversion. Those differences establish a comparison axis, not demonstrated superiority. Souček is especially close to the post-hoc setting; Jain makes encoder-gradient transfer a concrete future threat.

Semantic-binding defenses have residual failures and assumptions. SEAL's analysis assumes patch-distance separation; SemBind's semantic code can group related content. Neither establishes unique original-instance identity. The 2026 geometric defense studies proxy mismatch and reports AUC, while explicitly allowing distribution overlap. Its reference-latent availability should be resolved before treating it as storage-free [lee2026geometric, §§4–6](cards/lee2026geometric.md).

## What defenses actually assume

A fixed admissible watermark protocol and content-bound evidence constrain counterfeit claims; a trusted registry also needs an enrollment-admissibility rule. Secret-key authentication can establish who authorized a record, but cannot by itself establish that its image was originally created by that signer. These are security-model deductions, not implemented thesis features.

A timestamp establishes prior existence of committed data under a trustworthy clock/signing authority. It does not inspect authorship or automatically authenticate the requester: RFC 3161 §§1–2.4.1 explicitly separates these matters [protocol notes](protocol-notes.md). Timestamping a stolen image later does not repair permissive enrollment.

Cryptographic undetectability is also distinct from unforgeability. Thietke's nonce-respecting construction addresses multi-image distinguishing, not content ownership [thietke2025crypto, §3](cards/thietke2025crypto.md). A public owner identifier remains a pointer, not a secret authentication key.

## Evaluation implications

A later authorized study should distinguish passive enrollment, attacker re-embedding, victim-mark copying and adaptive descriptor matching; fix enrollment order, attacker access, attempt budget and accepted-content relation first. Report any-attacker-record acceptance, multiple-record ambiguity and unique wrong attribution separately. Descriptor-only rejection and whole-pipeline rejection are different endpoints.

Report calibration, sample unit, confidence bounds and distortion jointly. Souček's bit accuracy, geometric-defense AUC and low-FPR acceptance rates are not interchangeable. Existing thesis outcomes need evidence-ledger citations; no numerical thesis result is reproduced here.

The plausible contribution is a carefully bounded measurement of regeneration survival versus instance discrimination under declared registry assistance. The present literature does not justify a new general ownership guarantee, a novel registry concept, or resistance to active public-owner re-embedding.


Parent addition: MetaSeal v2 is now V2 (Zhou2026MetaSeal). Its self-contained signature construction narrows any novelty claim for content-dependent attribution, while its gray-box model-secrecy assumption and illustrated regeneration failure differ from the registry setting.
