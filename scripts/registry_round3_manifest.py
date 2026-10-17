"""Round3 data manifest: count saved native rows without making scientific choices."""
from pathlib import Path
import json
from collections import Counter
from registry_step1_transfer import MAIN, read, write, journal
ROOT=Path(__file__).resolve().parents[1]
ASSETS=MAIN/'.thesis-build/assets/registry-round3-20261017'
FRESH=MAIN/'.thesis-build/dev-runs/20261017-round3-registry-fresh'
ANALYSIS=MAIN/'.thesis-build/dev-runs/20261017-round3-registry-analysis'
MANIFEST=MAIN/'.thesis-build/agent-logs/round3-data-manifest.json'

def main():
    docs=ROOT/'research/journal-upgrade-20261009'
    ids=[s['source_id'] for s in read(docs/'round3-development-selection.json')['selected']]
    pairs=[s['pair_id'] for s in read(docs/'round3-near-duplicate-selection.json')['selected']]
    rows=journal(FRESH/'rows.jsonl'); calls=journal(ANALYSIS/'calls.jsonl')
    phases={}
    for phase,expected in [('embed',120),('sd15',720),('sd21',720)]:
        subset=[r for r in rows.values() if r.get('phase')==phase]
        counts=Counter(r['status'] for r in subset)
        missing=expected-sum(v for k,v in counts.items() if k!='running')
        phases[phase]=dict(expected=expected,counts=dict(counts),missing=missing,failed=sum(counts[k] for k in ('error','scientific_failure','input_unavailable')),safety_blocked=counts['safety_blocked'],status='complete' if missing==0 else 'partial')
    for phase,prefix,expected in [('T4','T4:',80),('look_alike_calls','near:',60)]:
        counts=Counter(r['status'] for k,r in calls.items() if k.startswith(prefix))
        phases[phase]=dict(expected=expected,counts=dict(counts),missing=expected-counts['ok'],failed=counts['error'],safety_blocked=counts['safety_blocked'],status='complete' if counts['ok']==expected else 'partial')
    paths=list(ANALYSIS.glob('descriptor-index-*.json'))
    descriptors={str(p):len(read(p)) for p in paths}
    score=ANALYSIS/'evaluation-D1-scores.json'
    phases['descriptors']=dict(status='complete' if score.exists() else 'partial',index_counts=descriptors)
    acquired=ASSETS/'sources.json'; near=ASSETS/'near-duplicates.json'
    phases['acquisition']=dict(status='complete' if acquired.exists() and near.exists() else 'partial',sources=len(read(acquired)['sources']) if acquired.exists() else 0,pairs=len(read(near)['pairs']) if near.exists() else 0)
    seconds=sum(read(p)['duration_seconds'] for p in (FRESH/'run.json',ANALYSIS/'run.json') if p.exists())
    result=dict(schema='round3-development-data-manifest-v1', fresh_dir=str(FRESH),canonical_dir=str(ASSETS/'canonical'),analysis_dir=str(ANALYSIS),descriptor_indexes=[str(p) for p in paths],pointer_scores=str(score),t4_glob=str(ANALYSIS/'images/T4-evaluation-*.png'),source_ids=ids,look_alike_ids=pairs,phases=phases,duration_seconds=seconds,budget_seconds=10800,usd=0,data_split='development only; all40 evaluation',side_information='Trusted enrolled continuous descriptors and owner/record lookup',scoring='Unchanged frozen step2b calibration; no round3 thresholds or definitions read or selected',acquisition_receipts=str(ASSETS/'acquisition.jsonl'),native_rows=str(FRESH/'rows.jsonl'))
    if (ANALYSIS/'availability-metadata-evaluation.json').exists():
        avail=read(ANALYSIS/'availability-metadata-evaluation.json')['paths']
        result['descriptor_availability']={d:dict(Counter(r['reason'] for r in avail if r['descriptor']==d)) for d in ('D1','D2','D3')}
    MANIFEST.parent.mkdir(parents=True,exist_ok=True); write(MANIFEST,result)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
