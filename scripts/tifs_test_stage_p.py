"""Pure-logic tests. Synthetic JSON and opaque byte artifacts only; no science."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import tifs_common as common
import tifs_stage_p as p
import tifs_stage_p_select as select


def synthetic_summary(candidate="f6-noise-p52", n=16, counts=16, partition="tune"):
    sources = [str(i) for i in range(n)]
    return dict(configuration_id=candidate, sources=sources, source_uids=sources, partition=partition,
        parameters=p.trial_parameters(candidate), parameter_sha256=p.digest(p.trial_parameters(candidate)),
        status="COMPLETE", missing=[], rejection_reasons=[], clean_F=n,
        counts={c: {r: dict(lower=counts, upper=counts) for r in ("C", "J")} for c in p.CELLS},
        clean_metrics={s: dict(psnr_db=45, ssim_rgb=.96, lpips=.02) for s in sources},
        pairing=dict(sources=sources, tapes="fixed", owners="fixed", cells=list(p.CELLS), seeds=[0,1,2]),
        evidence_sha256="a" * 64, compute=dict(attempts=1))


class StagePLogic(unittest.TestCase):
    def test_frozen_manifest_and_prefix(self):
        manifest = p.load_manifest(p.HERE / "source-manifest.json")
        self.assertEqual([r["source_id"] for r in manifest["tune_sources"][:4]], [544,1355,902,599])
        config = dict(stage_p=dict(partition="tune", sources=manifest["tune_sources"]))
        before = p.digest(config)
        for n in (4,8,16):
            self.assertEqual(len(p.active_sources(config,n)),n)
        self.assertEqual(p.digest(config),before)
        with self.assertRaises(ValueError): p.active_sources(config,5)
        config["stage_p"]["configuration_id"]="f6-noise-p52"
        self.assertEqual(len(p.active_sources(config,2,calibration=True)),2)
        with self.assertRaises(ValueError): p.active_sources(config,2)
        config["stage_p"]["configuration_id"]="f6-noise-p46"
        with self.assertRaises(ValueError): p.active_sources(config,2,calibration=True)
        config["stage_p"]["partition"] = "check"
        with self.assertRaises(ValueError): p.active_sources(config,8)

    def test_materialization_full_identity_no_check_without_nomination(self):
        receipt = dict(schema="tifs-round3-user-choice-v1", decision="approve", recorded_by="Claude",
            config_sha256=common.sha256_file(p.BASE), gate_profile="round1", stage_p="run",
            k3_optimization="excluded", before_server_outputs=True, user_decision_reference="TEST FIXTURE ONLY",
            max_instance_hours=15)
        real_load, real_sha = common.load_json, common.sha256_file
        fixture = Path("nonexistent-test-only-choice.json")
        with patch.object(common,"load_json", side_effect=lambda path: receipt if Path(path)==fixture else real_load(path)), \
             patch.object(common,"sha256_file", side_effect=lambda path: "e"*64 if Path(path)==fixture else real_sha(path)):
            config = p.materialize(p.BASE,p.HERE / "source-manifest.json",fixture,"f6-x0-p38")
            self.assertEqual(config["arms"],["f6-x0","unmarked"])
            self.assertEqual(config["writer"]["psnr_db"],38)
            self.assertEqual(config["writer"]["refine_psnr_db"],58)
            self.assertEqual(len(config["stage_p"]["sources"]),16)
            before = p.digest(config)
            p.active_sources(config,4)
            self.assertEqual(p.digest(config),before)
            with self.assertRaises(ValueError):
                p.materialize(p.BASE,p.HERE / "source-manifest.json",fixture,"f6-x0-p38","check")

    def test_search_and_ranking_literal_tie_break(self):
        self.assertEqual(len(p.CANDIDATES),8)
        summaries = {i: synthetic_summary(i,4) for i in p.CANDIDATES}
        retained = synthetic_summary(n=4)
        result = p.select_rung(summaries,retained,{},4,"round1",list(p.CANDIDATES))
        self.assertEqual(result["survivors"],sorted(p.CANDIDATES)[:4])
        # J is a separate endpoint; owner-only C cannot win this ordering.
        summaries[p.CANDIDATES[0]]["counts"]["K3-0.2"]["J"].update(lower=0,upper=0)
        result = p.select_rung(summaries,retained,{},4,"round1",list(p.CANDIDATES))
        self.assertNotIn(p.CANDIDATES[0],result["survivors"])

    def test_missing_candidate_cannot_be_ranked_away(self):
        ids=list(p.CANDIDATES)
        summaries={i:synthetic_summary(i,4) for i in ids}
        summaries[ids[-1]].update(status="INCOMPLETE",missing=["one seed"])
        summaries[ids[-1]]["pairing"]["tapes"]="missing native tape"
        result=p.select_rung(summaries,synthetic_summary(n=4),{},4,"round1",ids)
        self.assertEqual(result["status"],"INCOMPLETE")
        self.assertEqual(result["survivors"],[])
        summaries[ids[-1]].update(status="REJECTED", rejection_reasons=["observed forbidden event"])
        self.assertEqual(p.select_rung(summaries,synthetic_summary(n=4),{},4,"round1",ids)["status"],"ADVANCE")

    def test_round1_parity_no_profile_rescue(self):
        candidate=synthetic_summary(n=16)
        retained=synthetic_summary(n=16,counts=8)
        budget=copy.deepcopy(retained)
        for v in retained["clean_metrics"].values(): v["lpips"]=.001
        self.assertEqual(p.eligibility(candidate,retained,budget,16,"round1",True)["status"],"REJECTED")
        self.assertEqual(p.eligibility(candidate,retained,budget,16,"round3-proposed",True)["status"],"ELIGIBLE")
        self.assertEqual(p.eligibility(candidate,retained,None,16,"round1",True)["status"],"INCOMPLETE")

    def test_rung3_and_check_futility_no_fallback(self):
        candidate=synthetic_summary(counts=11)
        controls=synthetic_summary(counts=10)
        result=p.select_rung({p.CANDIDATES[0]:candidate},controls,{52:controls},16,"round1",[p.CANDIDATES[0]])
        self.assertEqual(result["status"],"SCIENTIFIC_STOP")
        self.assertEqual(result["survivors"],[])
        self.assertEqual(result["futility"],"BELOW_SCREEN_BAR")
        check=synthetic_summary(n=8,counts=5,partition="check")
        baseline=synthetic_summary(n=8,counts=4,partition="check")
        self.assertEqual(p.check_winner(check,baseline,baseline,"round1")["check_status"],"FAIL")
        check["counts"]={c:{r:dict(lower=6,upper=6) for r in ("C","J")} for c in p.CELLS}
        self.assertEqual(p.check_winner(check,baseline,baseline,"round1")["check_status"],"PASS")

    def test_proposed_gains_scaled_prospectively(self):
        check=synthetic_summary(n=8,counts=6,partition="check")
        baseline=synthetic_summary(n=8,counts=4,partition="check")
        self.assertEqual(p.check_winner(check,baseline,baseline,"round3-proposed")["check_status"],"PASS")
        baseline["counts"]["K3-0.2"]["J"].update(lower=5,upper=5)
        self.assertEqual(p.check_winner(check,baseline,baseline,"round3-proposed")["check_status"],"FAIL")

    def test_comparator_requires_source_and_random_tape_identity(self):
        candidate=synthetic_summary()
        baseline=synthetic_summary()
        baseline["pairing"]["tapes"]="different"
        with self.assertRaises(ValueError): p.comparison(candidate,baseline)

    def test_proposed_budget_absolute_gate_does_not_change_round1(self):
        candidate=synthetic_summary()
        baseline=synthetic_summary(counts=8)
        budget=synthetic_summary(counts=8)
        budget["control_diagnostics"]=["strict_quality:0"]
        self.assertEqual(p.eligibility(candidate,baseline,budget,16,"round1",True)["status"],"ELIGIBLE")
        self.assertEqual(p.eligibility(candidate,baseline,budget,16,"round3-proposed",True)["status"],"REJECTED")


def journal_fixture(root, count=4):
    manifest=p.load_manifest(p.HERE / "source-manifest.json")
    rows=manifest["tune_sources"]
    arm="f6-noise"
    config=dict(candidate=arm, arms=[arm,"unmarked"], cells=[dict(id=c) for c in p.CELLS], seeds=[0,1,2],
        owners=dict(positive="alpha",wrong="beta"), stage_p=dict(configuration_id="f6-noise-p52", partition="tune",
            sources=rows, parameters=p.trial_parameters("f6-noise-p52"),parameter_sha256=p.digest(p.trial_parameters("f6-noise-p52")),
            source_manifest_sha256=common.sha256_file(p.HERE / "source-manifest.json")))
    common.atomic_json(root/"config.json",config)
    common.atomic_json(root/"identity.json",dict(config_sha256=common.sha256_file(root/"config.json"),source_manifest_sha256=config["stage_p"]["source_manifest_sha256"],profiles={"fixture-profile":"b"*64},code={"fixture-code":"c"*64}))
    common.atomic_json(root/"prepared.json",dict(donors=[str(r["source_id"]) for r in rows],targets=[],sources={str(r["source_id"]):r for r in rows}))
    # Opaque bytes exercise artifact validation without producing any image.
    artifact=root/"opaque.bin"
    artifact.write_bytes(b"pure logic test; this is not image data")
    output=dict(path=str(artifact),sha256=common.sha256_file(artifact))
    tape=[dict(shape=[1],dtype="fixture",sha256=output["sha256"],bytes=1)]
    def raw(positive):
        return dict(semantic=dict(read=positive,content_match=positive,decoded_code=1,found=positive),
            instance=dict(read=positive,decoded_code=2,found=positive),outcome="both_match" if positive else "no_match")
    journals={key:common.Journal(root/name) for key,name in dict(clean="clean.jsonl",native="native.jsonl",detect="detect-f6-noise-0-of-1.jsonl",quality="quality-0-of-1.jsonl").items()}
    for sid in [str(r["source_id"]) for r in rows[:count]]:
        for arm in config["arms"]:
            marked=arm!="unmarked"
            payload=dict(q=1,h=2) if marked else None
            for cell,seed in [(None,None)]+[(c,s) for c in p.CELLS for s in (0,1,2)]:
                kind="clean" if cell is None else "native"
                uid=f"clean:{sid}:{arm}" if cell is None else f"native:{cell}:{sid}:{seed}:{arm}"
                producer=dict(id=uid,status="ok",kind=kind,source=sid,arm=arm,payload=payload,output=output,seconds=1)
                if cell:
                    producer.update(cell=cell,seed=seed,input=output)
                    if marked: producer.update(replay_tape_receipt=tape,replay_tape_consumed=True)
                    else: producer.update(tape=output,tape_receipt=tape)
                journals[kind].append(producer)
                journals["detect"].append(dict(id=f"det:f6-noise:{uid}",status="ok",kind="detect",item=uid,source=sid,arm=arm,
                    input_sha256=output["sha256"],calls={"alpha":dict(status="ok",raw=raw(marked)),"beta":dict(status="ok",raw=raw(False))},seconds=.1))
                metrics=dict(psnr_db=45,ssim_rgb=.96,lpips=.02)
                if not marked and kind=="clean": metrics.update(psnr_db=None,psnr_infinite=True)
                journals["quality"].append(dict(id="quality:"+uid,status="ok",kind="quality",item=uid,source=sid,arm=arm,
                    input_sha256=output["sha256"],total=metrics,reference_source=sid,seconds=.1))
    return config,journals


class StagePJournalTests(unittest.TestCase):
    def test_complete_raw_inventory_and_cost(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            config,journals=journal_fixture(root)
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["status"],"COMPLETE")
            self.assertEqual(result["expected"],104)
            self.assertEqual(result["negative_calls"],312)
            self.assertEqual(result["compute"]["marked_clean"],4)
            self.assertEqual(result["compute"]["c0_native_attempts"],48)
            self.assertEqual(result["counts"]["K3-0.2"]["J"]["lower"],4)

    def test_missing_negative_is_incomplete_and_observed_positive_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            row=copy.deepcopy(next(iter(journals["detect"].latest.values())))
            row["calls"].pop("beta")
            journals["detect"].append(row)
            self.assertEqual(p.summarize_trial(root,config,count=4)["status"],"INCOMPLETE")
            row["calls"]["beta"]=copy.deepcopy(row["calls"]["alpha"])
            journals["detect"].append(row)
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["status"],"REJECTED")
            self.assertGreater(result["negative_events"],0)

    def test_missing_seed_even_decided_majority_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            row=copy.deepcopy(next(r for r in journals["native"].latest.values() if r["arm"]=="f6-noise"))
            row["status"]="error_terminal"
            journals["native"].append(row)
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["status"],"INCOMPLETE")
            self.assertEqual(result["compute"]["native_attempts"],97)

    def test_observed_failure_cannot_hide_missingness_or_resource_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            bad=copy.deepcopy(next(r for r in journals["quality"].latest.values() if r["arm"]=="f6-noise"))
            bad["total"]["psnr_db"]=35
            journals["quality"].append(bad)
            missing=copy.deepcopy(next(iter(journals["native"].latest.values())))
            missing["status"]="error_terminal"
            journals["native"].append(missing)
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["status"],"INCOMPLETE")
            self.assertTrue(result["rejection_reasons"])
            self.assertEqual(p.eligibility(result,None,None,4,"round1")["status"],"INCOMPLETE")
            (root/"RESOURCE_STOP-test.json").write_text("{}\n")
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["status"],"RESOURCE_STOP")
            self.assertTrue(result["rejection_reasons"])

    def test_quality_missing_and_strict_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            row=copy.deepcopy(next(r for r in journals["quality"].latest.values() if r["arm"]=="f6-noise"))
            row["total"]["psnr_db"]=None
            journals["quality"].append(row)
            self.assertEqual(p.summarize_trial(root,config,count=4)["status"],"INCOMPLETE")
            row["total"]["psnr_db"]=35
            journals["quality"].append(row)
            self.assertEqual(p.summarize_trial(root,config,count=4)["status"],"REJECTED")

    def test_endpoint_recomputed_not_trusted(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            for saved in list(journals["detect"].latest.values()):
                if saved["arm"]=="f6-noise" and saved["item"].startswith("native:K3"):
                    row=copy.deepcopy(saved)
                    row["calls"]["alpha"]["raw"]["semantic"]["decoded_code"]=99
                    row["calls"]["alpha"]["endpoints"]=dict(C=True,J=True,F=True)
                    journals["detect"].append(row)
            result=p.summarize_trial(root,config,count=4)
            self.assertEqual(result["counts"]["K3-0.2"]["C"]["lower"],4)
            self.assertEqual(result["counts"]["K3-0.2"]["J"]["lower"],0)

    def test_tape_and_artifact_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            row=copy.deepcopy(next(r for r in journals["native"].latest.values() if r["arm"]=="f6-noise"))
            row["replay_tape_consumed"]=False
            journals["native"].append(row)
            self.assertEqual(p.summarize_trial(root,config,count=4)["status"],"INCOMPLETE")
            (root/"opaque.bin").write_bytes(b"changed")
            with self.assertRaises(ValueError): p.summarize_trial(root,config,count=4)


class StagePCLIPlanTests(unittest.TestCase):
    def test_full_promotion_nomination_veto_lifecycle(self):
        receipt = dict(schema="tifs-round3-user-choice-v1", decision="approve", recorded_by="Claude",
            config_sha256=common.sha256_file(p.BASE), gate_profile="round1", stage_p="run",
            k3_optimization="excluded", before_server_outputs=True, user_decision_reference="TEST FIXTURE ONLY",
            max_instance_hours=15)
        real_load,real_sha=common.load_json,common.sha256_file
        fixture=Path("nonexistent-test-only-choice.json")
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(common,"load_json",side_effect=lambda path:receipt if Path(path)==fixture else real_load(path)), \
             patch.object(common,"sha256_file",side_effect=lambda path:"e"*64 if Path(path)==fixture else real_sha(path)):
            args=SimpleNamespace(run_root=Path(directory),base_config=p.BASE,source_manifest=p.HERE/"source-manifest.json",user_choice=fixture,
                destination=Path(directory)/"selected-config.json",count=4)
            select.plan(args)
            self.assertFalse((args.run_root/"check").exists())
            with self.assertRaises(FileNotFoundError): select.plan_check(args)
            def mock_summary(args,trial,n,partition="tune"):
                result=synthetic_summary(trial,n,n,partition)
                result["evidence_sha256"]=p.digest(dict(trial=trial,n=n,partition=partition))
                return result
            with patch.object(select,"summary",side_effect=mock_summary), patch("builtins.print"):
                self.assertEqual(select.entrants(args,4),list(p.CANDIDATES))
                self.assertEqual(select.advance(args),0)
                first=select.entrants(args,8)
                self.assertEqual(len(first),4)
                args.count=8
                self.assertEqual(select.advance(args),0)
                finalists=select.entrants(args,16)
                self.assertEqual(len(finalists),2)
                args.count=16
                self.assertEqual(select.advance(args),0)
                nomination=select.load_nomination(args)
                winner=nomination["candidate_id"]
                self.assertEqual(select.plan_check(args)[0],winner)
                self.assertEqual(select.finish(args),0)
                selected=common.load_json(args.destination)
                self.assertEqual(selected["status"],"SELECTED")
                self.assertEqual(selected["number_attempted"],8)
                self.assertEqual(selected["check_status"],"PASS")
                self.assertFalse(selected["execution_authorized"])
                consumed=p.profiles.load_execution_config(p.BASE,selection_path=args.destination,receipt_path=fixture)
                self.assertEqual(consumed["candidate"],selected["candidate"])
                self.assertEqual(consumed["writer"]["psnr_db"],selected["writer_psnr_db"])
                self.assertEqual([len(r["progression"]["survivors"]) for r in selected["rungs"]],[4,2,1])
                # A failed check can neither replace the winner nor overwrite
                # an earlier successful selection under changed evidence.
                def failed_summary(args,trial,n,partition="tune"):
                    result=mock_summary(args,trial,n,partition)
                    if partition=="check" and trial==winner:
                        result["counts"]["K3-0.2"]["J"].update(lower=0,upper=0)
                    return result
                with patch.object(select,"summary",side_effect=failed_summary):
                    with self.assertRaises(ValueError): select.finish(args)
                self.assertEqual(common.load_json(args.destination),selected)

    def test_torn_tail_and_undeclared_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); config,journals=journal_fixture(root)
            with (root/"native.jsonl").open("ab") as stream: stream.write(b'{"unterminated":')
            self.assertEqual(p.summarize_trial(root,config,count=4)["status"],"INCOMPLETE")
            journals["clean"].append(dict(id="clean:undeclared:f6-noise",status="error_terminal"))
            with self.assertRaises(ValueError): p.summarize_trial(root,config,count=4)


if __name__=="__main__":
    unittest.main()
