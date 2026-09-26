"""Full-shaped synthetic config bytes only; not a scientific config/approval."""
import copy
import hashlib
import json

from src.runtime.config import LoadedConfig, SCHEMA


def loaded_fixture(settings, component_hashes=None):
    schema = json.loads(SCHEMA.read_bytes())
    def specimen(rule):
        if "$ref" in rule:
            return specimen(schema["$defs"][rule["$ref"].split("/")[-1]])
        if "const" in rule: return copy.deepcopy(rule["const"])
        kind = rule.get("type")
        if kind == "object": return {name: specimen(rule["properties"][name]) for name in rule["required"]}
        if kind == "integer": return max(rule.get("minimum", 0), 1)
        if kind == "number": return 1 if "exclusiveMinimum" in rule else rule.get("minimum", 0)
        if kind == "string": return "a"*64
        raise AssertionError(rule)
    value = specimen(schema)
    e = value["embedding"]
    e["scheduler"].update(inference_steps=settings.inference_steps, strength=settings.strength)
    e["working_image"]["maximum_side"] = settings.maximum_side
    e.update(vae_scale=settings.vae_scale, alpha_s=settings.alpha_s, alpha_i=settings.alpha_i, rho=settings.rho, noise_seed=7)
    e["optimizer"].update(learning_rate=settings.learning_rate, iterations=settings.iterations)
    e["loss"] = {name: getattr(settings, name) for name in ("lambda_q", "lambda_r", "lambda_s", "lambda_i", "margin_s", "margin_i")}
    if component_hashes is not None: e["model_component_hashes"] = component_hashes
    dct = dict(value["dct"])
    dct.pop("config_id")
    raw_static = json.dumps({"feature": value["feature"], "signature": value["signature"], "dct": dct},
                            sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    value["dct"]["config_id"] = hashlib.sha256(raw_static).hexdigest()
    raw = json.dumps(value).encode("utf-8")
    return LoadedConfig(value, raw, hashlib.sha256(raw).hexdigest(), hashlib.sha256(SCHEMA.read_bytes()).hexdigest())
