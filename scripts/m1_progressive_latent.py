"""Progressive guided DDIM latent carrier candidate, inspired by GROW.

Exploratory public 16-bit carrier only; not a faithful GROW reproduction.
No inversion: native readout is a VAE encoder and a channel-zero DCT.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
ASSETS = MAIN / ".thesis-build/assets/a6"
CONFIG = {"alphas": [0.1, 0.3, 0.5], "etas": [25.0, 100.0],
          "steps": 50, "start_ratio": 0.5, "guidance_scale": 7.5,
          "bits": 16, "repetitions": 8, "channel": 0,
          "band_sum": [16, 48], "carrier_seed": "m1-progressive-public-v1",
          "payload": "1011010001101001", "threshold": 0.875,
          "wrong_payload_queries": 64, "wrong_payload_seed": "m1-progressive-wrong-payload-v1",
          "attack_strengths": [0.1, 0.4], "attack_seed": 0,
          "gpu_budget_bytes": 10*1024**3, "guidance_phase": "first-half-after-CFG",
          "loss": "masked mean square: denominator128", "size": [512,512]}


def dct_matrix(n, *, device="cpu"):
    import torch
    k = torch.arange(n, dtype=torch.float32, device=device)[:,None]
    x = torch.arange(n, dtype=torch.float32, device=device)[None,:]
    basis = torch.cos(torch.pi*(x+.5)*k/n)*(2/n)**.5
    basis[0] /= 2**.5
    return basis


def dct2(x, basis):
    return basis @ x @ basis.T


def idct2(x, basis):
    return basis.T @ x @ basis


def positions(size=64):
    lo, hi = CONFIG["band_sum"]
    candidates = [(u,v) for u in range(size) for v in range(size) if lo <= u+v <= hi]
    def rank(p):
        return hashlib.sha256((CONFIG["carrier_seed"]+f":{p[0]}:{p[1]}").encode()).digest()
    return sorted(candidates, key=rank)[:CONFIG["bits"]*CONFIG["repetitions"]]


def target_and_mask(alpha, basis):
    import torch
    target = torch.zeros((64,64), device=basis.device)
    mask = torch.zeros_like(target)
    for i,(u,v) in enumerate(positions()):
        target[u,v] = alpha*(1 if CONFIG["payload"][i//CONFIG["repetitions"]] == "1" else -1)
        mask[u,v] = 1
    return target, mask


def analytic_gradient(plane, target, mask, basis):
    """Derivative of sum(mask*(DCT(x)-target)^2)/sum(mask)."""
    residual = mask*(dct2(plane, basis)-target)
    return 2*idct2(residual, basis)/mask.sum()


def read_bits(plane, basis):
    coef = dct2(plane.float(), basis)
    locations=positions()
    signs = [int(x > 0) for x in coef[tuple(zip(*locations))].tolist()]
    r = CONFIG["repetitions"]
    # Explicit tie rule: ties decode zero, never random/favorable.
    bits = [int(sum(signs[i*r:(i+1)*r]) > r/2) for i in range(CONFIG["bits"])]
    expected = [int(x) for x in CONFIG["payload"]]
    acc = sum(a == b for a,b in zip(bits,expected))/len(bits)
    return {"bits": "".join(map(str,bits)), "bit_accuracy": acc,
            "bit_errors": int(round(len(bits)*(1-acc))),
            "wrong_payload_bit_accuracy": 1-acc,
            "wrong_payload_bit_errors": int(round(len(bits)*acc)),
            "found_descriptive": acc >= CONFIG["threshold"],
            "wrong_payload_found_descriptive": 1-acc >= CONFIG["threshold"],
            "wrong_payload_queries": wrong_payload_scores(bits),
            "coefficient_sign_accuracy": sum(s == expected[i//r] for i,s in enumerate(signs))/len(signs)}


def wrong_payloads():
    """Domain-separated SHAKE payload hypotheses; no image-dependent selection."""
    payloads=[]
    for i in range(CONFIG["wrong_payload_queries"]):
        counter=0
        while True:
            material=f"{CONFIG['wrong_payload_seed']}:{i}:{counter}".encode()
            bits="".join(f"{byte:08b}" for byte in hashlib.shake_256(material).digest(2))
            if bits != CONFIG["payload"]:
                break
            counter+=1
        payloads.append(bits)
    return payloads


def wrong_payload_scores(bits):
    accuracy=[sum(a==int(b) for a,b in zip(bits,p))/CONFIG["bits"] for p in wrong_payloads()]
    return {"queries":len(accuracy),"bit_accuracies":accuracy,
            "false_findings":sum(a>=CONFIG["threshold"] for a in accuracy),
            "denominator":len(accuracy),"threshold":CONFIG["threshold"],
            "caveat":"Fixed SHAKE hypotheses share one extracted word; query results and repeated conditions are correlated, not independent image-level FPR evidence"}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024**2),b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, obj):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    tmp.replace(path)


def validate(manifest):
    if manifest.get("data_split") != "synthetic" or manifest.get("config") != CONFIG:
        raise ValueError("Exact synthetic candidate configuration required")
    reference=json.loads((ROOT/"research/m1-gs-synthetic.json").read_text())
    cases=manifest.get("cases",[])
    expected=[{"seed":c["seed"],"prompt":c["prompt"]} for c in reference["cases"]]
    if [c['seed'] for c in expected]!=list(range(1000,1004)) or manifest.get('schema_version')!='m1-progressive-synthetic-v1' or cases!=expected or any(type(c['seed']) is not int for c in cases):
        raise ValueError("Exact ordered four synthetic prompt/seed cases required")
    return cases


def generate(pipe, prompt, seed, alpha, eta, journal):
    import torch
    from diffusers import DDIMScheduler
    from three_threat_models import DDIM_CONFIG
    pipe.scheduler=DDIMScheduler(**DDIM_CONFIG)
    pipe.scheduler.set_timesteps(CONFIG["steps"],device="cuda")
    with torch.inference_mode():
        embeddings,unconditional=pipe.encode_prompt(prompt,"cuda",1,True,negative_prompt="")[:2]
    embeddings=torch.cat([unconditional,embeddings])
    generator=torch.Generator(device="cuda").manual_seed(seed)
    latents=torch.randn((1,4,64,64),generator=generator,device="cuda",dtype=pipe.unet.dtype)*pipe.scheduler.init_noise_sigma
    basis=dct_matrix(64,device="cuda")
    target,mask=target_and_mask(alpha,basis)
    times=[int(t) for t in pipe.scheduler.timesteps]
    guidance_indices=list(range(int(CONFIG["steps"]*(1-CONFIG["start_ratio"]))))
    with torch.inference_mode():
        for i,t in enumerate(pipe.scheduler.timesteps):
            inp=pipe.scheduler.scale_model_input(torch.cat([latents,latents]),t)
            eps=pipe.unet(inp,t,encoder_hidden_states=embeddings,return_dict=False)[0]
            eps_u,eps_c=eps.chunk(2)
            eps=eps_u+CONFIG["guidance_scale"]*(eps_c-eps_u)
            if alpha and i in guidance_indices:
                a=pipe.scheduler.alphas_cumprod[int(t)].to(device="cuda",dtype=torch.float32)
                z0=(latents.float()-(1-a).sqrt()*eps.float())/a.sqrt()
                grad=analytic_gradient(z0[0,CONFIG["channel"]],target,mask,basis)
                guided=z0.clone()
                guided[0,CONFIG["channel"]]-=eta*grad
                # Exact rearrangement of z0=(zt-sqrt(1-a)*eps)/sqrt(a).
                eps=((latents.float()-a.sqrt()*guided)/(1-a).sqrt()).to(pipe.unet.dtype)
            latents=pipe.scheduler.step(eps,t,latents,eta=0.0,return_dict=False)[0]
            if i % 10 == 0:
                journal({"phase":"denoise","seed":seed,"alpha":alpha,"eta":eta,"step_index":i,"timestep":int(t)})
        decoded=pipe.vae.decode(latents/pipe.vae.config.scaling_factor,return_dict=False)[0]
        decoded,flags=pipe.run_safety_checker(decoded,"cuda",pipe.vae.dtype)
        if flags is None or len(flags) != 1 or bool(flags[0]):
            raise RuntimeError("Safety checker incomplete or blocked output")
        image=pipe.image_processor.postprocess(decoded,output_type="pil",do_denormalize=[True])[0]
    return image, {"timesteps":times,"guided_step_indices":guidance_indices if alpha else [],
                   "safety_flag":False,"scheduler_eta":0.0}


def score(pipe, rgb):
    import numpy as np
    import torch
    from PIL import Image
    torch.cuda.synchronize()
    started=time.monotonic()
    basis=dct_matrix(64,device="cuda")
    with torch.inference_mode():
        tensor=pipe.image_processor.preprocess(Image.fromarray(rgb)).to(device="cuda",dtype=pipe.vae.dtype)
        z=pipe.vae.encode(tensor).latent_dist.mode()*pipe.vae.config.scaling_factor
        native=read_bits(z[0,CONFIG["channel"]],basis)
        torch.cuda.synchronize()
        native_seconds=time.monotonic()-started
        pixel_started=time.monotonic()
        # Diagnostic image luminance DCT uses same position list; no claimed parity.
        tiny=np.asarray(Image.fromarray(rgb).resize((64,64),Image.Resampling.BICUBIC),dtype=np.float32)
        gray=(tiny[...,0]*.299+tiny[...,1]*.587+tiny[...,2]*.114)/127.5-1
        pixel=read_bits(torch.from_numpy(gray).to("cuda"),basis)
    torch.cuda.synchronize()
    return {"native_vae_dct":native,"image_dct_diagnostic":pixel,
            "native_vae_dct_seconds":native_seconds,
            "image_dct_diagnostic_seconds":time.monotonic()-pixel_started,
            "extract_both_seconds":time.monotonic()-started}


def artifact_path(output, relative):
    """Resume never follows arbitrary absolute/traversal/symlink artifacts."""
    value=Path(relative)
    if value.is_absolute() or len(value.parts)!=1 or value.suffix!=".png" or value.name!=relative:
        raise ValueError("Unsafe resume artifact path")
    path=output/value
    if path.is_symlink() or not path.is_file() or path.resolve().parent!=output.resolve():
        raise ValueError("Missing/linked resume artifact")
    return path


def planned_ids():
    return [f'seed{s}-C0' for s in range(1000,1004)]+[
        f'seed{s}-a{a}-e{e}' for s in range(1000,1004) for a in CONFIG['alphas'] for e in CONFIG['etas']]


def finite_number(value):
    return not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)


def validate_quality(value, *, clip=False):
    if not isinstance(value,dict):raise ValueError('Missing quality object')
    for name in ('mse_rgb8','ssim_rgb','lpips')+ (('clip_cosine',) if clip else ()):
        if not finite_number(value.get(name)):raise ValueError('Missing/nonfinite quality '+name)
    if value['mse_rgb8']<0 or type(value.get('psnr_infinite')) is not bool:raise ValueError('Malformed quality MSE/PSNR flag')
    if value['mse_rgb8']==0:
        if value['psnr_infinite'] is not True or value.get('psnr_db','missing') is not None:raise ValueError('Inconsistent infinite PSNR')
    elif value['psnr_infinite'] or not finite_number(value.get('psnr_db')):raise ValueError('Missing/nonfinite PSNR')


def validate_readout(value):
    if not isinstance(value,dict) or not isinstance(value.get('bits'),str) or len(value['bits'])!=16 or set(value['bits'])-{'0','1'}:
        raise ValueError('Missing/malformed extracted word')
    matches=sum(a==b for a,b in zip(value['bits'],CONFIG['payload']));acc=matches/16
    expected={'bit_accuracy':acc,'bit_errors':16-matches,'wrong_payload_bit_accuracy':1-acc,
        'wrong_payload_bit_errors':matches,'found_descriptive':acc>=CONFIG['threshold'],
        'wrong_payload_found_descriptive':1-acc>=CONFIG['threshold']}
    for key,want in expected.items():
        got=value.get(key)
        if type(want) is bool:
            if type(got) is not bool or got!=want:raise ValueError('Readout decision inconsistent: '+key)
        elif not finite_number(got) or got!=want or (type(want) is int and type(got) is not int):raise ValueError('Readout score inconsistent: '+key)
    if not finite_number(value.get('coefficient_sign_accuracy')) or not 0<=value['coefficient_sign_accuracy']<=1:
        raise ValueError('Missing/nonfinite coefficient sign score')
    queries=value.get('wrong_payload_queries',{})
    scores=queries.get('bit_accuracies',[]) if isinstance(queries,dict) else []
    bits=[int(x) for x in value['bits']];reference=wrong_payload_scores(bits)
    if not isinstance(scores,list) or len(scores)!=64 or any(not finite_number(x) for x in scores):raise ValueError('Missing/nonfinite wrong query scores')
    for key in ('queries','bit_accuracies','false_findings','denominator','threshold'):
        if queries.get(key)!=reference[key]:raise ValueError('Wrong payload query mismatch: '+key)
    if any(type(queries.get(k)) is not int for k in ('queries','false_findings','denominator')) or not finite_number(queries.get('threshold')):
        raise ValueError('Malformed wrong payload query types')


def validate_condition(value):
    if not isinstance(value,dict):raise ValueError('Missing condition object')
    for key in ('native_vae_dct','image_dct_diagnostic'):validate_readout(value.get(key))
    for key in ('native_vae_dct_seconds','image_dct_diagnostic_seconds','extract_both_seconds'):
        if not finite_number(value.get(key)) or value[key]<0:raise ValueError('Missing/nonfinite extraction time')
    validate_quality(value.get('quality_vs_same_arm_clean'),clip=True)


def prepare_resume(record, identities, output):
    if any(record.get(k)!=v for k,v in identities.items()):
        raise ValueError("Resume identity mismatch")
    required={"clean","vae","t3-0.1","t3-0.4"}
    if record.get('config')!=CONFIG or record.get('planned_ids')!=planned_ids():raise ValueError('Resume fixed inventory/config mismatch')
    completed=set();prefixes=set()
    for row in record["rows"]:
        if row.get('id') not in record['planned_ids'] or row.get('seed') not in range(1000,1004):raise ValueError('Unplanned resume row')
        ident=row['id'];seed=row['seed']
        if row.get('control')=='C0':expected=f'seed{seed}-C0'
        elif row.get('control')=='C1' and row.get('alpha') in CONFIG['alphas'] and row.get('eta') in CONFIG['etas']:
            expected=f"seed{seed}-a{row['alpha']}-e{row['eta']}"
        else:raise ValueError('Resume row control/variant mismatch')
        prefix=row.get('artifact_prefix','')
        suffix=prefix.removeprefix(ident+'-attempt')
        if ident!=expected or not prefix.startswith(ident+'-attempt') or not suffix.isdigit() or int(suffix)<1 or prefix in prefixes:
            raise ValueError('Resume row identity/attempt conflict')
        prefixes.add(prefix)
        if row["outcome"]=="completed":
            if ident in completed:raise ValueError('Duplicate completed resume ID')
            completed.add(ident)
            if set(row.get("conditions",{}))!=required or len(row.get("artifacts",[]))!=4:
                raise ValueError("Completed resume row is incomplete")
            names=[a.get('path') for a in row['artifacts']]
            if len(set(names))!=4 or set(names)!={prefix+'-'+k+'.png' for k in required}:raise ValueError('Resume artifact condition membership mismatch')
            for value in row['conditions'].values():validate_condition(value)
            if row['control']=='C1':validate_quality(row.get('quality_to_matched_C0'))
            generation=row.get('generation',{})
            if generation.get('timesteps')!=list(range(981,0,-20)) or generation.get('guided_step_indices')!=(list(range(25)) if row['control']=='C1' else []) or generation.get('safety_flag') is not False or not finite_number(generation.get('scheduler_eta')) or generation['scheduler_eta']!=0. or any(type(x) is not int for x in generation['timesteps']+generation['guided_step_indices']):
                raise ValueError('Resume generation metadata incomplete/inconsistent')
            for artifact in row["artifacts"]:
                if sha(artifact_path(output,artifact["path"]))!=artifact["sha256"]:
                    raise ValueError("Resume artifact hash mismatch")
            if row["control"]=="C0":
                if row.get('png_path')!=prefix+'.png' or sha(artifact_path(output,row["png_path"]))!=row.get("png_sha256"):
                    raise ValueError("Resume C0 PNG hash mismatch")
        elif row["outcome"]=="started":
            row.update(outcome="interrupted",error="Previous invocation ended without a terminal row")
    return record


def run(manifest_path, output):
    started=time.monotonic()
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    cases=validate(manifest)
    if not output.is_relative_to(MAIN / ".thesis-build/dev-runs"):
        raise ValueError("Outputs must be under MAIN/.thesis-build/dev-runs")
    output.mkdir(parents=True,exist_ok=True)
    state_path=output/"run.json"
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    identities={"manifest_sha256":sha(manifest_path),"script_sha256":sha(__file__),"commit":commit}
    identities["dependency_sha256"]={name:sha(ROOT/"scripts"/name) for name in
        ("three_threat_models.py","m1_latent_reconstruction.py","check_a6_lpips_assets.py","verify_science_assets.py","a6_clip_visual.py")}
    identities["comparator_prompt_manifest_sha256"]=sha(ROOT/"research/m1-gs-synthetic.json")
    if state_path.exists():
        record=prepare_resume(json.loads(state_path.read_text()),identities,output)
        record.setdefault("resume_commands",[]).append(sys.argv)
    else:
        if any(output.iterdir()):
            raise ValueError("Nonempty output directory has no run.json; refuse overwrite")
        record={**identities,"command":sys.argv,"config":CONFIG,"seeds":[c["seed"] for c in cases],
                "data_split":"synthetic","duration_seconds":0,"outcome":"started","rows":[],
                "environment":{"python":sys.version},"side_information":"Public payload, mask and known owner hypothesis; native detector uses VAE encoder weights; no inversion",
                "label":"Exploratory progressive-guidance carrier candidate; not faithful GROW or complete proposal"}
        record["planned_ids"]=[f"seed{c['seed']}-C0" for c in cases]+[f"seed{c['seed']}-a{a}-e{e}" for c in cases for a in CONFIG["alphas"] for e in CONFIG["etas"]]
    elapsed_before=record["duration_seconds"]
    record["outcome"]="started"
    write(state_path,record)
    def event(obj):
        with (output/"journal.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps({"seconds":time.monotonic()-started,**obj},allow_nan=False)+"\n")
    def checkpoint_record():
        record["duration_seconds"]=elapsed_before+time.monotonic()-started
        write(state_path,record)
    try:
        from three_threat_models import block_network,verify_assets,DDIM_CONFIG,load_lpips,lpips_score,validate_generated
        block_network()
        import torch
        import numpy as np
        from PIL import Image
        from diffusers import StableDiffusionPipeline,StableDiffusionImg2ImgPipeline,DDIMScheduler
        from m1_latent_reconstruction import quality
        receipt,package=verify_assets(ASSETS,ROOT/"research/a6-candidate-model-assets.json")
        record["asset_files"]=receipt["files"]
        record["environment"].update({p:importlib.metadata.version(p) for p in ("torch","diffusers","transformers","numpy","Pillow","lpips")})
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        torch.cuda.set_per_process_memory_fraction(CONFIG["gpu_budget_bytes"]/torch.cuda.get_device_properties(0).total_memory)
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False
        record["environment"]["gpu"]=torch.cuda.get_device_name(0)
        pipe=StableDiffusionPipeline.from_pretrained(ASSETS/"sd15-fp16",variant="fp16",use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).to("cuda")
        if pipe.safety_checker is None or pipe.feature_extractor is None:
            raise RuntimeError("Required safety components missing")
        pipe.set_progress_bar_config(disable=True)
        for component in (pipe.unet,pipe.vae,pipe.text_encoder,pipe.safety_checker):
            component.eval().requires_grad_(False)
        attack=StableDiffusionImg2ImgPipeline(**pipe.components)
        attack.set_progress_bar_config(disable=True)
        metric=load_lpips(ASSETS,package)
        from a6_clip_visual import load_visual_encoder
        from three_threat_models import clip_feature
        clip_model,clip_transform=load_visual_encoder(ASSETS/"clip/ViT-B-32.pt",device="cpu")
        record["vae_scaling_factor"]=float(pipe.vae.config.scaling_factor)
        def conditions(rgb):
            variants={"clean":rgb}
            with torch.inference_mode():
                tensor=pipe.image_processor.preprocess(Image.fromarray(rgb)).to(device="cuda",dtype=pipe.vae.dtype)
                reconstructed=pipe.vae.decode(pipe.vae.encode(tensor).latent_dist.mode(),return_dict=False)[0]
                reconstructed,flags=pipe.run_safety_checker(reconstructed,"cuda",pipe.vae.dtype)
                if flags is None or len(flags)!=1 or bool(flags[0]):
                    raise RuntimeError("VAE reconstruction safety incomplete/blocked")
                vae_rgb=pipe.image_processor.postprocess(reconstructed,output_type="pil",do_denormalize=[True])[0]
            variants["vae"]=np.asarray(vae_rgb).copy()
            for strength in CONFIG["attack_strengths"]:
                attack.scheduler=DDIMScheduler(**DDIM_CONFIG)
                with torch.inference_mode():
                    result=attack(prompt="",negative_prompt="",image=Image.fromarray(rgb),strength=strength,num_inference_steps=20,eta=0.0,guidance_scale=1.0,generator=torch.Generator(device="cuda").manual_seed(CONFIG["attack_seed"]),output_type="pil")
                variants[f"t3-{strength}"]=np.asarray(validate_generated(result)).copy()
            return variants
        def persist_scores(row,variants):
            source=variants["clean"]
            source_feature=clip_feature(clip_model,clip_transform,source)
            for condition,suspect in variants.items():
                artifact=output/f"{row['artifact_prefix']}-{condition}.png"
                Image.fromarray(suspect).save(artifact)
                row["artifacts"].append({"path":artifact.name,"sha256":sha(artifact)})
                row["conditions"][condition]=score(pipe,suspect)
                row["conditions"][condition]["quality_vs_same_arm_clean"]={**quality(source,suspect),
                    "lpips":lpips_score(metric,source,suspect),
                    "clip_cosine":float((source_feature*clip_feature(clip_model,clip_transform,suspect)).sum())}
                validate_condition(row['conditions'][condition])
                event({"phase":"condition","id":row["id"],"condition":condition,**row["conditions"][condition]})
                checkpoint_record()
        checkpoint_record()
        for case in cases:
            seed=case["seed"]
            c0entry=next((r for r in record["rows"] if r["id"]==f"seed{seed}-C0" and r["outcome"]=="completed"),None)
            if c0entry:
                c0path=artifact_path(output,c0entry["png_path"])
                if sha(c0path)!=c0entry["png_sha256"]:
                    raise ValueError("Resume C0 PNG hash mismatch")
                for artifact in c0entry["artifacts"]:
                    if sha(artifact_path(output,artifact["path"]))!=artifact["sha256"]:
                        raise ValueError("Resume C0 artifact hash mismatch")
                c0=np.asarray(Image.open(c0path).convert("RGB")).copy()
            else:
                row={"id":f"seed{seed}-C0","seed":seed,"outcome":"started","control":"C0","artifacts":[],"conditions":{}}
                attempt=1+sum(r["id"]==row["id"] for r in record["rows"])
                row["artifact_prefix"]=f"{row['id']}-attempt{attempt}"
                c0path=output/f"{row['artifact_prefix']}.png"
                row["png_path"]=c0path.name
                record["rows"].append(row); checkpoint_record()
                try:
                    image,meta=generate(pipe,case["prompt"],seed,0,0,event)
                    image.save(c0path)
                    c0=np.asarray(Image.open(c0path).convert("RGB")).copy()
                    row.update(png_sha256=sha(c0path),generation=meta)
                    persist_scores(row,conditions(c0))
                    row["outcome"]="completed"
                    checkpoint_record()
                except Exception as err:
                    row.update(outcome="failed",error=str(err)); checkpoint_record(); raise
            for alpha in CONFIG["alphas"]:
                for eta in CONFIG["etas"]:
                    ident=f"seed{seed}-a{alpha}-e{eta}"
                    previous=next((r for r in record["rows"] if r["id"]==ident and r["outcome"]=="completed"),None)
                    if previous:
                        for artifact in previous["artifacts"]:
                            if sha(artifact_path(output,artifact["path"]))!=artifact["sha256"]:
                                raise ValueError("Resume artifact hash mismatch")
                        continue
                    row={"id":ident,"seed":seed,"alpha":alpha,"eta":eta,"outcome":"started","control":"C1","artifacts":[],"conditions":{}}
                    attempt=1+sum(r["id"]==ident for r in record["rows"])
                    row["artifact_prefix"]=f"{ident}-attempt{attempt}"
                    record["rows"].append(row); checkpoint_record()
                    event({"phase":"variant_started","id":ident})
                    try:
                        image,meta=generate(pipe,case["prompt"],seed,alpha,eta,event)
                        png=output/f"{row['artifact_prefix']}-clean.png"; image.save(png)
                        rgb=np.asarray(Image.open(png).convert("RGB")).copy()
                        row["generation"]=meta
                        row["quality_to_matched_C0"]={**quality(c0,rgb),"lpips":lpips_score(metric,c0,rgb)}
                        validate_quality(row['quality_to_matched_C0'])
                        persist_scores(row,conditions(rgb))
                        row.update(outcome="completed",peak_allocated_bytes=torch.cuda.max_memory_allocated())
                        checkpoint_record(); torch.cuda.empty_cache()
                    except Exception as err:
                        row.update(outcome="failed",error=str(err),traceback=traceback.format_exc())
                        checkpoint_record(); event({"phase":"variant_failed","id":ident,"error":str(err)})
                        raise
        record["outcome"]="completed"
    except Exception as err:
        record.update(outcome="failed",error=str(err),traceback=traceback.format_exc())
    finally:
        completed={r["id"] for r in record["rows"] if r["outcome"]=="completed"}
        record["incomplete_planned_ids"]=[x for x in record["planned_ids"] if x not in completed]
        checkpoint_record()
    return 0 if record["outcome"]=="completed" else 1


def self_test():
    import torch
    basis=dct_matrix(64)
    torch.manual_seed(0)
    x=torch.randn(64,64)
    assert torch.allclose(idct2(dct2(x,basis),basis),x,atol=4e-5)
    assert torch.allclose(basis@basis.T,torch.eye(64),atol=1e-5)
    target,mask=target_and_mask(.3,basis)
    assert read_bits(idct2(target,basis),basis)["bit_accuracy"]==1
    x.requires_grad_(True)
    loss=(mask*(dct2(x,basis)-target).square()).sum()/mask.sum()
    loss.backward()
    assert torch.allclose(x.grad,analytic_gradient(x.detach(),target,mask,basis),atol=2e-7)
    print("DCT orthonormality, roundtrip, analytic gradient and payload tests passed")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path)
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        self_test(); return 0
    if args.manifest is None or args.output_dir is None:
        parser.error("--manifest and --output-dir are required for a run")
    return run(args.manifest.resolve(),args.output_dir.resolve())


if __name__=="__main__":
    raise SystemExit(main())
