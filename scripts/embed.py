"""C4 CLI contract preflight only; never bypass scientific runner approval."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.runtime.config import ConfigError, load_method_config
from src.embedding.proposed import Settings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preview", action="store_true", help="validate bytes only, without loading a model")
    args = parser.parse_args(argv)
    try:
        config = load_method_config(args.config)
        settings = Settings.from_embedding_config(config.value["embedding"])
    except (ConfigError, ValueError, KeyError) as error:
        print(json.dumps({"status": "invalid_config", "error": str(error), "scientific_execution_authorized": False}))
        return 2
    record = {"status": "component_preflight_only" if args.preview else "execution_adapter_not_ready",
              "config_sha256": config.sha256, "inference_steps": settings.inference_steps,
              "scientific_execution_authorized": False,
              "missing": ["approved exact execution manifest and runner worker", "verified component loader",
                          "safety and RGB8 PNG roundtrip", "quality metrics and full blind detector"]}
    print(json.dumps(record, sort_keys=True))
    return 0 if args.preview else 4


if __name__ == "__main__":
    sys.exit(main())
