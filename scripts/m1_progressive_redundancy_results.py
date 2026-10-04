"""Read-only primary-result and matched-replay stage summary; no model inference."""
import argparse
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import m1_progressive_t3 as validator
from m1_progressive_vote_results import summarize_stage


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    snapshot=validator.source_snapshot(args.input_dir,'a232861b4062025afe501e27916b3ed96528df750aff8fb8774891aacec8d5e0')
    source=json.loads((args.input_dir/'run.json').read_text());rows=[]
    for row in source['rows']:
        stages={name:summarize_stage(stage,row['intended_payload']) for name,stage in row['generation']['readout_stages'].items()}
        trace=[json.loads(line) for line in (args.input_dir/(row['id']+'-trace.jsonl')).read_text().splitlines()]
        rows.append(dict(id=row['id'],seed=row['seed'],arm=row['arm'],payload=row['intended_payload'],
            embedding_margin=row['generation']['embedding_margin'],quality=row['quality_to_new_C0'],stages=stages,
            objectives=[dict(index=r['step_index'],before=r['objective']['objective_value'],
                after=r['objective']['after_intended_update']['objective_value'],margin=r['objective']['margin'])
                for r in trace if r['guided']]))
    pairs=[]
    for row in rows:
        if not row['arm'].startswith('C-Q5M5'):continue
        old_arm='C-Q5-replay-complement' if row['arm'].endswith('complement') else 'C-Q5-replay'
        old=next(r for r in rows if r['seed']==row['seed'] and r['arm']==old_arm)
        pairs.append(dict(seed=row['seed'],payload=row['payload'],old_id=old['id'],candidate_id=row['id'],
            old_psnr_db=old['quality']['psnr_db'],candidate_psnr_db=row['quality']['psnr_db'],
            psnr_difference_db=row['quality']['psnr_db']-old['quality']['psnr_db'],
            measured_pixel_mse_ratio=row['quality']['mse_rgb8']/old['quality']['mse_rgb8'],
            old_matches={n:s['matches'] for n,s in old['stages'].items()},
            candidate_matches={n:s['matches'] for n,s in row['stages'].items()}))
    candidate=[r for r in rows if r['arm'].startswith('C-Q5M5')]
    groups={}
    for label,selected in [('old_q5_replays',[r for r in rows if r['arm'].startswith('C-Q5-replay')]),('candidate',candidate)]:
        groups[label]=dict(n=8,source_clusters=4,quality_passes=sum(r['quality']['quality_admissible'] for r in selected),
            metrics={key:dict(mean=statistics.mean(r['quality'][key] for r in selected),minimum=min(r['quality'][key] for r in selected),maximum=max(r['quality'][key] for r in selected)) for key in ('psnr_db','ssim_rgb','lpips')},
            stages={name:dict(exact=sum(r['stages'][name]['matches']==16 for r in selected),present=sum(r['stages'][name]['matches']>=14 for r in selected),mean_matches=statistics.mean(r['stages'][name]['matches'] for r in selected)) for name in validator.parent.STAGES})
    result=dict(schema_version='m1-progressive-redundancy-results-v1',source_snapshot=snapshot,
        script_sha256=validator.sha(Path(__file__)),helper_sha256={name:validator.sha(Path(__file__).parent/name) for name in ('m1_progressive_t3.py','m1_progressive_vote_results.py')},
        source_duration_seconds=source['duration_seconds'],artifact_bytes=sum(a['bytes'] for r in source['rows'] for a in r['artifacts']),
        rows=rows,matched_pairs=pairs,groups=groups,t3_result=None,
        caveat='Read-only summary of completed primary screen. Four reused synthetic clusters; oracle stages are not primary detections. No new image/model trials or independent milestone review.')
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),sha256=validator.sha(args.output))))


if __name__=='__main__':main()
