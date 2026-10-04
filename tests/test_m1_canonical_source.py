import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image, ImageCms
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m1_canonical_source as canonical
import m1_dual_latent as legacy


class CanonicalSourceTests(unittest.TestCase):
    def fixture(self, orientation=None, icc=False):
        y, x = np.indices((31, 57))
        rgb = np.stack((x*4, y*7, (x+y)*2), axis=-1).astype(np.uint8)
        image = Image.fromarray(rgb)
        options = {}
        if orientation is not None:
            exif = Image.Exif(); exif[274] = orientation; options['exif'] = exif
        if icc:
            options['icc_profile'] = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
        stream = io.BytesIO(); image.save(stream, format='PNG', **options)
        return stream.getvalue()

    def test_exact_development_preprocessing_parity(self):
        for orientation, icc in ((None, False), (6, False), (None, True), (8, True)):
            with self.subTest(orientation=orientation, icc=icc), tempfile.TemporaryDirectory() as tmp:
                raw = self.fixture(orientation, icc); digest = hashlib.sha256(raw).hexdigest()
                path = Path(tmp)/'generated.png'; path.write_bytes(raw)
                old, native = legacy.source_rgb({'path':str(path), 'sha256':digest})
                new, receipt = canonical.canonicalize(raw, digest)
                np.testing.assert_array_equal(new, old)
                self.assertEqual(native, receipt['native_shape'])
                self.assertEqual(receipt['icc_present'], icc)
                self.assertEqual(receipt['exif_orientation'], orientation)
                self.assertEqual(receipt['rgb8_sha256'], hashlib.sha256(old.tobytes()).hexdigest())

    def test_hash_rejection_precedes_decode(self):
        with patch('PIL.Image.open', side_effect=AssertionError('must not decode')):
            with self.assertRaises(ValueError): canonical.canonicalize(b'invalid', '0'*64)

    def test_non_rgb_never_silently_converted(self):
        for mode in ('L', 'RGBA', 'P'):
            stream = io.BytesIO(); Image.new(mode, (5, 7)).save(stream, format='PNG')
            raw = stream.getvalue()
            with self.assertRaises(ValueError): canonical.canonicalize(raw, hashlib.sha256(raw).hexdigest())

    def test_bad_icc_retained_as_failure(self):
        stream = io.BytesIO(); Image.new('RGB',(5,7)).save(stream,format='PNG',icc_profile=b'bad profile')
        raw = stream.getvalue()
        with self.assertRaises((ImageCms.PyCMSError, OSError)): canonical.canonicalize(raw,hashlib.sha256(raw).hexdigest())


if __name__ == '__main__': unittest.main()
