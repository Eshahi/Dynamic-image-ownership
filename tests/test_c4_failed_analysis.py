"""Owned failure-analysis fixtures, never study pixels/models/GPU or retry."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import summarize_c4_failed_run as analysis


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"run";self.repo=Path(self.tmp.name)/"repo"
        self.root.mkdir();self.repo.mkdir()
        def put(name,value):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(json.dumps(value).encode() if not isinstance(value,bytes) else value)
            return path
        self.put=put
        config=self.repo/"experiments/c4-embedding-development-v1/frozen-case.json"
        config.parent.mkdir(parents=True);config.write_text(json.dumps({"selected":{"source_uid":"owned","canonical_pixel_sha256":"owned"}}))
        self.execution={"inputs":[{"path":"experiments/c4-embedding-development-v1/frozen-case.json",
            "sha256":analysis.sha(config)}],"outputs":["outputs/c4-development.json","logs/c4-progress.jsonl"]}
        executed = {item["path"]:(self.repo/item["path"]).read_bytes() for item in self.execution["inputs"]}
        self.input_patch=mock.patch.object(analysis,"executed_input",side_effect=lambda repo,name:executed[name])
        self.input_patch.start();self.addCleanup(self.input_patch.stop)
        digest=__import__("hashlib").sha256(analysis.canonical(self.execution)).hexdigest()
        self.patch=mock.patch.object(analysis,"DIGEST",digest);self.patch.start();self.addCleanup(self.patch.stop)
        put("execution-manifest.json",self.execution)
        put("outputs/c4-development.json",{"status":"failed","error_type":"OutOfMemoryError",
            "resources":{"peak_torch_allocated_bytes":8,"torch_allocation_limit_bytes":10}})
        phases=["worker_started","exact_inputs_checked","source_and_resources_started",
                "source_and_resources_checked","model_load_started","model_load_completed","worker_failed"]
        put("logs/c4-progress.jsonl",b"".join((json.dumps({"phase":p,"elapsed_seconds":i,
            **({"error_type":"OutOfMemoryError"} if p=="worker_failed" else {})})+"\n").encode()
            for i,p in enumerate(phases)))
        source=put("checkpoints/source-snapshot.bin",b"owned buffer, not pixels")
        put("outputs/c4-trial-owned/failed.json",{"error_type":"OutOfMemoryError",
            "source_raw_hash":analysis.sha(source),"source_id":"owned","source_pixel_hash":"owned"})
        put("outputs/c4-trial-owned/trajectory.jsonl",b'{"phase":"source_enrollment"}\n')
        for name in ("summary.md","logs/process.log","checkpoints/source-checked.json",
                     "checkpoints/model-load.json","checkpoints/c4-config-validation.json"):
            put(name,b"owned metadata")
        self.record={"execution_manifest_sha256":digest,"run_id":analysis.RUN,"git_commit":analysis.COMMIT,
            "git_dirty":False,"status":"failed","exit_status":2,"started_at":"owned","ended_at":"owned",
            "output_artifacts":[{"path":n,"sha256":analysis.sha(self.root/n)} for n in self.execution["outputs"]]}
        put("manifest.json",self.record)

    def test_failure_is_not_zero_metric_or_success(self):
        result=analysis.summarize(self.root,self.repo)
        self.assertIsNone(result["gradient_norm"]);self.assertEqual(result["recorded_gradient_observations"],0)
        self.assertEqual(result["unrecorded_internal_progress"],"unknown")
        self.assertEqual(result["status"],"failed");self.assertFalse(result["retry_authorized"])

    def test_missing_or_reordered_phases_rejected(self):
        for rows in ([{"phase":"worker_failed","elapsed_seconds":1,"error_type":"OutOfMemoryError"}],
                     [{"phase":"model_load_completed","elapsed_seconds":2},
                      {"phase":"worker_failed","elapsed_seconds":1,"error_type":"OutOfMemoryError"}]):
            self.put("logs/c4-progress.jsonl",b"".join((json.dumps(row)+"\n").encode() for row in rows))
            self.record["output_artifacts"]=[{"path":n,"sha256":analysis.sha(self.root/n)} for n in self.execution["outputs"]]
            self.put("manifest.json",self.record)
            with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)

    def test_tampered_declared_output_rejected(self):
        self.put("outputs/c4-development.json",b"changed")
        with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)

    def test_unexpected_png_and_trajectory_block_silent_analysis(self):
        png=self.put("outputs/c4-trial-owned/owned.png",b"not actual PNG")
        with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)
        png.unlink()
        self.put("outputs/c4-trial-owned/trajectory.jsonl",b'{"phase":"source_enrollment"}\n{"gradient_norm":0}\n')
        with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)

    def test_fabricated_clean_success_rejected(self):
        self.record["status"]="completed";self.put("manifest.json",self.record)
        with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)

    def test_repaired_checkout_cannot_replace_executed_case(self):
        (self.repo/"experiments/c4-embedding-development-v1/frozen-case.json").write_text("changed current file")
        self.assertEqual(analysis.summarize(self.root,self.repo)["source_uid"],"owned")
        with mock.patch.object(analysis,"executed_input",return_value=b"untrusted Git blob"):
            with self.assertRaises(ValueError):analysis.summarize(self.root,self.repo)

    def test_only_known_crlf_requirements_with_exact_digest_reconstruct(self):
        import hashlib
        raw=b"owned\nfixture\n"; crlf=raw.replace(b"\n",b"\r\n")
        digest=hashlib.sha256(crlf).hexdigest()
        self.assertEqual(analysis.checkout_bytes(raw,"requirements-wsl-torch-py314.txt",digest),crlf)
        for name,expected in (("src/embedding/proposed.py",digest),
                              ("requirements-wsl-torch-py314.txt","f"*64)):
            with self.assertRaises(ValueError):analysis.checkout_bytes(raw,name,expected)


if __name__ == "__main__":unittest.main()
