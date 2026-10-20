"""Build a pinned stage-2 download plan from research metadata; text only now."""
from pathlib import Path
import hashlib
import urllib.request
from encoder_transfer_test import ROOT,read,write

DEST=ROOT/"research/encoder-transfer-20261019"
CACHE=Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/transfer-integration")


def build():
    CACHE.mkdir(parents=True,exist_ok=True)
    files=[]
    t5=DEST/"design-research/T5-pipeline"
    for x in read(t5/"sdxl-download-plan.json")["files"]:
        files.append(dict(path="sdxl/"+x["path"],url=x["url"],sha256=x["sha256"],size_bytes=x["size_bytes"],license="CreativeML Open RAIL++-M"))
    for x in read(t5/"sd15-lock-source-map.json")["files"]:
        files.append(dict(path="a6/"+x["path"],url=x["url"],sha256=x["expected_sha256"],size_bytes=x["size_bytes"],license="CreativeML OpenRAIL-M"))
    lock=read(ROOT/"research/a6-candidate-model-assets.json")["files"]
    for x in lock[:2]:
        url=(f'https://openaipublic.azureedge.net/clip/models/{x["sha256"]}/ViT-B-32.pt' if x["path"].startswith("clip/") else "https://download.pytorch.org/models/alexnet-owt-7be5be79.pth")
        files.append({**x,"path":"a6/"+x["path"],"url":url,"license":"MIT (CLIP) / BSD-3-Clause (torchvision)"})
    t3=read(DEST/"design-research/T3-baseline-fidelity/manifest.json")
    text_receipts=[]
    prefixes={"stabilityai/sd-turbo":"vine/sd-turbo","Shilin-LU/VINE-R-Enc":"vine/encoder","Shilin-LU/VINE-R-Dec":"vine/decoder"}
    for x in t3["approved_core_weight_plan"]:
        sha=x["sha256_remote_lfs"]
        size=x["bytes_remote"]
        if sha is None:
            # The only stage-1 network requests here are allowlisted small text.
            if size>2_000_000 or not x["path"].endswith((".json",".txt")):
                raise ValueError("Refusing non-text or large stage1 fetch")
            target=CACHE/(x["repo"].replace("/","_")+"_"+x["path"].replace("/","_"))
            if not target.exists():
                with urllib.request.urlopen(x["url"],timeout=60) as response:
                    content=response.read(2_000_001)
                if len(content)!=size:
                    raise ValueError("Small metadata size mismatch")
                target.write_bytes(content)
            sha=hashlib.sha256(target.read_bytes()).hexdigest()
            text_receipts.append(dict(url=x["url"],cache_path=str(target),bytes=size,sha256=sha))
        files.append(dict(path=prefixes[x["repo"]]+"/"+x["path"],url=x["url"],sha256=sha,size_bytes=size,
                          license="VINE author research code terms / HF card MIT; SD-Turbo Community License 2024"))
    wam=read(ROOT/"research/journal-upgrade-20261009/wam-download.json")
    for x,name in zip(wam["files"],("source.zip","wam_mit.pth")):
        files.append(dict(path="wam/"+name,url=x["url"],sha256=x["sha256"],size_bytes=x["bytes"],license="MIT"))
    patches={}
    for x in t3["source_cache"]:
        if x.get("url","").endswith(("/vine/src/model.py","/vine/src/vine_turbo.py")):
            patches["vine/src/"+x["url"].rsplit("/",1)[-1]]=x["sha256"]
    result=dict(schema="encoder-transfer-assets-v1",stage1="metadata only, no runnable upstream code/weights downloaded",
                files=files,total_file_bytes=sum(x["size_bytes"] for x in files),wam_revision=wam["revision"],
                vine_repository="https://github.com/Shilin-LU/VINE.git",vine_revision="d72f11a93f8de9bc45ef61202b9c8dda2a70cc77",
                vine_patch_source_sha256=patches,small_text_receipts=text_receipts,
                allowance=dict(asset_download_bytes=40_000_000_000,dependencies_bytes=20_000_000_000,other_reserve_bytes=20_000_000_000,total_bytes=80_000_000_000))
    write(DEST/"asset-download-plan.json",result)
    print({"files":len(files),"file_bytes":result["total_file_bytes"],"stage1_weight_bytes":0})

if __name__=="__main__":
    build()
