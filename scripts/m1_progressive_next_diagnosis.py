"""Read-only CPU arithmetic on retained C-L100 tensors; no model inference."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

VERSION = 'm1-progressive-next-diagnosis-v1'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args=ap.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    receipts={}
    def read(name):
        path=args.input_dir/name
        receipts[name]=sha(path)
        if name.endswith('.npy'):
            return np.load(path, allow_pickle=False).astype(np.float64)
        return [json.loads(line) for line in path.read_text().splitlines()]
    rows=[]
    for seed in range(1000,1004):
        c0=read(f'seed{seed}-C0-replay-terminal_latent.npy')
        tr0=read(f'seed{seed}-C0-replay-trace.jsonl')
        c=np.array(tr0[-1]['stages']['actual_noisy_scheduler_output']['selected_coefficients'])
        for arm in ['C-L100', 'C-L100-complement']:
            z=read(f'seed{seed}-{arm}-terminal_latent.npy')
            tr=read(f'seed{seed}-{arm}-trace.jsonl')
            last=tr[-1]['stages']['actual_noisy_scheduler_output']
            y=np.repeat([1 if bit=='1' else -1 for bit in last['intended_payload']],8)
            d=np.array(last['selected_coefficients'])-c
            energy=float(np.sum((z-c0)**2))
            costs={}
            for margin in [.1,.3,.5]:
                violation=np.maximum(0,margin-y*c)
                grouped=violation.reshape(16,8)**2
                costs[str(margin)]={
                    'equality_squared_distance':float(np.sum((c-margin*y)**2)),
                    'all_eight_margin_squared_distance':float(np.sum(violation**2)),
                    'five_vote_margin_squared_distance':float(np.sort(grouped,axis=1)[:,:5].sum()),
                }
            rows.append(dict(seed=seed,arm=arm,c0_selected_rms=float(np.sqrt(np.mean(c*c))),
                total_terminal_squared_distance=energy,
                selected_squared_distance=float(np.sum(d*d)),
                selected_energy_fraction=float(np.sum(d*d)/energy),
                other_channels_squared_distance=float(np.sum((z[:,1:]-c0[:,1:])**2)),
                algebraic_c0_projection_costs=costs,
                trace=[dict(index=r['step_index'],timestep=r['timestep'],q=r['q_t'],
                    ordinary_mse=r['stages']['ordinary_predicted_clean']['target_mse'],
                    noisy_matches=r['stages']['actual_noisy_scheduler_output']['intended_matches'],
                    local_displacement=r['local_scheduler_displacement_l2'])
                    for r in tr if r['step_index'] in [25,35,40,44,45,46,47,48,49]]))
    report=dict(schema_version=VERSION,source=str(args.input_dir.resolve()),
        script_sha256=sha(Path(__file__)),source_receipts=receipts,
        method='float64 arithmetic on saved tensors and recorded coefficient traces; no model/image inference',
        caveat='Projection costs are squared Euclidean latent coefficient distances, not image-quality or channel-survival predictions. No new scientific image trials.',
        source_clusters=4,rows=rows)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output), 'sha256':sha(args.output), 'rows':len(rows)}))

if __name__=='__main__':
    main()
