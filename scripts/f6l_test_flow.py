"""End-to-end lean flow with stubbed models. Runs the real runner stages, the reviewed Stage S native,
threat, secondary, detect and quality functions, and the real decision code on what they write.

Needs numpy and PIL only. No GPU, no model, no scientific result. A stub encodes arm, cell and source
in the first pixel, so each read outcome is fixed in advance and every decision can be checked exactly.
"""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
from types import ModuleType, SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from PIL import Image

ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
ARM_CODES = {name: i for i, name in enumerate(("unmarked", "f5-r2", "f5b-46", "f5b-42", "ren-38", "ren-36", "gen-46", "gen-42", "gen-38",
                                               "noise-46", "noise-42", "noise-46-ren38", "x0-46", "v5-r3", "vine-r", "vine-b", "f7"), 1)}
CELL_CODES = {("R0", .2): 1, ("R1", .1): 2, ("R1", .2): 3, ("K3", .2): 4, ("R0", .4): 5}
# How many of the sources read positive, per arm and cell, in R0 .2, R1 .1, R1 .2, K3 .2 order.
POSITIVE = {"f5-r2": (16, 1, 0, 3), "noise-46": (16, 14, 12, 13), "noise-46-ren38": (16, 13, 12, 12), "f5b-46": (16, 5, 2, 7),
            "f5b-46-ren38": (16, 6, 3, 7), "v5-r3": (10, 12, 3, 14), "vine-b": (12, 14, 12, 14)}
SCORE = {"noise-46": 10., "noise-46-ren38": 9.5, "f5-r2": 5., "f5b-46": 7., "gen-46": 7.5}


def stub_torch():
    class Cuda:
        OutOfMemoryError = type("OutOfMemoryError", (RuntimeError,), {})
        reset_peak_memory_stats = staticmethod(lambda: None)
        mem_get_info = staticmethod(lambda: (10, 100))
        memory_allocated = memory_reserved = max_memory_allocated = max_memory_reserved = staticmethod(lambda: 1)
    saved = {}
    def save(value, path):
        Path(path).write_bytes(b"tape")
        saved[str(path)] = value
    return SimpleNamespace(cuda=Cuda, save=save, load=lambda path, weights_only=True: saved[str(path)])


class Draw:
    def cpu(self):
        return self

    def cuda(self):
        return self


class Tape:
    def __init__(self):
        self.draws, self.cursor = [], 0

    def record(self):
        self.draws.append(Draw())
        return None

    def replay(self):
        self.cursor = len(self.draws)
        return None

    def receipt(self):
        return dict(draws=len(self.draws))


class Attention:
    def __init__(self, *modules):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def stamped(rgb, arm):
    out = rgb.copy()
    out[0, 0, 0] = ARM_CODES[arm]
    return out


def read_raw(rgb, method, owner, mode=None, table=None):
    arm_code, cell_code, index = int(rgb[0, 0, 0]), int(rgb[0, 0, 1]), int(rgb[0, 0, 2])
    names = {v: k for k, v in ARM_CODES.items()}
    arm = names.get(arm_code)
    marked = arm is not None and arm == method
    positive = False
    if owner == ALPHA and marked and cell_code in (1, 2, 3, 4, 5):
        counts = table if table is not None else POSITIVE.get(arm, ())
        positive = index < (counts[cell_code - 1] if cell_code - 1 < len(counts) else 0)
    clean = owner == ALPHA and marked and cell_code == 0
    read = positive or clean
    # The stub's exact code never equals the payload outside clean images, so J stays false: J must not matter.
    code = "0000abcd" if clean else "ffffffff"
    semantic = dict(read=read, found=read, content_match=read, decoded_code=code, decoded_score=SCORE.get(arm, 3.) if owner == ALPHA else 2.,
                    corrected_distance=0.)
    instance = dict(read=clean, found=clean, content_match=clean, decoded_code="0000beef")
    return dict(semantic=semantic, instance=instance, outcome="both_match" if clean else "none")


class Internal:
    v5 = None  # F7's threshold check is stubbed in the flow test

    def __init__(self, assets, base):
        self.reader = SimpleNamespace(latent=lambda rgb: None)
        self.method = None

    def features(self, rgb, views):
        self.views = views
        return []

    def embed(self, rgb, arm):
        return stamped(rgb, arm), dict(q="0000abcd", h="0000beef"), dict(semantic_code="0000abcd")

    def _detect(self, rgb, kind, owner, features, latent, mode="combined"):
        # The runtime dispatches lean arms to the F5 reader: the stub answers for the arm stamped in the image.
        arm = {v: k for k, v in ARM_CODES.items()}.get(int(rgb[0, 0, 0]))
        method = "v5-r3" if kind == "v5" else arm if arm not in ("v5-r3", "unmarked") else None
        return read_raw(rgb, method, owner, mode)


class Vine:
    def __init__(self, assets, encoding=False):
        pass

    def embed(self, rgb, bits):
        return stamped(rgb, "vine-r")

    def detect(self, rgb, bits):
        return dict(status="ok", presence=dict(present=int(rgb[0, 0, 0]) == ARM_CODES["vine-r"]), raw=dict(decoded_message=[0]))


class VineB:
    def __init__(self, assets, base, encoding=False):
        pass

    def embed(self, rgb, owner):
        return stamped(rgb, "vine-b"), dict(q="0000abcd", h="0000beef"), {}

    def blind(self, rgb):
        return dict(raw=dict(decoded_message=[0]))

    def features(self, rgb):
        return []

    def read(self, rgb, owner, blind=None, features=None):
        return dict(read_raw(rgb, "vine-b", owner), carrier_decode={})


class Writer:
    """Stands in for LeanWriter; the real one has its own CPU test."""
    _closed = False
    closed = 0

    def embed_arm(self, rgb, spec, source_id):
        for arm, value in ALL_SPECS.items():
            if value == spec:
                return stamped(rgb, arm), dict(q="0000abcd", h="0000beef"), dict(semantic_code="0000abcd")
        raise AssertionError("Unknown lean spec")

    def close(self):
        Writer.closed += 1


class Regenerator:
    def __init__(self, assets, spec):
        self.pipe = SimpleNamespace(unet=None, vae=None, movq=None)
        self.family = spec


ALL_SPECS = {}


def install_stubs():
    stubs = dict(et_final_pilot=dict(Tape=Tape, ClassicAttention=Attention),
        et_final_phase_a=dict(run_native=None),
        et_final_phase_a_attacks=dict(Quality=lambda assets: (lambda a, b: dict(psnr_db=44., ssim_rgb=.98, lpips=.03))),
        encoder_transfer_test=dict(ALPHA=ALPHA, BETA=BETA, message=lambda sid, bits, seed: [0], presence=lambda d, w: dict(present=False)),
        tifs_vine_b=dict(VineB=VineB, delivery_diagnostics=lambda *a: {}))
    def run_native(family, regen, rgb, strength, seed, tape):
        out = rgb.copy()
        out[0, 0, 1] = CELL_CODES[(family, strength)]
        return out
    stubs["et_final_phase_a"]["run_native"] = run_native
    for name, values in stubs.items():
        module = ModuleType(name)
        module.__dict__.update(values)
        sys.modules[name] = module


class Flow(unittest.TestCase):
    def setUp(self):
        install_stubs()
        import f6l_common, f6l_run, f6l_select, tifs_common, tifs_stage_s, tifs_stage_s_read
        self.lean_common, self.run_mod, self.select, self.common, self.stage, self.read = (
            f6l_common, f6l_run, f6l_select, tifs_common, tifs_stage_s, tifs_stage_s_read)
        self.original_new, self.original_items = tifs_stage_s.NEW, tifs_stage_s_read.items
        self.root = Path(tempfile.mkdtemp())
        self.lean = f6l_common.load_lean()
        ALL_SPECS.update(self.lean["arms"])
        ALL_SPECS["f5b-46-ren38"] = dict(kind="lean", variant="f5-budget", robust_psnr_db=46, render_db=38)
        def load_rgb(path):
            return np.asarray(Image.open(path), dtype=np.uint8).copy()
        def save_rgb(path, rgb):
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgb).save(path)
            return dict(path=str(path), sha256=tifs_common.sha256_file(path))
        self.rt = SimpleNamespace(load_rgb=load_rgb, save_rgb=save_rgb, release=lambda: None, Internal=Internal, Vine=Vine, Regenerator=Regenerator)
        self.torch = stub_torch()
        f6l_run.build_writer = lambda *a, **k: Writer()
        f6l_run.load_policy = lambda args: {}

    def tearDown(self):
        self.stage.NEW, self.read.items = self.original_new, self.original_items
        shutil.rmtree(self.root, ignore_errors=True)

    def plan(self, phase, out, previous=None):
        base = self.common.load_json(self.lean_common.ROOT / self.lean["base_config"])
        config = self.lean_common.stage_config(self.lean, base, phase, previous=previous)
        self.common.atomic_json(out / "config.json", config)
        config["_runtime_bounds"] = None
        return config

    def prepare(self, out, sources, pairs=(), targets=()):
        records = {}
        for index, sid in enumerate([*sources, *targets]):
            rgb = np.full((512, 512, 3), 128, np.uint8)
            # A recipient carries cell code 9, so a transferred residual is not mistaken for a clean mark.
            rgb[0, 0] = (0, 9 if sid in targets else 0, index)
            path = out / "originals" / f"{sid}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgb).save(path)
            records[sid] = dict(path=str(path), source_uid="u" + sid, canonical_png_sha256="x")
        self.common.atomic_json(out / "prepared.json", dict(sources=records, donors=list(sources), targets=list(targets), pairs=list(pairs), original_features={}))

    def args(self, out, phase, **kwargs):
        return SimpleNamespace(out=out, assets=self.root, phase=phase, stage=kwargs.pop("stage", "clean"), method=None, worker="", family=None,
                               rehearsal=False, invocation="test", **kwargs)

    def execute(self, out, phase, config, *stages):
        budget = self.common.Budget(36000, reserve_seconds=0)
        specs = dict(R0="R0", R1="R1", K3="K3")
        base = dict(payload_bits={"vine-r": 100}, message_seed=1, wrong_message_seed=2)
        for name in stages:
            args = self.args(out, phase, stage=name)
            getattr(self.run_mod, name)(args, self.lean, config, base, specs, budget, self.rt, self.torch)

    def decide(self, out, phase):
        code = self.select.main(["--action", "decide", "--phase", phase, "--out", str(out)])
        return code, self.common.load_json(out / "decision.json")

    def test_whole_study_flows_and_reaches_the_expected_verdict(self):
        # Stage 1.
        out = self.root / "stage1"
        out.mkdir()
        config = self.plan("stage1", out)
        self.prepare(out, ["1", "2", "3", "4"])
        POSITIVE["gen-46"] = (4, 0, 0, 0)
        SCORE.update({"ren-38": 4., "ren-36": 4., "gen-42": 7., "gen-38": 7., "noise-42": 7., "x0-46": 8., "f5b-42": 6.})
        self.execute(out, "stage1", config, "clean", "quality")
        report = self.select.clean_gate(out, self.common.load_json(out / "config.json"))
        self.assertEqual(report["removed"], {})
        self.execute(out, "stage1", config, "native", "detect", "quality")
        code, decision = self.decide(out, "stage1")
        self.assertEqual(code, 0, decision.get("reason"))
        self.assertEqual(decision["finalists"], ["noise-46", "noise-46-ren38"])
        self.assertEqual(decision["c0"], dict(events=0, unresolved=0))
        self.assertEqual(decision["arms"]["noise-46"]["cells"]["R1-0.1"]["mean_decoded"], 10.)
        self.assertEqual(Writer.closed > 0, True)
        now = datetime.now(timezone.utc).isoformat()
        fit_args = ["--action", "fit", "--root", str(self.root), "--instance-start-utc", now, "--hourly-usd", ".5512"]
        self.assertEqual(self.select.main([*fit_args, "--phase", "stage2", "--previous", str(out / "decision.json")]), 0)
        report = self.common.load_json(self.root / "stage2-fit.json")
        self.assertTrue(report["fits"])
        self.assertLess(report["cap_seconds"], 34 * 3600)

        # Stage 2: twelve new sources, three seeds, matched controls added automatically.
        out2 = self.root / "stage2"
        out2.mkdir()
        config2 = self.plan("stage2", out2, previous=decision)
        self.assertEqual(config2["arms"], ["unmarked", "f5-r2", "f5b-46", "f5b-46-ren38", "noise-46", "noise-46-ren38"])
        sources = [str(i) for i in range(10, 22)]
        self.prepare(out2, sources)
        self.execute(out2, "stage2", config2, "clean", "native", "detect", "quality")
        code, decision2 = self.decide(out2, "stage2")
        self.assertEqual(code, 0, decision2.get("reason"))
        self.assertEqual(decision2["winner"], "noise-46")
        self.assertEqual(decision2["arms"]["noise-46"]["cells"]["R1-0.2"]["c_lower"], 12)
        self.assertEqual(decision2["arms"]["noise-46"]["cells"]["R1-0.2"]["j_lower"], 0)
        self.assertEqual(self.select.main([*fit_args, "--phase", "stage3", "--previous", str(out2 / "decision.json")]), 0)

        # Stage 3: baselines, threats and distortions on disjoint sources.
        out3 = self.root / "screen"
        out3.mkdir()
        config3 = self.plan("stage3", out3, previous=decision2)
        self.assertEqual(config3["arms"], ["unmarked", "f5-r2", "f5b-46", "noise-46", "v5-r3", "vine-r", "vine-b"])
        donors = [str(i) for i in range(100, 116)]
        targets = [str(i) for i in range(200, 216)]
        pairs = [dict(donor=d, target=t, cosine=.5, distinctness="human_label_missing") for d, t in zip(donors, targets)]
        self.prepare(out3, donors, pairs, targets)
        self.execute(out3, "stage3", config3, "clean", "native", "threats", "secondary", "detect", "quality")
        code, result = self.decide(out3, "stage3")
        self.assertEqual(result["status"], "FULL_GO", [g for g in result.get("gates", []) if g["status"] != "pass"])
        self.assertEqual(code, 0)
        self.assertEqual(result["winner"], "noise-46")
        self.assertEqual(result["control"], "f5b-46")
        self.assertEqual(result["arms"]["noise-46"]["cells"]["K3-0.2"]["c_lower"], 13)
        self.assertEqual(result["arms"]["noise-46"]["cells"]["K3-0.2"]["j_lower"], 0)
        self.assertEqual(result["threats"]["events"], [])
        self.assertEqual(result["threats"]["unresolved"], 0)
        self.assertEqual(result["threats"]["by_condition"]["patch256"]["reads"], 16)
        self.assertEqual(result["vine_r_presence"]["R1-0.2"], 16)
        self.assertEqual(result["secondary"]["noise-46"]["jpeg90"]["reads"], 16)
        self.assertEqual(result["arms"]["vine-b"]["cells"]["R1-0.2"]["c_lower"], 12)
        self.assertEqual(set(result["threats_by_arm"]), {"f5-r2", "f5b-46", "noise-46", "v5-r3", "vine-b"})
        self.check_pack()

    def test_f7_dual_carrier_flow(self):
        """F7 writes through Internal and reads with both carriers; the union decides."""
        import f7_dual
        saved = f7_dual.embed, f7_dual.read, f7_dual.check_threshold
        # Carrier counts per cell in R0 .2, R1 .1, R1 .2, K3 .2, R0 .4 order: F5 carrier strong at home, v5 abroad.
        f5_carrier, v5_carrier = (16, 0, 0, 0, 10), (6, 13, 3, 14, 0)
        POSITIVE.update({"f5-r2": (16, 1, 0, 3, 11), "v5-r3": (10, 12, 3, 14, 1)})
        def carrier(rgb, owner, counts):
            raw = read_raw(rgb, "f7", owner, table=counts)
            raw["semantic"]["decoded_score"] = 9.0 if raw["semantic"]["read"] else 3.0
            return raw
        f7_dual.embed = lambda internal, rgb, base, owner, metric=None: (stamped(rgb, "f7"), dict(q="0000abcd", h="0000beef"), dict(v5_scale=1.0))
        f7_dual.read = lambda internal, rgb, owner, features=None, latent=None: dict(
            f5=carrier(rgb, owner, f5_carrier), v5=carrier(rgb, owner, v5_carrier), combined=dict(decoded_score=3.0, content_match=False))
        f7_dual.check_threshold = lambda v5: 8.341671
        try:
            out = self.root / "f7" / "rehearsal"
            out.mkdir(parents=True)
            config = self.plan("f7", out)
            self.assertEqual(config["arms"], ["unmarked", "f5-r2", "v5-r3", "f7"])
            donors = [str(i) for i in range(100, 116)]
            targets = [str(i) for i in range(200, 216)]
            pairs = [dict(donor=d, target=t, cosine=.5, distinctness="human_label_missing") for d, t in zip(donors, targets)]
            self.prepare(out, donors, pairs, targets)
            self.execute(out, "f7", config, "clean", "native", "threats", "secondary", "detect", "quality")
            code, result = self.decide(out, "f7")
            now = datetime.now(timezone.utc).isoformat()
            fit_code = self.select.main(["--action", "fit", "--phase", "f7", "--root", str(self.root),
                                         "--instance-start-utc", now, "--hourly-usd", ".5512"])
            fit = self.common.load_json(self.root / "f7-fit.json")
        finally:
            f7_dual.embed, f7_dual.read, f7_dual.check_threshold = saved
        self.assertEqual(result["status"], "GO", [g for g in result.get("gates", []) if g["status"] != "pass"])
        self.assertEqual(code, 0)
        cells = result["arms"]["f7"]["cells"]
        self.assertEqual([cells[c]["c_lower"] for c in ("R0-0.2", "R1-0.1", "R1-0.2", "K3-0.2", "R0-0.4")], [16, 13, 3, 14, 10])
        self.assertEqual(result["f7_carriers"]["C_v5"]["R1-0.1"]["lower"], 13)
        self.assertEqual(result["f7_carriers"]["C_f5"]["R0-0.2"]["lower"], 16)
        self.assertEqual(result["c0"], dict(events=0, unresolved=0))
        self.assertEqual(result["threats"]["unresolved"], 0)
        self.assertEqual(result["arms"]["f7"]["clean_f"]["lower"], 16)
        self.assertEqual(set(result["c0_by_reader"]), {"f5-r2", "v5-r3"})
        self.assertEqual(result["f7_writer"]["rows"], 16)
        self.assertEqual(fit_code, 0)
        self.assertTrue(fit["fits"])

    def test_f7c_replication_flow(self):
        """f7c: fresh manifest, F7 and unmarked arms only, no distortion stage; the fit scales to 64 donors."""
        import f7_dual
        saved = f7_dual.embed, f7_dual.read, f7_dual.check_threshold
        def carrier(rgb, owner, counts):
            raw = read_raw(rgb, "f7", owner, table=counts)
            raw["semantic"]["decoded_score"] = 9.0 if raw["semantic"]["read"] else 3.0
            return raw
        f7_dual.embed = lambda internal, rgb, base, owner, metric=None: (stamped(rgb, "f7"), dict(q="0000abcd", h="0000beef"), dict(v5_scale=1.0))
        f7_dual.read = lambda internal, rgb, owner, features=None, latent=None: dict(
            f5=carrier(rgb, owner, (16, 0, 0, 0, 10)), v5=carrier(rgb, owner, (6, 13, 3, 14, 0)),
            combined=dict(decoded_score=3.0, content_match=False, found=False))
        f7_dual.check_threshold = lambda v5: 8.341671
        try:
            out = self.root / "f7c" / "rehearsal"
            out.mkdir(parents=True)
            config = self.plan("f7c", out)
            self.assertEqual(config["arms"], ["unmarked", "f7"])
            self.assertEqual(config["source_manifest"], "research/f7-dual-carrier-20261102/replication/source-manifest.json")
            self.assertEqual(config["source_manifest_sha256"], self.common.sha256_file(self.stage.manifest_path(config)))
            manifest = self.common.load_json(self.stage.manifest_path(config))
            self.common.validate_sources(manifest)
            self.assertEqual([len(manifest[g]) for g in ("screen_donors", "screen_targets")], [64, 64])
            donors = [str(i) for i in range(100, 104)]
            targets = [str(i) for i in range(200, 204)]
            pairs = [dict(donor=d, target=t, cosine=.5, distinctness="human_label_missing") for d, t in zip(donors, targets)]
            self.prepare(out, donors, pairs, targets)
            self.execute(out, "f7c", config, "clean", "native", "threats", "detect", "quality")
            now = datetime.now(timezone.utc).isoformat()
            fit_code = self.select.main(["--action", "fit", "--phase", "f7c", "--root", str(self.root),
                                         "--instance-start-utc", now, "--hourly-usd", ".5512"])
            fit = self.common.load_json(self.root / "f7c-fit.json")
            data = self.select.load_phase(out)
        finally:
            f7_dual.embed, f7_dual.read, f7_dual.check_threshold = saved
        self.assertEqual(fit_code, 0)
        self.assertEqual(fit["screen_donors"], 64)
        self.assertEqual(data["producers"]["secondary"], {})
        items = {r["item"] for r in data["detections"].values()}
        self.assertIn("native:K3-0.2:100:2:f7", items)
        self.assertIn("native:R1-0.2:103:0:unmarked", items)
        self.assertTrue(any(i.startswith("threat:T4:100:200:f7:") for i in items))
        self.assertTrue(any(i.startswith("threat:T5:") for i in items))
        self.assertFalse(any(r.get("method") != "f7" for r in data["detections"].values()))

    def check_pack(self):
        import f6l_pack
        dest = self.root / "bundle.tgz"
        f6l_pack.main(["--root", str(self.root), "--dest", str(dest)])
        with tarfile.open(dest) as bundle:
            names = bundle.getnames()
        self.assertIn("screen/decision.json", names)
        self.assertTrue(any(name.startswith("screen/images/") for name in names))
        self.assertFalse(any(name.endswith(".pt") for name in names))


if __name__ == "__main__":
    unittest.main(verbosity=2)
