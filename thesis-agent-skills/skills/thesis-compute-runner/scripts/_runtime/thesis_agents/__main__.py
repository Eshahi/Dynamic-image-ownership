import argparse
import importlib
import sys
from .common import cli_entry

MODULES={"control","guide","research","design","compute","analysis","audit","writing","runpod","smoke","validate_bundle"}
def main():
    p=argparse.ArgumentParser(description="Thesis agent deterministic helpers")
    p.add_argument("helper",choices=sorted(MODULES))
    args,remaining=p.parse_known_args()
    sys.argv=[sys.argv[0],*remaining]
    return cli_entry(importlib.import_module("thesis_agents."+args.helper).main)

if __name__=="__main__":
    raise SystemExit(main())
