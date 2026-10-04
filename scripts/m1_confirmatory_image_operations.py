"""Path-free frozen image operations. No models, assets or sources are loaded here."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
import numpy as np
from PIL import Image
import three_threat_models as models
import three_threat_protocol as protocol
import revised_watermark_v5 as codec
import m1_owner_interface as owners
from m1_confirmatory_t5_pairs import category_signature, schedule as select_t5_pairs

VERSION = 'm1-confirmatory-image-operations-v1'
STRENGTHS = (.05, .1, .2, .4)
SEEDS = (0, 1, 2)
TIMESTEPS = tuple(range(951, 0, -50))


@dataclass(frozen=True)
class OperationResult:
    rgb8: np.ndarray
    receipt: dict


class OperationFailure(RuntimeError):
    def __init__(self, message, receipt):
        super().__init__(message)
        self.receipt = dict(receipt, outcome='failed', error=message)


def rgb8(value):
    if not isinstance(value, np.ndarray) or value.dtype != np.uint8 or value.shape != (512, 512, 3):
        raise ValueError('Exact canonical RGB8 ndarray512x512x3 required')
    return np.ascontiguousarray(value).copy()


def pixel_sha(value):
    return hashlib.sha256(rgb8(value).tobytes()).hexdigest()


def _receipt(image, operator):
    return dict(schema=VERSION, operator=operator, input_rgb8_sha256=pixel_sha(image),
                query_budget=0, human_visual_verdict=None)


def _finish(value, receipt):
    value = rgb8(value)
    return OperationResult(value, dict(receipt, outcome='completed', output_rgb8_sha256=pixel_sha(value)))


def _numbers(value):
    if hasattr(value, 'detach'): value = value.detach().cpu().tolist()
    return [float(x) for x in value]


def regeneration(image, strength, seed, *, pipeline, generator_factory, inference_context):
    """One untouched C0/C1 input, fresh paired seed, no retries or reader calls."""
    image = rgb8(image)
    if type(strength) not in (int, float) or strength not in STRENGTHS:
        raise ValueError('Frozen regeneration strength required')
    if type(seed) is not int or seed not in SEEDS: raise ValueError('Frozen seed required')
    for key, expected in models.DDIM_CONFIG.items():
        if getattr(pipeline.scheduler.config, key, object()) != expected:
            raise ValueError('Effective DDIM config mismatch: '+key)
    if pipeline.safety_checker is None or pipeline.feature_extractor is None:
        raise ValueError('Required pipeline safety components missing')
    receipt = _receipt(image, 'SD1.5 DDIM20 img2img')
    receipt.update(strength=strength, seed=seed, ddim_config=dict(models.DDIM_CONFIG),
                   prompt='', negative_prompt='', guidance_scale=1., eta=0., num_inference_steps=20,
                   actual_ddim_timesteps=[], nfe_unet=0, safety_verdict=None)
    def forward(module, args, kwargs, output):
        t = args[1] if len(args)>1 else kwargs['timestep']
        if hasattr(t, 'detach'): t=t.detach().cpu().item()
        t=float(t)
        if not math.isfinite(t): raise ValueError('Nonfinite actual UNet timestep')
        receipt['actual_ddim_timesteps'].append(t)
        receipt['nfe_unet']+=1
    hook=pipeline.unet.register_forward_hook(forward, with_kwargs=True)
    try:
        # Reuse original validated settings/generator factory. Original inventory only
        # accepted .2/.4; prospective draft adds .05/.1 without changing its math.
        kwargs=models.regeneration_kwargs(.2,seed,Image.fromarray(image),generator_factory)
        kwargs['strength']=strength
        with inference_context(): result=pipeline(**kwargs)
        receipt['safety_verdict']=getattr(result,'nsfw_content_detected',None)
        receipt['scheduler_timesteps']=_numbers(pipeline.scheduler.timesteps)
        generated=models.validate_generated(result)
        expected=list(TIMESTEPS[-int(20*strength):])
        if receipt['scheduler_timesteps']!=list(TIMESTEPS) or receipt['actual_ddim_timesteps']!=expected:
            raise ValueError('Actual DDIM timestep inventory differs from frozen operator')
        return _finish(np.asarray(generated),receipt)
    except Exception as error:
        raise OperationFailure(str(error),receipt) from error
    finally: hook.remove()


def vae_mode(image, *, vae, processor, safety, safety_processor, torch_module, device='cuda'):
    """Exact existing public FP16 posterior-mode cycle including its safety check."""
    image=rgb8(image)
    if float(vae.config.scaling_factor)!=.18215: raise ValueError('VAE scale differs')
    if safety is None or safety_processor is None: raise ValueError('Required VAE safety components missing')
    receipt=_receipt(image,'VAE FP16 posterior-mode cycle')
    receipt.update(latent_units='scaled_posterior_mode', scaling_factor=.18215,
                   multiplication_then_division_dtype='float16', nfe_unet=0, safety_verdict=None)
    try:
        with torch_module.inference_mode():
            x=processor.preprocess(Image.fromarray(image)).to(device,dtype=torch_module.float16)
            if tuple(x.shape)!=(1,3,512,512) or x.dtype!=torch_module.float16:
                raise ValueError('Preprocessed VAE tensor differs')
            mode=vae.encode(x).latent_dist.mode()
            if tuple(mode.shape)!=(1,4,64,64) or mode.dtype!=torch_module.float16:
                raise ValueError('Posterior-mode latent units/shape/dtype differ')
            z=mode*.18215
            decoded=vae.decode(z/.18215,return_dict=False)[0]
            safety_input=safety_processor(processor.postprocess(decoded,output_type='pil'),return_tensors='pt').pixel_values.to(device,dtype=torch_module.float16)
            checked,flags=safety(images=decoded,clip_input=safety_input)
            receipt['safety_verdict']=flags
            if flags!=[False] or any(type(flag) is not bool for flag in flags):
                raise RuntimeError('VAE cycle safety checker blocked or malformed output')
            value=processor.postprocess(checked,output_type='np',do_denormalize=[True])[0]
            if np.asarray(value).shape!=(512,512,3) or not np.isfinite(value).all():
                raise ValueError('Malformed decoded RGB')
            from m1_blind_noise import rgb8 as quantize_rgb8
            return _finish(quantize_rgb8(value),receipt)
    except Exception as error:
        raise OperationFailure(str(error),receipt) from error


def center_patch(recipient_source_c0, donor_rgb8, size, *, donor_control):
    recipient=rgb8(recipient_source_c0);donor=rgb8(donor_rgb8)
    if type(size) is not int or size not in (128,256): raise ValueError('Frozen patch size required')
    if donor_control not in ('C1','C0'): raise ValueError('Marked donor or unmarked donor sham required')
    result=np.asarray(protocol.center_patch(recipient.tolist(),donor.tolist(),size),dtype=np.uint8)
    start=(512-size)//2
    receipt=_receipt(recipient,'same-coordinate centered RGB8 patch')
    receipt.update(recipient_control='C0-source',donor_control=donor_control,
                   donor_rgb8_sha256=pixel_sha(donor),patch_size=size,
                   bounds_xyxy=[start,start,start+size,start+size], area_pixels=size**2,
                   area_fraction=size**2/512**2,blending=False)
    return _finish(result,receipt)


class V5Comparator:
    """Image-domain codec with injected suspect-only CLIP; codec fields stay intact."""
    def __init__(self, profile, feature):
        self.profile=codec.validate_profile(profile)
        if self.profile['security']!='public-derived' or self.profile['semantic_source']!='external:clip-vit-b32-a6-40d365715913':
            raise ValueError('Public-derived external CLIP profile required')
        decision=self.profile['decision']
        expected=dict(false_positive_target=1e-6,semantic_radius=6,semantic_mismatch_distance=10,
                      instance_radius=6,instance_mismatch_distance=10)
        if decision!=expected: raise ValueError('Frozen v5 draft decision profile differs')
        self.feature=feature

    def embed(self, image, source_uid):
        image=rgb8(image);schedule=owners.source_schedule(source_uid)
        # v5 derives deterministic carriers from owner/profile/content, not the
        # A4 scheduled seed. Preserve exact metadata without claiming consumption.
        schedule=dict(schedule,schedule_seed_role='metadata_only_not_consumed_by_v5',
                      execution_phase_seed=None,execution_rng_policy='deterministic_codec_no_rng')
        output,report=codec.embed_rgb(image.tolist(),schedule['owner'],profile=self.profile,
                                     semantic_features=self.feature(image),strict=False)
        receipt=_receipt(image,'v5 image-domain comparator')
        receipt.update(schedule=schedule,detector_config_id=codec.detector_config_id(self.profile),
                       decision_id=codec.decision_id(self.profile),
                       profile_sha256=hashlib.sha256(json.dumps(self.profile,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),
                       embedding_self_verification_queries=2)
        return _finish(np.asarray(output,dtype=np.uint8),receipt),report

    def extract(self, suspect_rgb8, claim_owner):
        image=rgb8(suspect_rgb8)
        if type(claim_owner) is not str or claim_owner not in owners.A4_OWNERS:
            raise ValueError('Exact public A4 owner required')
        # No source features, reference image, seed, or embedding report reaches readout.
        return codec.detect_rgb(image.tolist(),claim_owner,profile=self.profile,
                                semantic_features=self.feature(image),binding_mode='combined',roster_size=1)
