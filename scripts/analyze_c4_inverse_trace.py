"""Read-only retained scalar trace diagnosis. No model, tensor, image or GPU use."""
import argparse
import hashlib
import json
import math
from pathlib import Path

RUN = "c4-refined-target-dev-001"
BINDING = "78bcae98866135714d0f7847a8de7d076f1adea29c20509d8766079d95088683"
ARMS = ("fixed_point_encoded_inverse", "fixed_point_refined_inverse")


def real(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("finite nonnegative scalar required")
    return value


def integer(value):
    if type(value) is not int or value < 1:
        raise ValueError("positive exact integer required")
    return value


def diagnose(rows, report, record):
    if not rows or len(rows) > 20000:
        raise ValueError("bounded nonempty journal required")
    if (report.get("run_id") != RUN or record.get("run_id") != RUN
            or report.get("manifest_sha256") != BINDING
            or record.get("execution_manifest_sha256") != BINDING
            or report.get("git_commit") != record.get("git_commit")
            or record.get("status") != "failed" or type(record.get("exit_status")) is not int
            or record["exit_status"] != 1 or report.get("status") != "failed_retained_partial"):
        raise ValueError("exact retained failed execution binding required")
    previous = -1
    for row in rows:
        if type(row) is not dict or type(row.get("phase")) is not str:
            raise ValueError("malformed journal row")
        elapsed = real(row.get("elapsed_seconds"))
        if elapsed < previous:
            raise ValueError("journal time reversal")
        previous = elapsed
    if rows[-1]["phase"] != "failed":
        raise ValueError("terminal worker failure required; no running trace")
    pairs = []
    for arm in ARMS:
        scope = [r for r in rows if r.get("arm") == arm]
        states = [r for r in scope if r["phase"] == "pair_state"]
        for row in scope:
            if row["phase"] in ("pair_state", "evaluated", "terminated", "evaluation_started"):
                integer(row.get("timestep"))
        if [r.get("timestep") for r in states] != [1, 101]:
            raise ValueError("exact two-pair attempt inventory required")
        total = 0
        for timestep in (1, 101):
            evaluated = [r for r in scope if r["phase"] == "evaluated" and r.get("timestep") == timestep]
            endings = [r for r in scope if r["phase"] == "terminated" and r.get("timestep") == timestep]
            starts = [r for r in scope if r["phase"] == "evaluation_started" and r.get("timestep") == timestep]
            if not evaluated or len(endings) != 1 or len(starts) != len(evaluated):
                raise ValueError("incomplete pair evaluation inventory")
            for sequence in (evaluated, starts):
                if [integer(r.get("evaluation")) for r in sequence] != list(range(1, len(evaluated)+1)):
                    raise ValueError("duplicate/missing/out-of-order pair evaluation")
            errors = [real(r.get("residual_max")) for r in evaluated]
            objectives = [real(r.get("objective")) for r in evaluated]
            end = endings[0]
            if (integer(end.get("evaluations")) != len(evaluated)
                    or real(end.get("residual_max")) != errors[-1]
                    or real(end.get("objective")) != objectives[-1]):
                raise ValueError("pair terminal does not match last measured state")
            state = next(r for r in states if r["timestep"] == timestep)
            total += len(evaluated)
            expected_status = "converged" if timestep == 1 else "evaluation_budget"
            if end.get("status") != expected_status or state.get("status") != expected_status:
                raise ValueError("unexpected pair status; do not reinterpret another run")
            if integer(state.get("evaluations")) != total or state.get("residual_max") != errors[-1]:
                raise ValueError("pair state/path accounting mismatch")
            pairs.append({"arm": arm, "timestep": timestep, "status": expected_status,
                "evaluations": len(evaluated), "first_residual_max": errors[0],
                "minimum_residual_max": min(errors), "minimum_residual_evaluation": errors.index(min(errors))+1,
                "last_residual_max": errors[-1], "first_objective_l1": objectives[0],
                "last_objective_l1": objectives[-1],
                "residual_increases": sum(b > a for a,b in zip(errors,errors[1:])),
                "objective_increases": sum(b > a for a,b in zip(objectives,objectives[1:])),
                "last_over_best_residual": errors[-1]/min(errors) if min(errors) else None,
                "trace": [{"evaluation": i+1,"residual_max":e,"objective_l1":o}
                          for i,(e,o) in enumerate(zip(errors,objectives))]})
        outcome = report["arms"][arm]["component_outcome"]
        if (outcome.get("status") != "not_rendered_nonconverged"
                or integer(outcome.get("actual_unet_forward_calls")) != total
                or outcome.get("roundtrip_residual_max") is not None):
            raise ValueError("worker arm accounting mismatch")
    return {"run_id": RUN, "manifest_sha256": BINDING, "pairs": pairs,
        "scope": "retained-scalar-trace-description-only",
        "conclusion": "Both t1 pairs converged; both t101 pair budgets exhausted. Residual increases are observations, not a Jacobian/noncontraction proof or signed-vector oscillation test.",
        "scientific_acceptance": False, "compute_authorization": False}


def strict_object(items):
    obj = {}
    for key,value in items:
        if key in obj:
            raise ValueError("duplicate JSON field")
        obj[key] = value
    return obj


def load(path, *, lines=False):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8*1024**2:
        raise ValueError("bounded regular metadata file required")
    raw = path.read_bytes()
    def parse(text):
        return json.loads(text,object_pairs_hook=strict_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    return ([parse(row) for row in raw.splitlines()] if lines else parse(raw)), hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("journal", "report", "record", "output"):
        parser.add_argument("--"+name, required=True, type=Path)
    args = parser.parse_args()
    rows,journal_sha = load(args.journal,lines=True)
    report,report_sha = load(args.report)
    record,record_sha = load(args.record)
    result = diagnose(rows,report,record)
    result["provenance"] = {"journal_sha256":journal_sha,"worker_report_sha256":report_sha,
        "runner_record_sha256":record_sha,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    payload = json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if args.output.is_symlink() or args.output.exists():
        raise ValueError("new nonlinked output required; no overwrite")
    with args.output.open("x",encoding="utf-8",newline="\n") as stream:
        stream.write(payload)
    print(json.dumps({"run_id":RUN,"pairs":len(result["pairs"]),"scientific_execution":False}))


if __name__ == "__main__":
    main()
