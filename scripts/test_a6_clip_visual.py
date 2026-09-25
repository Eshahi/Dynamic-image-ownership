import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import a6_clip_visual as adapter


class ClipVisualAdapterTests(unittest.TestCase):
    def test_changed_source_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "clip").mkdir()
            (root / "clip/clip.py").write_bytes(b"changed")
            (root / "clip/model.py").write_bytes(b"not executable")
            distribution = Mock()
            distribution.locate_file.side_effect = lambda name: root / name
            with patch.object(adapter.importlib.metadata, "distribution",
                              return_value=distribution):
                with patch.object(adapter.importlib.util,
                                  "spec_from_file_location") as execute:
                    with self.assertRaisesRegex(RuntimeError, "digest changed"):
                        adapter.verified_visual_builder()
                    execute.assert_not_called()

    def test_invalid_device_and_checkpoint_size_fail_without_model_import(self):
        with tempfile.TemporaryDirectory() as temp:
            checkpoint = Path(temp) / "ViT-B-32.pt"
            checkpoint.write_bytes(b"not a model")
            with self.assertRaisesRegex(ValueError, "device"):
                adapter.load_visual_encoder(checkpoint, device="other")
            with patch.object(adapter, "verified_visual_builder") as builder:
                with self.assertRaisesRegex(RuntimeError, "size"):
                    adapter.load_visual_encoder(checkpoint)
                builder.assert_not_called()

    @unittest.skipUnless(importlib.util.find_spec("torchvision"),
                         "requires isolated science venv")
    def test_official_preprocess_known_answer_without_model_load(self):
        import numpy as np
        from PIL import Image
        from check_a6_metric_parity import synthetic_rgb8

        image = Image.frombytes("RGB", (224, 224), synthetic_rgb8(224))
        pixels = adapter.official_image_transform()(image).unsqueeze(0)
        observed = hashlib.sha256(
            np.asarray(pixels.numpy(), dtype="<f4").tobytes()).hexdigest()
        self.assertEqual(observed,
                         "9465569501fdd08c5fc6d057f0263763eb703ad0547cda10c049e109401f2db3")


if __name__ == "__main__":
    unittest.main()
