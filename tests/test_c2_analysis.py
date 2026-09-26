"""Synthetic evidence fixtures only; no model/data/compute execution."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import analyze_c2_development as analysis
from scripts.c2_dev_probe import planned_cases


class AnalysisTests(unittest.TestCase):
    def fixture(self, root):
        selected = [(f"domain:source:{i:02}", {"domain": "domain"}, {}, Path("unused")) for i in range(32)]
        planned = planned_cases(selected)
        cases = [dict(row, config_hash="config", status="completed", feature_distance=-1e-8,
                      semantic_code_distance=0, key_distance=0, exact_features_equal=True) for row in planned]
        report = {"cases": cases, "examples": cases, "failures": [], "pending_cases": 0,
                  "planned_cases": 96, "config_hash": "config", "development_only": True,
                  "no_threshold_selection": True, "scientific_method_success": False, "status": "completed"}
        execution = {"inputs": []}
        (root / "outputs").mkdir(); (root / "logs").mkdir()
        (root / "execution-manifest.json").write_text(json.dumps(execution))
        (root / "outputs/semantic-examples.json").write_text(json.dumps(report))
        (root / "logs/case-progress.jsonl").write_text("\n".join(json.dumps(event) for event in
            [{"event": "prospective_inventory", "cases": planned}, *cases]))
        manifest = {"run_id": "c2-semantic-dev-001", "experiment_id": "c2-semantic-development-v1",
                    "execution_target": "local", "seeds": [0], "git_dirty": False,
                    "execution_manifest_sha256": analysis.digest(analysis.canonical(execution)),
                    "input_artifacts": [], "output_artifacts": [], "git_commit": "fixture",
                    "approval_reference": "fixture", "status": "completed"}
        for name in ("outputs/semantic-examples.json", "logs/case-progress.jsonl"):
            manifest["output_artifacts"].append({"path": name, "sha256": analysis.digest((root/name).read_bytes())})
        (root / "manifest.json").write_text(json.dumps(manifest))
        spec = root / "experiments/c2-semantic-development-v1/experiment-spec.yaml"
        spec.parent.mkdir(parents=True); spec.write_text("synthetic")
        return selected

    def test_all_cases_negative_roundoff_preserved_no_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); selected = self.fixture(root)
            with patch.object(analysis, "selection", return_value=("config", selected)):
                result = analysis.analyze(root, root)
            self.assertEqual(result["completed"], 96)
            self.assertTrue(result["no_inferential_statistics"])
            self.assertEqual(result["conditions"]["same_image_uncached_repeat"]["metrics"]["feature_distance"]["min"], -1e-8)

    def test_modified_output_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.fixture(root)
            with (root/"outputs/semantic-examples.json").open("a") as handle: handle.write(" ")
            with self.assertRaisesRegex(ValueError, "digest mismatch"): analysis.analyze(root, root)

    def test_duplicate_journal_even_rehashed_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); selected = self.fixture(root)
            journal = root/"logs/case-progress.jsonl"
            with journal.open("a") as handle: handle.write("\n"+journal.read_text().splitlines()[1])
            manifest = json.loads((root/"manifest.json").read_bytes())
            manifest["output_artifacts"][1]["sha256"] = analysis.digest(journal.read_bytes())
            (root/"manifest.json").write_text(json.dumps(manifest))
            with patch.object(analysis, "selection", return_value=("config", selected)):
                with self.assertRaisesRegex(ValueError, "duplicate terminal"): analysis.analyze(root, root)

    def test_failures_and_pending_are_not_filtered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); selected = self.fixture(root)
            report_path = root/"outputs/semantic-examples.json"
            report = json.loads(report_path.read_bytes())
            failed = {k: report["cases"][0][k] for k in
                      ("case_id", "image_id", "paired_image_id", "transform", "config_hash")}
            failed.update(status="failed", phase="synthetic", error="preserve")
            pending = {k: report["cases"][1][k] for k in
                       ("case_id", "image_id", "paired_image_id", "transform", "config_hash")}
            pending["status"] = "pending"
            report["cases"][:2] = [failed, pending]
            report.update(status="incomplete", examples=report["cases"][2:], failures=[failed], pending_cases=1)
            report_path.write_text(json.dumps(report))
            journal = root/"logs/case-progress.jsonl"
            inventory = json.loads(journal.read_text().splitlines()[0])
            journal.write_text("\n".join(json.dumps(row) for row in [inventory, failed, *report["examples"]]))
            manifest_path = root/"manifest.json"
            manifest = json.loads(manifest_path.read_bytes())
            manifest["status"] = "failed"
            for item in manifest["output_artifacts"]:
                item["sha256"] = analysis.digest((root/item["path"]).read_bytes())
            manifest_path.write_text(json.dumps(manifest))
            with patch.object(analysis, "selection", return_value=("config", selected)):
                result = analysis.analyze(root, root)
            self.assertEqual(result["completed"], 94)
            self.assertEqual(result["failed"], [failed])
            self.assertEqual(result["pending"], [pending])


if __name__ == "__main__":
    unittest.main()
