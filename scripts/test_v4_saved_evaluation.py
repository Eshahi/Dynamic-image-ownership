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
from run_v4_saved_evaluation import command
from v4_durable_host import (detach, creation_time, host, process_identity, child_handshake,
                             parent_handshake, validate_ready, ack_value, identity_alive, wait_json)
from v4_durable_host import verify_preflight, PREFLIGHT_RUN
from v4_evaluation_journal import atomic_json, object_sha, file_sha


class Tests(unittest.TestCase):
    @unittest.skipUnless(os.name=="nt","Windows process identity required")
    def test_final_host_dispatch_denies_missing_or_changed_preflight(self):
        for message in ("missing preflight","changed preflight"):
            with self.subTest(message=message),tempfile.TemporaryDirectory() as root:
                path=Path(root)/"intent.json"
                atomic_json(path,{"manifest_sha256":"c"*64,"artifacts":root})
                with patch("v4_durable_host.verify_request",return_value=({"run_id":"c4-v4-saved-evaluation-002"},{})),\
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
        values=command("W:/a b/manifest.json","W:/a b/output")
        self.assertIn("env",values)
        self.assertIn("-i",values)
        self.assertIn("HF_HUB_OFFLINE=1",values)
        self.assertIn("PYTHONHASHSEED=0",values)
        self.assertIn("86200s",values)
        self.assertTrue(any(v.endswith("/v4_saved_evaluation_worker.py") for v in values))
        self.assertFalse(any(v.endswith("/v4_study_worker.py") for v in values))
        self.assertNotIn("-c",values)

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
            with patch("v4_durable_host.verify_request",return_value=({"run_id":"c4-v4-recovery-host-check-002"},{})),\
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
        for name in ("v4_saved_evaluation_adapter.py","v4_saved_evaluation_worker.py"):
            source=(directory/name).read_text()
            self.assertNotIn("load_regenerator",source)
            self.assertNotIn("vae_round_trip",source)
            self.assertNotIn("codec.embed",source)
            compile(source,str(directory/name),"exec")


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
