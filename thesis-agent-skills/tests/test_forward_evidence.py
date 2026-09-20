"""Offline forward probes. All papers, claims, and metrics are synthetic fixtures.

These tests demonstrate contract behavior, never scientific citation validity.
They intentionally assert safety contracts, so an unfixed defect fails visibly.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from thesis_agents import analysis, audit, research, writing
from thesis_agents.common import ContractError, digest, write


class ForwardEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="thesis-forward-evidence-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ("sources", "runs", "analysis"):
            (self.root / name).mkdir()

    def response(self):
        papers, evidence = [], []
        for pid, stance, text in (
            ("synthetic-a", "supporting", "Synthetic fixture: method A improved the toy metric."),
            ("synthetic-b", "contradicting", "Synthetic fixture: method A worsened the toy metric."),
        ):
            file = self.root / "sources" / (pid + ".txt")
            write(file, text)
            papers.append({"schema_version": "1.0", "paper_id": pid,
                "citation_key": pid, "doi": None,
                "canonical_url": "https://example.invalid/" + pid,
                "title": "Offline synthetic fixture " + pid,
                "authors": ["Synthetic Test Author"], "year": 2026,
                "venue": "Synthetic test fixture only", "access_date": "2026-09-19",
                "source_type": "report", "verification": "verified",
                "inspected_content": "full-text",
                "inspection": {"artifact": file.name, "sha256": digest(file)},
                "limitations": ["Synthetic; no scientific validity"]})
            evidence.append({"claim_id": "toy-comparison", "claim": "Method A improves the toy metric.",
                "source_id": pid, "kind": "direct-evidence", "stance": stance,
                "locator": "line 1", "confidence": "low",
                "limitations": ["Synthetic fixture"], "assumptions": []})
        return {"request_id": "synthetic-request", "papers": papers, "evidence": evidence,
                "assumptions": [], "open_questions": ["Why do the two synthetic fixtures disagree?"]}

    def claim(self, **changes):
        result = {"claim_id": "thesis-claim", "text": "Method A improves the toy metric.",
            "evidence_ids": [], "run_ids": [], "analysis_paths": [],
            "kind": "result", "author_id": "synthetic-author"}
        result.update(changes)
        return result

    def audit_claim(self, claim, data=None, expected=(), name="audit"):
        data = data or {"papers": [], "evidence": []}
        return audit.audit([claim], data["papers"], data["evidence"],
            self.root / "runs", self.root / "analysis", self.root / "sources",
            list(expected), "independent-reviewer", self.root / name)

    def spec(self):
        return {"schema_version": "1.0", "experiment_id": "synthetic-forward",
            "task_id": "synthetic-task", "question": "What does the toy metric do?",
            "hypothesis": "Toy treatment changes value.", "primary_outcome": "value",
            "secondary_outcomes": [], "datasets": [], "leakage_risks": ["Synthetic fixture"],
            "preprocessing": "None", "baselines": ["baseline"], "controls": ["Offline"],
            "ablations": [], "seeds": [1, 2, 3, 4, 5, 6],
            "stopping_rule": "All twelve declared runs", "acceptance_rule": "No scientific acceptance",
            "negative_result_policy": "Preserve failed and missing runs",
            "analysis": {"mode": "preregistered", "metric": "value", "direction": "higher",
                "conditions": ["baseline", "treatment"],
                "expected_runs": [{"run_id": f"{c}-{s}", "condition": c, "seed": s}
                                  for c in ("baseline", "treatment") for s in range(1, 7)],
                "comparison": ["baseline", "treatment"], "confidence_interval": "paired-bootstrap",
                "bootstrap_samples": 1000, "random_seed": 42,
                "multiple_comparisons": "none-single-comparison", "exclusion_rule": "none"}}

    def rows(self):
        return [{"run_id": f"{c}-{s}", "condition": c, "seed": s,
                 "status": "completed", "value": s + (1 if c == "treatment" else 0)}
                for c in ("baseline", "treatment") for s in range(1, 7)]

    def analyze(self, rows, name="toy"):
        path = self.root / (name + "-raw.json")
        write(path, rows)
        return analysis.analyze(self.spec(), [path], self.root / "analysis" / name)

    def manifest(self, row):
        folder = self.root / "runs" / "synthetic-forward" / row["run_id"]
        write(folder / "result.json", row)
        result = {"schema_version": "1.0", "run_id": row["run_id"], "stage_id": "test",
            "task_id": "synthetic-task", "experiment_id": "synthetic-forward",
            "status": row["status"], "executor": "test-fixture", "execution_target": "mock",
            "created_at": "2026-09-19T00:00:00Z", "started_at": "2026-09-19T00:00:00Z",
            "ended_at": "2026-09-19T00:00:01Z", "git_commit": "a" * 40,
            "git_dirty": False, "command": ["synthetic-offline-fixture"],
            "environment": {"python": "3.12", "platform": "synthetic"},
            "system": {"gpu": [], "cpu_count": 1}, "seeds": [row["seed"]], "datasets": [],
            "input_artifacts": [], "output_artifacts": [{"path": "result.json", "sha256": digest(folder / "result.json")}],
            "declared_metrics": ["value"], "budget_limits": {"max_seconds": 1, "max_usd": 0, "hourly_usd": 0},
            "approval_reference": "synthetic-fixture-only", "execution_manifest_sha256": "b" * 64,
            "errors": [], "cleanup_status": "not-needed", "pod_id": None,
            "exit_status": 0 if row["status"] == "completed" else 1}
        write(folder / "manifest.json", result)

    def test_request_and_conflicting_literature_survive_synthesis_and_audit(self):
        task = {"id": "synthetic-task", "title": "Compare contradictory toy evidence",
                "evidence_requirements": ["Both sources"], "inputs": [], "outputs": [],
                "dependencies": [], "gates": []}
        research.request(task, "synthetic-request", self.root / "requests")
        self.assertTrue((self.root / "requests/synthetic-request/response-contract.json").exists())
        data = self.response()
        self.assertTrue(research.validate_response(data, "synthetic-request", self.root / "sources")["valid"])
        research.synthesize(data, self.root / "synthesis", self.root / "sources")
        ledger = (self.root / "synthesis/evidence-ledger.jsonl").read_text()
        self.assertEqual(len(ledger.splitlines()), 2)
        self.assertIn('"contradicting"', ledger)
        result = self.audit_claim(self.claim(evidence_ids=["toy-comparison"]), data)
        self.assertEqual(result["claims"][0]["classification"], "conflicting")
        self.assertTrue(result["blocking"])

    def test_wrong_request_duplicate_source_and_changed_inspection_are_rejected(self):
        data = self.response()
        with self.assertRaises(ContractError):
            research.validate_response(data, "wrong-request", self.root / "sources")
        duplicate = copy.deepcopy(data)
        duplicate["papers"][1]["canonical_url"] = duplicate["papers"][0]["canonical_url"]
        with self.assertRaises(ContractError):
            research.validate_response(duplicate, "synthetic-request", self.root / "sources")
        (self.root / "sources/synthetic-a.txt").write_text("changed")
        with self.assertRaises(ContractError):
            research.validate_response(data, "synthetic-request", self.root / "sources")

    def test_failed_run_retained_and_interval_withheld_despite_five_good_pairs(self):
        rows = self.rows()
        rows[-1].update(status="failed", value=None)
        result = self.analyze(rows)
        self.assertEqual(result["failed_runs"], [{"run_id": "treatment-6", "status": "failed"}])
        self.assertEqual(result["comparison"]["n"], 5)
        self.assertIsNone(result["comparison"]["confidence_interval"])
        self.assertEqual(result["summaries"]["treatment"]["n"], 5)
        self.assertIn("no superiority", " ".join(result["warnings"]))

    def test_favorable_subset_reports_missing_runs_and_withholds_interval(self):
        result = self.analyze([r for r in self.rows() if r["seed"] != 6])
        self.assertEqual(result["missing_runs"], ["baseline-6", "treatment-6"])
        self.assertIsNone(result["comparison"]["confidence_interval"])

    def test_fractional_seed_is_not_silently_truncated(self):
        rows = self.rows()
        rows[0]["seed"] = 1.9
        with self.assertRaises(ContractError):
            self.analyze(rows)

    def test_unsupported_claim_is_marked_and_finalization_refused(self):
        claim = self.claim()
        result = self.audit_claim(claim)
        self.assertEqual(result["claims"][0]["classification"], "unsupported")
        writing.write_section([claim], result, "toy-draft", self.root / "thesis")
        text = (self.root / "thesis/chapters/toy-draft.md").read_text()
        self.assertIn("TODO:EVIDENCE TODO:CITATION", text)
        with self.assertRaises(ContractError):
            writing.write_section([claim], result, "toy-final", self.root / "thesis", final=True)
        self.assertFalse((self.root / "thesis/chapters/toy-final.md").exists())

    def test_self_review_is_rejected(self):
        with self.assertRaises(ContractError):
            self.audit_claim(self.claim(author_id="independent-reviewer"))

    def test_audit_detects_tampered_table(self):
        self.analyze(self.rows())
        (self.root / "analysis/toy/tables/descriptive.csv").write_text("tampered")
        result = self.audit_claim(self.claim(analysis_paths=["toy/tables/descriptive.csv"]))
        self.assertNotEqual(result["claims"][0]["classification"], "verified")
        self.assertTrue(result["blocking"])

    def test_audit_blocks_tampered_script_and_spec_hashes(self):
        rows = self.rows()
        self.analyze(rows)
        for row in rows:
            self.manifest(row)
        path = self.root / "analysis/toy/provenance.json"
        provenance = json.loads(path.read_text())
        provenance["script_sha256"] = "0" * 64
        provenance["specification_sha256"] = "0" * 64
        path.write_text(json.dumps(provenance))
        result = self.audit_claim(self.claim(run_ids=[r["run_id"] for r in rows],
            analysis_paths=["toy/tables/descriptive.csv"]), expected=[r["run_id"] for r in rows])
        self.assertTrue(result["blocking"], "Tampered script/spec provenance must block audit verification")

    def test_missing_citation_access_date_and_unmarked_inference_are_rejected(self):
        data=self.response()
        for change in ("source","date","inference"):
            candidate=copy.deepcopy(data)
            if change=="source": candidate["evidence"][0]["source_id"]="invented-source"
            if change=="date": del candidate["papers"][0]["access_date"]
            if change=="inference": candidate["evidence"][0]["kind"]="agent-inference"
            with self.subTest(change=change), self.assertRaises(ContractError):
                research.validate_response(candidate,"synthetic-request",self.root/"sources")

    def test_seed_bootstrap_and_figure_are_reproducible(self):
        first=self.analyze(self.rows(),"first")
        second=self.analyze(self.rows(),"second")
        self.assertEqual(first["comparison"],second["comparison"])
        self.assertIsNotNone(first["comparison"]["confidence_interval"])
        self.assertEqual(digest(self.root/"analysis/first/figures/seed-values.svg"),digest(self.root/"analysis/second/figures/seed-values.svg"))
        self.assertEqual(first["comparison"]["mean_difference"],1.0)

    def test_other_audit_classifications_distinguish_partial_and_unverifiable(self):
        data=self.response(); data["evidence"]=data["evidence"][:1]
        verified=self.audit_claim(self.claim(evidence_ids=["toy-comparison"]),data,name="verified")
        partial=self.audit_claim(self.claim(evidence_ids=["toy-comparison","missing"]),data,name="partial")
        unavailable=self.audit_claim(self.claim(evidence_ids=["missing"]),data,name="unavailable")
        self.assertEqual(verified["claims"][0]["classification"],"verified")
        self.assertEqual(partial["claims"][0]["classification"],"partially supported")
        self.assertEqual(unavailable["claims"][0]["classification"],"unverifiable")


if __name__ == "__main__":
    unittest.main()
