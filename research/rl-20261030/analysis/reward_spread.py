"""Descriptive rewards and attacker choice ceilings from saved development numbers."""
import collections
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = [json.loads(line) for line in (HERE/'dev-records.jsonl').open(encoding='utf-8')]

def quantile(values, p):
    x = sorted(values)
    if not x:
        return None
    z = (len(x)-1)*p
    i = int(z)
    return x[i] + (x[min(i+1, len(x)-1)]-x[i])*(z-i)

def summary(values):
    v = [float(x) for x in values if x is not None]
    return {'n': len(v), 'mean': st.mean(v) if v else None,
        'sd': st.stdev(v) if len(v)>1 else None,
        'q10': quantile(v,.1), 'median': quantile(v,.5), 'q90': quantile(v,.9),
        'below_zero': sum(x<0 for x in v), 'nonnegative': sum(x>=0 for x in v)}

groups = collections.defaultdict(list)
for r in rows:
    groups[(r['cohort'],r['cell'],r['arm'])].append(r)
rewards = []
for (cohort,cell,arm), group in sorted(groups.items()):
    sources = collections.defaultdict(list)
    for r in group:
        sources[r['source']].append(r)
    observed = [r for r in group if r['ok']]
    mixed = sum(any(r['success'] is True for r in rr) and any(r['success'] is False for r in rr)
                for rr in sources.values())
    majority = sum(sum(r['success'] is True for r in rr)>=2 for rr in sources.values()) if cell!='clean' else sum(r['success'] is True for r in group)
    optimistic = sum(sum(r['success'] is not False for r in rr)>=2 for rr in sources.values()) if cell!='clean' else sum(r['success'] is not False for r in group)
    rewards.append({'cohort':cohort,'cell':cell,'arm':arm,'attempts':len(group),'observed':len(observed),
        'missing':len(group)-len(observed),'sources':len(sources),
        'seed_successes':sum(r['success'] is True for r in group),
        'source_successes_conservative':majority,'source_successes_optimistic':optimistic,
        'sources_with_mixed_observed_binary_rewards':mixed,
        'source_J_conservative':sum(sum(r['J'] is True for r in rr)>=2 for rr in sources.values()) if arm in ('f5-r2','v5-r3') and cell!='clean' else None,
        'semantic_decoded_margin':summary(r['semantic_decoded_margin'] for r in group),
        'semantic_generic_margin':summary(r['semantic_margin'] for r in group),
        'semantic_recomputed_margin':summary(r['semantic_recomputed_margin'] for r in group),
        'instance_decoded_margin':summary(r['instance_decoded_margin'] for r in group),
        'presence_margin':summary(r['presence_margin'] for r in group),
        'generic_positive_but_C_false':sum(r['semantic_margin'] is not None and r['semantic_margin']>=0 and r['C'] is False for r in group),
        'decoded_positive_but_C_false':sum(r['semantic_decoded_margin'] is not None and r['semantic_decoded_margin']>=0 and r['C'] is False for r in group),
        'qualities':{k:summary(r['quality'][k] for r in group) for k in ('psnr_db','ssim_rgb','lpips')},
        'strict_clean_passes':sum(r['strict_quality'] is True for r in group) if cell=='clean' else None,
    })

attacker = []
for cohort in ('stage2_union','phase_a'):
    for arm in ('f5-r2','v5-r3','wam','vine-r'):
        g = [x for x in rewards if x['cohort']==cohort and x['arm']==arm and x['cell']!='clean']
        cells = [x['cell'] for x in g]
        cell_counts = {x['cell']:x['source_successes_conservative'] for x in g}
        by_source = collections.defaultdict(dict)
        for cell in cells:
            cc = collections.defaultdict(list)
            for r in groups[(cohort,cell,arm)]:
                cc[r['source']].append(r)
            for s, rr in cc.items():
                by_source[s][cell] = {'lo':int(sum(r['success'] is True for r in rr)>=2),
                    'hi':int(sum(r['success'] is not False for r in rr)>=2),
                    'complete':all(r['ok'] for r in rr)}
        # This lets a hindsight attacker select a different cell for each source.
        # It does not constrain attack fidelity and uses every outcome to select.
        oracle_lo = sum(min(v['lo'] for v in d.values()) for d in by_source.values())
        oracle_hi = sum(min(v['hi'] for v in d.values()) for d in by_source.values())
        complete = {s:d for s,d in by_source.items() if all(v['complete'] for v in d.values())}
        attacker.append({'cohort':cohort,'arm':arm,'n_sources':len(by_source),
            'fixed_source_survival_by_cell':cell_counts,'best_fixed_attack_survivors':min(cell_counts.values()),
            'oracle_attack_survivors_lo':oracle_lo,'oracle_attack_survivors_hi':oracle_hi,
            'complete_all_cell_sources':len(complete),
            'complete_oracle_survivors':sum(min(v['lo'] for v in d.values()) for d in complete.values()),
            'complete_fixed_survivors':min(sum(d[c]['lo'] for d in complete.values()) for c in cells) if complete else None,
            'interpretation':'unconstrained-fidelity hindsight lower survival bound; no learnable policy demonstrated'})
out = {'rewards':rewards,'attacker_spread':attacker,
    'definitions':{'success':'C for F5/v5; message presence P for WAM/VINE, not common binding',
        'nonfloor':'positive binary reward among observed rows; also mixed observed seeds per source. These are descriptive, not policy-gradient estimates.',
        'margins':'not pooled between arms; external margins have bit-count units',
        'missing':'conservative non-success versus optimistic success; soft margins unavailable',
        'attacker':'same fixed clean marks; oracle sees future outcomes and all cell evaluations; no fidelity constraint'}}
(HERE/'reward-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
lines = ['# Saved development reward tables', '',
    'DERIVED by reward_spread.py from the normalized numeric records. C applies only to F5/v5; P is external message presence, without content binding. J is unavailable for WAM/VINE. All nonclean denominators are 60 sources and 180 planned seed outcomes. Clean has one outcome/source. Margins are decoded correlations for F5/v5 and matching-bit counts for WAM/VINE; do not compare their units across arms.', '',
    'Mixed = sources with at least one observed positive and one observed negative seed reward. It is not a policy-gradient variance estimate. Median [p10,p90] uses observed outcomes only; missing values are not replaced by a numerical floor. Source success shows conservative–optimistic missingness bounds.', '',
    '| Cohort | Cell | Arm | Observed | Positive binary reward | Source success | Mixed/60 | Margin median [p10,p90] | Below threshold/observed | Generic positive but C false |',
    '|---|---|---|---:|---:|---:|---:|---|---:|---:|']
for x in rewards:
    m = x['semantic_decoded_margin'] if x['arm'] in ('f5-r2','v5-r3') else x['presence_margin']
    lines.append(f"| {x['cohort']} | {x['cell']} | {x['arm']} | {x['observed']}/{x['attempts']} | {x['seed_successes']}/{x['observed']} | {x['source_successes_conservative']}–{x['source_successes_optimistic']}/60 | {x['sources_with_mixed_observed_binary_rewards']} | {m['median']:.3f} [{m['q10']:.3f}, {m['q90']:.3f}] | {m['below_zero']}/{m['n']} | {x['generic_positive_but_C_false']} |")
(HERE/'reward-tables.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'groups':len(rewards),'attacker':attacker},allow_nan=False))
