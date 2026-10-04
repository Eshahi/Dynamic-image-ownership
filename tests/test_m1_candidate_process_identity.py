"""Real owned Windows redirector fixture, no models or acquired data."""
import json,os,sys,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import m1_candidate_process_identity as identity

class IdentityTests(unittest.TestCase):
    def test_foreign_worker_parent_and_scope_are_denied(self):
        scope=dict(child_pid=10,parent_pid=1,job_id='private',token_sha256='a'*64)
        request=dict(worker_pid=20,worker_parent_pid=10,root_pid=10,launcher_pid=1,job_id='private',token_sha256='a'*64)
        self.assertTrue(identity.verify_registration(scope,request,[10,20])['assignment_verified'])
        for field,value in [('worker_pid',99),('worker_parent_pid',99),('root_pid',11),('token_sha256','b'*64),('job_id','other')]:
            with self.subTest(field=field),self.assertRaises(ValueError):identity.verify_registration(scope,dict(request,**{field:value}),[10,20])
        direct=dict(request,worker_pid=10,worker_parent_pid=1)
        self.assertTrue(identity.verify_registration(scope,direct,[10])['assignment_verified'])
    @unittest.skipUnless(os.name=='nt','Windows redirector containment fixture')
    def test_real_venv_descendant_waits_for_exact_job_binding(self):
        from m1_windows_job import OwnedJobProcess
        from m1_owned_cleanup_evidence import job_snapshot,terminate_job
        python=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'logs').mkdir();token='a'*64
            code="import sys,json,pathlib;sys.path.insert(0,sys.argv[1]);from m1_candidate_process_identity import register_interpreter;p=pathlib.Path(sys.argv[2]);s=json.loads((p/'scope.json').read_text());v=register_interpreter(p,s,'a'*64);(p/'verified.json').write_text(json.dumps(v))"
            child=None
            with (root/'fixture.log').open('w') as log:
                def before(child):
                    scope=dict(child_pid=child.pid,parent_pid=os.getpid(),job_id=child.ownership['job_id'],token_sha256=__import__('hashlib').sha256(token.encode()).hexdigest())
                    (root/'scope.json').write_text(json.dumps(scope))
                try:
                    child=OwnedJobProcess([str(python),'-c',code,str(ROOT/'scripts'),str(root)],log,cwd=ROOT,before_resume=before)
                    deadline=time.monotonic()+10
                    while not (root/'logs/worker-process-registration.json').exists():
                        if time.monotonic()>deadline: self.fail('Registration absent')
                        time.sleep(.02)
                    self.assertFalse((root/'verified.json').exists())
                    scope=json.loads((root/'scope.json').read_text())
                    value=identity.accept_registration(root,scope,job_snapshot(child)['process_ids'])
                    self.assertEqual(value['root_pid'],child.pid)
                    self.assertNotEqual(value['worker_pid'],child.pid)
                    child.wait(10)
                    self.assertEqual(json.loads((root/'verified.json').read_text()),value)
                finally:
                    if child is not None:
                        if child.poll() is None:terminate_job(child)
                        child.close()

if __name__=='__main__':unittest.main()
