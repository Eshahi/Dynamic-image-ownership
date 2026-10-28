"""Pure logic forecast guard tests; no images or science libraries."""
import importlib.util
import math
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("forecast",Path(__file__).with_name("tifs_stage_s_forecast.py"))
f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)


class ForecastTests(unittest.TestCase):
    def test_storage_margin_and_24gb_ceiling(self):
        gib=1024**3
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,23*gib)["status"],"GO")
        self.assertEqual(f.capacity(gib,8,31*gib,100*gib,23*gib)["status"],"RESOURCE_STOP")
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,25*gib)["status"],"RESOURCE_STOP")
        with self.assertRaises(ValueError): f.capacity(gib,8,40*gib,100*gib,0)

    def test_full_clock_includes_prior_elapsed(self):
        self.assertEqual(f.calculate(1000,200,1000)["forecast_seconds"],6300)
        self.assertEqual(f.calculate(50000,200,1000)["status"],"RESOURCE_STOP")

    def test_inclusive_budget_boundary(self):
        self.assertEqual(f.calculate(0,0,33600)["status"],"GO")
        self.assertEqual(f.calculate(.01,0,33600)["status"],"RESOURCE_STOP")

    def test_missing_rehearsal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(OSError): f.forecast(Path(tmp),Path(tmp)/"config", "2026-01-01T00:00:00Z",2000000000)

    def test_retained_resource_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/"RESOURCE_STOP.json").write_text('{}')
            self.assertEqual(f.forecast(Path(tmp),None,None,None)["status"],"RESOURCE_STOP")

    def test_invalid_measurements(self):
        for x in (-1,math.inf,math.nan,True,None):
            with self.assertRaises(ValueError): f.calculate(0,0,x)

    def test_cumulative_resumed_invocations_and_sealed_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"invocations.jsonl"
            events=[dict(event="INVOCATION_START",invocation="one",epoch=10,stage="clean"),
                    dict(event="MODEL_READY",invocation="one",label="load_f6-noise",load_seconds=20),
                    dict(event="INVOCATION_END",invocation="one",seconds=110),
                    dict(event="INVOCATION_START",invocation="two",epoch=130,stage="clean"),
                    dict(event="INVOCATION_END",invocation="two",seconds=110)]
            path.write_text("\n".join(json.dumps(e) for e in events))
            rows=[dict(invocation="one",operation="clean_f6-noise",seconds=90),
                  dict(invocation="two",operation="clean_f6-noise",seconds=90)]
            prepare,overhead,bounds=f.invocation_measurements(path,300,rows)
            self.assertEqual(prepare,0)
            self.assertEqual(overhead,70)
            self.assertEqual(bounds,{"clean_f6-noise":135,"load_f6-noise":30})

    def test_killed_invocation_clock_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"invocations.jsonl"
            path.write_text(json.dumps(dict(event="INVOCATION_START",invocation="one",epoch=10,stage="native")))
            self.assertEqual(f.invocation_measurements(path,110,[])[1],100)

    def test_load_memory_high_water_includes_nonallocator_use(self):
        gib=1024**3
        peak=f.measured_peak(dict(device_used_bytes=10*gib,reserved_bytes=8*gib,max_reserved_bytes=23*gib))
        self.assertEqual(peak,25*gib)
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,peak)["status"],"RESOURCE_STOP")

    def test_screen_requires_measured_operation_bounds(self):
        self.assertEqual(f.stage.estimate({"_runtime_bounds":{"native_K3":1234}},"native_K3"),1234)
        with self.assertRaises(ValueError): f.stage.estimate({"_runtime_bounds":{}},"native_K3",900)

    def test_failed_or_missing_stage_done_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"clean.log"
            for text in ('', '{"event":"UNIT_DONE","status":"error_terminal"}\n','{"event":"STAGE_DONE","seconds":null}\n'):
                log.write_text(text)
                with self.assertRaises(ValueError): f.timings(log)

    def test_resume_uses_original_completed_stage_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            log=Path(tmp)/"clean.log"
            log.write_text('{"event":"STAGE_DONE","seconds":300}\n{"event":"STAGE_DONE","seconds":1}\n')
            self.assertEqual(f.timings(log),300)


if __name__=="__main__": unittest.main()
