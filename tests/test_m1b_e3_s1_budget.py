"""Budget checks use official attempt elapsed time, not just successful image units."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m1b_coco512_worker as W


class BudgetTests(unittest.TestCase):
    def test_parent_attempts_include_failed_and_model_time(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for n, parent in [('a', None), ('b', str(root / 'a'))]:
                p = root / n; (p / 'outputs').mkdir(parents=True)
                (p / 'manifest.json').write_text(json.dumps(dict(status='failed',
                    started_at='2026-10-10T10:00:00Z', ended_at='2026-10-10T10:02:00Z')))
                (p / 'outputs/lineage.json').write_text(json.dumps(dict(parent=parent)))
            attempts = W.s1_parent_attempts(dict(resume_from=str(root/'b')))
            self.assertEqual(sum(a['elapsed_seconds'] for a in attempts), 242)
            m = root/'a/manifest.json'; data=json.loads(m.read_text()); data['ended_at']=None
            m.write_text(json.dumps(data))
            with self.assertRaises(ValueError): W.s1_parent_attempts(dict(resume_from=str(root/'b')))

    def test_ram_and_disk_limits_stop_infrastructure(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(W, 'peak_process_ram_bytes', return_value=17*2**30):
                with self.assertRaises(W.InfrastructureStop): W.s1_resource_check(Path(td), [])()
            with patch.object(W, 'peak_process_ram_bytes', return_value=1), \
                 patch.object(W.shutil, 'disk_usage', return_value=type('D', (), dict(free=19*2**30))()):
                with self.assertRaises(W.InfrastructureStop): W.s1_resource_check(Path(td), [])()

    def test_native_ram_counter_available(self):
        self.assertGreater(W.peak_process_ram_bytes(), 0)


if __name__ == '__main__': unittest.main()
