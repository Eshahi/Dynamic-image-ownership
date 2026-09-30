"""Ordinary launch-array tests; never starts a subprocess or scientific worker."""
import unittest
import os
from run_three_threat_study import command, linux_path


@unittest.skipUnless(os.name == "nt", "launcher paths require the actual Windows runner host")
class LaunchTests(unittest.TestCase):
    def test_fixed_offline_clean_environment_and_watchdog(self):
        values = command("W:/test/package.json", "W:/test/outputs")
        self.assertEqual(values[:3], ["C:/Windows/System32/wsl.exe", "--exec", "timeout"])
        self.assertIn("86200s", values)
        self.assertIn("--kill-after=30s", values)
        self.assertIn("-i", values)
        self.assertIn("HF_HUB_OFFLINE=1", values)
        self.assertIn("DIFFUSERS_OFFLINE=1", values)
        self.assertIn("PYTHONNOUSERSITE=1", values)
        self.assertNotIn("CUDA_VISIBLE_DEVICES=", values)
        self.assertEqual(values[-4:], ["--manifest", "/mnt/w/test/package.json", "--output-dir", "/mnt/w/test/outputs"])

    def test_literal_space_path_not_shell_command(self):
        self.assertEqual(linux_path("W:/a b/c.json"), "/mnt/w/a b/c.json")
        values = command("W:/a b/c.json", "W:/a b/output")
        self.assertIn("/mnt/w/a b/c.json", values)
        self.assertNotIn("sh", values)
        self.assertNotIn("-c", values)


if __name__ == "__main__":
    unittest.main()
