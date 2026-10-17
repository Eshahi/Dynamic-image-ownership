"""Layout-only missing-file normalization around the unmodified frozen scorer.

An absent canonical path is None, just as the frozen scorer's latest() returns
None for absent regeneration and enrollment files. Never create substitute pixels.
"""
from pathlib import Path
import claude_round3_two_factor as frozen


class Cohort(frozen.Cohort):
    def suspects(self, sid):
        return [(model, strength, seed, arm,
                 path if path is not None and Path(path).is_file() else None)
                for model, strength, seed, arm, path in super().suspects(sid)]


if __name__ == '__main__':
    frozen.Cohort = Cohort
    frozen.main()
