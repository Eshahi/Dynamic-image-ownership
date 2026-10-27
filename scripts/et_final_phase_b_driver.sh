#!/usr/bin/env bash
# Phase B driver under amendment B1 (written by Claude, Opus 5.5, 2026-10-26).
# Usage: bash scripts/et_final_phase_b_driver.sh OUT_DIR [--rehearsal 1790,1822]
# Order (AMENDMENT-B1 section 5): acquire -> clean -> forecast + seal -> outcome, with the detector release and
# quality reading already-written outputs in parallel after the seal (they start after K3 has loaded) -> final passes.
# Every stage resumes from its journal; rerunning this script continues.
set -u
cd /workspace/thesis
OUT=$1; shift
EXTRA="$*"
PY=/workspace/venv/bin/python
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
A="--assets /workspace/assets --out $OUT $EXTRA"
R="--assets /workspace/assets --out $OUT"
mkdir -p "$OUT"
log() { echo "$(date -u +%FT%TZ) $*" >> "$OUT/driver.log"; }
log "driver start ($EXTRA)"
if [ -z "$EXTRA" ] && [ ! -f "$OUT/phase-b-sources.json" ]; then
  $PY scripts/et_final_phase_b.py --stage acquire $A >> "$OUT/acquire.log" 2>&1; log "acquire exit $?"
fi
[ -f "$OUT/phase-b-sources.json" ] || [ -n "$EXTRA" ] || { log "no frozen source list; stop"; exit 1; }
K=${CLEAN_SHARDS:-1}  # parallel marking on slow-core machines: K shards over sources[i::K], then a merge
if [ "$K" -gt 1 ]; then
  for i in $(seq 0 $((K - 1))); do
    $PY scripts/et_final_phase_b.py --stage clean $A --shard $i/$K --threads ${SHARD_THREADS:-16} >> "$OUT/clean-$i.log" 2>&1 &
  done
  wait; log "clean shards done"
  $PY scripts/et_final_phase_b.py --stage merge-clean $A >> "$OUT/clean.log" 2>&1; log "clean merge exit $?"
else
  $PY scripts/et_final_phase_b.py --stage clean $A >> "$OUT/clean.log" 2>&1; log "clean exit $?"
fi
if [ ! -f "$OUT/forecast-seal.json" ]; then
  $PY scripts/et_final_phase_b.py --stage forecast $A >> "$OUT/forecast.log" 2>&1; log "forecast exit $?"
fi
[ -f "$OUT/forecast-seal.json" ] || { log "no forecast seal; stop"; exit 1; }
$PY scripts/et_final_phase_b.py --stage outcome $A >> "$OUT/outcome.log" 2>&1 &
OC=$!
sleep 600
while kill -0 $OC 2>/dev/null; do
  $PY scripts/et_final_phase_b_read.py --stage detect $R --threads ${DETECT_THREADS:-8} >> "$OUT/detect.log" 2>&1
  $PY scripts/et_final_phase_b_read.py --stage quality $R --threads 4 >> "$OUT/quality.log" 2>&1
  sleep 120
done
wait $OC; log "outcome exit $?"
$PY scripts/et_final_phase_b_read.py --stage quality $R --threads 6 >> "$OUT/quality.log" 2>&1 &
QP=$!
$PY scripts/et_final_phase_b_read.py --stage detect $R --threads ${DETECT_THREADS_FINAL:-10} >> "$OUT/detect.log" 2>&1; log "detect exit $?"
wait $QP; log "quality exit $?"
$PY research/encoder-transfer-20261019/final-study-20261025/phase-b/analyze_phase_b.py "$OUT" \
    research/encoder-transfer-20261019/final-study-20261025/phase-b/amendment-b1.json "$OUT/phase-b-results.json" "$OUT/phase-b-tables.md" \
    >> "$OUT/analysis.log" 2>&1; log "analysis exit $?"
log "PHASE_B_COMPUTE_DONE"
