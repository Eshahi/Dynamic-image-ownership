"""Analytic CPU adapter mechanics; mocked numerical cores, no efficacy evidence."""
import copy
import hashlib
import os
from pathlib import Path
import random
import sys
import types
import unittest
from unittest import mock

import numpy as np
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import m1_candidate_adapter as method
import m1_source_initialization as initializer

REAL_SESSION=initializer.ReconstructionSession


class VAE(torch.nn.Module):
    def __init__(self,dtype):
        super().__init__();self.weight=torch.nn.Parameter(torch.tensor(1.,dtype=dtype),requires_grad=False)
        self.config=types.SimpleNamespace(scaling_factor=.18215);self.eval()


class AnalyticInitialization:
    """Shape-valid state generator to exercise orchestration, not reconstruction."""
    def __init__(self,target,vae,identity,resume=None):
        self.target=target;self.vae=vae;self.identity=identity
        self.target_hash=initializer.digest(target);self.runtime=initializer._runtime(target)
        self.initial=torch.zeros(1,4,64,64);self.z=self.initial.clone().requires_grad_(True)
        self.optimizer=torch.optim.Adam([self.z],lr=.02)
        if resume:
            initializer._validate_payload(resume,identity,self.target_hash,self.runtime)
            self.initial=resume["initial"].clone();self.z=resume["z"].clone().requires_grad_(True)
            self.optimizer=torch.optim.Adam([self.z],lr=.02);self.optimizer.load_state_dict(resume["optimizer"])
            self.step=resume["step"];self.observations=copy.deepcopy(resume["observations"])
            initializer._restore_rng(resume["rng"])
        else:
            self.step=0;self.observations={};self.observe()

    def observe(self):
        if self.step in (0,50,100,200):
            self.observations[self.step]={"rgb8":torch.zeros(512,512,3,dtype=torch.uint8),
                "objective_float_mse":0.,"latent_displacement_l2":float(self.z.detach().norm())}

    def advance(self,to_step,on_update):
        if to_step<self.step:raise ValueError("Backward fixture step")
        while self.step<to_step:
            draw=random.random()+float(np.random.random())+float(torch.rand(()))
            self.optimizer.zero_grad(set_to_none=True);self.z.grad=torch.full_like(self.z,draw)
            self.optimizer.step();self.step+=1;self.observe();on_update(self)

    def state_dict(self):return REAL_SESSION.state_dict(self)


def analytic_optimize(embedder,source,u0,oracle,cfg,event,save,check,resume=None):
    u=(resume["u"].clone() if resume else u0.detach().clone()).requires_grad_(True)
    optimizer=torch.optim.Adam([u],lr=cfg["learning_rate"],betas=tuple(cfg["adam_betas"]),eps=cfg["adam_eps"])
    start=0
    if resume:
        optimizer.load_state_dict(resume["optimizer"]);start=resume["step"]
        method.component.restore_rng(resume["rng"])
    save(start,u,optimizer)
    for step in range(start,cfg["steps"]):
        check();draw=random.random()+float(np.random.random())+float(torch.rand(()))
        optimizer.zero_grad(set_to_none=True);u.grad=torch.full_like(u,draw)
        optimizer.step();event({"step":step+1})
        if (step+1)%cfg["checkpoint_every"]==0:save(step+1,u,optimizer)
    return {"u":u.detach(),"residual":torch.zeros_like(source)}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.rgb=np.zeros((512,512,3),np.uint8)
        self.source={"source_id":"synthetic-fixture"}
        self.models={k:hashlib.sha256(k.encode()).hexdigest() for k in
                     ("vae_fp32","vae_public","clip","profile","scientific_core_sha256")}
        runtime=initializer._runtime(torch.zeros(1))
        runtime.update(deterministic=True,deterministic_warn_only=False,matmul_tf32=False,cudnn_tf32=False,
                       cudnn_benchmark=False,cudnn_deterministic=True,cublas_workspace_config=":4096:8")
        self.patches=[mock.patch.dict(os.environ,{"CUBLAS_WORKSPACE_CONFIG":":4096:8"}),
            mock.patch.object(initializer,"_runtime",return_value=runtime),
            mock.patch.object(initializer,"ReconstructionSession",AnalyticInitialization),
            mock.patch.object(method.component,"PublicReader"),
            mock.patch.object(method.component,"FixedSourceScores"),
            mock.patch.object(method.component,"optimize",side_effect=analytic_optimize),
            mock.patch.object(method.component.codec,"luminance_from_rgb",return_value=[]),
            mock.patch.object(method.component.codec,"perceptual_hash",return_value=17),
            mock.patch.object(method.component.residual,"cap",side_effect=lambda rgb,raw:(rgb.copy(),{"fixture":True}))]
        for p in self.patches:p.start()
        self.adapter=method.CandidateAdapter(VAE(torch.float32),VAE(torch.float16),object(),
                    lambda rgb:np.ones(512),{},self.models)

    def tearDown(self):
        for p in reversed(self.patches):p.stop()

    def init(self,**kwargs):
        return self.adapter.initialize(self.rgb,self.source,method.component.core.OWNERS[0],**kwargs)

    def test_phase_checkpoints_new_optimizers_fixed_configuration(self):
        initialization_states=[];embedding_states=[]
        init=self.init(on_checkpoint=initialization_states.append)
        final=self.adapter.embed(self.rgb,init,on_checkpoint=embedding_states.append)
        self.assertEqual([p["step"] for p in initialization_states],list(range(0,201,10)))
        self.assertEqual([p["step"] for p in embedding_states],list(range(0,101,10)))
        self.assertEqual(initialization_states[-1]["phase"],"initialization")
        self.assertEqual(embedding_states[-1]["phase"],"embedding")
        self.assertEqual(float(init["state"]["optimizer"]["state"][0]["step"]),200)
        self.assertEqual(embedding_states[0]["state"]["optimizer"]["state"],{})
        self.assertEqual(float(final["checkpoint"]["state"]["optimizer"]["state"][0]["step"]),100)
        self.assertEqual(method.component.optimize.call_args.args[4],
            {"steps":100,"learning_rate":.01,"adam_betas":[.9,.999],"adam_eps":1e-8,"cycle_every":2,"checkpoint_every":10})
        self.assertEqual(final["checkpoint"]["initializer_sha256"],initializer.digest(init))
        self.assertTrue(final["completed"])

    def test_resume_restores_both_phase_states_exactly(self):
        full_init=self.init()
        part=self.init(stop_step=100)
        random.random();np.random.random();torch.rand(19)
        resumed_init=self.init(resume=part)
        self.assertEqual(initializer.digest(full_init),initializer.digest(resumed_init))
        full=self.adapter.embed(self.rgb,full_init)
        prefix=self.adapter.embed(self.rgb,full_init,stop_step=50)
        self.assertFalse(prefix["completed"])
        random.random();np.random.random();torch.rand(19)
        resumed=self.adapter.embed(self.rgb,full_init,resume=prefix["checkpoint"])
        self.assertEqual(initializer.digest(full["checkpoint"]),initializer.digest(resumed["checkpoint"]))

    def test_owner_and_exact_uint64_schedule_are_metadata_only(self):
        uid="synthetic:fixture-owner-schedule"
        schedule=method.owners.source_schedule(uid)
        init=self.adapter.initialize(self.rgb,self.source,schedule["owner"],source_uid=uid)
        final=self.adapter.embed(self.rgb,init,stop_step=0)
        binding=init["binding"]
        self.assertEqual(binding["schedule"],schedule)
        self.assertEqual(binding["scientific_embedding_seed"],None)
        self.assertEqual(binding["execution_phase_seed"],0)
        self.assertEqual(method.component.FixedSourceScores.call_args.args[2],schedule["owner"])
        self.assertNotIn("seed",method.component.optimize.call_args.kwargs)
        self.assertEqual(final["checkpoint"]["state"]["optimizer"]["state"],{})
        for owner in method.component.core.ACCEPTED_OWNERS:
            self.assertEqual(method.component.core._owner(owner),owner)
        with self.assertRaisesRegex(ValueError,"schedule"):
            self.adapter.initialize(self.rgb,self.source,method.component.core.OWNERS[0],source_uid=uid)
        with self.assertRaises(TypeError):
            self.adapter.initialize(self.rgb,self.source,schedule["owner"],scientific_seed=12)

    def test_source_owner_phase_corruption_and_incomplete_initialization_rejected(self):
        partial=self.init(stop_step=100)
        with self.assertRaisesRegex(ValueError,"Complete original200"):
            self.adapter.embed(self.rgb,partial)
        bad=copy.deepcopy(partial);bad["state"]["z"][0,0,0,0]+=1
        with self.assertRaisesRegex(ValueError,"integrity"):
            self.init(resume=bad)
        changed=self.rgb.copy();changed[0,0,0]=1
        with self.assertRaisesRegex(ValueError,"identity"):
            self.adapter.initialize(changed,self.source,method.component.core.OWNERS[0],resume=partial)
        with self.assertRaisesRegex(ValueError,"identity"):
            self.adapter.initialize(self.rgb,self.source,method.component.core.OWNERS[1],resume=partial)
        wrong=method._sealed({k:v for k,v in partial.items() if k!="integrity_sha256"}|{"phase":"embedding"})
        with self.assertRaisesRegex(ValueError,"phase"):
            self.init(resume=wrong)

    def test_readout_gets_only_suspect_public_owner_reader(self):
        with mock.patch.object(method.component,"detect",return_value={"fixture":True}) as spy:
            result=self.adapter.readout(self.rgb,"thesis:owner:15")
            self.assertEqual(result,{"fixture":True})
            self.assertEqual(len(spy.call_args.args),3)
            self.assertEqual(spy.call_args.args[1],"thesis:owner:15")
            self.assertIs(spy.call_args.args[2],self.adapter.public)
        with self.assertRaises(ValueError):self.adapter.readout(self.rgb,"thesis:owner:16")

    def test_callbacks_cannot_mutate_checkpoints_or_consume_rng(self):
        def mutate(p):p["binding"]["owner"]="changed"
        actual=self.init(stop_step=0,on_checkpoint=mutate)
        self.assertEqual(actual["binding"]["owner"],method.component.core.OWNERS[0])
        with self.assertRaisesRegex(ValueError,"consumed"):
            self.init(stop_step=0,on_checkpoint=lambda p:random.random())

    def test_changed_scientific_core_rejects_phase_import_and_resume(self):
        partial=self.init(stop_step=100)
        complete=self.init()
        prefix=self.adapter.embed(self.rgb,complete,stop_step=10)["checkpoint"]
        changed=dict(self.models,scientific_core_sha256="f"*64)
        other=method.CandidateAdapter(VAE(torch.float32),VAE(torch.float16),object(),
                                     lambda rgb:np.ones(512),{},changed)
        with self.assertRaisesRegex(ValueError,"identity"):
            other.initialize(self.rgb,self.source,method.component.core.OWNERS[0],resume=partial)
        with self.assertRaisesRegex(ValueError,"identity"):
            other.embed(self.rgb,complete,resume=prefix)
        self.assertEqual(complete["binding"]["scientific_core_sha256"],self.models["scientific_core_sha256"])
        for bad in ("x","A"*64,"f"*63,None):
            with self.assertRaisesRegex(ValueError,"SHA256"):
                method.CandidateAdapter(VAE(torch.float32),VAE(torch.float16),object(),
                    lambda rgb:np.ones(512),{},dict(self.models,scientific_core_sha256=bad))


if __name__=="__main__":unittest.main()
