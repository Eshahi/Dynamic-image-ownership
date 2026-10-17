"""Mechanical development recovery tests; no models, data, or held-out access."""
import contextlib
import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import m1b_registry_runtime as R
import m1b_coco512_worker as W


class Recovery(unittest.TestCase):
    def test_canonical_hash_mismatch_remains_integrity_failure(self):
        import m1b_canonical_source as canonical
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'invalid.png'
            path.write_bytes(b'not image bytes')
            with self.assertRaisesRegex(ValueError, 'Source hash mismatch') as raised:
                canonical.registry_canonical(dict(raw_path=str(path), raw_sha256='0' * 64), 'development')
            self.assertEqual(type(raised.exception), ValueError)

    def test_verified_undecodable_bytes_are_scientific_failure(self):
        import m1b_canonical_source as canonical
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'invalid.png'
            raw = b'not image bytes'
            path.write_bytes(raw)
            with self.assertRaises(canonical.CanonicalScientificFailure):
                canonical.registry_canonical(dict(raw_path=str(path), raw_sha256=hashlib.sha256(raw).hexdigest()), 'development')

    def test_scorer_wrapper_normalizes_missing_canonical_without_dropping_source(self):
        from m1b_registry_scorer import Cohort
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            cohort = Cohort(base / 'fresh', base / 'canonical', [1, 2], [], [], [])
            # A valid enrollment for another source exposes the missing C0 path
            # in frozen wrong-source negatives; preserve it as a missing row.
            record = base / 'fresh/2/supplier-attempt1/F5-bootstrap.png'
            record.parent.mkdir(parents=True)
            record.write_bytes(b'only existence is inspected')
            suspects = cohort.suspects(1)
            self.assertEqual(len(suspects), 38)
            self.assertEqual(suspects[0], ('clean', None, None, 'C0', None))
            self.assertEqual(cohort.record(2), str(record))
            self.assertEqual(cohort.sids, [1, 2])

    def test_actual_run_fault_resume_keeps_scientific_failure(self):
        import numpy as np
        from PIL import Image
        calls = dict(canonical=0, embed=0, attacks=0, close=0)
        order = []
        image = np.zeros((2, 2, 3), dtype=np.uint8)

        class FakeRuntime:
            def __init__(self, plan):
                assert order[-1:] == ['preflight'], 'Footage must precede the network block'
                order.append('runtime')
                self.np = np
                self.torch = SimpleNamespace(cuda=SimpleNamespace(empty_cache=lambda: None))
            def load(self, path):
                with Image.open(path) as im:
                    return np.asarray(im).copy()
            def embed(self, rgb, folder):
                calls['embed'] += 1
                raise R.ScientificFailure('deterministic supplier miss')
            def attack(self, rgb, model, strength, seed):
                calls['attacks'] += 1
                return rgb, dict(mock=True)
            def native(self, rgb, owner):
                return {}
            def descriptor(self, rgb, path):
                return dict(mock=True)
            def close(self):
                calls['close'] += 1

        def canonical(*args):
            calls['canonical'] += 1
            return image, dict(mock=True)

        sources = [dict(source_id=1, uid='synthetic-recovery-only')]
        fault = 't3:sd15:1:0.1:16:C0'
        plan = dict(data_split='development', near=[], models=['sd15', 'sd21'],
                    strengths=[.1, .2, .4], seeds=[15, 16, 17], max_wall_seconds=60,
                    fault_injection=dict(unit=fault, kind='infrastructure'))
        with tempfile.TemporaryDirectory() as temp, contextlib.ExitStack() as stack:
            out = Path(temp)
            stack.enter_context(patch.object(R, 'validate_plan', return_value=(plan, sources)))
            stack.enter_context(patch.object(R, 'scientific_core', return_value=dict(core_sha256='mock-science')))
            stack.enter_context(patch.object(W, 'bind_manifest'))
            stack.enter_context(patch('m1b_registry_footage.prepare_near', side_effect=lambda *a, **kw: order.append('preflight') or []))
            stack.enter_context(patch('m1b_canonical_source.registry_canonical', side_effect=canonical))
            stack.enter_context(patch('m1b_registry_analysis.analyze', return_value=dict(pass_=False, mock=True)))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            with self.assertRaisesRegex(OSError, 'Injected infrastructure'):
                R.run(dict(git_commit='mock'), plan, out, FakeRuntime)
            first = W.Journal(out)
            self.assertEqual(first.get('embed:1')['outcome'], 'scientific_failure')
            self.assertNotIn(fault, first)
            self.assertEqual(calls['attacks'], 1)
            before = dict(first.rows)
            # Simulate process death during the next append. Real run() repairs it.
            with first.path.open('ab') as stream:
                stream.write(b'{"id":"torn')
            self.assertEqual(R.run(dict(git_commit='mock'), plan, out, FakeRuntime), 0)
            rows = W.Journal(out).rows
            self.assertEqual(calls, dict(canonical=1, embed=1, attacks=18, close=2))
            self.assertEqual(order, ['preflight', 'runtime', 'preflight', 'runtime'])
            for rid, row in before.items():
                self.assertEqual(rows[rid], row)
            self.assertEqual(rows['enroll:1']['outcome'], 'input_unavailable')
            self.assertEqual(rows[fault]['outcome'], 'completed')
            self.assertEqual(json.loads((out / 'outputs/run.json').read_text())['outcome'], 'completed')
            self.assertEqual(json.loads((out / 'outputs/fault-triggered.json').read_text())['unit'], fault)

    def test_journal_rejects_interior_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = W.Journal(Path(temp))
            journal.path.write_bytes(b'{broken}\n{"id":"valid"}\n')
            with self.assertRaisesRegex(ValueError, 'before its last line'):
                W.Journal(Path(temp))

    def test_torn_multibyte_utf8_tail_is_recoverable(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = W.Journal(Path(temp))
            journal.emit(dict(id='kept', outcome='completed'))
            with journal.path.open('ab') as stream:
                stream.write(b'{"id":"\xe2\x82')
            resumed = W.Journal(Path(temp))
            self.assertEqual(list(resumed.rows), ['kept'])
            self.assertEqual(resumed.torn_lines, 1)


if __name__ == '__main__':
    unittest.main()
