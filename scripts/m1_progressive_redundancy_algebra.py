"""Two fixed coefficient-space probes; no model or pixel inference."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def coefficients(row,stage):
    return [v for g in row['stages'][stage]['groups'] for v in g['coefficients']]


def project(coeff,payload,votes,margin):
    result=coeff[:]
    for bit,target in enumerate(payload):
        sign=1 if target=='1' else -1
        chosen=sorted(range(8*bit,8*bit+8),key=lambda i:(max(0,margin-sign*coeff[i])**2,i))[:votes]
        for index in chosen:result[index]=sign*max(margin,sign*coeff[index])
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if sha(args.input)!='bedb59886b71a432a42d09b8d0e8dcf287c224d468e2b347db275fd49f0f5df0':
        raise ValueError('Frozen stage-diagnosis receipt differs')
    source=json.loads(args.input.read_text());rows=[]
    for row in source['rows']:
        if not row['arm'].startswith('C-Q5'):continue
        c0=next(r for r in source['rows'] if r['seed']==row['seed'] and r['arm']=='C0-replay')
        baseline=coefficients(c0,'terminal_predecode')
        terminal=coefficients(row,'terminal_predecode')
        observed=coefficients(row,'additional_vae_rgb8')
        errors=[b-a for a,b in zip(terminal,observed)]
        costs={};probes={}
        for votes,margin in [(5,.3),(6,.3),(5,.5)]:
            key=f'votes{votes}-margin{margin}'
            projected=project(baseline,row['payload'],votes,margin)
            costs[key]=sum((a-b)**2 for a,b in zip(projected,baseline))
            if margin==.3 and votes==5:continue
            projected_terminal=project(terminal,row['payload'],votes,margin)
            stress=[x+e for x,e in zip(projected_terminal,errors)]
            word=''.join(str(int(sum(v>0 for v in stress[i:i+8])>4)) for i in range(0,128,8))
            probes[key]=dict(word=word,matches=sum(a==b for a,b in zip(word,row['payload'])),
                wrong_bit_indices=[i for i,(a,b) in enumerate(zip(word,row['payload'])) if a!=b])
        rows.append(dict(id=row['id'],seed=row['seed'],payload=row['payload'],
            observed_q5_psnr_db=row['quality']['psnr_db'],
            pixel_mse_headroom_factor_to_35db=10**((row['quality']['psnr_db']-35)/10),
            c0_projection_squared_costs=costs,
            relative_costs={key:value/costs['votes5-margin0.3'] for key,value in costs.items()},
            frozen_channel_residual_stress=probes))
    result=dict(schema_version='m1-progressive-redundancy-algebra-v1',script_sha256=sha(Path(__file__)),
        input_sha256=sha(args.input),input_source_run_sha256=source['source_run_sha256'],rows=rows,
        caveat='Exact algebra only: orthogonal coefficient projection, then optionally adding the old observed terminal-to-extra-VAE coefficient residual unchanged. The VAE is nonlinear and actual changed trajectories/coefficients/channel residuals are unknown. This is not a generated image, quality prediction, actual channel result or additional independent trial.')
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),sha256=sha(args.output))))


if __name__=='__main__':main()
