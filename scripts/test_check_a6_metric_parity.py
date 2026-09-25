import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_a6_metric_parity as probe


class MetricParityPreparationTests(unittest.TestCase):
    def test_synthetic_pixels_are_fixed_and_bounded(self):
        image = probe.synthetic_rgb8(64)
        self.assertEqual(len(image), 64 * 64 * 3)
        self.assertEqual(image[:6], bytes((0, 47, 94, 17, 64, 111)))
        self.assertEqual(image, probe.synthetic_rgb8(64))
        with self.assertRaises(ValueError):
            probe.synthetic_rgb8(63)

    def test_default_preflight_verifies_identity_without_metric_load(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset_root = root / "assets"
            asset_root.mkdir()
            entries = []
            for index, relative in enumerate(
                [probe.CLIP_PATH, probe.ALEXNET_PATH]
                + [f"sd15-fp16/dummy{index}.bin" for index in range(15)]
            ):
                path = asset_root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                content = bytes((index,))
                path.write_bytes(content)
                entries.append({
                    "path": relative,
                    "size_bytes": 1,
                    "sha256": hashlib.sha256(content).hexdigest(),
                })
            lock_path = root / "lock.json"
            raw = json.dumps({"schema_version": "a6-asset-lock-v1",
                              "files": entries}).encode()
            lock_path.write_bytes(raw)
            with patch.object(probe, "LOCK_SHA256", hashlib.sha256(raw).hexdigest()):
                with patch.object(probe, "verify_package", return_value={"a": "b"}):
                    report = probe.check_inputs(asset_root, lock_path, root)
                    self.assertEqual(report["status"], "verified_no_model_load")
                    self.assertEqual(report["verified_asset_count"], 17)
                    (asset_root / probe.CLIP_PATH).write_bytes(b"wrong")
                    with self.assertRaises(ValueError):
                        probe.check_inputs(asset_root, lock_path, root)

    def test_launch_requires_both_deterministic_settings(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                probe._check_launch_environment()
        with patch.dict("os.environ", {
            "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
            "PYTHONHASHSEED": "0",
        }, clear=True):
            probe._check_launch_environment()

    def test_lpips_only_selection_does_not_load_clip(self):
        with patch.object(probe, "_load_clip_and_measure") as clip_load:
            with patch.object(probe, "_load_lpips_and_measure",
                              return_value={"cpu_score": 0.1}) as lpips_load:
                result = probe._selected_measurements(
                    "lpips", Path("assets"), Path("package"))
        clip_load.assert_not_called()
        lpips_load.assert_called_once_with(
            Path("assets") / probe.ALEXNET_PATH,
            Path("package") / "weights/v0.1/alex.pth",
        )
        self.assertEqual(result, {"lpips": {"cpu_score": 0.1}})
        with self.assertRaises(ValueError):
            probe._selected_measurements("unknown", Path("a"), Path("b"))


if __name__ == "__main__":
    unittest.main()
