"""Validate A5 configuration syntax and cross-field invariants; no model loading."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator

from noise_path_reference import leading_suffix


def _reject_constant(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def strict_json(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=_reject_constant)
    def visit(item):
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("nonfinite numeric value")
        if isinstance(item, dict):
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    return value


def detector_id(config):
    dct = dict(config["dct"])
    dct.pop("config_id", None)
    static = {"feature": config["feature"], "signature": config["signature"], "dct": dct}
    raw = json.dumps(static, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate(config, schema):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(config)
    def reject_placeholders(item):
        if isinstance(item, str):
            if item.casefold() in {"tbd", "unknown", "placeholder"}:
                raise ValueError("placeholder value is not a configuration")
            if len(item) == 64 and set(item) == {"0"}:
                raise ValueError("zero SHA sentinel is not an artifact digest")
        elif isinstance(item, dict):
            for child in item.values():
                reject_placeholders(child)
        elif isinstance(item, list):
            for child in item:
                reject_placeholders(child)
    reject_placeholders(config)
    if detector_id(config) != config["dct"]["config_id"]:
        raise ValueError("detector_config_id does not match static feature/signature/DCT configuration")
    scheduler = config["embedding"]["scheduler"]
    leading_suffix(scheduler["inference_steps"], scheduler["strength"])
    if config["embedding"]["alpha_s"] == 0 and config["embedding"]["alpha_i"] == 0:
        raise ValueError("both key-derived carrier strengths cannot be zero")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    validate(strict_json(args.config), strict_json(args.schema))
    print(json.dumps({"valid_structure": True, "scientific_execution_authorized": False}))


if __name__ == "__main__":
    main()
