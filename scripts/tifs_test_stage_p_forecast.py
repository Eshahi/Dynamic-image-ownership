"""Pure metadata/journal Stage P forecast integration tests.

The real materializer and journal summarizer validate all first-two-source
inventories. Opaque .bin bytes stand in for artifacts; no image is generated,
decoded, or inspected. Gradient/parity/memory/timing receipts are synthetic
metadata, not evidence that numerical checks or a GPU run actually passed.
Only external choice reads and disk capacity are mocked. Choice fixtures stay
in memory and are never written as approval files.
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
import tifs_stage_p as p
import tifs_stage_s_forecast as forecast


TRIALS = ("retained-f5", "f6-noise-p52", "f6-x0-p52")
START = "2026-01-01T00:00:00Z"
EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
GIB = 1024**3


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_rows(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


class CalibrationFixture:
    """Build complete three-trial byte-bound journals without science imports."""
    def __init__(self, root, stack, hours=15):
        self.root = Path(root)
        self.choice_path = self.root / "unwritten-synthetic-choice.json"
        self.choice = dict(schema="tifs-round3-user-choice-v1", decision="approve", recorded_by="Claude",
            config_sha256=common.sha256_file(p.BASE), gate_profile="round1", stage_p="run",
            k3_optimization="excluded", before_server_outputs=True,
            user_decision_reference="SYNTHETIC UNIT TEST; NOT A HUMAN DECISION", max_instance_hours=hours)
        original_load, original_hash = common.load_json, common.sha256_file
        stack.enter_context(patch.object(common, "load_json", side_effect=lambda path:
            copy.deepcopy(self.choice) if Path(path) == self.choice_path else original_load(path)))
        stack.enter_context(patch.object(common, "sha256_file", side_effect=lambda path:
            p.digest(self.choice) if Path(path) == self.choice_path else original_hash(path)))
        stack.enter_context(patch.object(forecast.shutil, "disk_usage", return_value=SimpleNamespace(
            free=800*GIB, total=1000*GIB)))
        self.memory = dict(device_total_bytes=48*GIB, device_used_bytes=4*GIB,
                           reserved_bytes=3*GIB, max_reserved_bytes=4*GIB)
        self.code_path = self.root / "fixture-code.txt"
        self.code_path.write_text("Synthetic code identity, never executed.\n", encoding="utf-8")
        self.profile_path = self.root / "fixture-profile.json"
        self.profile_path.write_text('{"fixture":true}\n', encoding="utf-8")
        self.configs = {}
        for trial in TRIALS:
            self.build_trial(trial, hours)

    def out(self, trial=TRIALS[-1]):
        return self.root / "tune" / trial

    def run(self, elapsed=100):
        return forecast.forecast_stage_p(self.root, p.BASE, self.choice_path, START, EPOCH+elapsed)

    def build_trial(self, trial, hours):
        out = self.out(trial)
        out.mkdir(parents=True)
        config = p.materialize(p.BASE, p.HERE / "source-manifest.json", self.choice_path, trial)
        self.configs[trial] = config
        common.atomic_json(out / "config.json", config)
        identity = dict(config_sha256=common.sha256_file(out / "config.json"),
            effective_config_sha256=p.digest(config), source_manifest_sha256=config["stage_p"]["source_manifest_sha256"],
            code={str(self.code_path): common.sha256_file(self.code_path)},
            profiles={str(self.profile_path): common.sha256_file(self.profile_path)},
            packages={"synthetic-package": "fixture-only"}, device=dict(name="SYNTHETIC GPU", capability=[8, 9], total_bytes=48*GIB),
            instance_start_utc="2026-01-01T00:00:00+00:00", rehearsal=False, max_hours=hours)
        common.atomic_json(out / "identity.json", identity)
        source_rows = config["stage_p"]["sources"]
        common.atomic_json(out / "prepared.json", dict(donors=[str(r["source_id"]) for r in source_rows],
            targets=[], sources={str(r["source_id"]): r for r in source_rows}))
        artifact = out / "opaque.bin"
        artifact.write_bytes(b"opaque unit-test bytes, not image data")
        output = dict(path=str(artifact), sha256=common.sha256_file(artifact))
        tape = [dict(shape=[1], dtype="fixture", sha256=output["sha256"], bytes=1)]
        arm = config["candidate"]
        groups = {name: [] for name in ("clean", "native", "detect", "quality", "checks")}
        def timed(row, label, stage):
            return dict(**row, operation=label, invocation=trial+":"+stage, seconds=.01, memory=dict(self.memory))
        def raw(positive):
            return dict(semantic=dict(read=positive, content_match=positive, decoded_code=1, found=positive),
                        instance=dict(read=positive, decoded_code=2, found=positive), outcome="both_match" if positive else "no_match")
        for source in source_rows[:2]:
            sid = str(source["source_id"])
            for writer in config["arms"]:
                marked = writer != "unmarked"
                payload = dict(q=1, h=2) if marked else None
                for cell, seed in [(None, None)] + [(cell, seed) for cell in p.CELLS for seed in config["seeds"]]:
                    kind = "clean" if cell is None else "native"
                    uid = f"clean:{sid}:{writer}" if cell is None else f"native:{cell}:{sid}:{seed}:{writer}"
                    row = dict(id=uid, status="ok", kind=kind, source=sid, arm=writer, payload=payload, output=output)
                    if cell:
                        family = cell.split("-")[0]
                        row.update(cell=cell, family=family, seed=seed, input=output)
                        if marked:
                            row.update(replay_tape_receipt=tape, replay_tape_consumed=True)
                        else:
                            row.update(tape=output, tape_receipt=tape, native_parity=dict(status="ok", exact_rgb8=True))
                            if family in ("R0", "R1") and seed == 0:
                                row["x0_native_first_step_parity"] = dict(status="ok", exact_conditioning=True)
                    groups[kind].append(timed(row, "clean_"+writer if cell is None else "native_"+family, kind))
                    calls = {owner: dict(status="ok", raw=raw(marked and role == "positive")) for role, owner in config["owners"].items()}
                    groups["detect"].append(timed(dict(id=f"det:{arm}:{uid}", status="ok", kind="detect", item=uid,
                        source=sid, arm=writer, input_sha256=output["sha256"], calls=calls), "detect_"+arm, "detect"))
                    metrics = dict(psnr_db=45, ssim_rgb=.96, lpips=.02)
                    if not marked and cell is None:
                        metrics.update(psnr_db=None, psnr_infinite=True)
                    groups["quality"].append(timed(dict(id="quality:"+uid, status="ok", kind="quality", item=uid,
                        source=sid, arm=writer, input_sha256=output["sha256"], total=metrics, reference_source=sid), "quality", "quality"))
            if trial != "retained-f5":
                path = out / ("synthetic-gradient-"+sid+".json")
                common.atomic_json(path, dict(status="ok", gradient_checks=[dict(synthetic=True)], clean_input_gradient_norm=1))
                groups["checks"].append(timed(dict(id="writer-check:"+sid, status="ok", kind="writer-rehearsal", source=sid,
                    output=dict(path=str(path), sha256=common.sha256_file(path))), "writer_rehearsal", "clean"))
        names = dict(clean="clean.jsonl", native="native.jsonl", detect="detect-"+arm+"-0-of-1.jsonl",
                     quality="quality-0-of-1.jsonl", checks="rehearsal-checks.jsonl")
        for key, rows in groups.items():
            write_rows(out / names[key], rows)
        events = []
        loads = dict(clean=["load_"+arm, "load_unmarked"], native=["load_R0", "load_R1", "load_K3"],
                     detect=["load_reader"], quality=["load_quality"], prepare=[])
        for stage, labels in loads.items():
            invocation = trial+":"+stage
            events.append(dict(event="INVOCATION_START", invocation=invocation, epoch=EPOCH+1, stage=stage))
            for label in labels:
                events.append(dict(event="MODEL_READY", invocation=invocation, label=label, load_seconds=.01, memory=dict(self.memory)))
            units = sum(row["seconds"] for rows in groups.values() for row in rows if row["invocation"] == invocation)
            events.append(dict(event="INVOCATION_END", invocation=invocation, seconds=units+.1, status="ok"))
        write_rows(out / "invocations.jsonl", events)


class StagePForecastTests(unittest.TestCase):
    def fixture(self, stack, hours=15):
        directory = stack.enter_context(tempfile.TemporaryDirectory())
        return CalibrationFixture(directory, stack, hours)

    def test_complete_real_journal_summaries_and_default_cap(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            for trial in TRIALS:
                summary = p.summarize_trial(fixture.out(trial), fixture.configs[trial], count=2, calibration=True)
                self.assertEqual(summary["status"], "COMPLETE")
                self.assertEqual(len(summary["sources"]), 2)
            result = fixture.run()
            self.assertEqual(result["status"], "GO")
            self.assertEqual(result["ceiling_seconds"], 15*3600)
            self.assertEqual(set(result["calibration_identity_sha256"]), set(TRIALS))
            self.assertGreater(result["projected_stage_p_seconds"], 0)
            self.assertTrue(result["upper_inventory"])
            self.assertEqual(result["retrieval_reserve_seconds"], 3600)
            self.assertFalse(fixture.choice_path.exists())

    def test_actual_clock_and_explicit_cap_drive_resource_stop(self):
        for hours, expected in ((15, "RESOURCE_STOP"), (126, "GO")):
            with self.subTest(hours=hours), ExitStack() as stack:
                fixture = self.fixture(stack, hours)
                result = fixture.run(elapsed=16*3600)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["elapsed_instance_seconds"], 16*3600)
                self.assertEqual(result["ceiling_seconds"], hours*3600)

    def test_retained_resource_stop_short_circuits_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RESOURCE_STOP-fixture.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(forecast.forecast_stage_p(root, None, None, None, None)["status"], "RESOURCE_STOP")

    def test_missing_operation_and_model_load_labels_fail_closed(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            required = ("clean_f6-noise", "clean_f6-x0", "clean_f5-r2", "clean_unmarked", "native_R0", "native_R1", "native_K3",
                        "detect_f6-noise", "detect_f6-x0", "detect_f5-r2", "quality", "prepare", "load_f6-noise", "load_f6-x0",
                        "load_f5-r2", "load_R0", "load_R1", "load_K3", "load_reader", "load_quality")
            originals = {path: read_rows(path) for path in fixture.root.glob("tune/*/*.jsonl")}
            for label in required:
                with self.subTest(label=label):
                    for path, rows in originals.items():
                        changed = copy.deepcopy(rows)
                        for row in changed:
                            if row.get("operation") == label:
                                row["operation"] = "unregistered-operation"
                            if row.get("event") == "MODEL_READY" and row.get("label") == label:
                                row["label"] = "unregistered-model-load"
                            if label == "prepare" and row.get("event") == "INVOCATION_START" and row.get("stage") == "prepare":
                                row["stage"] = "unregistered-stage"
                        write_rows(path, changed)
                    with self.assertRaisesRegex(ValueError, "timing bounds"):
                        fixture.run()
            for path, rows in originals.items():
                write_rows(path, rows)
            self.assertEqual(fixture.run()["status"], "GO")

    def test_incomplete_producer_reader_quality_and_second_source_gradient(self):
        for name in ("clean.jsonl", "native.jsonl", "detect-f6-x0-0-of-1.jsonl", "quality-0-of-1.jsonl", "rehearsal-checks.jsonl"):
            with self.subTest(journal=name), ExitStack() as stack:
                fixture = self.fixture(stack)
                path = fixture.out() / name
                rows = read_rows(path)
                write_rows(path, rows[:-1])
                with self.assertRaises((ValueError, KeyError)):
                    fixture.run()

    def test_operation_timing_must_belong_to_recorded_invocation(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            path = fixture.out() / "clean.jsonl"
            original = read_rows(path)
            for changes in ({"operation": None}, {"seconds": 0}, {"invocation": None}, {"invocation": "unrecorded-invocation"}):
                with self.subTest(changes=changes):
                    rows = copy.deepcopy(original)
                    rows[-1].update(changes)
                    write_rows(path, rows)
                    with self.assertRaises(ValueError): fixture.run()

    def test_second_source_native_replay_and_x0_parity_required(self):
        for field in ("native_parity", "x0_native_first_step_parity"):
            with self.subTest(field=field), ExitStack() as stack:
                fixture = self.fixture(stack)
                path = fixture.out() / "native.jsonl"
                rows = read_rows(path)
                sid = str(fixture.configs[TRIALS[-1]]["stage_p"]["sources"][1]["source_id"])
                row = next(r for r in rows if r["source"] == sid and r["arm"] == "unmarked" and r["cell"] == "R1-0.2" and r["seed"] == 0)
                row.pop(field)
                write_rows(path, rows)
                with self.assertRaisesRegex(ValueError, "parity|native replay"):
                    fixture.run()

    def test_second_source_gradient_receipt_status_and_positive_numeric_norm(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            journal = fixture.out() / "rehearsal-checks.jsonl"
            original_rows = read_rows(journal)
            receipt_path = Path(original_rows[-1]["output"]["path"])
            original_receipt = common.load_json(receipt_path)
            for changed_status, changes in (("error_terminal", {}), ("ok", {"status": "error"}),
                                            ("ok", {"gradient_checks": []}), ("ok", {"clean_input_gradient_norm": 0}),
                                            ("ok", {"clean_input_gradient_norm": True})):
                with self.subTest(status=changed_status, changes=changes):
                    receipt = dict(original_receipt, **changes)
                    common.atomic_json(receipt_path, receipt)
                    rows = copy.deepcopy(original_rows)
                    rows[-1]["status"] = changed_status
                    rows[-1]["output"]["sha256"] = common.sha256_file(receipt_path)
                    write_rows(journal, rows)
                    with self.assertRaises(ValueError): fixture.run()

    def test_choice_clock_config_and_shared_runtime_identity_mismatch(self):
        mutations = dict(choice=lambda value: value["stage_p"].update(user_choice_sha256="0"*64),
                         config=lambda value: value.update(candidate="f6-noise"))
        for name, change in mutations.items():
            with self.subTest(change=name), ExitStack() as stack:
                fixture = self.fixture(stack)
                path = fixture.out() / "config.json"
                value = common.load_json(path)
                change(value)
                common.atomic_json(path, value)
                with self.assertRaises(ValueError): fixture.run()
        for field, value in (("instance_start_utc", "2026-01-01T00:00:01+00:00"), ("max_hours", 14),
                             ("rehearsal", True), ("device", {"name": "different"}), ("packages", {"changed": "fixture"}),
                             ("profiles", {"changed": "0"*64}), ("code", {"changed": "0"*64})):
            with self.subTest(field=field), ExitStack() as stack:
                fixture = self.fixture(stack)
                path = fixture.out() / "identity.json"
                identity = common.load_json(path)
                identity[field] = value
                common.atomic_json(path, identity)
                with self.assertRaises(ValueError): fixture.run()

    def test_changed_code_and_profile_bytes_rejected(self):
        for field in ("code_path", "profile_path"):
            with self.subTest(field=field), ExitStack() as stack:
                fixture = self.fixture(stack)
                getattr(fixture, field).write_text("Changed after calibration\n", encoding="utf-8")
                with self.assertRaises(ValueError): fixture.run()

    def test_effective_config_identity_required(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            path = fixture.out() / "identity.json"
            identity = common.load_json(path)
            identity["effective_config_sha256"] = "0"*64
            common.atomic_json(path, identity)
            with self.assertRaises(ValueError): fixture.run()

    def test_mixed_device_capacity_and_low_free_disk_fail_closed(self):
        with ExitStack() as stack:
            fixture = self.fixture(stack)
            with patch.object(forecast.shutil, "disk_usage", return_value=SimpleNamespace(free=GIB, total=1000*GIB)):
                self.assertEqual(fixture.run()["status"], "RESOURCE_STOP")
            path = fixture.out() / "native.jsonl"
            rows = read_rows(path)
            rows[0]["memory"]["device_total_bytes"] = 24*GIB
            write_rows(path, rows)
            with self.assertRaisesRegex(ValueError, "capacity changed"):
                fixture.run()


if __name__ == "__main__":
    unittest.main()
