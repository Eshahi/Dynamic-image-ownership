"""Prospective three-arm scientific worker: exact official approval required."""
import argparse
import gc
import importlib.metadata
import json
import os
import platform
import shutil
import socket
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.embedding import localization_package as package
from src.embedding import quality_package as custody
from scripts.c4_saved_pair import fresh, append_progress, failed_cells
STABLE=Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")


def cells():
    return {stage+":"+arm:"pending" for stage in ("render","safety","lpips")
            for arm in ("vae_only","ddim_zero_noise","ddim_fixed_base_noise")}


def run(manifest_path,output):
    start=time.monotonic()
    manifest,snapshots,pins=package.inputs(custody.read(manifest_path),ROOT)
    custody.unlinked(output)
    if not all((output/n).is_dir() for n in ("outputs","logs","checkpoints")):
        raise ValueError("official artifact directories required")
    inventory=cells();current={"phase":"worker_started"}
    result={"run_id":package.RUN,"experiment_id":package.EXPERIMENT,
        "git_commit":manifest["git_commit"],"manifest_sha256":custody.sha(custody.canonical(manifest)),
        "input_sha256":pins,"cell_inventory":inventory,"arms":{},
        "scope":"one-source-exploratory-localization-not-replacement-method",
        "scientific_acceptance":False,"blind_detection":"NOT_RUN"}
    with custody.unlinked(output/"logs/localization-progress.jsonl").open("xb") as journal:
        def record(phase,**values):
            if "cell" in values:
                cell,status=values["cell"],values["cell_status"]
                allowed={"pending":"running","running":"completed"}
                if cell not in inventory or (status!="failed" and allowed.get(inventory[cell])!=status):
                    raise ValueError("invalid cell transition")
                inventory[cell]=status
            append_progress(journal,start,phase,**values);current["phase"]=phase
        record("worker_started",expected_cells=dict(inventory),manifest_sha256=result["manifest_sha256"],
               missing_terminal_report="interrupted-incomplete-never-completed")
        try:
            for name in ("HF_HUB_OFFLINE","TRANSFORMERS_OFFLINE","DIFFUSERS_OFFLINE"):
                if os.environ.get(name)!="1": raise ValueError("offline flags absent")
            if os.environ.get("CUBLAS_WORKSPACE_CONFIG")!=":4096:8": raise ValueError("determinism flag absent")
            def blocked(*args,**kwargs): raise RuntimeError("network prohibited")
            socket.socket.connect=blocked;socket.socket.connect_ex=blocked;socket.create_connection=blocked
            actual={"python":platform.python_version(),"versions":sorted(
                (d.metadata["Name"],d.version) for d in importlib.metadata.distributions())}
            if custody.canonical(actual)!=custody.canonical(json.loads(snapshots[custody.ENV])):
                raise ValueError("pinned scientific environment changed")
            result["environment"]=actual
            from src.embedding.validation_bridge import consume_validation_receipt
            loaded=consume_validation_receipt(manifest_path,output/"checkpoints",root=ROOT)
            raw_images,enrollment=custody.retained(STABLE)
            import numpy as np
            import torch
            from src.data.preprocess import load_config,decode_source,pixel_sha,normalized,encode_output
            from src.embedding.local_assets import plan_assets,snapshot_assets,load_snapshot
            from src.embedding.residency import PhaseResidency
            from src.embedding.proposed import latent_streams,padded_source
            from src.embedding.reconstruction import localization,ARMS
            from src.embedding.quality import classical,load_lpips,lpips_distance,target_checks
            config,_=load_config(ROOT/"configs/data.json")
            source=decode_source(raw_images["source"],config)[0]
            if source.shape!=(333,500,3) or pixel_sha(source)!=custody.PIXELS["source"]:
                raise ValueError("retained source canonical identity changed")
            if not torch.cuda.is_available(): raise ValueError("CUDA unavailable")
            free,total=torch.cuda.mem_get_info();limit=package.RESOURCES["vram_mib"]*1024**2
            available=int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                if line.startswith("MemAvailable:")))*1024
            disk=shutil.disk_usage(output).free
            if free<limit+1024**3 or available<13*1024**3 or disk<4*1024**3:
                raise ValueError("fixed resource headroom unavailable")
            result["resources_initial"]={"free_vram_bytes":free,"total_vram_bytes":total,
                "torch_limit_bytes":limit,"available_ram_bytes":available,"free_disk_bytes":disk}
            torch.cuda.set_per_process_memory_fraction(limit/total);torch.cuda.reset_peak_memory_stats()
            torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False
            torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.manual_seed(0)
            record("retained_source_and_environment_verified")
            plan=plan_assets(ROOT/"research/a6-candidate-model-assets.json")
            snapshot=snapshot_assets(STABLE/custody.ASSETS,output/"checkpoints",plan)
            record("sd_load_started")
            models=load_snapshot(loaded,plan,snapshot,device="cuda",progress=lambda row:record(**row),
                                 activation_checkpointing=True)
            result["model_identity"]=models.identity;record("sd_load_completed",identity=models.identity)
            residency=PhaseResidency(models,progress=lambda row:record(**row));residency.park_idle()
            tensor=torch.from_numpy(normalized(source).transpose(2,0,1).copy()).unsqueeze(0).to("cuda")
            padded=padded_source(tensor,models.components.settings.maximum_side)
            base,_,_=latent_streams(0,bytes.fromhex(custody.FILES["source"][2]),
                bytes.fromhex(enrollment["Ws"]),bytes.fromhex(enrollment["Wi"]),
                bytes.fromhex(loaded.value["dct"]["config_id"]),padded.shape[-2]//8,padded.shape[-1]//8,tensor.device)
            pixels={}
            def progress(row):
                if row["operation"] in ARMS:
                    arm=row["operation"]
                    if row["phase"]=="operation_started":
                        record("arm_started",cell="render:"+arm,cell_status="running")
                    else:
                        record("arm_completed",cell="render:"+arm,cell_status="completed",outcome=result["arms"][arm])
                else: record(**row)
            def save_arm(arm,image):
                native=image[0].permute(1,2,0).detach().cpu().numpy()
                raw,decoded=encode_output(native)
                path=output/"outputs"/(arm+".png");custody.unlinked(path)
                with path.open("xb") as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
                pixels[arm]=decoded
                result["arms"][arm]={"png_sha256":custody.sha(raw),"pixel_sha256":pixel_sha(decoded),
                    "native_hwc":list(decoded.shape),"quality_source":classical(source,decoded),
                    "safety_status":"NOT_RUN"}
                record("saved_arm_partial",arm=arm,outcome=result["arms"][arm])
            images=localization(models.components,tensor,base,maximum_side=models.components.settings.maximum_side,
                                progress=progress,record_arm=save_arm)
            result["matched_control_pixel_replay"]=(result["arms"][ARMS[2]]["pixel_sha256"]==custody.PIXELS["control"])
            record("matched_control_replay",passed=result["matched_control_pixel_replay"])
            if not result["matched_control_pixel_replay"]:
                raise ValueError("fixed-base control differs from prior canonical pixels; no silent relabel")
            residency.prepare_safety()
            for arm in ARMS:
                record("safety_started",cell="safety:"+arm,cell_status="running")
                flag=models.check_saved_pixels(pixels[arm]);result["arms"][arm]["safety_flagged"]=flag
                result["arms"][arm]["safety_status"]="flagged" if flag else "unflagged"
                record("safety_observed",arm=arm,flagged=flag)
                if flag: raise ValueError("diagnostic safety flagged; preserve restricted outputs")
                record("safety_completed",cell="safety:"+arm,cell_status="completed",outcome=result["arms"][arm])
            del models,residency,images,tensor,padded,base;gc.collect();torch.cuda.empty_cache()
            record("lpips_load_started")
            metric=load_lpips(STABLE/custody.ASSETS/"alexnet/alexnet-owt-7be5be79.pth","cuda")
            record("lpips_load_completed")
            for arm in ARMS:
                record("lpips_started",cell="lpips:"+arm,cell_status="running")
                metrics=result["arms"][arm]["quality_source"]
                metrics["lpips_alex_v01"]=lpips_distance(metric,source,pixels[arm])
                metrics["target_diagnostics"]=target_checks(metrics)
                record("lpips_completed",cell="lpips:"+arm,cell_status="completed",outcome=result["arms"][arm])
            torch.cuda.synchronize()
            if any(status!="completed" for status in inventory.values()): raise ValueError("incomplete arms")
            result["status"]="completed_localization_diagnostic_only";code=0
            record("completed_localization_diagnostic_only")
        except Exception as error:
            result.update(status="failed_retained_partial",error_type=type(error).__name__,
                error_message=str(error)[:512],failure_phase=current["phase"]);code=1
            for cell in failed_cells(inventory):
                record("cell_failed",cell=cell,cell_status="failed",error_type=type(error).__name__,
                       failure_phase=result["failure_phase"])
            record("failed",error_type=type(error).__name__,failure_phase=result["failure_phase"])
        try:
            if "torch" in locals() and torch.cuda.is_initialized():
                result["resources_final"]={"peak_torch_allocated_bytes":torch.cuda.max_memory_allocated(),
                    "peak_torch_reserved_bytes":torch.cuda.max_memory_reserved(),
                    "peak_worker_rss_bytes":__import__("resource").getrusage(__import__("resource").RUSAGE_SELF).ru_maxrss*1024}
        except Exception as error: result["resource_read_error"]=type(error).__name__
        result["elapsed_seconds"]=time.monotonic()-start
        fresh(output/"outputs/localization.json",result)
        return code


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True,type=Path);parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args();raise SystemExit(run(args.manifest,args.output_dir))
