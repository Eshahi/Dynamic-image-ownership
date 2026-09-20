#!/usr/bin/env bash
set -euo pipefail
installer_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$installer_dir/install.py" "$@"
