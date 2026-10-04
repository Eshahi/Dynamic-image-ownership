"""Working-byte receipt plus clean normalized Git blob identity; no byte rewriting."""
from __future__ import annotations
import hashlib,re,subprocess
from pathlib import Path


def verify_git_input(path,commit,root,expected_raw_sha256):
    root=Path(root).resolve();path=Path(path).resolve()
    if not path.is_relative_to(root) or not path.is_file():raise ValueError('Repository input required')
    if type(commit) is not str or re.fullmatch('[0-9a-f]{40}',commit) is None:raise ValueError('Exact commit required')
    if type(expected_raw_sha256) is not str or re.fullmatch('[0-9a-f]{64}',expected_raw_sha256) is None:raise ValueError('Exact byte receipt required')
    rel=path.relative_to(root).as_posix();raw=hashlib.sha256(path.read_bytes()).hexdigest()
    if raw!=expected_raw_sha256:raise ValueError('Working input bytes differ: '+rel)
    committed=subprocess.check_output(['git','rev-parse',commit+':'+rel],cwd=root,text=True).strip()
    working=subprocess.check_output(['git','hash-object','--path='+rel,str(path)],cwd=root,text=True).strip()
    if re.fullmatch('[0-9a-f]{40}',committed) is None or working!=committed:raise ValueError('Uncommitted normalized Git input: '+rel)
    return dict(working_sha256=raw,git_blob_sha1=working,committed_blob_sha1=committed)
