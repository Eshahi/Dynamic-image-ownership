"""Model-free recipe/launcher/state tests; never invoke the scientific worker."""
import copy
import os
import unittest
from unittest.mock import patch
from pathlib import Path
from src.embedding import localization_package as package
from src.embedding.quality_package import canonical,CONFIG_SHA
from scripts.run_c4_localization import command
from scripts.c4_localization import cells


class LocalizationPackageTests(unittest.TestCase):
    def fixture(self):
        snapshots={name:b"owned" for name in package.REQUIRED}
        snapshots[package.SPEC+"/experiment-spec.yaml"]=canonical({"datasets":[]})
        pins={name:"a"*64 for name in package.REQUIRED};pins["configs/c4-development.json"]=CONFIG_SHA
        manifest={"experiment_id":package.EXPERIMENT,"run_id":package.RUN,"stage_id":"C4-localization-development",
            "task_id":"C4","execution_target":"local","seeds":[0],"reviewed_script":package.SCRIPT,
            "outputs":package.OUTPUTS,"metrics":package.METRICS,"budget":package.BUDGET,
            "resources":package.RESOURCES,"cleanup_policy":"stop-for-recovery","script_sha256":pins[package.SCRIPT],"datasets":[]}
        return manifest,snapshots,pins

    def check(self,values):
        with patch("src.embedding.localization_package.check_inputs",return_value=values):
            return package.inputs(b"owned",Path("/owned"))

    def test_fixed_recipe_and_each_field_reject(self):
        values=self.fixture();self.check(values)
        for field in values[0]:
            altered=copy.deepcopy(values);altered[0][field]="wrong"
            with self.subTest(field=field),self.assertRaises(ValueError):self.check(altered)

    def test_exact_inventory_config_and_outputs(self):
        values=self.fixture()
        for extra in (False,True):
            altered=copy.deepcopy(values)
            if extra:altered[1]["extra"]=b"owned"
            else:del altered[1][package.CHILD]
            with self.assertRaises(ValueError):self.check(altered)
        altered=copy.deepcopy(values);altered[2]["configs/c4-development.json"]="b"*64
        with self.assertRaises(ValueError):self.check(altered)
        self.assertEqual(len(package.OUTPUTS),6)
        self.assertEqual(len(cells()),9)
        self.assertEqual(set(cells().values()),{"pending"})

    @unittest.skipUnless(os.name=="nt","Windows launcher path contract tested on Windows")
    def test_launcher_exact_array_offline_and_external_timeout(self):
        args=command(Path("W:/owned manifest.json"),Path("W:/owned outputs"))
        self.assertIn("1140s",args);self.assertIn("--kill-after=10s",args)
        self.assertIn(package.CHILD,args);self.assertIn("/mnt/w/owned manifest.json",args)
        self.assertIn("HF_HUB_OFFLINE=1",args)
        self.assertNotIn("--execute",args)


if __name__=="__main__":unittest.main()
