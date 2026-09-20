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


# GitHub is the collaboration surface for this project.  The imported guide is
# intentionally preserved in its source language for provenance, while every
# issue generated from it uses a reviewed English operational summary.
ISSUE_ENGLISH = {
    "A1": (
        "Initialize the thesis repository, ingest the approved proposal without altering it, and extract a traceable text representation.",
        "Repository structure, proposal hashes, extracted text, tables, and equations are consistent with the approved source document.",
    ),
    "A2a": (
        "Extract the approved research questions, requirements, claims, scope boundaries, datasets, methods, and metrics into traceable records.",
        "Every approved question and requirement has a source locator; unresolved ambiguity is explicit and no new claim is introduced.",
    ),
    "A3": (
        "Specify pipeline inputs, outputs, notation, secrets, detector knowledge, protected assets, attackers, and attack success conditions.",
        "All pipeline interfaces are compatible and each security claim maps to an explicit scenario, control, and threat assumption.",
    ),
    "A2b": (
        "Map every requirement to components, datasets, baselines, metrics, experiments, controls, and planned evidence while enforcing scope-change rules.",
        "Coverage matches the complete claim inventory and planned work is not represented as implemented or experimentally verified.",
    ),
    "A4": (
        "Define measurable acceptance criteria, analysis units, sample sizes, seeds, stopping rules, failure policy, and resource bounds before experiments.",
        "Criteria are falsifiable, statistically coherent, fixed before results, and distinguish technical failure from a negative scientific result.",
    ),
    "A5": (
        "Document the end-to-end architecture, trust boundaries, data flow, ownership/key path, embedding path, detector path, and evidence outputs.",
        "The architecture is consistent with the I/O specification and threat model, and every component has defined responsibilities and interfaces.",
    ),
    "A6": (
        "Lock the reproducible software and hardware environment, dependency versions, deterministic settings, and environment-capture procedure.",
        "A clean installation can reproduce the declared environment and records the exact GPU, driver, framework, and dependency versions.",
    ),
    "B1": (
        "Run the documented literature-search protocol and build a deduplicated literature matrix, evidence ledger, and verified bibliography.",
        "Queries, dates, databases, inclusion decisions, inspected artifacts, contradictions, and citation metadata are traceable and reproducible.",
    ),
    "B2": (
        "Select defensible baselines and perform a reproducibility review of their code, data, licenses, checkpoints, metrics, and evaluation assumptions.",
        "Each selected or rejected baseline has an evidence-based rationale and no unavailable reproduction is presented as completed.",
    ),
    "B3": (
        "Create the dataset manifest, license record, provenance ledger, integrity hashes, and dataset datasheet for every planned data source.",
        "Dataset identity, version, license, acquisition path, checksum, permitted use, and known limitations are recorded.",
    ),
    "B4": (
        "Define deterministic sampling, train/validation/test separation, leakage controls, grouping rules, and an untouched out-of-distribution holdout.",
        "Split manifests are immutable, reproducible from recorded seeds, and demonstrate group separation and holdout isolation.",
    ),
    "B5": (
        "Implement versioned preprocessing with explicit image, caption, color-space, normalization, resizing, and cache rules.",
        "Preprocessing is deterministic, tested on representative inputs, and recorded by version and checksum in downstream runs.",
    ),
    "B6": (
        "Create the thesis outline and integrate the official university template, section requirements, bibliography style, and figure/table conventions.",
        "The outline covers the approved research questions and the template compiles or renders without undocumented formatting substitutions.",
    ),
    "C1": (
        "Implement validated configuration loading and immutable run logging for code, data, environment, seeds, parameters, outputs, and failures.",
        "Every run receives a unique identifier and complete manifest; invalid configurations fail before execution and failed runs remain visible.",
    ),
    "C3a": (
        "Specify and implement owner identity encoding, secret handling, key derivation, namespaces, rotation, and wrong-owner controls.",
        "The protocol separates public owner identity from secret key material and produces deterministic, domain-separated test vectors.",
    ),
    "C2": (
        "Implement the semantic-key construction from the approved feature representation with normalization and deterministic serialization.",
        "Equivalent semantic inputs meet the declared stability target while distinct controls expose collision and sensitivity behavior.",
    ),
    "C3b": (
        "Implement instance-key derivation and the reviewed fusion rule that combines owner, semantic, and instance information.",
        "Fusion is deterministic, shape-safe, domain-separated, and verified with correct-key, wrong-key, and changed-instance tests.",
    ),
    "C4": (
        "Implement the watermark embedding module with explicit strength, domain, tensor contracts, clipping, reconstruction, and logging behavior.",
        "The module preserves required shapes and ranges, produces finite outputs, and passes identity, determinism, and perturbation tests.",
    ),
    "C5": (
        "Implement the detector and perform threshold/calibration selection using validation data only, with clean and wrong-key controls.",
        "No test or holdout data influences calibration, and detector outputs, thresholds, ROC inputs, and error cases are reproducibly recorded.",
    ),
    "C6": (
        "Measure semantic and instance key stability, sensitivity, collision rates, owner separation, and failure cases across preregistered perturbations.",
        "The report includes denominators, confidence intervals where planned, collision examples, and comparison against declared acceptance criteria.",
    ),
    "C7": (
        "Implement a classical DCT watermark as a positive control using the same data, ownership protocol, attacks, and reporting conventions.",
        "The control is independently testable and its capacity, quality, and detection behavior are measured without tuning on test data.",
    ),
    "C8": (
        "Reproduce the selected reference latent-watermark baseline under pinned code, model, data, configuration, and evaluation conditions.",
        "Reproduction differences, unavailable assets, deviations, and observed metrics are fully recorded instead of silently substituted.",
    ),
    "C9": (
        "Test the latent-to-DCT bridge hypothesis with explicit transforms, controls, capacity checks, reconstruction paths, and failure diagnostics.",
        "The bridge is accepted or rejected using preregistered criteria, including quality, detectability, stability, and incompatible-domain failures.",
    ),
    "C10": (
        "Integrate the complete pipeline and run unit, contract, negative, and end-to-end smoke tests before full evaluation.",
        "All components exchange valid artifacts, failures are reproducible, smoke outputs are audited, and the technical gate decision is documented.",
    ),
    "D1": (
        "Freeze the method and preregister evaluation datasets, conditions, metrics, comparisons, exclusions, seeds, stopping rules, and analysis code.",
        "The preregistration is timestamped before result inspection and every later deviation must be labeled and justified.",
    ),
    "D2": (
        "Run paired image-quality, detection, capacity, memory, and runtime evaluation across methods using the locked samples and seeds.",
        "Pairing is preserved, denominators and failed runs are reported, and all raw metrics link to immutable manifests and artifacts.",
    ),
    "D3": (
        "Evaluate the preregistered benign transformation grid, including severity levels and asymmetric geometry where in scope.",
        "Each attack cell has complete run coverage or an explicit failure record, with quality and detection metrics at every severity.",
    ),
    "D4": (
        "Evaluate preregistered regeneration and removal attacks with controlled models, prompts, seeds, budgets, and quality constraints.",
        "Attack success is separated from unacceptable quality degradation and all model/version/query details are recorded.",
    ),
    "D5": (
        "Evaluate forgery, copy-paste, wrong-owner, wrong-key, clean, and hard-negative cases under the declared query and attribution protocol.",
        "False attribution and forgery results include the number of owners, keys, queries, negatives, and exact success criteria.",
    ),
    "D9": (
        "Run only the preregistered ablations needed to isolate semantic, instance, owner, fusion, embedding, and calibration contributions.",
        "Ablations use matched data and seeds, retain negative results, and do not expand post hoc to favor the proposed method.",
    ),
    "D6": (
        "Perform result quality control across all primary evaluation and ablation outputs, including missing runs, corruption, exclusions, and leakage checks.",
        "Every expected run is accounted for and exclusions follow preregistered rules without hiding failures or unfavorable results.",
    ),
    "D7": (
        "Compute clustered or paired bootstrap confidence intervals at the preregistered independent analysis unit.",
        "Resampling preserves pairing and clustering, uses recorded seeds, reports sample counts, and withholds invalid intervals.",
    ),
    "D8": (
        "Run the preregistered statistical comparisons, report effect sizes, and apply Holm correction to the declared hypothesis family.",
        "Assumptions, family definition, adjusted values, effect sizes, uncertainty, and exploratory deviations are reported transparently.",
    ),
    "E1": (
        "Draft the methods and experimental-protocol chapters from the frozen implementation, manifests, preregistration, and reproducibility evidence.",
        "Every technical statement links to code or evidence, notation is consistent, and unsupported details remain explicitly marked.",
    ),
    "E2": (
        "Draft the results chapter with complete tables, uncertainty, negative findings, failed runs, and representative failure figures.",
        "Narrative values match audited outputs and no table, figure, seed, condition, or comparison is selectively omitted.",
    ),
    "E3": (
        "Draft the discussion, limitations, threat-to-validity analysis, and novelty reaudit against the final evidence and literature matrix.",
        "Claims remain within the tested scope, contradictory evidence is addressed, and limitations are not rewritten as future guarantees.",
    ),
    "E4": (
        "Rerun a representative locked experiment from a clean environment and assemble the code, manifests, hashes, instructions, and evidence package.",
        "An independent user can reproduce the selected result or obtain a fully diagnosed failure using only the documented package.",
    ),
    "E5": (
        "Prepare the first-review handoff with chapter inventory, evidence links, open decisions, reproducibility status, and the academic submission checklist.",
        "The package identifies every unresolved item, passes citation and formatting checks, and does not claim final acceptance on behalf of reviewers.",
    ),
}


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
        if task["id"] not in ISSUE_ENGLISH:
            raise ContractError(f"Missing English GitHub summary for {task['id']}")
        objective, acceptance = ISSUE_ENGLISH[task["id"]]
        outputs = [item[0] if isinstance(item, list) else str(item) for item in task["outputs"]]
        body = [
            f"Source tasks: {', '.join(task['source_task_ids'])}",
            f"Depends on local tasks: {', '.join(task['dependencies']) or 'none'}",
            f"Execution class: {task['execution']}",
            "", "## Objective",
            objective,
            "", "## Work checklist",
            f"- [ ] Complete the reviewed scope summarized above for source tasks: {', '.join(task['source_task_ids'])}.",
            "- [ ] Preserve input, code, environment, decision, and output provenance for every produced artifact.",
            "- [ ] Produce every declared output below, or record a blocking reason without claiming completion.",
            "", "## Evidence required",
            f"- [ ] {acceptance}",
            "- [ ] Link the relevant manifests, checksums, tests, reviews, and negative or failed-run evidence.",
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
