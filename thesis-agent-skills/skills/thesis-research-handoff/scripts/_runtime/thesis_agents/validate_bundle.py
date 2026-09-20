"""Validate skills, code safety and official Spec Kit definitions without execution."""
import ast
import importlib.util
import json
from pathlib import Path
import re
from .common import ContractError, parser, read

def validate_skill(path):
    import yaml
    text=(path/"SKILL.md").read_text(encoding="utf-8")
    match=re.match(r"\A---\n(.*?)\n---\n",text,re.S)
    if not match: raise ContractError("Missing YAML frontmatter: "+path.name)
    data=yaml.safe_load(match.group(1))
    if set(data)-{"name","description","metadata","license","allowed-tools"}: raise ContractError("Unknown frontmatter")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",data["name"]) or len(data["name"])>=64 or data["name"]!=path.name: raise ContractError("Invalid skill name")
    if not isinstance(data["description"],str) or not 1<=len(data["description"])<=1024: raise ContractError("Invalid description")
    ui=yaml.safe_load((path/"agents/openai.yaml").read_text(encoding="utf-8"))
    if ui.get("policy",{}).get("allow_implicit_invocation") is not True: raise ContractError("Discovery must remain enabled")
    if not 25<=len(ui["interface"]["short_description"])<=64: raise ContractError("Invalid UI description")
    for target in re.findall(r"\]\(([^)]+)\)",text):
        if not target.startswith("https://") and not (path/target).is_file(): raise ContractError("Broken skill reference: "+target)
    if re.search(r"(?m)^\s*\[TODO:|\bTBD\b|IMPLEMENT[_ ]ME",text): raise ContractError("Unfinished skill scaffold")
    return True

def validate_bundle(root):
    root=Path(root).resolve(); checked=[]
    for path in sorted((root/"skills").iterdir()):
        if path.is_dir(): validate_skill(path); checked.append(path.name)
    if len(checked)!=8: raise ContractError("Expected eight skills")
    for tree in ("src","skills","installers","spec-kit/steps","tools"):
        for file in (root/tree).rglob("*.py"):
            if "__pycache__" in file.parts: continue
            parsed=ast.parse(file.read_text(encoding="utf-8"),filename=str(file))
            for node in ast.walk(parsed):
                if isinstance(node,ast.Call):
                    if any(k.arg=="shell" and isinstance(k.value,ast.Constant) and k.value.value is True for k in node.keywords): raise ContractError("Forbidden shell execution: "+str(file))
                    if isinstance(node.func,ast.Name) and node.func.id in ("eval","exec"): raise ContractError("Dynamic execution forbidden")
                    if isinstance(node.func,ast.Attribute) and node.func.attr in ("rmtree","system"): raise ContractError("Destructive or shell primitive forbidden")
    from specify_cli.workflows import STEP_REGISTRY
    from specify_cli.workflows.engine import WorkflowDefinition,validate_workflow
    from .plan import HUMAN_GATES, github_issue_seed, reduce_guide
    source_plan=read(root/"fixtures/guide-tasks.json")
    reduced_plan=read(root/"fixtures/guide-plan-38.json")
    if reduced_plan != reduce_guide(source_plan): raise ContractError("Stale or modified thesis-38 fixture")
    if read(root/"fixtures/github-issue-seed-38.json") != github_issue_seed(reduced_plan): raise ContractError("Stale or modified GitHub issue seed")
    entry=root/"spec-kit/steps/thesis-safe/__init__.py"
    module_spec=importlib.util.spec_from_file_location("thesis_safe_validator",entry)
    module=importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    STEP_REGISTRY["thesis-safe"]=module.ThesisSafeStep()
    workflows=[]
    for file in sorted((root/"spec-kit/workflows").glob("*/workflow.yml")):
        definition=WorkflowDefinition.from_yaml(file)
        errors=validate_workflow(definition)
        if errors: raise ContractError("; ".join(errors))
        if any(s.get("type")=="shell" for s in definition.steps): raise ContractError("Bundle workflows must not execute shell steps")
        gates=[s for s in definition.steps if s.get("type")=="gate"]
        for g in gates:
            if definition.inputs[g["verdict_input"]].get("default")!="": raise ContractError("A gate must never default to approval")
        workflows.append({"id":definition.id,"steps":len(definition.steps),"gates":len(gates)})
        if definition.id=="thesis-lifecycle":
            if [g["id"] for g in gates] != [g["id"] for g in HUMAN_GATES]: raise ContractError("Lifecycle human gates disagree with thesis-38 profile")
    return {"skills":checked,"task_profile":{"source":58,"execution":38,"milestones":5,"human_gates":7},"workflows":workflows,"code_safety":"passed"}

def main():
    p=parser("Validate skill contracts, code safety and official workflow schema")
    p.add_argument("bundle"); a=p.parse_args(); return validate_bundle(a.bundle)
