"""Portable entrypoint; installation embeds the reviewed shared runtime."""
from pathlib import Path
import sys
here=Path(__file__).resolve()
runtime=here.parent/"_runtime"
source=here.parents[3]/"src"
sys.path.insert(0,str(runtime if runtime.is_dir() else source))
from thesis_agents.common import cli_entry
from thesis_agents.compute import main
if __name__=="__main__":
    raise SystemExit(cli_entry(main))
