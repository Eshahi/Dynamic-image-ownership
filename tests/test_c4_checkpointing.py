"""Owned CPU fixtures only: no study images, weights, GPU or scientific run."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from tests import test_embedding as fixtures
from tests.test_embedding import SETTINGS, SOURCE, WS, WI, CONFIG, torch
from src.embedding.proposed import EmbeddingError, optimize_existing, padded_source
from src.embedding.checkpointing import CheckpointedComponents


@unittest.skipIf(torch is None, "existing WSL Torch required")
class CheckpointContracts(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.TensorContracts()
        self.fixture.setUp()

    def backend(self):
        original = self.fixture.backend()
        return CheckpointedComponents(original.vae, original.unet, original.condition, SETTINGS)

    def test_output_gradient_and_timestep_parity(self):
        original, candidate = self.fixture.backend(), self.backend()
        outputs, gradients = [], []
        for backend in (original, candidate):
            latent = backend.encode(padded_source(self.fixture.source, 256))
            noise = torch.full_like(latent, .01, requires_grad=True)
            value = backend.reconstruct(latent, noise)
            outputs.append(value.detach())
            gradients.append(torch.autograd.grad(value.square().sum(), noise)[0])
        self.assertTrue(torch.equal(*outputs))
        self.assertTrue(torch.equal(*gradients))
        self.assertGreater(gradients[0].abs().sum().item(), 0)
        self.assertEqual([t for t, _, _ in candidate.unet.calls[:2]], [101, 1])
        # Recomputation must use both original timesteps, not the final loop value.
        self.assertEqual([t for t, _, _ in candidate.unet.calls[2:]], [1, 101])

    def test_optimizer_trajectory_and_no_grad_control_parity(self):
        for control in (False, True):
            values = [optimize_existing(self.fixture.source, SETTINGS, backend, seed=7,
                source_digest=SOURCE, ws=WS, wi=WI, config_id=CONFIG, control=control)
                for backend in (self.fixture.backend(), self.backend())]
            self.assertTrue(torch.equal(values[0].image, values[1].image))
            self.assertTrue(torch.equal(values[0].perturbation, values[1].perturbation))
            self.assertEqual(values[0].trajectory, values[1].trajectory)

    def test_no_grad_path_does_not_checkpoint(self):
        backend = self.backend()
        latent = backend.encode(padded_source(self.fixture.source, 256))
        with patch("torch.utils.checkpoint.checkpoint", side_effect=AssertionError("not needed")):
            with torch.no_grad():
                backend.reconstruct(latent, torch.zeros_like(latent))

    def test_mutation_between_forward_backward_fails(self):
        for mutation in ("condition", "parameter", "train", "replacement", "schedule"):
            backend = self.backend()
            latent = backend.encode(padded_source(self.fixture.source, 256))
            noise = torch.zeros_like(latent, requires_grad=True)
            image = backend.reconstruct(latent, noise)
            with torch.no_grad():
                if mutation == "condition": backend.condition.add_(.01)
                if mutation == "parameter": backend.unet.parameter.add_(.01)
                if mutation == "train": backend.vae.train()
                if mutation == "replacement": backend.condition = backend.condition.clone()
                if mutation == "schedule": backend.scheduler.alphas_cumprod.add_(.001)
            with self.subTest(mutation=mutation), self.assertRaises(EmbeddingError):
                image.square().sum().backward()

    def test_recompute_failure_is_not_hidden(self):
        backend = self.backend()
        latent = backend.encode(padded_source(self.fixture.source, 256))
        noise = torch.zeros_like(latent, requires_grad=True)
        image = backend.reconstruct(latent, noise)
        def failure(*args, **kwargs): raise MemoryError("owned replay fixture")
        backend.vae.decode = failure
        with self.assertRaises(MemoryError):
            image.square().sum().backward()

    def test_owned_nonlinear_saved_tensor_payload_and_gradient_parity(self):
        payloads, outputs, gradients = [], [], []
        for checkpointed in (False, True):
            original = self.fixture.backend()
            def nonlinear(value, vae=original.vae):
                expanded = torch.nn.functional.interpolate(value[:, :3], scale_factor=8,
                                                            mode="nearest")
                return SimpleNamespace(sample=expanded.sin().tanh()*vae.parameter)
            original.vae.decode = nonlinear
            backend = (CheckpointedComponents(original.vae, original.unet,
                       original.condition, SETTINGS) if checkpointed else original)
            latent = backend.encode(padded_source(self.fixture.source, 256))
            noise = torch.full_like(latent, .01, requires_grad=True)
            saved = []
            def pack(value):
                saved.append(value.numel()*value.element_size())
                return value
            with torch.autograd.graph.saved_tensors_hooks(pack, lambda value: value):
                image = backend.reconstruct(latent, noise)
            payloads.append(sum(saved))
            outputs.append(image.detach())
            gradients.append(torch.autograd.grad(image.square().sum(), noise)[0])
        self.assertLess(payloads[1], payloads[0])
        self.assertTrue(torch.equal(*outputs))
        self.assertTrue(torch.equal(*gradients))
        # Hook payload counts are not peak RSS/allocator/physical GPU memory.


if __name__ == "__main__":
    unittest.main()
