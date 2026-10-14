"""Fixed E3-FG128 fine-feature capacity screen on cached development pixels."""
import hashlib
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scripts import journal_stable_instance as harness
from scripts import revised_watermark_v4 as base

LABEL = b'E3-FG128-native-fine-gaussian-v1'
BITS = 128
MATCH = 44
FAR = 51
MATRICES = {}
MATRIX_METADATA = {}


def ball(n, r):
    return sum(math.comb(n, k) for k in range(r + 1)) / 2**n


def conventions():
    # Thresholds are frozen by exact integer comparisons, before image outcomes.
    old_match = sum(math.comb(32, k) for k in range(7))
    old_nonfar = sum(math.comb(32, k) for k in range(10))
    for r, old in [(MATCH, old_match), (FAR - 1, old_nonfar)]:
        assert sum(math.comb(BITS, k) for k in range(r + 1)) <= old * 2**96
        assert sum(math.comb(BITS, k) for k in range(r + 2)) > old * 2**96
    return dict(old_match_ball=ball(32, 6), new_match_ball=ball(128, MATCH),
                old_nonfar_ball=ball(32, 9), new_nonfar_ball=ball(128, FAR - 1),
                meaning='Hypothetical independent uniform bits only, not calibrated FPR')


def matrix(key, config, width):
    assert width > 0 and width % 2 == 0
    cache_key = (key, config, width)
    if cache_key not in MATRICES:
        stream = base._stream(key, config,
            base._pack(LABEL, width.to_bytes(4, 'big'), BITS.to_bytes(4, 'big')),
            BITS * width * 8)
        integers = np.frombuffer(stream, dtype='>u8').reshape(-1, 2)
        uniform = ((integers >> 12).astype(np.float64) + .5) / 2**52
        assert np.all((uniform > 0) & (uniform < 1))
        radius = np.sqrt(-2 * np.log(uniform[:, 0]))
        angle = 2 * math.pi * uniform[:, 1]
        coefficients = np.column_stack((radius * np.cos(angle), radius * np.sin(angle)))
        gaussian = coefficients.reshape(BITS, width)
        assert gaussian.dtype == np.float64 and np.all(np.isfinite(gaussian))
        MATRICES[cache_key] = gaussian
        identity = hashlib.sha256(key + config + width.to_bytes(4, 'big')).hexdigest()
        MATRIX_METADATA[identity] = dict(width=width, rows=BITS,
            stream_sha256=hashlib.sha256(stream).hexdigest(), stream_bytes=len(stream),
            construction='Big-endian uint64, upper 52 bits midpoint, Box-Muller cosine/sine, row major float64')
    return MATRICES[cache_key]


def serialize(margins):
    h = sum(int(value > 0) << (BITS - 1 - i) for i, value in enumerate(margins))
    encoded = f'{h:032x}'
    assert len(encoded) == 32
    assert [int(x) for x in f'{int(encoded, 16):0128b}'] == [int(x > 0) for x in margins]
    return encoded


def descriptor(luma, key, config):
    means, detail = base._analyse(luma, base._DETAIL_PLANES)
    legacy = base._perceptual_hash(means, detail, key, config)
    columns = len(means[0])
    fine = []
    for position in range(len(base.HASH_DETAIL_POSITIONS)):
        fine += base._local_detail([[block[position] for block in detail[start:start+columns]]
                                   for start in range(0, len(detail), columns)])
    g = np.asarray(fine, dtype=np.float64)
    norm = float(np.linalg.norm(g))
    floor = base.HASH_DETAIL_FLOOR * math.sqrt(len(fine))
    available = bool(np.all(np.isfinite(g)) and math.isfinite(norm) and norm >= max(floor, 1e-9))
    out = dict(h=None, legacy_h=f'{legacy:08x}', norm=norm if math.isfinite(norm) else None,
        fine_raw_norm=norm if math.isfinite(norm) else None, fine_floor=floor,
        available=available, vector=None, margins=None)
    if not available:
        return out
    f = g / max(norm, floor)
    assert abs(float(np.linalg.norm(f)) - 1) < 1e-12
    margins = matrix(key, config, len(fine)) @ f
    out.update(h=serialize(margins), vector=f.tolist(), margins=margins.tolist(),
               zero_margins=int(np.sum(margins == 0)))
    return out


def compare(a, b):
    out = harness.compare(a, b)
    d = out['distance']
    out.update(match=d is not None and d <= MATCH, mismatch=d is not None and d >= FAR)
    if out['cosine'] is not None:
        out['hypothetical_gaussian_expected_distance'] = BITS * math.acos(min(1, max(-1, out['cosine']))) / math.pi
    return out


if __name__ == '__main__':
    null = conventions()
    assert serialize([1.] + [0.] * 127) == '8' + '0' * 31
    assert serialize([-1.] * 127 + [1.]) == '0' * 31 + '1'
    harness.main(descriptor_fn=descriptor, compare_fn=compare, descriptor_config=dict(
        method='E3-FG128', label=LABEL.decode(), bits=BITS, radius=MATCH, mismatch=FAR,
        representation='Native local detail only; weak detail abstains',
        null_convention=null, gaussian_streams=MATRIX_METADATA,
        payload_cost='128 instance bits versus 32; transport not evaluated by this oracle'))
