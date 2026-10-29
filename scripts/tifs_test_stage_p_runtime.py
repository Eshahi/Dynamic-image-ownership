"""Runtime routing tests on opaque bytes/pure mocks; no image or ML execution."""
import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import tifs_common as common
import tifs_stage_p as p
import tifs_stage_s as stage
import tifs_stage_s_read as reader


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)
        self.choice=Path("nonexistent-runtime-test-choice.json")
        self.receipt=dict(schema="tifs-round3-user-choice-v1",decision="approve",recorded_by="Claude",
            config_sha256=common.sha256_file(p.BASE),gate_profile="round1",stage_p="run",k3_optimization="excluded",
            before_server_outputs=True,user_decision_reference="TEST FIXTURE ONLY",max_instance_hours=24)
        original_load,original_sha=common.load_json,common.sha256_file
        self.loader=patch.object(common,"load_json",side_effect=lambda path:self.receipt if Path(path)==self.choice else original_load(path))
        self.hasher=patch.object(common,"sha256_file",side_effect=lambda path:"e"*64 if Path(path)==self.choice else original_sha(path))
        self.loader.start();self.hasher.start()
        self.config=p.materialize(p.BASE,p.HERE/"source-manifest.json",self.choice,"f6-noise-p52")
        out=self.root/"tune/f6-noise-p52"
        self.args=SimpleNamespace(out=out,config=out/"config.json",user_choice=self.choice,selection=None,
            rehearsal=False,stage="prepare",stage_p_count=4,stage_p_calibration=False,assets=self.root/"assets")
        common.atomic_json(self.args.config,self.config)

    def tearDown(self):
        self.hasher.stop();self.loader.stop();self.temporary.cleanup()

    def test_bound_choice_and_immutable_config(self):
        result=stage.execution_config(self.args)
        self.assertEqual(result,self.config)
        self.assertEqual(len(stage.active_source_ids(self.args)),4)
        self.args.user_choice=None
        with self.assertRaises(ValueError):stage.execution_config(self.args)
        self.args.user_choice=self.choice
        changed=copy.deepcopy(self.config);changed["writer"]["psnr_db"]=38
        common.atomic_json(self.args.config,changed)
        with self.assertRaises(ValueError):stage.execution_config(self.args)

    def test_flags_and_prohibited_stage(self):
        for key,value in (("rehearsal",True),("stage","threats"),("stage","secondary"),("stage_p_count",None)):
            args=copy.copy(self.args);setattr(args,key,value)
            with self.assertRaises(ValueError):stage.execution_config(args)
        self.args.stage_p_count=2
        with self.assertRaises(ValueError):stage.execution_config(self.args)
        self.args.stage_p_calibration=True
        self.assertEqual(len(stage.active_source_ids(self.args,stage.execution_config(self.args))),2)

    def test_prefix_enlargement_requires_prior_promotion(self):
        self.args.stage_p_count=8
        with self.assertRaises(FileNotFoundError):stage.execution_config(self.args)
        meta=self.config["stage_p"]
        binding={key:meta[key] for key in ("base_config_sha256","source_manifest_sha256","protocol_sha256","search_config_sha256","user_choice_sha256","gate_profile")}
        record=dict(status="ADVANCE",survivors=["f6-x0-p52"],**binding)
        common.atomic_json(self.root/"selection/rung-4.json",record)
        with self.assertRaisesRegex(ValueError,"eliminated"):stage.execution_config(self.args)
        record["survivors"].append("f6-noise-p52")
        common.atomic_json(self.root/"selection/rung-4.json",record)
        self.assertEqual(stage.execution_config(self.args),self.config)

    def test_prepared_and_reader_only_active_prefix(self):
        stage.execution_config(self.args)
        rows=self.config["stage_p"]["sources"]
        common.atomic_json(self.args.out/"prepared.json",dict(sources={str(r["source_id"]):r for r in rows},
            donors=[str(r["source_id"]) for r in rows],targets=[],pairs=[]))
        result,donors,targets=stage.prepared(self.args)
        self.assertEqual(len(donors),4)
        self.assertEqual(len(common.load_json(self.args.out/"prepared.json")["donors"]),16)
        self.assertEqual(targets,[])
        clean=common.Journal(self.args.out/"clean.jsonl")
        for row in rows:
            clean.append(dict(id="clean:"+str(row["source_id"])+":unmarked",status="ok",source=str(row["source_id"])))
        # A stray threat journal is never routed into the Stage P reader.
        threats=common.Journal(self.args.out/"threats.jsonl")
        threats.append(dict(id="forbidden",source=donors[0],status="ok"))
        self.assertEqual(len(reader.items(self.args)),4)
        self.assertEqual(len(stage.expected_ids(self.config,result)["native"]),96)
        self.assertEqual(set(stage.expected_ids(self.config,result)),{"clean","native"})

    def test_prepare_seals_full_metadata_opens_only_prefix_without_clip(self):
        # The fixture bytes have no image format; rt.load_rgb is a pure mock.
        manifest=copy.deepcopy(p.load_manifest(p.HERE/"source-manifest.json"))
        pixel_bytes={}
        for index,row in enumerate(manifest["tune_sources"]):
            source=self.root/"opaque"/(str(index)+".bin")
            source.parent.mkdir(exist_ok=True)
            source.write_bytes(("opaque source "+str(index)).encode())
            pixels=("opaque pixels "+str(index)).encode()
            pixel_bytes[str(source)]=pixels
            row.update(canonical_path=str(source),canonical_png_sha256=common.sha256_file(source),rgb8_sha256=hashlib.sha256(pixels).hexdigest())
        config=copy.deepcopy(self.config);config["stage_p"]["sources"]=manifest["tune_sources"]
        self.args._execution_config=config
        rt=SimpleNamespace(load_rgb=Mock(side_effect=lambda path:SimpleNamespace(tobytes=lambda:pixel_bytes[str(path)])))
        budget=SimpleNamespace(require=Mock())
        with patch.object(p,"load_manifest",return_value=manifest):
            stage.prepare_stage_p(self.args,config,budget,rt)
            prepared=common.load_json(self.args.out/"prepared.json")
            self.assertEqual(len(prepared["sources"]),16)
            self.assertEqual(prepared["targets"],[])
            self.assertEqual(rt.load_rgb.call_count,4)
            identity=copy.deepcopy(prepared)
            self.args.stage_p_count=8
            stage.prepare_stage_p(self.args,config,budget,rt)
            self.assertEqual(rt.load_rgb.call_count,12)
            self.assertEqual(common.load_json(self.args.out/"prepared.json"),identity)

    def test_stage_s_flags_cannot_invoke_stage_p_routing(self):
        self.args.config=p.BASE;self.args.user_choice=None
        with self.assertRaisesRegex(ValueError,"source flags"):stage.execution_config(self.args)


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.root=Path(self.temporary.name)
        total=48*1024**3
        self.now=1767225700
        self.meta=dict(base_config_sha256="base",source_manifest_sha256="manifest",user_choice_sha256="choice")
        self.config=dict(stage_p=self.meta,budget=dict(retrieval_reserve_seconds=3600))
        self.args=SimpleNamespace(out=self.root/"tune/f6-noise-p52",_execution_config=self.config,stage_p_calibration=False,rehearsal=False)
        self.identity=dict(config_sha256="trial",profiles={"profile":"fixed"},code={"code":"fixed"},packages={"package":"fixed"},
            device=dict(name="fixture",capability=[8,0],total_bytes=total),instance_start_utc="2026-01-01T00:00:00+00:00",max_hours=24)
        calibration={}
        for trial in ("retained-f5","f6-noise-p52","f6-x0-p52"):
            path=self.root/"tune"/trial/"identity.json"
            common.atomic_json(path,dict(self.identity,config_sha256=trial))
            calibration[trial]=common.sha256_file(path)
        self.forecast=dict(schema="tifs-stage-p-forecast-v1",status="GO",stage_p_root=str(self.root),config_sha256="base",source_manifest_sha256="manifest",
            user_choice_sha256="choice",identity_profiles=self.identity["profiles"],identity_code=self.identity["code"],identity_packages=self.identity["packages"],
            device=self.identity["device"],instance_start_utc=self.identity["instance_start_utc"],ceiling_seconds=86400,
            operation_bounds_seconds={"prepare":5},calibration_identity_sha256=calibration,forecast_seconds=36000,
            capacity=dict(status="GO",device_total_bytes=total,peak_device_bytes=30*1024**3,gpu_margin_bytes=1536*1024**2,
                gpu_limit_bytes=total-1536*1024**2,gpu_policy="measured-total-minus-1.5GiB-v1",gpu_ok=True))
        common.atomic_json(self.root/"forecast.json",self.forecast)

    def tearDown(self):self.temporary.cleanup()

    def launch(self):
        stage.stage_p_launch(self.args,self.identity,self.now,self.identity["device"]["total_bytes"])

    def test_forecast_bound_to_choice_device_clock_profiles_and_code(self):
        self.launch()
        self.launch()
        for key in ("user_choice_sha256","config_sha256","source_manifest_sha256","identity_code","identity_profiles","identity_packages","device","instance_start_utc","ceiling_seconds"):
            changed=copy.deepcopy(self.forecast);changed[key]="changed"
            common.atomic_json(self.root/"forecast.json",changed)
            with self.assertRaises(ValueError):self.launch()
        common.atomic_json(self.root/"forecast.json",self.forecast)
        (self.root/"tune/f6-x0-p52/identity.json").write_text("{}")
        with self.assertRaises(ValueError):self.launch()

    def test_only_calibration_bypasses_full_forecast_and_keeps_hard_clock(self):
        (self.root/"forecast.json").unlink()
        self.args.stage_p_calibration=True
        self.launch()
        self.args.stage_p_calibration=False
        with self.assertRaises(FileNotFoundError):self.launch()
        self.args.stage_p_calibration=True
        self.now+=85000
        with self.assertRaises(common.ResourceStop):self.launch()

    def test_alarm_uses_current_instance_clock_and_reserve(self):
        args=SimpleNamespace(max_hours=24)
        instant=datetime(2026,1,1,tzinfo=timezone.utc)
        fake_signal=SimpleNamespace(SIGALRM=14,ITIMER_REAL=0,signal=Mock(),setitimer=Mock())
        with patch.dict(sys.modules,{"signal":fake_signal}):
            seconds=stage.install_deadline(args,self.config,instant,now=instant.timestamp()+100)
            self.assertEqual(seconds,82700)
            fake_signal.setitimer.assert_called_once_with(0,82700)
            handler=fake_signal.signal.call_args.args[1]
            with self.assertRaises(common.ResourceStop):handler(14,None)
            with self.assertRaises(common.ResourceStop):stage.install_deadline(args,self.config,instant,now=instant.timestamp()+84000)

    def test_alarm_during_operation_is_preserved_as_resource_stop(self):
        args=SimpleNamespace(invocation="pure-mock-invocation")
        torch=SimpleNamespace(cuda=SimpleNamespace(OutOfMemoryError=type("MockOOM",(Exception,),{}),reset_peak_memory_stats=Mock()))
        journal=SimpleNamespace(done=lambda uid:False,append=Mock())
        budget=SimpleNamespace(require=Mock())
        operation=Mock(side_effect=common.ResourceStop("collection reserve reached"))
        with patch.object(stage,"telemetry",return_value={"device_total_bytes":48*1024**3}):
            with self.assertRaisesRegex(common.ResourceStop,"collection reserve"):
                stage.execute_unit(args,{},budget,None,torch,journal,dict(id="opaque-unit"),operation,"opaque-operation")
        persisted=journal.append.call_args.args[0]
        self.assertEqual(persisted["status"],"resource_stop")
        self.assertEqual(persisted["invocation"],args.invocation)
        self.assertGreaterEqual(persisted["seconds"],0)
        self.assertIn("collection reserve reached",persisted["error"])


if __name__=="__main__":unittest.main()
