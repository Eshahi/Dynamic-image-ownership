"""Official-runner entrypoint, fixed offline evaluation worker only."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from prepare_v4_saved_evaluation import contract, core, run_root
from run_v4_study import linux_path

# The worker stops itself first; TERM and KILL follow with room to finalise evidence.
WORKER_MARGIN, TERM_MARGIN, KILL_AFTER, LAUNCH_MARGIN = 900, 420, 300, 360


def command(manifest, output, seconds, worker=None, extra=()):
    execution = core()["execution"]
    worker = worker or Path(__file__).with_name("v4_saved_evaluation_worker.py")
    return ["C:/Windows/System32/wsl.exe","--exec","timeout","--signal=TERM",f"--kill-after={KILL_AFTER}s",
            f"{int(seconds)}s","env","-i",*[name+"="+value for name,value in execution["env"].items()],
            execution["interpreter"],"-B",linux_path(worker),*extra,
            "--manifest",linux_path(manifest),"--output-dir",linux_path(output)]


def launch(manifest, output, seconds, worker=None, extra=()):
    """One exclusive worker log per run directory; identical for scientific and rehearsal runs."""
    env = {k:v for k,v in os.environ.items() if k.upper() in
           {"SYSTEMROOT","WINDIR","PATH","TEMP","TMP","USERPROFILE","LOCALAPPDATA"}}
    with (Path(output)/"logs/evaluation-worker.log").open("x",encoding="utf-8") as log:
        result = subprocess.run(command(manifest,output,seconds,worker,extra),stdin=subprocess.DEVNULL,
                                stdout=log,stderr=subprocess.STDOUT,timeout=seconds+LAUNCH_MARGIN,env=env)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args = parser.parse_args(argv)
    manifest = json.loads(Path(args.manifest).read_text())
    contract(manifest)
    if Path(args.output_dir).resolve() != Path(run_root(manifest)).resolve():
        raise ValueError("fixed one-shot evaluation output root required")
    return launch(args.manifest,args.output_dir,manifest["budget"]["max_seconds"]-TERM_MARGIN)


if __name__ == "__main__":
    raise SystemExit(main())
