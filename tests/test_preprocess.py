import io
import json
import tempfile
import unittest
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, PngImagePlugin
from src.data.preprocess import (PreprocessError, decode_source, encode_output,
                                 load_config, normalized, pixel_sha, preprocess_file,
                                 runtime, sha)

CONFIG = Path(__file__).resolve().parents[1] / "configs/data.json"


class PreprocessTests(unittest.TestCase):
    def setUp(self):
        self.config, _ = load_config(CONFIG)

    def image_bytes(self, mode="RGB", fmt="PNG", **kwargs):
        image = Image.new(mode, (3, 2))
        if mode == "RGB":
            image.putdata([(0, 1, 2), (20, 30, 40), (50, 60, 70),
                           (80, 90, 100), (120, 130, 140), (253, 254, 255)])
        stream = io.BytesIO()
        image.save(stream, format=fmt, **kwargs)
        return stream.getvalue()

    def test_native_rgb_normalization_and_roundtrip(self):
        raw = self.image_bytes()
        rgb, receipt = decode_source(raw, self.config)
        self.assertEqual(rgb.shape, (2, 3, 3))
        self.assertEqual(receipt["color_action"], "assumed-srgb-no-icc")
        self.assertEqual(receipt["caption"], "")
        unit = normalized(rgb)
        self.assertEqual(unit.dtype, np.float32)
        self.assertEqual(unit[-1, -1, -1], 1)
        data, decoded = encode_output(unit)
        self.assertTrue(np.array_equal(decoded, rgb))
        self.assertEqual(data, encode_output(unit)[0])
        with Image.open(io.BytesIO(data)) as saved:
            self.assertEqual(saved.info, {})

    def test_ties_even_clamp_and_nonfinite(self):
        values = np.array([[[-1, 0.5 / 255, 1.5 / 255], [2.5 / 255, 1, 2]]], dtype=np.float64)
        _, rgb = encode_output(values)
        self.assertEqual(rgb.tolist(), [[[0, 0, 2], [2, 255, 255]]])
        for value in (float("nan"), float("inf")):
            with self.assertRaises(PreprocessError):
                encode_output(np.full((1, 1, 3), value))
        with self.assertRaises(PreprocessError):
            encode_output(np.zeros((1, 1, 3), dtype=np.uint8))

    def test_exif_all_orientations_and_invalid(self):
        base, _ = decode_source(self.image_bytes(), self.config)
        # Independent expected array operations for EXIF 1..8.
        expect = [base, base[:, ::-1], base[::-1, ::-1], base[::-1],
                  base.transpose(1, 0, 2), np.rot90(base, 3),
                  base.transpose(1, 0, 2)[::-1, ::-1], np.rot90(base, 1)]
        for orientation in range(1, 9):
            exif = Image.Exif(); exif[274] = orientation
            actual, receipt = decode_source(self.image_bytes(exif=exif), self.config)
            self.assertTrue(np.array_equal(actual, expect[orientation-1]), orientation)
            self.assertEqual(receipt["exif_orientation"], orientation)
        exif = Image.Exif(); exif[274] = 9
        with self.assertRaisesRegex(PreprocessError, "orientation"):
            decode_source(self.image_bytes(exif=exif), self.config)

    def test_icc_srgb_and_bad_profile(self):
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        rgb, receipt = decode_source(self.image_bytes(icc_profile=profile), self.config)
        base, _ = decode_source(self.image_bytes(), self.config)
        self.assertTrue(np.array_equal(rgb, base))
        self.assertEqual(receipt["icc_sha256"], sha(profile))
        self.assertEqual(receipt["color_action"], "icc-to-srgb")
        self.assertEqual(Image.open(io.BytesIO(encode_output(normalized(rgb))[0])).info, {})
        with self.assertRaisesRegex(PreprocessError, "color_failure"):
            decode_source(self.image_bytes(icc_profile=b"not-a-profile"), self.config)

    def test_rejected_modes_corruption_and_limits(self):
        for mode in ("RGBA", "L", "I;16", "P"):
            with self.assertRaisesRegex(PreprocessError, "mode"):
                decode_source(self.image_bytes(mode), self.config)
        with self.assertRaises(PreprocessError):
            decode_source(self.image_bytes("CMYK", "JPEG"), self.config)
        with self.assertRaises(PreprocessError):
            decode_source(b"bad image", self.config)
        with self.assertRaises(PreprocessError):
            decode_source(self.image_bytes()[:-20], self.config)
        with self.assertRaisesRegex(PreprocessError, "pixel_count"):
            decode_source(self.image_bytes(), dict(self.config, max_pixels=5))
        with self.assertRaisesRegex(PreprocessError, "source_size"):
            decode_source(self.image_bytes(), dict(self.config, max_source_bytes=1))

    def test_hidden_rgb16_and_rgb_transparency_rejected(self):
        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind+data))
        raw = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 16, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(b"\0\x00\x01\x00\x02\x00\x03")) + chunk(b"IEND", b""))
        self.assertEqual(Image.open(io.BytesIO(raw)).mode, "RGB")
        with self.assertRaisesRegex(PreprocessError, "bit_depth"):
            decode_source(raw, self.config)
        with self.assertRaisesRegex(PreprocessError, "alpha"):
            decode_source(self.image_bytes(transparency=(0, 1, 2)), self.config)

    def test_cache_replay_source_binding_and_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "source.png"; raw = self.image_bytes()
            source.write_bytes(raw)
            cache = root / "cache"
            args = (source, sha(raw), len(raw), cache, CONFIG)
            first, receipt = preprocess_file(*args)
            second, again = preprocess_file(*args)
            self.assertTrue(np.array_equal(first, second))
            self.assertEqual(receipt, again)
            self.assertEqual(receipt["identity"]["runtime"], runtime())
            self.assertEqual(receipt["canonical_pixel_sha256"], pixel_sha((first * 255).astype(np.uint8)))
            with self.assertRaisesRegex(PreprocessError, "snapshot"):
                preprocess_file(source, "0"*64, len(raw), cache, CONFIG)
            output = cache / (receipt["cache_key"] + ".png")
            output.write_bytes(b"corrupted-cache-fixture")
            with self.assertRaisesRegex(PreprocessError, "cache_output"):
                preprocess_file(*args)
            self.assertEqual(output.read_bytes(), b"corrupted-cache-fixture")

    def test_runtime_policy_and_missing_cache_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); config = root / "config.json"
            data = json.loads(CONFIG.read_text()); data["resize"] = "hidden-512"
            config.write_text(json.dumps(data))
            with self.assertRaisesRegex(PreprocessError, "policy"):
                load_config(config)
            data = json.loads(CONFIG.read_text()); data["runtime_profiles"] = []
            config.write_text(json.dumps(data))
            with self.assertRaisesRegex(PreprocessError, "runtime"):
                load_config(config)
            raw = self.image_bytes(); source = root / "source.png"; source.write_bytes(raw)
            cache = root / "cache"
            _, receipt = preprocess_file(source, sha(raw), len(raw), cache, CONFIG)
            (cache / (receipt["cache_key"] + ".json")).unlink()  # Owned temporary fixture.
            with self.assertRaisesRegex(PreprocessError, "incomplete_cache"):
                preprocess_file(source, sha(raw), len(raw), cache, CONFIG)


    def test_self_consistent_cache_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "source.png"; raw = self.image_bytes()
            source.write_bytes(raw); cache = root / "cache"
            args = (source, sha(raw), len(raw), cache, CONFIG)
            _, receipt = preprocess_file(*args)
            replacement, rgb = encode_output(np.ones((2, 3, 3), dtype=np.float32))
            receipt.update(output_sha256=sha(replacement), output_size_bytes=len(replacement),
                           canonical_pixel_sha256=pixel_sha(rgb))
            output = cache / (receipt["cache_key"] + ".png")
            output.write_bytes(replacement)
            (cache / (receipt["cache_key"] + ".json")).write_text(json.dumps(receipt))
            with self.assertRaisesRegex(PreprocessError, "cache_source_canonical"):
                preprocess_file(*args)
            self.assertEqual(output.read_bytes(), replacement)


    def test_cache_ancillary_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "source.png"; raw = self.image_bytes()
            source.write_bytes(raw); cache = root / "cache"
            args = (source, sha(raw), len(raw), cache, CONFIG)
            _, receipt = preprocess_file(*args)
            rgb, _ = decode_source(raw, self.config)
            metadata = PngImagePlugin.PngInfo(); metadata.add_text("unexpected", "synthetic")
            stream = io.BytesIO(); Image.fromarray(rgb).save(stream, format="PNG", pnginfo=metadata)
            replacement = stream.getvalue()
            receipt.update(output_sha256=sha(replacement), output_size_bytes=len(replacement))
            output = cache / (receipt["cache_key"] + ".png"); output.write_bytes(replacement)
            (cache / (receipt["cache_key"] + ".json")).write_text(json.dumps(receipt))
            with self.assertRaisesRegex(PreprocessError, "output_metadata"):
                preprocess_file(*args)
            self.assertEqual(output.read_bytes(), replacement)


if __name__ == "__main__":
    unittest.main()
