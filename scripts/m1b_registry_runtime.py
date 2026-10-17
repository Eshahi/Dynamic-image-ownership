"""Versioned registry extension of the official M1b worker; no launcher."""
from __future__ import annotations
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

PROTOCOL = "registry-two-factor-v1"
ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ALPHA, BETA = "qim-pilot-owner-alpha", "qim-pilot-owner-beta"
DOCS = "research/registry-confirmation/"

def read(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p, base=ROOT): return Path(p) if Path(p).is_absolute() else Path(base)/p

def validate_plan(plan, base=ROOT):
    base=Path(base)
    if plan.get("protocol") != PROTOCOL or plan.get("data_split") not in ("test", "development"):
        raise ValueError("Frozen registry protocol/split required")
    if plan.get("seeds") != [15,16,17] or plan.get("strengths") != [.1,.2,.4] or plan.get("sibling_seeds") != list(range(21,33)):
        raise ValueError("Frozen registry seeds/strengths differ")
    if plan.get("scenario_seeds") != [15,16] or plan.get("models") != ["sd15","sd21"]:
        raise ValueError("Frozen scenario/model values differ")
    frozen=read(resolve(plan["frozen"],base))
    if any(frozen[k] != v for k,v in dict(tau1_d1=.0594367,tau2_b1=.90,tauF_b1_fallback=.99,psnr_cutoff_primary=18.126065828471827).items()):
        raise ValueError("Frozen threshold binding differs")
    pins=read(base/DOCS/"source-pins.json")
    for rel, sha in pins["files"].items():
        if digest(base/rel)!=sha: raise ValueError("Source pin differs: "+rel)
    ref=plan["sources"]["index"]
    if digest(resolve(ref["path"],base))!=ref["sha256"]: raise ValueError("Source index digest differs")
    entries=read(resolve(ref["path"],base))["entries"]
    allowed=read(base/DOCS/("heldout-index.json" if plan["data_split"]=="test" else "development-index.json"))["entries"]
    keyed={str(s["source_id"]):s for s in allowed}
    if not entries or len({str(s["source_id"]) for s in entries})!=len(entries): raise ValueError("Distinct source IDs required")
    for s in entries:
        if s!=keyed.get(str(s["source_id"])): raise ValueError("Non-admitted source or changed metadata")
    if plan["data_split"]=="test" and (len(entries)!=300 or len({s["group_id"] for s in entries})!=300):
        raise ValueError("All 300 held-out groups required")
    approved_near=read(base/DOCS/("heldout-shots.json" if plan["data_split"]=="test" else "development-near.json"))
    allowed_near=approved_near.get("selected",approved_near.get("pairs",[]))
    for pair in plan["near"]:
        if pair not in allowed_near: raise ValueError("Non-admitted near pair")
    if plan["data_split"]=="test" and plan["near"]!=allowed_near: raise ValueError("Complete near panel required")
    if plan["data_split"]=="test" and plan.get("fault_injection"): raise ValueError("Test faults prohibited")
    config=read(base/DOCS/"frozen-config.json")
    if digest(base/config["method"]["path"])!=config["method"]["sha256"]: raise ValueError("F5 config differs")
    return plan,entries

def data_files(plan):
    files=[DOCS+f for f in ("source-pins.json","frozen-config.json","development-index.json","development-near.json","heldout-index.json","heldout-shots.json","model-lock.json")]
    files += [plan["sources"]["index"]["path"],plan["frozen"],"configs/f5-r2.json","research/a6-candidate-model-assets.json","experiments/c4-v5-two-tier-regeneration-v1/profile.json"]
    files += list(read(ROOT/DOCS/"source-pins.json")["files"])
    files += [DOCS+f for f in ("tears-of-steel-shots-index.json","development-frame-exposure-index.json","div2k-exposure.json")]
    return sorted(set(files))

def scientific_core(plan, read_bytes=None):
    import m1b_coco512_worker as W
    rb=read_bytes or (lambda p:resolve(p).read_bytes())
    code=W.code_closure(read=lambda p: rb(p).decode() if resolve(p).is_file() else None)
    code += ["thesis-agent-skills/src/thesis_agents/compute.py", "thesis-agent-skills/skills/thesis-compute-runner/scripts/_runtime/thesis_agents/compute.py"]
    core=dict(protocol=PROTOCOL, science_digest=W.object_digest({k:v for k,v in plan.items() if k not in ("max_wall_seconds","approval_path","fault_injection","label")}),code_sha256={p:W.sha_bytes(rb(p)) for p in sorted(set(code))},data_sha256={p:W.sha_bytes(rb(p)) for p in data_files(plan)})
    core["core_sha256"]=W.object_digest(core)
    return core

class ScientificFailure(Exception): pass
class CooperativeStop(BaseException): pass

class Runtime:
    def __init__(self, plan):
        import numpy as np
        import torch
        import three_threat_models as models
        from journal_vae_probe import Evaluator
        from f4_transfer_probe import ASSETS
        models.block_network()
        models.verify_assets(ASSETS, ROOT/"research/a6-candidate-model-assets.json")
        self.np,self.torch,self.models,self.assets=np,torch,models,ASSETS
        self.ev=Evaluator(); self.pipe=None; self.model=None; self.budget=lambda:None
        lock=read(ROOT/DOCS/"model-lock.json")
        for item in lock["sd21_files"]:
            if digest(Path(lock["sd21_root"])/item["file"])!=item["sha256"]: raise ValueError("SD2.1 asset hash differs")
        self.sd21=Path(lock["sd21_root"])
        if digest(lock["profile_run"]["path"])!=lock["profile_run"]["sha256"]:raise ValueError("Scorer profile metadata differs")
    def load(self,p):
        from PIL import Image
        with Image.open(p) as im:
            if im.mode!="RGB" or im.size!=(512,512): raise ValueError("RGB512 required")
            return self.np.asarray(im).copy()
    def embed(self,rgb,folder):
        from journal_e3_writer import supply_f5
        from m1b_e3_s1_runtime import Runtime as OldRuntime
        result=supply_f5(rgb,self.ev,folder,self.budget)
        OldRuntime._execution_error(self,result)
        if result['status']!='ok': raise ScientificFailure(result.get('error','unreadable supplier'))
        return dict(image=result['bootstrap_image'],payload=result['payload'],supplier=result,quality=self.ev.metrics(rgb,self.load(result['bootstrap_image'])))
    def set_model(self,model):
        if model==self.model:return
        self.pipe=None;gc.collect();self.torch.cuda.empty_cache()
        if model=='sd15':self.pipe=self.models.load_regenerator(self.assets)
        else:
            from diffusers import AutoencoderKL,DDIMScheduler,StableDiffusionImg2ImgPipeline
            vae=AutoencoderKL.from_pretrained(self.sd21/'vae',local_files_only=True,use_safetensors=True,torch_dtype=self.torch.float16)
            self.pipe=StableDiffusionImg2ImgPipeline.from_pretrained(self.sd21,vae=vae,variant='fp16',local_files_only=True,use_safetensors=True,torch_dtype=self.torch.float16,safety_checker=None,requires_safety_checker=False)
            self.pipe.scheduler=DDIMScheduler.from_config(self.pipe.scheduler.config)
            self.pipe.set_progress_bar_config(disable=True);self.pipe.to('cuda')
        self.model=model
    def attack(self,rgb,model,strength,seed):
        from m1b_e3_s1_runtime import registry_regeneration
        self.set_model(model)
        return registry_regeneration(rgb,strength,seed,model,self.pipe,self.torch)
    def native(self,rgb,owner):return self.ev.detect(rgb,'f5',owner)
    def descriptor(self,rgb,path):
        import revised_watermark_v5 as v5
        import journal_fine_gaussian_instance as fine
        from PIL import Image
        _,key,config=v5._resolve(self.ev.profile,None)
        d=fine.descriptor(v5.luminance_from_rgb(rgb.tolist()),key,config)
        vector=d['vector']; abstain=vector is None
        if abstain:
            from registry_step2_fresh_analysis import native_weak_detail
            if not native_weak_detail(d):raise ValueError('Unknown descriptor failure')
        a=self.np.asarray([] if abstain else vector,dtype=self.np.float64)
        if a.size:a=a/self.np.linalg.norm(a)
        b=self.np.asarray(Image.fromarray(rgb).convert('L').resize((32,32),Image.Resampling.BOX),dtype=self.np.float64).ravel();b=b-b.mean()
        bn=self.np.linalg.norm(b);b=b/bn if bn>0 else self.np.array([])
        if not self.np.isfinite(a).all() or not self.np.isfinite(b).all():raise ValueError('Nonfinite descriptor')
        self.np.savez(path,D1=a,B1=b)
        return dict(cache=str(path),d1_abstained=abstain,b1_abstained=not bool(b.size),native_detail={k:v for k,v in d.items() if k!='vector'})
    def close(self):
        self.pipe=None;self.ev=None;gc.collect();self.torch.cuda.empty_cache()

def run(manifest,plan,out,runtime_factory=Runtime):
    import m1b_coco512_worker as W
    plan,sources=validate_plan(plan)
    W.bind_manifest(manifest)
    if plan['data_split']=='test':
        if not plan.get('approval_path'):raise ValueError('Held-out pixels refused before exact human approval')
        W.check_approval(plan,manifest)
    # All approval and metadata checks precede runtime construction and pixel reads.
    out=Path(out);(out/'outputs').mkdir(parents=True,exist_ok=True);(out/'metrics').mkdir(exist_ok=True)
    core=scientific_core(plan)
    ctx=out/'outputs/run-context.json'
    if ctx.exists() and read(ctx)['core_sha256']!=core['core_sha256']:raise ValueError('Resume scientific core differs')
    W.atomic_json(ctx,core)
    W.atomic_json(out/"outputs/lineage.json",dict(mode="same-manifest journal resume",core_sha256=core["core_sha256"]))
    os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR",str(out/"checkpoints/torch-inductor-cache"))
    journal=W.Journal(out/'outputs/journal.jsonl')
    start=time.monotonic(); prior=read(out/'outputs/run.json').get('duration_seconds',0) if (out/'outputs/run.json').exists() else 0
    state=dict(protocol=PROTOCOL,data_split=plan['data_split'],commit=manifest['git_commit'],outcome='running',duration_seconds=prior,usd=0)
    def save():
        state.update(duration_seconds=prior+time.monotonic()-start,completed_units=len(journal.rows))
        W.atomic_json(out/'outputs/run.json',state)
    def budget():
        if (out/'STOP').exists() or time.monotonic()-start>=plan['max_wall_seconds']:raise CooperativeStop()
    rt=None;current=None
    def unit(rid,fn,**fields):
        nonlocal current
        if rid in journal:return journal.get(rid)
        current=rid;budget();fault=plan.get('fault_injection') or {}
        if fault.get('unit')==rid and not (out/'outputs/fault-triggered.json').exists():
            W.atomic_json(out/'outputs/fault-triggered.json',dict(unit=rid,kind=fault['kind']))
            if fault['kind']=='stop':raise CooperativeStop()
            raise OSError('Injected infrastructure interruption')
        tick=time.monotonic()
        try:row=dict(fn(),outcome='completed')
        except ScientificFailure as e:row=dict(outcome='scientific_failure',error=str(e))
        row.update(id=rid,**fields,duration_seconds=time.monotonic()-tick)
        journal.emit(row);save();print(json.dumps(dict(id=rid,outcome=row['outcome'])),flush=True)
        return row
    def missing():return dict(outcome_reason='input unavailable')
    def image_unit(rid,parents,fn,**fields):
        if rid in journal:return journal.get(rid)
        if any(not journal.get(p) or not journal.get(p).get('image') for p in parents):
            row=dict(id=rid,outcome='input_unavailable',parents=parents,**fields);journal.emit(row);save();return row
        return unit(rid,lambda:fn(*[rt.load(journal.get(p)['image']) for p in parents]),**fields)
    def store(rgb,rid,**fields):
        from PIL import Image
        p=out/'outputs/images'/f'{W.file_tag(rid)}.png';p.parent.mkdir(exist_ok=True)
        Image.fromarray(rgb).save(p)
        return dict(image=str(p.resolve()),**fields)
    save()
    try:
        budget();rt=runtime_factory(plan);rt.budget=budget
        for s in sources:
            sid=s['source_id']
            def canon(s=s,sid=sid):
                from m1b_canonical_source import registry_canonical
                rgb,receipt=registry_canonical(s,plan['data_split'],plan['data_split']=='test')
                return store(rgb,f'canon:{sid}',canonicalization=receipt)
            unit(f'canon:{sid}',canon,source_id=sid)
        # Development pairs are admitted by exact metadata equality; test acquisition is approval-gated here.
        from m1b_registry_footage import prepare_near
        near=prepare_near(plan,out,budget,heldout_authorized=plan['data_split']=='test')
        for pair in near:
            for side in (0,1):
                unit(f"near:{pair['pair_id']}:{side}",lambda pair=pair,side=side:dict(image=pair['left_path' if side==0 else 'right_path']),pair_id=pair['pair_id'])
        for s in sources:
            sid=s['source_id'];rid=f'embed:{sid}'
            folder=out/'outputs'/str(sid)
            def embed(rgb,folder=folder):
                attempt=1
                while (folder/f'supplier-attempt{attempt}').exists():attempt+=1
                return rt.embed(rgb,folder/f'supplier-attempt{attempt}')
            image_unit(rid,[f'canon:{sid}'],embed,source_id=sid)
        for s in sources:
            sid=s['source_id']
            image_unit(f'enroll:{sid}',[f'embed:{sid}'],lambda rgb,sid=sid:dict(owner=ALPHA,q=journal.get(f'embed:{sid}')['payload']['q']),source_id=sid)
        for model in plan['models']:
            for s in sources:
                sid=s['source_id']
                for strength in plan['strengths']:
                    for seed in plan['seeds']:
                        for arm in ('C0','C1'):
                            rid=f't3:{model}:{sid}:{strength}:{seed}:{arm}'
                            def attack(rgb,rid=rid,model=model,strength=strength,seed=seed):
                                arr,receipt=rt.attack(rgb,model,strength,seed);return store(arr,rid,attack=receipt)
                            image_unit(rid,[f'canon:{sid}' if arm=='C0' else f'embed:{sid}'],attack,source_id=sid,model=model,strength=strength,seed=seed,arm=arm)
            for s in sources:
                sid=s['source_id']
                for strength in (.2,.4):
                    rid=f'scenario:{model}:{sid}:{strength}'
                    def attack(rgb,rid=rid,model=model,strength=strength):
                        arr,receipt=rt.attack(rgb,model,strength,16);return store(arr,rid,attack=receipt)
                    image_unit(rid,[f't3:{model}:{sid}:{strength}:15:C1'],attack,source_id=sid,model=model,strength=strength,seed=16)
        ordered=sorted(sources,key=lambda s:(hashlib.sha256(s['uid'].encode()).hexdigest(),s['uid']))
        for i,s in enumerate(ordered):
            sid=s['source_id'];recipient=ordered[(i+1)%len(ordered)]['source_id']
            for scale in (.5,1.):
                rid=f't4:{sid}:{scale}'
                def transfer(rec,donor,orig,rid=rid,scale=scale):
                    from three_threat_protocol import residual_transfer
                    return store(rt.np.asarray(residual_transfer(rec.tolist(),donor.tolist(),orig.tolist(),scale),rt.np.uint8),rid)
                image_unit(rid,[f'canon:{recipient}',f'embed:{sid}',f'canon:{sid}'],transfer,source_id=sid,donor_id=sid,recipient_id=recipient,scale=scale)
        rt.pipe=None;rt.model=None;gc.collect();rt.torch.cuda.empty_cache()
        images=[(k,r) for k,r in journal.rows.items() if k.startswith(('canon:','embed:','t3:','t4:','scenario:','near:'))]
        for key,row in images:
            sid=row.get('source_id');q=(journal.get(f'embed:{sid}') or {}).get('payload',{}).get('q')
            for owner in (ALPHA,BETA):
                def native(rgb,owner=owner,q=q):
                    from registry_step2_screen import pointer,distance
                    call=rt.native(rgb,owner);p=pointer(call)
                    recovered=bool(p['recovered'] and q is not None and distance(p['q'],q)<=6)
                    return dict(detection=call,pointer_recovered=recovered)
                image_unit(f'native:{key}:{owner}',[key],native,source_id=sid,owner=owner,image_unit=key)
        for key,row in images:
            cache=out/'outputs/descriptors'/f'{W.file_tag(key)}.npz';cache.parent.mkdir(exist_ok=True)
            image_unit(f'descriptor:{key}',[key],lambda rgb,cache=cache:rt.descriptor(rgb,cache),source_id=row.get('source_id'),image_unit=key)
        rt.close();rt=None
        from m1b_registry_analysis import analyze
        endpoint=analyze(out,dict(plan,near=near),sources)
        W.atomic_json(out/'metrics/endpoints.json',endpoint)
        state['outcome']='completed'
    except CooperativeStop:state['outcome']='cooperative_stop'
    except BaseException:
        state.update(outcome='infrastructure_interrupted',unit=current,error=traceback.format_exc())
        raise
    finally:
        if rt is not None:rt.close()
        save()
    return 0 if state['outcome']=='completed' else 2
