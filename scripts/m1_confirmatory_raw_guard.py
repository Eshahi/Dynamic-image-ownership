"""Deny-by-default scoped input reader. Scientific issuance is unavailable.

Only generated token/image fixtures can receive a capability in this implementation.
No approval JSON, CLI boolean, metadata index or development receipt can unlock
scientific sources. Integration must supply a separately reviewed trusted issuer.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import time

FIXTURE_MAGIC=b"M1_SYNTHETIC_INPUT_V1\n"
MARKER=".m1-synthetic-resolver-fixture"
PNG_MAGIC=b"\x89PNG\r\n\x1a\n"
MAX_FIXTURE_BYTES=1024*1024
_HASH=re.compile(r"[0-9a-f]{64}\Z")
_SEAL=object()

class AccessDenied(ValueError): pass

@dataclass(frozen=True,slots=True)
class InputReceipt:
    source_uid: str
    role: str
    relative_path: str
    sha256: str
    size_bytes: int

@dataclass(frozen=True,slots=True,init=False)
class ScopedCapability:
    mode: str
    input_root: str
    output_root: str
    manifest_sha256: str
    index_sha256: str
    receipts: tuple[InputReceipt,...]
    expires_monotonic: float
    official_approval_verified: bool
    source_adoption_verified: bool
    _seal: object

@dataclass(frozen=True,slots=True)
class VerifiedBytes:
    data: bytes
    receipt: InputReceipt
    observed_sha256: str
    capability_mode: str


def _relative(value):
    if type(value) is not str or not value or "\\" in value or ":" in value or "\0" in value:
        raise AccessDenied("Canonical relative input path required")
    path=PurePosixPath(value)
    if path.is_absolute() or any(p in (".","..","") for p in value.split("/")):
        raise AccessDenied("Relative path traversal refused")
    return path


def _reject_reparse(path):
    info=path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info,"st_file_attributes",0)&getattr(stat,"FILE_ATTRIBUTE_REPARSE_POINT",0x400):
        raise AccessDenied("Symlink/junction/reparse input refused")
    return info


def _fixture_root(value):
    # Reject actual dataset spelling before filesystem resolution/stat.
    lexical=Path(value)
    if any(part.lower() in ("raw","data") for part in lexical.parts):
        raise AccessDenied("Dataset-root fixture issuance refused")
    root=lexical.absolute()
    temp=Path(tempfile.gettempdir()).resolve()
    if not root.is_relative_to(temp) or root==temp:
        raise AccessDenied("Fixture root must be its own temporary directory")
    for part in (root,*root.parents):
        if part==temp: break
        _reject_reparse(part)
    root=root.resolve(strict=True)
    marker=root/MARKER
    _reject_reparse(marker)
    fd=os.open(marker,os.O_RDONLY|getattr(os,"O_BINARY",0)|getattr(os,"O_NOFOLLOW",0))
    try:
        final=_handle_final_path(fd)
        info=os.fstat(fd)
        if os.path.normcase(str(final))!=os.path.normcase(str(marker)) or info.st_nlink!=1 or info.st_size!=len(FIXTURE_MAGIC):
            raise AccessDenied("Fixture marker handle identity differs")
        with os.fdopen(fd,"rb",closefd=False) as stream: marker_bytes=stream.read(len(FIXTURE_MAGIC)+1)
        if marker_bytes!=FIXTURE_MAGIC: raise AccessDenied("Exact generated-fixture marker required")
    finally: os.close(fd)
    return root


def issue_fixture_capability(input_root, output_root, receipts, *, manifest_sha256, index_sha256, ttl_seconds=60):
    """Generated fixtures only; NOT an official approval or source adoption surrogate."""
    root=_fixture_root(input_root)
    output=Path(output_root).absolute()
    if not output.is_relative_to(root) or output==root:
        raise AccessDenied("Fixture output destination must be a distinct contained subdirectory")
    _relative(output.relative_to(root).as_posix())
    current=root
    for part in output.relative_to(root).parts:
        current=current/part
        try: _reject_reparse(current)
        except FileNotFoundError: break
    if type(ttl_seconds) not in (int,float) or not 0<ttl_seconds<=600:
        raise AccessDenied("Bounded positive fixture capability lifetime required")
    if not all(type(x) is str and _HASH.fullmatch(x) for x in (manifest_sha256,index_sha256)):
        raise AccessDenied("Exact fixture manifest/index receipt hashes required")
    if not isinstance(receipts,(list,tuple)) or not receipts:
        raise AccessDenied("Nonempty explicit receipt allowlist required")
    allowed=[]; keys=set(); paths=set()
    for r in receipts:
        if type(r) is not InputReceipt or type(r.source_uid) is not str or not r.source_uid.startswith("fixture:") or type(r.role) is not str or r.role not in ("source-token","annotation-token","synthetic-generated-image"):
            raise AccessDenied("Synthetic fixture identity/role required")
        path=_relative(r.relative_path)
        if path.parts[0] in (output.relative_to(root).parts[0],MARKER):
            raise AccessDenied("Output/marker cannot serve as source input")
        if type(r.sha256) is not str or not _HASH.fullmatch(r.sha256) or type(r.size_bytes) is not int or not (len(PNG_MAGIC) if r.role=="synthetic-generated-image" else len(FIXTURE_MAGIC))<=r.size_bytes<=MAX_FIXTURE_BYTES:
            raise AccessDenied("Exact bounded input size/hash required")
        key=(r.source_uid,r.role)
        if key in keys or r.relative_path.casefold() in paths:
            raise AccessDenied("Overlapping fixture identity/path allowlist refused")
        keys.add(key); paths.add(r.relative_path.casefold()); allowed.append(r)
    cap=object.__new__(ScopedCapability)
    for k,v in dict(mode="synthetic-fixture-only",input_root=str(root),output_root=str(output),
                   manifest_sha256=manifest_sha256,index_sha256=index_sha256,receipts=tuple(allowed),
                   expires_monotonic=time.monotonic()+ttl_seconds,official_approval_verified=False,
                   source_adoption_verified=False,_seal=_SEAL).items():
        object.__setattr__(cap,k,v)
    return cap


def issue_scientific_capability(*args,**kwargs):
    """Fail before inspecting any user-supplied object/path, even apparently valid receipts."""
    raise AccessDenied("Scientific capability issuer unavailable: upstream authenticated official approval AND source-adoption integration pending")


def _authorize(cap,manifest_sha256,index_sha256,output_root):
    if type(cap) is not ScopedCapability or getattr(cap,"_seal",None) is not _SEAL:
        raise AccessDenied("Trusted in-process scoped capability required")
    if cap.mode!="synthetic-fixture-only" or cap.official_approval_verified is not False or cap.source_adoption_verified is not False:
        raise AccessDenied("Scientific raw access is not implemented")
    if time.monotonic()>=cap.expires_monotonic:
        raise AccessDenied("Scoped capability expired")
    if manifest_sha256!=cap.manifest_sha256 or index_sha256!=cap.index_sha256 or str(Path(output_root).absolute())!=cap.output_root:
        raise AccessDenied("Manifest/index/output scope differs")


def _handle_final_path(fd):
    """Query opened handle before reading bytes; catches parent-directory swap escapes."""
    if os.name=="nt":
        import msvcrt
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        query=kernel.GetFinalPathNameByHandleW
        query.argtypes=(ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32)
        query.restype=ctypes.c_uint32
        handle=msvcrt.get_osfhandle(fd)
        length=query(handle,None,0,0)
        if not length: raise AccessDenied("Opened handle final path unavailable")
        buffer=ctypes.create_unicode_buffer(length+1)
        written=query(handle,buffer,len(buffer),0)
        if not written or written>=len(buffer): raise AccessDenied("Opened handle final path unavailable")
        value=buffer.value
        if value.startswith("\\\\?\\UNC\\"): value="\\\\"+value[8:]
        elif value.startswith("\\\\?\\"): value=value[4:]
        return Path(value)
    link=Path(f"/proc/self/fd/{fd}")
    if not link.exists(): raise AccessDenied("Opened handle containment unavailable on this platform")
    return link.resolve(strict=True)


def read_scoped_input(cap, source_uid, role, *, manifest_sha256, index_sha256, output_root):
    """Return the same bounded bytes that were verified, never a path to reopen."""
    _authorize(cap,manifest_sha256,index_sha256,output_root)
    matches=[r for r in cap.receipts if (r.source_uid,r.role)==(source_uid,role)]
    if len(matches)!=1: raise AccessDenied("Input identity absent from immutable allowlist")
    receipt=matches[0]
    root=Path(cap.input_root)
    relative=_relative(receipt.relative_path)
    _reject_reparse(root)
    candidate=root
    for part in relative.parts:
        candidate=candidate/part
        path_info=_reject_reparse(candidate)
    if not stat.S_ISREG(path_info.st_mode) or path_info.st_nlink!=1 or path_info.st_size!=receipt.size_bytes:
        raise AccessDenied("Planned input must already be a single-linked regular file of expected size")
    if not candidate.is_relative_to(root): raise AccessDenied("Input escapes scoped root")
    flags=os.O_RDONLY|getattr(os,"O_BINARY",0)|getattr(os,"O_NOFOLLOW",0)
    fd=os.open(candidate,flags)
    try:
        final=_handle_final_path(fd)
        if not final.is_relative_to(root) or os.path.normcase(str(final))!=os.path.normcase(str(candidate)):
            raise AccessDenied("Opened input handle escapes/exchanges scoped path")
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size!=receipt.size_bytes:
            raise AccessDenied("Input type/size differs from receipt")
        with os.fdopen(fd,"rb",closefd=False) as stream:
            data=stream.read(receipt.size_bytes+1)
        after=os.fstat(fd)
        if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):
            raise AccessDenied("Input changed while read")
        digest=hashlib.sha256(data).hexdigest()
        required_magic=PNG_MAGIC if receipt.role=="synthetic-generated-image" else FIXTURE_MAGIC
        if len(data)!=receipt.size_bytes or digest!=receipt.sha256 or not data.startswith(required_magic):
            raise AccessDenied("Input byte identity or fixture format differs")
        _authorize(cap,manifest_sha256,index_sha256,output_root)
        return VerifiedBytes(data,receipt,digest,cap.mode)
    finally:
        os.close(fd)
