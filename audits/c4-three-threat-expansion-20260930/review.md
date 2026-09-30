# Semantic cohort expansion and attack arithmetic review

The approved local expansion now has seven same-topic, two uncertain and 57 different-topic pairs across twelve images. This resolves the earlier semantic coverage shortfall, not scientific correctness. Copy-Paste and Regeneration still use the original ten sources. No scientific execution or lifecycle acceptance occurred.

## Independent review scope

The author is root. Independent read-focused reviewer `/root/three_threat_design_review` used actual gpt-6-astra with high reasoning under the user's model-selection delegation. A stronger reviewer was chosen because source separation and attack/control accounting affect scientific validity. The reviewer inspected the exact expansion records and ordinary arithmetic, independently replayed the metadata graph and reran synthetic tests. Review was not blind to the author's category selection or proposed pair labels.

The reviewer reported no blocking finding within this narrow scope. It verified all 66 unique pair labels, both JPEG raw hashes, item metadata in the existing COCO annotations, the ascending candidate-selection rule, and both singleton components with no overlap with any frozen selected source. The graph replay uses existing identities and fingerprints from 19,900 nodes and 7,627 components; it does not decode locked-test pixels or evaluate method scores. Finite grouping does not establish population independence or rights clearance.

## Exact reviewed artifacts

| Artifact | SHA256 |
| --- | --- |
| development-expansion.json | a3506ff65244a94cd62e2bde7dfb8632c2a7ff50f6e62a97e8a76736abb06ddd |
| semantic-labels.json | 89dd92ebbd1c0807880178146ae1ff7dd5b1dfb682229f45a7524656b6f7ceae |
| cohort-expansion-addendum.md | 0de7fb3299da2eeed26c3b68ed72e3c2984351a769e83e666590d44f426d80cd |
| check_three_threat_source_groups.py | aa9f2f47a9a38042d0ef5c1df1569aaaaa6b4cb1cc11286ce3744fea9829b08d |
| three_threat_protocol.py | 7fad2f0f0eea778f8cd04f02678eed78da8b4be4abdda485de0717f3dc809fb7 |
| test_three_threat_protocol.py | 30bb9913346702d8f74723b7f29bbc7d21cc3dbe7952f2d3cb91b1970bfa028f |

The three experiment JSON/Markdown files are under `experiments/c4-three-threat-small-v1/`; the Python files are under `scripts/`.

## Checks and remaining execution obligations

All seven ordinary synthetic tests passed for both author and reviewer using the verified Windows interpreter. The fixed inventory contains 24 clean images, 120 T4 attack/control images, 120 T3 regeneration images and 66 T5 pairs. It is an image/pair inventory, not the complete detector-call inventory. T4 uses C0 recipients, exact central patch copies and a separate clean-donor residual arm with clipping followed by ties-to-even quantization. Inputs remain unchanged and construction exposes no detector feedback.

Broad Windows script discovery retained one import failure because its workflow environment intentionally lacks NumPy: 49 discovered tests, 48 passed and one module import error. The four existing synthetic RGB pilot tests then passed in the pinned WSL numerical environment, and all eight supplied-code tests passed in Windows. No installation was attempted and the failed invocation is not relabelled a broad-suite success. `git diff --check` passed.

Actual C0 file identity, saved-PNG handling, model/runtime/weight bindings, fresh paired random generators, complete detector-call accounting, resources, exact clean execution manifest and independent whole-package review remain outstanding. Only official runner authorization can permit scientific execution. Rights and first-party checkpoint custody remain bounded unresolved provenance concerns; no download or substitution is authorized.

Read-only GitHub API verification found issue18 open and PR67 open/draft on `codex/18-embedding-module`, remote head `d3cc3d9f0cdd06399cd7e781ff7549f63a02a896`. The initial `gh` command failed because it is absent from PATH; public API reads succeeded without installing it. The controller still reports d916749c paused at plan-acceptance, choice null and workflow hash `772a1a3b1a4ff674c878b0532485820f860e81490e026441a0bb384a3aebda51`. No publication, push, gate mutation or authorization record was created.
