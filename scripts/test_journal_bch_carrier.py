"""Independent CPU algebra checks for the one frozen E1 carrier.

Run from the repository root with python scripts/test_journal_bch_carrier.py.
JSON stdout contains counts and inclusive interpreter-time approximation;
the parent process separately measures the hard enclosing wall-clock cap.
"""
from __future__ import annotations

import sys
import time

_START = time.perf_counter()
import itertools
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import journal_bch_carrier as bch

VECTORS = (
    (0x00000000, 0x000000000000000),
    (0x00000001, 0x0000000086E8113),
    (0x80000000, 0x400000003D3EC7F),
    (0xFFFFFFFF, 0x7FFFFFFFD62B7AA),
    (0x12345678, 0x091A2B3C1F385B9),
)


def gf_product(a, b):
    """Bit-serial field product, independent of production log tables."""
    product = 0
    for _ in range(6):
        if b & 1:
            product ^= a
        b >>= 1
        a <<= 1
        if a & 64:
            a ^= 0x43
    return product


def polynomial_remainder(word, generator):
    """Fixed-coordinate long division, independent of production bit_length loop."""
    for position in range(62, 26, -1):
        if (word >> position) & 1:
            word ^= generator << (position - 27)
    return word


def lfsr_encode(q):
    """MSB-first systematic streaming division, with 27 appended zeros."""
    register = 0
    for position in range(31, -28, -1):
        bit = (q >> position) & 1 if position >= 0 else 0
        outgoing = (register >> 26) & 1
        register = ((register << 1) | bit) & ((1 << 27) - 1)
        if outgoing:
            register ^= 0x06E8113
    return (q << 27) ^ register


def mask(positions):
    result = 0
    for position in positions:
        result ^= 1 << position
    return result


def run():
    stats = {}
    powers = [1]
    for _ in range(63):
        powers.append(gf_product(powers[-1], 2))
    assert powers[63] == 1 and len(set(powers[:63])) == 63
    roots = set()
    for first in range(1, 11):
        current = first
        while current not in roots:
            roots.add(current)
            current = 2 * current % 63
    assert len(roots) == 27
    polynomial = [1]
    for root in sorted(roots):
        next_polynomial = [0] * (len(polynomial) + 1)
        for i, coefficient in enumerate(polynomial):
            next_polynomial[i] ^= gf_product(coefficient, powers[root])
            next_polynomial[i + 1] ^= coefficient
        polynomial = next_polynomial
    assert all(coefficient in (0, 1) for coefficient in polynomial)
    generator = sum(coefficient << i for i, coefficient in enumerate(polynomial))
    assert generator == 0x086E8113 == bch.GENERATOR
    stats["field_order"] = 63
    stats["generator_degree"] = len(polynomial) - 1

    rng = random.Random(20261010)
    messages = [q for q, _ in VECTORS] + [1 << i for i in range(32)]
    messages += [rng.getrandbits(32) for _ in range(100)]
    for q in messages:
        direct = (q << 27) ^ polynomial_remainder(q << 27, generator)
        assert bch.encode(q) == lfsr_encode(q) == direct
        assert direct >> 27 == q and direct < (1 << 59)
    # Distinct systematic coordinates prove rank 32, without numeric rank heuristics.
    unit_codes = [bch.encode(1 << i) for i in range(32)]
    assert [word >> 27 for word in unit_codes] == [1 << i for i in range(32)]
    stats["encoder_comparisons"] = len(messages)
    stats["unit_rank"] = 32

    def recover(q, code, error_positions):
        result = bch.decode(code ^ mask(error_positions))
        assert result["success"], (q, error_positions, result)
        assert result["q"] == q and result["code"] == code, (q, error_positions, result)
        assert result["error_positions"] == list(error_positions)
        assert len(result["syndromes"]) == 10

    count = 0
    for q, expected in VECTORS:
        assert bch.encode(q) == expected
        recover(q, expected, ())
        for weight in (1, 2):
            for positions in itertools.combinations(range(59), weight):
                recover(q, expected, positions)
                count += 1
        recover(q, expected, (0, 26, 27, 58))
    stats["single_double_cases"] = count
    # A separate random stream makes exact error sets independent of encoder probes.
    rng = random.Random(20261010)
    for q, code in VECTORS:
        for weight in (3, 4, 5):
            for _ in range(100):
                recover(q, code, sorted(rng.sample(range(59), weight)))
    stats["weight_3_4_5_cases"] = 1500

    # Construct a FULL code with a nonzero omitted message coordinate independently.
    # Removing that coordinate produces a legal 59-bit input whose locator must
    # point outside the shortened code, even though a full-parent decoder can fix it.
    for omitted in range(59, 63):
        shifted = 1 << omitted
        full_word = shifted ^ polynomial_remainder(shifted, generator)
        received = full_word ^ shifted
        assert received < (1 << 59)
        result = bch.decode(received)
        assert not result["success"] and result["q"] is None and result["code"] is None
        assert result["error_positions"] == [omitted]
        assert result["reason"] == "located error in omitted coordinate"
    stats["omitted_coordinate_cases"] = 4
    for invalid in (-1, 1 << 59, 1 << 62, True, None, 1.5):
        result = bch.decode(invalid)
        assert not result["success"] and result["syndromes"] == []
    for invalid in (-1, 1 << 32, True, None, 1.5):
        try:
            bch.encode(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("encoder accepted invalid input")

    # >t errors have no universal rejection guarantee. Every accepted result
    # must instead satisfy the declared radius, systematic word and re-encoding.
    accepted = 0
    for weight in (6, 7, 10, 20, 30, 59):
        for _ in range(100):
            q = rng.getrandbits(32)
            received = bch.encode(q) ^ mask(rng.sample(range(59), weight))
            result = bch.decode(received)
            if result["success"]:
                accepted += 1
                assert result["code"] == bch.encode(result["q"])
                assert (received ^ result["code"]).bit_count() <= 5
                assert result["error_positions"] == [
                    i for i in range(59) if (received ^ result["code"]) >> i & 1]
            else:
                assert result["q"] is None and result["code"] is None
    # Explicitly produce >5-error miscorrection from one code to another:
    # word1 has weight >=11; leave just one error around word1, originating at 0.
    other = bch.encode(1)
    flip = (other & -other).bit_length() - 1
    received = other ^ (1 << flip)
    assert received.bit_count() > 5
    result = bch.decode(received)
    assert result["success"] and result["q"] == 1
    stats["beyond_t_cases"] = 601
    stats["beyond_t_random_accepted"] = accepted

    from scripts import revised_watermark_v5 as v5
    profile = v5.DEFAULT_PROFILE
    owner = "e1-cpu-test-owner"
    signs = bch.signs(profile, owner)
    _, key, config = v5._resolve(profile, None)
    material = v5.base._stream(key, config,
        v5.base._pack(b"E1-BCH59-A-v1", v5.canonical_owner(owner)), 40)
    independent_signs = [1.0 - 2.0 * int(bit)
                         for byte in material for bit in f"{byte:08b}"]
    assert signs == independent_signs
    assert bch.BOUNDS == tuple(320 * i // 59 for i in range(60))
    assert bch.LENGTHS.count(6) == 25 and bch.LENGTHS.count(5) == 34
    assert signs != bch.signs(profile, owner + "-other")
    for q, code in VECTORS:
        chips = bch.pattern(profile, owner, q)
        assert len(chips) == 320 and sum(value * value for value in chips) == 320
        assert chips == [signs[k] * (-1.0 if code >> i & 1 else 1.0)
                         for i in range(59)
                         for k in range(bch.BOUNDS[i], bch.BOUNDS[i + 1])]
        # Independently reconstruct hard bits from noiseless segment projection.
        raw = sum(int(sum(signs[k] * chips[k]
                          for k in range(bch.BOUNDS[i], bch.BOUNDS[i + 1])) < 0) << i
                  for i in range(59))
        assert raw == code and bch.decode(raw)["q"] == q
    # Degenerate projection: u_i==0 yields raw zero by the frozen tie rule.
    zeros = [0.0] * 320
    raw = sum(int(sum(signs[k] * zeros[k]
                      for k in range(bch.BOUNDS[i], bch.BOUNDS[i + 1])) < 0) << i
              for i in range(59))
    assert raw == 0 and bch.decode(raw)["q"] == 0
    assert sum(a * p for a, p in zip(bch.pattern(profile, owner, 0), zeros)) == 0
    stats["carrier_vectors"] = 5
    return stats


if __name__ == "__main__":
    # --json is accepted for caller consistency; stdout is always one JSON object.
    try:
        stats = run()
    except Exception as exc:
        print(json.dumps({"success": False, "error": repr(exc),
                          "duration_seconds": time.perf_counter() - _START}))
        raise
    print(json.dumps({"success": True, "stats": stats,
                      "duration_seconds": time.perf_counter() - _START}, sort_keys=True))
