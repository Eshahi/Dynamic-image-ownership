"""Print prospective C4 case metadata; no images, models, outputs or approval."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.embedding.development_case import freeze_case

if __name__ == "__main__":
    print(json.dumps(freeze_case(ROOT), sort_keys=True, indent=2, allow_nan=False))
