"""CPU mechanics fixtures for a not-yet-executed real-model audit runner."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from test_m1_source_initialization import TinyVAE,fixture,seed
import m1_source_initialization as adapter
import m1_source_initialization_audit as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.main=Path(self.folder.name)
        self.root=self.main/".thesis-build/dev-runs";self.root.mkdir(parents=True)
        self.patch=mock.patch.object(audit,"MAIN",self.main);self.patch.start()
        self.identity={"source_id":1675,"source_rgb8_sha256":"b"*64,"model_sha256":"a"*64,
                       "scientific_core_sha256":"c"*64,"phase_seed":0}

    def tearDown(self):
        self.patch.stop();self.folder.cleanup()

    def record(self,stage,pid,folder):
        canonical=folder/"source.png";canonical.write_bytes(b"CPU receipt fixture, not a source image")
        return {"schema":audit.VERSION,"data_split":"development","stage":stage,"outcome":"completed",
            "audit_config":audit.config(),"process_id":pid,"scientific_files":{"tiny":"fixture"},
            "scientific_core_sha256":"c"*64,"deterministic_execution":{"fixture":True},
            "environment":{"fixture":"cpu"},"device_identity":{"fixture":"cpu"},"assets":[],
            "identity":self.identity,"source":{"raw_sha256":"d"*64,"rgb8_sha256":"b"*64,
                "native_shape":[3,4,3],"canonical_png":audit.receipt(canonical)},"checkpoints":[]}

    def fixture_runs(self):
        folders=[self.root/name for name in ("r1","r2a","r2b")]
        for p in folders:p.mkdir()
        records=[self.record(stage,pid,path) for stage,pid,path in zip(audit.STAGES[:3],(1,2,3),folders)]
        def saver(folder,record):
            def callback(s):
                if s.step%10==0:
                    path=folder/f"state{s.step:03d}.pt";audit.save_payload(path,s.state_dict())
                    record["checkpoints"].append({"step":s.step,**audit.receipt(path)})
            return callback
        seed();literal=audit.LiteralReference(fixture(),TinyVAE(True),self.identity)
        literal.advance(saver(folders[0],records[0]))
        seed();prefix=adapter.ReconstructionSession(fixture(),TinyVAE(True),self.identity)
        save=saver(folders[1],records[1]);save(prefix);prefix.advance(100,on_update=save)
        audit.write(folders[1]/"run.json",records[1])
        saved=adapter.load_checkpoint(records[1]["checkpoints"][-1]["path"])
        torch.rand(20)
        resume=adapter.ReconstructionSession(fixture(),TinyVAE(True),self.identity,resume=saved)
        resume.advance(200,on_update=saver(folders[2],records[2]))
        records[2]["resume_from"]=audit.receipt(folders[1]/"run.json")
        records[2]["resume_checkpoint"]=records[1]["checkpoints"][-1]
        for path,r in zip(folders,records):audit.write(path/"run.json",r)
        return folders,records

    def test_literal_adapter_actual_disk_split_exact_all21_states(self):
        paths,records=self.fixture_runs()
        result,entries=audit.compare_runs(*paths)
        self.assertTrue(result["passed"])
        self.assertEqual([v["step"] for v in result["comparisons"]],list(range(0,201,10)))
        self.assertTrue(all(v["exact"] for v in result["comparisons"]))
        self.assertFalse(result["watermark_success_claim"])

    def test_missing_state_corrupt_hash_and_wrong_resume_rejected(self):
        paths,records=self.fixture_runs()
        cp=records[2]["checkpoints"][-1]
        path=Path(cp["path"]);original=path.read_bytes();path.write_bytes(original+b"corrupt")
        with self.assertRaisesRegex(ValueError,"changed"):
            audit.compare_runs(*paths)
        path.write_bytes(original)
        bad=copy.deepcopy(records[2]);bad["resume_from"]=audit.receipt(paths[0]/"run.json")
        audit.write(paths[2]/"run.json",bad)
        with self.assertRaisesRegex(ValueError,"independent adapter prefix"):
            audit.compare_runs(*paths)
        bad=copy.deepcopy(records[2]);bad["checkpoints"].pop()
        audit.write(paths[2]/"run.json",bad)
        with self.assertRaisesRegex(ValueError,"inventory"):
            audit.compare_runs(*paths)

    def test_parity_failure_remains_failure_without_tolerance(self):
        paths,records=self.fixture_runs()
        cp=records[2]["checkpoints"][-1]
        state=adapter.load_checkpoint(cp["path"])
        state["z"][0,0,0,0]+=1e-5
        state["integrity_sha256"]=adapter.digest({k:v for k,v in state.items() if k!="integrity_sha256"})
        Path(cp["path"]).unlink();audit.save_payload(cp["path"],state)
        records[2]["checkpoints"][-1]={"step":200,**audit.receipt(cp["path"])}
        audit.write(paths[2]/"run.json",records[2])
        result,_=audit.compare_runs(*paths)
        self.assertFalse(result["passed"])
        self.assertFalse(result["comparisons"][-1]["fields"]["z"])
        with self.assertRaisesRegex(ValueError,"Passing"):
            audit.export_bridge(self.root,{"comparison":result},[])

    def test_no_independence_and_runtime_differences_rejected(self):
        paths,records=self.fixture_runs()
        bad=copy.deepcopy(records[1]);bad["process_id"]=1;audit.write(paths[1]/"run.json",bad)
        with self.assertRaisesRegex(ValueError,"independent"):
            audit.compare_runs(*paths)
        audit.write(paths[1]/"run.json",records[1])
        records[2]["environment"]["fixture"]="different"
        audit.write(paths[2]/"run.json",records[2])
        with self.assertRaisesRegex(ValueError,"environment"):
            audit.compare_runs(*paths)

    def test_reject_external_dependencies_before_read_and_no_overwrite(self):
        with self.assertRaisesRegex(ValueError,"root"):
            audit.load_run(self.main/"external","literal")
        with self.assertRaisesRegex(ValueError,"root"):
            audit.verify_audit(self.main/"external")
        with self.assertRaisesRegex(ValueError,"root"):
            audit.load_development_bridge(self.main/"external",1675,"b"*64)
        path=self.root/"checkpoint.pt";path.write_bytes(b"retained")
        with self.assertRaises(FileExistsError):audit.save_payload(path,{})
        self.assertEqual(path.read_bytes(),b"retained")

    def test_successful_bridge_format_guarded_import_and_dependency_corruption(self):
        # Shape-valid synthetic receipt for loader mechanics, not model evidence.
        paths,records=self.fixture_runs()
        for index in (0,2):
            cp=records[index]["checkpoints"][-1]
            state=adapter.load_checkpoint(cp["path"])
            state["z"]=torch.zeros(1,4,64,64);state["initial"]=torch.zeros_like(state["z"])
            for key in ("exp_avg","exp_avg_sq"):
                state["optimizer"]["state"][0][key]=torch.zeros_like(state["z"])
            state["observations"][200]["rgb8"]=torch.full((512,512,3),127,dtype=torch.uint8)
            state["integrity_sha256"]=adapter.digest({k:v for k,v in state.items() if k!="integrity_sha256"})
            Path(cp["path"]).unlink();audit.save_payload(cp["path"],state)
            records[index]["checkpoints"][-1]={"step":200,**audit.receipt(cp["path"])}
            audit.write(paths[index]/"run.json",records[index])
        result,entries=audit.compare_runs(*paths)
        self.assertTrue(result["passed"])
        output=self.root/"comparison";output.mkdir()
        record={"schema":audit.VERSION,"stage":"compare","data_split":"development","outcome":"completed",
                "comparison":result,"input_runs":[audit.receipt(p/"run.json") for p in paths],"config":{},"commit":"fixture"}
        audit.export_bridge(output,record,entries);audit.write(output/"run.json",record)
        bridge=record["u0_bridge"]
        payload=adapter.load_checkpoint(bridge["latent"]["path"])
        self.assertEqual(set(payload),{"z","step","latent_units"})
        self.assertEqual(payload["step"],200)
        self.assertEqual(payload["z"].shape,(1,4,64,64))
        from scripts import m1_dual_latent as original
        (self.main/"research").mkdir()
        (self.main/"research/a6-candidate-model-assets.json").write_text(json.dumps({"files":[]}))
        with mock.patch.object(audit,"ROOT",self.main), \
                mock.patch.object(original,"require_committed",return_value=records[0]["scientific_files"]), \
                mock.patch.object(torch.cuda,"is_initialized",return_value=True), \
                mock.patch.object(torch.cuda,"current_device",return_value=0), \
                mock.patch.object(adapter,"_runtime",return_value=state["runtime"]):
            u0,provenance=audit.load_development_bridge(output,1675,"b"*64)
            self.assertTrue(torch.equal(u0,payload["z"]))
            self.assertEqual(provenance["embedding_optimizer"],"fresh independent Adam")
            with self.assertRaisesRegex(ValueError,"identity"):
                audit.load_development_bridge(output,1675,"e"*64)
            Path(records[2]["checkpoints"][-1]["path"]).write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError,"changed"):
                audit.load_development_bridge(output,1675,"b"*64)


if __name__=="__main__":unittest.main()
