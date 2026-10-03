"""Development tooling: a held-out set of synthetic hosts for the final v5 revision-2 check.

Sixteen images generated locally with the pinned SD 1.5 pipeline from the
sixteen prompts of ``dev_v5_channel_probe`` with seeds 2000..2015 (the tuning
hosts used seeds 1000..1011 and the first twelve prompts), and four procedural
colour fields with seeds 200..203.  They are written once to
``.thesis-build/rehearsal/v5-channel-dev/holdout/`` and are not used for tuning.
No study image is read.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import dev_v5_channel_probe as probe  # noqa: E402


def main() -> int:
    import torch
    from PIL import Image

    probe.offline()
    directory = probe.OUTPUT / "holdout"
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(4):
        path = directory / f"holdout-procedural-{index}.png"
        if not path.exists():
            Image.fromarray(probe.procedural(200 + index)).save(path)
    text, _image = probe.load()
    for index, prompt in enumerate(probe.PROMPTS):
        path = directory / f"holdout-generated-{index:02d}.png"
        if path.exists():
            continue
        with torch.inference_mode():
            result = text(
                prompt=prompt, negative_prompt="", height=512, width=512, num_inference_steps=25, guidance_scale=7.5,
                generator=torch.Generator(device="cuda").manual_seed(2000 + index), output_type="pil",
            )
        if result.nsfw_content_detected and result.nsfw_content_detected[0]:
            print("blocked by the safety checker:", index, flush=True)
            continue
        result.images[0].save(path)
        print("wrote", path.name, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
