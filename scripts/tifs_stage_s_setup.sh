#!/usr/bin/env bash
# Future authorized Linux server only. This never starts rehearsal or screen.
# Usage: bash scripts/tifs_stage_s_setup.sh ASSETS VENV ACTUAL_INSTANCE_START_UTC [--user-choice PATH]
# Optional --config PATH binds a different committed base-config location.
# The external receipt is recorded by Claude before server output. Setup never
# creates one and never needs selected-config.json, which does not exist pre-P.
set -euo pipefail
[ "$#" -ge 3 ] || { echo 'Expected ASSETS VENV ACTUAL_INSTANCE_START_UTC [--user-choice PATH] [--config PATH]' >&2; exit 1; }
cd "$(dirname "$0")/.."
ASSETS=$1; VENV=$2; START=$3
shift 3
exec "${TIFS_BOOTSTRAP_PYTHON:-python3}" scripts/tifs_stage_s_setup.py --assets "$ASSETS" --venv "$VENV" --instance-start-utc "$START" "$@"
