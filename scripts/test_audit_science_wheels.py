import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_science_wheels import audit, parse_lock, wheel_identity


class ScienceWheelAuditTests(unittest.TestCase):
    def test_full_candidate_inventory_covers_stage2_without_version_drift(self):
        root = Path(__file__).resolve().parents[1]
        candidates = parse_lock((root / "requirements-science-candidates-win312.txt")
                                .read_text(encoding="utf-8"))
        stage2 = parse_lock((root / "requirements-science-stage2-win312-hashes.txt")
                            .read_text(encoding="utf-8"))
        self.assertEqual(len(candidates), 42)
        self.assertEqual({key: candidates[key] for key in stage2}, stage2)

    def test_lock_rejects_duplicate_and_unhashed_line(self):
        value = "alpha==1 --hash=sha256:" + "a" * 64
        with self.assertRaises(ValueError):
            parse_lock(value + "\n" + value)
        with self.assertRaises(ValueError):
            parse_lock("alpha==1")

    def test_cached_wheel_matches_lock_and_reports_missing_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "alpha-1-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
            self.assertEqual(wheel_identity(wheel), ("alpha", "1"))
            expected = hashlib.sha256(wheel.read_bytes()).hexdigest()
            report = audit({"alpha": "1", "beta": "2"}, [root],
                           parse_lock(f"alpha==1 --hash=sha256:{expected}"))
            self.assertEqual(report["locked_failures"], [])
            self.assertEqual(report["installed_without_cached_wheel"], ["beta==2"])
            self.assertEqual(report["installed_wheel_candidates"],
                             {"alpha==1": [expected], "beta==2": []})
            self.assertEqual(report["status"], "partial_inventory")

    def test_multiple_candidate_hashes_are_visible_not_silently_chosen(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for suffix in ("a", "b"):
                wheel = root / f"alpha-1-{suffix}-py3-none-any.whl"
                with zipfile.ZipFile(wheel, "w") as archive:
                    archive.writestr("alpha-1.dist-info/METADATA",
                                     "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
                    archive.writestr("alpha/payload.txt", suffix)
            report = audit({"alpha": "1"}, [root], {})
            self.assertEqual(report["installed_with_multiple_candidates"],
                             ["alpha==1"])
            self.assertEqual(len(report["installed_wheel_candidates"]["alpha==1"]), 2)

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "alpha-1-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
            report = audit({"alpha": "1"}, [root],
                           parse_lock("alpha==1 --hash=sha256:" + "0" * 64))
            self.assertEqual(report["locked_failures"],
                             ["alpha==1:wheel-hash-missing"])

    def test_invalid_wheel_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "broken.whl").write_bytes(b"not a wheel")
            with self.assertRaises(ValueError):
                audit({}, [root], {("alpha", "1"): "0" * 64})

    def test_vendored_dist_info_does_not_change_wheel_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            wheel = Path(temp) / "alpha-1-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("alpha-1.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
                archive.writestr("alpha/_vendor/beta-2.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Beta\nVersion: 2\n")
            self.assertEqual(wheel_identity(wheel), ("alpha", "1"))

    def test_multiple_top_level_dist_info_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            wheel = Path(temp) / "ambiguous.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                for name in ("alpha-1", "beta-2"):
                    archive.writestr(f"{name}.dist-info/METADATA",
                                     "Metadata-Version: 2.1\nName: Alpha\nVersion: 1\n")
            with self.assertRaisesRegex(ValueError, "exactly one METADATA"):
                wheel_identity(wheel)

    def test_http_cache_wheel_recovers_missing_distribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheels = root / "wheels"
            wheels.mkdir()
            cache = root / "http"
            cache.mkdir()
            body = cache / "cached.body"
            with zipfile.ZipFile(body, "w") as archive:
                archive.writestr("beta-2.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: Beta\nVersion: 2\n")
            (cache / "not-a-wheel.body").write_bytes(b"HTML cache body")
            report = audit({"beta": "2"}, [wheels], {}, [cache])
            self.assertEqual(report["installed_without_cached_wheel"], [])
            self.assertEqual(report["http_cached_wheel_body_count"], 1)

    def test_built_wheel_cache_recovers_vcs_distribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheels = root / "wheels"
            wheels.mkdir()
            built = root / "built"
            nested = built / "nested"
            nested.mkdir(parents=True)
            wheel = nested / "clip-1.0-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("clip-1.0.dist-info/METADATA",
                                 "Metadata-Version: 2.1\nName: clip\nVersion: 1.0\n")
            report = audit({"clip": "1.0"}, [wheels], {}, [], [built])
            self.assertEqual(report["built_cached_wheel_count"], 1)
            self.assertEqual(report["installed_without_cached_wheel"], [])


if __name__ == "__main__":
    unittest.main()
