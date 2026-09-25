import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import capture_science_environment as science


class ScienceEnvironmentCaptureTests(unittest.TestCase):
    def test_distribution_inventory_canonicalizes_and_rejects_duplicates(self):
        one = SimpleNamespace(metadata={"Name": "typing_extensions"}, version="4.16")
        two = SimpleNamespace(metadata={"Name": "Alpha.Beta"}, version="1.0")
        self.assertEqual(science.distribution_versions([one, two]),
                         {"alpha-beta": "1.0", "typing-extensions": "4.16"})
        with self.assertRaisesRegex(ValueError, "duplicate installed distribution"):
            science.distribution_versions([one, one])

    def test_lock_hashes_are_explicit_and_missing_is_not_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "requirements.lock").write_bytes(b"locked")
            values = science.lock_digests(root)
            self.assertEqual(values["requirements.lock"],
                             hashlib.sha256(b"locked").hexdigest())
            self.assertIsNone(values["requirements-science-clip.txt"])

    @patch.object(science, "distribution_versions", return_value={"torch": "2.12.1"})
    @patch.object(science, "lock_digests", return_value={"requirements.lock": "a" * 64})
    @patch.object(science, "gpu_snapshot", return_value={"status": "nvidia-smi-not-found", "devices": []})
    @patch.object(science, "git_output", side_effect=["", "b" * 40])
    def test_receipt_excludes_paths_and_environment_variables(self, _git, _gpu, _locks, _dists):
        record = science.capture(Path.cwd())
        self.assertEqual(record["schema_version"], "a6-science-environment-v1")
        self.assertFalse(record["git_dirty"])
        self.assertEqual(record["installed_distributions"], {"torch": "2.12.1"})
        self.assertNotIn("executable", record)
        self.assertNotIn("environment_variables", record)


if __name__ == "__main__":
    unittest.main()
