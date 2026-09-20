"""Reviewed synthetic CPU-only entrypoint; emits no scientific evidence."""
import argparse
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True); parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    rows=[{"run_id":f"seed-{seed}","seed":seed,"condition":"noop","status":"completed","value":0.0} for seed in manifest["seeds"]]
    out=Path(args.output_dir)/"metrics/values.json"; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8")
    print("Synthetic no-op complete; no GPU or network used")

if __name__=="__main__": main()
