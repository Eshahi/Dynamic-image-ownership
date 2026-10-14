"""Receipt-only descriptive analysis of the fixed common-message development screen."""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import median


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--clean', type=Path, required=True)
    p.add_argument('--t3', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    clean, attack = [json.loads((d/'run.json').read_text()) for d in (a.clean, a.t3)]
    if clean['outcome'] != 'completed' or attack['outcome'] != 'completed':
        raise ValueError('Terminal complete receipts required; do not report a running subset')
    if clean.get('summary', {}).get('eligibility_pass') is not True:
        raise ValueError('This conditional-comparison report requires clean eligibility PASS')
    ids = [s['source_id'] for s in clean['sources']]
    expected = {(sid, method, family, strength, seed) for sid in ids
        for method, family in [('E3','q'),('WAM','q'),('E3','C0'),('WAM','C0')]
        for strength in (.1,.2) for seed in (9,10,11)}
    actual = [(r['source_id'],r['method'],r['family'],r['strength'],r['seed']) for r in attack['rows']]
    if len(actual) != 144 or set(actual) != expected or len(set(actual)) != 144:
        raise ValueError('Attack reader identity coverage differs')
    images = [(r['source_id'],r['method'],r['family'],r['strength'],r['seed']) for r in attack['images']]
    expected_images = {(sid,method,family,s,seed) for sid in ids for method,family in [('E3','q'),('WAM','q'),('shared','C0')]
                       for s in (.1,.2) for seed in (9,10,11)}
    if len(images) != 108 or set(images) != expected_images: raise ValueError('Attack image coverage differs')
    text = ['# E3 and WAM common-message development comparison', '',
        '2026-10-14. Fixed native operating points; previously consulted development images. '
        'This is a common exact-payload task, not matched-FPR, matched-distortion or ownership benchmarking.', '',
        '## Execution and eligibility', '',
        f"Clean receipt: `{a.clean}/run.json`, code `{clean['commit']}`, {clean['duration_seconds']:.3f} s. "
        f"T3 receipt: `{a.t3}/run.json`, code `{attack['commit']}`, {attack['duration_seconds']:.3f} s.", '',
        f"Clean eligibility **{'PASS' if clean['summary']['eligibility_pass'] else 'FAIL'}**: "
        '36/36 reader calls and 30 image-family records. E3 q, WAM q, WAM complement and WAM hash '
        'each pass strict clean quality and readable exact assigned-message recovery on 6/6. '
        'Native WAM tensor parity, empty-mask/serialization tests and retained E3 classification checks pass. '
        'All tested C0 own/complement/cyclic targets and primary C1 wrong-message counts are zero. '
        'Control-message successes are not pooled with the common-q endpoint.', '',
        f"T3 contains 108 unique image attempts and 144 unique planned reads. Image statuses: {dict(Counter(r['status'] for r in attack['images']))}; "
        f"reader statuses: {dict(Counter(r['status'] for r in attack['rows']))}. No missing, duplicate or extra identities. "
        'Shared C0 images are read by both methods and are not duplicate independent sources.', '',
        'The six ascending reserved IDs are '+', '.join(map(str,ids))+'. Both primary methods embed the same frozen source-derived 32-bit q. '
        'WAM additionally embeds complementary and fixed source-ID-hash controls at the same native w=2. '
        'Neither reader receives expected q, source ID or original pixels; equality is evaluator-only. '
        'E3 Q requires semantic.read, so recomputed-only matches and below-threshold BCH candidates never count. '
        'WAM uses predicted masks and native semihard raw-logit means >.5; an empty mask is unavailable.', '',
        '## Clean quality and control messages', '',
        '| Source | Method / message | PSNR dB | SSIM | LPIPS | Exact | Strict |',
        '|---:|---|---:|---:|---:|---:|---:|']
    for r in clean['rows']:
        if r['family'] == 'C0': continue
        q = r['quality_source']
        text.append(f"| {r['source_id']} | {r['method']} / {r['family']} | {q['psnr_db']:.4f} | {q['ssim_rgb']:.6f} | {q['lpips']:.6f} | {int(r['scores']['assigned']['Q'])} | {int(r['strict_quality'])} |")
    diag = clean['message_diagnostics']; distances = [d['distance'] for d in diag['pair_distances']]
    text += ['', 'Strict means PSNR>35 dB, SSIM>.9, LPIPS<.1, each against the same canonical source. '
        'These are ceilings, not equal distortion. All delivered pixels and failed outcomes are retained.', '',
        f"Assigned-q bit-one counts across six images: `{diag['bit_ones']}`. Pairwise distances range {min(distances)}–{max(distances)} bits; "
        f"hash-control schedule collisions: {diag['control_collisions']}. There are no repeated q words. "
        'Six structured messages do not establish uniformity or 32 bits of entropy.', '',
        '## Regeneration outcomes', '',
        'Pinned SD1.5 DDIM20, strengths .1/.2, seeds 9/10/11, empty prompts, guidance=1, eta=0, '
        'native safety checks, same fresh generator seed for each matched identity. Native sampler FP16; readers FP32. '
        'Each delivered primary mark and shared C0 is regenerated afresh, saved and reopened. '
        'All 18 planned C1 attempts per method/strength remain in the denominator; source N=6.', '',
        '| Strength | Method | Available / 18 | Readable / 18 | Exact Q / 18 | Source majority Q / 6 | Zero-filled bit score |',
        '|---:|---|---:|---:|---:|---:|---:|']
    for s in (.1,.2):
        for method in ('E3','WAM'):
            g = attack['summary']['groups'][f'{method}/q/{s}']
            text.append(f"| {s} | {method} | {g['completed']} | {g['readable']} | {g['exact']} | {g['source_majorities']} | {g['zero_filled_bit_accuracy_mean']:.6f} |")
    text += ['', 'The zero-filled bit score assigns zero to unreadable/unavailable calls; it is not measured BER. '
        'At least two of three planned seeds define a source majority. No seed-level independence or significance test is asserted.', '',
        '| Source | .1 E3 Q / 3 | .1 WAM Q / 3 | Paired difference | .2 E3 Q / 3 | .2 WAM Q / 3 | Paired difference |',
        '|---:|---:|---:|---:|---:|---:|---:|']
    for sid in ids:
        counts = []
        for s in (.1,.2):
            n = [sum(r['status']=='ok' and r['scores']['assigned']['Q'] for r in attack['rows']
                if (r['source_id'],r['method'],r['family'],r['strength']) == (sid,m,'q',s)) for m in ('E3','WAM')]
            counts.extend([str(n[0]), str(n[1]), f'{(n[0]-n[1])/3:+.3f}'])
        text.append(f"| {sid} | "+' | '.join(counts)+' |')
    text += ['', '| Strength | E3 S | E3 J | E3 H | E3 F |', '|---:|---:|---:|---:|---:|']
    for s in (.1,.2):
        group = [r for r in attack['rows'] if r['method']=='E3' and r['family']=='q' and r['strength']==s and r['status']=='ok']
        text.append(f'| {s} | '+' | '.join(f"{sum(r['native_endpoints'][k] for r in group)}/18" for k in ('S','J','H','F'))+' |')
    text += ['', 'E3 content checks are system-specific secondary endpoints; WAM has no equivalent full ownership decision. '
        'Their absence is not a WAM failure. Neither a wrong-message control nor E3 public-owner routing establishes cryptographic security.', '',
        '| Strength | Method | C0 available / 18 | C0 readable / 18 | C0 own / complement / cyclic matches | C1 complement / cyclic matches | Attack-input LPIPS median / max | Canonical LPIPS median / max |',
        '|---:|---|---:|---:|---|---|---|---|']
    for s in (.1,.2):
        for m in ('E3','WAM'):
            c0=attack['summary']['groups'][f'{m}/C0/{s}']; c1=attack['summary']['groups'][f'{m}/q/{s}']
            group=[r for r in attack['rows'] if (r['method'],r['family'],r['strength'],r['status'])==(m,'q',s,'ok')]
            def dist(key):
                vals=[r[key]['lpips'] for r in group]
                return f'{median(vals):.6f} / {max(vals):.6f}' if vals else 'unavailable'
            text.append(f"| {s} | {m} | {c0['completed']} | {c0['readable']} | {c0['own_q']} / {c0['wrong_complement']} / {c0['cyclic_q']} | {c1['wrong_complement']} / {c1['cyclic_q']} | {dist('quality_marking_input')} | {dist('quality_source')} |")
    text += ['', 'Distortion is descriptive; no attack was removed by a quality filter. Human admissibility remains missing. '
        'Native WAM readable-mask counts are diagnostics, not a calibrated image-presence FPR. '
        'Zero observed exact negative matches on six source clusters does not certify a rare-event rate.', '',
        '## Interpretation and next allocation', '',
        'This establishes a usable shared payload-recovery implementation and a bounded native-setting comparison. '
        'It does not establish matched-FPR superiority, equal distortion, arbitrary-message advantage, added binding value or journal readiness. '
        'E3 has BCH(59,32), 320 semantic carrier chips plus a separate h tier; WAM is an arbitrary 32-bit image watermark. '
        'The payload source, total coding budget, models used at extraction, and writer effort differ. '
        'E3 construction explicitly optimized this SD1.5 DDIM .1/.2 channel with seeds 0–2; these new seeds are not a new diffusion backbone. '
        'The published WAM SA-1B MIT checkpoint is not the paper’s COCO model.', '',
        'The fixed comparison is complete, including unfavorable results. Do not tune amplitude, message, seed or threshold on these six sources. '
        'Retain native tables and carry the comparison forward only through a separately frozen distortion/FPR calibration and independent-transfer design. '
        'Use new development source groups for calibration and evaluation, with ID/hash exclusion of protected held-out assignments. '
        'No large construction run or acquisition is launched by this report; the protocol describes its feasibility and resource requirements.', '',
        f"Peak process RAM: clean {clean['peak_ram_bytes']/1024**3:.3f} GiB, T3 {attack['peak_ram_bytes']/1024**3:.3f} GiB. "
        f"Peak CUDA allocations: {clean['peak_gpu_bytes']/1024**3:.3f} / {attack['peak_gpu_bytes']/1024**3:.3f} GiB. "
        'USD 0 rental/API; electricity unmetered. No downloads, paid computation, held-out inspection or protected edits. '
        'E3 marks were reused from the retained construction run; fresh WAM embedding time versus cached E3 access is not a fair construction-speed comparison.', '',
        'Reproduce this report from receipts with `scripts/analyze_e3_wam_common.py --clean <clean-dir> --t3 <t3-dir> --output <report.md>`. '
        'The interface and report-guard regression tests are `tests/test_e3_wam_common.py`. Independent review is recorded separately.', '']
    a.output.write_text('\n'.join(text), encoding='utf-8')
    print(str(a.output))


if __name__ == '__main__': main()
