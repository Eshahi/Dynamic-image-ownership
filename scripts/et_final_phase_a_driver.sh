#!/usr/bin/env bash
# Phase A driver after stage 1 (written by Claude, Opus 5.5, 2026-10-26, under the user's Phase-A approval).
# Order fixed by 05-informed-attacks.md and 07-final-experiment.md: attack quality grids -> selection freeze ->
# controls -> detector release (CPU-bound) in parallel with the GPU mechanism module (SDXL, K3) -> fit/freeze.
# Every stage is resumable; rerunning this script continues from the journals.
set -u
cd /workspace/thesis
OUT=/workspace/runs/et-phase-a
ARGS="--assets /workspace/assets --images /workspace/runs/stage2a-full/images --out $OUT"
PY=/workspace/venv/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
log() { echo "$(date -u +%FT%TZ) $*" >> "$OUT/driver.log"; }
log "driver waiting for stage 1 and the SD1.5 mechanism run"
while ! grep -q STAGE1_EXIT /workspace/runs/et-phase-a-stage1.log; do sleep 60; done
while tmux has-session -t mechR0 2>/dev/null; do sleep 60; done
log "attack grid start"
$PY scripts/et_final_phase_a_attacks.py --stage grid $ARGS >> "$OUT/attacks.log" 2>&1; log "attack grid exit $?"
if [ ! -f "$OUT/attack-freeze.json" ]; then
  $PY scripts/et_final_phase_a_attacks.py --stage select $ARGS >> "$OUT/attacks.log" 2>&1; log "attack select exit $?"
fi
$PY scripts/et_final_phase_a_attacks.py --stage controls $ARGS >> "$OUT/attacks.log" 2>&1; log "attack controls exit $?"
$PY scripts/et_final_phase_a_fit.py --stage detect --assets /workspace/assets --out "$OUT" >> "$OUT/detect.log" 2>&1 &
DET=$!
$PY scripts/et_final_phase_a_mechanism.py $ARGS --families R1,K3 >> /workspace/runs/et-phase-a-mechanism.log 2>&1; log "mechanism exit $?"
wait $DET; log "detect exit $?"
$PY scripts/et_final_phase_a_fit.py --stage fit --assets /workspace/assets --out "$OUT" >> "$OUT/fit.log" 2>&1; log "fit exit $?"
log "PHASE_A_COMPUTE_DONE"
