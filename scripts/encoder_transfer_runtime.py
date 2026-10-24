"""Stage-2 adapters and execution for encoder_transfer_test.py.

No function here is called during stage-1 scientific validation. Model imports
are lazy; CPU unit tests use fake adapters. Upstream implementations are loaded
from separately pinned stage-2 assets, never vendored into this repository.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import gc
import types

from encoder_transfer_test import (ALPHA, BETA, ROOT, Journal, analyze, digest,
                                   endpoints, message, plan, presence, read, unit_id, write, validate_effective,
                                   read_methods, reduction_steps, apply_reduction, contract_status)


class Budget:
    def __init__(self, start_utc, hourly_usd, reserve_seconds=1800, max_hours=15, max_usd=15):
        start=datetime.fromisoformat(start_utc.replace("Z","+00:00"))
        if start.tzinfo is None or hourly_usd <= 0:
            raise ValueError("Actual timezone-aware instance start and positive hourly cost required")
        self.start=start.timestamp()
        self.hourly=hourly_usd
        # Frozen core: 15 h or USD 15. Amendment 1d (user, 2026-10-21): 35 h or USD 30 in total.
        self.max_hours,self.max_usd=max_hours,max_usd
        self.deadline=self.start+min(max_hours,max_usd/hourly_usd)*3600
        self.compute_deadline=self.deadline-reserve_seconds
        if self.start>time.time()+60:
            raise ValueError("Instance start cannot be in the future")

    def check(self, reserve=300):
        if time.time()+reserve >= self.compute_deadline:
            raise TimeoutError("Compute budget exhausted; reserve is for retrieval and instance stop")

    def record(self):
        elapsed=max(0,time.time()-self.start)
        return dict(instance_seconds=elapsed,projected_charged_usd=elapsed*self.hourly/3600,
                    hourly_usd=self.hourly,max_instance_hours=self.max_hours,max_usd=self.max_usd,instance_deadline_utc=datetime.fromtimestamp(self.deadline,timezone.utc).isoformat(),
                    compute_deadline_utc=datetime.fromtimestamp(self.compute_deadline,timezone.utc).isoformat())


class PhaseMemory:
    """Allocated CUDA peak per serial phase, including its resident models."""
    def __init__(self,cuda,path):
        self.cuda,self.path=cuda,Path(path)
        self.records=read(self.path) if self.path.exists() else []
        self.active=None
        self.peak=max([r["peak_allocated_bytes"] for r in self.records]+[0])

    def begin(self,label):
        self.finish()
        self.cuda.synchronize()
        self.cuda.reset_peak_memory_stats()
        self.active=dict(phase=label,started_utc=datetime.now(timezone.utc).isoformat(),
                         baseline_allocated_bytes=self.cuda.memory_allocated())

    def finish(self,incomplete=False):
        if self.active is None:
            return
        peak=self.cuda.max_memory_allocated()
        self.peak=max(self.peak,peak)
        self.records.append({**self.active,"peak_allocated_bytes":peak,"incomplete":incomplete})
        self.active=None
        write(self.path,self.records)


def require_finite(value,torch,label):
    if not bool(torch.isfinite(value).all()):
        raise ValueError(f"Nonfinite {label}; refuse RGB8 conversion")


def guard_vae(vae,torch,require_fp32=False):
    """Check native floating tensors before any PIL/uint8 conversion."""
    encode,decode=vae.encode,vae.decode
    def check_dtype(value):
        if require_fp32 and (not vae.config.force_upcast or value.dtype!=torch.float32 or
                             any(p.dtype!=torch.float32 for p in vae.parameters())):
            raise ValueError("Official SDXL VAE must encode/decode entirely in fp32 with force_upcast")
        require_finite(value,torch,"VAE input")
    def checked_encode(_self,value,*args,**kwargs):
        check_dtype(value)
        result=encode(value,*args,**kwargs)
        posterior=result[0] if isinstance(result,tuple) else result.latent_dist
        require_finite(posterior.parameters,torch,"VAE posterior")
        return result
    def checked_decode(_self,value,*args,**kwargs):
        check_dtype(value)
        result=decode(value,*args,**kwargs)
        require_finite(result[0] if isinstance(result,tuple) else result.sample,torch,"VAE decoded output")
        return result
    vae.encode=types.MethodType(checked_encode,vae)
    vae.decode=types.MethodType(checked_decode,vae)


def resize_rgb(rgb, size):
    import numpy as np
    from PIL import Image
    return np.asarray(Image.fromarray(rgb).resize((size,size),Image.Resampling.LANCZOS),dtype=np.uint8).copy()


def load_rgb(path):
    import numpy as np
    from PIL import Image
    with Image.open(path) as image:
        if image.mode!="RGB" or image.size!=(512,512):
            raise ValueError("Saved detector input must be RGB8 512 square")
        return np.asarray(image,dtype=np.uint8).copy()


def save_rgb(path,rgb):
    from PIL import Image
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(rgb).save(path)
    return dict(path=str(path),sha256=digest(path))


class Internal:
    def __init__(self,assets,config):
        import torch
        import three_threat_models as models
        import f5_latent_codec as f5
        import revised_watermark_v5 as v5
        from a6_clip_visual import load_visual_encoder
        from journal_vae_probe import Evaluator
        from f5_gate import semantic_feature
        from m1_latent_reconstruction import quality
        self.torch,self.models,self.f5,self.v5=torch,models,f5,v5
        self.reader=f5.Reader(assets/"a6",device="cuda")
        self.clip,self.transform=load_visual_encoder(assets/"a6/clip/ViT-B-32.pt",device="cpu")
        self.lpips=models.load_lpips(assets/"a6",Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
        self.profile=read(ROOT/config["profile_file"])
        self.config=config
        self.semantic_feature,self.quality=semantic_feature,quality
        # Reuse the historical detector method with explicit portable asset loading.
        self._detect=Evaluator.detect.__get__(self,type(self))

    def features(self,rgb,views):
        return self.semantic_feature(self.models,self.clip,self.transform,rgb,views)

    def metrics(self,a,b):
        return {**self.quality(a,b),"lpips":self.models.lpips_score(self.lpips,a,b)}

    def embed(self,rgb,method):
        import numpy as np
        if method=="f5-r2":
            params=self.config["f5"].copy()
            views=params.pop("semantic_views")
            marked,report=self.f5.embed_rgb(rgb,ALPHA,self.profile,self.features(rgb,views),self.reader,**params)
            # Historical F5 has no exported intended h; preserve that limitation.
            h=report["verification"]["instance"].get("decoded_code")
            payload=dict(q=report["semantic_code"],h=h,h_target_basis="native clean decoded h; intended h not exported")
        elif method=="v5-r3":
            marked,report=self.v5.embed_rgb(rgb.tolist(),ALPHA,profile=self.profile,
                                          semantic_features=self.features(rgb,1),strict=False)
            marked=np.asarray(marked,np.uint8)
            payload=dict(q=report["semantic_code"],h=report["perceptual_hash"],h_target_basis="native intended h")
        else:
            raise ValueError(method)
        return marked,payload,report

    def detect(self,rgb,method,payload,control):
        features=self.features(rgb,7 if method=="f5-r2" else 1)
        latent=self.reader.latent(rgb) if method=="f5-r2" else None
        calls={}
        for owner in ((ALPHA,BETA) if control=="C1" else (ALPHA,)):
            tick=time.monotonic()
            try:
                result=self._detect(rgb,"f5" if method=="f5-r2" else "v5",owner,features,latent)
                calls[owner]=dict(status="ok",raw=result,endpoints=endpoints(result,payload if owner==ALPHA and control=="C1" else None))
            except Exception:
                calls[owner]=dict(status="error",error=traceback.format_exc())
            calls[owner]["seconds"]=time.monotonic()-tick
        return calls


class Wam:
    def __init__(self,assets):
        repo=assets/"wam/source"
        sys.path.insert(0,str(repo))
        from journal_wam_probe import Adapter
        self.native=Adapter(repo,assets/"wam/wam_mit.pth","cuda")

    def embed(self,rgb,bits):
        # Official torchvision.save_image quantization: floor(255*x + .5).
        # Keep all model/transform logic of the retained native adapter.
        t=self.native.torch
        with t.inference_mode():
            y=self.native.model.embed(self.native.tensor(rgb),t.tensor([bits],dtype=t.float32,device="cuda"))["imgs_w"]
            require_finite(y,t,"WAM model output")
            y=self.native.unnormalize(y)[0]
            require_finite(y,t,"WAM denormalized output")
            y=y.mul(255).add(.5).clamp(0,255).permute(1,2,0)
            return y.to("cpu",t.uint8).numpy().copy()

    def detect(self,rgb,bits):
        result=self.native.detect(rgb,bits)
        return dict(status="ok",presence=presence(result["decoded_message"],bits),raw=result,
                    native=dict(rule="s_det > 0.07 at mask sigmoid > 0.5",
                                present=result["native_mask_fraction"]>.07,
                                calibration="paper COCO-model rule; MIT SA1B calibration transfer unverified"))


class Vine:
    def __init__(self,assets,encoding=False):
        import torch
        from torchvision import transforms
        sys.path.insert(0,str(assets/"vine/source"))
        self.torch,self.transforms=torch,transforms
        if encoding:
            from vine.src.vine_turbo import VINE_Turbo
            self.model=VINE_Turbo.from_pretrained(str(assets/"vine/encoder"),local_files_only=True)
        else:
            from vine.src.stega_encoder_decoder import CustomConvNeXt
            self.model=CustomConvNeXt.from_pretrained(str(assets/"vine/decoder"),local_files_only=True)
        self.model=self.model.eval().requires_grad_(False).to("cuda",dtype=torch.float32)

    def embed(self,rgb,bits):
        import numpy as np
        from PIL import Image
        t,tr=self.torch,self.transforms
        image=Image.fromarray(rgb)
        transform=tr.Compose([tr.Resize(256,interpolation=tr.InterpolationMode.BICUBIC),tr.ToTensor()])
        x=transform(image).unsqueeze(0).cuda()*2-1
        original=tr.ToTensor()(image).unsqueeze(0).cuda()*2-1
        with t.inference_mode():
            y=self.model(x,t.tensor([bits],dtype=t.float32,device="cuda"))
            require_finite(y,t,"VINE model output")
            residual=tr.Resize(image.size,interpolation=tr.InterpolationMode.BICUBIC)(y-x)
            out=(residual+original)*.5+.5
            require_finite(out,t,"VINE residual output")
            out=out.clamp(0,1)
        return np.asarray(tr.ToPILImage()(out[0].cpu()),dtype=np.uint8).copy()

    def detect(self,rgb,bits):
        import numpy as np
        from PIL import Image
        tr=self.transforms
        x=tr.Compose([tr.Resize(256,interpolation=tr.InterpolationMode.BICUBIC),tr.ToTensor()])(Image.fromarray(rgb)).unsqueeze(0).cuda()
        with self.torch.inference_mode():
            probabilities=self.model(x).cpu().numpy()[0]
        if probabilities.shape!=(100,) or not np.isfinite(probabilities).all():
            raise ValueError("Invalid native VINE decoder probabilities")
        decoded=np.round(probabilities).astype(int).tolist()
        return dict(status="ok",presence=presence(decoded,bits),raw=dict(probabilities=probabilities.tolist(),decoded_message=decoded),
                    native=dict(rule="No published universal fixed cutoff; descriptive empirical ROC only"))


def _rgb8(image):
    import numpy as np
    rgb=np.asarray(image.convert("RGB"),dtype=np.uint8).copy()
    if rgb.shape!=(512,512,3):
        raise ValueError("Native baseline output must stay RGB8 512 square")
    return rgb


class TrustMarkQ:
    """Amendment 1d / P1: official TrustMark Q, use_ECC=True, BCH_5 (61 payload bits), native decode path.

    The detector repeats the native decode() path for an unrotated image without the bbox
    detector (get_the_image_for_processing, 245 bilinear resize, decoder > 0, BCH decode),
    so the raw 100-bit decoder output can be reported next to the native result.
    """
    def __init__(self,assets):
        import torch
        sys.path.insert(0,str(assets/"trustmark/source/python"))
        from trustmark import TrustMark
        self.torch,self.TrustMark=torch,TrustMark
        self.tm=TrustMark(use_ECC=True,verbose=False,secret_len=100,device="cuda",model_type="Q",
                          encoding_type=TrustMark.Encoding.BCH_5,loadRemover=False,loadBBoxDetector=False)
        if self.tm.encoder is None or self.tm.decoder is None:
            raise RuntimeError("TrustMark Q weights did not load (MD5 check or download failed)")
        if self.tm.schemaCapacity()!=61:
            raise ValueError("TrustMark Q BCH_5 capacity must be 61 bits")

    def embed(self,rgb,bits):
        from PIL import Image
        if len(bits)!=61:
            raise ValueError("TrustMark Q payload must have 61 bits")
        out=self.tm.encode(Image.fromarray(rgb),"".join(str(int(b)) for b in bits),MODE="binary",WM_STRENGTH=1.0,WM_MERGE="bilinear")
        return _rgb8(out)

    def detect(self,rgb,bits):
        from PIL import Image
        from torchvision import transforms
        t,tm=self.torch,self.tm
        image=tm.get_the_image_for_processing(Image.fromarray(rgb))
        image=image.resize((tm.model_resolution_dec,tm.model_resolution_dec),Image.BILINEAR)
        x=transforms.ToTensor()(image).unsqueeze(0).to(tm.decoder.device)*2.0-1.0
        with t.no_grad():
            raw=(tm.decoder.decoder(x)>0).cpu().numpy()
        secret,detected,version=tm.ecc.decode_bitstream(raw,"binary")[0]
        decoded=[int(c) for c in secret] if detected and len(secret)==61 and set(secret)<={"0","1"} else None
        codeword=[int(round(float(v))) for v in tm.ecc.encode_binary(["".join(str(int(b)) for b in bits)])[0]]
        raw_bits=[int(v) for v in raw[0]]
        result=presence(decoded,bits)
        # Common presence needs the native detected flag (BCH success) as well as the payload rule.
        result["present"]=bool(detected) and bool(result["present"])
        return dict(status="ok",presence=result,
                    raw=dict(decoded_message=decoded,native_detected=bool(detected),schema_version=int(version),
                             raw_bits=raw_bits,raw_codeword_agreement=sum(a==b for a,b in zip(raw_bits,codeword))/len(codeword)),
                    native=dict(rule="BCH_5 decode success (native detected flag)",present=bool(detected),
                                exact_payload=decoded==[int(b) for b in bits]))


class PixelSeal:
    """Amendment 1d / P9: official Pixel Seal card from VideoSeal, native 256 bits, image mode.

    Mirrors videoseal.utils.cfg.setup_model without the training-data imports; the
    augmenter is never used at inference, so a no-op module stands in for it.
    """
    def __init__(self,assets):
        import torch
        import omegaconf
        repo=assets/"videoseal/source"
        sys.path.insert(0,str(repo))
        from videoseal.models import Videoseal,build_embedder,build_extractor
        from videoseal.modules.jnd import JND
        self.torch=torch
        card=omegaconf.OmegaConf.load(repo/"videoseal/cards/pixelseal.yaml")
        args=card.args
        if int(args.nbits)!=256 or int(args.img_size_proc)!=256:
            raise ValueError("Pixel Seal card must be the native 256-bit, 256-pixel release")
        embedder=build_embedder(card.embedder.model,card.embedder.params,args.nbits,args.hidden_size_multiplier)
        extractor=build_extractor(card.extractor.model,card.extractor.params,args.img_size_proc,args.nbits)
        attenuation_cfg=omegaconf.OmegaConf.load(repo/args.attenuation_config)
        attenuation=JND(**attenuation_cfg[args.attenuation])
        model=Videoseal(embedder,extractor,torch.nn.Identity(),attenuation=attenuation,scaling_w=args.scaling_w,
                        scaling_i=args.scaling_i,img_size=args.img_size_proc,blending_method=args.blending_method,
                        chunk_size=args.videowam_chunk_size,step_size=args.videowam_step_size)
        checkpoint=torch.load(assets/"videoseal/pixelseal-checkpoint.pth",map_location="cpu",weights_only=True)
        missing=model.load_state_dict(checkpoint["model"],strict=False)
        if missing.missing_keys:
            raise ValueError(f"Pixel Seal checkpoint is missing model keys: {missing.missing_keys[:5]}")
        self.load_report=dict(unexpected_keys=list(missing.unexpected_keys))
        self.model=model.eval().to("cuda")

    def tensor(self,rgb):
        return self.torch.from_numpy(rgb).permute(2,0,1).unsqueeze(0).float().div(255.).to("cuda")

    def embed(self,rgb,bits):
        t=self.torch
        if len(bits)!=256:
            raise ValueError("Pixel Seal payload must have 256 bits")
        with t.no_grad():
            out=self.model.embed(self.tensor(rgb),msgs=t.tensor([bits],dtype=t.float32,device="cuda"),is_video=False)["imgs_w"]
            require_finite(out,t,"Pixel Seal output")
            # Native image saving: clamp to [0,1], then round half up to RGB8.
            y=out[0].clamp(0,1).mul(255).add(.5).floor().clamp(0,255).permute(1,2,0)
        rgb_out=y.to("cpu",t.uint8).numpy().copy()
        if rgb_out.shape!=(512,512,3):
            raise ValueError("Pixel Seal output must stay RGB8 512 square")
        return rgb_out

    def detect(self,rgb,bits):
        t=self.torch
        with t.no_grad():
            preds=self.model.detect(self.tensor(rgb),is_video=False)["preds"]
        preds=preds.float()
        if preds.dim()>2:
            preds=preds.mean(dim=tuple(range(2,preds.dim())))
        logits=preds[0,1:].cpu()
        if logits.numel()!=256 or not bool(t.isfinite(logits).all()):
            raise ValueError("Invalid native Pixel Seal message logits")
        decoded=[int(v) for v in (logits>0).tolist()]
        return dict(status="ok",presence=presence(decoded,bits),
                    raw=dict(decoded_message=decoded,detection_logit=float(preds[0,0]),
                             mean_abs_logit=float(logits.abs().mean())),
                    native=dict(rule="No universal fixed native presence cutoff; bit agreement only"))


class MoVQ:
    """Amendment 1d / P4 AE-only: Kandinsky 3 MoVQ encode/decode, as the img2img pipeline uses it.

    Kandinsky3Img2ImgPipeline encodes with movq.encode(image).latents and decodes with
    force_not_quantize=True; this diagnostic applies exactly that round trip, no diffusion.
    """
    def __init__(self,assets):
        import torch
        from diffusers import VQModel
        self.torch=torch
        self.movq=VQModel.from_pretrained(assets/"kandinsky3/movq",variant="fp16",torch_dtype=torch.float16,
                                          use_safetensors=True,local_files_only=True)
        self.movq=self.movq.to("cuda",dtype=torch.float32).eval().requires_grad_(False)

    def roundtrip(self,rgb):
        t=self.torch
        x=t.from_numpy(rgb).permute(2,0,1).unsqueeze(0).float().div(127.5).sub(1.).to("cuda")
        require_finite(x,t,"MoVQ input")
        with t.no_grad():
            z=self.movq.encode(x).latents
            require_finite(z,t,"MoVQ latent")
            y=self.movq.decode(z,force_not_quantize=True).sample
            require_finite(y,t,"MoVQ decoded output")
        y=y[0].clamp(-1,1).add(1).mul(127.5).round().clamp(0,255).permute(1,2,0)
        return y.to("cpu",t.uint8).numpy().copy()


def p5_perturbations(spec):
    """Amendment 2b / P5: four fixed public Gaussian arrays (used with their negatives), shared by every source and arm."""
    import hashlib
    import numpy as np
    rng=np.random.default_rng(spec["noise_seed"])
    arrays=rng.standard_normal((spec["pairs"],*spec["shape"]),dtype=np.float32)*np.float32(spec["sigma"])
    if hashlib.sha256(arrays.tobytes()).hexdigest()!=spec["noise_sha256"]:
        raise ValueError("P5 perturbation arrays differ from the contract")
    return arrays


class Regenerator:
    def __init__(self,assets,spec):
        import torch
        self.torch,self.spec=torch,spec
        family=spec["family"]
        if family=="kandinsky3-movq":
            self.movq=MoVQ(assets)
            self.pipe=None
            return
        if family=="kandinsky3":
            # Amendment 2b / P4: full Kandinsky 3 img2img at revision bf79e6c, native scheduler, fp16 variant.
            from diffusers import Kandinsky3Img2ImgPipeline
            pipe=Kandinsky3Img2ImgPipeline.from_pretrained(assets/"kandinsky3",variant="fp16",torch_dtype=torch.float16,
                                                           use_safetensors=True,local_files_only=True)
            # The contract fixes the empty prompt without guidance, so the prompt embedding is computed
            # once with the pinned text encoder, as the pipeline computes it on every call, and the
            # 21.7 GB encoder then leaves the GPU before the U-Net and MoVQ load.
            pipe.text_encoder.to("cuda")
            with torch.no_grad():
                embeds,_,mask,_=pipe.encode_prompt(spec["prompt"],do_classifier_free_guidance=False,device="cuda",_cut_context=True)
            require_finite(embeds,torch,"Kandinsky 3 prompt embedding")
            pipe.text_encoder.to("cpu")
            pipe.text_encoder=None
            release()
            pipe.unet.to("cuda")
            pipe.movq.to("cuda")
            pipe.set_progress_bar_config(disable=True)
            self.pipe,self.prompt=pipe,dict(prompt_embeds=embeds,attention_mask=mask)
            return
        if family=="sd15":
            from three_threat_models import load_regenerator
            self.pipe=load_regenerator(assets/"a6")
        elif family=="sdxl":
            from diffusers import StableDiffusionXLImg2ImgPipeline,DDIMScheduler
            self.pipe=StableDiffusionXLImg2ImgPipeline.from_pretrained(assets/"sdxl",variant="fp16",
                torch_dtype=torch.float16,use_safetensors=True,local_files_only=True,add_watermarker=False)
            self.pipe.scheduler=DDIMScheduler.from_config(self.pipe.scheduler.config,**spec["scheduler_overrides"])
            # Native upcast_vae recasts parts of the decoder to fp16. The brief
            # requires the ENTIRE official VAE in fp32 during decode.
            def full_upcast(pipe):
                pipe.vae.to(dtype=torch.float32)
            self.pipe.upcast_vae=types.MethodType(full_upcast,self.pipe)
            self.pipe.to("cuda")
        else:
            raise ValueError(f"Unimplemented frozen regenerator {family}")
        guard_vae(self.pipe.vae,torch,require_fp32=family=="sdxl")
        self.pipe.set_progress_bar_config(disable=True)

    def roundtrip(self,rgb):
        import numpy as np
        from PIL import Image
        t=self.torch
        if self.spec["family"]=="kandinsky3-movq":
            return self.movq.roundtrip(rgb)
        if self.spec["family"]=="sdxl":
            vae=self.pipe.vae
            vae.to(dtype=t.float32)
            x=self.pipe.image_processor.preprocess(Image.fromarray(rgb)).to("cuda",dtype=t.float32)
            with t.inference_mode():
                z=vae.encode(x).latent_dist.mode()
                y=vae.decode(z,return_dict=False)[0]
                out=self.pipe.image_processor.postprocess(y,output_type="pil")[0]
            vae.to(dtype=t.float16)
        else:
            raise ValueError("No unregistered diagnostic")
        return np.asarray(out,dtype=np.uint8).copy()

    def posterior_mode(self,rgb,perturbations=None):
        """Amendment 2b / P5: SDXL VAE posterior mode in full fp32, scaled for the img2img path.

        With perturbations, the mean of the modes of clip(x ± g_k, 0, 1) over the antithetic pairs
        (encoder-aware smoothing); without, the mode of x itself (the matched control).
        """
        from PIL import Image
        t=self.torch
        vae=self.pipe.vae
        vae.to(dtype=t.float32)
        x=self.pipe.image_processor.preprocess(Image.fromarray(rgb)).to("cuda",dtype=t.float32)
        require_finite(x,t,"P5 VAE input")
        with t.inference_mode():
            if perturbations is None:
                z=vae.encode(x).latent_dist.mode()
            else:
                x01=(x+1)/2
                total=None
                for g in perturbations:
                    g=t.from_numpy(g).to("cuda").unsqueeze(0)
                    for sign in (1.,-1.):
                        mode=vae.encode((x01+sign*g).clamp(0,1)*2-1).latent_dist.mode()
                        total=mode if total is None else total+mode
                z=total/(2*len(perturbations))
        require_finite(z,t,"P5 posterior mode")
        vae.to(dtype=t.float16)
        return z*vae.config.scaling_factor

    def __call__(self,rgb,strength,seed,latent=None):
        import numpy as np
        from PIL import Image
        t=self.torch
        generator=t.Generator(device="cuda").manual_seed(seed)
        if self.spec["family"]=="kandinsky3":
            with t.inference_mode():
                result=self.pipe(image=Image.fromarray(rgb),strength=strength,num_inference_steps=self.spec["steps"],
                                 guidance_scale=self.spec["guidance_scale"],generator=generator,output_type="np",
                                 return_dict=True,**self.prompt)
            image=result.images[0]
            if not np.isfinite(image).all():
                raise FloatingPointError("Kandinsky 3 decoded output contains non-finite values")
            # The quantization diffusers applies for PIL output (numpy_to_pil).
            return (image*255).round().astype("uint8")
        # A given latent (P5) replaces the pipeline's own VAE encoding; the pipeline still adds the
        # seed's noise at the strength's timestep and denoises.
        kwargs=dict(prompt=self.spec["prompt"],image=latent if latent is not None else Image.fromarray(rgb),strength=strength,
                    num_inference_steps=self.spec["steps"],guidance_scale=self.spec["guidance_scale"],
                    generator=generator,output_type="pil",return_dict=True)
        if self.spec["family"] in ("sd15","sdxl"):
            kwargs.update(negative_prompt="",eta=0.)
        if self.spec["family"]=="sdxl":
            kwargs.update(prompt_2="",original_size=(1024,1024),target_size=(1024,1024),crops_coords_top_left=(0,0),clip_skip=None)
        with t.inference_mode():
            result=self.pipe(**kwargs)
        if self.spec["family"]=="sd15":
            from three_threat_models import validate_generated
            image=validate_generated(result)
        else:
            image=result.images[0]
        return np.asarray(image,dtype=np.uint8).copy()


def release():
    import torch
    gc.collect()
    torch.cuda.empty_cache()


def seed_everything(seed):
    import random
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def image_path(out,unit):
    return out/"images"/(unit["id"].replace(":","_")+".png")


def expected_methods(unit,config):
    return read_methods(config,unit)


def clean_id(unit):
    return unit_id(unit["source_id"],"clean",None,None,unit["arm"])


def failed_row(unit,exc):
    text=str(exc)
    status="safety_blocked" if "safety" in text.lower() or "nsfw" in text.lower() else "error"
    return {**unit,"status":status,"error":traceback.format_exc()}


def produce_images(config,sources,out,assets,journal,budget,smoke,memory=None):
    """One model resident at a time; generated rows survive readout interruption."""
    units=list(plan(config,sources,smoke))
    clean=[u for u in units if u["channel"]=="clean"]
    adapter=None
    for arm in ["unmarked",*config["arms"]]:
        pending=[u for u in clean if u["arm"]==arm and not journal.done(u["id"]) and not journal.latest.get(u["id"],{}).get("output")]
        if not pending:
            continue
        budget.check()
        if memory:
            memory.begin("embedding/"+arm)
        if arm in ("f5-r2","v5-r3"):
            adapter=Internal(assets,config)
        elif arm=="wam":
            adapter=Wam(assets)
        elif arm=="vine-r":
            adapter=Vine(assets,encoding=True)
        elif arm=="trustmark-q":
            adapter=TrustMarkQ(assets)
        elif arm=="pixelseal":
            adapter=PixelSeal(assets)
        for unit in pending:
            budget.check()
            start=time.monotonic()
            try:
                seed_everything(config["implementation_seed"])
                rgb=load_rgb(assets/"sources"/f'{unit["source_id"]}.png')
                payload,report=None,None
                if arm in ("f5-r2","v5-r3"):
                    marked,payload,report=adapter.embed(rgb,arm)
                elif arm=="unmarked":
                    marked=rgb
                else:
                    bits=message(unit["source_id"],config["payload_bits"][arm],config["message_seed"])
                    marked=adapter.embed(rgb,bits)
                    payload=dict(bits=bits)
                row={**unit,"status":"generated","output":save_rgb(image_path(out,unit),marked),"payload":payload,"embedding_report":report}
            except Exception as exc:
                row=failed_row(unit,exc)
            row["generation_seconds"]=time.monotonic()-start
            journal.append(row)
        adapter=None
        release()
        if memory:
            memory.finish()
    specs={s["id"]:s for s in config["channels"]}
    generator=None
    loaded_family=None
    for spec in config["channels"]:
        pending=[u for u in units if u["channel"]==spec["id"] and not journal.done(u["id"]) and not journal.latest.get(u["id"],{}).get("output")]
        if not pending:
            continue
        budget.check()
        if memory:
            memory.begin("regeneration/"+spec["id"])
        family=spec.get("family")
        if family and family!=loaded_family:
            generator=None
            release()
            generator=Regenerator(assets,specs[spec.get("base_channel",spec["id"])] )
            loaded_family=family
        # P5: one smoothed (or control) latent per marked input, reused by its three seeds.
        perturbations=p5_perturbations(config["p5"]) if spec["kind"]=="smoothing" else None
        latents={}
        for unit in pending:
            budget.check()
            start=time.monotonic()
            dependency=journal.latest.get(clean_id(unit),{})
            if spec["kind"]=="rinse":
                dependency=journal.latest.get(unit_id(unit["source_id"],"R1",.1,unit["seed"],unit["arm"]),{})
            if not dependency.get("output"):
                journal.append({**unit,"status":"input_missing","dependency":dependency.get("id"),"generation_seconds":0.})
                continue
            try:
                seed_everything(config["implementation_seed"])
                rgb=load_rgb(dependency["output"]["path"])
                if spec["kind"]=="resize":
                    for _ in range(spec["passes"]):
                        rgb=resize_rgb(resize_rgb(rgb,1024),512)
                elif spec["kind"]=="vae":
                    rgb=resize_rgb(generator.roundtrip(resize_rgb(rgb,1024)),512)
                elif spec["kind"] in ("smoothing","mode"):
                    key=dependency["output"]["sha256"]
                    if key not in latents:
                        latents[key]=generator.posterior_mode(resize_rgb(rgb,1024),perturbations)
                    rgb=resize_rgb(generator(None,unit["strength"],unit["seed"],latent=latents[key]),512)
                else:
                    size=spec["resolution"]
                    rgb=resize_rgb(rgb,size) if size!=512 else rgb
                    seed=unit["seed"]+(spec.get("seed_offset",0))
                    strength=spec.get("pass_strength",unit["strength"])
                    rgb=generator(rgb,strength,seed)
                    rgb=resize_rgb(rgb,512) if size!=512 else rgb
                row={**unit,"status":"generated","output":save_rgb(image_path(out,unit),rgb),
                     "payload":journal.latest[clean_id(unit)].get("payload"),"input_sha256":dependency["output"]["sha256"]}
            except Exception as exc:
                row=failed_row(unit,exc)
            row["generation_seconds"]=time.monotonic()-start
            journal.append(row)
        if memory:
            memory.finish()
    generator=None
    release()


def read_images(config,sources,out,assets,journal,budget,smoke,memory=None):
    units=list(plan(config,sources,smoke))
    for method in config["arms"]:
        pending=[u for u in units if method in expected_methods(u,config) and
                 journal.latest.get(u["id"],{}).get("output") and method not in journal.latest[u["id"]].get("detections",{})]
        if not pending:
            continue
        budget.check()
        if memory:
            memory.begin("extraction/"+method)
        adapter=(Internal(assets,config) if method in ("f5-r2","v5-r3") else Wam(assets) if method=="wam" else
                 TrustMarkQ(assets) if method=="trustmark-q" else PixelSeal(assets) if method=="pixelseal" else Vine(assets))
        for unit in pending:
            budget.check()
            row=journal.latest[unit["id"]].copy()
            row["detections"]=row.get("detections",{}).copy()
            tick=time.monotonic()
            try:
                rgb=load_rgb(row["output"]["path"])
                if method in ("f5-r2","v5-r3"):
                    calls=adapter.detect(rgb,method,row.get("payload"),unit["control"])
                else:
                    bits=message(unit["source_id"],config["payload_bits"][method],config["message_seed"])
                    calls={ALPHA:adapter.detect(rgb,bits)}
                    wrong=message(unit["source_id"],config["payload_bits"][method],config["wrong_message_seed"])
                    calls[ALPHA]["wrong_message_presence"]=presence(calls[ALPHA]["raw"].get("decoded_message"),wrong)
                row["detections"][method]=calls
            except Exception:
                owners=[ALPHA,BETA] if method in ("f5-r2","v5-r3") and unit["control"]=="C1" else [ALPHA]
                row["detections"][method]={owner:dict(status="error",error=traceback.format_exc()) for owner in owners}
            row.setdefault("detection_seconds",{})[method]=time.monotonic()-tick
            journal.append(row)
        adapter=None
        release()
        if memory:
            memory.finish()
    # Distortion uses saved RGB8 inputs and outputs and CPU LPIPS, independently
    # of detector success. A missing metric never turns a positive into a success.
    from m1_latent_reconstruction import quality
    from m1b_e3_s1_analysis import strict_quality
    import three_threat_models as models
    lpips=models.load_lpips(assets/"a6",Path(importlib.metadata.distribution("lpips").locate_file("lpips")))
    for unit in units:
        row=journal.latest.get(unit["id"],{}).copy()
        if not row.get("output") or row.get("status")=="ok":
            continue
        budget.check()
        tick=time.monotonic()
        try:
            rgb=load_rgb(row["output"]["path"])
            reference=assets/"sources"/f'{unit["source_id"]}.png' if unit["channel"]=="clean" else Path(journal.latest[clean_id(unit)]["output"]["path"])
            original=load_rgb(reference)
            metrics={**quality(original,rgb),"lpips":models.lpips_score(lpips,original,rgb)}
            row["distortion"]=dict(status="ok",reference_sha256=digest(reference),**metrics)
            source=load_rgb(assets/"sources"/f'{unit["source_id"]}.png')
            row["total_distortion"]=dict(status="ok",**quality(source,rgb),lpips=models.lpips_score(lpips,source,rgb))
            if unit["channel"]=="R1-rinse":
                prior=Path(journal.latest[unit_id(unit["source_id"],"R1",.1,unit["seed"],unit["arm"])]["output"]["path"])
                first=load_rgb(prior)
                row["incremental_distortion"]=dict(status="ok",reference_sha256=digest(prior),
                    **quality(first,rgb),lpips=models.lpips_score(lpips,first,rgb))
            if unit["channel"]=="clean":
                row["strict_quality"]=strict_quality(metrics)
        except Exception:
            row["distortion"]=dict(status="error",error=traceback.format_exc())
        row["metrics_seconds"]=time.monotonic()-tick
        row["status"]="ok"
        journal.append(row)


def projected_seconds(config,sources,smoke_rows):
    """Timing only: use the slower smoke source in each arm/cell, plus 30%.

    A block by R0's frozen SD1.5 safety checker is a terminal content outcome (protocol: blocked
    inventories are retained), not an implementation failure; that cell is timed from the other
    smoke source, and a cell with no timed unit is still refused.
    Amendment 2b: cells inherited from stage 2a are already complete and are neither timed nor charged.
    """
    inherited={tuple(cell) for cell in config.get("inherited_cells",[])}
    needed=Counter((u["channel"],u["strength"],u["arm"]) for u in plan(config,sources) if (u["channel"],u["strength"],u["arm"]) not in inherited)
    costs={}
    for unit in plan(config,sources,True):
        key=(unit["channel"],unit["strength"],unit["arm"])
        if key not in needed:
            continue
        row=smoke_rows.get(unit["id"])
        if row is None:
            raise ValueError("Smoke is missing a planned unit")
        if row.get("status")=="safety_blocked" and row["channel"]=="R0":
            continue
        methods=read_methods(config,unit)
        required=[(m,o) for m in methods for o in ([ALPHA,BETA] if m in ("f5-r2","v5-r3") and unit["control"]=="C1" else [ALPHA])]
        if row.get("status")!="ok" or row.get("distortion",{}).get("status")!="ok" or any(row.get("detections",{}).get(m,{}).get(o,{}).get("status")!="ok" for m,o in required):
            raise ValueError("Smoke has failed units/calls; fix implementation before full run")
        elapsed=row.get("generation_seconds",0)+row.get("metrics_seconds",0)+sum(row.get("detection_seconds",{}).values())
        costs[key]=max(costs.get(key,0),elapsed)
    untimed=sorted(set(needed)-set(costs),key=str)
    if untimed:
        raise ValueError(f"Smoke has no timed unit for {untimed}")
    return 1.3*sum(count*costs[key] for key,count in needed.items())+900


def budget_contract(config,sources,smoke_rows,available):
    import copy
    effective=copy.deepcopy(config)
    dropped=[]
    for stage in (None,*reduction_steps(config)):
        if stage:
            apply_reduction(effective,stage)
            dropped.append(stage)
        projection=projected_seconds(effective,sources,smoke_rows)
        if projection<=available:
            return effective,dict(projected_seconds=projection,available_seconds=available,dropped=dropped,
                                  rule="maximum timing per smoke source/cell +30% +900s model-loading reserve; no scores read")
    raise TimeoutError("Protected schedule cannot fit the budget after the permitted reductions")


def execute(args,config,sources):
    contract_status(config)
    limits=config.get("budget",{})
    budget=Budget(args.instance_start_utc,args.hourly_usd,limits.get("retrieval_stop_reserve_seconds",1800),
                  limits.get("max_instance_hours",15),limits.get("max_usd",15))
    budget.check()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    if args.phase=="prepare":
        from encoder_transfer_assets import prepare
        prepare(args.assets_root,config,sources,budget)
        return
    os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
    import torch
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["TRANSFORMERS_OFFLINE"]="1"
    from encoder_transfer_assets import verify_ready
    verify_ready(args.assets_root,config,sources)
    if not torch.cuda.is_available():
        raise RuntimeError("Stage2 requires the rented CUDA GPU")
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
    torch.cuda.reset_peak_memory_stats()
    versions={name:importlib.metadata.version(name) for name in config["packages"]}
    if versions!=config["packages"]:
        raise ValueError(f"Runtime versions differ from frozen pins: {versions}")
    current_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    manifest_sha=digest(args.manifest)
    smoke=args.phase=="smoke"
    record_path=args.output_dir/"run.json"
    if record_path.exists():
        record=read(record_path)
        if record["manifest_sha256"]!=manifest_sha or record["phase"]!=args.phase:
            raise ValueError("Cannot resume a different contract or phase")
        previous=record.get("implementation_commits",[record["commit"]])[-1]
        if previous!=current_commit:
            if not args.bugfix_note:
                raise ValueError("New implementation commit requires --bugfix-note; design changes remain forbidden")
            record.setdefault("implementation_commits",[record["commit"]]).append(current_commit)
            record.setdefault("bug_fixes",[]).append(dict(commit=current_commit,note=args.bugfix_note,utc=datetime.now(timezone.utc).isoformat()))
    else:
        record=dict(commit=current_commit,
                    command=sys.argv,phase=args.phase,data_split="development",manifest_sha256=manifest_sha,
                    config=config,seeds=config["seeds"],created_utc=datetime.now(timezone.utc).isoformat(),
                    environment=versions,
                    gpu=torch.cuda.get_device_name(),outcome="running",duration_seconds=0)
    effective_path=args.output_dir/"effective-config.json"
    if not smoke:
        if effective_path.exists():
            effective=read(effective_path)
            validate_effective(config,effective)
        else:
            smoke_dir=args.smoke_dir
            if not smoke_dir:
                raise ValueError("Full run requires --smoke-dir from the two reserved smoke sources")
            smoke_record=read(smoke_dir/"run.json")
            if smoke_record["manifest_sha256"]!=manifest_sha or smoke_record["outcome"]!="smoke_completed":
                raise ValueError("Matching completed smoke required")
            smoke_rows=Journal(smoke_dir/"rows.jsonl").latest
            effective,projection=budget_contract(config,sources,smoke_rows,budget.compute_deadline-time.time())
            record["projection"]=projection
            write(effective_path,effective)
        config=effective
    journal=Journal(args.output_dir/"rows.jsonl")
    # Amendment 2b: in the full run, stage-2a cells are inherited, never rerun; their verified rows
    # must be seeded first (encoder_transfer_seed_2b.py). The smoke reruns its two reserved sources.
    inherited={tuple(cell) for cell in config.get("inherited_cells",[])} if not smoke else set()
    unseeded=[u["id"] for u in plan(config,sources) if (u["channel"],u["strength"],u["arm"]) in inherited and not journal.done(u["id"])]
    if unseeded:
        raise ValueError(f"Seed the stage-2a rows before stage 2b: {len(unseeded)} inherited units missing, e.g. {unseeded[0]}")
    memory=PhaseMemory(torch.cuda,args.output_dir/"memory-phases.json")
    start=time.monotonic()
    write(record_path,record)
    try:
        produce_images(config,sources,args.output_dir,args.assets_root,journal,budget,smoke,memory)
        read_images(config,sources,args.output_dir,args.assets_root,journal,budget,smoke,memory)
        if smoke:
            projection=projected_seconds(config,sources,journal.latest)
            write(args.output_dir/"smoke-timing.json",dict(projected_full_seconds=projection,peak_cuda_bytes=memory.peak,budget=budget.record()))
            record["outcome"]="smoke_completed"
        else:
            metrics=analyze(config,sources,journal.latest)
            write(args.output_dir/"metrics.json",metrics)
            final=config.get("amendment",{}).get("stage2a_decision")
            if final and (metrics["decision"]["label"],metrics["decision"]["route"])!=(final["label"],final["route"]):
                raise ValueError("The stage-2b analysis does not reproduce the final stage-2a label")
            record["outcome"]="completed"
            record["decision"]=metrics["decision"]
    except BaseException:
        record["outcome"]="interrupted_or_failed"
        record["error"]=traceback.format_exc()
        raise
    finally:
        memory.finish(incomplete=record["outcome"]=="interrupted_or_failed")
        record["duration_seconds"]+=time.monotonic()-start
        record["budget"]=budget.record()
        record["peak_cuda_bytes"]=max(record.get("peak_cuda_bytes",0),memory.peak)
        record["memory_phases_file"]="memory-phases.json"
        write(record_path,record)
