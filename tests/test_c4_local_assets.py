"""Owned tiny asset fixtures/mock factory; no real weights or network/model run."""
import dataclasses
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.embedding import local_assets as assets
from src.embedding.proposed import EmbeddingError
from src.runtime.config import LoadedConfig
from tests import test_embedding as fixtures

SETTINGS, torch = fixtures.SETTINGS, fixtures.torch


class LocalAssetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root/"assets"
        self.stage = self.root/"stages"
        self.source.mkdir()
        self.stage.mkdir()
        entries = []
        for path in sorted(assets.SD_FILES):
            raw = ("owned fixture, not weights: "+path).encode()
            destination = self.source/"sd15-fp16"/path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
            entries.append({"path": "sd15-fp16/"+path, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        raw_lock = json.dumps({"schema_version": "a6-asset-lock-v1", "files": entries}).encode()
        self.lock = self.root/"owned-lock.json"
        self.lock.write_bytes(raw_lock)
        self.lock_patch = patch.object(assets, "LOCK_SHA256", hashlib.sha256(raw_lock).hexdigest())
        self.lock_patch.start()
        self.addCleanup(self.lock_patch.stop)
        self.plan = assets.plan_assets(self.lock)

    def loaded(self):
        # Deliberately unit-only C1 object, not a reviewed science configuration.
        value = {"embedding": {"model_repository": "stable-diffusion-v1-5/stable-diffusion-v1-5",
            "model_revision": "451f4fe16113bff5a5d2269ed5ad43b0592e9a14",
            "diffusers_commit": "0f252be0ed42006c125ef4429156cb13ae6c1d60",
            "model_component_hashes": self.plan.component_hashes,
            "scheduler": {"inference_steps": 10, "strength": .2}, "vae_scale": .18215,
            "working_image": {"maximum_side": 256}, "alpha_s": .2, "alpha_i": .3, "rho": .01,
            "optimizer": {"learning_rate": .005, "iterations": 2},
            "loss": {"lambda_q": 1, "lambda_r": 1, "lambda_s": 1, "lambda_i": 1, "margin_s": .1, "margin_i": .1}}}
        raw = json.dumps(value).encode()
        return LoadedConfig(value, raw, hashlib.sha256(raw).hexdigest(), "a"*64)

    def test_plan_snapshot_and_group_identity_are_complete(self):
        self.assertEqual(len(self.plan.entries), 15)
        self.assertEqual(set(self.plan.component_hashes), set(assets.GROUPS))
        settings = assets.bind_config_assets(self.loaded(), self.plan)
        self.assertEqual(settings, SETTINGS)
        snapshot = assets.snapshot_assets(self.source, self.stage, self.plan)
        self.assertTrue((snapshot/"snapshot-complete.json").is_file())
        for entry in self.plan.entries:
            self.assertEqual((snapshot/"sd15-fp16"/entry["path"]).read_bytes(),
                             (self.source/"sd15-fp16"/entry["path"]).read_bytes())
        another = assets.snapshot_assets(self.source, self.stage, self.plan)
        self.assertNotEqual(snapshot, another)

    def test_changed_lock_plan_or_config_rejected(self):
        self.lock.write_bytes(self.lock.read_bytes()+b" ")
        with self.assertRaises(EmbeddingError):
            assets.plan_assets(self.lock)
        with self.assertRaises(EmbeddingError):
            assets.snapshot_assets(self.source, self.stage, dataclasses.replace(self.plan, total_bytes=1))
        config = self.loaded()
        config.value["embedding"]["rho"] = 3
        with self.assertRaises(EmbeddingError):
            assets.bind_config_assets(config, self.plan)
        config = self.loaded()
        config.value["embedding"]["model_component_hashes"]["vae"] = "f"*64
        raw = json.dumps(config.value).encode()
        forged = LoadedConfig(config.value, raw, hashlib.sha256(raw).hexdigest(), "a"*64)
        with self.assertRaises(EmbeddingError):
            assets.bind_config_assets(forged, self.plan)

    def test_bad_source_bytes_keep_failed_snapshot(self):
        selected = self.source/"sd15-fp16"/self.plan.entries[0]["path"]
        old = selected.read_bytes()
        selected.write_bytes(b"X"+old[1:])
        with self.assertRaises(EmbeddingError):
            assets.snapshot_assets(self.source, self.stage, self.plan)
        snapshots = list(self.stage.iterdir())
        self.assertEqual(len(snapshots), 1)
        self.assertTrue((snapshots[0]/"snapshot-start.json").exists())
        self.assertTrue((snapshots[0]/"snapshot-failed.json").exists())
        self.assertFalse((snapshots[0]/"snapshot-complete.json").exists())
        self.assertEqual(selected.read_bytes(), b"X"+old[1:])

    def test_copy_never_overwrites_and_relative_roots_rejected(self):
        entry = self.plan.entries[0]
        output = self.root/"already-present"
        output.write_bytes(b"preserve me")
        with self.assertRaises(FileExistsError):
            assets._copy_checked(self.source/"sd15-fp16"/entry["path"], output, entry)
        self.assertEqual(output.read_bytes(), b"preserve me")
        with self.assertRaises(EmbeddingError):
            assets.snapshot_assets(Path("relative"), self.stage, self.plan)

    @unittest.skipIf(torch is None, "factory binding tests require existing WSL Torch")
    def test_loader_binds_mock_empty_condition_and_safety_without_real_model(self):
        from diffusers import StableDiffusionImg2ImgPipeline
        snapshot = assets.snapshot_assets(self.source, self.stage, self.plan)
        backend = fixtures.TensorContracts().backend()
        class Text(torch.nn.Module):
            def forward(self, tokens): return (torch.zeros(1, 77, 768),)
        class Tokenizer:
            model_max_length = 77
            def __call__(self, texts, **kwargs):
                self.texts, self.kwargs = texts, kwargs
                return SimpleNamespace(input_ids=torch.zeros(1, 77, dtype=torch.long))
        class Safety(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.weight = torch.nn.Parameter(torch.tensor(1.))
            def forward(self, clip_input, images):
                images[:] = 0
                return images, [True]
        pipeline = SimpleNamespace(vae=backend.vae, unet=backend.unet, text_encoder=Text(),
            tokenizer=Tokenizer(), safety_checker=Safety(),
            feature_extractor=lambda images, **kwargs: SimpleNamespace(pixel_values=torch.zeros(1, 3, 224, 224)))
        pipeline.to = lambda device: pipeline
        environment = {name: "1" for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE")}
        old = (torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32, torch.backends.cudnn.benchmark)
        try:
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            torch.backends.cudnn.benchmark = False
            with patch.dict(os.environ, environment), patch.object(torch, "are_deterministic_algorithms_enabled", return_value=True), \
                 patch.object(StableDiffusionImg2ImgPipeline, "from_pretrained", return_value=pipeline) as factory:
                loaded = assets.load_snapshot(self.loaded(), self.plan, snapshot, device="cpu")
        finally:
            torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32, torch.backends.cudnn.benchmark = old
        self.assertEqual(pipeline.tokenizer.texts, [""])
        self.assertTrue(factory.call_args.kwargs["local_files_only"])
        self.assertTrue(factory.call_args.kwargs["use_safetensors"])
        self.assertEqual(factory.call_args.kwargs["torch_dtype"], torch.float32)
        self.assertEqual(loaded.identity["conditioning"], "fixed-empty-string")
        import numpy as np
        pixels = np.full((32, 32, 3), 127, dtype=np.uint8)
        self.assertTrue(loaded.check_saved_pixels(pixels))
        self.assertTrue((pixels == 127).all())  # safety's black replacement is not used

    @unittest.skipIf(torch is None, "factory guard tests require existing WSL Torch")
    def test_modified_snapshot_never_reaches_factory(self):
        from diffusers import StableDiffusionImg2ImgPipeline
        snapshot = assets.snapshot_assets(self.source, self.stage, self.plan)
        file = snapshot/"sd15-fp16"/self.plan.entries[0]["path"]
        raw = file.read_bytes()
        file.write_bytes(b"X"+raw[1:])
        environment = {name: "1" for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "DIFFUSERS_OFFLINE")}
        with patch.dict(os.environ, environment), patch.object(StableDiffusionImg2ImgPipeline, "from_pretrained") as factory:
            with self.assertRaises(ValueError):
                assets.load_snapshot(self.loaded(), self.plan, snapshot, device="cpu")
            factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
