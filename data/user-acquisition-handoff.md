# B3 user-operated dataset acquisition handoff

**Superseding decision 2026-09-26:** first-batch extracted files/metadata have been received. The user's direct «دانلود کن» now authorizes agent acquisition of **only the exact fourteen DiffusionDB ZIPs** in [the bounded acquisition decision](../research/b3-diffusiondb-acquisition-decision-20260926.md). The older declined-download/second-batch-unassigned instructions below are historical for this batch; no blanket acquisition or scientific-compute permission follows.

Status 2026-09-25: the user chose to obtain dataset files personally. Agents must not download dataset archives, image partitions or metadata on the user's behalf under the declined 12 GB request. This handoff specifies a first batch only; it is not a frozen image selection, rights clearance, scientific-compute approval or B3 completion.

Place the **unextracted, unrenamed** files in `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw/incoming/`, which is ignored by Git. Do not commit or send the archives in chat. The W: project directory is the stable handoff location; the B3 agent's isolated C: worktree can inspect it by absolute path later. If the actual download arrives elsewhere, provide its local folder path instead of copying large files solely to match this suggestion.

## First batch

| Local filename | Official source | Why it is needed |
| --- | --- | --- |
| `val2017.zip` | [COCO maintained download page](https://cocodataset.org/#download), “2017 Val images [5K/1GB]”; the maintained page's ZIP link is `http://images.cocodataset.org/zips/val2017.zip`. | Candidate frame for the user-approved 1,000 **COCO 2017** images. Do not download `train2017.zip`. |
| `annotations_trainval2017.zip` | The same [COCO download page](https://cocodataset.org/#download), “2017 Train/Val annotations [241MB]”; ZIP link `http://images.cocodataset.org/annotations/annotations_trainval2017.zip`. | Source image IDs, split and license references. This annotation license does not grant image copyright. |
| `DIV2K_train_HR.zip` | [DIV2K maintainers' page](https://data.vision.ee.ethz.ch/cvl/DIV2K/), “Train Data (HR images)”; direct link `https://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_train_HR.zip`. | All 800 source-train HR images. |
| `DIV2K_valid_HR.zip` | The same [DIV2K page](https://data.vision.ee.ethz.ch/cvl/DIV2K/), “Validation Data (HR images)”; direct link `https://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip`. | All 100 source-validation HR images. |
| `metadata.parquet` | [DiffusionDB 2M curator repository at pinned revision `fb620fbe49fa4420e0734bd9c0df11f51176b61f`](https://huggingface.co/datasets/poloclub/diffusiondb/tree/fb620fbe49fa4420e0734bd9c0df11f51176b61f), `metadata.parquet` (not `metadata-large.parquet`). | Metadata-only selection and content/dependence preflight before requesting image partitions. |

At the pinned DiffusionDB revision, its API advertises `metadata.parquet` size **194,548,652 bytes** and LFS SHA-256 **`eecd341187bc91c07f5994ad0660d40228ea025616fd57a509bef8323677c68f`**. These are upstream claims to verify against the local file, not a claim that bytes have been acquired. The DIV2K server's 2026-09-25 HEAD advertised **3,530,603,713** and **448,993,893** bytes for train and validation HR archives, respectively; COCO's maintained page advertises rounded sizes only. Actual final archive sizes/hashes must be captured on receipt.

## Second batch remains unassigned

Do **not** download the full DiffusionDB dataset, `metadata-large.parquet`, the first five arbitrary image partitions, or any particular image ZIP yet. The source is about 1.6 TB in full; the 5,000-image commitment calls for a deterministic metadata/eligibility/duplicate-group rule and exact partition IDs before a bounded user download list. The agent will publish that list after the first-batch metadata is locally available and inspected, without using method outcomes to choose parts.

## Agent receipt once files arrive

The agent will check names, byte sizes and SHA-256, verify ZIP central directories and member paths without unsafe extraction, inspect COCO license metadata and DiffusionDB prompt/NSFW/dependence fields, and record exclusions. Any unpacking stays in ignored local storage. A source archive hash is not a per-image manifest; `data/manifest.csv` and `data/dev-ids.json` remain absent until item IDs, rights, dimensions, groups and hashes are actually checked. Raw images and sensitive prompts/user identifiers must not enter Git.
