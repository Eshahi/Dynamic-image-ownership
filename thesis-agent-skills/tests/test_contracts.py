"""Portable security and contract checks; no live services."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import re
import unittest
from unittest.mock import patch
from thesis_agents.common import ContractError, contained, digest, read, redact, relative, safe_env, validate, write
from thesis_agents.compute import parse_gpu,verify_artifacts
from thesis_agents.guide import LiteralParser
from thesis_agents.plan import github_issue_seed, reduce_guide
from thesis_agents.validate_bundle import validate_bundle

ROOT=Path(__file__).resolve().parents[1]

class Contracts(unittest.TestCase):
    def test_all_skill_and_official_workflow_validation(self):
        result=validate_bundle(ROOT)
        self.assertEqual(len(result["skills"]),8)
        self.assertEqual(len(result["workflows"]),2)

    def test_gpu_parsing_and_invalid_numbers(self):
        rows=parse_gpu((ROOT/"fixtures/nvidia-smi.csv").read_text())
        self.assertEqual(rows[0]["total_mib"],12227)
        self.assertEqual(rows[0]["free_mib"],11200)
        for text in ("0,bad,2,3,driver", "0,bad,NaN,3,driver","bad"):
            with self.subTest(text=text),self.assertRaises(ContractError): parse_gpu(text)

    def test_safe_env_preserves_windows_gpu_discovery_roots(self):
        with patch.dict(os.environ,{"ProgramFiles":r"C:\Program Files","ProgramW6432":r"C:\Program Files"},clear=False):
            environment=safe_env()
        normalized={key.upper():value for key,value in environment.items()}
        self.assertEqual(normalized["PROGRAMFILES"],r"C:\Program Files")
        self.assertEqual(normalized["PROGRAMW6432"],r"C:\Program Files")

    def test_portable_paths_and_traversal(self):
        self.assertEqual(relative(r"metrics\with spaces\x.json"),Path("metrics/with spaces/x.json"))
        for value in (r"C:\Windows\x",r"\\server\x","/etc/passwd","../x",r"metrics\..\x","a:b","a//b"):
            with self.subTest(value=value),self.assertRaises(ContractError): relative(value)

    def test_checksum_tampering(self):
        with tempfile.TemporaryDirectory(prefix="artifact spaces ") as t:
            p=Path(t)/"a.txt"; p.write_text("original")
            entries=[{"path":"a.txt","sha256":digest(p)}]
            self.assertTrue(verify_artifacts(t,entries))
            p.write_text("changed")
            with self.assertRaises(ContractError): verify_artifacts(t,entries)

    def test_literal_parser_never_evaluates(self):
        self.assertEqual(LiteralParser('{a:`literal`,b:[1,true,null]}').value(),{"a":"literal","b":[1,True,None]})
        for text in ('{a:process.exit()}','{a:`${danger()}`}','{a:1+2}'):
            with self.assertRaises(ContractError): LiteralParser(text).value()

    def test_imported_guide_integrity(self):
        guide=read(ROOT/"fixtures/guide-tasks.json")
        self.assertEqual(len(guide["tasks"]),58)
        self.assertEqual(len(guide["phases"]),10)
        self.assertFalse(guide["warnings"])
        order=guide["topological_order"]
        for t in guide["tasks"]:
            self.assertEqual(t["dependencies"],t["original_contract"]["needs"])
            self.assertTrue(all(order.index(d)<order.index(t["id"]) for d in t["dependencies"]))

    def test_reduced_plan_covers_source_once_and_is_acyclic(self):
        source=read(ROOT/"fixtures/guide-tasks.json")
        plan=reduce_guide(source)
        self.assertEqual(len(plan["tasks"]),38)
        self.assertEqual([len(m["task_ids"]) for m in plan["milestones"]],[7,6,11,9,5])
        covered=[source_id for task in plan["tasks"] for source_id in task["source_task_ids"]]
        self.assertEqual(len(covered),58)
        self.assertEqual(set(covered),{task["id"] for task in source["tasks"]})
        self.assertEqual(len(covered),len(set(covered)))
        order=plan["topological_order"]
        self.assertEqual(len(order),38)
        for task in plan["tasks"]:
            self.assertEqual(task["gates"],[])
            self.assertTrue(all(order.index(dep)<order.index(task["id"]) for dep in task["dependencies"]))
        by_id={task["id"]:task for task in plan["tasks"]}
        self.assertLess(order.index("A2a"),order.index("A3"))
        self.assertLess(order.index("A3"),order.index("A2b"))
        self.assertLess(order.index("C3a"),order.index("C2"))
        self.assertLess(order.index("C2"),order.index("C3b"))
        self.assertNotIn("E4",by_id["D6"]["dependencies"])
        self.assertTrue({"D2","D3","D4","D5","D9"} <= set(by_id["D6"]["dependencies"]))

    def test_github_seed_is_complete_and_dry_run_only(self):
        plan=reduce_guide(read(ROOT/"fixtures/guide-tasks.json"))
        seed=github_issue_seed(plan)
        self.assertTrue(seed["dry_run_only"])
        self.assertEqual(len(seed["milestones"]),5)
        self.assertEqual(len(seed["issues"]),38)
        self.assertEqual({issue["local_task_id"] for issue in seed["issues"]},{task["id"] for task in plan["tasks"]})
        self.assertTrue(all("Link commits and pull request" in issue["body"] for issue in seed["issues"]))
        github_text=json.dumps({"milestones":seed["milestones"],"issues":seed["issues"],"governance":seed["governance"]},ensure_ascii=False)
        self.assertIsNone(re.search(r"[\u0600-\u06ff]",github_text),"GitHub-facing task content must be English")
        self.assertIn("explicit repository scope",seed["governance"]["external_mutation"])

    def test_redaction_and_strict_unknown_fields(self):
        with patch.dict(os.environ,{"RUNPOD_API_KEY":"fixture-secret-value"}):
            result=redact("fixture-secret-value token=other-secret Bearer abc123")
            self.assertNotIn("fixture-secret-value",result); self.assertNotIn("other-secret",result); self.assertNotIn("abc123",result)
        m=read(ROOT/"fixtures/execution-manifest.json"); m["shell"]="arbitrary text"
        with self.assertRaises(ContractError): validate(m,"execution")

    def test_installer_profiles_preserve_modified_files(self):
        spec=importlib.util.spec_from_file_location("profile_installer",ROOT/"installers/install.py")
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="installer spaces ") as t,contextlib.redirect_stdout(io.StringIO()):
            target=Path(t)/"skills target"
            preview=module.install("controller",target)
            self.assertTrue(preview["dry_run"]); self.assertFalse(target.exists())
            module.install("controller",target,dry_run=False)
            file=target/"thesis-workflow-control/SKILL.md"; file.write_text("user-modified")
            with self.assertRaises(FileExistsError): module.install("controller",target,dry_run=False)
            self.assertEqual(file.read_text(),"user-modified")
            wrappers=list(target.glob("*/scripts/*.py"))
            for wrapper in wrappers:
                proc=subprocess.run([sys.executable,str(wrapper),"--help"],capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
        with self.assertRaises(ValueError): module.install("controller",Path.home()/".codex/skills")

    def test_helpers_help(self):
        scripts=list((ROOT/"skills").glob("*/scripts/*.py"))+list((ROOT/"installers").glob("*.py"))+list((ROOT/"tools").glob("*.py"))+list((ROOT/"fixtures/scripts").glob("*.py"))
        for script in scripts:
            with self.subTest(script=script.name):
                p=subprocess.run([sys.executable,str(script),"--help"],capture_output=True,text=True,timeout=30)
                self.assertEqual(p.returncode,0,p.stderr)
        for module in ("control","guide","research","design","compute","analysis","audit","writing","runpod","smoke","validate_bundle"):
            with self.subTest(module=module):
                p=subprocess.run([sys.executable,"-m","thesis_agents",module,"--help"],capture_output=True,text=True,timeout=30)
                self.assertEqual(p.returncode,0,p.stderr)

    def test_actual_local_noop_and_approval_provenance(self):
        from thesis_agents.compute import dispatch
        from thesis_agents.common import object_digest
        from datetime import datetime,timedelta,timezone
        with tempfile.TemporaryDirectory(prefix="local CPU spaces ") as t:
            root=Path(t); repo=root/"reviewed repo"; (repo/"scripts").mkdir(parents=True)
            script=repo/"scripts/noop.py"; shutil.copyfile(ROOT/"fixtures/scripts/noop.py",script)
            for args in (["init","--quiet"],["add","scripts/noop.py"],["-c","user.name=Test","-c","user.email=fixture@example.invalid","commit","-qm","Synthetic fixture"]):
                subprocess.run(["git","-C",str(repo),*args],check=True,capture_output=True)
            m=read(ROOT/"fixtures/execution-manifest.json"); m["execution_target"]="local"; m["script_sha256"]=digest(script)
            m["git_commit"]=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
            current=datetime.now(timezone.utc)
            a={"schema_version":"1.0","experiment_id":m["experiment_id"],"run_id":m["run_id"],"execution_target":"local","manifest_sha256":object_digest(m),"decision":"approve","timestamp":(current-timedelta(seconds=1)).isoformat(),"expires_at":(current+timedelta(minutes=2)).isoformat(),"max_seconds":30,"max_usd":0,"actor":"SYNTHETIC TEST ONLY","source_ref":"offline-unittest"}
            result=dispatch(m,repo,root/"artifacts",True,a)
            self.assertEqual(result["status"],"completed",result)
            self.assertEqual(result["exit_status"],0)
            self.assertEqual(len(result["output_artifacts"]),1)
            self.assertEqual(result["approval_reference"],object_digest(a))
            validate(result,"run")

    def test_python311_syntax_and_all_schema_definitions(self):
        import ast
        from jsonschema import Draft202012Validator
        for file in (ROOT/"src").rglob("*.py"):
            ast.parse(file.read_text(encoding="utf-8"),feature_version=(3,11))
        for file in (ROOT/"src/thesis_agents/schemas").glob("*.json"):
            Draft202012Validator.check_schema(read(file))

    def test_workflow_install_uses_real_cli_for_both_packages(self):
        spec=importlib.util.spec_from_file_location("workflow_installer",ROOT/"installers/install_workflows.py")
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix="workflow install spaces ") as t:
            self.assertTrue(module.install(t)["dry_run"])
            self.assertFalse((Path(t)/".specify").exists())
            result=module.install(t,True)
            self.assertFalse(result["dry_run"])
            for name in ("thesis-smoke","thesis-lifecycle"):
                self.assertTrue((Path(t)/".specify/workflows"/name/"workflow.yml").is_file())

if __name__=="__main__": unittest.main()
