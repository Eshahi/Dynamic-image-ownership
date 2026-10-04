"""Exclusive contained unit storage with byte reread receipts. No authority issuer."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import numpy as np
from PIL import Image


class VerifiedUnitSink:
    def __init__(self,output_root,*,allowed_root,stage_layout='native',checkpoint_observer=None,before_checkpoint=None):
        self.root=Path(output_root).absolute();self.allowed=Path(allowed_root).resolve()
        self.stage_layout=stage_layout;self.checkpoint_observer=checkpoint_observer
        self.before_checkpoint=before_checkpoint
        if stage_layout not in ('native','generated-hwc-float64'):raise ValueError('Explicit stage layout required')
        self._contained(self.root)
        if not self.root.is_dir():raise ValueError('Caller must create owned output root')

    def _contained(self,path):
        path=Path(path).absolute()
        if not path.resolve().is_relative_to(self.allowed):raise ValueError('Artifact escapes declared output scope')
        for parent in [path,*path.parents]:
            if parent.exists():
                if parent.is_symlink() or getattr(parent.stat(),'st_file_attributes',0)&0x400:
                    raise ValueError('Reparse/symlink artifact path refused')
            if parent==self.allowed:break
        return path

    def _path(self,name,category,suffix):
        if type(name) is not str or not re.fullmatch('[A-Za-z0-9_-]{1,160}',name):raise ValueError('Fixed safe unit artifact name required')
        path=self._contained(self.root/category/(name+suffix));path.parent.mkdir(exist_ok=True)
        if path.exists():raise ValueError('Artifact already exists; no overwrite')
        return path

    def _receipt(self,path):
        path=self._contained(path)
        return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size_bytes=path.stat().st_size)

    def _write(self,path,writer):
        temporary=self._contained(path.with_name(path.name+'.partial'))
        with temporary.open('xb') as stream:
            writer(stream);stream.flush();os.fsync(stream.fileno())
        # Windows rename refuses an existing destination; preserve failed partials.
        if path.exists():raise ValueError('Concurrent artifact collision')
        temporary.rename(path)
        return self._receipt(path)

    def save_image(self,name,rgb):
        from m1_confirmatory_image_operations import rgb8
        value=rgb8(rgb);path=self._path(name,'outputs','.png')
        receipt=self._write(path,lambda stream:Image.fromarray(value).save(stream,format='PNG'))
        with Image.open(path) as image:
            if image.mode!='RGB' or image.size!=(512,512):raise ValueError('Persisted PNG geometry differs')
            saved=np.asarray(image).copy()
        if not np.array_equal(saved,value):raise ValueError('Persisted PNG pixels differ')
        return saved,receipt

    def save_array(self,name,value):
        value=np.asarray(value)
        if value.dtype.kind not in 'fiu' or not np.isfinite(value).all():raise ValueError('Finite numeric arrays required')
        if self.stage_layout=='generated-hwc-float64' and name in ('reference','decoded','residual','surrogate'):
            if value.shape!=(1,3,512,512):raise ValueError('Generated compatibility boundary requires native NCHW')
            value=value[0].transpose(1,2,0).astype(np.float64)
        # Preserve old generated reader filenames while retaining source-E evidence.
        file_name=name[:-2]+'-reader' if name.endswith('-z') else name
        path=self._path(file_name,'outputs','.npy')
        receipt=self._write(path,lambda stream:np.save(stream,value,allow_pickle=False))
        loaded=np.load(path,allow_pickle=False)
        if loaded.dtype!=value.dtype or not np.array_equal(loaded,value):raise ValueError('Persisted numeric array differs')
        return receipt

    def save_checkpoint(self,name,value):
        import torch
        import m1_source_initialization as initialization
        path=self._path(name,'checkpoints','.pt')
        if self.before_checkpoint is not None:self.before_checkpoint(value)
        receipt=self._write(path,lambda stream:torch.save(value,stream))
        loaded=torch.load(path,map_location='cpu',weights_only=True)
        if initialization.digest(loaded)!=initialization.digest(value):raise ValueError('Saved sealed checkpoint differs')
        if self.checkpoint_observer is not None:self.checkpoint_observer(value,receipt)
        return receipt
