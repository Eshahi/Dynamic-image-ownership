"""Render the terminal E3-RC1 receipt as descriptive tables; no scientific imports."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def flag(value):
    return 'missing' if value is None else str(int(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.run.read_bytes()
    run = json.loads(raw)
    if run['outcome'] not in ('completed', 'stopped'):
        raise ValueError('Only a terminal receipt may be reported')
    rows = run['cells']
    pairs = [(30, 72), (73, 89), (127, 165), (309, 370), (436, 450), (459, 471)]
    expected = {(r, d, c) for r, d in pairs for c in ('RR', 'DR', 'RD', 'DD')}
    if len(rows) != 24 or {(c['recipient'], c['donor'], c['cell']) for c in rows} != expected:
        raise ValueError('Unexpected or duplicate planned cells')
    summary = run['summary']
    rr_summary = summary['fixed_denominators']['RR']
    text = [
        '# E3-RC1 constructed-positive and component-control results', '',
        'Exploratory development evidence, 2026-10-13. The prospective '
        '[protocol](binding-positive-protocol.md) is unchanged. This is a public '
        'initializer rewrite study, not admitted full-E3 output or human assessment.', '',
        f"Construction commit: `{run['commit']}`. Outcome: **{run['outcome']}**. "
        f"Inclusive duration: **{run['duration_seconds']:.6f} s**. "
        f"Completed native PGD steps: **{run['completed_pgd_steps']}/3000**; "
        f"forward attempts: {run['attempted_forward_steps']}. "
        f"Deadline overrun: {run['deadline_overrun_seconds']:.6f} s. Local USD 0.", '',
        f"The same-source RR controls have exact delivery in {rr_summary['modes']['none']['D']}/6, "
        f"combined acceptance in {rr_summary['modes']['combined']['F']}/6, and strict quality "
        f"against both references in {rr_summary['quality_both']}/6. There are "
        f"{summary['primary_witness_count']} quality-qualified primary component witnesses. "
        'Individual witnesses do not override the all-six positive-control gate.', '',
        'The six pairs, four cells and thresholds were fixed before execution. '
        'All branches start from the same retained recipient. Targets come from '
        'pre-intervention public q and native h; detection receives only the '
        'rewritten suspect. Original images enter quality evaluation only. '
        'Supplied q/h enter endpoint comparison outside the detector.', '',
        '## Fixed-denominator results', '',
        'N=6 planned images per cell. Q/H are exact readable supplied payloads; '
        'D=Q and H; F is full acceptance. None-mode D checks physical delivery. '
        'Mode decisions are paired and share extraction. Quality must pass '
        'PSNR >35 dB, SSIM >.9 and LPIPS <.1 against both recipient and canonical '
        'source. Missing calls are separately counted, never successful rejection.', '',
        '| Cell | Completed /6 | Quality vs recipient /6 | Quality vs canonical /6 | Both quality /6 | None Q /6 | None H /6 | None D /6 | Combined F /6 | Semantic-only F /6 | Perceptual-only F /6 | None F /6 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for label, s in summary['fixed_denominators'].items():
        modes = s['modes']
        values = [label, s['completed'], s['quality_recipient'], s['quality_canonical'],
                  s['quality_both'], modes['none']['Q'], modes['none']['H'], modes['none']['D']]
        values += [modes[mode]['F'] for mode in ('combined', 'semantic_only', 'perceptual_only', 'none')]
        text.append('| ' + ' | '.join(map(str, values)) + ' |')
    text += ['', 'None F is not an ownership endpoint. Counts above retain the planned '
             'denominator; the following availability and selected-subset counts '
             'must accompany them.', '',
             '| Cell | Observed modes (combined/semantic/perceptual/none) /6 each | Delivered and both-quality subset | F within subset (combined/semantic/perceptual/none) | Primary witness | Reciprocal witness |',
             '|---|---|---:|---|---:|---:|']
    for label, s in summary['fixed_denominators'].items():
        subset = [c for c in rows if c['cell'] == label]
        observed = '/'.join(str(s['modes'][m]['observed']) for m in ('combined', 'semantic_only', 'perceptual_only', 'none'))
        conditional = s['conditional_delivered_quality']
        selected_fs = '/'.join(str(conditional['modes'][m]['F']) for m in ('combined', 'semantic_only', 'perceptual_only', 'none'))
        text.append(f"| {label} | {observed} | {conditional['denominator']} | {selected_fs} | "
                    f"{sum(c.get('primary_witness') is True for c in subset)} | "
                    f"{sum(c.get('reciprocal_witness') is True for c in subset)} |")
    beta = summary['beta']
    text += ['', '## Predeclared conclusions', '',
        f"- Constructed-positive gate: **{summary['positive_control_gate']}**. "
        f"Nonidentical RR controls: {summary['nonidentical_RR']}/6.",
        f"- Primary eligible witness count: {summary['primary_witness_count']}; "
        f"pairs {summary['primary_witness_pairs']}. Repeated incremental-witness "
        f"criterion: **{summary['repeated_incremental_witness']}**.",
        f"- Reciprocal eligible witnesses: {summary['reciprocal_witness_count']}.",
        f"- New beta presence A: {beta['A']}/{beta['observed']} observed; "
        f"{beta['unresolved']}/24 unresolved. No calibrated FPR claim.",
        f"- Full predeclared useful-result conjunction: **{summary['unqualified_useful_result']}**.", '',
        'A failed quality/delivery construction cannot establish that semantic '
        'binding is useless or that valid positives are rejected. Predicate '
        'disagreements outside the quality envelope are diagnostic only. '
        'No human preservation, arbitrary-owner authentication, attribution, '
        'T3 full-ownership robustness, external superiority or novelty follows.', '',
        '## All planned cells', '',
        'Quality columns show PSNR / SSIM / LPIPS. Outcomes are 1/0; absent values '
        'remain missing. Gate failure does not remove a row.', '',
        '| Pair | Cell | Status | Recipient quality | Canonical quality | Both quality | D | F combined / semantic / perceptual | Semantic / own-instance status | Primary / reciprocal witness |',
        '|---|---|---|---|---|---|---|---|---|---|']
    for c in rows:
        def metrics(name):
            m = c.get('quality_'+name)
            if m is None:
                return 'missing'
            psnr = 'inf' if m.get('psnr_infinite') else f"{m['psnr_db']:.4f}"
            return f"{psnr} / {m['ssim_rgb']:.6f} / {m['lpips']:.6f}"
        eps = c['endpoints']
        fs = ' / '.join(flag(eps.get(mode, {}).get('F')) for mode in ('combined', 'semantic_only', 'perceptual_only'))
        call = c['calls'].get('combined', {})
        text.append(f"| {c['recipient']}-{c['donor']} | {c['cell']} | {c['status']} | "
            f"{metrics('recipient')} | {metrics('canonical')} | {flag(c.get('quality_both'))} | "
            f"{flag(eps.get('none', {}).get('D'))} | {fs} | "
            f"{call.get('semantic', {}).get('content_status', 'missing')} / "
            f"{call.get('instance_own_content_status', 'missing')} | "
            f"{flag(c.get('primary_witness'))} / {flag(c.get('reciprocal_witness'))} |")
    text += ['', '## Frozen target relationships and positive controls', '',
        'Equality and Hamming distances below describe fixed pre-intervention '
        'payloads, not human semantic labels or a pair selection rule.', '',
        '| Pair | qR / qD | q bit distance | hR / hD | h bit distance | RR changed pixels | RR target h differs from old operational h | RR classification |',
        '|---|---|---:|---|---:|---:|---|---|']
    for r, d in pairs:
        a, b = run['targets'].get(str(r)), run['targets'].get(str(d))
        rr = next(c for c in rows if c['recipient'] == r and c['cell'] == 'RR')
        if a is None or b is None:
            text.append(f'| {r}-{d} | missing | missing | missing | missing | missing | missing | missing |')
            continue
        text.append(f"| {r}-{d} | {a['q']:08x} / {b['q']:08x} | {(a['q']^b['q']).bit_count()} | "
            f"{a['h']:08x} / {b['h']:08x} | {(a['h']^b['h']).bit_count()} | "
            f"{rr.get('changed_pixels', 'missing')} | "
            f"{flag(rr.get('target_h_differs_from_original_operational'))} | "
            f"{rr.get('positive_classification', 'missing')} |")
    text += ['', '## Resources and provenance', '',
        f"Recorded resources: `{json.dumps(run['resources'], sort_keys=True)}`. "
        'The runtime checks live RSS, while the receipt also records peak RSS.', '',
        f"Source receipt: `{args.run.resolve().as_posix()}`.", '',
        f"Receipt SHA-256: `{hashlib.sha256(raw).hexdigest()}`. "
        f"Protocol SHA-256: `{run['protocol_sha256']}`. "
        f"Report renderer: `scripts/journal_binding_reissue_report.py`, "
        f"SHA-256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`.", '',
        'All saved images, raw calls, targets and partial states remain in the '
        'source run. No rerun, pair replacement, target revision or threshold '
        'change was performed. E3/M2 and H2 are unchanged.', '',
        'Terminal reason:', '', '```text', run['terminal_reason'], '```', '']
    args.output.write_text('\n'.join(text), encoding='utf-8')
    print(json.dumps(dict(report=str(args.output), outcome=run['outcome'], summary=summary)))


if __name__ == '__main__':
    main()
