# A6 bounded Diffusers source-to-wheel parity receipt

Status 2026-09-24: **five exact installed-source-file matches, no model loaded**. The A5 method pins Diffusers source commit `0f252be0ed42006c125ef4429156cb13ae6c1d60`. The official GitHub `refs/tags/v0.35.1` is an annotated tag `e116b12bed30c0dc756575b8cdc8f35b3f3199b7` whose object targets exactly that commit, with tag message “Adds tag v0.35.1 for PyPI.” The isolated science environment reports installed PyPI package version `diffusers==0.35.1` and a locally measured PyPI-matched Windows-independent wheel SHA-256 `fe29ff10200970c7c5934c6488c213e2a77a03dad5e6fa00bbd8e1d04234cb0e` in the [Stage-2 lock](../requirements-science-stage2-win312-hashes.txt).

The following raw files fetched from that exact official commit matched the corresponding installed `site-packages/diffusers` files **byte-for-byte by SHA-256**. Both copies were read as bytes; the upstream copies are retained only in ignored `.thesis-build/upstream-diffusers-0f252be/`.

| Module relative to `src/diffusers` | SHA-256 of both files |
| --- | --- |
| `pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py` | `4e1de04f178a3509c01e39cf1760e0001edd287ccbb16359eb2a06c355ced3de` |
| `schedulers/scheduling_ddim.py` | `6bb3c830a7937a96acd9bfc3bbab6d75404ceda0189c423899d03c9d34da8599` |
| `models/autoencoders/autoencoder_kl.py` | `1ea5f6d3f2737bc6542a9d5edfbe8c7cb5e06e86e859f45742d9ba4af4bd4a4b` |
| `models/unets/unet_2d_condition.py` | `a1ee650816d1617c367a555377ead4f6114c8cd159311c54731b763eed26e49c` |
| `image_processor.py` | `eaaa29edf8a54c776adcbf991955a624c9f4fb4b38060ed6f8068014135d3b44` |

This resolves the narrower concern that **these five installed modules** may differ from the A5-pinned source. It does not prove every module in the wheel matches Git, package dependencies are reproducible across hosts, the unofficial model components are original, the nonstandard gradient route works, or scientific numerical parity. No diffusion weights were loaded or executed; A6/#7 and plan acceptance remain open.
