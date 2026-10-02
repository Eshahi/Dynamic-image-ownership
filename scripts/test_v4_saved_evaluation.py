"""Model-free saved-evaluation boundary and real Windows detachment tests."""
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import hashlib
import prepare_v4_saved_evaluation as prepare
from run_v4_saved_evaluation import (command, launch, main, WORKER_MARGIN, TERM_MARGIN, KILL_AFTER,
                                     LAUNCH_MARGIN)
from v4_durable_host import (detach, creation_time, host, process_identity, child_handshake,
                             parent_handshake, validate_ready, ack_value, identity_alive, wait_json)
from v4_durable_host import verify_preflight, PREFLIGHT_RUN
from v4_evaluation_journal import atomic_json, object_sha, file_sha

CORE_INPUTS = (
    "experiments/c4-three-threat-small-v1/runtime-files-v2.json",
    "experiments/c4-three-threat-small-v1/semantic-labels.json",
    "experiments/c4-v4-three-threat-recovery-v1/acceptance-criteria.md",
    "experiments/c4-v4-three-threat-recovery-v1/evaluation-core.json",
    "experiments/c4-v4-three-threat-recovery-v1/experiment-spec.yaml",
    "experiments/c4-v4-three-threat-recovery-v1/parent-input-lock.json",
    "experiments/c4-v4-three-threat-recovery-v1/plan.md",
    "experiments/c4-v4-three-threat-recovery-v1/schedule.json",
    "experiments/c4-v4-three-threat-small-v1/acceptance-criteria.md",
    "experiments/c4-v4-three-threat-small-v1/profile.json",
    "research/a6-candidate-model-assets.json",
    "research/method-amendment-decision-20261001.md",
    "research/method-amendment-v4.md",
    "research/proposal-aligned-plan-20260930.md",
    "research/research-contract.md",
    "research/scope-guard.md",
    "scripts/a6_clip_visual.py",
    "scripts/check_a6_lpips_assets.py",
    "scripts/qim_rgb_pilot.py",
    "scripts/revised_watermark.py",
    "scripts/revised_watermark_v3.py",
    "scripts/revised_watermark_v4.py",
    "scripts/three_threat_models.py",
    "scripts/three_threat_protocol.py",
    "scripts/v4_evaluation_journal.py",
    "scripts/v4_recovery_design.py",
    "scripts/v4_saved_evaluation_adapter.py",
    "scripts/v4_study_protocol.py",
    "scripts/verify_science_assets.py",
)
HARNESS_INPUTS = ("scripts/prepare_v4_saved_evaluation.py","scripts/run_v4_saved_evaluation.py",
                  "scripts/run_v4_study.py","scripts/v4_saved_evaluation_worker.py")


def manifest_fixture(run_id="c4-v4-saved-evaluation-004",commit="a"*40,harness="c"*64):
    """Shape of a prepared manifest without Git or the parent run."""
    value=prepare.core()
    return {"schema_version":"1.0","run_id":run_id,**{key:value[key] for key in prepare.PINNED},
            "script_sha256":"b"*64,"git_commit":commit,"datasets":prepare.datasets(),
            "inputs":[{"path":p,"sha256":harness if p in HARNESS_INPUTS else "d"*64} for p in prepare.files()]}


class ContractTests(unittest.TestCase):
    def test_listed_identity_is_accepted_and_everything_else_refused(self):
        self.assertEqual(prepare.contract(manifest_fixture())["evaluation_units"],209)
        prepare.contract(manifest_fixture("rehearsal-20261002a-real",prepare.REHEARSAL_COMMIT),rehearsal=True)
        for run in ("c4-v4-saved-evaluation-4","c4-v4-saved-evaluation-0044","../x","rehearsal-x",
                    "c4-v4-saved-evaluation-004 ","C4-v4-saved-evaluation-004",None,4):
            with self.subTest(run=run),self.assertRaisesRegex(ValueError,"unlisted evaluation identity"):
                prepare.contract(manifest_fixture(run))
        for run in ("c4-v4-saved-evaluation-004","rehearsal-","rehearsal-A","rehearsal-a/b","rehearsal-"+"a"*60):
            with self.subTest(rehearsal=run),self.assertRaisesRegex(ValueError,"unlisted evaluation identity"):
                prepare.contract(manifest_fixture(run,prepare.REHEARSAL_COMMIT),rehearsal=True)
        with self.assertRaisesRegex(ValueError,"null commit"):
            prepare.contract(manifest_fixture(commit=prepare.REHEARSAL_COMMIT))
        with self.assertRaisesRegex(ValueError,"null commit"):
            prepare.contract(manifest_fixture("rehearsal-x"),rehearsal=True)

    def test_scientific_envelope_is_pinned(self):
        changes={"seeds":[0,1],"resources":{"ram_mib":8192,"vram_mib":0,"disk_mib":2048},
                 "budget":{"max_seconds":7200,"max_usd":0,"hourly_usd":0},"stage_id":"C4-other",
                 "experiment_id":"other","execution_target":"mock","reviewed_script":"scripts/v4_study_worker.py",
                 "outputs":["outputs/results.json"],"metrics":["rgb_quality"],"cleanup_policy":"delete-after-verified",
                 "datasets":[]}
        for key,value in changes.items():
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"contract differs: "+key):
                prepare.contract({**manifest_fixture(),key:value})
        value=manifest_fixture()
        for inputs in (value["inputs"][1:],value["inputs"]+[{"path":"scripts/extra.py","sha256":"e"*64}],
                       list(reversed(value["inputs"]))):
            with self.assertRaisesRegex(ValueError,"input inventory differs"):
                prepare.contract({**value,"inputs":inputs})

    def test_manifest_has_exactly_the_runner_schema_fields_and_one_digest(self):
        value=manifest_fixture()
        self.assertEqual(set(value),{"schema_version","experiment_id","run_id","stage_id","task_id",
            "execution_target","reviewed_script","script_sha256","git_commit","seeds","datasets","inputs",
            "outputs","metrics","budget","resources","cleanup_policy"})
        # The official runner hashes with ensure_ascii=False; the worker with ASCII escaping.
        runner=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,
                                         allow_nan=False).encode()).hexdigest()
        self.assertEqual(object_sha(value),runner)
        accented=json.loads(json.dumps(value))
        accented["datasets"][0]["version"]+=" é"
        with patch.object(prepare,"datasets",return_value=accented["datasets"]):
            with self.assertRaisesRegex(ValueError,"ASCII"):
                prepare.contract(accented)

    def test_output_root_is_fixed_by_identity(self):
        value=manifest_fixture()
        self.assertEqual(prepare.run_root(value),prepare.BUILD+"/v4-recovery-runs/C4-v4-saved-evaluation/c4-v4-saved-evaluation-004")
        self.assertEqual(prepare.run_root({"run_id":"rehearsal-a-real"},rehearsal=True),prepare.BUILD+"/rehearsal/rehearsal-a-real")
        for run,rehearsal in (("rehearsal-a",False),("c4-v4-saved-evaluation-004",True),("../../x",False),("a/b",True)):
            with self.subTest(run=run),self.assertRaises(ValueError):
                prepare.run_root({"run_id":run},rehearsal=rehearsal)

    def test_core_and_harness_classification_is_exact(self):
        value=prepare.core()
        self.assertEqual(tuple(value["core_inputs"]),CORE_INPUTS)
        self.assertEqual(tuple(value["harness_inputs"]),HARNESS_INPUTS)
        self.assertEqual(prepare.files(),sorted(CORE_INPUTS+HARNESS_INPUTS))
        for name in prepare.files():
            self.assertTrue((prepare.ROOT/name).is_file(),name)
            self.assertFalse(Path(name).name.startswith("test_"),name)
        for name in CORE_INPUTS:
            self.assertFalse(prepare.harness_path(name,value),name)
        for name in HARNESS_INPUTS+("scripts/test_v4_evaluation_journal.py","scripts/rehearse_v4_saved_evaluation.py",
                                    "experiments/c4-v4-three-threat-recovery-v1/harness-correction-004.md",
                                    "experiments/c4-v4-three-threat-recovery-v1/evaluation-phase.md"):
            self.assertTrue(prepare.harness_path(name,value),name)
        for name in ("scripts/lpips.py","scripts/new_module.py","research/approval-policy.md","AGENTS.md",
                     "experiments/c4-v4-three-threat-recovery-v1/plan.md","scripts/sub/test_v4_x.py"):
            self.assertFalse(prepare.harness_path(name,value),name)

    def test_core_hash_ignores_harness_and_identity_but_not_science(self):
        base=prepare.core_sha256(manifest_fixture())
        self.assertEqual(base,prepare.core_sha256(manifest_fixture("c4-v4-saved-evaluation-005","f"*40,"9"*64)))
        self.assertEqual(base,prepare.core_sha256({**manifest_fixture(),"script_sha256":"0"*64}))
        for key,value in (("seeds",[0]),("resources",{"ram_mib":1,"vram_mib":0,"disk_mib":1}),
                          ("budget",{"max_seconds":1,"max_usd":0,"hourly_usd":0}),("datasets",[]),("metrics",["x"])):
            with self.subTest(key=key):
                self.assertNotEqual(base,prepare.core_sha256({**manifest_fixture(),key:value}))
        for name in CORE_INPUTS:
            changed=manifest_fixture()
            next(i for i in changed["inputs"] if i["path"]==name)["sha256"]="1"*64
            self.assertNotEqual(base,prepare.core_sha256(changed),name)
        with self.assertRaisesRegex(ValueError,"core plus harness"):
            prepare.core_sha256({**manifest_fixture(),"inputs":manifest_fixture()["inputs"][1:]})


class RerunCheckTests(unittest.TestCase):
    def attempt(self,stage,manifest,status="failed",complete=False,core=True,sealed=()):
        root=stage/manifest["run_id"]
        atomic_json(root/"execution-manifest.json",manifest)
        atomic_json(root/"manifest.json",{"status":status,"git_commit":manifest["git_commit"],
                    "execution_manifest_sha256":object_sha(manifest)})
        atomic_json(root/"outputs/runtime.json",{"scientific_core_sha256":prepare.core_sha256(manifest)} if core else {})
        atomic_json(root/"outputs/results.json",{"evaluation_phase_complete":complete,"sealed_units":list(sealed)})
        atomic_json(root/"outputs/failure.json",{"type":"OSError","phase":"VERIFYING_INPUTS"})
        return root

    def check(self,original,candidate,changed,definition=True):
        shown=unittest.mock.Mock(returncode=0 if definition else 1,stdout=json.dumps(prepare.core()))
        with patch.object(prepare,"build",return_value=candidate),\
             patch.object(prepare.subprocess,"run",return_value=shown),\
             patch.object(prepare.subprocess,"check_output",return_value="\n".join(changed)+"\n"):
            return prepare.check_rerun(original,candidate["run_id"])

    def test_harness_only_rerun_of_a_failed_attempt_is_eligible(self):
        with tempfile.TemporaryDirectory() as scratch:
            stage=Path(scratch)/"C4-v4-saved-evaluation"
            original=self.attempt(stage,manifest_fixture())
            candidate=manifest_fixture("c4-v4-saved-evaluation-005","b"*40,"9"*64)
            result=self.check(original,candidate,["scripts/v4_saved_evaluation_worker.py","scripts/test_v4_saved_evaluation.py"])
            self.assertTrue(result["eligible"],result["reasons"])
            self.assertEqual((result["rerun_ordinal"],result["approved_commit"]),(1,"a"*40))
            self.assertEqual(result["approved_core_sha256"],result["candidate_core_sha256"])
            self.assertEqual(result["attempts"][0]["failure_phase"],"VERIFYING_INPUTS")

    def test_every_disqualifying_condition_is_reported(self):
        cases={"core":"scientific core differs","path":"outside the approved harness list",
               "completed":"already completed","third":"already used","definition":"no scientific-core definition",
               "receipt":"does not bind","used":"run id already used","unrecorded":"does not record this scientific core"}
        for case,reason in cases.items():
            with self.subTest(case=case),tempfile.TemporaryDirectory() as scratch:
                stage=Path(scratch)/"C4-v4-saved-evaluation"
                original=self.attempt(stage,manifest_fixture(),complete=case=="completed",core=case!="unrecorded")
                candidate=manifest_fixture("c4-v4-saved-evaluation-007","b"*40,"9"*64)
                changed=["scripts/v4_saved_evaluation_worker.py"]
                if case=="core":
                    candidate["inputs"][0]["sha256"]="1"*64
                elif case=="path":
                    changed.append("scripts/lpips.py")
                elif case=="third":
                    self.attempt(stage,manifest_fixture("c4-v4-saved-evaluation-005","b"*40))
                    self.attempt(stage,manifest_fixture("c4-v4-saved-evaluation-006","c"*40))
                elif case=="receipt":
                    atomic_json(original/"manifest.json",{"status":"failed","git_commit":"a"*40,"execution_manifest_sha256":"0"*64})
                elif case=="used":
                    (stage/candidate["run_id"]).mkdir()
                result=self.check(original,candidate,changed,definition=case!="definition")
                self.assertFalse(result["eligible"])
                self.assertTrue(any(reason in r for r in result["reasons"]),result["reasons"])


class Tests(unittest.TestCase):
    @unittest.skipUnless(os.name=="nt","Windows process identity required")
    def test_final_host_dispatch_denies_missing_or_changed_preflight(self):
        for message in ("missing preflight","changed preflight"):
            with self.subTest(message=message),tempfile.TemporaryDirectory() as root:
                path=Path(root)/"intent.json"
                atomic_json(path,{"manifest_sha256":"c"*64,"artifacts":root})
                with patch("v4_durable_host.verify_request",return_value=({"run_id":"c4-v4-saved-evaluation-003"},{})),\
                     patch("v4_durable_host.child_handshake"),\
                     patch("v4_durable_host.verify_preflight",side_effect=ValueError(message)),\
                     patch("v4_durable_host.subprocess.run") as dispatch:
                    self.assertEqual(host(path),1)
                    dispatch.assert_not_called()
                receipt=json.loads(path.with_suffix(".completion.json").read_text())
                self.assertIsNone(receipt["exit_code"])
                self.assertEqual(receipt["host_error"]["message"],message)
    @unittest.skipUnless(os.name=="nt","actual Windows launch paths required")
    def test_fixed_offline_array_has_no_generation_worker(self):
        values=command("W:/a b/manifest.json","W:/a b/output",85980)
        execution=prepare.core()["execution"]
        self.assertIn("env",values)
        self.assertIn("-i",values)
        self.assertIn("HF_HUB_OFFLINE=1",values)
        self.assertIn("PYTHONHASHSEED=0",values)
        self.assertIn("85980s",values)
        self.assertIn("--kill-after=300s",values)
        for name,value in execution["env"].items():
            self.assertIn(name+"="+value,values)
        self.assertTrue(execution["env"]["PYTHONPYCACHEPREFIX"].startswith("/nonexistent/"))
        self.assertEqual(values[values.index("-B")-1],execution["interpreter"])
        self.assertTrue(any(v.endswith("/v4_saved_evaluation_worker.py") for v in values))
        self.assertFalse(any(v.endswith("/v4_study_worker.py") for v in values))
        self.assertNotIn("-c",values)
        self.assertEqual(values[-4:],["--manifest","/mnt/w/a b/manifest.json","--output-dir","/mnt/w/a b/output"])
        extra=command("W:/a b/manifest.json","W:/a b/output",40,Path("W:/a b/rehearse.py"),("--wsl-worker",))
        self.assertEqual(extra[extra.index("-B")+1:extra.index("-B")+3],["/mnt/w/a b/rehearse.py","--wsl-worker"])

    @unittest.skipUnless(os.name=="nt","actual Windows launch paths required")
    def test_launch_is_exclusive_detached_from_stdin_and_bounded(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root)/"logs").mkdir()
            with patch("run_v4_saved_evaluation.subprocess.run") as started:
                started.return_value.returncode=7
                self.assertEqual(launch(Path(root)/"m.json",root,100),7)
                options=started.call_args.kwargs
                self.assertIs(options["stdin"],subprocess.DEVNULL)
                self.assertIs(options["stderr"],subprocess.STDOUT)
                self.assertEqual(options["timeout"],100+LAUNCH_MARGIN)
                with self.assertRaises(FileExistsError):
                    launch(Path(root)/"m.json",root,100)

    def test_timeouts_leave_room_to_finalise_inside_the_runner_budget(self):
        budget=prepare.core()["budget"]["max_seconds"]
        worker_deadline=budget-WORKER_MARGIN
        term=budget-TERM_MARGIN
        self.assertGreaterEqual(term-worker_deadline,480)
        self.assertLess(term+KILL_AFTER,term+LAUNCH_MARGIN)
        self.assertLess(term+LAUNCH_MARGIN,budget)

    def test_entrypoint_accepts_exactly_the_runner_argument_shape(self):
        with tempfile.TemporaryDirectory() as scratch:
            value=manifest_fixture()
            with patch.object(prepare,"BUILD",Path(scratch).as_posix()):
                output=Path(prepare.run_root(value))
                output.mkdir(parents=True)
                path=output/"execution-manifest.json"
                path.write_text(json.dumps(value))
                # compute.py passes str(Path.resolve()) for both arguments.
                arguments=["--manifest",str(path.resolve()),"--output-dir",str(output.resolve())]
                with patch("run_v4_saved_evaluation.launch",return_value=0) as launched:
                    self.assertEqual(main(arguments),0)
                    self.assertEqual(launched.call_args.args[2],value["budget"]["max_seconds"]-TERM_MARGIN)
                elsewhere=Path(scratch)/"elsewhere"
                elsewhere.mkdir()
                with patch("run_v4_saved_evaluation.launch") as launched:
                    with self.assertRaisesRegex(ValueError,"output root"):
                        main(["--manifest",str(path),"--output-dir",str(elsewhere)])
                    path.write_text(json.dumps({**value,"run_id":"rehearsal-x"}))
                    with self.assertRaisesRegex(ValueError,"unlisted evaluation identity"):
                        main(arguments)
                    launched.assert_not_called()

    @unittest.skipUnless(os.name=="nt","real hidden Windows process fixture required")
    def test_child_survives_termination_of_its_initiating_process(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            initiator=subprocess.Popen([sys.executable,"-B",__file__,"--initiator",str(root)],
                                       stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            owner=root/"intent.owner.json"
            starter=root/"starter.json"
            deadline=time.monotonic()+10
            while (not owner.exists() or not starter.exists() or not (root/"started.json").exists()) and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertTrue(owner.exists())
            identity=json.loads(owner.read_text())
            self.assertEqual(creation_time(identity["pid"]),identity["creation_time"])
            actual_starter=json.loads(starter.read_text())
            self.assertEqual(creation_time(actual_starter["pid"]),actual_starter["creation_time"])
            # Terminate the exact self-reported harmless interpreter, not Popen's venv launcher.
            os.kill(actual_starter["pid"],signal.SIGTERM)
            initiator.wait(timeout=10)
            self.assertFalse(identity_alive(actual_starter["pid"],actual_starter["creation_time"]))
            self.assertTrue(identity_alive(identity["pid"],identity["creation_time"]))
            progress=root/"progress.json"
            before=json.loads(progress.read_text())["step"] if progress.exists() else -1
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if progress.exists() and json.loads(progress.read_text())["step"] > before:
                    break
                time.sleep(.05)
            self.assertGreater(json.loads(progress.read_text())["step"],before)
            self.assertTrue(identity_alive(identity["pid"],identity["creation_time"]))
            done=root/"done.json"
            deadline=time.monotonic()+10
            while not done.exists() and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertTrue(done.exists(),"detached harmless child died with its initiating process")
            completed=json.loads(done.read_text())
            self.assertTrue(completed["model_free"] and completed["completed"])
            self.assertEqual((completed["pid"],completed["creation_time"]),(identity["pid"],identity["creation_time"]))
            self.assertTrue(completed["observed_initiator_exit"])
            # Give the fixture time to exit and release its log before temp cleanup.
            time.sleep(.2)

    @unittest.skipUnless(os.name=="nt","actual Windows identity API required")
    def test_process_snapshot_matches_actual_self(self):
        observed=process_identity(os.getpid())
        self.assertEqual(observed["parent_pid"],os.getppid())
        self.assertEqual(observed["creation_time"],creation_time(os.getpid()))

    def test_missing_ack_never_dispatches(self):
        with tempfile.TemporaryDirectory() as scratch:
            path=Path(scratch)/"intent.json"
            request={"manifest_sha256":"c"*64,"initiator_pid":10,"initiator_creation_time":"20"}
            atomic_json(path,request)
            identity={"pid":30,"creation_time":"40","parent_pid":50,"parent_creation_time":"60"}
            with patch("v4_durable_host.verify_request",return_value=({"run_id":"c4-v4-recovery-host-check-003"},{})),\
                 patch("v4_durable_host.process_identity",return_value=identity),\
                 patch("v4_durable_host.wait_json",side_effect=TimeoutError("missing ACK")),\
                 patch("v4_durable_host.creation_time",return_value="40"),\
                 patch("v4_durable_host.subprocess.run") as dispatch:
                self.assertEqual(host(path),1)
                dispatch.assert_not_called()
            self.assertIsNone(json.loads(path.with_suffix(".completion.json").read_text())["exit_code"])

    def test_mismatched_ack_rejected(self):
        with tempfile.TemporaryDirectory() as scratch:
            path=Path(scratch)/"intent.json"
            request={"initiator_pid":10,"initiator_creation_time":"20"}
            identity={"pid":30,"creation_time":"40","parent_pid":50,"parent_creation_time":"60"}
            ready={**identity,"request_sha256":object_sha(request)}
            good=ack_value(request,ready,{"pid":50,"creation_time":"60"})
            for field in ("request_sha256","ready_sha256","initiator_creation_time"):
                bad={**good,field:"wrong"}
                with self.subTest(field=field),patch("v4_durable_host.process_identity",return_value=identity),\
                     patch("v4_durable_host.wait_json",return_value=bad):
                    with self.assertRaisesRegex(ValueError,"acknowledgement binding"):
                        child_handshake(path,request)
                self.assertFalse(path.with_suffix(".accepted.json").exists())

    def test_wrong_lineage_or_reused_pid_rejected(self):
        request={"manifest_sha256":"c"*64}
        identity={"pid":30,"creation_time":"40","parent_pid":50,"parent_creation_time":"20"}
        ready={**identity,"request_sha256":object_sha(request)}
        for launcher in ({"pid":99,"creation_time":"20"},{"pid":50,"creation_time":"21"}):
            with patch("v4_durable_host.process_identity",return_value=identity):
                with self.assertRaisesRegex(ValueError,"lineage"):
                    validate_ready(request,ready,launcher)
        with patch("v4_durable_host.process_identity",return_value={**identity,"creation_time":"41"}):
            with self.assertRaisesRegex(ValueError,"live identity"):
                validate_ready(request,ready,{"pid":50,"creation_time":"20"})

    def test_access_denial_is_not_exit(self):
        with patch("v4_durable_host.creation_time",side_effect=OSError(5,"denied")):
            with self.assertRaises(OSError):
                identity_alive(10,"20")
        with patch("v4_durable_host.creation_time",side_effect=OSError(87,"absent")):
            self.assertFalse(identity_alive(10,"20"))

    def test_handshake_timeout_is_bounded(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(TimeoutError):
                wait_json(Path(root)/"absent.json",.05)

    def preflight_fixture(self, artifacts):
        expected={"git_commit":"fixture-commit"}
        request={"manifest_sha256":object_sha(expected),"initiator_pid":10,"initiator_creation_time":"20"}
        identity={"pid":30,"creation_time":"40","parent_pid":50,"parent_creation_time":"25"}
        ready={**identity,"request_sha256":object_sha(request)}
        launcher={"pid":50,"creation_time":"25"}
        ack=ack_value(request,ready,launcher)
        intent=artifacts/"host-intents"/(PREFLIGHT_RUN+".json")
        atomic_json(intent,request)
        atomic_json(intent.with_suffix(".ready.json"),ready)
        atomic_json(intent.with_suffix(".owner.json"),{**ready,"launcher":launcher,"manifest_sha256":object_sha(expected)})
        atomic_json(intent.with_suffix(".ack.json"),ack)
        atomic_json(intent.with_suffix(".accepted.json"),{"request_sha256":object_sha(request),
                    "ready_sha256":object_sha(ready),"ack_sha256":object_sha(ack)})
        atomic_json(intent.with_suffix(".completion.json"),{"host_pid":30,"host_creation_time":"40",
                    "request_sha256":object_sha(request),"manifest_sha256":object_sha(expected),"exit_code":0,"host_error":None})
        root=artifacts/"C4-v4-recovery-host-preflight"/PREFLIGHT_RUN
        atomic_json(root/"outputs/fixture.json",{"model_free":True,"step":5,"completed":True})
        survival={"request_sha256":object_sha(request),"host_identity":{"pid":30,"creation_time":"40"},
                  "observations":[{"step":s,"monotonic_ns":s+100,"host_alive":True,
                                   "initiator_alive":False,"official_status":"running"} for s in range(6)]}
        atomic_json(root/"outputs/survival.json",survival)
        receipt={"status":"completed","exit_status":0,"git_commit":"fixture-commit","git_dirty":False,
                 "execution_manifest_sha256":object_sha(expected),"output_artifacts":[
                     {"path":p,"sha256":file_sha(root/p)} for p in ("outputs/fixture.json","outputs/survival.json")]}
        atomic_json(root/"manifest.json",receipt)
        return expected,root,intent,survival,receipt

    def test_preflight_requires_actual_progress_and_exact_identity_chain(self):
        for mutation in ("none","owner_pid","ack","accepted","progress","one_observation","output_hash"):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as scratch:
                artifacts=Path(scratch)
                expected,root,intent,survival,receipt=self.preflight_fixture(artifacts)
                if mutation in ("owner_pid","ack","accepted"):
                    suffix={"owner_pid":".owner.json","ack":".ack.json","accepted":".accepted.json"}[mutation]
                    path=intent.with_suffix(suffix)
                    value=json.loads(path.read_text())
                    value["pid" if mutation=="owner_pid" else "request_sha256"]="wrong"
                    atomic_json(path,value)
                elif mutation in ("progress","one_observation","output_hash"):
                    if mutation=="progress":
                        for o in survival["observations"]:
                            o["initiator_alive"]=True
                    else:
                        survival["observations"]=survival["observations"][:1]
                    atomic_json(root/"outputs/survival.json",survival)
                    if mutation!="output_hash":
                        receipt["output_artifacts"][1]["sha256"]=file_sha(root/"outputs/survival.json")
                        atomic_json(root/"manifest.json",receipt)
                with patch("prepare_v4_saved_evaluation.build_fixture",return_value=expected),\
                     patch("v4_durable_host.identity_alive",return_value=False):
                    if mutation=="none":
                        self.assertEqual(verify_preflight(artifacts,expected),object_sha(expected))
                    else:
                        with self.assertRaises(ValueError):
                            verify_preflight(artifacts,expected)

    def test_no_generation_import_in_evaluation_adapter_or_worker(self):
        directory=Path(__file__).resolve().parent
        for name in ("v4_saved_evaluation_adapter.py","v4_saved_evaluation_worker.py","rehearse_v4_saved_evaluation.py"):
            source=(directory/name).read_text()
            self.assertNotIn("load_regenerator",source)
            self.assertNotIn("vae_round_trip",source)
            self.assertNotIn("codec.embed",source)
            compile(source,str(directory/name),"exec")

    def test_command_line_worker_can_never_rehearse(self):
        source=(Path(__file__).resolve().parent/"v4_saved_evaluation_worker.py").read_text()
        entry=source[source.index('if __name__ == "__main__":'):]
        self.assertIn("run(args.manifest,args.output_dir)",entry)
        self.assertNotIn("rehearsal",entry)

    def test_synthetic_parent_replays_the_committed_schedule_and_is_marked(self):
        import struct
        import rehearse_v4_saved_evaluation as rehearse
        with tempfile.TemporaryDirectory() as scratch,\
             patch.object(rehearse,"texture",side_effect=lambda seed,base=None,spread=0:bytearray(bytes([seed*40]))*(512*512*3)):
            root=Path(scratch)
            rehearse.mirror(root)   # raises unless the replay equals schedule.json
            lock=json.loads((root/"parent-input-lock.json").read_text())
            parent=Path(lock["parent_root"])
            self.assertTrue(lock["rehearsal_synthetic"] and parent.resolve().is_relative_to(root.resolve()))
            for item in lock["artifacts"]:
                self.assertEqual(file_sha(parent/item["path"]),item["sha256"])
            snapshot=json.loads((parent/"outputs/results.json").read_text())
            self.assertTrue(snapshot["rehearsal_synthetic"])
            self.assertEqual(len(snapshot["rows"]),537)
            self.assertTrue(all(row["synthetic"] for row in snapshot["rows"]))
            saved=[row for row in snapshot["rows"] if row.get("image")]
            self.assertEqual(len(saved),401)
            self.assertTrue(all(row["image"]["synthetic"] for row in saved))
            self.assertEqual({row["image"]["path"] for row in saved},{"outputs/images/a.png","outputs/images/b.png","outputs/images/c.png"})
            header=(parent/"outputs/images/a.png").read_bytes()[:26]
            self.assertEqual(header[:8],b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">IIBB",header[16:26]),(512,512,8,2))
            _,units=rehearse.evaluation_units()
            self.assertEqual((len(units),sum(len(u["row_ids"]) for u in units)),(209,483))
            chosen=rehearse.representative(units)
            self.assertEqual(len(set(chosen)),6)
            self.assertEqual(rehearse.arguments("fake",chosen[:2],0.2)[-3:],(",".join(chosen[:2]),"--sleep","0.2"))


if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--initiator":
        root=Path(sys.argv[2])
        request={"initiator_pid":os.getpid(),"initiator_creation_time":creation_time(os.getpid()),
                 "manifest_sha256":"d"*64,"launch_nonce":root.name}
        atomic_json(root/"starter.json",{"pid":os.getpid(),"creation_time":creation_time(os.getpid())})
        atomic_json(root/"intent.json",request)
        pid,created=detach([sys.executable,"-B",__file__,"--harmless-child",str(root)],root/"child.log")
        parent_handshake(root/"intent.json",request,{"pid":pid,"creation_time":created})
        atomic_json(root/"started.json",{"completed_handshake":True})
        time.sleep(20)
    elif len(sys.argv)>1 and sys.argv[1]=="--harmless-child":
        root=Path(sys.argv[2])
        request=json.loads((root/"intent.json").read_text())
        ready=child_handshake(root/"intent.json",request)
        exited=False
        for step in range(10):
            exited=exited or not identity_alive(request["initiator_pid"],request["initiator_creation_time"])
            atomic_json(root/"progress.json",{"step":step,"pid":os.getpid()})
            time.sleep(.4)
        atomic_json(root/"done.json",{"model_free":True,"completed":True,"pid":os.getpid(),
                    "creation_time":ready["creation_time"],"observed_initiator_exit":exited})
    else:
        unittest.main()
