"""Run the complete offline test suite and save an honest machine-readable result."""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--out",default=str(ROOT/"tests/validation-results.json"))
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"))
    started=time.monotonic(); result=unittest.TextTestRunner(verbosity=2).run(suite)
    data={"timestamp":datetime.now(timezone.utc).isoformat(),"python":sys.version.split()[0],"platform":sys.platform,"tests_run":result.testsRun,"failures":[t.id() for t,_ in result.failures],"errors":[t.id() for t,_ in result.errors],"skipped":[{"test":t.id(),"reason":reason} for t,reason in result.skipped],"passed":result.wasSuccessful() and not result.skipped,"duration_seconds":round(time.monotonic()-started,3),"live_services_contacted":False,"scope":"Offline synthetic fixtures, real local Spec Kit CLI, CPU no-op only"}
    Path(args.out).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    return 0 if data["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
