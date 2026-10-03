"""Development tooling: held-out sets of synthetic hosts for the final v5 checks.

``holdout`` (the revision-2 check): sixteen images generated locally with the
pinned SD 1.5 pipeline from the sixteen prompts of ``dev_v5_channel_probe``
with seeds 2000..2015 (the tuning hosts used seeds 1000..1011 and the first
twelve prompts), and four procedural colour fields with seeds 200..203.
``holdout2`` (the revision-3 check): the same prompts with seeds 3000..3015 and
procedural seeds 300..303.  Each set is written once to
``.thesis-build/rehearsal/v5-channel-dev/<set>/`` and is not used for tuning.
No study image is read.

    .thesis-build/a6-science-venv/Scripts/python.exe scripts/dev_v5_holdout_hosts.py --set holdout2
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_channel_probe as probe  # noqa: E402


SETS = {"holdout": (2000, 200), "holdout2": (3000, 300)}


def main() -> int:
    import argparse

    import torch
    from PIL import Image

    parser = argparse.ArgumentParser()
    parser.add_argument("--set", default="holdout", choices=sorted(SETS))
    args = parser.parse_args()
    generated_seed, procedural_seed = SETS[args.set]
    probe.offline()
    directory = probe.OUTPUT / args.set
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(4):
        path = directory / f"{args.set}-procedural-{index}.png"
        if not path.exists():
            Image.fromarray(probe.procedural(procedural_seed + index)).save(path)
    text, _image = probe.load()
    for index, prompt in enumerate(probe.PROMPTS):
        path = directory / f"{args.set}-generated-{index:02d}.png"
        if path.exists():
            continue
        with torch.inference_mode():
            result = text(
                prompt=prompt, negative_prompt="", height=512, width=512, num_inference_steps=25, guidance_scale=7.5,
                generator=torch.Generator(device="cuda").manual_seed(generated_seed + index), output_type="pil",
            )
        if result.nsfw_content_detected and result.nsfw_content_detected[0]:
            print("blocked by the safety checker:", index, flush=True)
            continue
        result.images[0].save(path)
        print("wrote", path.name, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
