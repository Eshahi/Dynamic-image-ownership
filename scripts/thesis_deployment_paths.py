"""Code-bound deployment paths; no environment-variable or caller overrides.

Linux is the explicitly amended Vast deployment. Windows retains the reviewed
local layout. This module is included in the worker's scientific code closure.
"""
from pathlib import Path
import sys

WINDOWS_MAIN = "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5"
LINUX_RAW_ROOT = "/workspace/thesis-data/coco2017"
WINDOWS_RAW_ROOT = WINDOWS_MAIN + "/data/raw"


def deployment_paths(platform):
    if platform == "linux":
        return dict(main="/workspace/thesis/repo", assets="/workspace/thesis-assets/a6",
                    sdxl="/workspace/thesis-assets/journal-sdxl-vae-6f5909a7",
                    official_runtime="/workspace/thesis-runtime/scripts/_runtime",
                    held_out_raw_root=LINUX_RAW_ROOT)
    if platform == "win32":
        return dict(main=WINDOWS_MAIN, assets=WINDOWS_MAIN + "/.thesis-build/assets/a6",
                    sdxl=WINDOWS_MAIN + "/.thesis-build/assets/journal-sdxl-vae-6f5909a7",
                    official_runtime="C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime",
                    held_out_raw_root=WINDOWS_RAW_ROOT)
    raise RuntimeError("Unbound thesis deployment platform: " + platform)


PATHS = deployment_paths(sys.platform)
MAIN = Path(PATHS["main"])
ASSETS = Path(PATHS["assets"])
SDXL = Path(PATHS["sdxl"])
OFFICIAL_RUNTIME = PATHS["official_runtime"]
HELD_OUT_RAW_ROOT = PATHS["held_out_raw_root"]
HELD_OUT_RAW_ROOTS = (WINDOWS_RAW_ROOT, LINUX_RAW_ROOT)
