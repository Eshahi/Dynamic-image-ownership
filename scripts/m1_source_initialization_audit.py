"""Fixed development1675 deterministic original200/adapter/recovery audit.

Each GPU stage is a separate parent-owned process. No GPU or model loads on
import; comparison is CPU only. Scientific data admission is fixed, not a CLI
path override. A passing comparison alone can create a new u0 bridge.
"""
from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
CONFIG_PATH = ROOT / "research/m1-source-initialization-audit-v1.json"
VERSION = "m1-source-initialization-audit-v1"
STEPS = list(range(0,201,10))
STAGES = ("literal", "adapter-prefix", "adapter-resume", "compare", "initialize")
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
if str(ROOT/"scripts") not in sys.path:
    sys.path.insert(0,str(ROOT/"scripts"))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024**2),b""):h.update(block)
    return h.hexdigest()


def write(path,value):
    path=Path(path);temp=path.with_name(path.name+".tmp")
    with temp.open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write("\n")
        f.flush();os.fsync(f.fileno())
    temp.replace(path)


def receipt(path):
    path=Path(path).resolve()
    return {"path":str(path),"sha256":sha(path),"size_bytes":path.stat().st_size}


def checked(item,root=None):
    path=Path(item["path"]).resolve()
    if root is not None and not path.is_relative_to(Path(root).resolve()):
        raise ValueError("Artifact escapes owned run directory")
    if not path.is_file() or sha(path)!=item["sha256"] or path.stat().st_size!=item["size_bytes"]:
        raise ValueError("Missing/changed retained artifact")
    return path


def config():
    value=json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if (value.get("schema")!="m1-source-initialization-audit-config-v1" or
            value.get("data_split")!="development" or value.get("source_id")!=1675 or
            value.get("updates")!=200 or value.get("interruption_step")!=100 or
            value.get("checkpoint_every")!=10 or value.get("seed")!=0 or
            value.get("cohort")!="research/m1-reconstruction-dev.json" or
            value.get("execution_variant")!="ac-deterministic-execution-v1" or
            value.get("legacy_initialization_allowed") is not False or
            value.get("heldout_allowed") is not False):
        raise ValueError("Fixed development audit configuration differs")
    return value


def scientific_paths():
    cfg=config()
    return [Path(__file__),ROOT/"scripts/m1_source_initialization.py",
        ROOT/"scripts/m1_latent_reconstruction.py",ROOT/"scripts/m1_dual_latent.py",
        ROOT/"scripts/m1_terminal_repeatability.py",ROOT/"scripts/three_threat_models.py",
        ROOT/cfg["cohort"],ROOT/"experiments/c4-qim-rgb-development-v1/cohort.json",
        ROOT/"experiments/c4-three-threat-small-v1/development-expansion.json",
        ROOT/"research/a6-candidate-model-assets.json",CONFIG_PATH]


def seed_phase():
    import numpy as np
    import torch
    random.seed(0);np.random.seed(0);torch.manual_seed(0)


def save_payload(path,payload):
    import torch
    path=Path(path);temp=path.with_name(path.name+".tmp")
    if path.exists() or temp.exists():raise FileExistsError("Retained checkpoint exists")
    with temp.open("xb") as f:
        torch.save(payload,f);f.flush();os.fsync(f.fileno())
    os.link(temp,path);temp.unlink()


class LiteralReference:
    """Separately expressed original equations; adapter only serializes state."""
    def __init__(self,target,vae,identity):
        import torch
        import m1_source_initialization as adapter
        self.target=target.detach().clone();self.vae=vae;self.identity=copy.deepcopy(identity)
        self.target_hash=adapter.digest(self.target);self.runtime=adapter._runtime(target)
        with torch.no_grad():self.initial=vae.encode(self.target*2-1).latent_dist.mode()
        self.z=self.initial.detach().clone().requires_grad_(True)
        self.optimizer=torch.optim.Adam([self.z],lr=.02)
        self.step=0;self.observations={}

    def decode(self,z):
        return (self.vae.decode(z,return_dict=False)[0]+1)/2

    def advance(self,on_checkpoint):
        import numpy as np
        import torch
        from torch.utils.checkpoint import checkpoint
        for step in range(201):
            self.step=step
            if step in (0,50,100,200):
                with torch.no_grad():
                    raw=self.decode(self.z)
                    rgb=(raw.clamp(0,1)[0].permute(1,2,0).cpu().numpy()*255).round().astype(np.uint8)
                    self.observations[step]={"rgb8":torch.from_numpy(rgb.copy()),
                        "objective_float_mse":float((raw-self.target).square().mean().item()),
                        "latent_displacement_l2":float(torch.linalg.vector_norm(self.z-self.initial).item())}
            if step%10==0:on_checkpoint(self)
            if step==200:break
            self.optimizer.zero_grad(set_to_none=True)
            decoded=checkpoint(self.decode,self.z,use_reentrant=False)
            loss=(decoded-self.target).square().mean()
            if not bool(torch.isfinite(loss)):raise RuntimeError("Nonfinite loss")
            loss.backward()
            if self.z.grad is None or not bool(torch.isfinite(self.z.grad).all()):
                raise RuntimeError("Missing/nonfinite latent gradient")
            self.optimizer.step()
            if not bool(torch.isfinite(self.z).all()):raise RuntimeError("Nonfinite latent after optimizer update")
        return self

    def state_dict(self):
        # Serialization is shared; no adapter encoding, observation or update call.
        import m1_source_initialization as adapter
        return adapter.ReconstructionSession.state_dict(self)


def compare_states(left,right):
    import m1_source_initialization as adapter
    # Validate integrity/operator/state structure independently before equality.
    for state in (left,right):
        adapter._validate_payload(state,state["identity"],state["target_sha256"],state["runtime"])
    fields=("schema","config","identity","target_sha256","runtime","step",
            "initial","z","optimizer","rng","observations")
    return {name:adapter.digest(left[name])==adapter.digest(right[name]) for name in fields}


def load_run(path,stage):
    path=Path(path).resolve()
    if not path.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):
        raise ValueError("Audit dependency escapes development run root")
    record=json.loads((path/"run.json").read_text(encoding="utf-8"))
    if (record.get("schema")!=VERSION or record.get("data_split")!="development" or
            record.get("stage")!=stage or record.get("outcome")!="completed" or
            record.get("audit_config")!=config()):
        raise ValueError("Completed matching development audit stage required")
    expected={"literal":STEPS,"adapter-prefix":list(range(0,101,10)),
              "adapter-resume":list(range(110,201,10)),"initialize":STEPS}[stage]
    if [v["step"] for v in record.get("checkpoints",[])]!=expected:
        raise ValueError("Incomplete fixed checkpoint inventory")
    for item in record["checkpoints"]:checked(item,path)
    checked(record["source"]["canonical_png"],path)
    return path,record


def compare_runs(reference_dir,prefix_dir,resume_dir):
    import m1_source_initialization as adapter
    entries=[load_run(p,s) for p,s in zip((reference_dir,prefix_dir,resume_dir),STAGES[:3])]
    if len({p for p,_ in entries})!=3 or len({r["process_id"] for _,r in entries})!=3:
        raise ValueError("Three independent process/run identities required")
    a,b,c=[r for _,r in entries]
    identity_fields=("audit_config","scientific_files","scientific_core_sha256","deterministic_execution",
                     "environment","device_identity","assets","identity")
    for field in identity_fields:
        if a[field]!=b[field] or a[field]!=c[field]:raise ValueError("Stage identity mismatch: "+field)
    for other in (b,c):
        for field in ("raw_sha256","rgb8_sha256","native_shape"):
            if a["source"][field]!=other["source"][field]:raise ValueError("Source receipt mismatch")
    dependency=c.get("resume_from",{})
    if dependency!=receipt(entries[1][0]/"run.json"):
        raise ValueError("Recovery must reference this independent adapter prefix")
    prefix100=b["checkpoints"][-1]
    if c.get("resume_checkpoint")!=prefix100:
        raise ValueError("Recovery checkpoint dependency differs")
    ref={v["step"]:v for v in a["checkpoints"]}
    candidate={v["step"]:v for v in b["checkpoints"]+c["checkpoints"]}
    comparisons=[]
    for step in STEPS:
        left=adapter.load_checkpoint(checked(ref[step],entries[0][0]))
        right=adapter.load_checkpoint(checked(candidate[step]))
        if left["step"]!=step or right["step"]!=step:raise ValueError("Checkpoint step differs")
        fields=compare_states(left,right)
        comparisons.append({"step":step,"fields":fields,"exact":all(fields.values()),
                            "reference":ref[step],"candidate":candidate[step]})
    return {"passed":all(v["exact"] for v in comparisons),"comparisons":comparisons,
            "full200_initializer_equivalence":all(v["exact"] for v in comparisons),
            "watermark_success_claim":False},entries


def bridge_from_state(output,record,final,checkpoint_receipt,audit_proof=None):
    """Only an exact verified R2 endpoint can supply a new unscaled u0 receipt."""
    import torch
    import m1_source_initialization as adapter
    from PIL import Image
    adapter._validate_payload(final,final["identity"],final["target_sha256"],final["runtime"])
    if (final["step"]!=200 or final["z"].shape!=(1,4,64,64) or
            final["observations"][200]["rgb8"].shape!=(512,512,3)):
        raise ValueError("Invalid step200 bridge latent/RGB8 shape")
    source_id=final["identity"]["source_id"]
    latent=Path(output)/f"{source_id}-step200.pt";png=Path(output)/f"{source_id}-step200.png"
    save_payload(latent,{"z":final["z"],"step":200,"latent_units":adapter.CONFIG["latent_units"]})
    with png.open("xb") as f:Image.fromarray(final["observations"][200]["rgb8"].numpy()).save(f,format="PNG")
    cp={"step":200,"latent_sha256":sha(latent),"png_sha256":sha(png),
        "objective_float_mse":final["observations"][200]["objective_float_mse"],
        "latent_displacement_l2":final["observations"][200]["latent_displacement_l2"]}
    record["cases"]=[{"id":source_id,"outcome":"completed","source_rgb8_sha256":final["identity"]["source_rgb8_sha256"],
                     "checkpoints":[cp]}]
    record["u0_bridge"]={"schema":"m1-verified-original200-u0-bridge-v1", "source_id":source_id,
        "initializer_state":checkpoint_receipt,"latent":receipt(latent),
        "png":receipt(png),"scientific_core_sha256":final["identity"]["scientific_core_sha256"],
        "legacy_format_only":True,"legacy_initialization_reused":False,
        "embedding_optimizer":"new independent Adam; no initialization moments imported"}
    if audit_proof is not None:record["audit_proof"]=audit_proof


def export_bridge(output,record,entries):
    import m1_source_initialization as adapter
    if record.get("comparison",{}).get("passed") is not True:
        raise ValueError("Passing full initialization audit required for u0 bridge")
    cp=entries[2][1]["checkpoints"][-1]
    final=adapter.load_checkpoint(checked(cp,entries[2][0]))
    bridge_from_state(output,record,final,cp)


def verify_audit(path):
    path=Path(path).resolve()
    if not path.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):
        raise ValueError("Audit proof escapes development run root")
    record=json.loads((path/"run.json").read_text(encoding="utf-8"))
    if (record.get("schema")!=VERSION or record.get("stage")!="compare" or
            record.get("outcome")!="completed" or record.get("comparison",{}).get("passed") is not True):
        raise ValueError("Passing initializer comparison required")
    runs=record["input_runs"]
    if len(runs)!=3:raise ValueError("Three retained audit dependencies required")
    for item in runs:checked(item,MAIN/".thesis-build/dev-runs")
    result,entries=compare_runs(*(Path(item["path"]).parent for item in runs))
    if result!=record["comparison"] or not result["passed"]:raise ValueError("u0 audit dependency invalid")
    return record,entries


def load_verified_u0(run_path,source_id,source_rgb8_sha256,expected_core):
    """Compatibility alias with an additional explicit core guard."""
    value,provenance=load_development_bridge(run_path,source_id,source_rgb8_sha256)
    if provenance["initializer_scientific_core_sha256"]!=expected_core:
        raise ValueError("Initializer core differs")
    return value,provenance


def load_development_bridge(run_path,source_id,source_rgb8_sha256):
    """Re-audit proof, current scientific files/runtime, then original dev loader.

    Caller has configured deterministic policy and initialized its local CUDA
    runtime already. This loader never initializes CUDA and does not load models.
    """
    from scripts import m1_dual_latent as original
    from m1_latent_reconstruction import IDS
    if type(source_id) is not int or source_id not in IDS:raise ValueError("Unreserved development bridge source")
    run_path=Path(run_path).resolve()
    if not run_path.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):
        raise ValueError("Development bridge root required")
    record=json.loads((run_path/"run.json").read_text(encoding="utf-8"))
    if (record.get("schema")!=VERSION or record.get("stage")!="compare" or
            record.get("outcome")!="completed"):
        if not (record.get("schema")==VERSION and record.get("stage")=="initialize" and record.get("outcome")=="completed"):
            raise ValueError("Verified development bridge required")
    if record["stage"]=="compare":proof,entries=verify_audit(run_path)
    else:
        proof_path=checked(record["audit_proof"],MAIN/".thesis-build/dev-runs")
        proof,entries=verify_audit(proof_path.parent)
        load_run(run_path,"initialize")
    audited=entries[0][1]
    if record["stage"]=="initialize":
        for field in ("scientific_files","scientific_core_sha256","deterministic_execution","environment","device_identity","assets"):
            if record[field]!=audited[field]:raise ValueError("Fresh bridge differs from audited identity: "+field)
    current=original.require_committed(scientific_paths())
    if current!=audited["scientific_files"]:raise ValueError("Current initializer scientific core differs from audit")
    bridge=record["u0_bridge"]
    checked(bridge["latent"],run_path);checked(bridge["png"],run_path)
    import m1_source_initialization as adapter
    expected_checkpoint=(entries[2][1]["checkpoints"][-1] if record["stage"]=="compare" else record["checkpoints"][-1])
    if bridge["initializer_state"]!=expected_checkpoint:raise ValueError("Bridge state is not this source endpoint")
    state=adapter.load_checkpoint(checked(bridge["initializer_state"],MAIN/".thesis-build/dev-runs"))
    adapter._validate_payload(state,state["identity"],state["target_sha256"],state["runtime"])
    if state["step"]!=200:raise ValueError("Bridge must contain exactly200 completed updates")
    audited_state=adapter.load_checkpoint(checked(entries[0][1]["checkpoints"][-1],entries[0][0]))
    if state["runtime"]!=audited_state["runtime"]:raise ValueError("Bridge runtime differs from audited initializer")
    import torch
    import types
    if not torch.cuda.is_initialized():raise ValueError("Caller must initialize configured CUDA runtime before bridge import")
    if adapter._runtime(types.SimpleNamespace(device=torch.device("cuda",torch.cuda.current_device())))!=state["runtime"]:
        raise ValueError("Current initializer runtime differs from audit")
    if (bridge["source_id"]!=source_id or state["identity"]["source_id"]!=source_id or
            state["identity"]["source_rgb8_sha256"]!=source_rgb8_sha256 or
            state["identity"]["scientific_core_sha256"]!=audited["scientific_core_sha256"] or
            state["identity"]["model_sha256"]!=audited["identity"]["model_sha256"]):
        raise ValueError("Bridge source/model/core identity differs")
    lock=json.loads((ROOT/"research/a6-candidate-model-assets.json").read_text())
    assets=[v for v in lock["files"] if v["path"].startswith("sd15-fp16/vae/")]
    if assets!=audited["assets"]:raise ValueError("Current VAE asset lock differs from audit")
    for item in assets:
        path=MAIN/".thesis-build/assets/a6"/item["path"]
        if path.stat().st_size!=item["size_bytes"] or sha(path)!=item["sha256"]:raise ValueError("Current VAE asset bytes differ")
    payload=torch.load(checked(bridge["latent"],run_path),map_location="cpu",weights_only=True)
    if not torch.equal(payload["z"],state["z"]):raise ValueError("Bridge no longer equals verified endpoint")
    value,provenance=original.reconstruction_latent(run_path,source_id,200,source_rgb8_sha256)
    provenance.update(initializer_kind="verified deterministic original200",
        initializer_scientific_core_sha256=audited["scientific_core_sha256"],
        audit_proof=receipt((run_path if record["stage"]=="compare" else Path(record["audit_proof"]["path"]).parent)/"run.json"),
        full_initializer_state=bridge["initializer_state"],embedding_optimizer="fresh independent Adam")
    return value,provenance


def rss_bytes():
    """Windows working set; no optional monitoring dependency."""
    if os.name!="nt":raise RuntimeError("This bounded audit worker requires Windows")
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)]+[
            (n,ctypes.c_size_t) for n in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    kernel=ctypes.WinDLL("kernel32",use_last_error=True);psapi=ctypes.WinDLL("psapi",use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counters),counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.WorkingSetSize)


def run(stage,output,reference_dir=None,prefix_dir=None,resume_dir=None,source_id=1675,audit_dir=None):
    cfg=config();output=Path(output).resolve()
    if not output.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):
        raise ValueError("Fresh MAIN development run destination required")
    from scripts import m1_dual_latent as original
    if stage!="initialize" and source_id!=1675:raise ValueError("Audit phases require fixed source1675")
    hashes=original.require_committed(scientific_paths())
    output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    record={"schema":VERSION,"stage":stage,"data_split":"development","audit_config":cfg,
        "command":sys.argv,"commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "scientific_files":hashes,"scientific_core_sha256":hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),
        "process_id":os.getpid(),"outcome":"started","checkpoints":[],"duration_seconds":0,
        "gate":None,"label":"Initializer execution audit; no watermark or held-out evidence"}
    write(output/"run.json",record)
    def persist():
        record["duration_seconds"]=time.monotonic()-started;write(output/"run.json",record)
    try:
        if stage=="compare":
            paths=[Path(p).resolve()/"run.json" for p in (reference_dir,prefix_dir,resume_dir)]
            if any(not p.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()) for p in paths):
                raise ValueError("Audit comparison dependencies escape development root")
            record["input_runs"]=[receipt(p) for p in paths]
            result,entries=compare_runs(reference_dir,prefix_dir,resume_dir)
            record["comparison"]=result
            if not result["passed"]:record["outcome"]="parity_failed"
            else:
                from m1_latent_reconstruction import CONFIG as original_config
                record["config"]=original_config
                export_bridge(output,record,entries);record["outcome"]="completed"
            persist();return 0 if record["outcome"]=="completed" else 1
        import m1_terminal_repeatability as deterministic
        record["deterministic_execution"]=deterministic.configure()
        from three_threat_models import block_network
        block_network()
        import numpy as np
        import torch
        from diffusers import AutoencoderKL
        from PIL import Image
        import m1_source_initialization as adapter
        from m1_latent_reconstruction import cases_for,quality
        cohort=json.loads((ROOT/cfg["cohort"]).read_text(encoding="utf-8"))
        cases=cases_for(cohort)
        if type(source_id) is not int or source_id not in {v["id"] for v in cases}:raise ValueError("Unreserved source")
        case=next(c for c in cases if c["id"]==source_id)
        source,native_shape=original.source_rgb(case)
        canonical=output/f"source{source_id}.png"
        with canonical.open("xb") as f:Image.fromarray(source).save(f,format="PNG")
        source_hash=hashlib.sha256(source.tobytes()).hexdigest()
        record["source"]={"id":source_id,"path":case["path"],"raw_sha256":case["sha256"],
                          "native_shape":native_shape,"rgb8_sha256":source_hash,"canonical_png":receipt(canonical)}
        lock=json.loads((ROOT/"research/a6-candidate-model-assets.json").read_text())
        assets=[v for v in lock["files"] if v["path"].startswith("sd15-fp16/vae/")]
        if len(assets)!=2:raise ValueError("Exact VAE config/weights lock required")
        for item in assets:
            path=MAIN/".thesis-build/assets/a6"/item["path"]
            if path.stat().st_size!=item["size_bytes"] or sha(path)!=item["sha256"]:raise ValueError("VAE asset mismatch")
        record["assets"]=assets
        record["identity"]={"source_id":source_id,"source_rgb8_sha256":source_hash,
            "model_sha256":hashlib.sha256(json.dumps(assets,sort_keys=True).encode()).hexdigest(),
            "scientific_core_sha256":record["scientific_core_sha256"],"phase_seed":0}
        if not torch.cuda.is_available():raise RuntimeError("CUDA unavailable; no CPU substitution")
        torch.cuda.init()
        free,total=torch.cuda.mem_get_info();cap=min(cfg["gpu_budget_bytes"],int(free)-cfg["gpu_reserve_bytes"])
        if cap<=0:raise RuntimeError("Insufficient GPU headroom")
        torch.cuda.set_per_process_memory_fraction(cap/int(total))
        record["gpu_budget"]={"initial_free_bytes":int(free),"total_bytes":int(total),"effective_cap_bytes":cap}
        properties=torch.cuda.get_device_properties(0)
        record["device_identity"]={"name":properties.name,"capability":[properties.major,properties.minor],
            "total_bytes":properties.total_memory,
            "driver_inventory":subprocess.check_output(["nvidia-smi","--query-gpu=index,name,driver_version,pci.bus_id","--format=csv,noheader"],text=True).strip()}
        record["environment"]={"python":sys.version,**{p:importlib.metadata.version(p) for p in
            ("torch","numpy","Pillow","diffusers","scipy")},"cuda":torch.version.cuda,
            "cudnn":torch.backends.cudnn.version(),"threads":torch.get_num_threads(),
            "fill_uninitialized_memory":bool(torch.utils.deterministic.fill_uninitialized_memory)}
        persist()
        vae=AutoencoderKL.from_pretrained(MAIN/".thesis-build/assets/a6/sd15-fp16/vae",variant="fp16",
            use_safetensors=True,local_files_only=True,torch_dtype=torch.float32).eval().requires_grad_(False).to("cuda")
        record["model_load_seconds"]=time.monotonic()-started
        record["placement"]="only pinned frozen FP32 VAE on GPU; no UNet/CLIP/LPIPS/pipeline"
        target=torch.from_numpy(source).permute(2,0,1).unsqueeze(0).float().to("cuda")/255
        torch.cuda.reset_peak_memory_stats()
        def check():
            elapsed=time.monotonic()-started
            ram=rss_bytes();disk=sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
            record["peak_rss_bytes"]=max(record.get("peak_rss_bytes",0),ram)
            record["artifact_bytes"]=disk;record["peak_allocated_bytes"]=torch.cuda.max_memory_allocated()
            if (elapsed>cfg["cooperative_seconds_cap"] or ram>cfg["ram_budget_bytes"] or
                    disk>cfg["artifact_budget_bytes"] or torch.cuda.memory_allocated()>cap):
                raise RuntimeError("Cooperative resource cap exceeded; saved checkpoints retained")
        def checkpoint_stage(session):
            if session.step%10==0:
                path=output/f"state{session.step:03d}.pt";save_payload(path,session.state_dict())
                record["checkpoints"].append({"step":session.step,**receipt(path)})
                with (output/"images.jsonl").open("a",encoding="utf-8") as f:
                    f.write(json.dumps({"phase":"checkpoint","step":session.step,"seconds":time.monotonic()-started})+"\n")
                persist()
            check()
        if stage=="literal":
            seed_phase();session=LiteralReference(target,vae,record["identity"])
            session.advance(checkpoint_stage)
        elif stage=="adapter-prefix":
            seed_phase();session=adapter.ReconstructionSession(target,vae,record["identity"])
            checkpoint_stage(session);session.advance(100,on_update=checkpoint_stage)
        elif stage=="adapter-resume":
            previous,prior=load_run(prefix_dir,"adapter-prefix")
            for field in ("scientific_files","scientific_core_sha256","deterministic_execution","environment","device_identity","assets","identity"):
                if prior[field]!=record[field]:raise ValueError("Resume dependency identity differs: "+field)
            cp=prior["checkpoints"][-1]
            record["resume_from"]=receipt(previous/"run.json");record["resume_checkpoint"]=cp
            session=adapter.ReconstructionSession(target,vae,record["identity"],resume=adapter.load_checkpoint(checked(cp,previous)))
            session.advance(200,on_update=checkpoint_stage)
        elif stage=="initialize":
            proof,entries=verify_audit(audit_dir);audited=entries[0][1]
            for field in ("scientific_files","scientific_core_sha256","deterministic_execution","environment","device_identity","assets"):
                if record[field]!=audited[field]:raise ValueError("Fresh initialization differs from audited core/runtime: "+field)
            seed_phase();session=adapter.ReconstructionSession(target,vae,record["identity"])
            audited_state=adapter.load_checkpoint(checked(audited["checkpoints"][0],entries[0][0]))
            if session.runtime!=audited_state["runtime"]:raise ValueError("Fresh initialization runtime differs from audit")
            checkpoint_stage(session);session.advance(200,on_update=checkpoint_stage)
            from m1_latent_reconstruction import CONFIG as original_config
            record["config"]=original_config
            bridge_from_state(output,record,session.state_dict(),record["checkpoints"][-1],receipt(Path(audit_dir)/"run.json"))
        else:raise ValueError("Unknown stage")
        check()
        record["observation_quality"]={str(s):quality(source,v["rgb8"].numpy()) for s,v in session.observations.items()}
        record["completed_updates"]=session.step;record["runtime"]=session.runtime
        record["outcome"]="completed"
    except Exception as error:
        record.update(outcome="operational_failed",error=repr(error),traceback=traceback.format_exc())
    finally:
        persist()
    return 0 if record["outcome"]=="completed" else 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage",choices=STAGES,required=True);p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--reference-dir",type=Path);p.add_argument("--prefix-dir",type=Path);p.add_argument("--resume-dir",type=Path)
    p.add_argument("--source-id",type=int,default=1675);p.add_argument("--audit-dir",type=Path)
    args=p.parse_args()
    if args.stage=="compare" and any(getattr(args,n) is None for n in ("reference_dir","prefix_dir","resume_dir")):
        p.error("compare requires reference/prefix/resume directories")
    if args.stage=="adapter-resume" and args.prefix_dir is None:p.error("adapter-resume requires prefix directory")
    if args.stage=="initialize" and args.audit_dir is None:p.error("initialize requires passing audit directory")
    return run(args.stage,args.output_dir,args.reference_dir,args.prefix_dir,args.resume_dir,args.source_id,args.audit_dir)


if __name__=="__main__":raise SystemExit(main())
