"""Recorded-call analysis of the frozen S1 B/C/D development qualification."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import statistics
import subprocess

from journal_e3_s1_full_writer import validate_stage_b
from journal_e3_s1_full_t3 import validate_finished
from journal_e3_threat_analysis import analyze as immediate_analysis
from journal_e3_projection_analysis import analyze as projection_analysis

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def agreement(stats):
    value = stats['recorded_summary_agreement']
    return (not stats['issues'] and value['run_summary_matches_file'] and
            not value['mismatches'] and not value['endpoint_disagreements'])


def analyze(b, c=None, immediate=None, projection=None):
    rows, br = validate_stage_b(b)
    sources = []
    for row in rows:
        writer, supplier = row['writer'], row['supplier']
        quality = row['conditions']['clean']['quality_source']
        sources.append(dict(source_id=row['source_id'], status=row['status'],
            payload=row['payload'], quality=quality, branch=writer['quality_branch'],
            supplier_seconds=supplier['duration_seconds'], writer_seconds=writer['duration_seconds'],
            construction_seconds=supplier['duration_seconds']+writer['duration_seconds'],
            provenance=row['provenance']))
    construction = [row['construction_seconds'] for row in sources]
    report = dict(candidate='E3-S1', data_split='development', usd=0,
        analysis_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        raw_paths=dict(B=str(b)), raw_commits=dict(B=br['commit']),
        B=dict(pass_recomputed=True, summary=br['summary'], sources=sources,
            strict_quality_extrema=dict(min_psnr=min(r['quality']['psnr_db'] for r in sources),
                min_ssim=min(r['quality']['ssim_rgb'] for r in sources),
                max_lpips=max(r['quality']['lpips'] for r in sources)),
            per_source_construction_seconds=dict(mean=statistics.mean(construction),
                median=statistics.median(construction), minimum=min(construction), maximum=max(construction),
                scope='Supplier plus writer only; shared loading and evaluation included in parent wall separately.')),
        C=None, D_immediate=None, D_projection=None, measured_m1a_pass=False,
        official_lifecycle_verdict=None, human_verdict=None)
    a = Path(br['ancestry']['stage_a'])
    aw = read(a/'parent-wall.json'); bw = read(Path(b)/'parent-wall.json')
    # Stage A completion parent record includes its original failed process once.
    report['parent_wall_seconds'] = dict(A=aw.get('combined_parent_inclusive_seconds',
        aw.get('parent_inclusive_seconds',aw.get('duration_seconds'))), B=bw['parent_inclusive_seconds'])
    if c:
        cs, cr = validate_finished(c)
        if Path(cr['ancestry']['stage_b']).resolve()!=Path(b).resolve():
            raise ValueError('Stage C has different B ancestry')
        report['C'] = dict(pass_recomputed=cr['stage_c_pass_recomputed'], summary=cs)
        report['raw_paths']['C'], report['raw_commits']['C'] = str(c), cr['commit']
        report['parent_wall_seconds']['C'] = read(Path(c)/'parent-wall.json')['parent_inclusive_seconds']
    for label, path, function, key in (
        ('D_immediate',immediate,immediate_analysis,'immediate_continuity_pass'),
        ('D_projection',projection,projection_analysis,'projection_continuity_pass')):
        if path is None: continue
        run = read(Path(path)/'run.json')
        if run.get('candidate_kind')!='E3-S1' or Path(run['s1_stage_b_dir']).resolve()!=Path(b).resolve():
            raise ValueError('Threat panel has different candidate ancestry')
        if label=='D_projection' and (immediate is None or
                Path(run['immediate_dir']).resolve()!=Path(immediate).resolve()):
            raise ValueError('Projection has different immediate ancestry')
        stats = function(Path(path))
        report[label] = dict(pass_recomputed=bool(stats[key] and agreement(stats)), analysis=stats)
        report['raw_paths'][label], report['raw_commits'][label] = str(path), run['commit']
        report['parent_wall_seconds'][label] = stats['resources']['parent_inclusive_seconds']
    report['measured_m1a_pass'] = all(report[k] is not None and report[k]['pass_recomputed']
        for k in ('B','C','D_immediate','D_projection'))
    report['total_parent_wall_seconds'] = sum(report['parent_wall_seconds'].values())
    report['limitations'] = ('Twelve adaptively reused development sources; alpha-only construction; seen SD1.5 '
        'DDIM strengths/seeds and seen SDXL VAE. Safety-blocked rows remain unavailable. Reused calls are not '
        'independent replication. No population FPR, unseen-model generalization, incremental combined-binding '
        'benefit, cryptographic authorization or reference-specific same-owner attribution is established. '
        'Historical strict E3-B remains failed. This measured assessment does not advance official lifecycle gates.')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('stage-b-dir','stage-c-dir','immediate-dir','projection-dir'):
        p.add_argument('--'+name,type=Path,required=name=='stage-b-dir')
    p.add_argument('--output-dir',type=Path,required=True)
    a = p.parse_args()
    stats = analyze(a.stage_b_dir,a.stage_c_dir,a.immediate_dir,a.projection_dir)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    (a.output_dir/'analysis.json').write_text(json.dumps(stats,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines = ['# E3-S1 development assessment','',
        f"Measured full M1a pass: {stats['measured_m1a_pass']}. Official and human verdicts: not recorded.",'',
        f"B: strict quality and exact q/h/full 12/12; both VAE checked q 12/12. Quality extrema: {stats['B']['strict_quality_extrema']}.",
        f"Construction seconds per source: {stats['B']['per_source_construction_seconds']}."]
    if stats['C']:
        s = stats['C']['summary']
        for strength,v in s['strengths'].items():
            lines.append(f"T3 {strength}: S/Q/J/F {v['successes']}; available {v['observed']}/36; fixed comparison {v['intersection']}.")
        lines.append(f"T3 negatives {s['negative_any_detections']}/{s['observed_negative_calls']} observed; {s['unavailable_negative_calls']} unavailable of 504 planned.")
    for key in ('D_immediate','D_projection'):
        lines.append(f"{key}: "+('pending' if stats[key] is None else str(stats[key]['pass_recomputed'])))
    lines += ['',f"Parent-inclusive seconds: {stats['parent_wall_seconds']}; total {stats['total_parent_wall_seconds']:.3f}, USD 0.",
        '',stats['limitations'],'','Raw paths: '+json.dumps(stats['raw_paths']),
        'Raw commits: '+json.dumps(stats['raw_commits'])]
    (a.output_dir/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__': main()
