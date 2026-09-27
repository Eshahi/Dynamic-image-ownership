"""Owned operation-ledger fixtures, no study pixels/models/GPU execution."""
import copy
import unittest
from scripts.summarize_c4_residency_failure import journal_evidence

class ResidencyAnalysisTests(unittest.TestCase):
    def setUp(self):
        def operation(name, phase, **extra): return {"phase": "operation_"+phase, "operation": name, **extra}
        self.rows = [{"phase": "source_enrollment"},
                     {"phase": "residency_resources_before_idle", "resources": {"current_torch_allocated_bytes": 6, "current_torch_reserved_bytes": 7}},
                     operation("idle_components_to_cpu", "started"), operation("idle_components_to_cpu", "completed"),
                     {"phase": "residency_resources_after_idle", "resources": {"current_torch_allocated_bytes": 4, "current_torch_reserved_bytes": 7}},
                     operation("matched_control_render", "started"), operation("vae_decode", "started"),
                     operation("vae_decode", "completed"), operation("matched_control_render", "completed"),
                     operation("optimization_render", "started", iteration=0),
                     operation("scheduler_step", "started", timestep=1),
                     operation("scheduler_step", "completed", timestep=1), operation("vae_decode", "started")]

    def test_observed_boundaries_not_kernel_or_zero_gradient(self):
        result = journal_evidence(self.rows)
        self.assertEqual(result["observed_idle_allocation_reduction_bytes"], 2)
        self.assertEqual(result["last_completed_operation"], {"operation": "scheduler_step", "timestep": 1})
        self.assertIsNone(result["gradient_norm"])
        self.assertEqual(result["unrecorded_internal_progress"], "unknown")
        self.assertIn("asynchronous", result["faulting_kernel"])

    def test_missing_swapped_or_alias_completed_boundary_rejected(self):
        for index in (0, 2, 3, 7, 8, 12):
            rows = copy.deepcopy(self.rows); del rows[index]
            with self.subTest(index=index), self.assertRaises(ValueError): journal_evidence(rows)
        rows = copy.deepcopy(self.rows); rows[-2]["timestep"] = 2
        with self.assertRaises(ValueError): journal_evidence(rows)
        rows = copy.deepcopy(self.rows); rows[-4]["iteration"] = False
        with self.assertRaises(ValueError): journal_evidence(rows)

    def test_added_update_or_gradient_not_silently_ignored(self):
        for row in ({"phase": "optimization_update", "gradient_norm": 0}, {"phase": "made_up"}):
            with self.assertRaises(ValueError): journal_evidence([*self.rows, row])

    def test_missing_bad_or_duplicate_resource_rejected(self):
        rows = copy.deepcopy(self.rows); rows[1]["resources"]["current_torch_allocated_bytes"] = True
        with self.assertRaises(ValueError): journal_evidence(rows)
        with self.assertRaises(ValueError): journal_evidence([*self.rows[:2], self.rows[1], *self.rows[2:]])
        rows = copy.deepcopy(self.rows); del rows[4]
        with self.assertRaises(ValueError): journal_evidence(rows)

if __name__ == "__main__": unittest.main()
