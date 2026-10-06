"""Canonical RGB8 512x512 source, v2: v1 operations plus an explicit, receipted mode conversion.

v1 (`m1_canonical_source.canonicalize`) rejects every non-RGB file. MS-COCO contains a few
grayscale JPEGs; under v1 each would be a failed source, counted adversely as a miss and as a
false attribution, for a preprocessing reason alone. v2 (declared before any held-out outcome)
converts single-channel, palette, CMYK and YCbCr images to RGB after EXIF transpose and ICC
handling and records the conversion. Images with alpha or high-bit-depth modes are still
rejected. RGB inputs give exactly the v1 pixels.
"""
from __future__ import annotations

import hashlib
import io
import re

VERSION = "m1b-canonical-rgb512-v2"
CONVERTIBLE = ("L", "P", "CMYK", "YCbCr")


def canonicalize(raw: bytes, expected_sha256: str):
    if type(raw) is not bytes or not raw:
        raise ValueError("Nonempty immutable source bytes required")
    if type(expected_sha256) is not str or not re.fullmatch("[0-9a-f]{64}", expected_sha256):
        raise ValueError("Exact lowercase SHA256 required")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError("Source hash mismatch before decoding")
    import numpy as np
    from PIL import Image, ImageCms, ImageOps
    with Image.open(io.BytesIO(raw)) as original:
        mode = original.mode
        if mode != "RGB" and mode not in CONVERTIBLE:
            raise ValueError(f"Unsupported source mode {mode}")
        original.load()
        icc = original.info.get("icc_profile")
        encoded_shape = [original.height, original.width, len(original.getbands())]
        orientation = original.getexif().get(274)
        image = ImageOps.exif_transpose(original)
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                                              ImageCms.createProfile("sRGB"), renderingIntent=0, outputMode="RGB", flags=0)
        converted = None
        if image.mode != "RGB":
            converted = dict(from_mode=image.mode, to_mode="RGB", method="Pillow Image.convert('RGB')")
            image = image.convert("RGB")
        native_shape = [image.height, image.width, 3]
        rgb = np.asarray(image.resize((512, 512), Image.Resampling.BICUBIC), dtype=np.uint8).copy()
    receipt = dict(schema=VERSION, raw_sha256=actual, raw_size_bytes=len(raw), encoded_mode=mode,
                   encoded_shape=encoded_shape, native_shape=native_shape, exif_orientation=orientation,
                   exif_transpose=True, icc_present=bool(icc),
                   icc_sha256=hashlib.sha256(icc).hexdigest() if icc else None,
                   icc_policy="profileToProfile sRGB intent0 RGB flags0 when present",
                   mode_conversion=converted, resize="Pillow BICUBIC 512x512",
                   rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest())
    return rgb, receipt
