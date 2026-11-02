#!/usr/bin/env bash
# SERVER ONLY. Setup (scripts/f6l_setup.py) runs first, as its own step.
# Usage: bash scripts/f6l_driver.sh ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [lean|f7]
# lean (default) runs probe, then stages 1 to 3, and stops as soon as a fixed rule says stop.
# f7 runs the F7 dual-carrier test: Stage S rehearsal, then screen, then its fixed verdict.
# Exit codes: 0 finished with a GO label, 2 scientific stop, 3 resource stop, 4 incomplete.
# The instance keeps billing after this exits: fetch the results, then stop it by hand.
set -euo pipefail
[ "$#" -eq 4 ] || [ "$#" -eq 5 ] || { echo 'Expected ASSETS RUN_ROOT INSTANCE_START_UTC HOURLY_USD [lean|f7]' >&2; exit 1; }
cd "$(dirname "$0")/.."
PY=${TIFS_PYTHON:-/workspace/venv/bin/python}
ASSETS=$1; RUN_ROOT=$2; START=$3; PRICE=$4; MODE=${5:-lean}
case "$MODE" in lean|f7) ;; *) echo 'Mode must be lean or f7' >&2; exit 1 ;; esac
mkdir -p "$RUN_ROOT"
RUN_ROOT=$(cd "$RUN_ROOT" && pwd)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
export PYTHONPATH="$PWD/scripts${PYTHONPATH:+:$PYTHONPATH}"
INCOMPLETE=0
CURRENT_PHASE=
CURRENT_OUT=
note() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$RUN_ROOT/driver.log"; }
# Record what the phase has before leaving, so a stop still has a report. A rehearsal has no verdict of its own.
resource_stop() {
  note RESOURCE_STOP
  if [ "$CURRENT_PHASE" != probe ] && [ -n "$CURRENT_OUT" ] && [ "$(basename "$CURRENT_OUT")" != rehearsal ] && [ -f "$CURRENT_OUT/prepared.json" ]; then
    "$PY" scripts/f6l_select.py --action decide --phase "$CURRENT_PHASE" --out "$CURRENT_OUT" >> "$CURRENT_OUT/decide.log" 2>&1 || true
  fi
  exit 3
}
# A missing unit stays missing and the rest of the fixed inventory still runs.
invoke() {
  local logfile=$1; shift
  local rc=0
  "$@" >> "$logfile" 2>&1 || rc=$?
  note "exit=$rc $(basename "$logfile")"
  case "$rc" in
    0) ;;
    4) INCOMPLETE=1 ;;
    3) resource_stop ;;
    *) note "IMPLEMENTATION_STOP rc=$rc"; exit "$rc" ;;
  esac
}
stage_run() {
  local phase=$1 out=$2 action=$3; shift 3
  CURRENT_PHASE=$phase; CURRENT_OUT=$out
  invoke "$out/$action.log" "$PY" scripts/f6l_run.py --phase "$phase" --stage "$action" --out "$out" \
    --assets "$ASSETS" --instance-start-utc "$START" --hourly-usd "$PRICE" "$@"
}
# CPU-bound readers: four processes raised Phase B throughput from .53 to 1.24 rows per second.
read_all() {
  local phase=$1 out=$2; shift 2
  local pids=() i r resource=0 fatal=0
  for i in 0 1 2 3; do
    "$PY" scripts/f6l_run.py --phase "$phase" --stage detect --out "$out" --assets "$ASSETS" --instance-start-utc "$START" \
      --hourly-usd "$PRICE" --worker "$i/4" --threads 4 "$@" >> "$out/detect-$i.log" 2>&1 & pids+=($!)
  done
  for i in "${pids[@]}"; do
    r=0
    wait "$i" || r=$?
    note "exit=$r detect worker pid=$i"
    case "$r" in
      0) ;;
      4) INCOMPLETE=1 ;;
      3) resource=1 ;;
      *) fatal=$r ;;
    esac
  done
  if [ "$fatal" -ne 0 ]; then note "IMPLEMENTATION_STOP rc=$fatal"; exit "$fatal"; fi
  if [ "$resource" -ne 0 ]; then resource_stop; fi
  stage_run "$phase" "$out" quality "$@"
}
decide() {
  local phase=$1 out=$2 rc=0
  "$PY" scripts/f6l_select.py --action decide --phase "$phase" --out "$out" >> "$out/decide.log" 2>&1 || rc=$?
  note "decide $phase exit=$rc"
  case "$rc" in 0) ;; *) exit "$rc" ;; esac
}
fit_check() {
  local phase=$1 previous=$2 rc=0
  "$PY" scripts/f6l_select.py --action fit --phase "$phase" --root "$RUN_ROOT" --previous "$previous" \
    --instance-start-utc "$START" --hourly-usd "$PRICE" >> "$RUN_ROOT/fit.log" 2>&1 || rc=$?
  note "fit $phase exit=$rc"
  case "$rc" in 0) ;; *) exit "$rc" ;; esac
}
plan() {
  local phase=$1 out=$2; shift 2
  mkdir -p "$out"
  "$PY" scripts/f6l_run.py --phase "$phase" --stage plan --out "$out" "$@" >> "$out/plan.log" 2>&1
}

if [ "$MODE" = f7 ]; then
  # The rehearsal must finish without implementation errors before the screen is paid for.
  for mode in rehearsal screen; do
    OUT="$RUN_ROOT/f7/$mode"
    plan f7 "$OUT"
    FLAG=(); if [ "$mode" = rehearsal ]; then FLAG=(--rehearsal); fi
    stage_run f7 "$OUT" prepare "${FLAG[@]}"
    stage_run f7 "$OUT" clean
    stage_run f7 "$OUT" native "${FLAG[@]}"
    stage_run f7 "$OUT" threats
    stage_run f7 "$OUT" secondary
    read_all f7 "$OUT"
    if [ "$mode" = rehearsal ]; then
      [ "$INCOMPLETE" -eq 0 ] || { note 'f7 rehearsal incomplete'; exit 4; }
      rc=0
      "$PY" scripts/f6l_select.py --action fit --phase f7 --root "$RUN_ROOT" --instance-start-utc "$START" \
        --hourly-usd "$PRICE" >> "$RUN_ROOT/fit.log" 2>&1 || rc=$?
      note "fit f7 exit=$rc"
      [ "$rc" -eq 0 ] || exit "$rc"
    fi
  done
  decide f7 "$OUT"
  note FINISHED
  exit 0
fi

# Probe: exact native replay on one source, then gradient and timing checks. No marks are read.
P="$RUN_ROOT/probe"
plan probe "$P"
stage_run probe "$P" prepare
stage_run probe "$P" clean
stage_run probe "$P" native --rehearsal
[ "$INCOMPLETE" -eq 0 ] || { note 'probe replay incomplete'; exit 4; }
stage_run probe "$P" probe
[ "$INCOMPLETE" -eq 0 ] || { note 'probe incomplete'; exit 4; }

# Stage 1: every arm on four sources, one seed. Arms failing strict clean quality stop there.
S1="$RUN_ROOT/stage1"
plan stage1 "$S1"
stage_run stage1 "$S1" prepare
stage_run stage1 "$S1" clean
stage_run stage1 "$S1" quality
"$PY" scripts/f6l_select.py --action clean-gate --phase stage1 --out "$S1" >> "$S1/decide.log" 2>&1
stage_run stage1 "$S1" native
read_all stage1 "$S1"
decide stage1 "$S1"

# Stage 2: finalists and controls on the next twelve sources, three seeds.
fit_check stage2 "$S1/decision.json"
S2="$RUN_ROOT/stage2"
plan stage2 "$S2" --previous "$S1/decision.json"
stage_run stage2 "$S2" prepare
stage_run stage2 "$S2" clean
stage_run stage2 "$S2" native
read_all stage2 "$S2"
decide stage2 "$S2"

# Stage 3: the one winner on disjoint Stage S sources, with baselines, threats and distortions.
fit_check stage3 "$S2/decision.json"
# An arm lost in an earlier stage must not stop this one: only this stage's own rehearsal counts.
INCOMPLETE=0
for mode in rehearsal screen; do
  S3="$RUN_ROOT/stage3/$mode"
  plan stage3 "$S3" --previous "$S2/decision.json"
  FLAG=(); if [ "$mode" = rehearsal ]; then FLAG=(--rehearsal); fi
  stage_run stage3 "$S3" prepare "${FLAG[@]}"
  stage_run stage3 "$S3" clean
  stage_run stage3 "$S3" native "${FLAG[@]}"
  stage_run stage3 "$S3" threats
  stage_run stage3 "$S3" secondary
  read_all stage3 "$S3"
  if [ "$mode" = rehearsal ] && [ "$INCOMPLETE" -ne 0 ]; then note 'stage 3 rehearsal incomplete'; exit 4; fi
done
decide stage3 "$S3"
note FINISHED
