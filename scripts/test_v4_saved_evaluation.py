"""Model-free saved-evaluation boundary and real Windows detachment tests."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from run_v4_saved_evaluation import command
from v4_durable_host import detach, creation_time, host
from v4_evaluation_journal import atomic_json


class Tests(unittest.TestCase):
    @unittest.skipUnless(os.name=="nt","Windows process identity required")
    def test_final_host_dispatch_denies_missing_or_changed_preflight(self):
        for message in ("missing preflight","changed preflight"):
            with self.subTest(message=message),tempfile.TemporaryDirectory() as root:
                path=Path(root)/"intent.json"
                atomic_json(path,{"manifest_sha256":"c"*64,"artifacts":root})
                with patch("v4_durable_host.verify_request",return_value=({"run_id":"c4-v4-saved-evaluation-001"},{})),\
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
            owner=root/"owner.json"
            deadline=time.monotonic()+10
            while not owner.exists() and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertTrue(owner.exists())
            identity=json.loads(owner.read_text())
            self.assertEqual(creation_time(identity["pid"]),identity["creation_time"])
            initiator.terminate()
            initiator.wait(timeout=10)
            done=root/"done.json"
            deadline=time.monotonic()+10
            while not done.exists() and time.monotonic()<deadline:
                time.sleep(.05)
            self.assertTrue(done.exists(),"detached harmless child died with its initiating process")
            self.assertEqual(json.loads(done.read_text()),{"model_free":True,"completed":True})
            # Give the fixture time to exit and release its log before temp cleanup.
            time.sleep(.2)

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
        pid,created=detach([sys.executable,"-B",__file__,"--harmless-child",str(root)],root/"child.log")
        atomic_json(root/"owner.json",{"pid":pid,"creation_time":created})
        time.sleep(20)
    elif len(sys.argv)>1 and sys.argv[1]=="--harmless-child":
        root=Path(sys.argv[2])
        time.sleep(2)
        atomic_json(root/"done.json",{"model_free":True,"completed":True})
    else:
        unittest.main()
