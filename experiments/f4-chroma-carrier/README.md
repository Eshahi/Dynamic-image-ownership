# Family 4: chroma-channel carrier (development)

Profiles for `scripts/f4_chroma_codec.py`, run with `scripts/f4_gate.py --profile <file>`.

- r1: the unchanged v5 study profile (`experiments/c4-v5-two-tier-regeneration-v1/profile.json`), robust tier moved to Cr.
- r2 (`profile-r2-mask1p0.json`, `profile-r2-mask1p5.json`): two changes from v5, both from the regeneration transfer probe (`.thesis-build/dev-runs/20261004-2130-f4-transfer-probe`) and a chroma visibility scale:
  1. robust frequencies limited to radius sqrt(u^2+v^2) <= 4 on the 128 grid (at most 32 cycles/image), because img2img keeps almost no Cr above 32 cycles/image (median gain .02 at strength .2) while keeping .3-.6 below it;
  2. `robust.mask_base` 1.0 or 1.5 Cr levels instead of v5's 0.4 grey levels, about one CIELAB unit of chroma, because v5's luminance just-noticeable level held the chroma robust tier to 44-50 dB in r1.
