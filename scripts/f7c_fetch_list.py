"""Server side, stdlib only: list the f7c files to fetch, relative to /workspace/runs/f6l/f7c.

Journals, configs and logs of both runs, plus every clean, native and threat image of the f7 and unmarked arms
written in the screen. Writes /workspace/f7c-fetch-list.txt for `tar -T`.
"""
import glob
import json
import os

ROOT = "/workspace/runs/f6l/f7c"
out = []
for run in ("rehearsal", "screen"):
    for pattern in ("*.jsonl", "*.json", "*.log"):
        out += [os.path.relpath(p, ROOT) for p in sorted(glob.glob(os.path.join(ROOT, run, pattern)))]
images = set()
for name in ("clean.jsonl", "native.jsonl", "threats.jsonl"):
    for line in open(os.path.join(ROOT, "screen", name), encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            path = (r.get("output") or {}).get("path")
            if r.get("arm") in ("f7", "unmarked") and r.get("status") == "ok" and path and os.path.exists(path):
                images.add(os.path.relpath(path, ROOT))
out += sorted(images)
open("/workspace/f7c-fetch-list.txt", "w").write("\n".join(out) + "\n")
print(len(out), "files,", len(images), "images")
