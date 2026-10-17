"""Synthetic-only tests of actual footage preflight and resume; no network/data."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import m1b_registry_footage as F


class Footage(unittest.TestCase):
    def fixture(self, root, selected=20, reserve=1, prior=None):
        import numpy as np
        docs = root / 'research/registry-confirmation'
        docs.mkdir(parents=True)
        ffmpeg = root / 'mock-decoder'
        ffmpeg.write_bytes(b'synthetic decoder identity only')
        def shot(index):
            return dict(shot=f's{index:02d}', frames=[dict(offset=offset, url=f'mock://{index * 4 + side + 1}')
                        for side, offset in enumerate((0, 72, 144, 288))])
        records = [shot(i) for i in range(selected + reserve)]
        for name, data in {
            'tears-of-steel-shots-index.json': dict(selected=records[:selected], ordered_replacement_reserve=records[selected:]),
            'model-lock.json': dict(ffmpeg=dict(path=str(ffmpeg), sha256=hashlib.sha256(ffmpeg.read_bytes()).hexdigest())),
            'development-frame-exposure-index.json': dict(frames=[] if prior is None else [dict(rgb8_sha256=prior)]),
        }.items():
            (docs / name).write_text(json.dumps(data))
        out = root / 'out'
        (out / 'outputs').mkdir(parents=True)
        def decode(path, decoder):
            value = int(Path(path).read_bytes())
            return np.full((2, 2, 3), value, dtype=np.uint8), dict(mock=True)
        return out, decode

    def acquire(self, out):
        return F.prepare_near(dict(data_split='test'), out, lambda: None, heldout_authorized=True)

    def test_resume_reuses_frames_and_duplicate_uses_fixed_reserve(self):
        import numpy as np
        prior = hashlib.sha256(np.full((2, 2, 3), 1, dtype=np.uint8).tobytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root, prior=prior)
            def fetch(url, timeout):
                return io.BytesIO(url.removeprefix('mock://').encode())
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', side_effect=fetch) as network, patch('registry_fresh_acquire.exr_rgb', side_effect=decode):
                pairs = self.acquire(out)
                self.assertEqual(len(pairs), 60)
                self.assertEqual({p['shot'] for p in pairs}, {f's{i:02d}' for i in range(1, 21)})
                self.assertEqual(network.call_count, 84)
                state = json.loads((out / 'outputs/footage/preflight.json').read_text())
                self.assertTrue(state['shots']['s00']['excluded_duplicate'])
                network.side_effect = AssertionError('resume attempted network access')
                self.assertEqual(self.acquire(out), pairs)
                self.assertFalse(list((out / 'outputs/footage').glob('*.exr')))

    def test_reserve_exhaustion_is_explicit_and_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root, selected=1, reserve=1)
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', side_effect=lambda url, timeout: io.BytesIO(url.removeprefix('mock://').encode())), patch('registry_fresh_acquire.exr_rgb', side_effect=decode):
                with self.assertRaisesRegex(RuntimeError, 'replacement reserve exhausted'):
                    self.acquire(out)
                state = json.loads((out / 'outputs/footage/preflight.json').read_text())
                self.assertFalse(state['complete'])
                self.assertEqual(len(state['pairs']), 6)
                self.assertEqual(len(state['shots']), 2)

    def test_partial_frame_receipts_resume_without_redownloading(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root)
            attempted = []
            def interrupted_decode(path, decoder):
                value = int(Path(path).read_bytes())
                attempted.append(value)
                if value == 2 and attempted.count(2) == 1:
                    raise OSError('synthetic decoder infrastructure interruption')
                return decode(path, decoder)
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', side_effect=lambda url, timeout: io.BytesIO(url.removeprefix('mock://').encode())) as network, patch('registry_fresh_acquire.exr_rgb', side_effect=interrupted_decode):
                with self.assertRaisesRegex(OSError, 'infrastructure interruption'):
                    self.acquire(out)
                self.assertEqual(network.call_count, 2)
                self.assertEqual(len(self.acquire(out)), 60)
                self.assertEqual(network.call_count, 80)
                self.assertEqual(attempted.count(1), 1)
                self.assertEqual(attempted.count(2), 2)

    def test_missing_completed_receipt_image_is_infrastructure_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root)
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', side_effect=lambda url, timeout: io.BytesIO(url.removeprefix('mock://').encode())), patch('registry_fresh_acquire.exr_rgb', side_effect=decode):
                pairs = self.acquire(out)
                Path(pairs[0]['left_path']).unlink()
                with self.assertRaises(FileNotFoundError):
                    self.acquire(out)

    def test_download_bytes_persist_before_interrupted_frame(self):
        class InterruptedResponse(io.BytesIO):
            def read(self, size=-1):
                if self.tell():
                    raise OSError('synthetic disconnected response')
                return super().read(size)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root)
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', return_value=InterruptedResponse(b'12345')), patch('registry_fresh_acquire.exr_rgb', side_effect=decode):
                with self.assertRaisesRegex(OSError, 'disconnected'):
                    self.acquire(out)
                state = json.loads((out / 'outputs/footage/preflight.json').read_text())
                self.assertEqual(state['downloaded_bytes'], 5)

    def test_cap_exceeded_bytes_remain_charged_after_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, decode = self.fixture(root)
            dest = out / 'outputs/footage'
            dest.mkdir()
            history = dest / 'preflight.json'
            cap = 3 * 2**30
            history.write_text(json.dumps(dict(shots={}, pairs=[], downloaded_bytes=cap - 1)))
            with patch.object(F, 'ROOT', root), patch.object(F.urllib.request, 'urlopen', side_effect=lambda url, timeout: io.BytesIO(b'12')), patch('registry_fresh_acquire.exr_rgb', side_effect=decode):
                for expected in (cap + 1, cap + 3):
                    with self.assertRaisesRegex(RuntimeError, 'incremental acquisition cap'):
                        self.acquire(out)
                    self.assertEqual(json.loads(history.read_text())['downloaded_bytes'], expected)


if __name__ == '__main__':
    unittest.main()
