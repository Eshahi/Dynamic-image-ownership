"""Real bounded Windows fixture descendants; no arbitrary process lookup/kills."""
import ctypes
from ctypes import wintypes as w
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from scripts import m1_windows_job as job

@unittest.skipUnless(sys.platform=='win32','Windows Job Object test')
class WindowsContainment(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='m1-owned-job-fixture-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.token=str(uuid.uuid4());self.receipts=[]
        self.log=(self.root/'fixture.log').open('w');self.addCleanup(self.log.close)
        self.fixture=self.root/'owned_fixture.py'
        self.fixture.write_text('''import json,os,sys,time,subprocess
from pathlib import Path
root=Path(sys.argv[1]);token=sys.argv[2];role=sys.argv[3]
(root/(role+'.json')).write_text(json.dumps(dict(pid=os.getpid(),parent_pid=os.getppid(),token=token,role=role)))
if role in ('root','child'):
    subprocess.Popen([sys.executable,__file__,str(root),token,'child' if role=='root' else 'grandchild'])
time.sleep(30)
''',encoding='utf-8')
        # A Windows venv python.exe can itself be a launcher that spawns the
        # base interpreter. Use the actual interpreter for exact PID assertions.
        self.executable=getattr(sys,'_base_executable',sys.executable)
        self.command=[self.executable,str(self.fixture),str(self.root),self.token,'root']

    def receipt(self,value):
        self.receipts.append(value)
        (self.root/'owner-receipts.json').write_text(json.dumps(self.receipts),encoding='utf-8')

    def observe_fixture_handles(self,owned):
        deadline=time.monotonic()+5
        while not all((self.root/(role+'.json')).exists() for role in ('root','child','grandchild')):
            if time.monotonic()>deadline:raise AssertionError('Fixture descendants not started')
            time.sleep(.02)
        records={role:json.loads((self.root/(role+'.json')).read_text()) for role in ('root','child','grandchild')}
        self.assertEqual(records['root']['pid'],owned.pid)
        self.assertEqual(records['child']['parent_pid'],owned.pid)
        self.assertEqual(records['grandchild']['parent_pid'],records['child']['pid'])
        for value in records.values():self.assertEqual(value['token'],self.token)
        # Open only exact PIDs recorded by this test's token-bound fixture tree.
        op=job.bind('OpenProcess',[w.DWORD,w.BOOL,w.DWORD],w.HANDLE)
        handles=[job.checked(op(0x101000,False,r['pid'])) for r in records.values()]
        for handle in handles:self.addCleanup(job.Close,handle)
        return handles

    def assert_all_exited(self,handles):
        for handle in handles:self.assertEqual(job.Wait(handle,5000),0)

    def test_no_worker_instruction_before_verified_assignment(self):
        def suspended(owned):
            self.assertTrue(owned.ownership['assignment_verified'])
            self.assertEqual(self.receipts[-1]['state'],'assigned_suspended')
            time.sleep(.15)
            self.assertFalse((self.root/'root.json').exists())
        with job.OwnedJobProcess(self.command,self.log,receipt=self.receipt,before_resume=suspended) as owned:
            handles=self.observe_fixture_handles(owned)
        self.assert_all_exited(handles)

    def test_timeout_closes_entire_owned_descendant_tree(self):
        owned=job.OwnedJobProcess(self.command,self.log,receipt=self.receipt)
        try:
            handles=self.observe_fixture_handles(owned)
            with self.assertRaises(subprocess.TimeoutExpired):owned.wait(.05)
        finally:owned.close()
        self.assert_all_exited(handles)
        self.assertEqual(self.receipts[0]['state'],'created_suspended')

    def test_keyboard_interrupt_closes_entire_owned_tree(self):
        with self.assertRaises(KeyboardInterrupt):
            with job.OwnedJobProcess(self.command,self.log,receipt=self.receipt) as owned:
                handles=self.observe_fixture_handles(owned)
                raise KeyboardInterrupt('owned fixture interruption')
        self.assert_all_exited(handles)

    def test_assignment_failure_never_runs_child(self):
        from unittest.mock import patch
        with patch.object(job,'Assign',return_value=False):
            with self.assertRaises(OSError):job.OwnedJobProcess(self.command,self.log,receipt=self.receipt)
        self.assertEqual(self.receipts[0]['state'],'created_suspended')
        time.sleep(.1);self.assertFalse((self.root/'root.json').exists())

    def test_independent_owned_job_survives_other_job_close(self):
        command=[self.executable,'-c','import time;time.sleep(30)']
        with job.OwnedJobProcess(command,self.log,receipt=self.receipt) as unrelated:
            with job.OwnedJobProcess(self.command,self.log,receipt=self.receipt) as owned:
                handles=self.observe_fixture_handles(owned)
            self.assert_all_exited(handles);self.assertIsNone(unrelated.poll())
        self.assertIsNotNone(unrelated.returncode)

    def test_parent_handle_close_on_real_host_loss_kills_descendants(self):
        # Test launcher is itself our child. Closing its containing Job simulates
        # hard parent loss; its private inner Job handle cannot survive inheritance.
        launcher=self.root/'launcher.py'
        launcher.write_text('''import json,sys,time
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from m1_windows_job import OwnedJobProcess
root=Path(sys.argv[2]);token=sys.argv[3]
with (root/'inner.log').open('w') as log:
    def receipt(value):(root/'inner-receipt.json').write_text(json.dumps(value))
    child=OwnedJobProcess([sys.executable,str(root/'owned_fixture.py'),str(root),token,'root'],log,receipt=receipt)
    time.sleep(30)
''',encoding='utf-8')
        command=[self.executable,str(launcher),str(Path(job.__file__).parent),str(self.root),self.token]
        outer=job.OwnedJobProcess(command,self.log,receipt=self.receipt)
        try:
            deadline=time.monotonic()+5
            while not (self.root/'grandchild.json').exists():
                if time.monotonic()>deadline:raise AssertionError('Nested owned fixture failed')
                time.sleep(.02)
            receipt=json.loads((self.root/'inner-receipt.json').read_text())
            from types import SimpleNamespace
            handles=self.observe_fixture_handles(SimpleNamespace(pid=receipt['pid']))
            # Terminate only the owned launcher HANDLE, while its outer Job stays
            # OPEN. Descendant exit therefore exercises inner kill-on-close,
            # rather than relying on closing the outer containing Job.
            self.assertEqual(self.receipts[-1]['pid'],outer.pid)
            job.checked(job.Terminate(outer.process,1));outer.wait(5)
            self.assert_all_exited(handles)
        finally:outer.close()
        self.assert_all_exited(handles)

if __name__=='__main__':unittest.main()
