"""Candidate-specific, path-free source -> original200 -> A-C100 adapter.

Models and canonical pixels are supplied by an authorized worker. This module
does not authorize data, configure/load models, persist images or assess gates.
"""
from __future__ import annotations

import copy
import hashlib
import os
import random
import re

import numpy as np
import torch

import m1_source_initialization as initialization
import m1_terminal_continuous as component
import m1_owner_interface as owners

VERSION = "m1-terminal-continuous-e2e-adapter-v1"
CHECKPOINT_VERSION = "m1-candidate-phase-checkpoint-v1"
CONFIG = {"initializer_updates":200,"initializer_lr":.02,"embedding_updates":100,
    "embedding_lr":.01,"adam_betas":[.9,.999],"adam_eps":1e-8,
    "checkpoint_every":10,"semantic_margin":6.,"instance_margin":8.,"cycle_margin":6.,
    "cycle_every":2,"quality_weight":.01,"psnr_cap_db":35.2,"bisection_steps":36,
    "threshold":4.,"execution_phase_seed":0,"scientific_embedding_seed":None,
    "owner_interface_version":owners.VERSION,"map_version":owners.MAP_VERSION,
    "schedule_seed_role":"metadata_only_not_consumed_by_ac_e2e",
    "operator":"source bypass plus quality-capped clamped-decoder residual",
    "final_selection":"last-fixed-step; quality-only cap"}


def _seed_fresh_phase():
    random.seed(0);np.random.seed(0);torch.manual_seed(0)


def _method_rng():
    r=initialization._rng()
    return {"python":r["python"],"numpy":r["numpy"],"torch_cpu":r["torch"],"torch_cuda":r["cuda"]}


def _sealed(body):
    body=initialization._cpu_tree(body)
    return {**body,"integrity_sha256":initialization.digest(body)}


def _check_seal(payload):
    if not isinstance(payload,dict) or payload.get("integrity_sha256")!=initialization.digest(
            {k:v for k,v in payload.items() if k!="integrity_sha256"}):
        raise ValueError("Phase checkpoint integrity differs")
    if payload.get("schema")!=CHECKPOINT_VERSION or payload.get("configuration")!=CONFIG:
        raise ValueError("Phase checkpoint schema/configuration differs")


def _pure_callback(callback,value):
    if callback is not None:
        before=initialization.digest(initialization._rng())
        callback(initialization._cpu_tree(value))
        if initialization.digest(initialization._rng())!=before:
            raise ValueError("Checkpoint/event callback consumed execution RNG")


class CandidateAdapter:
    """Reuse scientific cores with explicit model/processor/feature injection.

    ``feature`` supplies raw CLIP coordinates; this adapter applies the existing
    finite512-vector normalization once for both source oracle and public reader.
    ``model_identity`` pins caller-verified FP32/public VAE, CLIP and profile IDs.
    There is deliberately no scientific-seed or arbitrary source-path argument.
    """
    def __init__(self,vae_fp32,vae_public,processor,feature,profile,model_identity):
        if (not isinstance(model_identity,dict) or any(type(model_identity.get(k)) is not str
                or re.fullmatch(r"[0-9a-f]{64}",model_identity[k]) is None
                for k in ("vae_fp32","vae_public","clip","profile","scientific_core_sha256"))):
            raise ValueError("Explicit caller-verified lowercase SHA256 model/profile/scientific-core identities required")
        if (vae_fp32.training or any(p.requires_grad or p.dtype!=torch.float32 for p in vae_fp32.parameters())
                or float(vae_fp32.config.scaling_factor)!=.18215):
            raise ValueError("Embedding VAE must be frozen eval FP32 with scaling factor.18215")
        if (vae_public.training or any(p.requires_grad or p.dtype!=torch.float16 for p in vae_public.parameters())
                or float(vae_public.config.scaling_factor)!=.18215):
            raise ValueError("Public VAE must be frozen eval FP16 with scaling factor.18215")
        self.vae=vae_fp32;self.feature_input=feature;self.profile=copy.deepcopy(profile)
        self.model_identity=copy.deepcopy(model_identity)
        self.embedder=component.Embedder(vae_fp32)
        self.public=component.PublicReader(vae_public,processor,self.feature,self.profile)

    def feature(self,rgb):
        e=np.asarray(self.feature_input(rgb),np.float64).reshape(-1)
        norm=float(np.linalg.norm(e))
        if e.shape!=(512,) or not np.isfinite(e).all() or norm<=0:
            raise ValueError("Invalid CLIP feature")
        return e/norm

    def _source(self,rgb):
        if not isinstance(rgb,np.ndarray) or rgb.dtype!=np.uint8 or rgb.shape!=(512,512,3):
            raise ValueError("Already authorized canonical512 RGB8 required")
        rgb=rgb.copy()
        device=next(self.vae.parameters()).device
        target=torch.from_numpy(rgb).permute(2,0,1).unsqueeze(0).float().to(device)/255
        return rgb,target

    def _binding(self,rgb,target,source_identity,owner,source_uid=None):
        component.core._owner(owner)
        if not isinstance(source_identity,dict) or source_identity.get("source_id") is None:
            raise ValueError("Explicit resolver-supplied source identity required")
        rgb_sha=hashlib.sha256(rgb.tobytes()).hexdigest()
        if source_identity.get("source_rgb8_sha256",rgb_sha)!=rgb_sha:
            raise ValueError("Canonical source identity differs")
        schedule=owners.source_schedule(source_uid) if source_uid is not None else None
        if schedule is not None and schedule["owner"]!=owner:
            raise ValueError("Explicit owner differs from A4 UID schedule")
        runtime=initialization._runtime(target)
        if (os.environ.get("CUBLAS_WORKSPACE_CONFIG")!=":4096:8" or
                not runtime["deterministic"] or runtime["deterministic_warn_only"] or
                runtime["matmul_tf32"] or runtime["cudnn_tf32"] or runtime["cudnn_benchmark"] or
                not runtime["cudnn_deterministic"]):
            raise ValueError("Caller must configure frozen deterministic policy before model/CUDA setup")
        return {"source_identity":copy.deepcopy(source_identity),"source_rgb8_sha256":rgb_sha,
            "owner":owner,"source_uid":source_uid,"schedule":schedule,"model_identity":copy.deepcopy(self.model_identity),
            "profile_sha256":component.canonical_sha(self.profile),"runtime":runtime,
            "scientific_core_sha256":self.model_identity["scientific_core_sha256"],
            "fill_uninitialized_memory":bool(torch.utils.deterministic.fill_uninitialized_memory),
            "candidate_version":VERSION,"execution_phase_seed":0,"scientific_embedding_seed":None,
            "schedule_seed_role":CONFIG["schedule_seed_role"]}

    def _verify(self,payload,phase,binding):
        _check_seal(payload)
        if payload.get("phase")!=phase or payload.get("binding")!=binding:
            raise ValueError("Checkpoint phase/source/owner/model/runtime identity differs")
        limit=200 if phase=="initialization" else 100
        if type(payload.get("step")) is not int or payload["step"] not in range(0,limit+1,10):
            raise ValueError("Invalid completed phase update count")

    def initialize(self,rgb,source_identity,owner,*,source_uid=None,resume=None,stop_step=200,
                   on_checkpoint=None,check=None):
        if type(stop_step) is not int or stop_step not in range(0,201,10):
            raise ValueError("Initializer stop must be a scheduled0..200 checkpoint")
        rgb,target=self._source(rgb);binding=self._binding(rgb,target,source_identity,owner,source_uid)
        identity={"source_id":source_identity["source_id"],"source_rgb8_sha256":binding["source_rgb8_sha256"],
                  "model_sha256":self.model_identity["vae_fp32"],"candidate_binding_sha256":initialization.digest(binding)}
        if resume is not None:
            self._verify(resume,"initialization",binding)
            if resume["step"]!=resume["state"]["step"]:raise ValueError("Initializer wrapper/state step differs")
            session=initialization.ReconstructionSession(target,self.vae,identity,resume=resume["state"])
        else:
            _seed_fresh_phase()
            session=initialization.ReconstructionSession(target,self.vae,identity)
        latest=None
        def save(s):
            nonlocal latest
            if s.step%10==0:
                latest=_sealed({"schema":CHECKPOINT_VERSION,"configuration":copy.deepcopy(CONFIG),
                    "phase":"initialization","step":s.step,"binding":binding,
                    "optimizer_phase":"unmarked initialization Adam only","state":s.state_dict()})
                _pure_callback(on_checkpoint,latest)
            if check is not None:check()
        save(session)
        session.advance(stop_step,on_update=save)
        return latest

    def embed(self,rgb,initializer,*,resume=None,stop_step=100,on_checkpoint=None,event=None,check=None):
        if type(stop_step) is not int or stop_step not in range(0,101,10):
            raise ValueError("Embedding stop must be a scheduled0..100 checkpoint")
        rgb,target=self._source(rgb)
        _check_seal(initializer)
        b=initializer["binding"]
        binding=self._binding(rgb,target,b["source_identity"],b["owner"],
                              b["source_uid"])
        self._verify(initializer,"initialization",binding)
        state=initializer["state"]
        expected_identity={"source_id":b["source_identity"]["source_id"],"source_rgb8_sha256":binding["source_rgb8_sha256"],
            "model_sha256":self.model_identity["vae_fp32"],"candidate_binding_sha256":initialization.digest(binding)}
        initialization._validate_payload(state,expected_identity,initialization.digest(target),binding["runtime"])
        if initializer["step"]!=200 or state["step"]!=200:raise ValueError("Complete original200 initializer required")
        u0=state["z"].to(target.device).clone()
        if u0.shape!=(1,4,64,64):raise ValueError("Exactly one unscaled4x64x64 initializer latent required")
        E=self.feature(rgb)
        H=component.codec.perceptual_hash(component.codec.luminance_from_rgb(rgb.tolist()),profile=self.profile)
        feature_receipt={"E":torch.from_numpy(E.copy()),"H":H}
        initializer_sha=initialization.digest(initializer)
        oracle=component.FixedSourceScores(E,H,binding["owner"],target.device)
        core_resume=None
        if resume is not None:
            self._verify(resume,"embedding",binding)
            if resume.get("initializer_sha256")!=initializer_sha or resume.get("feature_sha256")!=initialization.digest(feature_receipt):
                raise ValueError("Embedding initializer/features provenance differs")
            core_resume=resume["state"]
            if core_resume["step"]!=resume["step"] or core_resume["step"]>stop_step:
                raise ValueError("Embedding resume step differs")
            self._validate_embedding_state(core_resume,u0)
        else:
            _seed_fresh_phase()
        latest=None
        class PhaseStop(Exception):pass
        def save(step,u,optimizer):
            nonlocal latest
            payload={"u":u.detach().cpu().clone(),"optimizer":initialization._cpu_tree(optimizer.state_dict()),
                     "step":step,"rng":_method_rng()}
            latest=_sealed({"schema":CHECKPOINT_VERSION,"configuration":copy.deepcopy(CONFIG),
                "phase":"embedding","step":step,"binding":binding,"initializer_sha256":initializer_sha,
                "initializer_step":200,"feature_sha256":initialization.digest(feature_receipt),
                "optimizer_phase":"fresh embedding Adam; no initialization moments","state":payload})
            _pure_callback(on_checkpoint,latest)
            if step==stop_step and stop_step<100:raise PhaseStop()
        cfg={"steps":100,"learning_rate":.01,"adam_betas":[.9,.999],"adam_eps":1e-8,
             "cycle_every":2,"checkpoint_every":10}
        def emit(row):_pure_callback(event,row)
        try:
            result=component.optimize(self.embedder,target,u0,oracle,cfg,emit,save,check or (lambda:None),core_resume)
        except PhaseStop:
            return {"checkpoint":latest,"completed":False,"marked_rgb8":None}
        raw=result["residual"].detach().float().cpu().numpy()[0].transpose(1,2,0).astype(np.float64)
        marked,cap=component.residual.cap(rgb,raw)
        return {"checkpoint":latest,"completed":True,"marked_rgb8":marked,
            "cap":cap,"core_result":result,"initializer_sha256":initializer_sha,
            "owner":binding["owner"],"seed_metadata":copy.deepcopy(binding["schedule"])}

    @staticmethod
    def _validate_embedding_state(state,u0):
        if (not isinstance(state,dict) or set(state)!={"u","optimizer","step","rng"} or
                type(state["step"]) is not int or state["step"] not in range(0,101,10) or
                state["u"].shape!=u0.shape or state["u"].dtype!=torch.float32 or
                not torch.isfinite(state["u"]).all()):raise ValueError("Invalid embedding latent/state")
        expected=torch.optim.Adam([torch.zeros(1,requires_grad=True)],lr=.01,betas=(.9,.999),eps=1e-8).state_dict()
        if state["optimizer"]["param_groups"]!=expected["param_groups"]:
            raise ValueError("Embedding Adam parameters differ")
        moments=state["optimizer"]["state"]
        if state["step"]==0:
            if moments:raise ValueError("Embedding step0 must have fresh empty Adam state")
        else:
            if (set(moments)!={0} or set(moments[0])!={"step","exp_avg","exp_avg_sq"} or
                    float(moments[0]["step"])!=state["step"]):
                raise ValueError("Embedding Adam step differs")
            for key in ("exp_avg","exp_avg_sq"):
                x=moments[0][key]
                if x.shape!=u0.shape or x.dtype!=torch.float32 or not torch.isfinite(x).all():
                    raise ValueError("Invalid embedding Adam moment")

    def readout(self,saved_suspect_rgb8,owner):
        """Only saved suspect bytes/public claim/models/profile reach the core reader."""
        component.core._owner(owner)
        if (not isinstance(saved_suspect_rgb8,np.ndarray) or saved_suspect_rgb8.dtype!=np.uint8 or
                saved_suspect_rgb8.shape!=(512,512,3)):
            raise ValueError("Saved canonical512 RGB8 suspect required")
        return component.detect(saved_suspect_rgb8.copy(),owner,self.public)
