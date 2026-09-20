---
name: thesis-experiment-design
description: "Preregister a falsifiable thesis experiment, evidence criteria and local versus remote compute requirements before execution."
---

# thesis-experiment-design

Use when a research question has enough documented scope to specify an experiment. If the approved proposal, data license, dataset version or code is missing, identify the blocking input and draft only the supported portion. Never invent method details or optimize the plan for a desired outcome.

Write the experiment contract before observing results: falsifiable hypothesis, primary/secondary outcomes, dataset identity/version/license/splits, leakage risks, preprocessing, baselines, controls, ablations, independent seeds, stopping rule and minimum evidence for acceptance/rejection. Declare the unit of analysis, planned statistical comparison, exclusions and negative-result policy. Existing results make the analysis exploratory, not retrospectively preregistered.

Create the execution contract referencing a reviewed version-controlled Python entrypoint and SHA-256, exact Git commit, input hashes, seeds, expected outputs, metrics, resources, duration and cost limits. Script arguments are fixed: `--manifest` and `--output-dir`; arbitrary command strings are prohibited. Estimate RAM, disk, runtime and total hourly cost including storage/egress. Never present estimates as current quotes.

Default safe local VRAM is 10,240 MiB; use lower measured free availability minus headroom when appropriate. Approximately 32 GB system RAM does not imply all is free. Explain the local/remote choice and confirm actual availability before execution. Target changes invalidate scoped approval.

Run the design helper on JSON documents (valid YAML 1.2) to validate and package the preregistration. Remote spending requires a matching human approval artifact. Live RunPod creation is currently blocked because upstream deadlines are not enforced; read the compute runner provider limitation before recommending executable remote work.

Authorization: design is not execution approval. Do not generate a human decision.

## Input/output contract

Inputs must match the strict JSON schemas in `scripts/_runtime/thesis_agents/schemas` after installation, or the bundle's `src/thesis_agents/schemas` during development. experiments/<id>/{experiment-spec.yaml,plan.md,acceptance-criteria.md,compute-estimate.json,execution-manifest.json}.

Use `python scripts/design_experiment.py --help` for the actual argument contract. Errors return nonzero JSON diagnostics. Do not infer success from artifact filenames alone.
