"""Fixed v4 revision-2 study. Scientific entry only through separately approved official runner.

Same inventory, attacks, seeds and models as v4_study_worker.py (revision 1);
only the codec revision, the profile and the experiment/run identity differ.
Bookkeeping writes are throttled; every stage boundary still forces a write.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import time

from v4_study_protocol import (OWNERS,MODES,EXPANDED_IDS,ORIGINAL_IDS,
                               inventory,claims,planned_calls,transfer,distance)
from three_threat_models import block_network
from v4_study_boundary import prepare_marked

ROOT = Path(__file__).resolve().parents[1]
EXP = "c4-v4r2-three-threat-small-v1"
RUN = "c4-v4r2-three-threat-dev-001"
CHECKPOINT_SECONDS = 30.0
PACKAGE = ROOT / "experiments" / EXP
OLD_PACKAGE = ROOT / "experiments/c4-three-threat-small-v1"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def run(manifest_path,output_path):
    block_network()
    import numpy as np
    import torch
    from PIL import Image
    from a6_clip_visual import load_visual_encoder
    from qim_rgb_pilot import canonical_rgb,host_path,persist_rgb,quality,write_json
    import revised_watermark_v4 as codec
    if codec.REVISION != 2:
        raise ValueError("revision-2 codec required")
    from three_threat_models import (verify_assets,clip_feature,load_regenerator,
                                     load_lpips,lpips_score,validate_generated,DDIM_CONFIG)
    from three_threat_protocol import center_patch,residual_transfer
    from v4_study_models import diffusion_kwargs,vae_round_trip

    manifest = json.loads(host_path(manifest_path).read_text())
    if (manifest["experiment_id"],manifest["run_id"],manifest["execution_target"])!=(EXP,RUN,"local"):
        raise ValueError("unlisted v4 experiment")
    if manifest["seeds"] != [0,1,2] or manifest["budget"] != {"max_seconds":86400,"max_usd":0,"hourly_usd":0}:
        raise ValueError("fixed seed/watchdog profile differs")
    if manifest["resources"] != {"vram_mib":8192,"ram_mib":6144,"disk_mib":2048}:
        raise ValueError("fixed resources differ")
    for item in manifest["inputs"]:
        if digest(ROOT/item["path"])!=item["sha256"]:
            raise ValueError("package input changed: "+item["path"])
    runtime = json.loads((OLD_PACKAGE/"runtime-files-v2.json").read_text())
    for item in runtime["files"]:
        if digest(item["path"])!=item["sha256"]:
            raise ValueError("runtime changed: "+item["path"])
    profile = codec.load_profile(PACKAGE/"profile.json")
    if profile["security"]!="public-derived" or profile["semantic_source"]!="external:clip-vit-b32-a6-40d365715913":
        raise ValueError("external public profile required")
    cases0 = json.loads((ROOT/"experiments/c4-qim-rgb-development-v1/cohort.json").read_text())["cases"]
    extra = json.loads((OLD_PACKAGE/"development-expansion.json").read_text())["new_cases"]
    cases = sorted(cases0+extra,key=lambda c:c["source_id"])
    if tuple(c["source_id"] for c in cases)!=EXPANDED_IDS or tuple(c["source_id"] for c in cases0)!=ORIGINAL_IDS:
        raise ValueError("reserved cohort differs")
    labels = json.loads((OLD_PACKAGE/"semantic-labels.json").read_text())["pairs"]
    rows = [{**r,"status":"NOT_RUN","detections":[],"visual_retention":"NOT_REVIEWED",
             "planned_claims":claims(r)} for r in inventory(labels)]
    index = {r["id"]:r for r in rows}
    planned = planned_calls(rows)
    if planned != 1884:
        raise ValueError("call inventory differs")
    assets = host_path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6")
    receipt,lpips_package = verify_assets(assets,ROOT/"research/a6-candidate-model-assets.json")
    output = host_path(output_path)
    images = output/"outputs/images"
    images.mkdir(parents=True,exist_ok=False)
    if os.environ.get("PYTHONHASHSEED")!="0" or os.environ.get("CUBLAS_WORKSPACE_CONFIG")!=":4096:8":
        raise ValueError("deterministic environment missing")
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark=False
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.set_num_threads(1)
    if not torch.cuda.is_available():
        raise RuntimeError("local CUDA unavailable; no fallback")
    torch.cuda.reset_peak_memory_stats()
    free,total = torch.cuda.mem_get_info()
    if free < 8704*1024**2:
        raise RuntimeError("VRAM headroom insufficient")
    started = time.monotonic()
    failures,saved,eligible = [],{},set()
    runtime_receipt={"asset_files":receipt["files"],"runtime_inventory_sha256":digest(OLD_PACKAGE/"runtime-files-v2.json"),
                     "profile_sha256":digest(PACKAGE/"profile.json"),"owners":OWNERS,
                     "cuda_device":torch.cuda.get_device_name(),"cuda_free_before_bytes":free,
                     "cuda_total_bytes":total,"planned_detector_calls":planned,"planned_rows":len(rows),
                     "nominal_bound":"conditional/unvalidated; not a public-profile security or FPR guarantee",
                     "native_to_pilot":[],"effective_ddim_config":DDIM_CONFIG,
                     "codec_revision":codec.REVISION,"detector_config_id":codec.detector_config_id(profile),
                     "codec_sha256":digest(ROOT/"scripts/revised_watermark_v4.py")}

    last_write=[0.0]
    image_bytes=[0]

    def log(message):
        print(f"[{time.monotonic()-started:8.1f}s] {message}",flush=True)

    def checkpoint(force=False):
        now=time.monotonic()
        if not force and now-last_write[0]<CHECKPOINT_SECONDS:
            return
        last_write[0]=now
        write_json(output/"outputs/results.json",{"run_id":RUN,"rows":rows,"stage_failures":failures,
            "elapsed_seconds":time.monotonic()-started,"method_acceptance":False,
            "scientific_verdict":"PENDING_ANALYSIS_AND_VISUAL_REVIEW",
            "planned_detector_calls":planned,"completed_detector_calls":sum(len(r["detections"]) for r in rows)})
        runtime_receipt.update(peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            cuda_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
            cuda_peak_reserved_bytes=torch.cuda.max_memory_reserved())
        write_json(output/"outputs/runtime.json",runtime_receipt)

    def guard():
        if time.monotonic()-started>=86000:
            raise TimeoutError("operational watchdog reached")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>6144*1024:
            raise MemoryError("RAM ceiling reached")
        if torch.cuda.max_memory_reserved()>8192*1024**2:
            raise MemoryError("VRAM ceiling reached")
        if image_bytes[0]>2000*1024**2:
            raise OSError("output allowance reached")

    def fail(row,error):
        row["status"]="failed"
        row.setdefault("errors",[]).append({"type":type(error).__name__,"message":str(error)})
        if isinstance(error,codec.EmbeddingError):
            row["embedding_error_report"]=error.report
        checkpoint()

    def stage_fail(stage,error):
        failures.append({"stage":stage,"type":type(error).__name__,"message":str(error)})
        log(f"STAGE FAILURE {stage}: {type(error).__name__}: {error}")
        checkpoint(True)

    def save(row,rgb):
        guard()
        path=images/(row["id"]+".png")
        observed=persist_rgb(path,rgb)
        image_bytes[0]+=path.stat().st_size
        row["image"]={"path":str(path.relative_to(output)),"sha256":digest(path),
                      "pixel_sha256":hashlib.sha256(observed.tobytes()).hexdigest()}
        saved[row["id"]]=path
        row["status"]="image_saved"
        checkpoint()
        return observed

    def read(identity):
        row=index[identity]
        path=saved[identity]
        if digest(path)!=row["image"]["sha256"]:
            raise ValueError("saved image changed")
        with Image.open(path) as im:
            im.load()
            if im.mode!="RGB" or im.size!=(512,512):
                raise ValueError("saved geometry changed")
            rgb=np.asarray(im,dtype=np.uint8).copy()
        if hashlib.sha256(rgb.tobytes()).hexdigest()!=row["image"]["pixel_sha256"]:
            raise ValueError("saved pixels changed")
        return rgb

    def feature(row,rgb,model,transform):
        guard()
        before=time.perf_counter()
        value=clip_feature(model,transform,rgb).reshape(-1).tolist()
        row["clip"]={"values":value,"dimension":512,"l2_normalized":True,
            "pixel_sha256":row["image"]["pixel_sha256"],
            "checkpoint_sha256":"40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af",
            "feature_sha256":hashlib.sha256(json.dumps(value,separators=(",",":"),allow_nan=False).encode()).hexdigest(),
            "elapsed_seconds":time.perf_counter()-before}
        return value

    def detect_row(row,rgb,vector):
        plane=codec.luminance_from_rgb(rgb.tolist())
        for owner,mode,roster in claims(row):
            try:
                guard()
                before=time.perf_counter()
                result=codec.detect(plane,owner,profile=profile,semantic_features=vector,
                                    binding_mode=mode,roster_size=roster)
                row["detections"].append({"claimed_owner":owner,"binding_mode":mode,"result":result,
                    "elapsed_seconds":time.perf_counter()-before,
                    "feature_origin":"same saved suspect RGB8","pixel_sha256":row["image"]["pixel_sha256"]})
                checkpoint()
            except Exception as error:
                row.setdefault("detector_failures",[]).append({"owner":owner,"mode":mode,"message":str(error)})
                fail(row,error)
        if len(row["detections"])==len(claims(row)):
            row["detection_complete"]=True
            row["status"]="detected" if not row.get("errors") else "failed"

    checkpoint(True)
    log(f"start: {len(rows)} rows, {planned} planned detector calls, codec r{codec.REVISION}")
    for case in cases:
        row=index[f"clean-{case['source_id']}-C0"]
        try:
            guard()
            path=host_path(case["path"])
            if digest(path)!=case["raw_sha256"]:
                raise ValueError("reserved raw bytes changed")
            native=canonical_rgb(path)
            if native.shape!=(case["height"],case["width"],3):
                raise ValueError("native shape changed")
            rgb=np.asarray(Image.fromarray(native).resize((512,512),Image.Resampling.BICUBIC),dtype=np.uint8).copy()
            save(row,rgb)
            runtime_receipt["native_to_pilot"].append({"source_id":case["source_id"],"raw_sha256":case["raw_sha256"],
                "native_shape":list(native.shape),"native_pixel_sha256":hashlib.sha256(native.tobytes()).hexdigest()})
        except Exception as error:
            fail(row,error)

    log("stage clean_clip_embed")
    # CLIP is now a declared detector component, not an evaluator-only shortcut.
    model=transform=None
    try:
        guard()
        model,transform=load_visual_encoder(assets/"clip/ViT-B-32.pt",device="cpu")
        for source_id in EXPANDED_IDS:
            c0=index[f"clean-{source_id}-C0"]
            c1=index[f"clean-{source_id}-C1"]
            try:
                rgb=read(c0["id"])
                vector=feature(c0,rgb,model,transform)
                detect_row(c0,rgb,vector)
            except Exception as error:
                fail(c0,error)
                fail(c1,RuntimeError("source/feature prerequisite failed"))
                continue
            try:
                guard()
                def record(report,seconds):
                    c1["embedding_seconds"]=seconds
                    c1["source_feature_embedding_report"]=report
                marked,suspect_vector=prepare_marked(
                    rgb.tolist(),vector,
                    lambda pixels,**kw:codec.embed_rgb(pixels,OWNERS[0],profile=profile,**kw),
                    lambda pixels:save(c1,np.asarray(pixels,dtype=np.uint8)),
                    lambda:read(c1["id"]),
                    lambda pixels:feature(c1,pixels,model,transform),record)
                detect_row(c1,marked,suspect_vector)
                c1["changed_channels"]=int(np.count_nonzero(rgb!=marked))
                c1["embedding_eligible"]=bool(c1.get("detection_complete") and c1["detections"][0]["result"]["outcome"]=="both_match" and c1["changed_channels"]>0)
                if c1["embedding_eligible"]:
                    eligible.add(source_id)
                else:
                    c1["embedding_failed"]=True
                    fail(c1,RuntimeError("authoritative saved-suspect verification or nonzero-payload prerequisite failed"))
            except Exception as error:
                fail(c1,error)
    except Exception as error:
        stage_fail("clean_clip_embed",error)
    finally:
        del model,transform
        gc.collect()
        checkpoint(True)

    log(f"stage transfers; eligible marked sources: {sorted(eligible)}")
    for row in rows:
        if row["axis"] not in ("T4","T5-transfer"):
            continue
        try:
            guard()
            attack_started=time.perf_counter()
            if row["arm"] not in ("unmarked_patch_sham","unmarked_band_sham") and row["donor_id"] not in eligible:
                raise RuntimeError("failed donor embedding prerequisite")
            recipient=read(f"clean-{row['recipient_id']}-C0")
            donor0=read(f"clean-{row['donor_id']}-C0")
            arm=row["arm"]
            if arm=="unmarked_patch_sham":
                attacked=center_patch(recipient.tolist(),donor0.tolist(),row["patch_size"])
            elif arm=="unmarked_band_sham":
                attacked=transfer(recipient.tolist(),donor0.tolist(),profile,arm)
            else:
                donor1=read(f"clean-{row['donor_id']}-C1")
                if arm=="public_patch":
                    attacked=center_patch(recipient.tolist(),donor1.tolist(),row["patch_size"])
                elif arm=="clean_donor_residual":
                    attacked=residual_transfer(recipient.tolist(),donor1.tolist(),donor0.tolist(),row["scale"])
                else:
                    attacked=transfer(recipient.tolist(),donor1.tolist(),profile,arm)
            save(row,np.asarray(attacked,dtype=np.uint8))
            row["attack_seconds_including_save"]=time.perf_counter()-attack_started
            checkpoint()
        except Exception as error:
            fail(row,error)

    log("stage regeneration")
    pipeline=None
    try:
        guard()
        pipeline=load_regenerator(assets)
        def on_step(pipe,step,timestep,values):
            guard()
            return values
        for row in rows:
            if row["axis"]!="T3":
                continue
            try:
                guard()
                attack_started=time.perf_counter()
                if row["control"]=="C1" and row["source_id"] not in eligible:
                    raise RuntimeError("failed source embedding prerequisite")
                rgb=read(f"clean-{row['source_id']}-{row['control']}")
                image=Image.fromarray(rgb)
                if row["dose"]=="vae_mode":
                    observed=vae_round_trip(pipeline,image)
                else:
                    kwargs=diffusion_kwargs(row["strength"],row["seed"],image,torch.Generator)
                    with torch.inference_mode():
                        generated=pipeline(**kwargs,callback_on_step_end=on_step,callback_on_step_end_tensor_inputs=["latents"])
                    observed=validate_generated(generated)
                row["safety_checked"]=True
                save(row,np.asarray(observed,dtype=np.uint8).copy())
                row["attack_seconds_including_save"]=time.perf_counter()-attack_started
                checkpoint()
            except Exception as error:
                fail(row,error)
    except Exception as error:
        stage_fail("regeneration",error)
    finally:
        del pipeline
        gc.collect()
        torch.cuda.empty_cache()
        checkpoint(True)

    model=transform=None
    try:
        guard()
        log("stage suspect_clip_detect")
        model,transform=load_visual_encoder(assets/"clip/ViT-B-32.pt",device="cpu")
        for row in rows:
            if row["axis"] in ("clean","T5") or row["id"] not in saved:
                continue
            try:
                guard()
                rgb=read(row["id"])
                vector=feature(row,rgb,model,transform)
                detect_row(row,rgb,vector)
                if row["axis"]=="T3":
                    source_vector=index[f"clean-{row['source_id']}-C0"]["clip"]["values"]
                    row["clip_source_cosine"]=sum(a*b for a,b in zip(vector,source_vector))
                    row["clip_retention_threshold"]=.90
                checkpoint()
            except Exception as error:
                fail(row,error)
        codes={}
        for identity in EXPANDED_IDS:
            for control in ("C0","C1"):
                try:
                    guard()
                    row=index[f"clean-{identity}-{control}"]
                    rgb=read(row["id"])
                    codes[identity,control]=(codec.semantic_code(row["clip"]["values"],profile=profile),
                         codec.perceptual_hash(codec.luminance_from_rgb(rgb.tolist()),profile=profile))
                except Exception as error:
                    stage_fail(f"code-{identity}-{control}",error)
            if (identity,"C0") in codes and (identity,"C1") in codes:
                a,b=codes[identity,"C0"],codes[identity,"C1"]
                index[f"clean-{identity}-C1"]["same_instance_distances"]={"semantic":distance(a[0],b[0]),"instance":distance(a[1],b[1])}
        for row in rows:
            if row["axis"]!="T5":
                continue
            try:
                for control in ("C0","C1"):
                    a,b=codes[row["left"],control],codes[row["right"],control]
                    row["distances_"+control]={"semantic":distance(a[0],b[0]),"instance":distance(a[1],b[1])}
                a=index[f"clean-{row['left']}-C0"]["clip"]["values"]
                b=index[f"clean-{row['right']}-C0"]["clip"]["values"]
                row["clip_pair_cosine"]=sum(x*y for x,y in zip(a,b))
                row["status"]="complete_component_diagnostic"
                checkpoint()
            except Exception as error:
                fail(row,error)
    except Exception as error:
        stage_fail("suspect_clip_detect",error)
    finally:
        del model,transform
        gc.collect()
        checkpoint(True)

    metric=None
    try:
        guard()
        log("stage lpips")
        metric=load_lpips(assets,lpips_package)
        for row in rows:
            if row["id"] not in saved:
                continue
            try:
                guard()
                rgb=read(row["id"])
                if row["axis"]=="clean":
                    references={"quality":f"clean-{row['source_id']}-C0"}
                elif row["axis"]=="T3":
                    references={"quality_immediate":f"clean-{row['source_id']}-{row['control']}",
                                "quality_source":f"clean-{row['source_id']}-C0"}
                else:
                    references={"quality":f"clean-{row['recipient_id']}-C0"}
                for name,identity in references.items():
                    reference=read(identity)
                    scores=quality(reference,rgb)
                    scores["lpips"]={"status":"measured","value":lpips_score(metric,reference,rgb)}
                    row[name]=scores
                row["metrics_complete"]=True
                if row.get("detection_complete") and not row.get("errors"):
                    row["status"]="metrics_complete"
                checkpoint()
            except Exception as error:
                fail(row,error)
    except Exception as error:
        stage_fail("lpips",error)
    finally:
        del metric
        gc.collect()
        checkpoint(True)
    checkpoint(True)
    log(f"done: {sum(len(r['detections']) for r in rows)}/{planned} detector calls, {len(failures)} stage failures")
    complete=(not failures and all(r["status"] in ("metrics_complete","complete_component_diagnostic") for r in rows)
              and sum(len(r["detections"]) for r in rows)==planned)
    return 0 if complete else 1


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    raise SystemExit(run(args.manifest,args.output_dir))
