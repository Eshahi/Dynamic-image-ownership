# B3 COCO image-release amendment decision

Status 2026-09-25: **user-authorized source-year amendment, not a completed dataset manifest or institutional approval**. This decision resolves the specific ambiguity documented in [the source preflight](b3-coco-release-preflight-20260924.md) for issue #10. The original proposal, source extraction, `DATA-01` claim row and historical decisions remain unchanged.

## Source requirement and verified conflict

The proposal calls for 1,000 MS-COCO images described as version **2020 or newer**. The COCO maintainers' [2020 detection-task source](https://github.com/cocodataset/cocodataset.github.io/blob/5e1c4da72464b1c6f068df0c02c91e3000ea62c4/dataset/detection-2020.htm) says that the 2020 challenge uses the preceding task's data and points to **COCO 2017** train/validation images. The pinned [download-page source](https://github.com/cocodataset/cocodataset.github.io/blob/5e1c4da72464b1c6f068df0c02c91e3000ea62c4/dataset/download.htm) lists 2017 image archives, not a separate 2020 image archive. Thus a 2020 **challenge** label does not satisfy a literal 2020-or-newer **image-release** condition.

## Decision and authority

In the authenticated Codex project conversation on 2026-09-25, after receiving that distinction, the user explicitly directed using the same images. Treat this as user authorization to use the official **COCO 2017 image release** for the existing 1,000-image MS-COCO commitment and to record the deviation from the literal release-year phrase. The actor is the user, not an agent-inferred or supervisor/university verdict. This is a material but bounded release-identity amendment under [approval-policy.md](approval-policy.md) and [scope-guard.md](scope-guard.md); it does not change the 1,000 count, real-image domain, separate DIV2K/DiffusionDB commitments, four research questions, or scientific method.

Do **not** relabel the image bytes as a new “COCO 2020” image release. In dataset manifests, methods text and thesis results, write **“COCO 2017 images used by the COCO 2020 challenge; user-authorized deviation from the proposal's 2020-or-newer release wording.”** This avoids claiming that the images themselves were published in 2020. If local academic rules require supervisor/university approval of a proposal amendment, that acceptance remains unverified; no institutional verdict is claimed here.

## Remaining B3 boundary

Issue #10 still depends on A6/#7. No image, annotation archive or dataset subset has yet been acquired. Before B3 acceptance, identify the official acquisition route and item-level rights, record exact release and annotation versions, freeze 1,000 source IDs with checksums and an auditable sampling rule, separate train/dev/test and later OOD holdout, and complete the datasheet. No dataset compute or paid service is authorized by this decision. The source-year choice alone does not close B3 or downstream B5/B4.
