"""Read-only post-run coefficient arithmetic; no model or image inference."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import m1_progressive_vote_margin as runner


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_stage(value,payload):
    c=value['selected_coefficients']
    if len(c)!=128 or not all(math.isfinite(x) for x in c):raise ValueError('Invalid coefficients')
    bits=''.join(str(int(sum(x>0 for x in c[i:i+8])>4)) for i in range(0,128,8))
    if bits!=value['bits']:raise ValueError('Recorded coefficient/word mismatch')
    groups=[]
    for b,target in enumerate(payload):
        values=c[8*b:8*b+8];signed=[x*(1 if target=='1' else -1) for x in values]
        order=sorted(signed,reverse=True)
        groups.append(dict(bit_index=b,intended=target,extracted=bits[b],positive_votes=sum(x>0 for x in values),
            intended_sign_votes=sum(x>0 for x in signed),fifth_signed_coefficient=order[4],
            reader_decision_signed_margin=order[4 if target=='1' else 3],signed_coefficients=signed,
            coefficients=values))
    return dict(bits=bits,matches=sum(a==b for a,b in zip(bits,payload)),
        wrong_bit_indices=[i for i,(a,b) in enumerate(zip(bits,payload)) if a!=b],groups=groups)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=args.input_dir/'run.json';run=json.loads(source.read_text())
    if run['outcome']!='completed' or run['config']!=runner.configuration():raise ValueError('Frozen completed source required')
    computed_gates=runner.gates(run['rows'])
    if computed_gates!=run['gates'] or not computed_gates['complete'] or not computed_gates['replay']:
        raise ValueError('Incomplete/inconsistent gates/replay')
    receipts={};summary=[]
    for row in run['rows']:
        for art in row['artifacts']:
            if Path(art['path']).name!=art['path']:raise ValueError('Unsafe artifact name')
            path=(args.input_dir/art['path']).resolve()
            if path.parent!=args.input_dir.resolve():raise ValueError('Unsafe artifact path')
            digest=sha(path)
            if digest!=art['sha256'] or path.stat().st_size!=art['bytes']:raise ValueError('Artifact receipt mismatch')
            receipts[art['path']]=digest
        trace_path=args.input_dir/(row['id']+'-trace.jsonl')
        traces=[json.loads(line) for line in trace_path.read_text().splitlines()]
        if len(traces)!=50 or [r['step_index'] for r in traces]!=list(range(50)):
            raise ValueError('Trace inventory incomplete')
        stages={name:summarize_stage(value,row['intended_payload']) for name,value in row['generation']['readout_stages'].items()}
        for channel,stage in [('clean','clean_rgb8'),('vae','additional_vae_rgb8')]:
            if stages[stage]['bits']!=row['conditions'][channel]['native_vae_dct']['bits']:
                raise ValueError('Primary/endpoint word mismatch')
        guided=[]
        for tr in traces:
            if tr['guided']:
                guided.append(dict(index=tr['step_index'],objective=tr['objective'],
                    ordinary=summarize_stage(tr['stages']['ordinary_predicted_clean'],row['intended_payload']),
                    corrected=summarize_stage(tr['stages']['corrected_predicted_clean'],row['intended_payload']),
                    noisy=summarize_stage(tr['stages']['actual_noisy_scheduler_output'],row['intended_payload'])))
        summary.append(dict(id=row['id'],seed=row['seed'],arm=row['arm'],payload=row['intended_payload'],
            quality=row['quality_to_new_C0'],stages=stages,guided=guided))
    report=dict(schema_version='m1-progressive-vote-results-v1',source=str(args.input_dir.resolve()),
        source_run_sha256=sha(source),source_commit=run['commit'],script_sha256=sha(Path(__file__)),
        source_duration_seconds=run['duration_seconds'],source_gates=computed_gates,
        artifact_count=len(receipts),artifact_receipts=receipts,source_clusters=4,rows=summary,
        caveat='Post hoc read-only coefficient arithmetic. No new model/image trials, calibration or family-exhaustion verdict.')
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),sha256=sha(args.output),artifact_count=len(receipts))))


if __name__=='__main__':main()
