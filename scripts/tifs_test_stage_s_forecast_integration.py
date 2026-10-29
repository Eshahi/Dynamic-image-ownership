"""Pure metadata integration tests of the complete Stage S forecast interface.

All eleven arms and both frozen rehearsal sources have complete producer,
reader and quality inventories. Artifacts contain opaque nonimage bytes;
gradient, parity, timing and memory receipts are synthetic metadata. These
tests do not establish numerical correctness, achieved quality or GPU fit.
Real config/selection loading and byte hashes are used. Only external choice
reads and disk capacity are mocked; no approval receipt is written.
"""
from contextlib import ExitStack
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tifs_common as common
import tifs_gate_profiles as gates
import tifs_stage_p as stage_p
import tifs_stage_s_forecast as forecast


BASE = stage_p.BASE
START = "2026-01-01T00:00:00Z"
EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
GIB = 1024**3


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_rows(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


class RehearsalFixture:
    def __init__(self, root, stack, selected=False, hours=15):
        self.root = Path(root)
        self.out = self.root / "rehearsal"
        self.out.mkdir()
        self.base = self.root / "research/stage-s/frozen-config.json"
        self.base.parent.mkdir(parents=True)
        self.base.write_bytes(BASE.read_bytes())  # Metadata only; same committed config bytes.
        self.choice_path = self.root / "unwritten-synthetic-choice.json"
        self.selection_path = self.base.parent.parent / "stage-p/selected-config.json"
        self.selected = selected
        self.choice = dict(schema="tifs-round3-user-choice-v1", decision="approve", recorded_by="Claude",
            config_sha256=common.sha256_file(self.base), gate_profile="round3-proposed", stage_p="run",
            k3_optimization="excluded", before_server_outputs=True,
            user_decision_reference="SYNTHETIC UNIT TEST; NOT A HUMAN DECISION", max_instance_hours=hours)
        real_load, real_hash = common.load_json, common.sha256_file
        stack.enter_context(patch.object(common, "load_json", side_effect=lambda path:
            copy.deepcopy(self.choice) if Path(path) == self.choice_path else real_load(path)))
        stack.enter_context(patch.object(common, "sha256_file", side_effect=lambda path:
            stage_p.digest(self.choice) if Path(path) == self.choice_path else real_hash(path)))
        stack.enter_context(patch.object(forecast.shutil, "disk_usage", return_value=SimpleNamespace(free=800*GIB, total=1000*GIB)))
        if selected:
            common.atomic_json(self.selection_path, dict(status="SELECTED", base_config_sha256=common.sha256_file(self.base),
                gate_profile="round3-proposed", user_choice_sha256=common.sha256_file(self.choice_path), check_status="PASS",
                candidate="f6-x0", writer_psnr_db=46, k3_optimization="excluded", execution_authorized=False,
                fixture="SYNTHETIC METADATA ONLY; NO EXPERIMENT WAS RUN"))
        self.config = gates.load_execution_config(self.base, receipt_path=self.choice_path if selected else None)
        self.manifest = common.load_json(forecast.stage.manifest_path(self.config))
        donors = [str(r["source_id"]) for r in self.manifest["rehearsal_donors"]]
        targets = [str(r["source_id"]) for r in self.manifest["rehearsal_targets"]]
        self.prepared = dict(donors=donors, targets=targets, pairs=[dict(donor=d, target=t) for d, t in zip(donors, targets)],
            sources={str(row["source_id"]): row for key in common.SOURCE_GROUPS for row in self.manifest[key]})
        common.atomic_json(self.out / "prepared.json", self.prepared)
        self.code_path = self.root / "synthetic-code.txt"
        self.code_path.write_text("Synthetic identity only, never executed.\n", encoding="utf-8")
        self.profile_path = self.root / "synthetic-profile.json"
        self.profile_path.write_text('{"synthetic":true}\n', encoding="utf-8")
        identity = dict(config_sha256=common.sha256_file(self.base), effective_config_sha256=stage_p.digest(self.config),
            source_manifest_sha256=common.sha256_file(forecast.stage.manifest_path(self.config)),
            code={str(self.code_path): common.sha256_file(self.code_path)}, profiles={str(self.profile_path): common.sha256_file(self.profile_path)},
            device=dict(name="SYNTHETIC GPU", capability=[8, 9], total_bytes=48*GIB),
            packages={"synthetic-package": "fixture-only"}, instance_start_utc="2026-01-01T00:00:00+00:00",
            rehearsal=True, max_hours=self.config["budget"]["max_instance_hours"])
        common.atomic_json(self.out / "identity.json", identity)
        self.memory = dict(device_total_bytes=48*GIB, device_used_bytes=4*GIB, reserved_bytes=3*GIB, max_reserved_bytes=4*GIB)
        artifact = self.out / "opaque.bin"
        artifact.write_bytes(b"Synthetic opaque bytes, not an image or scientific result.")
        output = dict(path=str(artifact), sha256=common.sha256_file(artifact))
        self.groups = {}
        self.expected = forecast.stage.expected_ids(self.config, self.prepared)
        def timed(row, operation, invocation):
            return dict(**row, operation=operation, invocation=invocation, seconds=.001, memory=dict(self.memory))
        for group, ids in self.expected.items():
            rows = []
            for uid in ids:
                fields = uid.split(":")
                arm = fields[-2] if group == "threats" else fields[-1]
                sid = fields[1] if group == "clean" else fields[2]
                row = dict(id=uid, status="ok", arm=arm, source=sid, output=output, kind=group)
                operation = "clean_"+arm if group == "clean" else group
                if group == "native":
                    cell = next(c for c in self.config["cells"] if c["id"] == fields[1])
                    row.update(cell=cell["id"], family=cell["family"], strength=cell["strength"], seed=int(fields[3]))
                    operation = "native_"+cell["family"]
                    if forecast.stage.c0(arm):
                        row["native_parity"] = dict(status="ok", exact_rgb8=True)
                        if cell["family"] in ("R0", "R1") and row["seed"] == self.config["seeds"][0]:
                            row["x0_native_first_step_parity"] = dict(status="ok", exact_conditioning=True)
                rows.append(timed(row, operation, group))
            self.groups[group] = rows
            write_rows(self.out / (group+".jsonl"), rows)
        producers = [row for rows in self.groups.values() for row in rows]
        for method in (arm for arm in self.config["arms"] if not forecast.stage.c0(arm)):
            name = "detect-"+method
            rows = [timed(dict(id="det:"+method+":"+row["id"], status="ok", item=row["id"], arm=row["arm"], source=row["source"],
                              input_sha256=output["sha256"], artifact_required=False), "detect_"+method, "detect")
                    for row in producers if row["arm"] == method or forecast.stage.c0(row["arm"])]
            self.groups[name] = rows
            write_rows(self.out / (name+"-0-of-1.jsonl"), rows)
        rows = [timed(dict(id="quality:"+row["id"], status="ok", item=row["id"], arm=row["arm"], source=row["source"],
                          input_sha256=output["sha256"], artifact_required=False), "quality", "quality") for row in producers]
        self.groups["quality"] = rows
        write_rows(self.out / "quality-0-of-1.jsonl", rows)
        checks = []
        for sid in donors:
            path = self.out / ("synthetic-gradient-"+sid+".json")
            common.atomic_json(path, dict(status="ok", gradient_checks=[dict(synthetic=True)], clean_input_gradient_norm=1))
            checks.append(timed(dict(id="writer-check:"+sid, kind="writer-rehearsal", status="ok", source=sid,
                output=dict(path=str(path), sha256=common.sha256_file(path))), "writer_rehearsal", "clean"))
        write_rows(self.out / "rehearsal-checks.jsonl", checks)
        events = []
        loads = dict(prepare=[], clean=["load_"+arm for arm in self.config["arms"]], native=["load_R0", "load_R1", "load_K3"],
                     threats=["load_threats"], secondary=[], detect=["load_reader"], quality=["load_quality"])
        for group, labels in loads.items():
            events.append(dict(event="INVOCATION_START", invocation=group, epoch=EPOCH+1, stage=group))
            for label in labels:
                events.append(dict(event="MODEL_READY", invocation=group, label=label, load_seconds=.001, memory=dict(self.memory)))
            duration = sum(row["seconds"] for rows in self.groups.values() for row in rows if row["invocation"] == group)
            if group == "clean":
                duration += sum(row["seconds"] for row in checks)
            events.append(dict(event="INVOCATION_END", invocation=group, seconds=duration+.1, status="ok"))
        write_rows(self.out / "invocations.jsonl", events)

    def run(self, elapsed=100, explicit_selection=False):
        return forecast.forecast(self.out, self.base, START, EPOCH+elapsed,
            receipt_path=self.choice_path if self.selected else None,
            selection_path=self.selection_path if explicit_selection else None)


class StageSForecastIntegrationTests(unittest.TestCase):
    def fixture(self, stack, **kwargs):
        return RehearsalFixture(stack.enter_context(tempfile.TemporaryDirectory()), stack, **kwargs)

    def test_full_eleven_arm_default_round1_inventory_go(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            self.assertEqual(len(fixture.config["arms"]), 11)
            self.assertEqual(len(fixture.prepared["donors"]), 2)
            self.assertEqual(fixture.config["gate_profile"], "round1")
            self.assertEqual(fixture.config["candidate"], "f6-noise")
            result = fixture.run()
            self.assertEqual(result["status"], "GO")
            self.assertEqual(result["ceiling_seconds"], 15*3600)
            for key, rows in fixture.expected.items():
                self.assertEqual(len(rows), fixture.config["inventory"]["rehearsal_"+key] if key != "clean" else
                    fixture.config["inventory"]["rehearsal_marked_clean"]+fixture.config["inventory"]["rehearsal_unmarked_clean"])
            self.assertIn("detect-f6-x0", result["measurement_groups"])
            self.assertIn("detect-f5-budget", result["measurement_groups"])
            self.assertFalse(fixture.choice_path.exists())

    def test_proposed_selected_x0_46_default_and_explicit_resolution(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack, selected=True, hours=126)
            self.assertEqual(fixture.config["gate_profile"], "round3-proposed")
            self.assertEqual(fixture.config["candidate"], "f6-x0")
            self.assertEqual(fixture.config["writer"]["psnr_db"], 46)
            self.assertEqual(fixture.config["execution_choices"]["selected_config_sha256"], common.sha256_file(fixture.selection_path))
            automatic = fixture.run(elapsed=16*3600)
            self.assertEqual(automatic["status"], "GO")
            self.assertEqual(automatic["ceiling_seconds"], 126*3600)
            self.assertEqual(automatic["elapsed_instance_seconds"], 16*3600)
            self.assertEqual(automatic, fixture.run(elapsed=16*3600, explicit_selection=True))
            self.assertFalse(fixture.choice_path.exists())
            self.assertEqual(fixture.run(elapsed=126*3600)["status"], "RESOURCE_STOP")

    def test_writer_check_peak_is_included_after_later_unit_resets(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            path = fixture.out / "rehearsal-checks.jsonl"
            rows = read_rows(path)
            rows[-1]["memory"].update(device_used_bytes=47*GIB, reserved_bytes=47*GIB, max_reserved_bytes=47*GIB)
            write_rows(path, rows)
            result = fixture.run()
            self.assertEqual(result["status"], "RESOURCE_STOP")
            self.assertEqual(result["capacity"]["peak_device_bytes"], 47*GIB)
            self.assertFalse(result["capacity"]["gpu_ok"])

    def test_missing_and_invalid_second_writer_checks_fail_closed(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            path = fixture.out / "rehearsal-checks.jsonl"
            original = read_rows(path)
            write_rows(path, original[:-1])
            with self.assertRaisesRegex(ValueError, "gradient/projection"): fixture.run()
            receipt_path = Path(original[-1]["output"]["path"])
            receipt = common.load_json(receipt_path)
            for changes in ({"clean_input_gradient_norm": 0}, {"clean_input_gradient_norm": -1},
                            {"clean_input_gradient_norm": True}, {"clean_input_gradient_norm": "1"}, {"gradient_checks": []}):
                with self.subTest(changes=changes):
                    common.atomic_json(receipt_path, dict(receipt, **changes))
                    rows = copy.deepcopy(original)
                    rows[-1]["output"]["sha256"] = common.sha256_file(receipt_path)
                    write_rows(path, rows)
                    with self.assertRaisesRegex(ValueError, "gradient receipt"): fixture.run()
            # A valid JSON number that overflows float must also fail at strict loading.
            receipt_path.write_text('{"status":"ok","gradient_checks":[true],"clean_input_gradient_norm":1e999}\n', encoding="utf-8")
            rows[-1]["output"]["sha256"] = common.sha256_file(receipt_path)
            write_rows(path, rows)
            with self.assertRaises(ValueError): fixture.run()

    def test_source_manifest_prepared_pairs_and_native_parity_bound(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            prepared_path = fixture.out / "prepared.json"
            prepared = common.load_json(prepared_path)
            changed = copy.deepcopy(prepared)
            changed["donors"][1] = "undeclared-source"
            common.atomic_json(prepared_path, changed)
            with self.assertRaisesRegex(ValueError, "frozen donors"): fixture.run()
            changed = copy.deepcopy(prepared)
            changed["pairs"] = changed["pairs"][:1]
            common.atomic_json(prepared_path, changed)
            with self.assertRaisesRegex(ValueError, "sealed rehearsal pairs"): fixture.run()
            common.atomic_json(prepared_path, prepared)
            path = fixture.out / "native.jsonl"
            original = read_rows(path)
            for field in ("native_parity", "x0_native_first_step_parity"):
                rows = copy.deepcopy(original)
                row = next(r for r in rows if r["arm"] == "unmarked" and r["source"] == prepared["donors"][1] and r["cell"] == "R1-0.2" and r["seed"] == 0)
                row.pop(field)
                write_rows(path, rows)
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, "parity"): fixture.run()

    def test_selected_choice_and_effective_config_changes_rejected(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack, selected=True, hours=126)
            selection = common.load_json(fixture.selection_path)
            changed = dict(selection, writer_psnr_db=42)
            common.atomic_json(fixture.selection_path, changed)
            with self.assertRaisesRegex(ValueError, "effective profile/selection/choice"): fixture.run()
            common.atomic_json(fixture.selection_path, selection)
            fixture.choice["max_instance_hours"] = 125
            with self.assertRaisesRegex(ValueError, "selection is incomplete"): fixture.run()

    def test_identity_cap_and_measured_device_total_are_bound(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            path = fixture.out / "identity.json"
            original = common.load_json(path)
            for changes in ({"max_hours": 126}, {"device": dict(original["device"], total_bytes=24*GIB)},
                            {"source_manifest_sha256": "0"*64}, {"instance_start_utc": "2026-01-01T00:00:01+00:00"}):
                with self.subTest(changes=changes):
                    common.atomic_json(path, dict(original, **changes))
                    with self.assertRaises(ValueError): fixture.run()
            common.atomic_json(path, original)
            checks = fixture.out / "rehearsal-checks.jsonl"
            rows = read_rows(checks)
            rows[-1]["memory"]["device_total_bytes"] = 24*GIB
            write_rows(checks, rows)
            with self.assertRaisesRegex(ValueError, "capacity changed"): fixture.run()

    def test_missing_inventory_and_changed_artifact_or_profile_rejected(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            for name in ("clean.jsonl", "native.jsonl", "secondary.jsonl", "threats.jsonl", "detect-f5-budget-0-of-1.jsonl", "quality-0-of-1.jsonl"):
                with self.subTest(journal=name):
                    path = fixture.out / name
                    rows = read_rows(path)
                    write_rows(path, rows[:-1])
                    with self.assertRaisesRegex(ValueError, "Incomplete/failed"): fixture.run()
                    write_rows(path, rows)
            artifact = fixture.out / "opaque.bin"
            original = artifact.read_bytes()
            artifact.write_bytes(b"Changed opaque bytes")
            with self.assertRaisesRegex(ValueError, "Missing/corrupt"): fixture.run()
            artifact.write_bytes(original)
            fixture.profile_path.write_text("Changed profile bytes", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "code changed"): fixture.run()


if __name__ == "__main__":
    unittest.main()
