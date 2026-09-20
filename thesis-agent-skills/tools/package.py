"""Build a clean deterministic ZIP, checksums and file manifest; no recursive deletion."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={".build",".venv","__pycache__",".git",".pytest_cache","dist","build"}

def included(path):
    parts=path.relative_to(ROOT).parts
    return not any(p in EXCLUDED or p.endswith(".egg-info") for p in parts) and path.suffix not in (".pyc",".pyo") and path.name!=".env"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def materialize():
    for skill in sorted((ROOT/"skills").iterdir()):
        if not skill.is_dir(): continue
        for src in sorted((ROOT/"src/thesis_agents").rglob("*")):
            if src.is_file() and "__pycache__" not in src.parts and src.suffix!=".pyc":
                target=skill/"scripts/_runtime/thesis_agents"/src.relative_to(ROOT/"src/thesis_agents")
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,target)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist",required=True); parser.add_argument("--materialize-only",action="store_true")
    args=parser.parse_args(); materialize()
    if args.materialize_only: print("Embedded shared runtime in eight skills"); return 0
    tests=json.loads((ROOT/"tests/validation-results.json").read_text())
    if not tests["passed"]: raise RuntimeError("Refusing package: validation did not pass")
    paths={p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and included(p)}
    paths.update({"DIRECTORY_TREE.txt","bundle-manifest.json","CHECKSUMS.sha256"})
    tree={}
    for path in sorted(paths):
        current=tree
        parts=path.split("/")
        for part in parts[:-1]: current=current.setdefault(part,{})
        current[parts[-1]]=None
    lines=["thesis-agent-skills/"]
    def render(node,prefix=""):
        entries=sorted(node.items(),key=lambda item:(item[1] is None,item[0]))
        for index,(name,children) in enumerate(entries):
            last=index==len(entries)-1
            lines.append(prefix+("└── " if last else "├── ")+name+("/" if children is not None else ""))
            if children is not None: render(children,prefix+("    " if last else "│   "))
    render(tree)
    (ROOT/"DIRECTORY_TREE.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    files=[p for p in sorted(ROOT.rglob("*")) if p.is_file() and included(p) and p.name not in ("CHECKSUMS.sha256","bundle-manifest.json")]
    metadata={"schema_version":"1.0","name":"thesis-agent-skills","version":"1.0.0","skills":sorted(p.name for p in (ROOT/"skills").iterdir() if p.is_dir()),"profiles":{"controller":["thesis-workflow-control","thesis-research-handoff"],"worker":"all-eight","reviewer":["thesis-literature-synthesis","thesis-results-analysis","thesis-evidence-audit","thesis-writing"]},"spec_kit":{"commit":"d4229c071c7ea3885b43e8a7739847300f618f13","version":"1.0.9.dev0","schema_version":"1.0"},"tests":tests,"capabilities":{"local_execution":True,"mock_runpod":True,"live_runpod_creation":False,"live_runpod_artifact_transfer":False},"files":[{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p)} for p in files],"checksum_policy":"Manifest lists payload excluding itself and CHECKSUMS.sha256; checksum file includes manifest but excludes itself; archive has an external checksum"}
    manifest=ROOT/"bundle-manifest.json"; manifest.write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    files.append(manifest); files=sorted(files)
    checksums=ROOT/"CHECKSUMS.sha256"; checksums.write_text("".join(sha(p)+"  "+p.relative_to(ROOT).as_posix()+"\n" for p in files),encoding="utf-8")
    files.append(checksums)
    dist=Path(args.dist).resolve(); dist.mkdir(parents=True,exist_ok=True); archive=dist/"thesis-agent-skills.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo("thesis-agent-skills/"+p.relative_to(ROOT).as_posix(),date_time=(2026,9,19,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise RuntimeError("ZIP CRC validation failed")
        for p in files:
            if hashlib.sha256(z.read("thesis-agent-skills/"+p.relative_to(ROOT).as_posix())).hexdigest()!=sha(p): raise RuntimeError("Archive checksum mismatch")
    (dist/"thesis-agent-skills.zip.sha256").write_text(sha(archive)+"  thesis-agent-skills.zip\n",encoding="utf-8")
    print(json.dumps({"files":len(files),"archive":str(archive),"archive_sha256":sha(archive),"bytes":archive.stat().st_size,"zip_crc":"passed","payload_checksums":"passed"}))
    return 0

if __name__=="__main__": raise SystemExit(main())
