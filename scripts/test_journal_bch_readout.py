"""CPU decision tests for E1: corrected-word score, no oracle and abstention."""
import inspect
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import journal_bch_carrier as codec
from scripts import journal_bch_readout as readout


def main():
    profile = json.loads((ROOT / "experiments/c4-v5-two-tier-regeneration-v1/profile.json").read_text())
    owner = "qim-pilot-owner-alpha"
    for q in (0, 1, 0x80000000, 0xffffffff, 0x12345678):
        clean = np.asarray(codec.pattern(profile, owner, q))
        for flipped in ((), (0,), (0, 26, 27, 57, 58)):
            p = clean.copy()
            for bit in flipped:
                p[codec.BOUNDS[bit]:codec.BOUNDS[bit + 1]] *= -1
            result = readout.semantic_channel(p, profile, owner, q ^ 0x12345678)
            assert result["read"] and result["bch_success"]
            assert result["decoded_code"] == f"{q:08x}"
            assert result["bch_error_positions"] == list(flipped)
            assert abs(result["decoded_score"] - clean @ p / np.linalg.norm(p)) < 1e-12
            assert result["decoding_error_rate"] == 0.0
            assert result["corrected_distance"] == result["code_distance"]
    zero = readout.semantic_channel(np.zeros(320), profile, owner, 0x12345678)
    assert zero["bch_success"] and not zero["read"] and not zero["found"]
    # Fixed six-error word is outside the five-error ball around zero.
    invalid = 0x3f
    assert not codec.decode(invalid)["success"]
    p = np.asarray(codec.signs(profile, owner))
    for bit in range(59):
        if invalid >> bit & 1:
            p[codec.BOUNDS[bit]:codec.BOUNDS[bit + 1]] *= -1
    failed = readout.semantic_channel(p, profile, owner, 0)
    assert not failed["read"] and failed["decoded_code"] is None
    assert failed["decoded_score"] is None
    assert abs(zero["decoded_threshold"] - 8.566138863740473) < 1e-12
    assert abs(zero["recomputed_threshold"] - 5.386772268905419) < 1e-12
    assert not {"q_target", "h_target", "source", "source_id"}.intersection(inspect.signature(readout.detect_rgb).parameters)
    print(json.dumps({"corrected_score_cases": 15, "zero_energy_abstention": True,
                      "decoder_failure_has_null_code": True, "frozen_thresholds": True,
                      "no_target_parameter": True, "outcome": "passed"}))


if __name__ == "__main__":
    main()
