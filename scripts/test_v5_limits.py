"""Deadline-boundary tests: no GPU, model, dataset or real child process."""
import ast
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_v5_study as prep
import run_v5_study as launcher
import v5_study_limits as limits


class DeadlineTests(unittest.TestCase):
    def test_manifest_ceiling_and_bound_input(self):
        with patch.object(prep.subprocess, 'check_output', side_effect=['', 'a'*40]), patch.object(prep, 'sha', return_value='0'*64):
            manifest = prep.build(rehearsal=True)
        self.assertEqual(manifest['budget'], {'max_seconds':2700,'max_usd':0,'hourly_usd':0})
        self.assertIn('scripts/v5_study_limits.py', [r['path'] for r in manifest['inputs']])
        estimate = json.loads((prep.ROOT/'experiments'/prep.EXP/'compute-estimate.json').read_text())
        self.assertEqual(estimate['budget'], manifest['budget'])
        self.assertLess(limits.WORKER_SECONDS, limits.WSL_SECONDS)
        self.assertLess(limits.WSL_SECONDS + limits.KILL_GRACE_SECONDS, limits.LAUNCHER_SECONDS)
        self.assertLess(limits.LAUNCHER_SECONDS, manifest['budget']['max_seconds'])

    def test_launcher_passes_bounded_timeout_and_refuses_old_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'logs').mkdir(); path=root/'input.json'
            manifest={'run_id':launcher.RUN,'execution_target':'local','budget':dict(limits.BUDGET)}
            path.write_text(json.dumps(manifest))
            with patch.object(sys,'argv',['launcher','--manifest',str(path),'--output-dir',str(root)]), patch.object(launcher,'command',return_value=['fake-bounded-child']), patch.object(launcher.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as child:
                self.assertEqual(launcher.main(),0)
                self.assertEqual(child.call_args.kwargs['timeout'],2650)
            manifest['budget']['max_seconds']=86400
            path.write_text(json.dumps(manifest))
            with patch.object(sys,'argv',['launcher','--manifest',str(path),'--output-dir',str(root)]), patch.object(launcher.subprocess,'run') as child:
                with self.assertRaisesRegex(ValueError,'watchdog'):
                    launcher.main()
                child.assert_not_called()

    def test_worker_guard_deadline_boundary(self):
        # Extract the actual guard to exercise its boundary on Windows without importing GPU dependencies.
        tree=ast.parse(Path(launcher.__file__).with_name('v5_study_worker.py').read_text())
        guard=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='guard')
        clock=SimpleNamespace(monotonic=lambda:2499.999)
        scope={'time':clock,'started':0,'WORKER_SECONDS':limits.WORKER_SECONDS,
            'resource':SimpleNamespace(RUSAGE_SELF=0,getrusage=lambda _:SimpleNamespace(ru_maxrss=0)),
            'torch':SimpleNamespace(cuda=SimpleNamespace(max_memory_reserved=lambda:0)), 'image_bytes':[0]}
        exec(compile(ast.Module(body=[guard],type_ignores=[]),'worker_guard','exec'),scope)
        scope['guard']()
        clock.monotonic=lambda:2500
        with self.assertRaisesRegex(TimeoutError,'watchdog'):
            scope['guard']()

    @unittest.skipUnless(sys.platform=='win32','Windows launcher paths')
    def test_wsl_hard_timeout_command(self):
        cmd=launcher.command('C:/manifest.json','C:/out')
        self.assertEqual(cmd[2:7],['timeout','--signal=TERM','--kill-after=30s','2600s','env'])


if __name__=='__main__':
    unittest.main()
