"""Synthetic metadata and CPU mock-decoder tests, never real source images."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch

from scripts import m1_reconstruction_diagnosis as method


def cases():
    return [{"id": ident, "path": f"unused-{ident}.jpg", "sha256": "a"*64} for ident in method.base.IDS]


def row(ident, psnr):
    return {"id": ident, "outcome": "completed", "raw_sha256": "a"*64,
        "source_rgb8_sha256": "b"*64, "checkpoints": [{"step": 200, "psnr_db": psnr,
        "psnr_infinite": False, "mse_rgb8": 100, "latent_sha256": "c"*64, "png_sha256": "d"*64}]}


def run(rows):
    return {"schema_version": "m1-development-run-v1", "data_split": "development",
        "config": copy.deepcopy(method.base.CONFIG), "latent_units": method.UNITS,
        "commit": "0"*40, "outcome": "started", "cases": rows}


def inventory():
    rows = [row(ident, 25 + i) for i, ident in enumerate(method.base.IDS)]
    entries, _ = method.collect_inventory(cases(), [(Path("first"), run(rows))])
    return entries


class ReconstructionDiagnosisTests(unittest.TestCase):
    def test_extrema_selection_and_numeric_ties(self):
        entries = inventory()
        selected = method.select_extrema(entries, method.base.IDS, ["best", "worst"])
        self.assertEqual([e["id"] for e in selected], [method.base.IDS[-1], method.base.IDS[0]])
        entries[-2]["checkpoint"]["psnr_db"] = entries[-1]["checkpoint"]["psnr_db"]
        selected = method.select_extrema(entries, method.base.IDS, ["best", "worst"])
        self.assertEqual(selected[0]["id"], min(method.base.IDS[-2:]))
        for entry in entries:
            entry["checkpoint"]["psnr_db"] = 30
        selected = method.select_extrema(entries, method.base.IDS, ["best", "worst"])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["selection_roles"], ["best", "worst"])

    def test_selection_refuses_missing_duplicate_and_bad_score(self):
        entries = inventory()
        for bad in (entries[:-1], entries[:-1] + [entries[0]]):
            with self.assertRaises(ValueError):
                method.select_extrema(bad, method.base.IDS, ["best", "worst"])
        entries[0]["checkpoint"]["psnr_db"] = float("nan")
        with self.assertRaises(ValueError):
            method.select_extrema(entries, method.base.IDS, ["best", "worst"])

    def test_infinite_psnr_is_explicit_and_json_safe(self):
        entries = inventory()
        entries[0]["checkpoint"].update(psnr_infinite=True, psnr_db=None, mse_rgb8=0)
        selected = method.select_extrema(entries, method.base.IDS, ["best"])
        self.assertEqual(selected[0]["id"], method.base.IDS[0])
        json.dumps(selected, allow_nan=False)
        entries[0]["checkpoint"]["psnr_db"] = float("inf")
        with self.assertRaises(ValueError):
            method.select_extrema(entries, method.base.IDS, ["best"])

    def test_inventory_combines_completed_cases_from_interrupted_runs(self):
        ids = method.base.IDS
        first = run([row(ident, 25) for ident in ids[:4]] + [{"id": ids[4], "outcome": "started"}])
        second = run([row(ident, 26) for ident in ids[4:]])
        entries, ignored = method.collect_inventory(cases(), [(Path("old"), first), (Path("new"), second)])
        self.assertEqual(len(entries), 12)
        self.assertEqual(ignored, [{"id": ids[4], "run": "old", "outcome": "started"}])
        duplicate = copy.deepcopy(second)
        duplicate["cases"].append(row(ids[0], 99))
        with self.assertRaisesRegex(ValueError, "duplicate_completed"):
            method.collect_inventory(cases(), [(Path("old"), first), (Path("new"), duplicate)])
        with self.assertRaisesRegex(ValueError, "missing"):
            method.collect_inventory(cases(), [(Path("old"), first)])

    def test_inventory_rejects_unreserved_split_units_and_hashes(self):
        good = run([row(ident, 25) for ident in method.base.IDS])
        for key, value in (("data_split", "heldout"), ("latent_units", "scaled"), ("config", {})):
            bad = copy.deepcopy(good)
            bad[key] = value
            with self.assertRaises(ValueError):
                method.collect_inventory(cases(), [(Path("unused"), bad)])
        bad = copy.deepcopy(good)
        bad["cases"][0]["raw_sha256"] = "e"*64
        with self.assertRaises(ValueError):
            method.collect_inventory(cases(), [(Path("unused"), bad)])

    def test_manifest_frozen_config_and_development_only(self):
        manifest = json.loads((method.ROOT / "research/m1-reconstruction-diagnosis-dev.json").read_text())
        reserved, paths, cohort = method.validate_manifest(manifest)
        self.assertEqual(len(reserved), 12)
        self.assertEqual(len(paths), 2)
        bad = copy.deepcopy(manifest)
        bad["config"]["learning_rate"] = .02
        with self.assertRaises(ValueError):
            method.validate_manifest(bad)
        bad = copy.deepcopy(manifest)
        bad["data_split"] = "test"
        with self.assertRaises(ValueError):
            method.validate_manifest(bad)

    def test_artifact_hash_and_start_units_are_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            latent, png = root / "start.pt", root / "start.png"
            torch.save({"z": torch.zeros(1, 4, 64, 64), "step": 200, "latent_units": method.UNITS}, latent)
            png.write_bytes(b"synthetic artifact, no photograph")
            entry = {"id": 1675, "latent_path": str(latent), "png_path": str(png),
                     "checkpoint": {"latent_sha256": method.sha(latent), "png_sha256": method.sha(png)}}
            self.assertEqual(len(method.verify_artifacts([entry])), 2)
            self.assertEqual(tuple(method.load_start(entry).shape), (1, 4, 64, 64))
            png.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                method.verify_artifacts([entry])
            torch.save({"z": torch.zeros(1, 4, 64, 64), "step": 200, "latent_units": "scaled"}, latent)
            entry["checkpoint"]["latent_sha256"] = method.sha(latent)
            with self.assertRaises(ValueError):
                method.load_start(entry)

    def test_mock_fit_unclamped_loss_fixed_schedule_and_frozen_model(self):
        class VAE(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.scale = torch.nn.Parameter(torch.tensor(1.0))
            def decode(self, z, return_dict=False):
                return (self.scale*z,)
        model = VAE()
        config = copy.deepcopy(method.CONFIG)
        config.update(additional_steps=4, evaluation_total_steps=[200, 202, 204], snapshot_every=2)
        target = torch.full((1, 1, 4, 4), .9)
        initial = torch.full_like(target, 4)
        updates, measurements, snapshots = [], [], []
        def measure(step, z, raw, mse):
            measurements.append((step, mse, raw.clone(), z.clone()))
        def snapshot(step, z, optimizer):
            snapshots.append((step, z.clone(), method.cpu_state(optimizer.state_dict())))
        final, report = method.fit_additional(model, target, initial, config, updates.append, measure, snapshot)
        self.assertEqual([m[0] for m in measurements], [200, 202, 204])
        self.assertEqual([s[0] for s in snapshots], [202, 204])
        self.assertEqual(len(updates), 4)
        self.assertGreater(float(measurements[0][2].max()), 1)
        self.assertAlmostEqual(measurements[0][1], (2.5-.9)**2, places=5)
        self.assertTrue(torch.equal(final, measurements[-1][3]))
        self.assertLess(float(final.mean()), float(initial.mean()))
        self.assertEqual(report["selection"], "last-fixed-step")
        self.assertEqual(report["optimizer_start"], "reset-Adam-at-step200")
        self.assertEqual(float(model.scale), 1)
        self.assertIsNone(model.scale.grad)
        self.assertFalse(model.scale.requires_grad)
        self.assertEqual(float(next(iter(snapshots[-1][2]["state"].values()))["step"]), 4)

    def test_plateau_is_descriptive_and_keeps_final_checkpoint(self):
        points = [{"step": step, "psnr_db": score, "psnr_infinite": False,
                   "quality_admissible": False} for step, score in ((200, 29), (400, 30), (600, 30.2))]
        result = method.comparison(points)
        self.assertTrue(result["plateau"])
        self.assertFalse(result["final_quality_admissible"])
        self.assertAlmostEqual(result["psnr_gain_200_to_600_db"], 1.2)
        points[-1]["psnr_db"] = 30.3
        self.assertFalse(method.comparison(points)["plateau"])
        self.assertIsNone(method.comparison(points[:-1])["plateau"])

    def test_malformed_psnr_flag_mse_and_roles_are_rejected(self):
        for changes in ({'psnr_infinite':1},{'psnr_infinite':'false'},
                        {'mse_rgb8':float('nan')},{'mse_rgb8':False},{'mse_rgb8':0}):
            point=dict(row(method.base.IDS[0],30)['checkpoints'][0],**changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):method.psnr_value(point)
        with self.assertRaises(ValueError):method.select_extrema(inventory(),method.base.IDS,['anything'])
        bad=run([row(i,30) for i in method.base.IDS]);bad['commit']=None
        with self.assertRaises(ValueError):method.collect_inventory(cases(),[(Path('unused'),bad)])

    def test_starting_latent_does_not_silently_coerce_precision_or_complex(self):
        with tempfile.TemporaryDirectory() as directory:
            latent=Path(directory)/'start.pt'
            for dtype in (torch.float16,torch.float64,torch.complex64,torch.int32):
                torch.save({'z':torch.zeros(1,4,64,64,dtype=dtype),'step':200,'latent_units':method.UNITS},latent)
                entry={'latent_path':str(latent),'checkpoint':{'latent_sha256':method.sha(latent)}}
                with self.subTest(dtype=dtype),self.assertRaises(ValueError):method.load_start(entry)

    def test_preflight_failure_has_receipt_and_never_overwrites_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);output=root/'.thesis-build/dev-runs/mock-failure'
            manifest=root/'fixture.json';manifest.write_text('{}')
            with patch.object(method,'MAIN',root),patch.object(method,'_run_verified',side_effect=ValueError('mock preflight failure')) as verified,patch.object(method.subprocess,'check_output',return_value='0'*40):
                self.assertEqual(method.run(manifest,output),1)
                receipt=json.loads((output/'run.json').read_text())
                self.assertEqual(receipt['outcome'],'failed')
                self.assertEqual(receipt['failure_phase'],'preflight_or_setup')
                self.assertEqual(receipt['manifest_sha256'],method.sha(manifest))
                original=(output/'run.json').read_bytes()
                with self.assertRaises(FileExistsError):method.run(manifest,output)
                self.assertEqual((output/'run.json').read_bytes(),original)
                self.assertEqual(verified.call_count,1)


if __name__ == "__main__":
    unittest.main()
