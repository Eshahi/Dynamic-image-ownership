"""Frozen E1-BCH59-A carrier: shortened systematic BCH(63,36), t=5.

Integer bit i is polynomial coordinate i. Only coordinates 0..58 transmit.
Algebra is stdlib-only; profile/sign machinery is imported only when used.
Decoding beyond five errors can return another valid word, not provenance.
"""
from __future__ import annotations

GENERATOR = 0x086E8113
FIELD_POLYNOMIAL = 0x43
N = 59
K = 32
T = 5
BOUNDS = tuple(320 * i // N for i in range(N + 1))
LENGTHS = tuple(BOUNDS[i + 1] - BOUNDS[i] for i in range(N))


def _field_tables():
    exp = []
    value = 1
    for _ in range(63):
        exp.append(value)
        value <<= 1
        if value & 64:
            value ^= FIELD_POLYNOMIAL
    log = [0] * 64
    for i, value in enumerate(exp):
        log[value] = i
    return tuple(exp * 2), tuple(log)


_EXP, _LOG = _field_tables()


def _mul(a: int, b: int) -> int:
    return _EXP[_LOG[a] + _LOG[b]] if a and b else 0


def _div(a: int, b: int) -> int:
    if not b:
        raise ZeroDivisionError("GF(64) divisor is zero")
    return _EXP[(_LOG[a] - _LOG[b]) % 63] if a else 0


def _remainder(value: int) -> int:
    while value.bit_length() > 27:
        value ^= GENERATOR << (value.bit_length() - 28)
    return value


def encode(q: int) -> int:
    """Encode precisely one unsigned 32-bit message, systematic and low-first."""
    if type(q) is not int or not 0 <= q < (1 << K):
        raise ValueError("q must be an unsigned 32-bit integer")
    shifted = q << 27
    return shifted ^ _remainder(shifted)


def _syndromes(word: int) -> list[int]:
    result = [0] * (2 * T)
    while word:
        bit = word & -word
        position = bit.bit_length() - 1
        for j in range(1, 2 * T + 1):
            result[j - 1] ^= _EXP[(position * j) % 63]
        word ^= bit
    return result


def decode(y: int) -> dict:
    """Bounded-distance decode using ten syndromes, BM, and full-63 Chien.

    On failure q/code are None. error_positions are located polynomial
    coordinates, including an omitted coordinate when that causes rejection.
    syndromes always describe the received word (empty for invalid input).
    """
    syndromes: list[int] = []
    positions: list[int] = []

    def failure(reason):
        return dict(success=False, q=None, code=None,
                    error_positions=positions, reason=reason,
                    syndromes=syndromes)

    if type(y) is not int or not 0 <= y < (1 << N):
        return failure("received word must be an unsigned 59-bit integer")
    syndromes = _syndromes(y)
    # Berlekamp-Massey, locator coefficients in increasing degree order.
    locator = [1] + [0] * (2 * T)
    previous = locator.copy()
    degree, shift, previous_discrepancy = 0, 1, 1
    for index in range(2 * T):
        discrepancy = syndromes[index]
        for i in range(1, degree + 1):
            discrepancy ^= _mul(locator[i], syndromes[index - i])
        if not discrepancy:
            shift += 1
            continue
        old_locator = locator.copy()
        scale = _div(discrepancy, previous_discrepancy)
        for i in range(2 * T + 1 - shift):
            locator[i + shift] ^= _mul(scale, previous[i])
        if 2 * degree <= index:
            degree = index + 1 - degree
            previous = old_locator
            previous_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1
    if degree > T:
        return failure("locator degree exceeds five")
    for i in range(63):
        at = _EXP[(-i) % 63]
        value = locator[degree]
        for j in range(degree - 1, -1, -1):
            value = _mul(value, at) ^ locator[j]
        if value == 0:
            positions.append(i)
    if len(positions) != degree:
        return failure("locator root count differs from degree")
    if any(i >= N for i in positions):
        return failure("located error in omitted coordinate")
    corrected = y
    for i in positions:
        corrected ^= 1 << i
    if any(_syndromes(corrected)):
        return failure("corrected syndrome is nonzero")
    if corrected >> N:
        return failure("corrected high four coordinates are nonzero")
    q = corrected >> 27
    if encode(q) != corrected:
        return failure("corrected word does not re-encode")
    if (corrected ^ y).bit_count() > T:
        return failure("distance exceeds five")
    return dict(success=True, q=q, code=corrected,
                error_positions=positions, reason="ok", syndromes=syndromes)


def signs(profile, owner_id: str) -> list[float]:
    """Public profile signs from the frozen base stream; MSB bit 1 is -1."""
    # v5.base is exactly f5.base; avoid importing f5's numpy dependency.
    from scripts import revised_watermark_v5 as v5
    _checked, key, config = v5._resolve(profile, None)
    owner = v5.canonical_owner(owner_id)
    material = v5.base._stream(
        key, config, v5.base._pack(b"E1-BCH59-A-v1", owner), 40)
    return [-1.0 if material[i >> 3] & (1 << (7 - (i & 7))) else 1.0
            for i in range(320)]


def pattern(profile, owner_id: str, q: int) -> list[float]:
    """320 antipodal chips in the fixed 59 contiguous segments."""
    code = encode(q)
    result = signs(profile, owner_id)
    for i in range(N):
        if (code >> i) & 1:
            for k in range(BOUNDS[i], BOUNDS[i + 1]):
                result[k] = -result[k]
    return result
