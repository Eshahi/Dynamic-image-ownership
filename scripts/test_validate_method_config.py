"""Structural contract regressions with synthetic values; no scientific config is supplied."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import ValidationError

from validate_method_config import detector_id, validate


SCHEMA = json.loads((Path(__file__).parents[1] / "configs" / "method.schema.json").read_text(encoding="utf-8"))


def specimen(rule):
    if "$ref" in rule:
        return specimen(SCHEMA["$defs"][rule["$ref"].split("/")[-1]])
    if "const" in rule:
        return copy.deepcopy(rule["const"])
    kind = rule.get("type")
    if kind == "object":
        return {name: specimen(rule["properties"][name]) for name in rule["required"]}
    if kind == "integer":
        return max(rule.get("minimum", 0), 1)
    if kind == "number":
        return 1 if "exclusiveMinimum" in rule else rule.get("minimum", 0)
    if kind == "string":
        return "a" * 64
    raise AssertionError(rule)


class MethodContractTests(unittest.TestCase):
    def setUp(self):
        self.config = specimen(SCHEMA)
        self.config["embedding"]["scheduler"]["strength"] = 1
        self.config["embedding"]["alpha_s"] = 1
        self.config["dct"]["config_id"] = detector_id(self.config)

    def test_synthetic_structure_can_pass(self):
        self.assertTrue(validate(self.config, SCHEMA))

    def test_required_calibration_cannot_be_omitted(self):
        del self.config["calibration"]["tau_i"]
        with self.assertRaises(ValidationError):
            validate(self.config, SCHEMA)

    def test_static_config_id_detects_change(self):
        self.config["feature"]["clip"]["projection_seed"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "detector_config_id"):
            validate(self.config, SCHEMA)

    def test_empty_schedule_is_rejected(self):
        self.config["embedding"]["scheduler"]["strength"] = 0.01
        self.config["embedding"]["scheduler"]["inference_steps"] = 1
        with self.assertRaisesRegex(ValueError, "empty reverse suffix"):
            validate(self.config, SCHEMA)

    def test_zero_carriers_rejected(self):
        self.config["embedding"]["alpha_s"] = 0
        self.config["embedding"]["alpha_i"] = 0
        with self.assertRaisesRegex(ValueError, "strengths cannot be zero"):
            validate(self.config, SCHEMA)

    def test_placeholder_threshold_rejected(self):
        self.config["calibration"]["threshold_version"] = "tBd"
        with self.assertRaisesRegex(ValueError, "placeholder"):
            validate(self.config, SCHEMA)

    def test_zero_digest_rejected(self):
        self.config["embedding"]["model_component_hashes"]["vae"] = "0" * 64
        with self.assertRaises(ValidationError):
            validate(self.config, SCHEMA)

    def test_image_io_and_guidance_required(self):
        del self.config["image_io"]
        with self.assertRaises(ValidationError):
            validate(self.config, SCHEMA)
        self.config = specimen(SCHEMA)
        self.config["embedding"]["scheduler"]["strength"] = 1
        self.config["embedding"]["alpha_s"] = 1
        self.config["dct"]["config_id"] = detector_id(self.config)
        del self.config["embedding"]["guidance_scale"]
        with self.assertRaises(ValidationError):
            validate(self.config, SCHEMA)


if __name__ == "__main__":
    unittest.main()
