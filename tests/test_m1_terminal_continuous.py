"""CPU algebra, image-cap, boundary and resume tests; no model evaluation."""
from __future__ import annotations

import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_blind_noise_core as core
import m1_terminal_continuous as method


class TerminalContinuousTests(unittest.TestCase):
    def setUp(self):
        # These analytic fixtures exercise CPU Adam continuation. The production
        # checkpoint helper also snapshots CUDA; do not initialize a real GPU
        # merely to represent the fixture's absent CUDA state.
        cuda_rng = patch.object(torch.cuda, 'get_rng_state_all', return_value=[])
        cuda_rng.start()
        self.addCleanup(cuda_rng.stop)
        self.rng=np.random.default_rng(810)
        self.E=self.rng.normal(size=512);self.E/=np.linalg.norm(self.E)
        self.H=0xBA84B4B8

    def test_gpu_budget_uses_current_free_memory_and_fixed_reserve(self):
        gib=1024**3;reserve=512*1024**2
        normal=method.gpu_allocation_budget(10*gib,12*gib,12*gib,reserve)
        self.assertEqual(normal['effective_allocation_bytes'],10*gib)
        busy=method.gpu_allocation_budget(10*gib,8*gib,12*gib,reserve)
        self.assertEqual(busy['effective_allocation_bytes'],8*gib-reserve)
        self.assertEqual(busy['allocator_fraction'],(8*gib-reserve)/(12*gib))
        self.assertEqual(busy['free_bytes_before_models'],8*gib)
        self.assertEqual(busy['reserve_bytes'],reserve)
        with self.assertRaises(RuntimeError):method.gpu_allocation_budget(10*gib,reserve,12*gib,reserve)
        with self.assertRaises(ValueError):method.gpu_allocation_budget(10*gib,13*gib,12*gib,reserve)
        with self.assertRaises(ValueError):method.gpu_allocation_budget(10*gib,8*gib,12*gib,-1)

    def test_torch_score_matches_independent_core(self):
        z=self.rng.normal(size=16384)
        for owner in core.OWNERS:
            expected=core.scores(z,self.E,self.H,owner)
            oracle=method.FixedSourceScores(self.E,self.H,owner,'cpu',torch.float64)
            actual=oracle.scores(torch.tensor(z))
            np.testing.assert_allclose([float(v) for v in actual],[expected['s'],expected['i']],atol=1e-12,rtol=1e-12)

    def test_score_gradient_and_unit_scaling(self):
        oracle=method.FixedSourceScores(self.E,self.H,core.OWNERS[0],'cpu',torch.float64)
        z=torch.tensor(self.rng.normal(size=16384),requires_grad=True)
        direction=torch.tensor(self.rng.normal(size=16384));direction/=direction.norm()
        s,i=oracle.scores(z);gradient=torch.autograd.grad(s+i,z)[0]
        eps=1e-5
        def total(x):return sum(oracle.scores(x))
        finite=(total(z+eps*direction)-total(z-eps*direction))/(2*eps)
        self.assertAlmostEqual(float(finite.detach()),float(gradient@direction),places=8)
        scaled=oracle.scores(z*.18215)
        np.testing.assert_allclose([float(v.detach()) for v in scaled],[float(s.detach()),float(i.detach())],atol=1e-12)
        with self.assertRaises(ValueError):oracle.scores(torch.zeros_like(z))

    def test_cap_zero_branch_gradient_is_identity(self):
        source=torch.full((4,),.5,dtype=torch.float64)
        r=torch.zeros_like(source,requires_grad=True)
        image,rho,beta=method.cap_tensor(source,r)
        image.sum().backward()
        self.assertEqual(float(beta.detach()),1.);self.assertEqual(float(rho.detach()),0.)
        self.assertTrue(bool(torch.isfinite(r.grad).all()))
        torch.testing.assert_close(r.grad,torch.ones_like(r))

    def test_cap_active_derivative_and_norm(self):
        source=torch.full((8,),.5,dtype=torch.float64)
        r=torch.tensor(self.rng.normal(size=8)*.1,requires_grad=True)
        weights=torch.tensor(self.rng.normal(size=8));direction=torch.tensor(self.rng.normal(size=8))
        image,rho,beta=method.cap_tensor(source,r)
        gradient=torch.autograd.grad(image@weights,r)[0]
        eps=1e-6
        f=lambda v:method.cap_tensor(source,v)[0]@weights
        finite=(f(r+eps*direction)-f(r-eps*direction))/(2*eps)
        self.assertAlmostEqual(float(finite.detach()),float(gradient@direction),places=7)
        self.assertAlmostEqual(float(((image-source)**2).mean().sqrt().detach()),method.EPSILON,places=12)
        self.assertAlmostEqual(float((gradient@r).detach()),0.,places=12)
        self.assertLess(float(beta.detach()),1.)

    def test_rgb8_identity_monotonicity_and_exact_cap(self):
        source=self.rng.integers(0,256,size=(12,13,3),dtype=np.uint8)
        delta=self.rng.normal(size=source.shape)*.2
        np.testing.assert_array_equal(method.residual.compose(source,delta,0),source)
        sses=[method.residual.pixel_sse(source,method.residual.compose(source,delta,v)) for v in np.linspace(0,1,101)]
        self.assertEqual(sses,sorted(sses))
        output,receipt=method.residual.cap(source,delta)
        self.assertEqual(receipt['iterations'],36)
        self.assertEqual(receipt['hi']-receipt['lo'],2**-36)
        self.assertLessEqual(receipt['mse_rgb8'],255**2*10**(-35.2/10))
        high=method.residual.compose(source,delta,receipt['hi'])
        self.assertGreater(method.residual.pixel_sse(source,high)/source.size,receipt['budget_mse_rgb8'])
        np.testing.assert_array_equal(output,method.residual.compose(source,delta,receipt['lo']))
        zero,zero_receipt=method.residual.cap(source,np.zeros_like(delta))
        np.testing.assert_array_equal(zero,source);self.assertEqual(zero_receipt['weight'],1.)

    def test_public_reader_boundary_and_no_oracle_parameters(self):
        names=list(inspect.signature(method.detect).parameters)
        self.assertEqual(names,['image_rgb8','owner_id','pinned_public_profile_and_models'])
        z=self.rng.normal(size=16384);e=self.E;h=self.H
        class PublicFixture:
            def observations(self,rgb):return e,h,z
        rgb=np.zeros((512,512,3),dtype=np.uint8)
        actual=method.detect(rgb,core.OWNERS[0],PublicFixture())
        self.assertEqual(actual,core.scores(z,e,h,core.OWNERS[0]))
        with self.assertRaises(TypeError):method.detect(rgb,core.OWNERS[0],PublicFixture(),source_E=e)

    def test_exact_plan_and_manifest(self):
        rows=method.planned();self.assertEqual(len(rows),8);self.assertEqual(len({r['id'] for r in rows}),8)
        self.assertEqual({r['source_id'] for r in rows},{1675,4795})
        cfg=method.configuration()
        self.assertEqual(cfg,json.loads((ROOT/'research/m1-terminal-continuous-dev.json').read_text()))
        self.assertEqual(cfg['steps'],100);self.assertEqual(cfg['threshold'],4.)
        self.assertEqual(cfg['owners'],list(core.OWNERS));self.assertEqual(len(rows)*len(cfg['owners']),32)

    def test_gate_keeps_missing_invalid_and_wrong_owner_failures(self):
        rows=method.planned()
        self.assertFalse(method.pilot_gate(rows)['passes'])
        for row in rows:
            row['outcome']='completed'
            row['quality_vs_source']={'quality_admissible':True}
            row['owner_decisions']={owner:dict(flags=dict(s=False,i=False),state='neither_supported') for owner in core.OWNERS}
            if row['control']=='C1':row['owner_decisions'][core.OWNERS[0]]=dict(flags=dict(s=True,i=True),state='both_match')
        self.assertTrue(method.pilot_gate(rows)['passes'])
        self.assertEqual(method.pilot_gate(rows)['negative_queries_below_both_n'],28)
        rows[0]['owner_decisions'][core.OWNERS[0]]['flags']['s']=None
        self.assertFalse(method.pilot_gate(rows)['passes'])
        self.assertFalse(method.pilot_gate(rows[1:])['passes'])

    def test_checkpoint_roundtrip_identity_and_replacement_guard(self):
        u=torch.ones((1,4,64,64),requires_grad=True)
        optimizer=torch.optim.Adam([u],lr=.01)
        (u.square().mean()).backward();optimizer.step()
        identity={'version':method.VERSION,'source_id':1675,'source_rgb8_sha256':'fixture'}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'checkpoint.pt'
            receipt=method.checkpoint_save(path,u,optimizer,10,identity)
            result=method.checkpoint_load(receipt,identity)
            torch.testing.assert_close(result['u'],u.detach())
            self.assertEqual(result['step'],10)
            self.assertIn('exp_avg',result['optimizer']['state'][0])
            method.restore_rng(result['rng'])
            with self.assertRaises(ValueError):method.checkpoint_load(receipt,{'version':'wrong'})
            with self.assertRaises(ValueError):method.checkpoint_save(path,u,optimizer,10,identity)

    def test_cpu_fixture_optimizer_resume_matches_uninterrupted(self):
        # A tiny analytic codec, not a pretrained VAE or scientific image.
        class AnalyticCodec:
            def decode(self,u):return torch.sigmoid(u[:,:3])
            def encode(self,x):return torch.cat((x,x.mean(dim=1,keepdim=True)),dim=1)*.18215
            def cycle(self,x):return x*.99+.005
        source=torch.full((1,3,64,64),.5)
        u0=torch.tensor(self.rng.normal(size=(1,4,64,64))*.1,dtype=torch.float32)
        oracle=method.FixedSourceScores(self.E,self.H,core.OWNERS[0],'cpu')
        cfg=method.configuration();cfg['steps']=20
        identity={'version':method.VERSION,'kind':'CPU analytic unit fixture'}
        with tempfile.TemporaryDirectory() as temp:
            def segment(name,configuration,resume=None):
                folder=Path(temp)/name;folder.mkdir();saved=[];events=[]
                def save(step,u,opt):saved.append(method.checkpoint_save(folder/f'{step}.pt',u,opt,step,identity))
                result=method.optimize(AnalyticCodec(),source,u0,oracle,configuration,events.append,save,lambda:None,resume)
                return result,saved,events
            full,_,full_events=segment('full',cfg)
            short=dict(cfg,steps=10)
            _,snapshots,_=segment('first',short)
            resumed,_,resume_events=segment('resume',cfg,method.checkpoint_load(snapshots[-1],identity))
            torch.testing.assert_close(full['u'],resumed['u'],atol=0,rtol=0)
            self.assertEqual([e['step'] for e in resume_events],list(range(11,21)))
            self.assertEqual(sum('cycle_loss' in e for e in full_events),10)
            self.assertTrue(all(np.isfinite(e['gradient_l2']) and e['gradient_l2']>0 for e in full_events))


if __name__=='__main__':unittest.main()
