"""Round3 data manifest: count saved native rows without making scientific choices."""
from pathlib import Path
import json
import hashlib
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
    acquisition_summary = ASSETS/'round3-acquisition-summary.json'
    acq = read(acquisition_summary) if acquisition_summary.exists() else {}
    phases['acquisition'].update(expected_sources=40, expected_pairs=60,
        missing_sources=40-phases['acquisition']['sources'], missing_pairs=60-phases['acquisition']['pairs'],
        failed=0 if phases['acquisition']['status']=='complete' else None, safety_blocked=0,
        retained_incident_count=len(acq.get('retained_failures',[])), retained_incidents=acq.get('retained_failures',[]))
    result['acquisition_summary'] = str(acquisition_summary)
    result['known_development_footage_overlaps'] = acq.get('known_development_canonical_overlaps',[])
    expected_paths = {r['image'] for r in rows.values() if r.get('status')=='ok' and r.get('image')}
    for r in calls.values():
        if r.get('status')=='ok':
            expected_paths.update(r[k] for k in ('image','left_path','right_path') if r.get(k))
    expected_paths = {str(Path(p).resolve()) for p in expected_paths}
    indexed = {}
    for p in paths: indexed.update(read(p))
    missing_vectors = sorted(p for p in expected_paths if p not in indexed or not Path(indexed[p]['cache']).is_file())
    missing_images = sorted(p for p in expected_paths if not Path(p).is_file())
    availability = result.get('descriptor_availability',{})
    unknown = sum(v.get('execution_or_descriptor_unknown',0) for v in availability.values())
    phases['descriptors'].update(expected_available_image_paths=len(expected_paths), indexed_image_paths=len(indexed),
        missing=len(missing_vectors), missing_paths=missing_vectors, failed=unknown, safety_blocked_excluded=phases['sd15']['safety_blocked']+phases['sd21']['safety_blocked'],
        missing_image_paths=missing_images)
    expected_scores = {k for k in rows if k.startswith(('clean:','sd15:','sd21:'))}
    scored = read(score)['positives_and_C0'] if score.exists() else []
    scored_ids = {r['id'] for r in scored}
    score_counts = dict(Counter(r['status'] for r in scored))
    phases['pointer_scores'] = dict(status='complete' if len(scored)==1520 and scored_ids==expected_scores else 'partial',
        expected=1520, rows=len(scored), counts=score_counts, missing=1520-len(scored_ids),
        failed=sum(score_counts.get(k,0) for k in ('error','scientific_failure','input_unavailable','missing')),
        safety_blocked=score_counts.get('safety_blocked',0))
    old_calibration = MAIN/'.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/calibration-thresholds.json'
    copied_calibration = ANALYSIS/'calibration-thresholds.json'
    if copied_calibration.exists():
        result['calibration_provenance'] = dict(source=str(old_calibration), copy=str(copied_calibration),
            sha256=hashlib.sha256(copied_calibration.read_bytes()).hexdigest(),
            identical_to_step2b=copied_calibration.read_bytes()==old_calibration.read_bytes(), recalibrated=False)
    result['availability_metadata'] = str(ANALYSIS/'availability-metadata-evaluation.json')
    result['run_records'] = [str(p) for p in (FRESH/'run.json',ANALYSIS/'run.json')]
    result['disk_cleanup_plan'] = str(MAIN/'.thesis-build/disk-hygiene/round3-plan-20261017.json')
    result['status'] = 'complete' if all(p['status']=='complete' for p in phases.values()) and not missing_vectors and not missing_images and unknown==0 else 'partial'
    MANIFEST.parent.mkdir(parents=True,exist_ok=True); write(MANIFEST,result)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
