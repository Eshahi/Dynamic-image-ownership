import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("trace",Path(__file__).with_name("analyze_c4_inverse_trace.py"))
trace = importlib.util.module_from_spec(spec); spec.loader.exec_module(trace)


def fixture():
    rows=[]; arms={}
    def add(**row):
        rows.append({"elapsed_seconds":len(rows),**row})
    for arm in trace.ARMS:
        total=0
        for timestep in (1,101):
            status="converged" if timestep==1 else "evaluation_budget"
            add(phase="pair_started",arm=arm,timestep=timestep)
            errors=(.1,.01,.001,.0001,.00003,.00002,.000005) if timestep==1 else (.2,.1)+(.15,)*30
            for i,error in enumerate(errors,1):
                add(phase="evaluation_started",arm=arm,timestep=timestep,evaluation=i)
                add(phase="evaluated",arm=arm,timestep=timestep,evaluation=i,residual_max=error,objective=error*10)
            add(phase="terminated",arm=arm,timestep=timestep,evaluations=i,status=status,residual_max=error,objective=error*10)
            total+=i
            add(phase="pair_state",arm=arm,timestep=timestep,evaluations=total,status=status,residual_max=error)
        add(phase="path_terminated",arm=arm,status="pair_not_converged",evaluations=39,backward_evaluations=0,roundtrip_residual_max=None)
        add(phase="path_forward_accounting",arm=arm,actual_unet_forward_calls=39,checkpoint_recomputation_calls=0)
        arms[arm]={"component_outcome":{"status":"not_rendered_nonconverged","actual_unet_forward_calls":total,"roundtrip_residual_max":None}}
    add(phase="failed")
    report={"run_id":trace.RUN,"manifest_sha256":trace.BINDING,"git_commit":trace.COMMIT,
            "status":"failed_retained_partial","arms":arms}
    record={"run_id":trace.RUN,"execution_manifest_sha256":trace.BINDING,"git_commit":trace.COMMIT,
            "status":"failed","exit_status":1}
    return rows,report,record


class TraceTests(unittest.TestCase):
    def test_owned_summary(self):
        out=trace.diagnose(*fixture())
        self.assertEqual(len(out["pairs"]),4)
        self.assertEqual(out["pairs"][1]["residual_increases"],1)
        self.assertAlmostEqual(out["pairs"][1]["last_over_best_residual"],1.5)
        self.assertFalse(out["scientific_acceptance"])
    def test_stale_binding(self):
        rows,report,record=fixture(); report["manifest_sha256"]="0"*64
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_bool_exit(self):
        rows,report,record=fixture();record["exit_status"]=True
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_duplicate_eval(self):
        rows,report,record=fixture();rows[4]["evaluation"]=1
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_time_reversal(self):
        rows,report,record=fixture();rows[-1]["elapsed_seconds"]=0
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_nonfinite(self):
        rows,report,record=fixture();rows[2]["residual_max"]=float("nan")
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_unmeasured_terminal(self):
        rows,report,record=fixture();next(r for r in rows if r["phase"]=="terminated")["residual_max"]=2
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_running_journal(self):
        rows,report,record=fixture();rows[-1]["phase"]="started"
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_duplicate_json(self):
        with self.assertRaises(ValueError):trace.strict_object([("x",1),("x",2)])
    def test_bool_timestep(self):
        rows,report,record=fixture(); rows[0]["timestep"]=True
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_bool_forward_count(self):
        rows,report,record=fixture(); report["arms"][trace.ARMS[0]]["component_outcome"]["actual_unet_forward_calls"]=True
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_missing_or_unrelated_commit(self):
        for commit in (None,"1"*40):
            rows,report,record=fixture();report["git_commit"]=record["git_commit"]=commit
            with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_evaluated_before_start(self):
        rows,report,record=fixture(); rows[1]["phase"],rows[2]["phase"]=rows[2]["phase"],rows[1]["phase"]
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_extra_timestep(self):
        rows,report,record=fixture();rows.insert(1,dict(rows[1],timestep=202))
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_false_convergence(self):
        rows,report,record=fixture()
        for row in rows:
            if row.get("timestep")==1 and "residual_max" in row: row["residual_max"]=.01
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)
    def test_path_terminal_mismatch(self):
        rows,report,record=fixture();next(r for r in rows if r["phase"]=="path_terminated")["evaluations"]=38
        with self.assertRaises(ValueError):trace.diagnose(rows,report,record)


if __name__=="__main__":unittest.main()
