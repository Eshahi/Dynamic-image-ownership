"""Coarse-lattice mark: writer and reader.

The writer moves secret low-frequency DCT coefficients of the image onto a secret
lattice. The reader needs no reference image, no model and no stored descriptor:
it measures how close those coefficients sit to the lattice.

For any image that does not depend on the key, each reader term is an independent
bounded symmetric variable over the random dither, so the false-positive bound
holds per image with no assumption about image statistics.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.fft import dctn, idctn

OPP = np.array([
    [1 / np.sqrt(3), 1 / np.sqrt(3), 1 / np.sqrt(3)],
    [1 / np.sqrt(2), -1 / np.sqrt(2), 0.0],
    [1 / np.sqrt(6), 1 / np.sqrt(6), -2 / np.sqrt(6)],
])
MULTS = (0.5, 0.71, 1.0, 1.41, 2.0, 2.83)


def to_coefs(rgb):
    opp = np.tensordot(np.asarray(rgb, dtype=np.float64), OPP.T, axes=([2], [0]))
    return np.stack([dctn(opp[..., c], norm="ortho") for c in range(3)], axis=0)


def from_coefs(coefs):
    opp = np.stack([idctn(coefs[c], norm="ortho") for c in range(3)], axis=-1)
    return np.tensordot(opp, OPP, axes=([2], [0]))


def psnr(a, b):
    mse = np.mean((np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)) ** 2)
    return float("inf") if mse == 0 else float(10 * np.log10(255 ** 2 / mse))


class Lattice:
    """Frozen public layout: which coefficients, and their design noise."""

    def __init__(self, ch, vv, uu, sigma, rho, beta):
        self.ch, self.vv, self.uu = np.asarray(ch), np.asarray(vv), np.asarray(uu)
        self.sigma = np.asarray(sigma, dtype=np.float64)
        self.rho, self.beta = float(rho), float(beta)
        self.k = len(self.ch)

    def save(self, path):
        Path(path).write_text(json.dumps({
            "ch": self.ch.tolist(), "vv": self.vv.tolist(), "uu": self.uu.tolist(),
            "sigma": self.sigma.tolist(), "rho": self.rho, "beta": self.beta,
        }), encoding="utf-8")

    @classmethod
    def load(cls, path):
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(d["ch"], d["vv"], d["uu"], d["sigma"], d["rho"], d["beta"])

    def secrets(self, key):
        seed = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        return rng.choice([-1.0, 1.0], size=self.k), rng.uniform(0, 1, size=self.k)

    def values(self, coefs):
        return coefs[self.ch, self.vv, self.uu]


def nudge(lat, values, key, mult):
    sign, dith = lat.secrets(key)
    step = lat.rho * lat.sigma * mult
    p = values * sign
    r = np.mod(p - dith * step + step / 2, step) - step / 2
    return -lat.beta * r * sign


def embed(rgb, lat, key, mult=1.0, floor_db=None):
    x = np.asarray(rgb, dtype=np.float64)
    coefs = to_coefs(x)
    move = nudge(lat, lat.values(coefs), key, mult)
    if floor_db is not None:
        budget = x.size * 255 ** 2 * 10 ** (-floor_db / 10)
        energy = (move ** 2).sum()
        if energy > budget:
            move *= np.sqrt(budget / energy)
    coefs[lat.ch, lat.vv, lat.uu] += move
    out = np.clip(np.rint(from_coefs(coefs)), 0, 255).astype(np.uint8)
    return out, move


def score_values(lat, values, key, mults=MULTS):
    sign, dith = lat.secrets(key)
    p = values * sign
    best = -99.0
    for q in mults:
        step = lat.rho * lat.sigma * q
        z = np.cos(2 * np.pi * (p - dith * step) / step).sum() / np.sqrt(lat.k)
        best = max(best, float(z))
    return best


def read(rgb, lat, key, mults=MULTS):
    return score_values(lat, lat.values(to_coefs(rgb)), key, mults)


def threshold(fpr=1e-6, tries=len(MULTS)):
    """Bentkus-Dzindzalieta style bound used by the existing project readers: 3.18 Q(t) * tries <= fpr."""
    from scipy.stats import norm
    return float(norm.isf(fpr / (3.18 * tries)))
