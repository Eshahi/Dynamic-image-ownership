# C5 synthesis: fingerprints and copy detection

Research-only; no extractor, image, score or experiment was run. Nine core V2 cards and one supplemental V2 challenge report were inspected, plus V1 pHash documentation. V2 means the primary method and experimental sections were read; it is not endorsement or independent reproduction. Access date: 2026-10-18.

The literature supports a comparison strategy, not a demonstrated replacement for D1+B1. None of the inspected work reports the joint operating point required here: accepting a diffusion-regenerated enrolled image while rejecting distinct same-shot frames around the thesis's operational 17–18 dB region, at a fixed false-binding constraint. PSNR alone does not identify such a boundary.

SSCD is the strongest conceptual first comparator because its target is shared two-dimensional source identity, explicitly distinct from nearby video frames [pizzi2022sscd]. DINOv2 and CLIP bring broad invariance and useful features, but landmark/semantic agreement is different from frame identity [oquab2024dinov2]. Stronger semantics can preserve the very ambiguity that E2 exposes. This is a hypothesis about the task mismatch, not a measured ranking on thesis data.

Local matching with geometry is plausible because it retains correspondence positions that a pooled vector discards. DELG and the ISC report show that global retrieval followed by local/pairwise verification is established practice [cao2020delg; papakipos2022isc]. Yet shared backgrounds can geometrically agree across different frames. Inlier count alone is therefore not evidence of source identity; no geometry improvement is claimed. The separately assigned C6 hybrid-soft-binding paper must be reconciled before recommending geometry, especially its matched-false-binding comparison.

Diffusion-specific copy detection already exists. ICDiff learns graded replication and improves agreement with annotation, but its PCC/relative-distance evaluation does not certify binary false binding [wang2024icdiff]. The 2026 ADMCD preprint already combines local, global and texture features; its small exact-copy subset, random class-consistent negatives and threshold/test ambiguities leave our hard-negative question unanswered [chen2026admcd]. “Combine descriptors” or “add geometry” is consequently insufficient architecture novelty.

A trusted registry plus perceptual fingerprints is also prior art: DinoHash combines enrolled hashes, signing and encrypted matching [singhi2025dinohash]. Its random-bit false-positive approximation must not be transferred to structured lookalikes. Natural cohort collisions and white-box hash collisions illustrate distinct failures [leblancalbarel2026blackbox; struppek2022neuralhash]; query-limited PDQ results supply counterevidence to blanket claims that all hashes are trivially broken [madden2024practicalhashing]. These studies neither break F5 nor establish its security. Continuous descriptors can avoid a particular binarization bottleneck, but do not acquire cryptographic binding from continuity.

The defensible later question is whether a frozen, copy-specific representation adds separation beyond the present fine/layout descriptor under a source-group-aware hard-negative protocol. If geometry is considered, its contribution must be isolated at matched false binding, with static-background and moving-object cases distinguished. These are proposed comparisons only; no experiment design, threshold choice or performance forecast is authorized by this literature note. Fingerprint-only and mark-plus-registry arms remain necessary to isolate what the mark contributes. Novelty would need to reside in a precisely evidenced binding/threat/evaluation contribution, not passive similarity or legal ownership proof.

## Evidence boundaries

- Retrieval mAP, graded replication correlation, bit-collision success and record-verification false acceptance are different quantities.
- Oracle access, white-box access, natural negatives and adaptive adversaries must remain separate.
- Registered-reference access is detector side information and must be stated for every method.
- The frozen thesis E1/E2/E3 evidence is supplied by the parent dossier ledger; this literature search neither recomputed it nor expanded its scope.
