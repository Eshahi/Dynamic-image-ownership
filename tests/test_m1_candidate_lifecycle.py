"""CPU-only lifecycle scope/inventory/owned ordering tests; no candidate inference."""
import copy, hashlib, json, os, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import m1_candidate_lifecycle as l

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        for name,replacement in [('gpu_snapshot',lambda *a:dict(available=True,devices=[],owned_compute_pids=[],mocked=True)),
                ('job_snapshot',lambda p:dict(process_ids=[p.pid])),
                ('close_with_evidence',lambda p,*a:(p.close() or dict(cleanup_verified=True,mocked=True)))]:
            patcher=patch.object(l,name,replacement);patcher.start();self.addCleanup(patcher.stop)
    def worker(self):return SimpleNamespace(dependency_paths=lambda:[],configuration=lambda:{'literal_generated_rgb':True},scientific_core_sha256=lambda:'a'*64)
    def parity(self):return dict(passes=True,checks={k:True for k in ('initialization_exact','embedding_adam_rng_exact','endpoint_rgb8_exact','blind_decisions_exact','overlap_inventory_exact','overlap_states_adam_rng_exact')},
        overlap_checks={f'{phase}-{n}':True for phase,values in [('embedding',range(0,101,10)),('initialization',range(100,201,10))] for n in values})
    def manifest(self,stage='real'):
        return dict(schema_version='1.0',experiment_id='generated',run_id='generated-1',stage_id=stage,task_id='generated',
            execution_target='local',reviewed_script=Path(l.__file__).relative_to(ROOT).as_posix(),script_sha256=l.file_sha(l.__file__),
            git_commit='b'*40,seeds=[0,1],datasets=l.DATASET,inputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=l.file_sha(p)) for p in l.dependencies()],
            outputs=l.OUTPUTS,metrics=['candidate_generated_rehearsal_units'],budget=dict(max_seconds=1800,max_usd=0,hourly_usd=0),
            resources=dict(vram_mib=10240,ram_mib=16384,disk_mib=500),cleanup_policy='stop-for-recovery')

    def test_frozen_cases_earliest_meaningful_phases(self):
        cases=l.read(l.CATALOG)['cases']
        self.assertEqual(set(cases),{'real','scale','prefix','resume','kill','term','finalterm','timeout-early','timeout-unit','hostloss'}|{'error-'+p for p in ['model','initializer','embedding','save','detector','safety','finalization']})
        self.assertEqual(cases['prefix']['stop_step'],100)
        for name in ('kill','term','hostloss'):self.assertEqual(cases[name]['control']['step'],10)
        self.assertLess(cases['timeout-early']['control']['after_seconds'],1)

    def test_official_envelope_and_exact_input_allowlist(self):
        with patch.object(l,'adapter_worker',self.worker):
            good=self.manifest();self.assertEqual(l.validate_manifest(good)['stage'],'full')
            for mutation in [dict(datasets=[dict(id='coco',version='2017',license='x',split='test')]),dict(seeds=[1]),dict(inputs=[]),dict(execution_target='runpod')]:
                with self.assertRaises(ValueError):l.validate_manifest(dict(good,**mutation))
            bad=copy.deepcopy(good);bad['inputs'].append(dict(path='data/raw/private.png',sha256='c'*64))
            with self.assertRaises(ValueError):l.validate_manifest(bad)

    def test_main_only_and_no_dataset_destination(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(l,'MAIN',Path(temp)):
            self.assertEqual(l.destination(Path(temp)/'.thesis-build/rehearsal/attempt'),Path(temp)/'.thesis-build/rehearsal/attempt')
            for path in [Path(temp)/'data/raw/a',Path(temp)/'.thesis-build/rehearsal',Path(temp)/'.thesis-build/rehearsal/../dev-runs/a']:
                with self.assertRaises(ValueError):l.destination(path)

    def test_scope_requires_suspended_verified_assignment(self):
        with patch.object(l,'adapter_worker',self.worker),patch.object(l,'WORKER',Path(l.__file__)):
            manifest=self.manifest();case=l.validate_manifest(manifest)
            owned=dict(pid=123,job_id='private',assignment_verified=True,created_suspended=True)
            scope=l.capability(manifest,case,Path('output'),'secret',owned,None)
            self.assertEqual(scope['child_pid'],123);self.assertEqual(scope['manifest_sha256'],l.object_sha(manifest))
            self.assertEqual(scope['token_sha256'],hashlib.sha256(b'secret').hexdigest());self.assertNotIn('secret',json.dumps(scope))
            for key in ('assignment_verified','created_suspended'):
                with self.assertRaises(ValueError):l.capability(manifest,case,Path('output'),'secret',dict(owned,**{key:False}),None)

    def test_recovery_receipts_contained_and_immutable(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(l,'MAIN',Path(temp)):
            base=Path(temp)/'.thesis-build/rehearsal/prior';base.mkdir(parents=True)
            run=base/'run.json';checkpoint=base/'checkpoint.pt';run.write_text('{}');checkpoint.write_bytes(b'checkpoint')
            receipts={k:dict(path=str(p),sha256=l.file_sha(p)) for k,p in [('run',run),('checkpoint',checkpoint)]}
            self.assertEqual(l.upstream_receipts(receipts),receipts);checkpoint.write_bytes(b'changed')
            with self.assertRaises(ValueError):l.upstream_receipts(receipts)

    def test_lifecycle_trigger_requires_matching_checkpoint(self):
        control=dict(phase='initialization',step=10,after_seconds=None)
        self.assertFalse(l.triggered(control,{'phase':'embedding','step':10},1))
        self.assertFalse(l.triggered(control,{'phase':'initialization','step':0},1))
        self.assertTrue(l.triggered(control,{'phase':'initialization','step':10},1))
        self.assertTrue(l.triggered(dict(control,after_seconds=.1),None,.2))

    def test_owned_callback_precedes_worker_execution_and_token_restored(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(l,'MAIN',Path(temp)),patch.object(l,'adapter_worker',self.worker),patch.object(l,'pin_execution'),patch.object(l,'WORKER',Path(l.__file__)):
            manifest=self.manifest();path=Path(temp)/'manifest.json';path.write_text(json.dumps(manifest));output=Path(temp)/'.thesis-build/rehearsal/run'
            stages=[]
            class FakeJob:
                def __init__(self,command,log,*,cwd,receipt,before_resume):
                    self.ownership=dict(pid=999,job_id='mock',assignment_verified=True,created_suspended=True,state='assigned_suspended');self.pid=999;self.returncode=0
                    receipt(self.ownership);before_resume(self);stages.append('assigned_scope')
                    scope=l.read(Path(os.environ['M1_REHEARSAL_CAPABILITY']))
                    assert scope['child_pid']==999 and hashlib.sha256(os.environ['M1_REHEARSAL_TOKEN'].encode()).hexdigest()==scope['token_sha256']
                    stages.append('worker');l.atomic(output/'outputs/worker-run.json',{'generated_only':True})
                def poll(self):return 0
                def close(self):self.ownership['state']='closed'
            original={k:os.environ.get(k) for k in ('M1_REHEARSAL_TOKEN','M1_REHEARSAL_CAPABILITY')}
            with patch.object(l,'OwnedJobProcess',FakeJob):self.assertEqual(l.run(path,output),0)
            self.assertEqual(stages,['assigned_scope','worker'])
            self.assertEqual(original,{k:os.environ.get(k) for k in original})
            record=l.read(output/'outputs/lifecycle-run.json');self.assertEqual(record['scientific_verdict'],'NOT_EVIDENCE')
            self.assertEqual(record['candidate_verification'],'PENDING_INDEPENDENT_STAGE_AND_PARITY_AUDIT')

    def test_real_worker_scope_contract_without_models(self):
        import m1_candidate_rehearsal_worker as worker
        with tempfile.TemporaryDirectory() as temp,patch.object(l,'MAIN',Path(temp)),patch.object(worker,'MAIN',Path(temp)):
            manifest=self.manifest();case=l.validate_manifest(manifest);output=Path(temp)/'.thesis-build/rehearsal/actual-seam'
            token='f'*64;owned=dict(pid=os.getpid(),job_id='fixture-private-job',assignment_verified=True,created_suspended=True)
            scope=l.capability(manifest,case,output,token,owned,None)
            with patch.object(worker.os,'getppid',return_value=os.getpid()):
                self.assertEqual(worker.validate_launch_scope(manifest,output,scope=scope,token=token),scope)
                for mutation in [dict(child_pid=0),dict(worker_sha256='0'*64),dict(unit_index=1),dict(upstream={'path':'data/raw'}),dict(token_sha256='0'*64)]:
                    with self.assertRaises(ValueError):worker.validate_launch_scope(manifest,output,scope=dict(scope,**mutation),token=token)

    def test_suite_prefix_handoff_audited_before_resume_and_parity(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(l,'MAIN',Path(temp)),patch.object(l,'adapter_worker',self.worker):
            base=Path(temp)/'.thesis-build/rehearsal';base.mkdir(parents=True);inputs=base/'manifests';inputs.mkdir()
            paths=[]
            for stage in ('prefix','resume'):
                path=inputs/(stage+'.json');path.write_text(json.dumps(self.manifest(stage)));paths.append(str(path))
            suite=inputs/'suite.json';suite.write_text(json.dumps(dict(schema=l.VERSION,execution='unperformed',manifests=paths)))
            outputs=base/'suite-result';seen=[];audits=[]
            def audit(directory):
                audits.append(Path(directory).name);record=l.read(Path(directory)/'outputs/worker-run.json')
                return dict(record,latest_checkpoint=dict(path=str(Path(directory)/'checkpoints/checkpoint.pt'),sha256=l.file_sha(Path(directory)/'checkpoints/checkpoint.pt')))
            worker=self.worker();worker.audit_rehearsal_run=audit;worker.compare_full_resume=lambda full,resumed:self.parity()
            class FakeOuter:
                def __init__(self,command,log,*,cwd,receipt):
                    manifest=l.read(Path(command[command.index('--manifest')+1]));out=Path(command[command.index('--output-dir')+1]);out.mkdir(parents=True)
                    seen.append(manifest['stage_id']);self.ownership={'state':'assigned','pid':123};self.pid=123;self.returncode=0;receipt(self.ownership)
                    if manifest['stage_id']=='resume':
                        selftest.assertIn('prefix-0',audits)
                        handoff=l.read(Path(command[command.index('--upstream-receipt')+1]));selftest.assertEqual(set(handoff),{'run','checkpoint'})
                    l.atomic(out/'outputs/worker-run.json',dict(outcome='prefix_completed' if manifest['stage_id']=='prefix' else 'completed',unit_index=0))
                    (out/'checkpoints').mkdir();(out/'checkpoints/checkpoint.pt').write_bytes(b'fixed-state')
                def poll(self):return 0
                def close(self):self.ownership['state']='closed'
            selftest=self
            with patch.object(l,'adapter_worker',return_value=worker),patch.object(l,'OwnedJobProcess',FakeOuter):
                self.assertEqual(l.coordinate_suite(suite,outputs,['prefix','resume'],reference_full=base/'full-reference'),0)
            self.assertEqual(seen,['prefix','resume']);record=l.read(outputs/'suite-run.json')
            self.assertEqual(record['attempts'][1]['full_resume_parity'],self.parity())
            self.assertEqual(record['attempts'][0]['ownership']['state'],'closed')
            bad=self.parity();bad['checks']['embedding_adam_rng_exact']=False
            worker.compare_full_resume=lambda full,resumed:bad
            with patch.object(l,'adapter_worker',return_value=worker),patch.object(l,'OwnedJobProcess',FakeOuter):
                l.coordinate_suite(suite,base/'failed-parity',['prefix','resume'],reference_full=base/'full-reference')
            failed=l.read(base/'failed-parity/suite-run.json')['attempts'][1]
            self.assertEqual(failed['candidate_receipt_audit']['outcome'],'failed')
            self.assertFalse(failed['full_resume_parity']['checks']['embedding_adam_rng_exact'])

    def test_parity_missing_false_nonboolean_and_contradiction_fail(self):
        self.assertEqual(l.require_parity(self.parity()),self.parity())
        for name in self.parity()['checks']:
            for value in (False,None,1):
                bad=self.parity();bad['checks'][name]=value
                with self.assertRaises(ValueError):l.require_parity(bad)
        for bad in [dict(passes=True,checks={}),dict(self.parity(),passes=False),dict(self.parity(),endpoint_rgb8_exact=False)]:
            with self.assertRaises(ValueError):l.require_parity(bad)
        bad=self.parity();bad['overlap_checks']['embedding-50']=False
        with self.assertRaises(ValueError):l.require_parity(bad)
        bad=self.parity();bad['overlap_checks'].pop('initialization-100')
        with self.assertRaises(ValueError):l.require_parity(bad)

class CleanupEvidenceTests(unittest.TestCase):
    def test_exact_owned_job_quiescence_precedes_close_and_scoped_gpu_check(self):
        import m1_owned_cleanup_evidence as c
        calls=[];process=SimpleNamespace(pid=10,ownership={'job_id':'private'},close=lambda:calls.append('close'))
        baseline=dict(available=True,devices=[dict(uuid='gpu',free_mib=100,total_mib=200)],owned_compute_pids=[])
        after=dict(available=True,devices=[dict(uuid='gpu',free_mib=100,total_mib=200)],owned_compute_pids=[])
        snapshots=[dict(active_process_count=2,process_ids=[10,11]),dict(active_process_count=0,process_ids=[])]
        with patch.object(c,'job_snapshot',side_effect=snapshots),patch.object(c,'terminate_job',side_effect=lambda p:calls.append('terminate-private-job')),patch.object(c,'gpu_snapshot',return_value=after) as telemetry:
            evidence=c.close_with_evidence(process,baseline)
        self.assertEqual(calls,['terminate-private-job','close']);self.assertTrue(evidence['cleanup_verified'])
        self.assertEqual(evidence['owned_pids_observed'],[10,11]);telemetry.assert_called_once_with({10,11})
        self.assertEqual(evidence['free_memory_delta_mib'],{'gpu':0})

    def test_missing_gpu_telemetry_does_not_claim_cleanup_verified(self):
        import m1_owned_cleanup_evidence as c
        process=SimpleNamespace(pid=10,ownership={'job_id':'private'},close=lambda:None)
        snapshot=dict(active_process_count=0,process_ids=[])
        with patch.object(c,'job_snapshot',return_value=snapshot),patch.object(c,'terminate_job'),patch.object(c,'gpu_snapshot',return_value=dict(available=False,owned_compute_pids=None)):
            evidence=c.close_with_evidence(process)
        self.assertTrue(evidence['job_quiescent']);self.assertIsNone(evidence['owned_gpu_pids_absent']);self.assertFalse(evidence['cleanup_verified'])

if __name__=='__main__':unittest.main()
