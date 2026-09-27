"""Model-free exact operation-ledger checks; discovery includes no scientific reruns."""
import unittest
from scripts.summarize_c4_checkpoint_run import journal_evidence


def fixture():
    rows = [{"phase": "source_enrollment"}]
    def boundary(phase, name, **values): rows.append({"phase": phase, "operation": name, **values})
    def both(name, **values):
        boundary("operation_started", name, **values); boundary("operation_completed", name, **values)
    def render(name, **values):
        boundary("operation_started", name, **values)
        both("scheduler_add_noise")
        for timestep in [101, 1]:
            both("unet_forward", timestep=timestep); both("scheduler_step", timestep=timestep)
        both("vae_decode"); boundary("operation_completed", name, **values)
    both("idle_components_to_cpu")
    boundary("operation_started", "source_encoding"); both("vae_encode")
    boundary("operation_completed", "source_encoding")
    render("matched_control_render")
    for i in [0, 1]:
        render("optimization_render", iteration=i)
        for name in ["objective", "backward_and_gradient_check", "optimizer_step", "perturbation_projection"]:
            both(name, iteration=i)
        rows.append({"phase": "pre_update_loss_post_projection_norm", "iteration": i,
                     "gradient_norm": 0.004, "perturbation_norm": 0.01})
    render("final_render"); both("final_objective")
    rows.append({"phase": "final", "iteration": 2, "perturbation_norm": 0.01})
    both("active_components_to_cpu_and_safety_to_cuda")
    for kind in ["matched_control", "marked_candidate"]:
        rows.extend([{"phase": "png_saved_before_safety", "kind": kind},
                     {"phase": "output_safety_completed", "kind": kind}])
    return rows


class LedgerTests(unittest.TestCase):
    def test_complete_is_one_trial_not_two_seeds(self):
        result = journal_evidence(fixture())
        self.assertEqual(result["independent_trials"], 1)
        self.assertEqual(result["recorded_updates"], 2)
        self.assertEqual(result["scalar_gradient_aggregation"], "not_preregistered_not_computed")

    def test_missing_balanced_operation_rejected(self):
        rows = [r for r in fixture() if r.get("operation") != "optimizer_step"]
        with self.assertRaises(ValueError): journal_evidence(rows)

    def test_unknown_balanced_operation_rejected(self):
        rows = fixture() + [{"phase": p, "operation": "invented"}
                            for p in ["operation_started", "operation_completed"]]
        with self.assertRaises(ValueError): journal_evidence(rows)

    def test_wrong_step_rejected(self):
        rows = fixture(); next(r for r in rows if "timestep" in r)["timestep"] = 999
        with self.assertRaises(ValueError): journal_evidence(rows)

    def test_zero_and_nonfinite_gradients_rejected(self):
        for value in [0, float("nan"), float("inf"), True]:
            rows = fixture(); next(r for r in rows if "gradient_norm" in r)["gradient_norm"] = value
            with self.assertRaises(ValueError): journal_evidence(rows)

    def test_missing_final_or_safety_rejected(self):
        for phase in ["final", "output_safety_completed"]:
            rows = [r for r in fixture() if r["phase"] != phase]
            with self.assertRaises(ValueError): journal_evidence(rows)

    def test_projection_bound_rejected(self):
        rows = fixture(); next(r for r in rows if "gradient_norm" in r)["perturbation_norm"] = 0.02
        with self.assertRaises(ValueError): journal_evidence(rows)


if __name__ == "__main__": unittest.main()
