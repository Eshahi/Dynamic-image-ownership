"""Render frozen M2 endpoints as tables/figures; no new inference or tuning."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--endpoints', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--plotting-site', type=Path, required=True)
    args = p.parse_args()
    sys.path.insert(0, str(args.plotting_site))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    data = json.loads(args.endpoints.read_text(encoding='utf-8'))
    # Avoid accidentally deriving a manuscript from a different run.
    if sha(args.endpoints) != '59d90d0f7d11aff86f11674a3c0c31061663d9212dbcfd9d739a7b724d6d36bd':
        raise ValueError('Expected retained coco512-confirm-rerun-1 endpoints')
    root = args.out
    for folder in ('tables', 'figures', 'evidence'):
        (root / folder).mkdir(parents=True, exist_ok=True)
    artifacts = []

    def table(name, columns, rows, note):
        cpath, mpath = root/'tables'/f'{name}.csv', root/'tables'/f'{name}.md'
        with cpath.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        def fmt(x):
            return f'{x:.6g}' if isinstance(x, float) else str(x)
        lines = ['| '+' | '.join(columns)+' |', '| '+' | '.join(['---']*len(columns))+' |']
        lines += ['| '+' | '.join(map(fmt, row))+' |' for row in rows]
        mpath.write_text('\n'.join(lines)+'\n\n'+note+'\n', encoding='utf-8')
        artifacts.extend([cpath, mpath])

    methods = ('f5-r2', 'v5-r3')
    clean_rows, quality_rows, t3_rows, paired_rows, threat_rows = [], [], [], [], []
    for method in methods:
        cells = data['methods'][method]
        for key in ('C1_correct_both_match','C0_correct_any_found','C0_wrong_any_found','C1_wrong_any_found'):
            c = cells['clean'][key]
            bound_key = 'lower_one_sided' if c['event_kind']=='positive_success' else 'upper_one_sided'
            clean_rows.append([method,key,c['conservative_events'],c['planned'],c['conservative']['rate'],bound_key,c['conservative'][bound_key]])
        q = cells['clean']['quality']
        for key in ('psnr_gt_35','ssim_gt_0_9','lpips_lt_0_1','joint'):
            quality_rows.append([method,key,q[key]['count'],q[key]['planned']])
        for condition, c in cells['t3'].items():
            total, checked = c['source_majority_semantic'], c['source_majority_semantic_checked']
            t3_rows.append([method,condition,total['conservative_events'],total['planned'],total['conservative']['lower_one_sided'],checked['conservative_events'],checked['conservative']['lower_one_sided'],c['rows']['semantic']['conservative_events'],c['rows']['semantic_checked']['conservative_events'],c['rows']['semantic_assumed']['conservative_events'],c['rows']['semantic']['planned']])
        for threat, keys in (
            ('t4',('false_donor_full_attribution_pair_any','donor_delivery_witness_pair_any')),
            ('t5',('C0_false_full_match_pair_any','C1_false_full_match_pair_any','C0_any_found_pair_any','C1_any_found_pair_any')),
        ):
            for key in keys:
                c = cells[threat][key]
                threat_rows.append([method,threat,key,c['conservative_events'],c['planned'],c['conservative']['upper_one_sided']])
    for rule, conditions in data['paired_t3_source_majority'].items():
        for condition, c in conditions.items():
            paired_rows.append([rule,condition,c['f5_only'],c['v5_only'],c['both'],c['neither'],c['exact_sign_test_p_two_sided'] if c['exact_sign_test_p_two_sided'] is not None else 'n/a'])
    table('m2-clean', ['Method','Cell','Events','Sources','Rate','Bound kind','Bound'],clean_rows,
          'One-sided 95% Clopper-Pearson bounds, per cell. Three negative cells share sources; secondary both_match summaries reuse the same calls. No pooled independent n=900 inference.')
    table('m2-quality', ['Method','Metric','Passing sources','Sources'],quality_rows,
          'Strict proposal thresholds; joint requires all three. These are counts, not a universal quality acceptance verdict.')
    table('m2-t3', ['Method','Condition','Semantic sources','Sources','Semantic LB','Checked sources','Checked LB','Semantic rows','Checked rows','Assumed rows','Rows'],t3_rows,
          'DDIM sources succeed on at least 2/3 seeds; VAE has one outcome per source. Rows are clustered repeats. Lower bounds are one-sided 95%, per cell, without simultaneous coverage.')
    table('m2-paired-t3', ['Rule','Condition','F5 only','v5 only','Both','Neither','Two-sided exact p'],paired_rows,
          'Frozen descriptive paired sign tests on source discordances. No multiplicity adjustment or new inferential analysis.')
    table('m2-t4-t5', ['Method','Threat','Cell','Events','Pairs','Upper bound'],threat_rows,
          'One-sided 95% Clopper-Pearson upper bounds, per cell. Delivery witness is a positive descriptive observation, not a false-attribution error. T4 same-owner pair 5 and T5 pairs 9/20/29 are excluded only from the declared different-owner rates.')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5), sharey=True)
    conditions = ('vae','ddim-0.05','ddim-0.1','ddim-0.2','ddim-0.4')
    labels = ('VAE','0.05','0.10','0.20','0.40')
    for ax, key, title in zip(axes, ('source_majority_semantic','source_majority_semantic_checked'),
                              ('A  All semantic detections','B  Decoded and compared only')):
        for method, color, offset, marker in zip(methods, ('#126b8a','#b25b36'),(-.12,.12),('o','s')):
            cells = [data['methods'][method]['t3'][c][key] for c in conditions]
            y = np.array([c['conservative_events'] for c in cells])
            lower = np.array([c['conservative']['lower_one_sided']*c['planned'] for c in cells])
            x = np.arange(len(conditions))+offset
            ax.errorbar(x,y,yerr=np.vstack((y-lower,np.zeros_like(y))),color=color,fmt=marker,
                        markersize=5,capsize=3,elinewidth=1.2,label={'f5-r2':'F5 r2','v5-r3':'v5 r3'}[method])
            for xx, yy in zip(x,y):
                ax.annotate(str(yy),(xx,yy),xytext=(-6 if offset<0 else 7,7),textcoords='offset points',ha='center',color=color,fontsize=9)
        ax.set_title(title,loc='left',fontsize=11,pad=12)
        ax.set_xticks(range(5),labels)
        ax.set_xlabel('Regeneration condition / DDIM img2img strength')
        ax.set_xlim(-.48,4.48)
        ax.set_ylim(0,33.7)
        ax.set_yticks(range(0,31,5))
        ax.grid(axis='y',alpha=.16)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Successful sources (out of 30)')
    handles, legends = axes[0].get_legend_handles_labels()
    fig.legend(handles,legends,loc='lower center',bbox_to_anchor=(.5,.085),ncol=2,frameon=False)
    fig.text(.5,.027,'DDIM: majority of three seeds. Whiskers: one-sided 95% lower bounds, per cell.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.075,right=.985,top=.875,bottom=.255,wspace=.14)
    for ext in ('png','pdf','svg'):
        path = root/'figures'/f'm2-t3-survival.{ext}'
        fig.savefig(path,dpi=220,metadata={'Creator':'Codex agent'} if ext=='pdf' else None)
        if ext == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
        artifacts.append(path)
    plt.close(fig)
    receipt = {
        'status':'derived presentation of retained endpoints; no experiment',
        'run_id':'coco512-confirm-rerun-1','input':str(args.endpoints.resolve()),'input_sha256':sha(args.endpoints),
        'script':str(Path(__file__).resolve()),'script_sha256':sha(__file__),
        'arguments':sys.argv[1:],'matplotlib_version':matplotlib.__version__,
        'rule':'Copy frozen counts and existing bounds; no new inference, filtering, threshold changes, or image inspection.',
        'artifacts':[{'path':str(path.relative_to(root)).replace('\\','/'),'sha256':sha(path)} for path in artifacts],
    }
    (root/'evidence/m2-exhibits-provenance.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    for folder in ('tables','figures'):
        (root/folder/'provenance.json').write_text(json.dumps({'artifacts':[a for a in receipt['artifacts'] if a['path'].startswith(folder+'/')],'source_receipt':'../evidence/m2-exhibits-provenance.json'},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tables':5,'figure_formats':3,'run_id':receipt['run_id']}))


if __name__ == '__main__':
    main()
