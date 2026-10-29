"""Stage P metadata planning and selection CLI; standard library only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import tifs_common as common
import tifs_stage_p as p


def read_config(root, partition, trial):
    path = root / partition / trial / "config.json"
    return path, common.load_json(path)


def summary(args, trial, n, partition="tune"):
    path, config = read_config(args.run_root, partition, trial)
    expected = p.materialize(args.base_config, args.source_manifest, args.user_choice,
                             trial, partition, load_nomination(args) if partition == "check" else None)
    if config != expected:
        raise ValueError("Materialized configuration changed after planning")
    required = [path.parent / name for name in ("identity.json", "prepared.json")]
    absent = [str(pth) for pth in required if not pth.exists()]
    if absent:
        rows = p.active_sources(config,n)
        return dict(configuration_id=trial, parameters=config["stage_p"]["parameters"],
            parameter_sha256=config["stage_p"]["parameter_sha256"], partition=partition,
            sources=[str(r["source_id"]) for r in rows], source_uids=[r["source_uid"] for r in rows],
            status="RESOURCE_STOP" if list(path.parent.glob("RESOURCE_STOP*.json")) else "INCOMPLETE",
            rejection_reasons=[], missing=absent, clean_metrics={}, counts={}, clean_F=0, pairing={},
            evidence_sha256=p.digest(dict(absent=absent)), evidence_files={},
            compute=dict(attempts=0, seconds=0., unresolved_inventory=True))
    return p.summarize_trial(path.parent, config, count=n)


def bindings(args):
    return dict(base_config_sha256=common.sha256_file(args.base_config),
        source_manifest_sha256=common.sha256_file(args.source_manifest),
        protocol_sha256=common.sha256_file(p.HERE / "PROTOCOL.md"),
        search_config_sha256=common.sha256_file(p.HERE / "search-config.json"),
        user_choice_sha256=common.sha256_file(args.user_choice))


def record_path(args, n):
    return args.run_root / "selection" / f"rung-{n}.json"


def verify_prior(args, n):
    record = common.load_json(record_path(args, n))
    if any(record.get(k) != v for k, v in bindings(args).items()) or record["status"] != "ADVANCE":
        raise ValueError("Prior rung did not advance under this frozen plan")
    for trial in record["entrants"]:
        if summary(args, trial, n)["evidence_sha256"] != record["candidate_evidence"][trial]:
            raise ValueError("Previously selected tuning evidence changed")
    if summary(args, "retained-f5", n)["evidence_sha256"] != record["retained_evidence"]:
        raise ValueError("Previously selected retained-control evidence changed")
    for budget, expected in record["budget_evidence"].items():
        if summary(args, "f5-budget-p" + str(budget), n)["evidence_sha256"] != expected:
            raise ValueError("Previously selected budget-control evidence changed")
    return record


def entrants(args, n):
    if n == 4:
        return list(p.CANDIDATES)
    if n not in (8, 16):
        raise ValueError("Unknown tuning rung")
    # Check every preceding selection, not just the last promotion.
    first = verify_prior(args, 4)
    if n == 8:
        return first["survivors"]
    second = verify_prior(args, 8)
    if second["entrants"] != first["survivors"]:
        raise ValueError("Rung ancestry changed")
    return second["survivors"]


def load_nomination(args):
    nomination = common.load_json(args.run_root / "selection/nomination.json")
    third = verify_prior(args, 16)
    if (third["survivors"] != [nomination.get("candidate_id")]
            or nomination.get("tuning_progression_sha256") != p.digest(third)
            or nomination.get("full_tuning_config_sha256") != common.sha256_file(args.run_root / "tune" / nomination["candidate_id"] / "config.json")
            or any(nomination.get(k) != v for k, v in bindings(args).items())):
        raise ValueError("Nomination no longer binds successful tuning progression")
    return nomination


def plan(args):
    # Only metadata is read: not a single check original is opened here.
    for trial in [*p.CANDIDATES, "retained-f5"]:
        config = p.materialize(args.base_config, args.source_manifest, args.user_choice, trial)
        p.immutable_json(args.run_root / "tune" / trial / "config.json", config)
    p.immutable_json(args.run_root / "selection/search-plan.json", dict(schema="tifs-stage-p-plan-v1",
        **bindings(args), candidates=list(p.CANDIDATES), execution_authorized=False))


def finalist_controls(args):
    ids = entrants(args, 16)
    budgets = sorted({p.trial_parameters(i)["writer_psnr_db"] for i in ids}, reverse=True)
    for budget in budgets:
        trial = "f5-budget-p" + str(budget)
        config = p.materialize(args.base_config, args.source_manifest, args.user_choice, trial)
        p.immutable_json(args.run_root / "tune" / trial / "config.json", config)
    return ["f5-budget-p" + str(b) for b in budgets]


def advance(args):
    ids = entrants(args, args.count)
    summaries = {i: summary(args, i, args.count) for i in ids}
    retained = summary(args, "retained-f5", args.count)
    budgets = {}
    if args.count == 16:
        budgets = {p.trial_parameters(i)["writer_psnr_db"]: summary(args, i, 16) for i in finalist_controls(args)}
    profile = common.load_json(args.user_choice)["gate_profile"]
    result = p.select_rung(summaries, retained, budgets, args.count, profile, ids)
    result.update(bindings(args))
    # Preserve every current summary, including failed and incomplete candidates.
    common.atomic_json(args.run_root / "selection" / f"rung-{args.count}-inventory.json", dict(
        summaries=summaries, retained=retained, budget_controls=budgets))
    common.atomic_json(args.run_root / "selection" / f"rung-{args.count}-latest.json", result)
    if result["status"] == "ADVANCE":
        p.immutable_json(record_path(args, args.count), result)
        if args.count == 16:
            winner = result["survivors"][0]
            path = args.run_root / "selection/nomination.json"
            nomination = dict(schema="tifs-stage-p-nomination-v1", status="NOMINATED", candidate_id=winner,
                **bindings(args), gate_profile=profile, parameter_sha256=summaries[winner]["parameter_sha256"],
                full_tuning_config_sha256=common.sha256_file(args.run_root / "tune" / winner / "config.json"),
                writer_overrides=p.trial_parameters(winner), tuning_progression_sha256=p.digest(result),
                tuning_row_sha256=summaries[winner]["evidence_sha256"], nomination_time_utc=p.utcnow(),
                check_not_yet_read=True, execution_authorized=False)
            if path.exists():
                nomination["nomination_time_utc"] = common.load_json(path)["nomination_time_utc"]
            p.immutable_json(path, nomination)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "ADVANCE" else 3 if result["status"] == "RESOURCE_STOP" else 4 if result["status"] == "INCOMPLETE" else 2


def plan_check(args):
    nomination = load_nomination(args)
    winner = nomination["candidate_id"]
    budget = p.trial_parameters(winner)["writer_psnr_db"]
    ids = [winner, "retained-f5", "f5-budget-p" + str(budget)]
    for trial in ids:
        config = p.materialize(args.base_config, args.source_manifest, args.user_choice, trial, "check", nomination)
        p.immutable_json(args.run_root / "check" / trial / "config.json", config)
    return ids


def finish(args):
    nomination = load_nomination(args)
    winner = nomination["candidate_id"]
    budget_id = "f5-budget-p" + str(p.trial_parameters(winner)["writer_psnr_db"])
    candidate = summary(args, winner, 8, "check")
    retained = summary(args, "retained-f5", 8, "check")
    budget = summary(args, budget_id, 8, "check")
    check = p.check_winner(candidate, retained, budget, nomination["gate_profile"])
    inventory = dict(candidate=candidate, retained=retained, budget=budget)
    common.atomic_json(args.run_root / "selection/check-inventory.json", inventory)
    result = dict(schema="tifs-stage-p-selection-v1", status="SELECTED" if check["check_status"] == "PASS" else check["check_status"],
        **bindings(args), gate_profile=nomination["gate_profile"], check_status=check["check_status"],
        selected_candidate_id=winner, candidate=p.trial_parameters(winner)["candidate"],
        writer_psnr_db=p.trial_parameters(winner)["writer_psnr_db"], writer_overrides=dict(psnr_db=p.trial_parameters(winner)["writer_psnr_db"], refine_psnr_db=58),
        full_writer_config=read_config(args.run_root,"tune",winner)[1]["writer"],
        k3_optimization="excluded", nomination=nomination, nomination_sha256=p.digest(nomination),
        check=check, check_evidence_sha256=p.digest(inventory),
        check_source_uids=candidate["source_uids"], tune_source_uids=[r["source_uid"] for r in p.load_manifest(args.source_manifest)["tune_sources"]],
        planned_candidate_ids=list(p.CANDIDATES), attempted_candidate_ids=[], rungs=[],
        execution_authorized=False, stage_s_eligibility="ELIGIBLE_FOR_PROPOSAL" if check["check_status"] == "PASS" else "BLOCKED")
    for n in (4, 8, 16):
        rung = verify_prior(args, n)
        details = common.load_json(args.run_root / "selection" / f"rung-{n}-inventory.json")
        result["rungs"].append(dict(progression=rung, inventory=details))
        for trial in rung["entrants"]:
            if trial not in result["attempted_candidate_ids"] and details["summaries"][trial]["compute"]["attempts"]:
                result["attempted_candidate_ids"].append(trial)
    result["number_attempted"] = len(result["attempted_candidate_ids"])
    # Actual work is counted once per directory, not once per cumulative rung.
    actual = {}
    for partition in ("tune", "check"):
        for config_path in sorted((args.run_root / partition).glob("*/config.json")):
            config = common.load_json(config_path)
            if (config_path.parent / "identity.json").exists():
                actual[str(config_path.parent)] = p.summarize_trial(config_path.parent, config)["compute"]
    result["actual_compute_by_directory"] = actual
    common.atomic_json(args.run_root / "selection/final-result.json", result)
    if check["check_status"] == "PASS":
        p.immutable_json(args.destination, result)
    elif Path(args.destination).exists():
        raise ValueError("Existing selected-config conflicts with failed check; never overwrite or fall back")
    print(json.dumps(dict(status=result["status"], check_status=result["check_status"], stage_s_eligibility=result["stage_s_eligibility"])))
    return 0 if check["check_status"] == "PASS" else 3 if check["check_status"] == "RESOURCE_STOP" else 4 if check["check_status"] == "INCOMPLETE" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "calibration", "entrants", "finalist-controls", "advance", "plan-check", "finish"))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--base-config", type=Path, default=p.BASE)
    parser.add_argument("--source-manifest", type=Path, default=p.HERE / "source-manifest.json")
    parser.add_argument("--user-choice", type=Path, required=True)
    parser.add_argument("--count", type=int, choices=(4, 8, 16))
    parser.add_argument("--destination", type=Path, default=p.HERE / "selected-config.json")
    args = parser.parse_args()
    args.run_root = args.run_root.resolve()
    # Enforce an external prospective receipt for every command, including reads.
    p.materialize(args.base_config, args.source_manifest, args.user_choice, p.CANDIDATES[0])
    if args.command in ("entrants", "advance") and args.count is None:
        parser.error("--count is required for a tuning rung")
    if args.command == "plan":
        plan(args)
    elif args.command == "calibration":
        print("\n".join(("retained-f5", "f6-noise-p52", "f6-x0-p52")))
    elif args.command == "entrants":
        print("\n".join(entrants(args, args.count)))
    elif args.command == "finalist-controls":
        print("\n".join(finalist_controls(args)))
    elif args.command == "advance":
        return advance(args)
    elif args.command == "plan-check":
        print("\n".join(plan_check(args)))
    elif args.command == "finish":
        return finish(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
