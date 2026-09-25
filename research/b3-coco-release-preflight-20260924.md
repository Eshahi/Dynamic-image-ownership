# B3 MS-COCO release-year conflict preflight

Status 2026-09-25: **documented source conflict, now resolved by a bounded user-authorized COCO 2017 image-release choice; no dataset acquisition or B3 acceptance**. See the [decision record](b3-coco-release-decision-20260925.md). Issue #10 (B3) still depends on A6/#7, which remains open. This preflight does not start the B3 manifest, rewrite the proposal, choose sample IDs, clear image rights, or authorize scientific compute. Apply the [research contract](research-contract.md), [scope guard](scope-guard.md), and [approval policy](approval-policy.md).

## Exact project requirement and inspected source

The preserved proposal extraction at `inputs/proposal-text.md:269` and claim `DATA-01` in `research/claims.csv` require a 1,000-image MS-COCO subset described as version **2020 or newer**. `research/scope.md` retains this wording and explicitly leaves the release identity unresolved. This is a release constraint, not just a sample count.

The COCO maintainers' [download-page source at commit `5e1c4da`](https://github.com/cocodataset/cocodataset.github.io/blob/5e1c4da72464b1c6f068df0c02c91e3000ea62c4/dataset/download.htm) lists public image archives labeled 2014, 2015 test, and 2017; it does not list a 2020 image archive. Its split/task table associates the 2020 detection, keypoint and panoptic tasks with the 2017 image splits, and its 2020 update says the challenge data were unchanged. The maintainers' [2020 detection-task source at the same commit](https://github.com/cocodataset/cocodataset.github.io/blob/5e1c4da72464b1c6f068df0c02c91e3000ea62c4/dataset/detection-2020.htm) also directs participants to COCO 2017 train/validation data and says the 2020 task reused the preceding task's data.

Source pin for audit: repository `cocodataset/cocodataset.github.io`, commit `5e1c4da72464b1c6f068df0c02c91e3000ea62c4`; `dataset/download.htm` Git blob `b75be340244caff18f8f50fdb885d7c5e9e49ddf`, 13,225 bytes, local SHA-256 `62e500d3e7be567d97c295f5f56c95a416618d0770dd334a0ab943a4c1e6954b`; `dataset/detection-2020.htm` Git blob `76c49960341d939ca3113700b814115f1a4f26f6`, 7,411 bytes, local SHA-256 `9ebb512a59ffdaa31e2df467d3ea5b969293617f79aefea577bd7acc15586e6e`. Only these public HTML source files and local project text were read. No COCO image, annotation or archive was downloaded.

## Interpretation and decision boundary

A **2020 challenge/task label does not establish a 2020 image release**. The official pages checked here support COCO 2017 image splits used in 2020 tasks, not the proposal's literal “2020 or newer” image-version condition. This is a bounded finding: it does not prove that no later COCO-derived release exists anywhere, and it does not evaluate image-by-image licenses or the suitability of any subset.

Two non-equivalent paths remain:

1. Make a recorded material amendment permitting the official **COCO 2017 images** for the existing 1,000-image real-image commitment. Preserve the original wording and report the deviation in the thesis/protocol. A user/supervisor decision may be needed under local academic rules; no such institutional approval is claimed here. This changes the release-year condition but not the 1,000 count or the separate DIV2K/DiffusionDB commitments.
2. Keep the literal **2020-or-newer COCO image-version** condition. B3 must remain blocked until an official qualifying image release or an authenticated institutional interpretation is supplied; relabeling 2017 images as “COCO 2020” is not allowed. This can delay B3/B5/B4 and their downstream implementation/evaluation dependencies.

The user selected path 1 on 2026-09-25; the exact bounded authority and remaining limitations are recorded in [the decision](b3-coco-release-decision-20260925.md). The options above are preserved as the historical decision package, not as an open user question. Do not freeze `data/manifest.csv`, `data/dev-ids.json`, or `data/datasheet.md` merely from the release choice. Independent A6 and non-COCO preparatory work may continue. Dataset acquisition, licenses per image, IDs/splits and hash receipts remain separate B3/B4 work after dependency readiness.
