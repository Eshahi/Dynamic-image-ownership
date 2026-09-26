"""Owned config-contract regressions, never calibrated or executed study runs."""
import copy
import dataclasses
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from src.runtime.config import ConfigError, LoadedConfig, SCHEMA, load_method_config
from src.runtime.feasibility import (FeasibilityConfig, PROFILE, VERSION, CALIBRATION,
    schema_bytes, load_feasibility_config)
from src.embedding.config_binding import validate_loaded_snapshot
from src.embedding.proposed import EmbeddingError, Settings
from tests.c4_fixtures import loaded_fixture

SETTINGS = Settings(10, .2, .18215, 256, .2, .3, .01, .005, 2, 1, 1, 1, 1, .1, .1)


def owned_development_fixture():
    final = loaded_fixture(SETTINGS)
    value = copy.deepcopy(final.value)
    value.update(schema_version=VERSION, profile=PROFILE, calibration=copy.deepcopy(CALIBRATION))
    raw = json.dumps(value).encode("utf-8")
    return FeasibilityConfig(value, raw, hashlib.sha256(raw).hexdigest(), hashlib.sha256(schema_bytes()).hexdigest())


class FeasibilityContractTests(unittest.TestCase):
    def test_real_candidate_metadata_and_full_preview_no_model(self):
        if importlib.util.find_spec("jsonschema") is None:
            self.skipTest("full config loader is in Windows controller")
        from src.embedding.local_assets import plan_assets, bind_config_assets
        root = Path(__file__).resolve().parents[1]
        config = load_feasibility_config(root/"configs/c4-development.json")
        plan = plan_assets(root/"research/a6-candidate-model-assets.json")
        settings = bind_config_assets(config, plan)
        self.assertEqual(config.value["feature"]["clip"]["projection_seed"], "0"*64)
        self.assertEqual(config.value["calibration"], CALIBRATION)
        self.assertEqual(settings.iterations, 2)
        self.assertEqual(settings.maximum_side, 1024)
        self.assertEqual(plan.total_bytes, 2742217630)
        with self.assertRaises(ConfigError): load_method_config(root/"configs/c4-development.json")

    def test_only_profile_version_calibration_derived_from_final_schema(self):
        final = json.loads(SCHEMA.read_bytes()); development = json.loads(schema_bytes())
        self.assertEqual(final["required"], development["required"])
        for key in final["properties"]:
            if key not in ("schema_version", "profile", "calibration"):
                self.assertEqual(final["properties"][key], development["properties"][key])
        self.assertEqual(development["properties"]["calibration"], {"const": CALIBRATION})
        self.assertEqual(final["properties"]["profile"]["const"], "public-derived-existing-image")

    def test_explicit_type_cannot_be_relabelled_as_final_config(self):
        fixture = owned_development_fixture()
        self.assertEqual(validate_loaded_snapshot(fixture), fixture.value)
        forged = LoadedConfig(fixture.value, fixture.raw, fixture.sha256, fixture.schema_sha256)
        with self.assertRaises(EmbeddingError): validate_loaded_snapshot(forged)
        final = loaded_fixture(SETTINGS)
        forged = FeasibilityConfig(final.value, final.raw, final.sha256, final.schema_sha256)
        with self.assertRaises(ValueError): validate_loaded_snapshot(forged)

    def test_added_threshold_or_success_claim_rejected(self):
        fixture = owned_development_fixture()
        for key, value in (("tau_s", 0), ("decision", "permitted"), ("status", "calibrated")):
            changed = copy.deepcopy(fixture.value)
            changed["calibration"][key] = value
            raw = json.dumps(changed).encode("utf-8")
            forged = dataclasses.replace(fixture, value=changed, raw=raw, sha256=hashlib.sha256(raw).hexdigest())
            with self.subTest(key=key), self.assertRaises(ValueError): validate_loaded_snapshot(forged)

    def test_actual_full_validators_keep_final_and_development_separate(self):
        if importlib.util.find_spec("jsonschema") is None:
            self.skipTest("full validators run in Windows controller only")
        fixture = owned_development_fixture()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"owned.json"; path.write_bytes(fixture.raw)
            self.assertEqual(load_feasibility_config(path), fixture)
            with self.assertRaises(ConfigError): load_method_config(path)
            final = loaded_fixture(SETTINGS); path.write_bytes(final.raw)
            self.assertEqual(load_method_config(path), final)
            with self.assertRaises(ConfigError): load_feasibility_config(path)
            for mutate in (lambda v: v["calibration"].update(tau_i=0),
                    lambda v: v["embedding"].update(safety_policy="skip"),
                    lambda v: v["embedding"]["model_component_hashes"].update(vae="0"*64)):
                invalid = copy.deepcopy(fixture.value); mutate(invalid)
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaises(ConfigError): load_feasibility_config(path)


if __name__ == "__main__": unittest.main()
