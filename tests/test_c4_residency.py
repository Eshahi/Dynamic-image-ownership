"""Owned module/device labels only: no Torch/GPU/models/weights or science."""
import unittest
from types import SimpleNamespace
from src.embedding.residency import PhaseResidency
from src.embedding.proposed import EmbeddingError, operation_phase


class Value:
    def __init__(self, device="cuda:0", dtype="torch.float32"):
        self.device, self.dtype, self.requires_grad = device, dtype, False


class Module:
    def __init__(self):
        self.weight, self.buffer = Value(), Value(dtype="torch.int64")
        self.calls, self.training = [], False
    def parameters(self): return iter((self.weight,))
    def buffers(self): return iter((self.buffer,))
    def to(self, *, device):
        self.calls.append(device)
        self.weight.device = self.buffer.device = device
        return self


def owned_models():
    pipeline = SimpleNamespace(**{n:Module() for n in ("vae","unet","text_encoder","safety_checker")})
    return SimpleNamespace(pipeline=pipeline,components=SimpleNamespace(vae=pipeline.vae,
        unet=pipeline.unet,condition=Value()))


class ResidencyTests(unittest.TestCase):
    def test_phase_residency_no_active_transfer_until_safety(self):
        models=owned_models(); rows=[]; plan=PhaseResidency(models,progress=rows.append)
        condition=models.components.condition
        plan.park_idle()
        self.assertEqual(plan.state,"optimization")
        for n in ("vae","unet"): self.assertEqual(getattr(models.pipeline,n).calls,[])
        for n in ("text_encoder","safety_checker"): self.assertEqual(getattr(models.pipeline,n).calls,["cpu"])
        self.assertIs(models.components.condition,condition)
        self.assertEqual(condition.device,"cuda:0")
        plan.prepare_safety()
        self.assertEqual(plan.state,"safety")
        self.assertEqual(models.pipeline.safety_checker.calls,["cpu","cuda:0"])
        self.assertEqual(models.pipeline.text_encoder.calls,["cpu"])
        self.assertEqual(len(rows),4)
        with self.assertRaises(EmbeddingError): plan.park_idle()
        with self.assertRaises(EmbeddingError): plan.prepare_safety()

    def test_invalid_profiles_and_early_safety_rejected(self):
        for attr,value in (("dtype","torch.float16"),("dtype","torch.bfloat16"),
                           ("requires_grad",True),("device","cpu")):
            models=owned_models();setattr(models.pipeline.vae.weight,attr,value)
            with self.assertRaises(EmbeddingError): PhaseResidency(models)
        models=owned_models();models.pipeline.text_encoder.training=True
        with self.assertRaises(EmbeddingError): PhaseResidency(models)
        models=owned_models();models.components.condition=Value(device="cpu")
        with self.assertRaises(EmbeddingError): PhaseResidency(models)
        with self.assertRaises(EmbeddingError): PhaseResidency(owned_models()).prepare_safety()

    def test_failed_transfer_is_terminal_and_never_inferred_complete(self):
        models=owned_models(); rows=[]; plan=PhaseResidency(models,progress=rows.append)
        def broken(*,device): raise MemoryError("owned fixture")
        models.pipeline.safety_checker.to=broken
        with self.assertRaises(MemoryError): plan.park_idle()
        self.assertEqual(plan.state,"failed_transition")
        self.assertEqual([r["phase"] for r in rows],["operation_started"])
        with self.assertRaises(EmbeddingError): plan.park_idle()

    def test_transfer_dtype_or_active_change_rejected(self):
        models=owned_models();plan=PhaseResidency(models)
        original=models.pipeline.text_encoder.to
        def altered(*,device):
            original(device=device);models.pipeline.unet.weight.dtype="torch.float16"
        models.pipeline.text_encoder.to=altered
        with self.assertRaises(EmbeddingError): plan.park_idle()
        self.assertEqual(plan.state,"failed_transition")

    def test_journal_failure_prevents_operation_and_completion(self):
        calls=[]
        def broken(row): raise OSError("owned journal")
        with self.assertRaises(OSError):
            with operation_phase(broken,"owned_operation"): calls.append("not reachable")
        self.assertEqual(calls,[])
        rows=[]
        with self.assertRaises(MemoryError):
            with operation_phase(rows.append,"owned_operation"): raise MemoryError("owned")
        self.assertEqual(len(rows),1)

    def test_between_transition_identity_condition_and_precision_drift_block(self):
        for mutation in (lambda m:setattr(m.components.condition,"device","cpu"),
                         lambda m:setattr(m.components.condition,"dtype","torch.float16"),
                         lambda m:setattr(m.components.condition,"requires_grad",True),
                         lambda m:setattr(m.pipeline,"unet",Module())):
            models=owned_models();plan=PhaseResidency(models);mutation(models)
            with self.assertRaises(EmbeddingError):plan.park_idle()
            self.assertEqual(plan.state,"failed_transition")
        for mutation in (lambda m:setattr(m.pipeline.vae.weight,"dtype","torch.float16"),
                         lambda m:setattr(m.pipeline.safety_checker,"training",True),
                         lambda m:setattr(m.pipeline.text_encoder.weight,"requires_grad",True),
                         lambda m:setattr(m.pipeline,"vae",Module()),
                         lambda m:setattr(m.components.condition,"device","cpu")):
            models=owned_models();plan=PhaseResidency(models);plan.park_idle();mutation(models)
            with self.assertRaises(EmbeddingError):plan.prepare_safety()
            self.assertEqual(plan.state,"failed_transition")


if __name__ == "__main__": unittest.main()
