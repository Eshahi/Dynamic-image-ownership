"""Exercise worker finalization through main, with model/file boundaries replaced by fixtures."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests.test_m1b_e3_s1_worker import W, Fake, fixture


class MainTests(unittest.TestCase):
    def test_finished_s1_run_keeps_analysis_selection_and_writes_endpoints(self):
        plan = fixture(); plan['max_wall_seconds'] = 27000
        sources = W.load_sources(plan)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); manifest = root / 'input.json'; plan_path = root/'fixture.m1b-plan.json'
            manifest.write_text(json.dumps(dict(budget=dict(max_seconds=28800))))
            plan_path.write_text(json.dumps(plan))
            with patch.object(W, 'find_plan', return_value=(plan_path, plan)), \
                 patch.object(W, 'validate_plan', return_value=(plan, sources)), \
                 patch.object(W, 'sha_file', return_value='0'*64), \
                 patch.object(W, '_git', side_effect=lambda *args: 'fixture-commit' if args[0]=='rev-parse' else ''), \
                 patch.object(W, 'scientific_core', return_value=dict(core_sha256='0'*64,code_sha256={},data_sha256={})), \
                 patch.object(W, 'preflight', return_value=dict(synthetic=True)), \
                 contextlib.redirect_stdout(io.StringIO()):
                code = W.main(['--manifest',str(manifest),'--output-dir',str(root/'run')], runtime_factory=lambda _:Fake())
            self.assertEqual(code, 0)
            run = json.loads((root/'run/outputs/run.json').read_text())
            endpoints = json.loads((root/'run/metrics/endpoints.json').read_text())
            self.assertNotIn('analysis_error',run)
            self.assertTrue(endpoints['inventory']['complete'])
            self.assertEqual(run['t5_selection'], endpoints['t5_selection'])
            self.assertEqual(run['t5_selection']['selected_pairs'], 1)


if __name__ == '__main__': unittest.main()
