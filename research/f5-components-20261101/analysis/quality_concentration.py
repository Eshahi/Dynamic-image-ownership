"""TQ: fixed saved-development residual diagnostics; no model or writer."""
import sys
sys.dont_write_bytecode = True
import csv, hashlib, json, math, os, statistics, subprocess, time
from pathlib import Path
import numpy as np
from PIL import Image

start=time.monotonic()
ROOT=Path(__file__).resolve().parents[3]
RD=ROOT/'research/f5-components-20261101'
invpath=RD/'results/wp4-pixels/inventory.json'
inv=json.loads(invpath.read_text(encoding='utf-8'))
out=RD/'results/wp4-tq'
assert not out.exists()
rows=[]; hashes={}
def read(item):
    p=Path(item['path']); raw=p.read_bytes(); h=hashlib.sha256(raw).hexdigest()
    assert h==item['expected_sha256']
    hashes[str(p)]=h
    a=np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
    assert a.shape==(512,512,3)
    return a
def patches(a):
    return a.reshape(16,32,16,32,*a.shape[2:]).swapaxes(1,2).reshape(256,32,32,*a.shape[2:])
items={(r['source'],r['arm']):r for r in inv['items'] if r['panel']=='stage2' and r['cell']=='clean'}
for src in inv['chosen_stage2']:
    c0=read(items[src,'unmarked']); lum=c0@np.array([.299,.587,.114])
    lp=patches(lum)
    texture=(np.abs(np.diff(lp,axis=1)).mean((1,2))+np.abs(np.diff(lp,axis=2)).mean((1,2)))/2
    order=np.argsort(texture,kind='stable'); flat=order[:64]; textured=order[-64:]
    for method in ('v5-r3','f5-r2'):
        mark=read(items[src,method]); delta=mark-c0; dp=patches(delta)
        patch_rms=np.sqrt(np.mean(dp*dp,axis=(1,2,3)))
        glob=float(np.sqrt(np.mean(delta*delta)))
        fr=float(np.sqrt(np.mean(dp[flat]**2))); tr=float(np.sqrt(np.mean(dp[textured]**2)))
        rows.append(dict(source=src,split=items[src,method]['split'],method=method,
                         global_RMS_255=glob,flat_RMS_255=fr,textured_RMS_255=tr,
                         flat_to_textured=fr/tr if tr else None,
                         max_patch_RMS_255=float(patch_rms.max()),max_patch_to_global=float(patch_rms.max())/glob,
                         max_absolute_residual_255=float(np.abs(delta).max()),PSNR=20*math.log10(255/glob),
                         flat_patches=';'.join(map(str,flat)),textured_patches=';'.join(map(str,textured))))
        assert time.monotonic()-start<500
summary=[]
for method in ('v5-r3','f5-r2'):
    for split in ('DESIGN','EVALUATE'):
        rs=[r for r in rows if r['method']==method and r['split']==split]
        a=statistics.median(r['max_patch_to_global'] for r in rs); b=statistics.median(r['flat_to_textured'] for r in rs)
        summary.append(dict(method=method,split=split,sources=len(rs),median_max_patch_to_global=a,
                            median_flat_to_textured=b,rule='RETAIN_CONCENTRATION_DIAGNOSTIC_ONLY' if a>2 or b>1.5 else 'KILL_LOCAL_CONCENTRATION_PRIORITY'))
out.mkdir()
with (out/'sources.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
meta=dict(command=[sys.executable,*sys.argv],commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          seconds=time.monotonic()-start,cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),phase_b_journals='off',inputs=hashes,
          script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),plan_sha256=hashlib.sha256((RD/'analysis/WP4-TEST-PLAN.md').read_bytes()).hexdigest())
assert meta['seconds']<540
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
