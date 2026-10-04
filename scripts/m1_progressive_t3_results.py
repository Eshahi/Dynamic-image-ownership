"""Read-only fixed T3 receipt, raw-word and finite-branch analysis; no inference."""
import argparse
import json
import math
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import m1_progressive_t3 as protocol
from m1_progressive_vote_results import summarize_stage


def require(value, message):
    if not value:
        raise ValueError(message)


def stats(values):
    return dict(n=len(values), mean=statistics.mean(values), median=statistics.median(values),
                sample_sd=statistics.stdev(values), minimum=min(values), maximum=max(values))


def analyze(folder):
    folder=Path(folder).resolve(); source=folder/'run.json'; source_sha=protocol.sha(source)
    run=json.loads(source.read_text())
    require(run['outcome']=='completed' and run['schema_version']==protocol.VERSION, 'Incomplete or wrong run')
    require(run['missing_condition_ids']==[], 'Missing conditions')
    snapshot=protocol.source_snapshot(run['config']['source_dir'], run['config']['source_run_sha256'])
    require(snapshot==run['source_snapshot'], 'Source snapshot differs')
    require(run['assets']==snapshot['source_assets'], 'Asset receipts differ')
    require(run['config']==protocol.configuration(snapshot), 'Frozen configuration differs')
    require(json.loads((folder/'manifest.json').read_text())==run['config'], 'Copied manifest differs')
    require(protocol.sha(folder/'manifest.json')==run['manifest_sha256'], 'Manifest hash differs')
    require(run['planned_counts']==run['config']['planned_counts'], 'Planned inventory differs')
    protocol.verify_source_code(run)
    rows=run['rows']; gate=protocol.gates(rows)
    require(gate['complete'] and gate==run['gates'], 'Gate recomputation differs')
    require(json.loads((folder/'conditions.json').read_text())==rows, 'Conditions copy differs')
    events=[json.loads(line) for line in (folder/'rows.jsonl').read_text().splitlines()]
    completed=[event for event in events if event.get('id') and event['outcome']=='completed']
    require(len(completed)==24, 'Completed event inventory differs')
    inputs={item['generation_id']:item for item in snapshot['inputs']}
    summary=[]; artifact_bytes=0
    for row in rows:
        require(next(event for event in completed if event['id']==row['id'])==dict(next(event for event in completed if event['id']==row['id']), **row), 'Completed event differs')
        protocol.checked_artifact(folder, row['artifact']); artifact_bytes+=row['artifact']['bytes']
        require(row['source_png_receipt']==inputs[row['source_id']]['artifact'], 'Source PNG receipt differs')
        require(row['safety_flag'] is False and row['human_visual_verdict'] is None, 'Safety/human status differs')
        require(row['attack_trace']['unet_timesteps']==row['actual_timesteps']==row['attack_trace']['scheduler_step_timesteps'], 'Actual attack traces differ')
        stage=row['native_coefficient_trace']
        word=protocol.word_from_coefficients(stage)
        require(word==row['readout']['native_vae_dct']['bits'], 'Primary coefficient word differs')
        require(set(row['readout'])=={'native_vae_dct','image_dct_diagnostic','native_vae_dct_seconds','image_dct_diagnostic_seconds','extract_both_seconds'}, 'Unexpected readout schema')
        for name in ('native_vae_dct','image_dct_diagnostic'):
            readout=row['readout'][name]
            protocol.parent.original.validate_readout(readout)
            for key,value in protocol.parent.evaluate_word(readout['bits'],row['intended_payload']).items():
                require(readout[key]==value, 'Raw-word evaluation differs')
        quality=row['quality_vs_same_arm_clean']
        require(all(type(quality[k]) in (int,float) and math.isfinite(quality[k]) for k in ('psnr_db','ssim_rgb','lpips')), 'Nonfinite quality')
        summary.append(dict(id=row['id'],seed=row['seed'],arm=row['arm'],strength=row['strength'],
            source_png_receipt=row['source_png_receipt'],artifact=row['artifact'],
            readout=row['readout'],stage=summarize_stage(stage,row['intended_payload']),quality=quality))
    require(sum(row['unet_calls'] for row in rows)==run['observed_unet_calls']==120, 'UNet budget inventory differs')
    require(run['duration_seconds']<=180 and artifact_bytes<=150*1024**2, 'Recorded budget exceeded')
    require(max(row['peak_allocated_bytes'] for row in rows)<=run['effective_gpu_budget_bytes'], 'Recorded GPU peak exceeds cap')
    groups={}
    for strength in protocol.STRENGTHS:
        marked=[row for row in summary if row['strength']==strength and row['arm']!='C0-replay']
        null=[row for row in summary if row['strength']==strength and row['arm']=='C0-replay']
        seed_means=[statistics.mean(row['stage']['matches'] for row in marked if row['seed']==seed) for seed in range(1000,1004)]
        groups[str(strength)]=dict(marked_presence=sum(row['stage']['matches']>=14 for row in marked),
            marked_exact=sum(row['stage']['matches']==16 for row in marked),marked_denominator=8,
            marked_match_range=[min(row['stage']['matches'] for row in marked),max(row['stage']['matches'] for row in marked)],
            seed_mean_matches=stats(seed_means),seed_means=seed_means,
            c0_absence=sum(not row['readout']['native_vae_dct']['original_present'] and not row['readout']['native_vae_dct']['complement_present'] for row in null),c0_denominator=4,
            marked_quality_seed_means={key:stats([statistics.mean(row['quality'][key] for row in marked if row['seed']==seed) for seed in range(1000,1004)]) for key in ('psnr_db','ssim_rgb','lpips')},
            native_wrong_panel_findings=sum(row['readout']['native_vae_dct']['wrong_payload_queries']['false_findings'] for row in summary if row['strength']==strength),native_wrong_panel_queries=12*64)
    require(protocol.sha(source)==source_sha, 'Run changed during analysis')
    return dict(schema_version='m1-progressive-t3-results-v1',source_dir=str(folder),source_run_sha256=source_sha,
        source_commit=run['commit'],manifest_sha256=run['manifest_sha256'],primary_source_sha256=snapshot['source_run_sha256'],
        analyzer_sha256=protocol.sha(Path(__file__)),helper_sha256=protocol.sha(Path(protocol.__file__)),
        spec_sha256=protocol.sha(protocol.ROOT/'research/m1-progressive-redundancy-design.md'),
        duration_seconds=run['duration_seconds'],artifact_count=24,artifact_bytes=artifact_bytes,
        observed_unet_calls=120,peak_allocated_bytes=max(row['peak_allocated_bytes'] for row in rows),
        gates=gate,groups=groups,rows=summary,
        decision='close_scalar_vote_window_branch' if not gate['joint_pass'] else 'mandatory_expansion_and_binding_design',
        exclusions=[],inference='Exploratory four reused source clusters; no confidence interval, significance test, independent FPR calibration or family-wide impossibility claim.')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--input-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=analyze(args.input_dir)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),sha256=protocol.sha(args.output),gates=result['gates'],groups=result['groups'])))


if __name__=='__main__':main()
