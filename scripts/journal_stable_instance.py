"""Fixed E3-CD1 cached-pixel stability AND discrimination diagnostic, CPU only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image
from scripts import revised_watermark_v4 as base, revised_watermark_v5 as v5
from scripts.watermark_synthetic import scene

LABEL = b'E3-CD1-coarse-instance-v1'
IDS = (30, 72, 73, 89, 127, 165)
ALPHA = 'qim-pilot-owner-alpha'


def descriptor(luma, key, config):
    means, detail = base._analyse(luma, base._DETAIL_PLANES)
    grid = base._resample(means, base.HASH_GRID)
    coarse = []
    for u, v in base._HASH_BAND:
        partial = [sum(base._HASH_BASIS[u][y]*grid[y][x] for y in range(base.HASH_GRID))
                   for x in range(base.HASH_GRID)]
        coarse.append(sum(partial[x]*base._HASH_BASIS[v][x] for x in range(base.HASH_GRID))*math.hypot(u,v))
    norm = math.sqrt(sum(x*x for x in coarse))
    legacy = base._perceptual_hash(means, detail, key, config)
    if norm < 1e-9:
        return dict(h=None, legacy_h=f'{legacy:08x}', norm=norm, vector=None, margins=None)
    vector = [x/norm for x in coarse]
    h = base._sign_projections(vector, key, config, LABEL)
    width = len(vector); rowbytes = (width+7)//8
    stream = base._stream(key, config, base._pack(LABEL, width.to_bytes(4,'big')),32*rowbytes)
    margins = [sum(-v if (stream[r*rowbytes+(i>>3)]>>(i&7))&1 else v
                   for i,v in enumerate(vector)) for r in range(32)]
    assert h == sum(int(m>1e-9)<<(31-r) for r,m in enumerate(margins))
    return dict(h=f'{h:08x}', legacy_h=f'{legacy:08x}', norm=norm, vector=vector, margins=margins)


def distance(a,b):
    return None if a is None or b is None else (int(a,16)^int(b,16)).bit_count()


def compare(a,b):
    d = distance(a['h'],b['h'])
    old = distance(a['legacy_h'],b['legacy_h'])
    dot = sum(x*y for x,y in zip(a['vector'],b['vector'])) if a['vector'] and b['vector'] else None
    return dict(distance=d, match=d is not None and d<=6, legacy_distance=old,
                legacy_match=old<=6, cosine=dot)


def main():
    tick = time.monotonic()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage-a',type=Path,required=True)
    p.add_argument('--h1',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a = p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=False)
    stage = json.loads(a.stage_a.read_text()); h1 = json.loads(a.h1.read_text())
    assert stage['outcome']=='completed' and h1['outcome']=='completed'
    profile,key,config = v5._resolve(stage['config']['profile'],None)
    assert profile['decision']['instance_radius']==6
    result = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=sys.argv, started_at_utc=datetime.now(timezone.utc).isoformat(),
        config=dict(label=LABEL.decode(), radius=6, mismatch=10,max_seconds=600,
                    targets='canonical', sibling_seeds=list(range(1,7)),detail_seeds=[11,12]),
        data_split='consulted development and synthetic', usd=0, seeds=[9,10,11],
        input_receipts=[str(a.stage_a),str(a.h1)], outcome='running', images={},clean=[],
        positives=[],impostors={},q_nearest=[],siblings=[],advance_gate=False)
    def save():
        result['duration_seconds']=time.monotonic()-tick
        (a.output_dir/'run.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    def budget():
        if time.monotonic()-tick>600: raise TimeoutError('Inclusive CPU cap exceeded')
    def load(path):
        path=str(path); budget()
        if path not in result['images']:
            with Image.open(path) as image:
                rgb=np.array(image.convert('RGB'))
            result['images'][path]=descriptor(v5.luminance_from_rgb(rgb.tolist()),key,config)
        return result['images'][path]
    try:
        sources={r['source_id']:r for r in stage['sources']}
        assert len(sources)==24 and all(s['status']=='ok' for s in sources.values())
        canonical={i:load(s['canonical_path']) for i,s in sources.items()}
        full={i:load(s['full_image']) for i,s in sources.items()}
        result['clean']=[dict(source_id=i,**compare(canonical[i],full[i])) for i in sources]
        print('Canonical/full-clean descriptor computations complete',flush=True);save()
        for row in h1['rows']:
            if row['arm']!='C':continue
            assert row['source_id'] in IDS and row['status']=='ok'
            observed=load(row['image']); i=row['source_id']
            c=compare(canonical[i],observed); j=bool(row['endpoints'][ALPHA]['J'])
            oldtarget=h1['sources'][str(i)]['shared_source']['payload']['h']
            olddist=distance(oldtarget,observed['legacy_h'])
            # Native legacy extraction must match the original full detector call.
            assert observed['legacy_h']==row['calls'][ALPHA]['perceptual_hash']
            result['positives'].append(dict(id=row['id'],source_id=i,phase=row['phase'],
                strength=row.get('strength'),seed=row.get('seed'),**c,actual_J=j,
                O_DJ=bool(j and c['match']),old_operational_distance=olddist,
                old_O_J=bool(j and olddist<=6)))
        expected={(i,phase,None,None) for i in IDS for phase in ('clean','sd15_vae','sdxl_vae')}
        expected|={(i,'T3',s,k) for i in IDS for s in (.2,.4) for k in (9,10,11)}
        assert len(result['positives'])==54 and {(r['source_id'],r['phase'],r['strength'],r['seed']) for r in result['positives']}==expected
        for panel,other in [('canonical',canonical),('marked',full)]:
            result['impostors'][panel]=[dict(target=i,suspect=j,**compare(canonical[i],other[j]))
                                       for i in sources for j in sources if i!=j]
        # Original q is the canonical-derived supplier word, never optimized against h_CD.
        for i in sources:
            j=min((j for j in sources if j!=i),key=lambda j:(distance(sources[i]['payload']['q'],sources[j]['payload']['q']),j))
            result['q_nearest'].append(dict(target=i,suspect=j,
                q_distance=distance(sources[i]['payload']['q'],sources[j]['payload']['q']),
                **compare(canonical[i],canonical[j])))
        print('All cached positives and real-source impostors complete',flush=True);save()
        for seed in range(1,7):
            budget()
            pair=[descriptor(scene(seed,512,512,12.0,d),key,config) for d in (11,12)]
            result['siblings'].append(dict(seed=seed,descriptors=pair,**compare(*pair)))
        summary={}
        for name,phase,s in [('clean','clean',None),('sd15_vae','sd15_vae',None),('sdxl_vae','sdxl_vae',None),('T3_0.2','T3',.2),('T3_0.4','T3',.4)]:
            rows=[r for r in result['positives'] if r['phase']==phase and r['strength']==s]
            summary[name]=dict(n=len(rows),O_DJ=sum(r['O_DJ'] for r in rows),
                old_O_J=sum(r['old_O_J'] for r in rows),
                majority=sum(sum(r['O_DJ'] for r in rows if r['source_id']==i)>=(2 if phase=='T3' else 1) for i in IDS),
                distances=dict(Counter(r['distance'] for r in rows)))
        summary['clean24']=sum(r['match'] for r in result['clean'])
        summary['impostor_matches']={k:sum(r['match'] for r in rows) for k,rows in result['impostors'].items()}
        summary['legacy_impostor_matches']={k:sum(r['legacy_match'] for r in rows) for k,rows in result['impostors'].items()}
        summary['nearest_match']=sum(r['match'] for r in result['q_nearest'])
        summary['nearest_mismatch']=sum(r['distance'] is not None and r['distance']>=10 for r in result['q_nearest'])
        summary['sibling_new_acceptances']=sum(r['match'] and not r['legacy_match'] for r in result['siblings'])
        all_resolved=all(r['h'] is not None for r in result['images'].values()) and all(r['h'] is not None for s in result['siblings'] for r in s['descriptors'])
        gates=dict(complete=all_resolved,clean=summary['clean24']==24 and summary['clean']['O_DJ']==6,
            vae=summary['sd15_vae']['O_DJ']>=5,
            regeneration=summary['T3_0.2']['O_DJ']>=15 and summary['T3_0.2']['majority']>=5,
            impostors=not any(summary['impostor_matches'].values()),
            nearest=summary['nearest_match']==0 and summary['nearest_mismatch']>=20,
            siblings=summary['sibling_new_acceptances']==0)
        budget();result.update(outcome='completed',summary=summary,gates=gates,advance_gate=all(gates.values()))
        print(json.dumps(dict(summary=summary,gates=gates,advance_gate=result['advance_gate']),indent=2),flush=True)
    except Exception as exc:
        result.update(outcome='inconclusive',error=f'{type(exc).__name__}: {exc}')
        raise
    finally:save()


if __name__=='__main__':main()
