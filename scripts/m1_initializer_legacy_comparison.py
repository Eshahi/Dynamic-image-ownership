"""CPU-only descriptive original200 versus retained legacy initializer comparison.

No decoding, model evaluation, closeness tolerance, reuse decision or gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parents[1]
MAIN=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
for p in (ROOT,ROOT/"scripts"):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
VERSION="m1-initializer-legacy-descriptive-comparison-v1"
ENDPOINTS=(0,200)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda:stream.read(1024**2),b""):h.update(data)
    return h.hexdigest()


def read(path):
    def invalid(value):raise ValueError("Nonfinite JSON: "+value)
    return json.loads(Path(path).read_text(encoding="utf-8"),parse_constant=invalid)


def receipt(path):
    path=Path(path).resolve()
    return dict(path=str(path),sha256=sha(path),size_bytes=path.stat().st_size)


def save(path,value):
    path=Path(path); temporary=path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    temporary.replace(path)


def development_path(path):
    path=Path(path).resolve()
    if not path.is_relative_to((MAIN/".thesis-build/dev-runs").resolve()):
        raise ValueError("MAIN retained development directory required")
    return path


def latent_difference(new,legacy):
    """Exact flags + float64 arithmetic only; no fitted/rounded tolerance."""
    import torch
    for value in (new,legacy):
        if not isinstance(value,torch.Tensor) or value.device.type!="cpu" or not value.is_floating_point() or not bool(torch.isfinite(value).all()):
            raise ValueError("Finite floating CPU latent required")
    if new.shape!=legacy.shape or new.numel()==0:raise ValueError("Equal nonempty latent shapes required")
    delta=new.double()-legacy.double()
    byte_equal=(new.dtype==legacy.dtype and torch.equal(new.contiguous().view(torch.uint8),legacy.contiguous().view(torch.uint8)))
    numbers=dict(l2=float(torch.linalg.vector_norm(delta)),rms=float(torch.sqrt(delta.square().mean())),
        max_abs=float(delta.abs().max()),signed_min=float(delta.min()),signed_max=float(delta.max()))
    if not all(math.isfinite(v) for v in numbers.values()):raise ValueError("Nonfinite float64 difference arithmetic")
    return dict(shape=list(new.shape),elements=new.numel(),new_dtype=str(new.dtype),legacy_dtype=str(legacy.dtype),
        dtype_equal=new.dtype==legacy.dtype,values_exact=bool(torch.equal(new,legacy)),bytes_exact=bool(byte_equal),
        delta_direction="new-minus-legacy",arithmetic_dtype="float64",
        **numbers,closeness_tolerance=None,reuse_claim=False)


def metric_difference(new,legacy):
    def value(item):
        return item if type(item) in (int,float) and math.isfinite(item) else None
    a,b=value(new),value(legacy)
    difference=a-b if a is not None and b is not None else None
    if difference is not None and not math.isfinite(difference):difference=None
    return dict(new_recorded=a,legacy_recorded=b,new_minus_legacy=difference,
                new_invalid_repr=repr(new) if new is not None and a is None else None,
                legacy_invalid_repr=repr(legacy) if legacy is not None and b is None else None,
                reason=None if difference is not None else "missing_invalid_or_nonfinite_recorded_metric_or_difference")


def case(record,source_id):
    rows=[r for r in record.get("cases",[]) if r.get("id")==source_id]
    if len(rows)!=1 or rows[0].get("outcome")!="completed":raise ValueError("Unique completed legacy case required")
    return rows[0]


def source_join(source_id,new_source,legacy_case):
    for key in ("raw_sha256","native_shape"):
        if new_source.get(key)!=legacy_case.get(key) or new_source.get(key) is None:
            raise ValueError("Source acquisition identity differs: "+key)
    if new_source.get("id")!=source_id or legacy_case.get("id")!=source_id:
        raise ValueError("Source ID differs")
    if new_source.get("rgb8_sha256")!=legacy_case.get("source_rgb8_sha256") or not new_source.get("rgb8_sha256"):
        raise ValueError("Canonical RGB8 input differs")
    return dict(source_id=source_id,raw_sha256=new_source["raw_sha256"],native_shape=new_source["native_shape"],
                source_rgb8_sha256=new_source["rgb8_sha256"],same_canonical_input=True,
                source_raw_bytes_opened=False)


def new_endpoints(bridge_dir,source_id):
    """Reuse complete audit/state validators without load_development_bridge's GPU-runtime check."""
    import m1_source_initialization_audit as audit
    import m1_source_initialization as adapter
    import m1_dual_latent as original
    record=read(bridge_dir/"run.json")
    if record.get("schema")!=audit.VERSION or record.get("data_split")!="development" or record.get("outcome")!="completed":
        raise ValueError("Completed new development initializer bridge required")
    if record.get("stage")=="compare":
        proof,entries=audit.verify_audit(bridge_dir)
        state_dir,state_record=entries[0]  # independent literal trajectory, exact audited against adapters
        if source_id!=state_record["identity"]["source_id"]:raise ValueError("Audit source differs")
        proof_path=bridge_dir/"run.json"
    elif record.get("stage")=="initialize":
        proof_path=audit.checked(record["audit_proof"],MAIN/".thesis-build/dev-runs")
        proof,entries=audit.verify_audit(proof_path.parent)
        state_dir,state_record=audit.load_run(bridge_dir,"initialize")
        for field in ("scientific_files","scientific_core_sha256","deterministic_execution","environment","device_identity","assets"):
            if state_record[field]!=entries[0][1][field]:raise ValueError("Fresh initializer/audit identity differs: "+field)
    else:raise ValueError("New bridge must be verified compare or fresh initialize stage")
    source=state_record["source"]
    if source["id"]!=source_id or state_record["identity"]["source_id"]!=source_id:
        raise ValueError("New source differs")
    bridge=record["u0_bridge"]
    if bridge.get("source_id")!=source_id or bridge.get("schema")!="m1-verified-original200-u0-bridge-v1":
        raise ValueError("New bridge identity differs")
    for key in ("latent","png"):audit.checked(bridge[key],bridge_dir)
    endpoint_state_path=audit.checked(bridge["initializer_state"],MAIN/".thesis-build/dev-runs")
    states={};receipts={}
    for step in ENDPOINTS:
        matches=[r for r in state_record["checkpoints"] if r["step"]==step]
        if len(matches)!=1:raise ValueError("Missing/duplicate new endpoint")
        path=audit.checked(matches[0],state_dir)
        payload=adapter.load_checkpoint(path)
        adapter._validate_payload(payload,payload["identity"],payload["target_sha256"],payload["runtime"])
        if payload["step"]!=step or payload["identity"]!=state_record["identity"] or tuple(payload["z"].shape)!=(1,4,64,64):
            raise ValueError("New checkpoint source/step/shape differs")
        states[step]=payload;receipts[str(step)]=receipt(path)
    endpoint=adapter.load_checkpoint(endpoint_state_path)
    adapter._validate_payload(endpoint,endpoint["identity"],endpoint["target_sha256"],endpoint["runtime"])
    if endpoint["step"]!=200 or endpoint["identity"]!=states[200]["identity"] or adapter.digest(endpoint["z"])!=adapter.digest(states[200]["z"]):
        raise ValueError("New bridge is not audited source endpoint")
    import torch
    value,bridge_receipt=original.reconstruction_latent(bridge_dir,source_id,200,source["rgb8_sha256"])
    if not torch.equal(value,states[200]["z"].float()):raise ValueError("New exported latent differs from verified state")
    return states,source,state_record,dict(run=receipt(bridge_dir/"run.json"),audit_proof=receipt(proof_path),
        input_audit_runs=proof["input_runs"],state_run=receipt(state_dir/"run.json"),states=receipts,
        canonical_png=state_record["source"]["canonical_png"],bridge=bridge,original_loader=bridge_receipt,
        validation="CPU audit proof/state validation; current GPU runtime and model bytes not loaded or revalidated")


def compare(source_id,new_bridge,legacy_dir,on_row=None):
    import torch
    import m1_dual_latent as original
    from m1_latent_reconstruction import IDS
    if type(source_id) is not int or source_id not in IDS:raise ValueError("Reserved development ID required")
    if torch.cuda.is_initialized():raise ValueError("Fresh CPU-only analyzer process required")
    new_bridge=development_path(new_bridge);legacy_dir=development_path(legacy_dir)
    if new_bridge==legacy_dir:raise ValueError("Distinct new/legacy inputs required")
    states,new_source,new_run,new_receipts=new_endpoints(new_bridge,source_id)
    legacy_run=read(legacy_dir/"run.json")
    if legacy_run.get("data_split")!="development":raise ValueError("Legacy development run required")
    legacy_case=case(legacy_run,source_id)
    identity=source_join(source_id,new_source,legacy_case)
    rows=[];legacy_receipts={}
    for step in ENDPOINTS:
        loaded,prov=original.reconstruction_latent(legacy_dir,source_id,step,identity["source_rgb8_sha256"])
        cp=prov["checkpoint_receipt"]
        raw= torch.load(prov["path"],map_location="cpu",weights_only=True)["z"]
        if sha(prov["path"])!=prov["sha256"] or not torch.equal(loaded,raw.float()):raise ValueError("Legacy checkpoint changed during load")
        png=legacy_dir/f"{source_id}-step{step:03d}.png"
        if sha(png)!=cp["png_sha256"]:raise ValueError("Legacy saved RGB8 artifact hash differs")
        legacy_receipts[str(step)]=dict(latent=prov,png=receipt(png))
        observation=states[step]["observations"][step]
        q=new_run.get("observation_quality",{}).get(str(step),{})
        fields={k:metric_difference(observation.get(k),cp.get(k)) for k in ("objective_float_mse","latent_displacement_l2")}
        fields.update({k:metric_difference(q.get(k),cp.get(k)) for k in ("mse_rgb8","psnr_db","ssim_rgb","lpips")})
        rows.append(dict(step=step,outcome="completed",latent=latent_difference(states[step]["z"],raw),
            recorded_metrics=fields,new_psnr_infinite=q.get("psnr_infinite"),legacy_psnr_infinite=cp.get("psnr_infinite"),
            quality_computed_now=False,new_observation_rgb8_digest=hashlib.sha256(observation["rgb8"].numpy().tobytes()).hexdigest()))
        if on_row is not None:on_row(rows[-1])
    if torch.cuda.is_initialized():raise ValueError("Unexpected CUDA initialization")
    return dict(source=identity,comparisons=rows,input_outcomes=dict(new=new_run["outcome"],legacy=legacy_run.get("outcome")),inputs=dict(new=new_receipts,legacy_run=receipt(legacy_dir/"run.json"),legacy=legacy_receipts),
        configurations=dict(new=new_run.get("audit_config"),new_initializer_config=states[200]["config"],
            new_identity=states[200]["identity"],new_assets=new_run.get("assets"),
            new_scientific_files=new_run.get("scientific_files"),new_runtime=new_run.get("runtime"),legacy=legacy_run.get("config"),
            legacy_environment=legacy_run.get("environment")),scientific_interpretation="descriptive trajectory difference only",
        tolerance=None,reuse_claim=False,gate=None,human_verdict=None,cuda_initialized=False)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id",required=True,type=int)
    parser.add_argument("--new-bridge",required=True)
    parser.add_argument("--legacy-dir",required=True)
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args(argv)
    output=development_path(args.output_dir)
    if output.exists():raise FileExistsError("Fresh output directory required")
    output.mkdir(parents=True)
    started=time.monotonic()
    record=dict(schema=VERSION,data_split="development",command=[sys.executable,*sys.argv],source_id=args.source_id,
        config=vars(args),outcome="started",duration_seconds=0.,comparisons=[dict(step=s,outcome="planned") for s in ENDPOINTS],
        errors=[],gate=None,reuse_claim=False,tolerance=None,human_verdict=None)
    save(output/"run.json",record)
    try:
        import m1_dual_latent as original
        paths=[Path(__file__),ROOT/"scripts/m1_dual_latent.py",ROOT/"scripts/m1_source_initialization_audit.py",ROOT/"scripts/m1_source_initialization.py"]
        record["committed_files"]=original.require_committed(paths)
        record["commit"]=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
        import torch
        record["environment"]=dict(python=sys.version,torch=str(torch.__version__),device="cpu")
        def retain(row):
            record["comparisons"]=[row if old["step"]==row["step"] else old for old in record["comparisons"]]
            save(output/"run.json",record)
        result=compare(args.source_id,args.new_bridge,args.legacy_dir,on_row=retain)
        record.update(result,outcome="completed")
    except Exception as error:
        record.update(outcome="incomplete",errors=[repr(error)],traceback=traceback.format_exc())
        record["comparisons"]=[dict(row,outcome="incomplete",reason=repr(error)) if row["outcome"]!="completed" else row for row in record["comparisons"]]
    record["duration_seconds"]=time.monotonic()-started
    save(output/"comparison.json",record)
    record["outputs"]={"comparison.json":sha(output/"comparison.json")}
    save(output/"run.json",record)
    return 0 if record["outcome"]=="completed" else 1

if __name__=="__main__":raise SystemExit(main())
