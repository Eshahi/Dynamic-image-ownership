"""E3-BI1: one fixed equal-energy structure/detail descriptor, CPU diagnostic."""
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import journal_stable_instance as harness
from scripts import revised_watermark_v4 as base

LABEL=b'perceptual-projection'


def descriptor(luma,key,config):
    means,detail=base._analyse(luma,base._DETAIL_PLANES)
    grid=base._resample(means,base.HASH_GRID)
    coarse=[]
    for u,v in base._HASH_BAND:
        partial=[sum(base._HASH_BASIS[u][y]*grid[y][x] for y in range(base.HASH_GRID))
                 for x in range(base.HASH_GRID)]
        coarse.append(sum(partial[x]*base._HASH_BASIS[v][x] for x in range(base.HASH_GRID))*math.hypot(u,v))
    columns=len(means[0]);fine=[]
    for position in range(len(base.HASH_DETAIL_POSITIONS)):
        fine+=base._local_detail([[block[position] for block in detail[start:start+columns]]
                                 for start in range(0,len(detail),columns)])
    floor=base.HASH_DETAIL_FLOOR*math.sqrt(len(fine))
    c=base._unit(coarse,1.0);f=base._unit(fine,1.0,floor)
    vector=[x*math.sqrt(.5) for x in c+f]
    norm=math.sqrt(sum(x*x for x in vector))
    legacy=base._perceptual_hash(means,detail,key,config)
    # Before scoring BI1, independently reconstruct the existing .25 allocation.
    native_vector=base._unit(coarse,math.sqrt(.25))+base._unit(fine,math.sqrt(.75),floor)
    assert base._sign_projections(native_vector,key,config,LABEL)==legacy
    assert len(native_vector)==len(vector) # Same profile, label and width -> same hyperplanes.
    if math.sqrt(sum(x*x for x in coarse))<1e-9:
        return dict(h=None,legacy_h=f'{legacy:08x}',norm=norm,vector=None,margins=None)
    h=base._sign_projections(vector,key,config,LABEL)
    width=len(vector);rb=(width+7)//8
    stream=base._stream(key,config,base._pack(LABEL,width.to_bytes(4,'big')),32*rb)
    margins=[sum(-v if (stream[r*rb+(i>>3)]>>(i&7))&1 else v for i,v in enumerate(vector))
             for r in range(32)]
    assert h==sum(int(m>1e-9)<<(31-r) for r,m in enumerate(margins))
    return dict(h=f'{h:08x}',legacy_h=f'{legacy:08x}',norm=norm,vector=vector,
        changed_from_same_pixels_legacy=f'{h^legacy:08x}',
        margins=margins,coarse_norm=math.sqrt(sum(x*x for x in coarse)),
        fine_raw_norm=math.sqrt(sum(x*x for x in fine)),fine_floor=floor,
        coarse_component_norm=math.sqrt(sum(x*x for x in c)),
        fine_component_norm=math.sqrt(sum(x*x for x in f)))


def compare(a,b):
    out=harness.compare(a,b)
    if a['vector'] is None or b['vector'] is None:
        return out
    # Undo the fixed sqrt(.5) scale; f retains the native detail floor.
    c=sum(x*y for x,y in zip(a['vector'][:63],b['vector'][:63]))*2
    d=sum(x*y for x,y in zip(a['vector'][63:],b['vector'][63:]))*2
    cna,cnb=a['coarse_component_norm'],b['coarse_component_norm']
    fa,fb=a['fine_component_norm'],b['fine_component_norm']
    cosine=(c+d)/math.sqrt((cna*cna+fa*fa)*(cnb*cnb+fb*fb))
    direct=sum(x*y for x,y in zip(a['vector'],b['vector']))/(a['norm']*b['norm'])
    assert abs(cosine-direct)<1e-10
    out.update(cosine=cosine,coarse_dot=c,coarse_cosine=c/(cna*cnb) if cna*cnb else None,
        fine_dot=d,fine_cosine=d/(fa*fb) if fa*fb else None,
        fine_norms=[fa,fb],coarse_norms=[cna,cnb],
        isotropic_expected_bit_distance=32*math.acos(min(1,max(-1,cosine)))/math.pi,
        geometry_status='Hypothetical isotropic-hyperplane expectation, not Rademacher bit prediction or a gate')
    return out


if __name__=='__main__':
    harness.main(descriptor_fn=descriptor,compare_fn=compare,descriptor_config=dict(
        method='E3-BI1',label=LABEL.decode(),coarse_energy=.5,detail_energy=.5,
        detail_floor='native unchanged',projection_stream='native unchanged',
        geometry='floor-aware continuous diagnostic only; no weight selected from outcomes'))
