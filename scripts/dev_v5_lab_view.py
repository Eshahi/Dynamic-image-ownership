"""Development lab: side-by-side views of host and marked image for visual inspection.

Development tooling (see ``dev_v5_lab``).  For each host it writes one PNG with
the full host and marked image side by side at their own size, and below them
the 128x128 region around the most-changed 32x32 block of each, magnified
three times, host left and marked right.

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_lab_view.py fill-p35.5-c2 generated-01 procedural-3
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_lab as lab  # noqa: E402
from scripts import dev_v5_lab_run as run  # noqa: E402


def view(variant: str, name: str, rgb: np.ndarray, hosts: str = "dev") -> Path:
    marked = np.asarray(Image.open(lab.LAB / hosts / variant / f"{name}-C1.png").convert("RGB"))
    difference = marked.astype(np.float64) - rgb
    block = np.sqrt((difference**2).mean(axis=2).reshape(16, 32, 16, 32).mean(axis=(1, 3)))
    by, bx = np.unravel_index(int(block.argmax()), block.shape)
    cy, cx = int(np.clip(by * 32 + 16 - 64, 0, rgb.shape[0] - 128)), int(np.clip(bx * 32 + 16 - 64, 0, rgb.shape[1] - 128))
    crop = lambda image: np.kron(image[cy : cy + 128, cx : cx + 128], np.ones((3, 3, 1), dtype=np.uint8))  # noqa: E731
    top = np.concatenate([rgb, np.full((rgb.shape[0], 8, 3), 255, np.uint8), marked], axis=1)
    bottom = np.concatenate([crop(rgb), np.full((384, 8, 3), 255, np.uint8), crop(marked)], axis=1)
    pad = np.full((bottom.shape[0], top.shape[1] - bottom.shape[1], 3), 255, np.uint8) if top.shape[1] > bottom.shape[1] else None
    if pad is not None:
        bottom = np.concatenate([bottom, pad], axis=1)
    sheet = np.concatenate([top, np.full((8, top.shape[1], 3), 255, np.uint8), bottom], axis=0)
    out = lab.LAB / hosts / "views" / f"{variant}-{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(sheet).save(out)
    print(out, f"worst block ({by},{bx}) rms {block.max():.1f}")
    return out


if __name__ == "__main__":
    variant, names = sys.argv[1], sys.argv[2:]
    hosts = dict(run.dev_hosts("dev"))
    for name in names:
        view(variant, name, hosts[name])
