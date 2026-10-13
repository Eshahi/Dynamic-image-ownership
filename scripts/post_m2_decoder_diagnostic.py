"""Explicitly post hoc correction diagnostic on fixed BCH-encoded signals.

This is not an uncoded-writer comparison or a detector at a matched FPR.
No threshold, model, received word, scientific output or decision gate changes.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

ALPHA = 'qim-pilot-owner-alpha'


def analyze(rows):
    observations = []
    for r in rows:
        if r['arm'] not in ('I','E'):
            continue
        semantic = r.get('calls',{}).get(ALPHA,{}).get('semantic')
        observation = dict(source_id=r['source_id'], arm=r['arm'], condition=r['condition'],
            strength=r['strength'], seed=r['seed'], reuse_of=r.get('reuse_of'),
            available=bool(semantic and semantic.get('raw_coded_word') is not None))
        if observation['available']:
            # journal_bch_carrier.encode(q) = (q << 27) XOR remainder,
            # where the remainder occupies only bits 0..26.
            q = int(r['payload']['q'],16)
            raw = int(semantic['raw_coded_word'],16)
            if not 0 <= raw < 2**59:
                raise ValueError('Not a 59-bit received word')
            raw_exact = raw >> 27 == q
            decoded_exact = (semantic.get('decoded_code') is not None and
                             int(semantic['decoded_code'],16) == q)
            read_exact = bool(decoded_exact and semantic['read'])
            observation.update(raw_systematic_q=f'{raw >> 27:08x}',
                raw_systematic_exact=raw_exact, decoded_exact=decoded_exact,
                read_exact=read_exact, checked_J=bool(read_exact and semantic['content_match']),
                algorithm_rescued=not raw_exact and decoded_exact,
                algorithm_harmed=raw_exact and not decoded_exact,
                threshold_qualified_rescue=not raw_exact and read_exact,
                raw_exact_but_no_qualified_read=raw_exact and not read_exact)
        observations.append(observation)
    summary={}
    for arm in ('I','E'):
        for strength in (None,.1,.2):
            group=[r for r in observations if r['arm']==arm and r['strength']==strength]
            observed=[r for r in group if r['available']]
            metrics=('raw_systematic_exact','decoded_exact','read_exact','checked_J',
                'algorithm_rescued','algorithm_harmed','threshold_qualified_rescue',
                'raw_exact_but_no_qualified_read')
            summary[f'{arm}/{strength}']=dict(planned=len(group), available=len(observed),
                unavailable=len(group)-len(observed),
                counts={k:sum(r[k] for r in observed) for k in metrics},
                source_clusters_with_event={k:sorted({r['source_id'] for r in observed if r[k]}) for k in metrics},
                paired_decode_categories=dict(Counter(
                    'both_exact' if r['raw_systematic_exact'] and r['decoded_exact'] else
                    'rescued' if r['decoded_exact'] else 'harmed' if r['raw_systematic_exact'] else
                    'neither_exact' for r in observed)))
    return dict(post_hoc=True, writer='fixed BCH-encoded I/E artifacts',
        inference_performed=False, systematic_convention='high 32 bits of raw 59-bit word: raw >> 27',
        limitation='Raw systematic equality is a diagnostic, not an implemented calibrated uncoded detector. '
        'Correction contribution is conditional on this writer/code/channel; no equal-rate coding gain or E3-v5 attribution.',
        summary=summary, observations=observations)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    run=json.loads((args.run_dir/'run.json').read_text())
    if run['outcome']=='running':
        raise ValueError('Analyze only a finished run')
    rows=[json.loads(x) for x in (args.run_dir/'rows.jsonl').read_text().splitlines() if x.strip()]
    result=analyze(rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result['summary']))
