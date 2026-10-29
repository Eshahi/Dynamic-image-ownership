"""Pure launch-seal tests; no scientific imports or experiment execution."""
import copy
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as c
import tifs_stage_s as s


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.args = SimpleNamespace(out=self.root/'screen', rehearsal=False, stage='prepare')
        self.identity = dict(rehearsal=False, config_sha256='config', instance_start_utc='2026-01-01T00:00:00+00:00', max_hours=15)
        self.now = 1767225700
        self.device_total = 48 * 1024**3
        self.rehearsal = self.root/'rehearsal/identity.json'
        c.atomic_json(self.rehearsal, dict(self.identity, rehearsal=True))
        self.forecast = dict(status='GO', capacity=dict(status='GO', device_total_bytes=self.device_total,
            peak_device_bytes=30*1024**3, gpu_margin_bytes=1536*1024**2, gpu_limit_bytes=self.device_total-1536*1024**2,
            gpu_policy='measured-total-minus-1.5GiB-v1', gpu_ok=True), complete_inventory_required=True,
            rehearsal_identity=c.sha256_file(self.rehearsal),config_sha256='config',
            measured_one_time_seconds=100,full_variable_seconds=1000,retrieval_reserve_seconds=3600)
        c.atomic_json(self.root/'forecast.json',self.forecast)

    def tearDown(self):
        self.temp.cleanup()

    def launch(self, identity=None, now=None, total=None):
        return s.screen_launch(self.args, identity or self.identity, self.now if now is None else now,
                               device_total_bytes=self.device_total if total is None else total)

    def test_initial_launch_and_identical_resume(self):
        self.launch()
        self.assertTrue((self.args.out/'launch.json').exists())
        self.args.stage='native'
        self.launch(now=self.now+100)
        with self.assertRaises(ValueError):
            self.launch(identity=dict(self.identity,config_sha256='changed'))

    def test_direct_later_stage_cannot_skip_launch(self):
        self.args.stage='clean'
        with self.assertRaises(ValueError): self.launch()

    def test_incomplete_or_failed_capacity_cannot_launch(self):
        for change in (dict(status='INCOMPLETE'),dict(capacity=dict(status='RESOURCE_STOP')),
                       dict(rehearsal_identity='changed'),dict(complete_inventory_required=False)):
            c.atomic_json(self.root/'forecast.json',dict(self.forecast,**change))
            with self.assertRaises(ValueError): self.launch()

    def test_elapsed_clock_expiry_cannot_launch(self):
        with self.assertRaises(c.ResourceStop): self.launch(now=self.now+53000)

    def test_current_device_must_match_on_initial_and_resume(self):
        with self.assertRaisesRegex(ValueError, 'capacity'):
            self.launch(total=24*1024**3)
        self.launch()
        self.args.stage = 'native'
        with self.assertRaisesRegex(ValueError, 'capacity'):
            self.launch(total=24*1024**3)

    def test_old_or_tampered_gpu_policy_cannot_launch(self):
        for key, value in (('gpu_margin_bytes', 0), ('gpu_policy', 'hardcoded24'),
                           ('peak_device_bytes', self.device_total), ('gpu_limit_bytes', self.device_total)):
            changed = copy.deepcopy(self.forecast)
            changed['capacity'][key] = value
            c.atomic_json(self.root/'forecast.json', changed)
            with self.assertRaisesRegex(ValueError, 'capacity'):
                self.launch()

    def test_rehearsal_does_not_require_forecast(self):
        self.args.rehearsal=True
        (self.root/'forecast.json').unlink()
        s.screen_launch(self.args,self.identity,self.now)


if __name__=='__main__': unittest.main()
