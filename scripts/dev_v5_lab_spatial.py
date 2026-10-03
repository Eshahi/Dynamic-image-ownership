"""Development lab: is the channel's change to the robust coefficients correlated between neighbouring blocks?

Development tooling (see ``dev_v5_lab``).  For the unmarked hosts and their
cached channel outputs it reports, per robust position, the correlation of the
channel noise (normalised coefficient after the channel minus before) between
horizontally and vertically adjacent coarse blocks, and the same for the host
coefficients themselves.  If either is well above zero, a high-pass filter
across blocks in the detector would remove part of it while keeping the mark,
whose signs are independent from block to block.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_lab as lab  # noqa: E402
from scripts import dev_v5_lab_run as run  # noqa: E402


def load(path: Path):
    from PIL import Image

    return np.asarray(Image.open(path).convert("RGB")) if path.exists() else None


def neighbour_correlation(field: np.ndarray) -> tuple[float, float]:
    """field: (16, 16) values of one position; correlation with the right and the lower neighbour."""
    a, b = field[:, :-1].ravel(), field[:, 1:].ravel()
    c, d = field[:-1, :].ravel(), field[1:, :].ravel()
    return float(np.corrcoef(a, b)[0, 1]), float(np.corrcoef(c, d)[0, 1])


def main() -> int:
    variant = {**lab.DEFAULT, "whitening": 2.0}
    keys = lab.Keys()
    root = lab.LAB / "dev"
    channels = ("vae", "sd0.05-0", "sd0.1-0", "sd0.2-0")
    noise = {channel: [] for channel in channels}
    host = []
    for name, rgb in run.dev_hosts("dev"):
        reference = lab.Analysis(lab.luma(rgb), keys, variant)
        before = reference.v.reshape(256, lab.COUNT)
        host.append(before)
        for channel in channels:
            attacked = load(root / "C0" / f"{name}-{channel}.png")
            if attacked is None:
                continue
            c = lab.coefficients(lab.coarse(lab.luma(attacked)))
            after = c * reference.w / reference.n[:, None]
            noise[channel].append(after - before)
    print("position  host(h,v)  " + "  ".join(f"{c}(h,v)" for c in channels))
    for index, (u, v) in enumerate(lab.POSITIONS):
        cells = []
        for fields in [host] + [noise[c] for c in channels]:
            pairs = [neighbour_correlation(f[:, index].reshape(16, 16)) for f in fields]
            cells.append("%5.2f,%5.2f" % (np.mean([p[0] for p in pairs]), np.mean([p[1] for p in pairs])))
        print(f"({u},{v})     " + "   ".join(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
