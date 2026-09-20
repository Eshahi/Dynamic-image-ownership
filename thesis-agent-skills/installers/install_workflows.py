"""Install reviewed local workflows and fixed safe-step extension via Spec Kit."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def install(project,execute=False):
    project=Path(project).resolve()
    for name in ("thesis-lifecycle","thesis-smoke"):
        if (project/".specify/workflows"/name).exists(): raise FileExistsError("Workflow already installed; review update explicitly")
    step_target=project/".specify/workflows/steps/thesis-safe"
    if step_target.exists(): raise FileExistsError("Step extension already installed")
    for p in [project,*project.parents]:
        if p.is_symlink(): raise ValueError("Project links are not supported")
    commands=[[sys.executable,"-c","from specify_cli import main; main()","workflow","add",str(ROOT/"spec-kit/workflows"/name)] for name in ("thesis-lifecycle","thesis-smoke")]
    if execute:
        (project/".specify").mkdir(parents=True,exist_ok=True)
        for source in sorted((ROOT/"spec-kit/steps/thesis-safe").glob("*")):
            if source.is_file():
                step_target.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,step_target/source.name)
        for command in commands:
            subprocess.run(command,cwd=project,check=True,stdin=subprocess.DEVNULL)
    return {"dry_run":not execute,"step_package":"thesis-safe","commands":commands}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--project",required=True); p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    try: print(json.dumps(install(a.project,a.execute)))
    except (OSError,ValueError,subprocess.CalledProcessError) as exc: print(str(exc),file=sys.stderr); return 2
    return 0

if __name__=="__main__": raise SystemExit(main())
