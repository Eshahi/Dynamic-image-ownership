"""Shared pinned local candidate model context; no source resolver or authorization.

Import is standard-library only. Construction is explicit real-model CUDA work;
callers must authorize execution and provide their own bounded lifecycle.
"""
from __future__ import annotations
import gc, hashlib, importlib.metadata, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ASSETS=MAIN/'.thesis-build/assets/a6'
PROFILE='configs/revised-watermark-v5.example.json'
VERSION='m1-candidate-model-context-v1'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()


def validate_inputs(config,core_sha256):
    if not isinstance(config,dict) or config.get('profile')!=PROFILE:raise ValueError('Frozen v5 public profile required')
    if type(core_sha256) is not str or re.fullmatch('[0-9a-f]{64}',core_sha256) is None:raise ValueError('Exact scientific core identity')
    for name in ('gpu_budget_bytes','gpu_reserve_bytes','ram_budget_bytes'):
        if type(config.get(name)) is not int or config[name]<=0:raise ValueError('Positive exact resource bytes required')
    if config['gpu_budget_bytes']>10*1024**3 or config['ram_budget_bytes']>16*1024**3:raise ValueError('Reviewed local resource ceiling')


class CandidateModelContext:
    """Supply pinned models and numerical hooks; never accept source/model paths.

    ``publish`` retains partial provenance before later load/inference failures.
    ``event`` and ``check`` must not consume scientific execution RNG.
    """
    def __init__(self,config,scientific_core_sha256,*,publish=None,event=None,check=None):
        validate_inputs(config,scientific_core_sha256)
        self.config=dict(config);self.provenance={'model_context_version':VERSION};self.peaks={'peak_rss_bytes':0,'peak_allocated_bytes':0}
        self.publish=publish or (lambda values:None);self.event=event or (lambda **value:None);self.check=check or (lambda:None)
        import numpy as np
        import torch
        import m1_terminal_continuous as component
        import m1_terminal_repeatability as repeatability
        import m1_candidate_adapter as candidate
        import revised_watermark_v5 as codec
        from three_threat_models import block_network,verify_assets,load_lpips,clip_feature
        from a6_clip_visual import load_visual_encoder
        block_network();self._update(deterministic_execution=repeatability.configure())
        if not torch.cuda.is_available():raise RuntimeError('CUDA required; no model mock fallback')
        self._update(environment={'python':sys.version,**{p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','Pillow','diffusers','lpips')}},
          device_identity=dict(name=torch.cuda.get_device_name(0),capability=list(torch.cuda.get_device_capability(0)),cuda_version=torch.version.cuda,cudnn_version=torch.backends.cudnn.version()),
          driver_inventory=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,driver_version,pci.bus_id','--format=csv,noheader'],text=True).strip(),
          execution_runtime=dict(threads=torch.get_num_threads(),fill_uninitialized_memory=bool(torch.utils.deterministic.fill_uninitialized_memory),embedding_device='cuda',embedding_dtype='float32',public_reader_dtype='float16',clip_device='cpu',lpips_device='cpu'))
        free,total=torch.cuda.mem_get_info(0)
        budget=component.gpu_allocation_budget(config['gpu_budget_bytes'],int(free),int(total),config['gpu_reserve_bytes'])
        torch.cuda.set_per_process_memory_fraction(budget['allocator_fraction']);self._update(gpu_allocation_budget=budget)
        assets,package=verify_assets(ASSETS,ROOT/'research/a6-candidate-model-assets.json');self._update(assets=assets)
        self.package=package
        self.resource_snapshot('before_model_load')
        from diffusers import AutoencoderKL
        from diffusers.image_processor import VaeImageProcessor
        from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
        from transformers import CLIPImageProcessor
        def load_vae(dtype):
            vae=AutoencoderKL.from_pretrained(ASSETS/'sd15-fp16/vae',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=dtype).eval().requires_grad_(False).to('cuda')
            if float(vae.config.scaling_factor)!=.18215:raise ValueError('Pinned scaling factor differs')
            return vae
        self.vae_fp32=load_vae(torch.float32);self.vae_public=load_vae(torch.float16)
        self.processor=VaeImageProcessor(vae_scale_factor=8)
        self.safety=StableDiffusionSafetyChecker.from_pretrained(ASSETS/'sd15-fp16/safety_checker',variant='fp16',use_safetensors=True,local_files_only=True,torch_dtype=torch.float16).eval().requires_grad_(False).to('cuda')
        self.safety_processor=CLIPImageProcessor.from_pretrained(ASSETS/'sd15-fp16/feature_extractor',local_files_only=True)
        self.clip,self.transform=load_visual_encoder(ASSETS/'clip/ViT-B-32.pt',device='cpu');self.clip.eval().requires_grad_(False);self.metric=load_lpips(ASSETS,package)
        if any(p.device.type!='cpu' for model in (self.clip,self.metric) for p in model.parameters()):raise ValueError('CPU feature/quality evaluator required')
        self.profile=codec.validate_profile(codec.load_profile(ROOT/PROFILE))
        model_identity=dict(vae_fp32=sha(ASSETS/'sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors'),vae_public=sha(ASSETS/'sd15-fp16/vae/diffusion_pytorch_model.fp16.safetensors'),clip=sha(ASSETS/'clip/ViT-B-32.pt'),profile=sha(ROOT/PROFILE),scientific_core_sha256=scientific_core_sha256)
        self.adapter=candidate.CandidateAdapter(self.vae_fp32,self.vae_public,self.processor,self.adapter_feature_input,self.profile,model_identity)
        self._update(adapter_version=candidate.VERSION,adapter_configuration=candidate.CONFIG,model_identity=model_identity,
            lpips_learned_sha256=sha(package/'weights/v0.1/alex.pth'),
            feature_normalization='existing clip_feature FP32 torch L2 then exactly one CandidateAdapter FP64 NumPy L2; context adds none')
        self.resource_snapshot('models_loaded');self.check()

    def _update(self,**values):
        self.provenance.update(values);self.publish(dict(values))

    def resource_snapshot(self,stage):
        import torch
        import m1_phasemark as util
        rss=util.working_set_bytes();self.peaks['peak_rss_bytes']=max(self.peaks['peak_rss_bytes'],rss)
        value=dict(stage=stage,rss_bytes=rss)
        if torch.cuda.is_initialized():
            torch.cuda.synchronize();free,total=torch.cuda.mem_get_info(0)
            allocated=torch.cuda.memory_allocated();peak=torch.cuda.max_memory_allocated();self.peaks['peak_allocated_bytes']=max(self.peaks['peak_allocated_bytes'],peak)
            value.update(allocated_bytes=allocated,reserved_bytes=torch.cuda.memory_reserved(),peak_allocated_bytes=peak,free_bytes=int(free),total_bytes=int(total))
            effective=self.provenance['gpu_allocation_budget']['effective_allocation_bytes']
            if allocated>effective:raise RuntimeError('Effective CUDA allocation ceiling')
        self._update(**self.peaks);self.event(kind='model_context_resource',**value)
        if rss>self.config['ram_budget_bytes']:raise RuntimeError('RAM ceiling')
        return value

    def place_inference(self,device):
        if device not in ('cpu','cuda'):raise ValueError('Only reviewed inference placements')
        import torch
        import m1_terminal_continuous as component
        before=self.resource_snapshot('before_inference_to_'+device)
        sizes=component.move_inference_models((self.vae_public,self.safety),device)
        gc.collect();torch.cuda.empty_cache()
        after=self.resource_snapshot('after_inference_to_'+device);self.check()
        return dict(device=device,model_tensor_bytes=sizes,before=before,after=after)

    def adapter_feature_input(self,rgb):
        """Preserve existing helper numerics; no extra context normalization."""
        from three_threat_models import clip_feature
        return clip_feature(self.clip,self.transform,rgb)

    def feature(self,rgb):return self.adapter.feature(rgb)
    def readout(self,rgb,owner):return self.adapter.readout(rgb,owner)

    @staticmethod
    def validate_rgb8(rgb):
        import numpy as np
        if not isinstance(rgb,np.ndarray) or rgb.shape!=(512,512,3) or rgb.dtype!=np.uint8:raise ValueError('Canonical RGB512 uint8 required')

    def safety_check(self,rgb,*,before_safety=None):
        import numpy as np
        import torch
        from PIL import Image
        self.validate_rgb8(rgb)
        if before_safety is not None:before_safety()
        with torch.inference_mode():
            x=self.safety_processor([Image.fromarray(rgb)],return_tensors='pt').pixel_values.to('cuda',dtype=torch.float16)
            _,flags=self.safety(images=rgb[None].astype(np.float32)/255,clip_input=x)
        if flags!=[False]:raise RuntimeError('Safety checker blocked output')
        return dict(checker='pinned SD1.5 FP16',nsfw=False)

    def vae_cycle(self,rgb,*,before_safety=None):
        import torch
        from m1_confirmatory_image_operations import vae_mode
        self.validate_rgb8(rgb)
        def checked_safety(**kwargs):
            if before_safety is not None:before_safety()
            return self.safety(**kwargs)
        result=vae_mode(rgb,vae=self.vae_public,processor=self.processor,safety=checked_safety,
            safety_processor=self.safety_processor,torch_module=torch,device='cuda')
        self.event(kind='image_operation',receipt=result.receipt)
        return result.rgb8

    def quality(self,left,right):
        self.validate_rgb8(left);self.validate_rgb8(right)
        from m1_latent_reconstruction import quality
        from three_threat_models import lpips_score
        value=quality(left,right);value['lpips']=lpips_score(self.metric,left,right)
        value['quality_admissible']=(value['psnr_infinite'] or value['psnr_db']>35) and value['ssim_rgb']>.9 and value['lpips']<.1
        return value
