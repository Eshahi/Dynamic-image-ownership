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
        self.execution={"inputs":[],"outputs":["outputs/c4-development.json","logs/c4-progress.jsonl"]}
        digest=__import__("hashlib").sha256(analysis.canonical(self.execution)).hexdigest()
        self.patch=mock.patch.object(analysis,"DIGEST",digest);self.patch.start();self.addCleanup(self.patch.stop)
        put("execution-manifest.json",self.execution)
        put("outputs/c4-development.json",{"status":"failed","error_type":"OutOfMemoryError",
            "resources":{"peak_torch_allocated_bytes":8,"torch_allocation_limit_bytes":10}})
        put("logs/c4-progress.jsonl",b'{"phase":"worker_failed","elapsed_seconds":1}\n')
        source=put("checkpoints/source-snapshot.bin",b"owned buffer, not pixels")
        put("outputs/c4-trial-owned/failed.json",{"error_type":"OutOfMemoryError",
            "source_raw_hash":analysis.sha(source),"source_id":"owned","source_pixel_hash":"owned"})
        put("outputs/c4-trial-owned/trajectory.jsonl",b'{"phase":"source_enrollment"}\n')
        for name in ("summary.md","logs/process.log","checkpoints/source-checked.json",
                     "checkpoints/model-load.json","checkpoints/c4-config-validation.json"):
            put(name,b"owned metadata")
        config=self.repo/"experiments/c4-embedding-development-v1/frozen-case.json"
        config.parent.mkdir(parents=True);config.write_text(json.dumps({"selected":{"source_uid":"owned","canonical_pixel_sha256":"owned"}}))
        self.record={"execution_manifest_sha256":digest,"run_id":analysis.RUN,"git_commit":analysis.COMMIT,
            "git_dirty":False,"status":"failed","exit_status":2,"started_at":"owned","ended_at":"owned",
            "output_artifacts":[{"path":n,"sha256":analysis.sha(self.root/n)} for n in self.execution["outputs"]]}
        put("manifest.json",self.record)

    def test_failure_is_not_zero_metric_or_success(self):
        result=analysis.summarize(self.root,self.repo)
        self.assertIsNone(result["gradient_norm"]);self.assertEqual(result["gradient_observations"],0)
        self.assertEqual(result["status"],"failed");self.assertFalse(result["retry_authorized"])

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


if __name__ == "__main__":unittest.main()
