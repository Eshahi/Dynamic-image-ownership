"""Generate strict JSON Schemas; JSON fixtures are also valid YAML 1.2."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = {"type": "string", "minLength": 1}
ID = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$"}
SHA = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
DATE = {"type": "string", "format": "date-time"}
NUM = {"type": "number"}
POS = {"type": "number", "exclusiveMinimum": 0}
BOOL = {"type": "boolean"}
def arr(item=S, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum}
def enum(*values):
    return {"enum": list(values)}
def obj(fields, optional=()):
    return {"type": "object", "properties": fields, "required": [k for k in fields if k not in optional], "additionalProperties": False}
ART = obj({"path": S, "sha256": SHA})
BUDGET = obj({"max_seconds": {"type": "integer", "minimum": 1, "maximum": 86400}, "max_usd": {"type": "number", "minimum": 0}, "hourly_usd": {"type": "number", "minimum": 0}})
DATASET = obj({"id": S, "version": S, "license": S, "split": S})
SCHEMAS = {}
SCHEMAS["approval"] = obj({"schema_version": enum("1.0"), "experiment_id": ID, "run_id": ID, "execution_target": enum("local", "runpod", "mock"), "manifest_sha256": SHA, "decision": enum("approve", "reject"), "timestamp": DATE, "expires_at": DATE, "max_seconds": POS, "max_usd": {"type":"number", "minimum":0}, "actor": S, "source_ref": S})
SCHEMAS["execution"] = obj({"schema_version": enum("1.0"), "experiment_id": ID, "run_id": ID, "stage_id": ID, "task_id": ID, "execution_target": enum("local", "runpod", "mock"), "reviewed_script": S, "script_sha256": SHA, "git_commit": {"type":"string", "pattern":"^[a-f0-9]{40}$"}, "seeds": arr({"type":"integer"},1), "datasets": arr(DATASET), "inputs": arr(ART), "outputs": arr(S,1), "metrics": arr(S,1), "budget": BUDGET, "resources": obj({"vram_mib": {"type":"integer", "minimum":0}, "ram_mib":POS, "disk_mib":POS}), "remote": obj({"image": S, "gpu_type": S, "gpu_count": {"type":"integer", "minimum":1,"maximum":8}, "artifact_base_url": {"type":"string", "format":"uri"}, "terminate_after_seconds": {"type":"integer","minimum":1,"maximum":86400}}), "cleanup_policy": enum("delete-after-verified", "stop-for-recovery")}, optional=("remote",))
SCHEMAS["run"] = obj({"schema_version":enum("1.0"), "run_id":ID, "stage_id":ID, "task_id":ID, "experiment_id":ID, "status":enum("running","completed","failed","interrupted","recovery-required"), "executor":S, "execution_target":enum("local","runpod","mock"), "created_at":DATE, "started_at":DATE, "ended_at":{"anyOf":[DATE,{"type":"null"}]}, "git_commit":{"type":"string","pattern":"^[a-f0-9]{40}$"}, "git_dirty":BOOL, "command":arr(S,1), "environment":obj({"python":S,"platform":S}), "system":obj({"gpu":arr({"type":"object"}),"cpu_count":{"type":["integer","null"]}}), "seeds":arr({"type":"integer"},1), "datasets":arr(DATASET), "input_artifacts":arr(ART), "output_artifacts":arr(ART), "declared_metrics":arr(S,1), "budget_limits":BUDGET, "approval_reference":{"type":["string","null"]}, "execution_manifest_sha256":SHA, "errors":arr(S), "cleanup_status":S, "pod_id":{"type":["string","null"]}, "exit_status":{"type":["integer","null"]}})
SCHEMAS["paper"] = obj({"schema_version":enum("1.0"),"paper_id":ID,"citation_key":ID,"doi":{"type":["string","null"],"pattern":"^10\\.\\d{4,9}/\\S+$"},"canonical_url":{"type":"string","format":"uri"},"title":S,"authors":arr(S,1),"year":{"type":"integer","minimum":1500,"maximum":2200},"venue":{"type":["string","null"]},"access_date":{"type":"string","format":"date"},"source_type":enum("paper","preprint","report","dataset","web"),"verification":enum("verified","unverified","inaccessible"),"inspected_content":enum("full-text","abstract","metadata","snippet","none"),"inspection":obj({"artifact":S,"sha256":SHA},optional=()),"limitations":arr(S)},optional=("inspection",))
SCHEMAS["evidence"] = obj({"claim_id":ID,"claim":S,"source_id":ID,"kind":enum("direct-evidence","author-interpretation","agent-inference","open-assumption"),"stance":enum("supporting","contradicting","inconclusive"),"locator":{"type":["string","null"]},"confidence":enum("low","medium","high"),"limitations":arr(S),"assumptions":arr(S)})
SCHEMAS["research-response"] = obj({"request_id":ID,"papers":arr(SCHEMAS["paper"],1),"evidence":arr(SCHEMAS["evidence"],1),"assumptions":arr(S),"open_questions":arr(S)})
SCHEMAS["experiment"] = obj({"schema_version":enum("1.0"),"experiment_id":ID,"task_id":ID,"question":S,"hypothesis":S,"primary_outcome":S,"secondary_outcomes":arr(S),"datasets":arr(DATASET),"leakage_risks":arr(S,1),"preprocessing":S,"baselines":arr(S,1),"controls":arr(S,1),"ablations":arr(S),"seeds":arr({"type":"integer"},1),"stopping_rule":S,"acceptance_rule":S,"negative_result_policy":S,"analysis":obj({"mode":enum("preregistered","exploratory"),"metric":S,"direction":enum("higher","lower"),"conditions":arr(S,1),"expected_runs":arr(obj({"run_id":ID,"condition":S,"seed":{"type":"integer"}}),1),"comparison":{"type":["array","null"],"items":S,"minItems":2,"maxItems":2},"confidence_interval":enum("none","paired-bootstrap"),"bootstrap_samples":{"type":"integer","minimum":100,"maximum":100000},"random_seed":{"type":"integer"},"multiple_comparisons":enum("none-single-comparison"),"exclusion_rule":enum("none")})})
SCHEMAS["claims"] = obj({"claim_id":ID,"text":S,"evidence_ids":arr(ID),"run_ids":arr(ID),"analysis_paths":arr(S),"kind":enum("result","interpretation","limitation","future-work"),"author_id":ID})
SCHEMAS["gate-decision"] = obj({"run_id":ID,"step_id":ID,"verdict":enum("approve","reject","revise","retry","stop"),"state_sha256":SHA,"timestamp":DATE,"expires_at":DATE,"actor":S,"source_ref":S})

def main():
    import argparse
    argparse.ArgumentParser(description=__doc__).parse_args()
    target = ROOT / "src/thesis_agents/schemas"
    target.mkdir(parents=True, exist_ok=True)
    for name, data in SCHEMAS.items():
        data = {"$schema":"https://json-schema.org/draft/2020-12/schema","title":name,**data}
        (target / f"{name}.schema.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(f"Generated {len(SCHEMAS)} schemas")

if __name__ == "__main__":
    main()
