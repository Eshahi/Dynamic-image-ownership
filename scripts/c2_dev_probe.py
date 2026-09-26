"""Offline development-only CLIP cases; entrypoint requires reviewed runner approval."""
import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import socket
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RAW_ROOT=Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw")
CHECKPOINT=Path("/mnt/w/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6/clip/ViT-B-32.pt")


def sha(raw): return hashlib.sha256(raw).hexdigest()
def checked(path,digest):
    path=Path(path).absolute()
    if any(p.is_symlink() or p.is_junction() for p in (path,*path.parents)):
        raise ValueError("linked input path")
    raw=path.read_bytes()
    if sha(raw)!=digest: raise ValueError("input hash mismatch:"+path.name)
    return raw


def prepare(manifest):
    # Every reviewed module/config is bound by the runner manifest and checked
    # again in the Linux runtime before importing Torch or loading a checkpoint.
    entries={item["path"]:item["sha256"] for item in manifest["inputs"]}
    required={"scripts/c2_dev_probe.py","src/signatures/semantic.py","src/signatures/owner.py",
              "src/data/preprocess.py","scripts/a6_clip_visual.py","configs/semantic-dev.json",
              "configs/data.json","data/splits.csv",
              "data/b4-admission-20260926/source-manifest.csv",
              "data/b4-admission-20260926/development-reservation.json"}
    if not required<=set(entries): raise ValueError("execution manifest misses code or input bindings")
    snapshots={name:checked(ROOT/name,digest) for name,digest in entries.items()}
    config=json.loads(snapshots["configs/semantic-dev.json"])
    if (config["schema_version"]!="c2-fixed-development-probe-v1" or config["projection_seed"]!="0"*64
            or config["image_count"]!=32 or config["device"]!="cuda"
            or config["benign_transform"]!={"format":"JPEG","quality":95,"subsampling":0,"optimize":False,"progressive":False}
            or manifest["experiment_id"]!="c2-semantic-development-v1" or manifest["task_id"]!="C2"
            or manifest["execution_target"]!="local" or manifest["seeds"]!=[0]):
        raise ValueError("unexpected fixed development recipe")
    for key,pin in (("source_manifest","manifest_sha256"),("development_ids","development_ids_sha256"),
                    ("splits","splits_sha256")):
        if sha(snapshots[config[key]])!=config[pin]: raise ValueError("config/manifest pin mismatch")
    source_rows=list(csv.DictReader(io.StringIO(snapshots[config["source_manifest"]].decode())))
    split_rows=list(csv.DictReader(io.StringIO(snapshots[config["splits"]].decode())))
    uid=lambda r: ":".join(r[k] for k in ("domain","release_id","source_split","source_id"))
    source={uid(r):r for r in source_rows};splits={r["source_uid"]:r for r in split_rows}
    reserved=json.loads(snapshots[config["development_ids"]])["images"]
    if len(reserved)!=32 or len({uid(r) for r in reserved})!=32: raise ValueError("development reservation mismatch")
    selected=[]
    for row in sorted(reserved,key=uid):
        name=uid(row);split=splits[name];original=source[name]
        if (split["study_split"]!="development" or split["canonical_status"]!="canonical_pass"
                or split["raw_sha256"]!=row["raw_sha256"] or original["raw_sha256"]!=row["raw_sha256"]
                or original["relative_path"]!=row["relative_path"]):
            raise ValueError("not a pinned admitted development source")
        path=RAW_ROOT/row["relative_path"]
        if ".." in Path(row["relative_path"]).parts or not path.absolute().is_relative_to(RAW_ROOT):
            raise ValueError("source outside raw root")
        selected.append((name,row,split,checked(path,row["raw_sha256"])))
    return config,sha(snapshots["configs/semantic-dev.json"]),selected


def distances(one,two,code_one,code_two,ws_one,ws_two):
    return {"feature_distance":1-sum(a*b for a,b in zip(one,two)),
            "key_distance":sum((a^b).bit_count() for a,b in zip(ws_one,ws_two)),
            "semantic_code_distance":(int.from_bytes(code_one.packed,"little")^int.from_bytes(code_two.packed,"little")).bit_count()}


def main(manifest_path,output):
    manifest=json.loads(manifest_path.read_bytes());config,config_hash,selected=prepare(manifest)
    def blocked(*args,**kwargs): raise RuntimeError("network forbidden in offline C2 probe")
    socket.socket.connect=blocked;socket.socket.connect_ex=blocked;socket.create_connection=blocked
    expected={"torch":"2.12.1+cu130","torchvision":"0.27.1+cu130","pillow":"12.3.0","numpy":"2.5.3","clip":"1.0"}
    if (sys.version_info[:3]!=(3,14,4) or any(importlib.metadata.version(k)!=v for k,v in expected.items())):
        raise ValueError("scientific runtime differs from fixed WSL profile")
    import numpy as np
    import torch
    from PIL import Image
    from src.data.preprocess import decode_source,load_config,pixel_sha
    from src.signatures.semantic import FeatureCache,PinnedClipEncoder,derive_ws
    output=Path(output);examples=[];failures=[];originals={};started=time.monotonic()
    data_config,_=load_config(ROOT/config["data_config"])
    # Keep allocator below a declared 4GiB ceiling; runner also checks free VRAM.
    total=torch.cuda.get_device_properties(0).total_memory
    torch.cuda.set_per_process_memory_fraction(min(1.0,4096*1024**2/total),0)
    torch.cuda.reset_peak_memory_stats()
    encoder=PinnedClipEncoder.from_checkpoint(CHECKPOINT,device="cuda")
    cache=FeatureCache(output/"checkpoints/feature-cache")
    seed=bytes.fromhex(config["projection_seed"])
    for name,row,split,raw in selected:
        try:
            pixels,receipt=decode_source(raw,data_config)
            if pixel_sha(pixels)!=split["canonical_pixel_sha256"]:
                raise ValueError("canonical source digest differs from locked B4 inventory")
            first=encoder.extract_features(pixels,cache);second=encoder.extract_features(pixels)
            if encoder.extract_features(pixels,cache)!=first: raise ValueError("cached feature mismatch")
            q1,ws1=derive_ws(first,seed,config["owner_id"]);q2,ws2=derive_ws(second,seed,config["owner_id"])
            originals[name]=(first,q1,ws1,row["domain"])
            examples.append({"image_id":name,"transform":"same_image_uncached_repeat","config_hash":config_hash,
                             **distances(first,second,q1,q2,ws1,ws2),"exact_features_equal":first==second,
                             "min_absolute_projection_margin":min(abs(v) for v in q1.projections)})
            with io.BytesIO() as buffer:
                Image.fromarray(pixels).save(buffer,**config["benign_transform"])
                with Image.open(io.BytesIO(buffer.getvalue())) as image:
                    image.load();changed=np.array(image,dtype=np.uint8,copy=True)
            feature=encoder.extract_features(changed,cache);q,ws=derive_ws(feature,seed,config["owner_id"])
            examples.append({"image_id":name,"transform":"jpeg_quality95_subsampling0","config_hash":config_hash,
                             **distances(first,feature,q1,q,ws1,ws),
                             "min_absolute_projection_margin":min(abs(v) for v in q.projections)})
        except Exception as exc:
            failures.append({"image_id":name,"phase":"source_and_fixed_cases","error_type":type(exc).__name__,
                             "error":str(exc)[:250]})
    # Preserve the original prospective pair order even when extraction fails.
    planned=defaultdict(list)
    for name,row,_,_ in selected: planned[row["domain"]].append(name)
    for domain,names in planned.items():
        for i,name in enumerate(names):
            other=names[(i+1)%len(names)]
            if name not in originals or other not in originals:
                failures.append({"image_id":name,"phase":"different_content","paired_image_id":other,
                                 "error_type":"MissingPlannedFeature"});continue
            one,q1,ws1,_=originals[name];two,q2,ws2,_=originals[other]
            examples.append({"image_id":name,"paired_image_id":other,"transform":"different_content",
                             "config_hash":config_hash,**distances(one,two,q1,q2,ws1,ws2)})
    failed=bool(failures) or len(examples)!=96 or any(r["semantic_code_distance"] for r in examples if r["transform"]=="same_image_uncached_repeat")
    report={"schema_version":"c2-development-examples-v1","status":"failed" if failed else "completed",
            "config_hash":config_hash,"examples":examples,"failures":failures,"planned_cases":96,
            "model_identity":encoder.identity,"elapsed_seconds":time.monotonic()-started,
            "peak_torch_allocated_bytes":torch.cuda.max_memory_allocated(),
            "development_only":True,"scientific_method_success":False,"no_threshold_selection":True}
    target=output/"outputs/semantic-examples.json"
    with target.open("x",encoding="utf-8") as handle: json.dump(report,handle,sort_keys=True,indent=2,allow_nan=False)
    return 1 if failed else 0


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True,type=Path);parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args();raise SystemExit(main(args.manifest,args.output_dir))
