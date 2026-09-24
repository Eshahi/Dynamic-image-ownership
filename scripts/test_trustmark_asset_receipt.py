"""Synthetic offline failure checks for the TrustMark Q asset receipt."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from trustmark_asset_receipt import Q_ASSETS, SOURCE_COMMIT, inspect_assets, verify_lock


class TrustMarkAssetReceiptTests(unittest.TestCase):
    def test_missing_and_mismatched_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(ValueError, "missing"):
                inspect_assets(directory)
            for name in Q_ASSETS:
                (directory / name).write_bytes(name.encode("ascii"))
            with self.assertRaisesRegex(ValueError, "MD5 mismatch"):
                inspect_assets(directory)

    def test_receipt_lock_rejects_tamper_and_wrong_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            synthetic = {name: name.encode("ascii") for name in Q_ASSETS}
            for name, content in synthetic.items():
                (directory / name).write_bytes(content)
            synthetic_md5 = {name: hashlib.md5(content).hexdigest()
                             for name, content in synthetic.items()}
            receipt = inspect_assets(directory, synthetic_md5)
            lock = {"source_commit": SOURCE_COMMIT,
                    "sha256": {name: value["sha256"]
                               for name, value in receipt["assets"].items()}}
            verify_lock(receipt, json.loads(json.dumps(lock)))
            self.assertIn("LOCK_MATCH", receipt["status"])
            lock["source_commit"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "source commit"):
                verify_lock(receipt, lock)
            lock["source_commit"] = SOURCE_COMMIT
            lock["sha256"]["decoder_Q.ckpt"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "lock mismatch"):
                verify_lock(receipt, lock)


if __name__ == "__main__":
    unittest.main()
