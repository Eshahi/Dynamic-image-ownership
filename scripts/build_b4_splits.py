"""Build explicit source-image quotas and observed-group counts, never fake N."""
import argparse
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data.splits import allocate, grouped_frame
from b4_metadata_dependence import MANIFEST_SHA, DEV_SHA, bound

META_BRIDGE_SHA="e54e3e4a82d7938ffbd2f6d9c77aaec0b6126dc983be19f2ae8218152a6d3d23"
CANONICAL_SUMMARY_SHA="924f7d43f8c5dd817d48dc1749afac7832618b451b3b0b418383c1d89cd64a3b"
ADMISSION_SHA="d8240a0ee0b6920727f743b485933a9d919d5ae224309dd9c7c8e334aeab1f6e"


def sha(raw): return hashlib.sha256(raw).hexdigest()
def json_output(path,value):
    with path.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(value,handle,sort_keys=True,indent=2,allow_nan=False);handle.write("\n")


def coverage_join(row, observed):
    if observed["raw_sha256"] != row["raw_sha256"]:
        raise ValueError("selected raw identity mismatch")
    status=observed["status"]
    if status not in ("canonical_pass", "canonical_rejected_coverage_failure"):
        raise ValueError("unknown canonical coverage status")
    if status=="canonical_pass" and not observed.get("canonical_pixel_sha256"):
        raise ValueError("missing passed canonical identity")
    if status!="canonical_pass" and (not observed.get("reason") or observed.get("canonical_pixel_sha256")):
        raise ValueError("invalid rejected canonical evidence")
    return {"id":row["domain"]+":"+row["source_id"],
            "source_uid":":".join(row[k] for k in ("domain","release_id","source_split","source_id")),
            **{k:row[k] for k in ("domain","release_id","source_split","source_id","raw_sha256")},
            "canonical_pixel_sha256":observed.get("canonical_pixel_sha256", ""),
            "canonical_status":status,"canonical_rejection_reason":observed.get("reason", ""),
            "independence_certified":False}


def run(manifest_path,dev_path,metadata_path,canonical_path,canonical_summary,config_path,output_root,admission_path=None):
    names=("splits.csv","sample-size-check.json","holdout.json","b4-observed-group-summary.json")
    if any((output_root/name).exists() for name in names):
        raise ValueError("existing outputs retained; choose fresh exact output directory")
    admission=json.loads(bound(admission_path,ADMISSION_SHA,64*1024)) if admission_path else None
    manifest_pin=admission["manifest_sha256"] if admission else MANIFEST_SHA
    dev_pin=admission["development_reservation_sha256"] if admission else DEV_SHA
    manifest_raw=bound(manifest_path,manifest_pin,8*1024*1024)
    dev_raw=bound(dev_path,dev_pin,64*1024)
    if admission:
        if admission["original_manifest_sha256"]!=MANIFEST_SHA or admission["original_dev_sha256"]!=DEV_SHA:
            raise ValueError("admission historical input mismatch")
        original_dev=json.loads(bound(Path(__file__).resolve().parents[1]/"data/dev-ids.json",DEV_SHA,64*1024))
        if json.loads(dev_raw)["images"]!=original_dev["images"]:
            raise ValueError("admitted development identities were reranked")
    bridge=json.loads(bound(metadata_path,META_BRIDGE_SHA,16*1024*1024))
    summary_raw=bound(canonical_summary,CANONICAL_SUMMARY_SHA,64*1024)
    summary=json.loads(summary_raw)
    canonical_raw=bound(canonical_path,summary["output_sha256"],32*1024*1024)
    canonical=[json.loads(line) for line in canonical_raw.splitlines()]
    if len(canonical)!=19900 or len({r["id"] for r in canonical})!=19900:
        raise ValueError("full canonical frame cardinality mismatch")
    if Counter(r["id"].split(":",1)[0] for r in canonical)!={"ms-coco":5000,"div2k":900,"diffusiondb":14000}:
        raise ValueError("canonical source frames mismatch")
    config_raw=config_path.read_bytes();config=json.loads(config_raw)
    if config["manifest_sha256"]!=manifest_pin or config["development_ids_sha256"]!=dev_pin:
        raise ValueError("split configuration input mismatch")
    if config.get("final_scientific_split_accepted") is not False or config.get("scientific_compute_authorized") is not False:
        raise ValueError("engineering builder cannot certify a scientific freeze or compute")
    manifest=list(csv.DictReader(io.StringIO(manifest_raw.decode())))
    selected=[]; canonical_index={r["id"]:r for r in canonical}
    for row in manifest:
        uid=row["domain"]+":"+row["source_id"]
        observed=canonical_index[uid]
        joined=coverage_join(row,observed)
        if admission and joined["canonical_status"]!="canonical_pass":
            raise ValueError("admitted selected source failed canonical eligibility")
        selected.append(joined)
    if Counter(r["domain"] for r in selected)!={"ms-coco":1000,"div2k":900,"diffusiondb":5000}:
        raise ValueError("selected source counts changed")
    reserved={r["domain"]+":"+r["source_id"] for r in json.loads(dev_raw)["images"]}
    groups,edges=grouped_frame(canonical,bridge["private_nodes"],config["grouping"])
    rows=allocate(groups,selected,reserved,config)
    by_group=defaultdict(list)
    for row in rows: by_group[row["group_id"]].append(row)
    if any(len({r["study_split"] for r in values})!=1 for values in by_group.values()):
        raise ValueError("connected group leaked across splits")
    fields=("source_uid","domain","release_id","source_split","source_id","raw_sha256",
            "canonical_pixel_sha256","canonical_status","canonical_rejection_reason","independence_certified",
            "group_id","study_split","primary_group_representative")
    native_holdout=[r for r in rows if r["domain"]=="div2k" and r["source_split"]=="valid"]
    if len(native_holdout)!=100 or any(r["study_split"]!="test" for r in native_holdout):
        raise ValueError("native holdout invariant failed")
    # Everything is computed/checked before any declared artifact is written.
    output_root.mkdir(parents=True,exist_ok=True)
    with (output_root/"splits.csv").open("x",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator="\n");writer.writeheader()
        for row in rows: writer.writerow({k:(str(row[k]).lower() if isinstance(row[k],bool) else row[k]) for k in fields})
    split_sha=sha((output_root/"splits.csv").read_bytes())
    inputs={"manifest_sha256":manifest_pin,"dev_ids_sha256":dev_pin,"private_metadata_bridge_sha256":META_BRIDGE_SHA,
            "private_canonical_sha256":summary["output_sha256"],"canonical_summary_sha256":sha(summary_raw),
            "config_file_sha256":sha(config_raw),"split_module_sha256":sha(Path("src/data/splits.py").read_bytes()),
            "builder_code_sha256":sha(Path(__file__).read_bytes()),"splits_sha256":split_sha}
    if admission:
        inputs.update(admission_sha256=ADMISSION_SHA,
                      statistical_plan_sha256=sha((Path(__file__).resolve().parents[1]/"research/sample-size.md").read_bytes()),
                      acceptance_plan_sha256=sha((Path(__file__).resolve().parents[1]/"research/acceptance.md").read_bytes()),
                      immutable_task_plan_sha256=sha((Path(__file__).resolve().parents[1]/"thesis-runs/d916749c/guide-plan-38.json").read_bytes()))
    z=NormalDist().inv_cdf(.975);cells=[]
    for domain in ("ms-coco","div2k","diffusiondb"):
        for split in ("development","validation","test"):
            pool=[r for r in rows if r["domain"]==domain and r["study_split"]==split]
            n=len({r["group_id"] for r in pool})
            unresolved={r["group_id"] for r in pool if r["canonical_status"]!="canonical_pass"}
            candidate_n=n-len(unresolved)
            cells.append({"domain":domain,"split":split,"images":len(pool),"observed_groups":n,
                          "canonical_screened_candidate_groups_not_certified_independent":candidate_n,
                          "unresolved_canonical_groups":len(unresolved),
                          "canonical_rejected_images":sum(r["canonical_status"]!="canonical_pass" for r in pool),
                          "nominal_a4_independent_group_target":config["allocation"][domain][split],
                          "independent_target_shortfall":config["allocation"][domain][split]-candidate_n,
                          "hypothetical_zero_fp_upper95_if_candidate_groups_eligible_independent":
                              -math.expm1(math.log(.05)/candidate_n) if candidate_n else None,
                          "wilson95_halfwidth_p05_if_candidate_groups_eligible_independent":
                              z/(2*math.sqrt(candidate_n+z*z)) if candidate_n else None,
                          "zero_fp_1pct_resolution_if_candidate_groups_eligible_independent":candidate_n>=299})
    class_cells=[{"domain":c["domain"],"split":c["split"],"class":label,
                  "planned_n":c["nominal_a4_independent_group_target"],
                  "actual_independent_n_under_declared_group_assumption":c["canonical_screened_candidate_groups_not_certified_independent"],
                  "row_count":c["images"],"status":"conditional_actual_N_shortfall" if c["independent_target_shortfall"] else "conditional_actual_N_matches_plan",
                  "observed_outcome_count":0,"paired_with_other_classes":True}
                 for c in cells for label in ("C1_positive","C0_source_negative","C0_reconstruction_negative","C2_wrong_owner_negative")]
    json_output(output_root/"sample-size-check.json",{
        "status":"locked_pre_outcome_engineering_data_plan_pending_review" if admission else "BLOCKED_DECISION_provisional_engineering_allocation_not_scientific_freeze","inputs":inputs,
        "source_image_total":len(rows),"observed_selected_groups":len(by_group),"cells":cells,
        "unit_rule":"one_prospective_representative_per_domain_component_for_group_based_inference_others_retained_for_coverage",
        "independence_assumption":"finite_observed_screen_only_unobserved_links_and_rights_can_invalidate_eligibility",
        "planned_independent_counts_met":all(c["independent_target_shortfall"]==0 for c in cells),
        "class_cells":class_cells,"class_counts_are_prospective_not_observed_results":True,
        "shortfalls":[c for c in class_cells if c["planned_n"]>c["actual_independent_n_under_declared_group_assumption"]],
        "engineering_split_locked":bool(admission),
        "final_scientific_split_accepted":False,
        "blockers":[] if admission else ["canonical_rejects_leave_unresolved_cross_split_links_and_eligibility",
                    "nominal_independent_group_counts_not_proven","new_domain_ood_not_established"],
        "confirmatory_execution_prerequisites":["reviewed_method_conformance_and_calibration",
                    "exact_manifest_user_compute_approval","separate_future_pair_attack_protocols"],
        "scientific_compute_authorized":False})
    holdout_groups={r["group_id"] for r in native_holdout}
    linked=[r["source_uid"] for r in rows if r["group_id"] in holdout_groups]
    json_output(output_root/"holdout.json",{
        "status":"locked_source_partition_holdout_not_new_domain_ood" if admission else "provisional_engineering_source_partition_holdout_not_scientific_freeze","inputs":inputs,
        "required":False,"claim_ids":["SCOPE-02","GOAL-01","METHOD-01","DATA-01","DATA-02","DATA-03"],
        "cross_model_domain":None,"cross_model_ids":[],
        "reason_if_not_required":"immutable_B4_data3_is_claim_dependent_current_scope_requires_same_method_three_source_strata_not_unseen_checkpoint_generalization",
        "source_partition_holdout_required":True,
        "declared_source_ids":[r["source_uid"] for r in native_holdout],"source_image_count":100,
        "observed_group_count":len(holdout_groups),"linked_test_only_source_ids":linked,
        "no_fit_or_calibration_use":True,"never_used_for_method_outcomes":True,
        "byte_reads_before_lock":"native_integrity_canonical_and_leakage_grouping_only_no_model_scores",
        "distribution_shift_evidence":"source_partition_designation_only_actual_ood_not_established",
        "final_scientific_split_accepted":False,
        "raw_redistribution_or_figure_permission":False,"scientific_compute_authorized":False})
    json_output(output_root/"b4-observed-group-summary.json",{
        "status":"locked_operational_graph_not_population_independence_proof" if admission else "provisional_observed_groups_not_scientific_split_acceptance","inputs":inputs,
        "observed_frame_images":19900,"observed_frame_components":len(groups),"selected_images":6900,
        "selected_components":len(by_group),"observed_edge_counts":edges,
        "cross_split_connected_group_count":0,"full_reserved_development_components_kept":True,
        "nominal_source_image_quotas_met":True,"canonical_frame_failure_count":summary["counts"].get("canonical_rejected_coverage_failure",0),
        "selected_canonical_failure_count":sum(r["canonical_status"]!="canonical_pass" for r in rows),
        "ineligible_observed_source_nodes":summary["coverage_failures"],
        "graph_boundary":"canonical_near_edges_defined_only_for_passing_nodes_raw_edges_retain_rejected_nodes_all_diffusion_metadata_bridges_retained",
        "residual_dependence_not_ruled_out":True,"engineering_split_locked":bool(admission),
        "final_scientific_split_accepted":False,
        "source_content_rights_reviewed":False,"scientific_compute":False})
    print(json.dumps({"splits_sha256":split_sha,"selected_images":6900,"selected_components":len(by_group),
                      "edge_counts":edges,"cells":cells},sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","dev","metadata","canonical","canonical-summary","config","output-root"):
        parser.add_argument("--"+name,required=True,type=Path)
    parser.add_argument("--admission",type=Path)
    args=parser.parse_args()
    run(args.manifest,args.dev,args.metadata,args.canonical,args.canonical_summary,args.config,args.output_root,args.admission)
