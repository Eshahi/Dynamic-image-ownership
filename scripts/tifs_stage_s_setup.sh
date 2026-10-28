#!/usr/bin/env bash
# Future authorized Linux server only. This never starts rehearsal or screen.
# Usage: bash scripts/tifs_stage_s_setup.sh ASSETS VENV ACTUAL_INSTANCE_START_UTC
set -euo pipefail
[ "$#" -eq 3 ] || { echo 'Expected ASSETS VENV ACTUAL_INSTANCE_START_UTC' >&2; exit 1; }
cd "$(dirname "$0")/.."
exec "${TIFS_BOOTSTRAP_PYTHON:-python3}" scripts/tifs_stage_s_setup.py --assets "$1" --venv "$2" --instance-start-utc "$3"
