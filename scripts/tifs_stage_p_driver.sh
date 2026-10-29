#!/usr/bin/env bash
# SERVER ONLY. Run only after external pre-output choice/setup.
# ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD USER_CHOICE_JSON
set -euo pipefail
[ "$#" -eq 5 ] || { echo 'Expected ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD USER_CHOICE_JSON' >&2; exit 1; }
cd "$(dirname "$0")/.."
PY=${TIFS_PYTHON:-/workspace/venv/bin/python}
ASSETS=$1; RUN_ROOT=$2; START=$3; PRICE=$4; CHOICE=$5
mkdir -p "$RUN_ROOT"
RUN_ROOT=$(cd "$RUN_ROOT" && pwd)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
SELECT=("$PY" scripts/tifs_stage_p_select.py)
SELECT_OPTS=(--run-root "$RUN_ROOT" --user-choice "$CHOICE")
MAX_HOURS=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["max_instance_hours"])' "$CHOICE")
invoke() {
  local log=$1; shift
  local rc=0
  "$@" >> "$log" 2>&1 || rc=$?
  printf '%s exit=%s log=%s\n' "$(date -u +%FT%TZ)" "$rc" "$log" >> "$RUN_ROOT/driver.log"
  # Terminal missing data must finish its frozen inventory before analysis.
  case "$rc" in 0|4) ;; *) exit "$rc" ;; esac
}
run_trial() {
  local partition=$1 trial=$2 count=$3
  local out="$RUN_ROOT/$partition/$trial"
  local opts=(--assets "$ASSETS" --out "$out" --config "$out/config.json" --stage-p-count "$count"
    --instance-start-utc "$START" --max-hours "$MAX_HOURS" --hourly-usd "$PRICE" --user-choice "$CHOICE")
  if [ "$count" -eq 2 ]; then opts+=(--stage-p-calibration); fi
  # Sequential processes preserve the one-GPU resource model and C0 replay.
  for action in prepare clean native; do
    invoke "$out/$action.log" "$PY" scripts/tifs_stage_s.py --stage "$action" "${opts[@]}"
  done
  invoke "$out/detect.log" "$PY" scripts/tifs_stage_s_read.py --stage detect "${opts[@]}"
  invoke "$out/quality.log" "$PY" scripts/tifs_stage_s_read.py --stage quality "${opts[@]}"
}
"${SELECT[@]}" plan "${SELECT_OPTS[@]}" >> "$RUN_ROOT/selection.log"
# Calibration uses only the first2 Stage P tuning sources. Outputs and journals
# are reused by rung1; no Stage S donor/target/rehearsal source is opened.
calibration_trials=$("${SELECT[@]}" calibration "${SELECT_OPTS[@]}")
while IFS= read -r trial; do
  [ -n "$trial" ] && run_trial tune "$trial" 2
done <<< "$calibration_trials"
"$PY" scripts/tifs_stage_s_forecast.py --stage-p-root "$RUN_ROOT" \
  --config research/tifs-20261028/stage-s/frozen-config.json --user-choice "$CHOICE" \
  --instance-start-utc "$START" --destination "$RUN_ROOT/forecast.json" >> "$RUN_ROOT/forecast.log" 2>&1
for n in 4 8 16; do
  # Capture first: a command failure cannot be hidden by process substitution.
  trials=$("${SELECT[@]}" entrants "${SELECT_OPTS[@]}" --count "$n")
  run_trial tune retained-f5 "$n"
  while IFS= read -r trial; do
    [ -n "$trial" ] && run_trial tune "$trial" "$n"
  done <<< "$trials"
  if [ "$n" -eq 16 ]; then
    controls=$("${SELECT[@]}" finalist-controls "${SELECT_OPTS[@]}")
    while IFS= read -r trial; do
      [ -n "$trial" ] && run_trial tune "$trial" 16
    done <<< "$controls"
  fi
  "${SELECT[@]}" advance "${SELECT_OPTS[@]}" --count "$n" >> "$RUN_ROOT/selection.log"
done
# This is the first operation permitted to create check configurations; its
# prerequisite is the immutable nominated tuning winner, never a runner-up.
check_trials=$("${SELECT[@]}" plan-check "${SELECT_OPTS[@]}")
while IFS= read -r trial; do
  [ -n "$trial" ] && run_trial check "$trial" 8
done <<< "$check_trials"
"${SELECT[@]}" finish "${SELECT_OPTS[@]}" >> "$RUN_ROOT/selection.log"
