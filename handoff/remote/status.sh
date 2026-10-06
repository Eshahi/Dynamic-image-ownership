#!/bin/bash
# Progress of held-out continuation 1. On the server: bash /root/status.sh
cd /workspace/m1b
J="W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/m1b-confirm/artifacts/M1b-test/coco512-confirm-rerun-1/outputs/journal.jsonl"
date -u +%H:%M:%S
echo "dispatcher alive: $(pgrep -fc 'dispatch_experiment[.]py')"
[ -f "$J" ] && echo "journal rows: $(wc -l < "$J") (the parent had 155; full plan about 7,500)"
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader
tail -c 400 /workspace/m1b-confirm/continuation-1/dispatch.log 2>/dev/null
