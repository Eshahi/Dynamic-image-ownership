"""Approval-gated ToS acquisition inside the existing registry worker preflight."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[1]

def prepare_near(plan,out,budget,heldout_authorized=False):
    if plan['data_split']=='development':return plan['near']
    if not heldout_authorized:raise PermissionError('Held-out footage refused before approval')
    from m1b_coco512_worker import atomic_json
    from registry_fresh_acquire import exr_rgb
    from PIL import Image
    docs=ROOT/'research/registry-confirmation'
    selection=json.loads((docs/'tears-of-steel-shots-index.json').read_text())
    lock=json.loads((docs/'model-lock.json').read_text())
    prior=json.loads((docs/'development-frame-exposure-index.json').read_text())
    known={f['rgb8_sha256'] for f in prior['frames'] if f.get('rgb8_sha256')}
    ffmpeg=Path(lock['ffmpeg']['path'])
    if hashlib.sha256(ffmpeg.read_bytes()).hexdigest()!=lock['ffmpeg']['sha256']:raise ValueError('EXR decoder differs')
    dest=Path(out)/'outputs/footage';dest.mkdir(exist_ok=True)
    history=dest/'preflight.json';state=json.loads(history.read_text()) if history.exists() else dict(shots={},downloaded_bytes=0,pairs=[])
    accepted=[];used=set()
    candidates=selection['selected']+selection['ordered_replacement_reserve']
    for shot in candidates:
        budget();name=shot['shot']
        if name in state['shots']:
            record=state['shots'][name]
        else:
            frames=[]
            for f in shot['frames']:
                budget();rid=f"{name}-{f['offset']}";receipt=dest/(rid+'.json');png=dest/(rid+'.png')
                if receipt.exists():frames.append(json.loads(receipt.read_text()));continue
                raw=dest/(rid+'.exr');part=dest/(rid+'.part')
                if not raw.exists():
                    with urllib.request.urlopen(f['url'],timeout=90) as response,part.open('wb') as h:
                        while True:
                            budget();chunk=response.read(1024*1024)
                            if not chunk:break
                            state['downloaded_bytes']+=len(chunk)
                            # Persist bytes received before writing: interrupted attempts
                            # remain charged against the cumulative acquisition cap.
                            atomic_json(history,state)
                            if state['downloaded_bytes']>3*2**30:raise RuntimeError('Frozen3GiB incremental acquisition cap reached')
                            h.write(chunk)
                    part.replace(raw)
                raw_hash=hashlib.sha256(raw.read_bytes()).hexdigest()
                rgb,canonical=exr_rgb(raw,str(ffmpeg));Image.fromarray(rgb).save(png)
                record=dict(url=f['url'],raw_sha256=raw_hash,rgb8_sha256=hashlib.sha256(rgb.tobytes()).hexdigest(),canonicalization=canonical,canonical_path=str(png.resolve()))
                atomic_json(receipt,record);frames.append(record);raw.unlink();atomic_json(history,state)
            duplicate=any(f['rgb8_sha256'] in known or f['rgb8_sha256'] in used for f in frames)
            record=dict(shot=name,frames=frames,excluded_duplicate=duplicate)
            state['shots'][name]=record;atomic_json(history,state)
        if record['excluded_duplicate']:continue
        for frame in record['frames']:
            if not Path(frame['canonical_path']).is_file():
                raise FileNotFoundError('Receipted canonical frame missing: '+frame['canonical_path'])
        # Within-shot shared reference frame is expected; cross-shot duplication is excluded.
        used.update(f['rgb8_sha256'] for f in record['frames'])
        for j,offset in enumerate((72,144,288),1):
            accepted.append(dict(pair_id=f'tos-{name}-o{offset:03d}',shot=name,left_path=record['frames'][0]['canonical_path'],right_path=record['frames'][j]['canonical_path']))
        if len(accepted)==60:break
    state['pairs']=accepted;state['complete']=len(accepted)==60;atomic_json(history,state)
    if not state['complete']:raise RuntimeError('Fixed shot replacement reserve exhausted; no cohort substitution allowed')
    return accepted
