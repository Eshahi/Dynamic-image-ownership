# Dynamic Image Ownership

This repository contains the reproducible research harness and execution plan for a thesis on dynamic image ownership and watermarking.

## Current status

- The thesis workflow has been reduced from 58 source tasks to 38 traceable execution issues.
- Five milestones and seven human-review gates define the delivery lifecycle.
- Eight reusable agent skills cover workflow control, research handoff, literature synthesis, experiment design, compute execution, results analysis, evidence audit, and thesis writing.
- Local and mock-provider execution are implemented and tested.
- Live RunPod creation remains disabled until an enforceable time and spending boundary is validated.
- Codex Remote is the human interaction channel for progress notifications, review, and explicit
  gate decisions; no project-specific messaging bot or gateway is required.

## Repository policy

GitHub-facing project management content is written in English. The original offline guide remains unchanged as a provenance artifact. Work must be linked to its GitHub issue through the branch name, commits, pull request, manifests, and evidence records.

Never commit credentials, API keys, environment files, raw private tokens, large datasets, model checkpoints, or large run outputs. Store manifests, checksums, and durable artifact references instead.

## Execution plan

The reviewed execution profile contains five milestones:

1. Specification
2. Data & Literature
3. Implementation
4. Evaluation & Statistics
5. First Review

The deterministic issue seed is stored at `thesis-agent-skills/fixtures/github-issue-seed-38.json`. The immutable source-to-task mapping is stored at `thesis-agent-skills/fixtures/guide-plan-38.json`.

## Local setup

See `thesis-agent-skills/INSTALL.md` for environment preparation, skill installation, Spec Kit workflow installation, Codex Remote requirements, and the synthetic smoke test.

## Scientific status

The repository provides infrastructure and a research plan. It does not, by itself, prove the proposed method, validate a scientific claim, or constitute university approval.
