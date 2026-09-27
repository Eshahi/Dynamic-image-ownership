"""Synthetic fake-backend CPU tests only, no models or study pixels."""
import unittest
try:
    import torch
except ImportError:
    torch = None
from src.embedding.reconstruction import localization, ARMS
from src.embedding.proposed import EmbeddingError, DiffusersComponents
from types import SimpleNamespace


@unittest.skipIf(torch is None, "fixed base environment has no Torch")
class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.source = torch.full((1, 3, 33, 35), .25)
        self.noise = torch.full((1, 4, 8, 8), .5)

    def backend(self):
        class Fake:
            def __init__(self): self.calls = []
            def encode(self, image):
                self.calls.append(("encode", tuple(image.shape)))
                return torch.full((1, 4, 8, 8), .25)
            def decode_encoded(self, latent):
                self.calls.append(("vae", float(latent.mean())))
                latent.zero_()  # adversarial mutation must not affect later arm
                return torch.full((1, 3, 64, 64), .25)
            def reconstruct(self, latent, noise):
                self.calls.append(("ddim", float(latent.mean()), float(noise.mean())))
                value = float(latent.mean()+noise.mean()/2)
                noise.zero_(); latent.zero_()
                return torch.full((1, 3, 64, 64), value)
        return Fake()

    def test_fixed_three_arm_order_grid_and_no_input_mutation(self):
        backend = self.backend(); events = []
        out = localization(backend, self.source, self.noise, maximum_side=256, progress=events.append)
        self.assertEqual(tuple(out), ARMS)
        self.assertEqual(backend.calls, [("encode", (1,3,64,64)), ("vae", .25),
                                        ("ddim", .25, 0.), ("ddim", .25, .5)])
        for arm, value in zip(ARMS, (.25,.25,.5)):
            self.assertEqual(tuple(out[arm].shape), (1,3,33,35))
            self.assertTrue(torch.all(out[arm] == value))
        self.assertTrue(torch.all(self.source == .25)); self.assertTrue(torch.all(self.noise == .5))
        self.assertEqual(len(events), 8)

    def test_bad_noise_rejects_before_encode(self):
        for noise in (self.noise.double(), self.noise[..., :7],
                      self.noise.clone().requires_grad_(), torch.full_like(self.noise, float("nan"))):
            backend = self.backend()
            with self.assertRaises(EmbeddingError): localization(backend,self.source,noise,maximum_side=256)
            self.assertEqual(backend.calls, [])

    def test_bad_arm_aborts_no_fallback_or_later_arm(self):
        for image in (torch.zeros((1,3,32,32)), torch.full((1,3,64,64), 2.),
                      torch.zeros((1,3,64,64), dtype=torch.float64),
                      torch.full((1,3,64,64), float("nan"))):
            backend = self.backend(); events = []
            backend.decode_encoded = lambda latent: image
            with self.assertRaises(EmbeddingError):
                localization(backend,self.source,self.noise,maximum_side=256,progress=events.append)
            self.assertEqual(len(backend.calls),1)
            self.assertEqual(events[-1], {"phase":"operation_started","operation":"vae_only"})

    def test_callback_failure_aborts(self):
        backend = self.backend()
        def broken(event): raise RuntimeError("owned journal failure")
        with self.assertRaises(RuntimeError): localization(backend,self.source,self.noise,maximum_side=256,progress=broken)
        self.assertEqual(backend.calls, [])

    def test_component_decode_uses_bound_scale_and_virtual_decoder(self):
        backend = DiffusersComponents.__new__(DiffusersComponents)
        backend.condition = torch.zeros(1)
        backend.settings = SimpleNamespace(vae_scale=.5)
        backend.progress = None
        calls = []
        def decoder(value):
            calls.append(value.clone())
            return torch.zeros((1,3,64,64))
        backend._decode = decoder
        image = backend.decode_encoded(torch.full((1,4,8,8), .25))
        self.assertTrue(torch.all(calls[0] == .5))
        self.assertTrue(torch.all(image == .5))
        with self.assertRaises(EmbeddingError): backend.decode_encoded(torch.zeros((1,4,8,8),dtype=torch.float64))
        backend._decode = lambda value: torch.zeros((1,3,32,32))
        with self.assertRaises(EmbeddingError): backend.decode_encoded(torch.zeros((1,4,8,8)))


if __name__ == "__main__": unittest.main()
