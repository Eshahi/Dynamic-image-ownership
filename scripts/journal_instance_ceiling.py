"""Fixed E3-DV1 prerequisite: cached C-arm instance-content oracle, no models."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

IDS = (30, 72, 73, 89, 127, 165)
OWNER = 'qim-pilot-owner-alpha'


def main():
    tick = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    d = json.loads(a.receipt.read_text())
    assert d['outcome'] == 'completed' and d['config']['sources'] == list(IDS)
    assert d['config']['profile']['decision']['instance_radius'] == 6
    expected = {(i, phase, None, None) for i in IDS for phase in ('clean','sd15_vae','sdxl_vae')}
    expected |= {(i,'T3',s,k) for i in IDS for s in (.2,.4) for k in (9,10,11)}
    actual = set(); rows = []
    for r in d['rows']:
        if r['arm'] != 'C':
            continue
        key = (r['source_id'],r['phase'],r.get('strength'),r.get('seed'))
        assert key in expected and key not in actual
        actual.add(key)
        target = d['sources'][str(r['source_id'])]['shared_source']['payload']
        row = dict(id=r['id'], source_id=r['source_id'], phase=r['phase'],
            strength=r.get('strength'), seed=r.get('seed'), status='unresolved', target=target)
        if r['status'] == 'ok' and OWNER in r.get('calls',{}):
            c = r['calls'][OWNER]; ep = r['endpoints'][OWNER]
            if c.get('perceptual_hash') is not None:
                distance = (int(target['h'],16)^int(c['perceptual_hash'],16)).bit_count()
                exact_q = c['semantic']['read'] and c['semantic']['decoded_code'] == target['q']
                j = bool(exact_q and c['semantic']['found'] and c['semantic']['content_match'])
                assert j == ep['J']
                row.update(status='resolved', h_now=c['perceptual_hash'], h_distance=distance,
                    instance_status='match' if distance <= 6 else 'mismatch' if distance >= 10 else 'uncertain',
                    O_I=distance <= 6, O_J=bool(j and distance <= 6),
                    O_S=bool(ep['S'] and distance <= 6), actual_J=j,
                    actual_H=ep['H'], actual_F=ep['F'])
        rows.append(row)
    assert actual == expected and len(rows) == 54
    summary = {}
    for name, phase, strength in [('clean','clean',None),('sd15_vae','sd15_vae',None),
            ('sdxl_vae','sdxl_vae',None),('T3_0.2','T3',.2),('T3_0.4','T3',.4)]:
        group = [r for r in rows if r['phase']==phase and r['strength']==strength]
        ok = [r for r in group if r['status']=='resolved']
        summary[name] = dict(planned=len(group), resolved=len(ok),
            **{k:sum(r[k] for r in ok) for k in ('O_I','O_J','O_S','actual_J','actual_H','actual_F')},
            distance_histogram=dict(sorted(Counter(r['h_distance'] for r in ok).items())),
            joint_table=dict(sorted(Counter(f"J{int(r['actual_J'])}_I{int(r['O_I'])}" for r in ok).items())),
            majority_O_J=sum(sum(r['O_J'] for r in ok if r['source_id']==i) >= (2 if phase=='T3' else 1) for i in IDS))
    gate = (all(r['status']=='resolved' for r in rows) and summary['clean']['O_J']==6
            and summary['sd15_vae']['O_J']>=5 and summary['T3_0.2']['O_J']>=15
            and summary['T3_0.2']['majority_O_J']>=5)
    duration = time.monotonic()-tick
    result = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=sys.argv, config=dict(ids=IDS, primary_arm='C', radius=6, max_seconds=600),
        seeds=[9,10,11], started_at_utc=started_at,
        data_split='consulted development', usd=0, input_receipt=str(a.receipt),
        outcome='completed', duration_seconds=duration, oracle_advance_gate=bool(gate and duration<=600),
        interpretation='Perfect target-h transport diagnostic on fixed saved suspects, not an executable detector or candidate success.',
        summary=summary, rows=rows)
    (a.output_dir/'run.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(summary=summary, oracle_advance_gate=result['oracle_advance_gate']),indent=2))


if __name__=='__main__':
    main()
