"""Render the exploratory descriptor-screen results directly from retained receipts."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    slugs = ['instance-ceiling', 'stable-instance-cd1', 'balanced-instance-bi1', 'fine-gaussian-fg128']
    labels = ['Original h\n32 bits, radius 6', 'CD1: coarse\n32 bits, radius 6',
              'BI1: balanced\n32 bits, radius 6', 'FG128: fine Gaussian\n128 bits, radius 44']
    for i, slug in enumerate(slugs):
        path = args.runs / ('20261014-' + slug) / 'run.json'
        run = json.loads(path.read_text())
        assert run['outcome'] == 'completed'
        s = run['summary']
        rows.append(dict(label=labels[i], source=str(path), commit=run['commit'],
            positive=s['T3_0.2']['O_J' if i == 0 else 'O_DJ'],
            sibling=None if i == 0 else s['sibling_new_acceptances'],
            impostor=None if i == 0 else s['impostor_matches']['canonical'],
            passes=run['oracle_advance_gate' if i == 0 else 'advance_gate']))
    assert not any(r['passes'] for r in rows)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'axes.titleweight': 'bold'})
    fig = plt.figure(figsize=(13, 7.2), facecolor='white')
    ax = fig.add_axes([.22, .30, .37, .47])
    for i, row in enumerate(rows):
        ax.barh(i, row['positive'], height=.50, color='#325b7c')
        ax.text(row['positive'] + .3, i, f"{row['positive']}/18", va='center', fontsize=11)
    ax.set_yticks(range(4), labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 20)
    ax.set_xticks([0, 6, 12, 18])
    ax.set_xlabel('Successful oracle checks / 18 attacked images')
    ax.set_title('Regeneration stability', loc='left', y=1.10, pad=0)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#e3e6e9')
    ax.tick_params(axis='y', length=0, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    table = fig.add_axes([.63, .30, .35, .47], sharey=ax)
    table.set_xlim(0, 1)
    table.axis('off')
    table.set_title('Specificity guards', loc='left', y=1.10, pad=0)
    table.text(.02, 1.02, 'New sibling matches', transform=table.transAxes, fontsize=10, color='#44515b')
    table.text(.53, 1.02, 'Real-impostor matches', transform=table.transAxes, fontsize=10, color='#44515b')
    for i, row in enumerate(rows):
        for x, key, n in [(.10, 'sibling', 6), (.65, 'impostor', 552)]:
            count = row[key]
            value = 'Not tested' if count is None else f'{count}/{n}'
            table.text(x, i, value, va='center', fontsize=12,
                       color='#a34133' if count else '#33424e')
    fig.text(.04, .94, 'No tested replacement passed the complete development gate',
             fontsize=18, weight='bold', color='#182c3a')
    fig.text(.04, .885, 'Perfect instance-payload transport assumed; actual checked semantic recovery retained. T3 strength 0.2.',
             fontsize=11, color='#44515b')
    fig.text(.04, .10,
        'Exploratory, consulted development data: six sources × three seeds. These are descriptor oracles, not new watermark systems.\n'
        'FG128 changes representation, bit length and tolerance; it is not a matched-FPR comparison. Its two ordered impostor matches\n'
        'are one pair (30/544) in both directions. Clean/VAE and other mandatory guards are reported in the accompanying results.',
        fontsize=10, color='#44515b', linespacing=1.55)
    fig.savefig(args.output_dir / 'descriptor-round.png', dpi=180)
    fig.savefig(args.output_dir / 'descriptor-round.svg')
    (args.output_dir / 'plotted-data.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(args.output_dir / 'descriptor-round.png')


if __name__ == '__main__':
    main()
