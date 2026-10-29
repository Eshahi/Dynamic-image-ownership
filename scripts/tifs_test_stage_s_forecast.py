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
    def test_stage_p_full_allocation_uses_upper_candidate_and_budget_cost(self):
        keys=("clean_f6-noise","clean_f6-x0","clean_f5-r2","clean_unmarked",
              "native_R0","native_R1","native_K3","detect_f6-noise","detect_f6-x0",
              "detect_f5-r2","quality","prepare","load_f6-noise","load_f6-x0",
              "load_f5-r2","load_R0","load_R1","load_K3","load_reader","load_quality")
        bounds={k:1 for k in keys}
        bounds["clean_f6-noise"]=10
        bounds["clean_f6-x0"]=30
        counts,costs,expanded=f.stage_p_allocation(bounds)
        self.assertEqual(sum(counts[k] for k in ("candidate_clean","retained_clean","budget_clean")),136)
        self.assertEqual(sum(counts[k] for k in ("native_R0","native_R1","native_K3")),3264)
        self.assertEqual(counts["detect"],3536)
        self.assertEqual(costs["candidate_clean"],2160)
        self.assertEqual(costs["budget_clean"],1200)
        self.assertEqual(expanded["clean_f5-budget"],30)
        self.assertEqual(costs["model_loads"],24*8)
        for key in keys:
            incomplete=dict(bounds);incomplete.pop(key)
            with self.assertRaises(ValueError):f.stage_p_allocation(incomplete)

    def test_explicit_later_cap_does_not_change_default(self):
        self.assertEqual(f.calculate(0,0,40000)["status"],"RESOURCE_STOP")
        self.assertEqual(f.calculate(0,0,40000,ceiling=126*3600)["status"],"GO")

    def test_storage_margin_and_measured_device_ceiling(self):
        gib=1024**3
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,22*gib,24*gib)["status"],"GO")
        self.assertEqual(f.capacity(gib,8,31*gib,100*gib,22*gib,24*gib)["status"],"RESOURCE_STOP")
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,23*gib,24*gib)["status"],"RESOURCE_STOP")
        result=f.capacity(gib,8,40*gib,100*gib,35*gib,48*gib)
        self.assertEqual(result["status"],"GO")
        self.assertEqual(result["gpu_limit_bytes"],46.5*gib)
        self.assertEqual(result["gpu_margin_bytes"],1.5*gib)
        self.assertNotIn("tested_24gb_fit",result)
        with self.assertRaises(ValueError): f.capacity(gib,8,40*gib,100*gib,0,48*gib)

    def test_gpu_boundary_minimum_and_invalid_total(self):
        gib=1024**3
        limit=48*gib-f.GPU_MARGIN_BYTES
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,limit,48*gib)["status"],"GO")
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,limit+1,48*gib)["status"],"RESOURCE_STOP")
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,gib,16*gib)["status"],"RESOURCE_STOP")
        for value in (None, True, math.nan, math.inf, -1):
            with self.assertRaises(ValueError): f.capacity(gib,8,40*gib,100*gib,gib,value)

    def test_measured_gpu_total_must_be_present_and_constant(self):
        rows=[dict(device_total_bytes=48*1024**3)]*2
        self.assertEqual(f.measured_device_total(rows),48*1024**3)
        for rows in ([],[{}],[dict(device_total_bytes=0)],
                     [dict(device_total_bytes=24*1024**3),dict(device_total_bytes=48*1024**3)]):
            with self.assertRaises(ValueError): f.measured_device_total(rows)

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
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,peak,24*gib)["status"],"RESOURCE_STOP")
        self.assertEqual(f.capacity(gib,8,40*gib,100*gib,peak,48*gib)["status"],"GO")

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
