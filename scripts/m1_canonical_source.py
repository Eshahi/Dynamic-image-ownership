"""Canonicalize already-authorized image bytes; this module cannot resolve paths."""
from __future__ import annotations
import hashlib
import io
import re

VERSION = 'm1-canonical-rgb512-v1'


def canonicalize(raw: bytes, expected_sha256: str):
    """Same RGB/EXIF/ICC/BICUBIC operations as development source_rgb.

    Caller owns source membership/authorization and bounded raw-byte acquisition.
    A matching hash here is integrity evidence, never scientific authorization.
    """
    if type(raw) is not bytes or not raw:
        raise ValueError('Nonempty immutable source bytes required')
    if type(expected_sha256) is not str or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('Exact lowercase SHA256 required')
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError('Source hash mismatch before decoding')
    import numpy as np
    from PIL import Image, ImageOps, ImageCms
    with Image.open(io.BytesIO(raw)) as original:
        if original.mode != 'RGB':
            raise ValueError('Only RGB inputs supported')
        original.load()
        icc = original.info.get('icc_profile')
        encoded_shape = [original.height, original.width, 3]
        orientation = original.getexif().get(274)
        image = ImageOps.exif_transpose(original)
        if icc:
            image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(icc)),
                ImageCms.createProfile('sRGB'), renderingIntent=0, outputMode='RGB', flags=0)
        native_shape = [image.height, image.width, 3]
        rgb = np.asarray(image.resize((512, 512), Image.Resampling.BICUBIC), dtype=np.uint8).copy()
    receipt = dict(schema=VERSION, raw_sha256=actual, raw_size_bytes=len(raw),
        encoded_shape=encoded_shape, native_shape=native_shape, exif_orientation=orientation,
        exif_transpose=True, icc_present=bool(icc),
        icc_sha256=hashlib.sha256(icc).hexdigest() if icc else None,
        icc_policy='profileToProfile sRGB intent0 RGB flags0 when present',
        resize='Pillow BICUBIC 512x512', rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),
        source_authorization='caller responsibility; hash is not authorization')
    return rgb, receipt
