"""CPU mechanics only: original loop parity, full replay and fail-closed receipts."""
import copy
import os
from pathlib import Path
import random
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np
import torch
from torch.utils.checkpoint import checkpoint

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m1_source_initialization as adapter


class TinyVAE(torch.nn.Module):
    def __init__(self, stochastic=False):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.tensor(.73), requires_grad=False)
        self.config = types.SimpleNamespace(scaling_factor=.18215)
        self.stochastic = stochastic
        self.eval()

    def encode(self, x):
        return types.SimpleNamespace(latent_dist=types.SimpleNamespace(mode=lambda: x*.4))

    def decode(self, z, return_dict=False):
        value = torch.tanh(z*self.weight+.07)
        if self.stochastic:
            value = value + torch.randn_like(z)*.004
        return (value,)


def seed():
    random.seed(31); np.random.seed(31); torch.manual_seed(31)


def fixture():
    return torch.arange(36, dtype=torch.float32).reshape(1,3,3,4)/35


IDENTITY = {"source_id": "cpu-fixture", "model_sha256": "a"*64,
            "source_rgb8_sha256": "b"*64}


def original(target, vae):
    """Literal scientific loop equations/order from m1_latent_reconstruction.py."""
    with torch.no_grad():
        initial = vae.encode(target*2-1).latent_dist.mode()
    z = initial.detach().clone().requires_grad_(True)
    optimizer = torch.optim.Adam([z], lr=.02)
    observations = {}
    def decode(latent):
        return (vae.decode(latent, return_dict=False)[0]+1)/2
    for step in range(201):
        if step in (0,50,100,200):
            with torch.no_grad():
                raw = decode(z)
                rgb = (raw.clamp(0,1)[0].permute(1,2,0).cpu().numpy()*255).round().astype(np.uint8)
                observations[step] = rgb
        if step == 200:
            break
        optimizer.zero_grad(set_to_none=True)
        loss = (checkpoint(decode,z,use_reentrant=False)-target).square().mean()
        loss.backward()
        optimizer.step()
    return z.detach(), optimizer.state_dict(), observations


class InitializationTests(unittest.TestCase):
    def assertTreeExact(self, a, b):
        self.assertEqual(adapter.digest(a), adapter.digest(b))

    def test_exact_original_equations_and_last_update(self):
        target = fixture(); seed()
        expected_z, expected_optimizer, expected_images = original(target,TinyVAE())
        seed()
        session = adapter.ReconstructionSession(target,TinyVAE(),IDENTITY).advance()
        self.assertTrue(torch.equal(expected_z,session.z))
        self.assertTreeExact(expected_optimizer,session.optimizer.state_dict())
        for s, rgb in expected_images.items():
            np.testing.assert_array_equal(rgb, session.observations[s]["rgb8"].numpy())
        final = session.final()
        self.assertEqual(final["step"],200)
        self.assertIn("unscaled",final["latent_units"])
        self.assertTrue(torch.equal(final["initial"],(target*2-1)*.4))
        self.assertFalse(torch.equal(final["initial"],(target*2-1)*.4*.18215))
        self.assertEqual(float(session.optimizer.state_dict()["state"][0]["step"]),200)

    def test_disk_resume_exact_adam_latent_all_rng_and_observations(self):
        target = fixture(); seed()
        full = adapter.ReconstructionSession(target,TinyVAE(True),IDENTITY).advance()
        expected = full.state_dict()
        expected_draws = (random.random(),np.random.random(),torch.rand(5))
        for cut in (0,1,49,50,100,199,200):
            seed()
            part = adapter.ReconstructionSession(target,TinyVAE(True),IDENTITY).advance(cut)
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/"restart.pt"
                part.save(path)
                saved = adapter.load_checkpoint(path)
            random.random(); np.random.random(); torch.rand(19)
            recovered = adapter.ReconstructionSession(target,TinyVAE(True),IDENTITY,resume=saved).advance()
            self.assertTreeExact(expected,recovered.state_dict())
            actual_draws = (random.random(),np.random.random(),torch.rand(5))
            self.assertEqual(expected_draws[:2],actual_draws[:2])
            self.assertTrue(torch.equal(expected_draws[2],actual_draws[2]))

    def test_original_stochastic_checkpoint_rng_order(self):
        seed(); expected_z,expected_optimizer,expected_images=original(fixture(),TinyVAE(True))
        expected_rng=torch.get_rng_state()
        seed(); session=adapter.ReconstructionSession(fixture(),TinyVAE(True),IDENTITY).advance()
        self.assertTrue(torch.equal(expected_z,session.z))
        self.assertTreeExact(expected_optimizer,session.optimizer.state_dict())
        self.assertTrue(torch.equal(expected_rng,torch.get_rng_state()))
        for s, rgb in expected_images.items():
            np.testing.assert_array_equal(rgb,session.observations[s]["rgb8"].numpy())

    def test_identity_target_config_and_corruption_rejected(self):
        seed(); payload=adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY).advance(50).state_dict()
        wrong=dict(IDENTITY,source_id="other")
        with self.assertRaisesRegex(ValueError,"identity"):
            adapter.ReconstructionSession(fixture(),TinyVAE(),wrong,resume=payload)
        with self.assertRaisesRegex(ValueError,"identity"):
            adapter.ReconstructionSession(fixture()*.99,TinyVAE(),IDENTITY,resume=payload)
        corrupted=copy.deepcopy(payload); corrupted["z"][0,0,0,0]+=.1
        with self.assertRaisesRegex(ValueError,"integrity"):
            adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY,resume=corrupted)
        for field in ("learning_rate","updates","latent_units"):
            bad=copy.deepcopy(payload); bad["config"][field]="changed"
            bad["integrity_sha256"]=adapter.digest({k:v for k,v in bad.items() if k!="integrity_sha256"})
            with self.assertRaisesRegex(ValueError,"config"):
                adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY,resume=bad)
        bad=copy.deepcopy(payload); bad["optimizer"]["param_groups"][0]["betas"]=(.8,.99)
        bad["integrity_sha256"]=adapter.digest({k:v for k,v in bad.items() if k!="integrity_sha256"})
        with self.assertRaisesRegex(ValueError,"Adam parameter"):
            adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY,resume=bad)
        bad=copy.deepcopy(payload); bad["optimizer"]["state"][0]["step"]+=1
        bad["integrity_sha256"]=adapter.digest({k:v for k,v in bad.items() if k!="integrity_sha256"})
        with self.assertRaisesRegex(ValueError,"completed-update"):
            adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY,resume=bad)

    def test_partial_final_and_step_bounds(self):
        s=adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY).advance(199)
        with self.assertRaises(ValueError): s.final()
        for bad in (198,201,True):
            with self.assertRaises(ValueError): s.advance(bad)
        s.advance(200)
        state=s.state_dict(); s.advance(200)
        self.assertTreeExact(state,s.state_dict())
        final=adapter.reconstruct_source(fixture(),TinyVAE(),IDENTITY)
        self.assertEqual(final["rgb8"].dtype,torch.uint8)
        self.assertEqual(final["rgb8"].shape,(3,4,3))

    def test_target_and_model_contract(self):
        for target in (fixture().double(),fixture().requires_grad_(True),fixture()*2,fixture()[0]):
            with self.assertRaises(ValueError):
                adapter.ReconstructionSession(target,TinyVAE(),IDENTITY)
        with self.assertRaises(ValueError):
            adapter.ReconstructionSession(fixture(),TinyVAE().train(),IDENTITY)

    def test_runtime_policy_guard_without_cuda_initialization(self):
        before = torch.cuda.is_initialized()
        with mock.patch.object(torch.cuda, "is_initialized", return_value=False), \
                mock.patch.object(torch.cuda, "get_device_properties", side_effect=AssertionError("GPU query")), \
                mock.patch.object(torch.backends.cudnn, "version", side_effect=AssertionError("cuDNN query")), \
                mock.patch.dict(os.environ, {"CUBLAS_WORKSPACE_CONFIG": ":4096:8"}):
            session = adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY)
            saved = session.state_dict()
            self.assertEqual(saved["runtime"]["cublas_workspace_config"],":4096:8")
            self.assertEqual(saved["runtime"]["cuda_version"],torch.version.cuda)
            self.assertIsNone(saved["runtime"]["cudnn_version"])
            self.assertIsNone(saved["runtime"]["cuda_device_name"])
            self.assertIsNone(saved["runtime"]["cuda_device_capability"])
        self.assertEqual(before,torch.cuda.is_initialized())
        with mock.patch.dict(os.environ, {"CUBLAS_WORKSPACE_CONFIG": ":16:8"}):
            with self.assertRaisesRegex(ValueError,"runtime"):
                adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY,resume=saved)

    def test_nonfinite_updated_latent_stops_before_callback(self):
        session = adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY)
        callback = mock.Mock()
        real_step = session.optimizer.step
        def bad_step():
            real_step()
            with torch.no_grad(): session.z[0,0,0,0] = float("nan")
        with mock.patch.object(session.optimizer,"step",side_effect=bad_step):
            with self.assertRaisesRegex(RuntimeError,"Nonfinite latent after"):
                session.advance(1,on_update=callback)
        callback.assert_not_called()
        self.assertEqual(session.step,0)

    def test_save_retains_existing_final_and_temporary_receipts(self):
        session = adapter.ReconstructionSession(fixture(),TinyVAE(),IDENTITY)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"step000.pt"
            temp = path.with_name(path.name+".tmp")
            path.write_bytes(b"retained final")
            with self.assertRaises(FileExistsError): session.save(path)
            self.assertEqual(path.read_bytes(),b"retained final")
            self.assertFalse(temp.exists())
            path.unlink(); temp.write_bytes(b"retained temporary")
            with self.assertRaises(FileExistsError): session.save(path)
            self.assertEqual(temp.read_bytes(),b"retained temporary")
            self.assertFalse(path.exists())
            temp.unlink()
            original_link = os.link
            def race_link(src,dst):
                Path(dst).write_bytes(b"concurrent retained final")
                return original_link(src,dst)
            with mock.patch.object(adapter.os,"link",side_effect=race_link):
                with self.assertRaises(FileExistsError): session.save(path)
            self.assertEqual(path.read_bytes(),b"concurrent retained final")
            self.assertTrue(temp.exists())


if __name__ == "__main__":
    unittest.main()
