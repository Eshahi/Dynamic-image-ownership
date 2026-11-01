"""SERVER ONLY: lean F6 setup. Reuses the retained Stage S setup steps; reuses verified files on disk."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

import f6l_common as lean_common
import tifs_common as common
import tifs_stage_s_setup as setup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--venv", required=True, type=Path)
    parser.add_argument("--instance-start-utc", required=True)
    parser.add_argument("--hourly-usd", required=True, type=float)
    args = parser.parse_args()
    if platform.system() != "Linux" or Path("/mnt/c/Users").exists():
        raise RuntimeError("Setup is Linux server only; laptop execution prohibited")
    lean = lean_common.load_lean()
    root = args.assets.resolve()
    root.mkdir(parents=True, exist_ok=True)
    deadline = setup.Deadline(args.instance_start_utc, max_hours=lean_common.hours_cap(lean, args.hourly_usd))
    plan = common.load_json(setup.HERE / "asset-plan.json")
    config = common.load_json(setup.ROOT / "research/encoder-transfer-20261019/stage2b-config.json")
    manifest = common.load_json(setup.HERE / "source-manifest.json")
    sources = setup.verify_sources(root, manifest)
    stage_p_sources = setup.verify_stage_p_sources(root, setup.STAGE_P_MANIFEST, manifest)
    packages = setup.install(args.venv.resolve(), setup.HERE / "requirements.txt", config, deadline)
    ledger = []
    for spec in setup.selected_files(plan):
        setup.fetch(spec, root, deadline, ledger)
    setup.extract_wam(root, plan, deadline)
    setup.prepare_vine(root, plan, deadline)
    common.atomic_json(root / "f6l-setup-ready.json", dict(schema="f6-lean-setup-v1", status="complete",
        instance_start_utc=deadline.start, hourly_usd=args.hourly_usd, sources=sources, stage_p_sources=stage_p_sources,
        packages=packages, assets=ledger, lean_config_sha256=common.sha256_file(lean_common.LEAN_CONFIG),
        user_choice_sha256=common.sha256_file(lean_common.ROOT / lean["user_choice"]),
        finished_utc=datetime.now(timezone.utc).isoformat()))


if __name__ == "__main__":
    sys.exit(main())
