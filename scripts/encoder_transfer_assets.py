"""Stage-2-only, pinned asset preparation. Importing this module has no I/O."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
import zipfile
from encoder_transfer_test import ROOT, digest, read, write


def fetch(spec,root,budget,ledger):
    target=root/spec["path"]
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if digest(target)!=spec["sha256"]:
            raise ValueError(f"Existing asset hash differs: {spec['path']}")
        return target
    budget.check()
    part=target.with_name(target.name+".part")
    received=0
    try:
        with urllib.request.urlopen(spec["url"],timeout=60) as response,part.open("wb") as handle:
            while chunk:=response.read(1024*1024):
                budget.check(120)
                received+=len(chunk)
                ledger["bytes_received"]+=len(chunk)
                if ledger["bytes_received"]>40_000_000_000 or received>spec["size_bytes"]:
                    raise RuntimeError("Frozen asset download allowance exceeded")
                handle.write(chunk)
        if received!=spec["size_bytes"] or digest(part)!=spec["sha256"]:
            raise ValueError(f"Downloaded hash/size mismatch: {spec['path']}")
        part.replace(target)
        ledger["files"].append({**spec,"actual_sha256":digest(target),"actual_bytes":received})
        return target
    finally:
        write(root/"download-ledger.json",ledger)


def patch_vine(root,plan):
    """Only redirect inspected SD-Turbo loads; preserve scientific code."""
    repo=root/"vine/source"
    changes=[]
    target=str((root/"vine/sd-turbo").resolve())
    for file in ("vine/src/model.py","vine/src/vine_turbo.py"):
        path=repo/file
        original=subprocess.check_output(["git","show",f"{plan['vine_revision']}:{file}"],cwd=repo)
        inspected=plan["vine_patch_source_sha256"][file]
        if hashlib.sha256(original).hexdigest()!=inspected:
            raise ValueError("VINE inspected source differs from pinned checkout")
        source=original.decode()
        patched=source.replace('"stabilityai/sd-turbo"',repr(target)).replace("'stabilityai/sd-turbo'",repr(target))
        if patched==source:
            raise ValueError("Expected native SD-Turbo path not found")
        path.write_text(patched,encoding="utf-8")
        changes.append(dict(path=file,original_sha256=inspected,patched_sha256=digest(path)))
    write(root/"vine/local-path-patch.json",dict(reason="Resolve native dependencies exclusively to pinned local assets",files=changes))


def prepare_amendment_1d(root,asset_plan,budget):
    """Pinned TrustMark and VideoSeal checkouts; TrustMark Q weights placed where its loader checks MD5."""
    import shutil
    extra=asset_plan.get("amendment_1d")
    if not extra:
        return
    for name in ("trustmark","videoseal"):
        repo=root/name/"source"
        if not repo.exists():
            budget.check()
            subprocess.run(["git","clone","--filter=blob:none","--no-checkout",extra[name+"_repository"],str(repo)],check=True,timeout=300)
            subprocess.run(["git","checkout","--detach",extra[name+"_revision"]],cwd=repo,check=True,timeout=180)
        head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
        if head!=extra[name+"_revision"]:
            raise ValueError(f"Unexpected {name} repository revision")
    models=root/"trustmark/source/python/trustmark/models"
    for file_name,md5 in extra["trustmark_loader_md5"].items():
        source=root/"trustmark/models"/file_name
        target=models/file_name
        if not target.exists() or digest(target)!=digest(source):
            shutil.copyfile(source,target)
        if hashlib.md5(target.read_bytes()).hexdigest()!=md5:
            raise ValueError(f"TrustMark loader MD5 mismatch: {file_name}")


def prepare(root,config,sources,budget):
    root=Path(root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    asset_plan=read(ROOT/config["asset_plan_file"])
    ledger=read(root/"download-ledger.json") if (root/"download-ledger.json").exists() else dict(bytes_received=0,files=[])
    for spec in asset_plan["files"]:
        fetch(spec,root,budget,ledger)
    archive=root/"wam/source.zip"
    if not (root/"wam/source").exists():
        with zipfile.ZipFile(archive) as z:
            prefix=f"watermark-anything-{asset_plan['wam_revision']}/"
            for info in z.infolist():
                if info.is_dir():
                    continue
                if not info.filename.startswith(prefix):
                    raise ValueError("Unexpected WAM archive root")
                relative=Path(info.filename[len(prefix):])
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe archive path")
                destination=root/"wam/source"/relative
                destination.parent.mkdir(parents=True,exist_ok=True)
                destination.write_bytes(z.read(info))
    repo=root/"vine/source"
    if not repo.exists():
        budget.check()
        subprocess.run(["git","clone","--filter=blob:none","--no-checkout",asset_plan["vine_repository"],str(repo)],check=True,timeout=300)
        subprocess.run(["git","checkout","--detach",asset_plan["vine_revision"]],cwd=repo,check=True,timeout=180)
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
    if head!=asset_plan["vine_revision"]:
        raise ValueError("Unexpected VINE repository revision")
    patch_vine(root,asset_plan)
    prepare_amendment_1d(root,asset_plan,budget)
    from m1b_canonical_source import canonicalize
    from PIL import Image
    for source in sources["sources"]+sources["smoke"]:
        spec=dict(path=f'sources/raw/{source["source_id"]}',url=source["url"],
                  sha256=source["raw_sha256"],size_bytes=source["raw_bytes"],license=source["license"])
        raw=fetch(spec,root,budget,ledger)
        rgb,receipt=canonicalize(raw.read_bytes(),source["raw_sha256"])
        if receipt["rgb8_sha256"]!=source["rgb8_sha256"]:
            raise ValueError("Canonical development pixel hash mismatch")
        path=root/"sources"/f'{source["source_id"]}.png'
        Image.fromarray(rgb).save(path)
        # PNG compression can differ by Pillow; pixel identity is authoritative.
        ledger.setdefault("canonical_sources",{})[str(source["source_id"])]=dict(path=str(path),sha256=digest(path),rgb8_sha256=receipt["rgb8_sha256"])
    write(root/"download-ledger.json",ledger)
    write(root/"ready.json",dict(asset_plan_sha256=digest(ROOT/config["asset_plan_file"]),sources_sha256=config["sources_sha256"],
                                  sources=[s["source_id"] for s in sources["sources"]+sources["smoke"]],budget=budget.record()))


def verify_ready(root,config,sources):
    ready=read(root/"ready.json")
    if ready["asset_plan_sha256"]!=digest(ROOT/config["asset_plan_file"]) or ready["sources_sha256"]!=config["sources_sha256"]:
        raise ValueError("Assets were prepared for a different frozen contract")
    if ready["sources"]!=[s["source_id"] for s in sources["sources"]+sources["smoke"]]:
        raise ValueError("Prepared source identities differ")
