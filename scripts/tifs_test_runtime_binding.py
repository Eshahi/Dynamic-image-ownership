"""Pure setup-to-runtime asset binding tests; tiny non-image fixtures only."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import tifs_stage_s as s
import tifs_common as c

class RuntimeTests(unittest.TestCase):
    def test_setup_start_receipt_and_same_path_asset_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); here=root/'research/tifs-20261028/stage-s';here.mkdir(parents=True)
            assets=root/'assets';assets.mkdir();(assets/'a6').mkdir()
            asset=assets/'a6/test.bin';asset.write_bytes(b'fixed')
            for name in ('tifs_stage_s_setup.py','tifs_stage_s_setup.sh','encoder_transfer_assets.py','tifs_common.py'):
                target=root/'scripts'/name;target.parent.mkdir(exist_ok=True);target.write_text('fixture')
            (here/'source-manifest.json').write_text('{}')
            (here/'requirements.txt').write_text('')
            c.atomic_json(here/'asset-plan.json',dict(files=[dict(path='a6/test.bin',size_bytes=5,sha256=c.sha256_file(asset))]))
            instant=datetime(2026,1,1,tzinfo=timezone.utc)
            receipt=dict(status='complete',instance_start_utc=instant.isoformat(),
                source_manifest_sha256=c.sha256_file(here/'source-manifest.json'),
                asset_plan_sha256=c.sha256_file(here/'asset-plan.json'),
                requirements_sha256=c.sha256_file(here/'requirements.txt'),
                setup_code_sha256={str(p.relative_to(root)).replace('\\','/'):c.sha256_file(p) for p in (root/'scripts').iterdir()})
            ready=assets/'tifs-stage-s-setup-ready.json';c.atomic_json(ready,receipt)
            args=SimpleNamespace(assets=assets,stage='prepare',rehearsal=True)
            config=dict(source_manifest=str(here/'source-manifest.json'))
            with patch.object(s,'ROOT',root):
                first=s.setup_identity(args,config,instant)
                args.rehearsal=False
                self.assertEqual(s.setup_identity(args,config,instant),first)
                asset.write_bytes(b'other')
                with self.assertRaisesRegex(ValueError,'asset changed'):s.setup_identity(args,config,instant)
                c.atomic_json(ready,dict(receipt,instance_start_utc='other'))
                with self.assertRaisesRegex(ValueError,'receipt'):s.setup_identity(args,config,instant)

    def test_pin_mismatch_rejected_without_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'requirements.txt';path.write_text('torch==1.0\n')
            metadata=SimpleNamespace(version=lambda name:'2.0')
            with self.assertRaisesRegex(ValueError,'pin mismatch'):s.package_pins(path,metadata)

if __name__=='__main__':unittest.main()
