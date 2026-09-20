"""Deterministic 38-task execution profile derived from the 58-task source guide."""
from __future__ import annotations

import json
from collections import deque

from .common import ContractError, object_digest


# Keep source IDs explicit: this is a reviewed reduction contract, not a heuristic merge.
TASKS = {
    "A1": ("Repository and proposal ingestion", "spec", ["eng-1"]),
    "A2a": ("Claims and operational scope", "spec", ["contract-1", "repair-1"]),
    "A3": ("I/O, notation and threat model", "spec", ["contract-2", "contract-3"]),
    "A2b": ("Traceability, research contract and scope guard", "spec", ["repair-2", "contract-4", "method-6"]),
    "A4": ("Acceptance criteria, sample size and stop rules", "spec", ["repair-3", "contract-5"]),
    "A5": ("Architecture specification", "spec", ["repair-4"]),
    "A6": ("Environment lock", "spec", ["eng-2"]),
    "B1": ("Search protocol, literature matrix and bibliography", "data", ["lit-1", "lit-2", "repair-5"]),
    "B2": ("Baseline selection and reproducibility review", "data", ["lit-4", "lit-3", "lit-5"]),
    "B3": ("Data manifest, licensing and datasheet", "data", ["data-1", "data-4"]),
    "B4": ("Sampling, split lock and OOD holdout", "data", ["data-2", "data-3"]),
    "B5": ("Versioned preprocessing", "data", ["data-5"]),
    "B6": ("Thesis outline and university template", "data", ["write-1", "repair-6"]),
    "C1": ("Configuration and run logging", "method", ["eng-3"]),
    "C3a": ("Owner identity and key protocol", "method", ["method-3"]),
    "C2": ("Semantic key", "method", ["method-1"]),
    "C3b": ("Instance key and fusion", "method", ["method-2"]),
    "C4": ("Embedding module", "method", ["method-4"]),
    "C5": ("Detector and validation-only calibration", "method", ["method-5"]),
    "C6": ("Key stability and collision study", "method", ["feas-1"]),
    "C7": ("Classical DCT positive control", "method", ["feas-2"]),
    "C8": ("Reference latent-watermark reproduction", "method", ["feas-3"]),
    "C9": ("Latent-to-DCT bridge test", "method", ["feas-4"]),
    "C10": ("Integrated tests, end-to-end smoke and technical gate", "method", ["eng-4", "feas-5", "eng-5"]),
    "D1": ("Method freeze and evaluation preregistration", "eval", ["method-7", "eval-1"]),
    "D2": ("Paired quality and runtime evaluation", "eval", ["eval-2", "eval-6"]),
    "D3": ("Benign attack grid", "eval", ["eval-3"]),
    "D4": ("Regeneration attacks", "eval", ["eval-4"]),
    "D5": ("Forgery, copy-paste and hard negatives", "eval", ["eval-5"]),
    "D9": ("Preregistered ablation", "eval", ["stats-5"]),
    "D6": ("Result quality control and exclusions", "eval", ["stats-1"]),
    "D7": ("Clustered bootstrap confidence intervals", "eval", ["stats-2"]),
    "D8": ("Preregistered tests, effect sizes and Holm correction", "eval", ["stats-3", "stats-4"]),
    "E1": ("Method and protocol chapters", "review", ["write-2"]),
    "E2": ("Results chapter and failure figures", "review", ["stats-6", "write-3"]),
    "E3": ("Discussion, limitations and novelty reaudit", "review", ["write-4"]),
    "E4": ("Representative rerun and reproducibility package", "review", ["eval-7", "write-5"]),
    "E5": ("First-review handoff and academic checklist", "review", ["write-6", "write-7"]),
}

MILESTONE_TITLES = {
    "spec": "Specification",
    "data": "Data & Literature",
    "method": "Implementation",
    "eval": "Evaluation & Statistics",
    "review": "First Review",
}

HUMAN_GATES = [
    {"id": "scope-acceptance", "purpose": "Accept scope and unresolved proposal inputs."},
    {"id": "evidence-review", "purpose": "Review inspected literature evidence and contradictions."},
    {"id": "plan-acceptance", "purpose": "Accept preregistration, negative-result policy and compute estimate."},
    {"id": "compute-approval", "purpose": "Authorize the exact execution manifest, target, duration and budget."},
    {"id": "results-acceptance", "purpose": "Review complete results including failed and missing runs."},
    {"id": "claims-acceptance", "purpose": "Accept the exact independently audited claim inventory."},
    {"id": "chapter-finalization", "purpose": "Accept the exact chapter and evidence hashes."},
]


def _unique(values):
    result, seen = [], set()
    for value in values:
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key); result.append(value)
    return result


def _order(tasks, preferred):
    by_id = {task["id"]: task for task in tasks}
    rank = {task_id: index for index, task_id in enumerate(preferred)}
    pending = {task_id: set(task["dependencies"]) for task_id, task in by_id.items()}
    order = []
    while pending:
        ready = sorted((task_id for task_id, deps in pending.items() if deps <= set(order)), key=rank.get)
        if not ready:
            raise ContractError("Reduced task profile contains a dependency cycle")
        for task_id in ready:
            order.append(task_id); del pending[task_id]
    return order


def reduce_guide(source):
    """Return an auditable 38-task view without altering the imported 58-task source."""
    original = {task["id"]: task for task in source["tasks"]}
    mapped = [source_id for _, _, source_ids in TASKS.values() for source_id in source_ids]
    if len(mapped) != len(set(mapped)) or set(mapped) != set(original):
        raise ContractError("thesis-38 profile must cover every source task exactly once")
    reverse = {source_id: task_id for task_id, (_, _, source_ids) in TASKS.items() for source_id in source_ids}
    tasks = []
    execution_rank = {"DOCUMENT": 0, "CPU": 1, "GPU": 2}
    for task_id, (title, milestone_id, source_ids) in TASKS.items():
        members = [original[source_id] for source_id in source_ids]
        dependencies = []
        for member in members:
            for dependency in member["dependencies"]:
                # The source graph put all analysis behind the representative rerun.
                # In the reduced plan the rerun confirms results later in E4.
                if dependency == "eval-7" and member["id"] == "stats-1":
                    continue
                reduced_dependency = reverse[dependency]
                if reduced_dependency != task_id:
                    dependencies.append(reduced_dependency)
        if task_id == "D6":
            dependencies.extend(["D2", "D3", "D4", "D5", "D9"])
        contracts = [member["original_contract"] for member in members]
        tasks.append({
            "id": task_id,
            "title": title,
            "milestone_id": milestone_id,
            "source_task_ids": source_ids,
            "source_phase_ids": _unique([member["phase_id"] for member in members]),
            "dependencies": _unique(dependencies),
            "gates": [],
            "evidence_requirements": _unique([check for contract in contracts for check in contract["checks"]]),
            "inputs": _unique([item for contract in contracts for item in contract["inputs"]]),
            "outputs": _unique([item for contract in contracts for item in contract["files"]]),
            "steps": [{"source_task_id": member["id"], "text": step} for member in members for step in member["original_contract"]["steps"]],
            "failure_modes": [{"source_task_id": member["id"], "text": member["original_contract"]["failure"]} for member in members],
            "execution": max((member["execution"] for member in members), key=execution_rank.get),
        })
    preferred = list(TASKS)
    topological_order = _order(tasks, preferred)
    task_by_id = {task["id"]: task for task in tasks}
    source_groups = {group["id"]: group for group in source["technical_groups"]}
    milestones = []
    for milestone_id, title in MILESTONE_TITLES.items():
        task_ids = [task_id for task_id, (_, group, _) in TASKS.items() if group == milestone_id]
        source_ids = source_groups[milestone_id]["ids"]
        checks = _unique([gate for source_id in source_ids for gate in original[source_id]["gates"]])
        milestones.append({"id": milestone_id, "title": title, "task_ids": task_ids, "acceptance_checks": checks})
    result = {
        "schema_version": "1.1",
        "profile": "thesis-38",
        "source_plan_sha256": object_digest(source),
        "source_task_count": len(source["tasks"]),
        "tasks": [task_by_id[task_id] for task_id in preferred],
        "milestones": milestones,
        "human_gates": HUMAN_GATES,
        "topological_order": topological_order,
        "dependency_changes": [{
            "removed": ["eval-7", "stats-1"],
            "replacement_dependencies": ["D2", "D3", "D4", "D5", "D9"],
            "reason": "The representative rerun confirms results in E4; primary QC must follow the actual evaluation and ablation outputs.",
        }],
        "availability": source["availability"],
    }
    # Recheck after serialization-oriented construction.
    _order(result["tasks"], preferred)
    return result


def github_issue_seed(plan):
    """Create local issue drafts; this function never contacts GitHub."""
    if plan.get("profile") != "thesis-38" or len(plan.get("tasks", [])) != 38:
        raise ContractError("GitHub issue seed requires the reviewed thesis-38 plan")
    milestones = {item["id"]: item for item in plan["milestones"]}
    issues = []
    for task in plan["tasks"]:
        outputs = [item[0] if isinstance(item, list) else str(item) for item in task["outputs"]]
        body = [
            f"Source tasks: {', '.join(task['source_task_ids'])}",
            f"Depends on local tasks: {', '.join(task['dependencies']) or 'none'}",
            f"Execution class: {task['execution']}",
            "", "## Work checklist",
            *[f"- [ ] {item['text']} _(source: {item['source_task_id']})_" for item in task["steps"]],
            "", "## Evidence required",
            *[f"- [ ] {item}" for item in task["evidence_requirements"]],
            "", "## Declared outputs",
            *[f"- `{item}`" for item in outputs],
            "", "## Completion record",
            "- [ ] Link commits and pull request.",
            "- [ ] Link run IDs, manifests, checksums and failed-run evidence where applicable.",
            "- [ ] Record unresolved items; do not close on partial evidence.",
        ]
        issues.append({
            "local_task_id": task["id"],
            "title": f"[{task['id']}] {task['title']}",
            "body": "\n".join(body) + "\n",
            "milestone": milestones[task["milestone_id"]]["title"],
            "labels": ["thesis", task["milestone_id"], task["execution"].lower()],
            "dependencies": task["dependencies"],
        })
    return {
        "schema_version": "1.0",
        "source_profile": "thesis-38",
        "source_plan_sha256": object_digest(plan),
        "dry_run_only": True,
        "milestones": [{"id": item["id"], "title": item["title"]} for item in plan["milestones"]],
        "issues": issues,
        "governance": {
            "issue_per_task": True,
            "branch_pattern": "task/<issue-number>-<local-task-id>",
            "commit_reference": "Every work commit must reference the matching GitHub issue.",
            "completion": "Close only after acceptance checks and evidence links are recorded.",
            "large_artifacts": "Do not commit datasets, checkpoints or large run outputs; commit manifests, checksums and durable references.",
            "secrets": "Never commit credentials, tokens or environment files.",
            "external_mutation": "Creating issues, branches, pushes, pull requests or merges requires explicit repository scope.",
        },
    }
