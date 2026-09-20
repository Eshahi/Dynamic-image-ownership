"""Preregistration packaging and explicit compute estimates."""
from .common import ContractError, fresh_dir, parser, read, validate, write

def recommend(resources, measured_free_mib=None):
    ceiling = 10240 if measured_free_mib is None else min(10240, max(0,measured_free_mib-1024))
    reasons=[]
    if resources["vram_mib"]>ceiling: reasons.append("VRAM exceeds safe available ceiling")
    if resources["ram_mib"]>28672: reasons.append("RAM exceeds conservative 28 GiB allowance")
    return {"target":"runpod" if reasons else "local","safe_vram_mib":ceiling,"reasons":reasons or ["Within conservative local VRAM/RAM limits; disk and availability must be checked"]}

def design(spec, execution, out):
    validate(spec,"experiment"); validate(execution,"execution")
    if spec["experiment_id"]!=execution["experiment_id"] or spec["task_id"]!=execution["task_id"] or spec["seeds"]!=execution["seeds"] or spec["datasets"]!=execution["datasets"]:
        raise ContractError("Experiment and execution contracts disagree")
    if len(set(spec["seeds"])) != len(spec["seeds"]): raise ContractError("Duplicate seeds")
    budget=execution["budget"]
    estimate=budget["hourly_usd"]*budget["max_seconds"]/3600
    if estimate>budget["max_usd"]: raise ContractError("Compute estimate exceeds budget")
    selection=recommend(execution["resources"])
    if execution["execution_target"]=="local" and selection["target"]!="local": raise ContractError("Local target exceeds resource envelope")
    out=fresh_dir(out)
    write(out/"experiment-spec.yaml",spec)
    write(out/"execution-manifest.json",execution)
    write(out/"compute-estimate.json",{"resources":execution["resources"],"budget":budget,"estimated_compute_usd":estimate,"storage_and_egress":"Must be added to approved hourly estimate; not independently priced",**selection})
    write(out/"plan.md",f"# {spec['experiment_id']}\n\nQuestion: {spec['question']}\n\nHypothesis: {spec['hypothesis']}\n\nPrimary outcome: {spec['primary_outcome']}\n\nPreprocessing: {spec['preprocessing']}\n\nStopping: {spec['stopping_rule']}\n\nLeakage risks: {'; '.join(spec['leakage_risks'])}\n\nThe machine-readable specification is canonical. Estimates are user-supplied, not live quotes. No execution authorized by generating this plan.\n")
    write(out/"acceptance-criteria.md",f"# Acceptance criteria\n\n{spec['acceptance_rule']}\n\nNegative results: {spec['negative_result_policy']}\n\nHuman review required before execution; remote spending needs a scoped, unexpired approval bound to the execution manifest hash.\n")
    return selection

def main():
    p=parser("Validate and package an experiment before execution")
    p.add_argument("spec"); p.add_argument("execution"); p.add_argument("--out",required=True)
    a=p.parse_args(); return design(read(a.spec),read(a.execution),a.out)
