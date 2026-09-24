import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import audit_a6_clip_install as clip_audit


class ClipInstallAuditTests(unittest.TestCase):
    def test_matches_exact_source_and_origin_then_rejects_modified_install(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "clip.whl"
            site = root / "site-packages"
            site.mkdir()
            with zipfile.ZipFile(wheel, "w") as archive:
                for name in clip_audit.SOURCE_FILES:
                    content = name.encode("ascii")
                    archive.writestr(name, content)
                    installed = site / name
                    installed.parent.mkdir(parents=True, exist_ok=True)
                    installed.write_bytes(content)
            origin = root / "origin.json"
            value = {"url": clip_audit.EXPECTED_URL,
                     "vcs_info": {"vcs": "git", "commit_id": clip_audit.EXPECTED_COMMIT,
                                  "requested_revision": clip_audit.EXPECTED_COMMIT}}
            origin.write_text(json.dumps(value), encoding="utf-8")
            installed_origin = site / "clip-1.0.dist-info/direct_url.json"
            installed_origin.parent.mkdir()
            installed_origin.write_text(json.dumps(value), encoding="utf-8")
            expected_hash = hashlib.sha256(wheel.read_bytes()).hexdigest()
            with patch.object(clip_audit, "EXPECTED_WHEEL_SHA256", expected_hash):
                report = clip_audit.audit(wheel, origin, site)
                self.assertEqual(report["source_file_count"], 5)
                (site / "clip/model.py").write_bytes(b"modified")
                with self.assertRaisesRegex(ValueError, "installed CLIP source differs"):
                    clip_audit.audit(wheel, origin, site)

    def test_rejects_wrong_origin_and_wheel_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wheel = root / "clip.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr(clip_audit.SOURCE_FILES[0], b"a")
            site = root / "site"
            site.mkdir()
            origin = root / "origin.json"
            origin.write_text('{"url":"https://example.org/other.git"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "wheel digest"):
                clip_audit.audit(wheel, origin, site)
            with patch.object(clip_audit, "EXPECTED_WHEEL_SHA256",
                              hashlib.sha256(wheel.read_bytes()).hexdigest()):
                with self.assertRaisesRegex(ValueError, "source origin"):
                    clip_audit.audit(wheel, origin, site)


if __name__ == "__main__":
    unittest.main()
