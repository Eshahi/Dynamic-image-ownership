"""Explicit, conservative profile installer; no destructive rollback or global defaults."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
NAMES=["thesis-workflow-control","thesis-research-handoff","thesis-literature-synthesis","thesis-experiment-design","thesis-compute-runner","thesis-results-analysis","thesis-evidence-audit","thesis-writing"]
PROFILES={"controller":NAMES[:2],"worker":NAMES,"reviewer":[NAMES[i] for i in (2,5,6,7)]}

def install(profile,target,dry_run=True,force=False,allow_global=False):
    target=Path(target).expanduser().absolute()
    home=Path.home().resolve()
    protected=[home/".codex",home/".hermes",home/".agents"]
    for name in ("CODEX_HOME","HERMES_HOME"):
        if os.environ.get(name): protected.append(Path(os.environ[name]).expanduser().resolve())
    global_path=any(target.resolve()==p or target.resolve().is_relative_to(p) for p in protected)
    if global_path and not allow_global: raise ValueError("Global skill directory requires --allow-global even in preview")
    for parent in [target,*target.parents]:
        if parent.is_symlink() or (hasattr(parent,"is_junction") and parent.is_junction()): raise ValueError("Installer target must not contain symlinks or junctions")
    plan=[]
    for name in PROFILES[profile]:
        for base,destbase in [(ROOT/"skills"/name,target/name),(ROOT/"src/thesis_agents",target/name/"scripts/_runtime/thesis_agents")]:
            for source in sorted(base.rglob("*")):
                if not source.is_file() or "__pycache__" in source.parts or "_runtime" in source.parts or source.suffix==".pyc": continue
                if source.is_symlink(): raise ValueError("Source symlinks are not installable")
                dest=destbase/source.relative_to(base)
                for component in [dest,*dest.parents]:
                    if component==target.parent: break
                    if component.is_symlink() or (hasattr(component,"is_junction") and component.is_junction()): raise ValueError("Existing target contains link")
                if dest.exists() and not force: raise FileExistsError("Refusing overwrite; use --force after backup: "+str(dest))
                plan.append((source,dest))
    receipt=target/("thesis-install-"+profile+".json")
    if receipt.exists() and not force: raise FileExistsError("Installation receipt exists; preserve previous installation")
    records=[]
    for source,dest in plan:
        sha=hashlib.sha256(source.read_bytes()).hexdigest()
        records.append({"path":dest.relative_to(target).as_posix(),"sha256":sha})
        print(json.dumps({"action":"would-copy" if dry_run else "copy","file":str(dest)},ensure_ascii=True))
        if not dry_run:
            dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,dest)
    if not dry_run:
        receipt.write_text(json.dumps({"profile":profile,"files":records},indent=2)+"\n",encoding="utf-8")
    return {"dry_run":dry_run,"profile":profile,"files":len(records)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile",choices=PROFILES,required=True); p.add_argument("--target",required=True)
    p.add_argument("--dry-run",action="store_true"); p.add_argument("--execute",action="store_true"); p.add_argument("--force",action="store_true"); p.add_argument("--allow-global",action="store_true")
    a=p.parse_args()
    if a.dry_run and a.execute: p.error("Choose --dry-run or --execute")
    try: print(json.dumps(install(a.profile,a.target,not a.execute,a.force,a.allow_global)))
    except (ValueError,OSError) as exc: print(str(exc),file=sys.stderr); return 2
    return 0

if __name__=="__main__": raise SystemExit(main())
