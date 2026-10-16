"""Render saved step-2a numeric ROC points as a standalone SVG; no models or tuning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(screen_dir, output):
    curves = {}
    for name in ('D1', 'D2', 'D3'):
        path = screen_dir / f'{name}-roc.json'
        if path.exists():
            curves[name] = json.loads(path.read_text(encoding='utf-8'))['points']
    if not curves:
        raise ValueError('No saved D1/D2/D3 numeric ROC files found')
    left, top, width, height = 90, 85, 620, 460
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="650" viewBox="0 0 850 650">',
           '<rect width="850" height="650" fill="white"/>',
           '<g font-family="Arial,sans-serif" fill="#222">',
           '<text x="425" y="30" text-anchor="middle" font-size="21">Registry development screen: pooled descriptor ROC</text>',
           '<text x="425" y="55" text-anchor="middle" font-size="14">Consulted development data; descriptor similarity only; pointer excluded</text>']
    for k in range(6):
        value = k / 5
        x, y = left + value * width, top + (1 - value) * height
        svg += [f'<path d="M {x} {top} V {top + height} M {left} {y} H {left + width}" stroke="#e5e5e5" fill="none"/>',
                f'<text x="{x}" y="{top + height + 23}" text-anchor="middle" font-size="13">{value:.1f}</text>',
                f'<text x="{left - 14}" y="{y + 4}" text-anchor="end" font-size="13">{value:.1f}</text>']
    svg += [f'<path d="M {left} {top} V {top + height} H {left + width}" stroke="#222" stroke-width="1.5" fill="none"/>',
            f'<path d="M {left} {top + height} L {left + width} {top}" stroke="#999" stroke-dasharray="6 5" fill="none"/>']
    styles = dict(D1=('#0072b2','Native fine'), D2=('#d55e00','DINOv2 CLS'), D3=('#009e73','CLIP seven-view'))
    for index, (name, points) in enumerate(curves.items()):
        color, label = styles[name]
        xy = []
        for point in points:
            x, y = point['fpr'], point['tpr']
            if not 0 <= x <= 1 or not 0 <= y <= 1:
                raise ValueError(f'Invalid ROC rate in {name}')
            coordinate = f'{left + x * width:.3f},{top + (1 - y) * height:.3f}'
            if not xy or xy[-1] != coordinate:
                xy.append(coordinate)
        svg.append(f'<polyline points="{" ".join(xy)}" stroke="{color}" stroke-width="2.2" fill="none"/>')
        y = 115 + index * 29
        svg += [f'<path d="M 730 {y} H 755" stroke="{color}" stroke-width="3"/>',
                f'<text x="763" y="{y + 4}" font-size="13">{name}</text>',
                f'<text x="730" y="{y + 19}" font-size="10">{label}</text>']
    svg += ['<text x="400" y="594" text-anchor="middle" font-size="16">Observed false-positive rate</text>',
            '<text x="27" y="315" transform="rotate(-90 27 315)" text-anchor="middle" font-size="16">Observed true-positive rate</text>',
            '<text x="425" y="628" text-anchor="middle" font-size="12">Thresholds are exploratory. Unavailable comparisons are excluded; no population FPR claim.</text>',
            '</g></svg>']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(svg) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screen-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.screen_dir / 'pooled-descriptor-roc.svg'
    render(args.screen_dir, output)
    print(output)


if __name__ == '__main__':
    main()
