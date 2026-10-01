"""Fixed offline v4 attack adapter; no model imports at module import."""
from types import SimpleNamespace
from v4_study_protocol import SEEDS, STRENGTHS
from three_threat_models import validate_generated


def diffusion_kwargs(strength, seed, image, factory):
    if type(strength) not in (int,float) or strength not in STRENGTHS:
        raise ValueError("unlisted strength")
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("unlisted seed")
    return {"prompt":"", "negative_prompt":"", "image":image, "strength":strength,
            "num_inference_steps":20, "eta":0.0, "guidance_scale":1.0,
            "generator":factory(device="cuda").manual_seed(seed), "num_images_per_prompt":1,
            "output_type":"pil", "return_dict":True}


def vae_round_trip(pipeline, image):
    import torch
    if pipeline.safety_checker is None or pipeline.feature_extractor is None:
        raise RuntimeError("safety components missing")
    with torch.inference_mode():
        inputs = pipeline.image_processor.preprocess(image).to(device="cuda",dtype=pipeline.vae.dtype)
        latent = pipeline.vae.encode(inputs).latent_dist.mode()
        decoded = pipeline.vae.decode(latent,return_dict=False)[0]
        decoded, flags = pipeline.run_safety_checker(decoded,torch.device("cuda"),pipeline.vae.dtype)
        # All safety failures are rejected before writing image bytes.
        if flags is None or len(flags)!=1 or type(flags[0]) is not bool or flags[0]:
            raise RuntimeError("safety_checker_blocked_or_malformed_vae_output")
        images = pipeline.image_processor.postprocess(decoded,output_type="pil",do_denormalize=[True])
    return validate_generated(SimpleNamespace(images=images,nsfw_content_detected=flags))
