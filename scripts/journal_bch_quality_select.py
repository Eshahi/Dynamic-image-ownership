"""E3 CPU composition of recorded marks using only their clean quality.

All detector observations are inherited. No image selection by attack outcome,
model load, pixel replay, new detector call or confirmatory inference occurs.
"""
from __future__ import annotations

import time
STARTED = time.monotonic()
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback
from journal_bch_analysis import ALPHA, BETA, CONDITIONS, endpoint, read_json, read_rows, strict_quality

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
IDS = (1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768)
METHOD = 'E3-BCH59-Q080'
CAP = 60.
D2 = MAIN / '.thesis-build/dev-runs/20261010-1212-native-writer'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def quality_branch(metrics):
    """The only branch predicate; invalid measurements cannot choose a dose."""
    if not isinstance(metrics, dict) or not all(isinstance(metrics.get(k), (float, int)) and
            math.isfinite(metrics[k]) for k in ('ssim_rgb', 'lpips')):
        raise ValueError('Missing or invalid quality measurements')
    psnr = metrics.get('psnr_db')
    if not (metrics.get('psnr_infinite') is True or isinstance(psnr, (float, int)) and math.isfinite(psnr)):
        raise ValueError('Missing or invalid PSNR measurement')
    return 'retain' if strict_quality(metrics) else 'contract_once'


def summarize(rows):
    quality = exact = c0 = wrong = calls = 0
    joint = {b: 0 for b in CONDITIONS}
    complete = len(rows)==12 and [r['source_id'] for r in rows]==list(IDS)
    lookup = {}
    for r in rows:
        complete &= r.get('status')=='ok' and set(r['conditions'])==set(CONDITIONS)
        lookup[r['source_id']] = r
        for b in CONDITIONS:
            cell = r['conditions'][b]
            intended = endpoint(cell['calls'][ALPHA], r['payload'])
            controls = [endpoint(cell['c0_call']), endpoint(cell['calls'][BETA])]
            joint[b] += bool(intended['J'] and intended['S'])
            c0 += controls[0]['A']
            wrong += controls[1]['A']
            calls += 3
            if b=='clean':
                quality += quality_branch(cell['quality_source'])=='retain'
                exact += bool(intended['Q'] and intended['H'] and intended['F'])
    old = read_rows(D2/'rows.jsonl')
    if len(old)!=12 or {r['source_id'] for r in old}!=set(IDS):
        raise ValueError('Incomplete D2 VAE comparator')
    positives = [(r['source_id'], b) for r in old for b in ('sd15_vae', 'sdxl_vae')
                 if r['conditions'][b]['joint_fixed_q']]
    lost = [dict(source_id=s, condition=b) for s,b in positives if s not in lookup or
            not endpoint(lookup[s]['conditions'][b]['calls'][ALPHA], lookup[s]['payload'])['J']]
    passed = bool(complete and quality==exact==joint['sd15_vae']==joint['sdxl_vae']==12
                  and calls==108 and not c0 and not wrong and not lost)
    return dict(planned_sources=12, completed=len(rows), all_source_cells_complete=bool(complete),
        strict_clean_quality=quality, clean_exact_q_h_both_match=exact, joint_fixed_q=joint,
        c0_any=c0, wrong_owner_any=wrong, completed_negative_calls=calls//3*2,
        planned_negative_calls=72, inherited_full_calls=calls, new_full_calls=0,
        inherited_negative_calls=calls//3*2, d2_vae_positive_count=len(positives),
        lost_d2_positive_vae_identities=lost, screen_pass=passed, stage_a_pass=False,
        m1a_pass=False, candidate_eligible=False,
        scope='Retrospective development composition; all calls reused, zero new measurements; full T3 pending')


def validate_stage_a(folder):
    folder = Path(folder).resolve()
    run, rows = read_json(folder/'run.json'), read_rows(folder/'rows.jsonl')
    if (run.get('schema')!='journal-e3-bch-quality-select-stage-a-v1' or run.get('method')!=METHOD or
        run.get('outcome')!='completed' or run.get('qualification')!='stage_a_pass' or
        run.get('data_split')!='development' or run.get('usd')!=0 or run.get('sources')!=list(IDS) or
        run.get('config', {}).get('quality_rule')!='retain_if_strict_else_contract_once' or
        run['config'].get('factor')!=.8 or run['config'].get('detector')!='E1-BCH59-A' or
        run['config'].get('cap_seconds')!=CAP or not 0<run.get('duration_seconds', math.inf)<=CAP or
        run.get('budget_overrun') is not False or not run.get('summary', {}).get('stage_a_pass') or
        any(r.get('method')!=METHOD for r in rows) or not summarize(rows)['screen_pass']):
        raise ValueError('Complete passing E3 cached composition required')
    if read_json(folder/'summary.json')!=run['summary']:
        raise ValueError('E3 summary mismatch')
    return rows, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--e1-stage-b-dir', type=Path, required=True)
    parser.add_argument('--e2-stage-a-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    a = parser.parse_args()
    out, bdir, edir = a.output_dir.resolve(), a.e1_stage_b_dir.resolve(), a.e2_stage_a_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    record = dict(schema='journal-e3-bch-quality-select-stage-a-v1', method=METHOD, stage='A',
        commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, data_split='development', usd=0, sources=list(IDS), seeds=[],
        e1_stage_b_dir=str(bdir), e2_stage_a_dir=str(edir), outcome='running', qualification='pending',
        config=dict(quality_rule='retain_if_strict_else_contract_once', factor=.8, detector='E1-BCH59-A',
            cap_seconds=CAP, semantic_views=7, binding='soft', roster_size=1,
            quality_limits=dict(psnr_db_gt=35, ssim_rgb_gt=.9, lpips_lt=.1)), new_full_calls=0)
    write(out/'run.json', record)
    try:
        brun, erun = read_json(bdir/'run.json'), read_json(edir/'run.json')
        brows, erows = read_rows(bdir/'rows.jsonl'), read_rows(edir/'rows.jsonl')
        for run, panel, schema in ((brun,brows,'journal-e1-bch-stage-b-v1'),
                                   (erun,erows,'journal-e2-bch-attenuation-stage-a-v1')):
            if (run.get('schema')!=schema or run.get('outcome')!='completed' or
                run.get('data_split')!='development' or run.get('usd')!=0 or len(panel)!=12 or
                {r['source_id'] for r in panel}!=set(IDS) or any(r['status']!='ok' for r in panel)):
                raise ValueError('Final complete E1/E2 parent panels required')
        if (Path(erun['ancestry']['stage_b_run_json']).resolve()!=bdir/'run.json' or
            erun['config']['factor']!=.8 or erun['config']['optimization'] or
            erun['config']['fragile_restoration'] or erun['config']['threshold_change'] or
            erun['config']['detector']!='E1-BCH59-A'):
            raise ValueError('E2 must implement the exact frozen contraction of these E1 marks')
        record['parent_commits'] = dict(E1=brun['commit'], E2=erun['commit'])
        record['config']['profile'] = erun['config']['profile']
        record['config']['sdxl_revision'] = erun['config']['sdxl_revision']
        for sid in IDS:
            if time.monotonic()-STARTED>CAP:
                raise TimeoutError('E3 composition 60-second inclusive cap')
            b, e = next(r for r in brows if r['source_id']==sid), next(r for r in erows if r['source_id']==sid)
            if b['payload']!=e['payload'] or Path(e['start_image'])!=Path(b['conditions']['clean']['image']):
                raise ValueError('E2 fixed payload or final E1 ancestry mismatch')
            branch = quality_branch(b['conditions']['clean']['quality_source'])
            chosen, parent, parent_rows = (b,bdir,brows) if branch=='retain' else (e,edir,erows)
            if branch=='retain' and b.get('inherited_provenance'):
                parent = Path(b['inherited_provenance']['run_json']).parent
                parent_rows = read_rows(parent/'rows.jsonl')
                chosen = next(r for r in parent_rows if r['source_id']==sid)
                if chosen['conditions']!=b['conditions'] or chosen['payload']!=b['payload']:
                    raise ValueError('Inherited E1 A selected endpoint mismatch')
            if set(chosen['conditions'])!=set(CONDITIONS):
                raise ValueError('Incomplete selected conditions')
            for condition in CONDITIONS:
                cell = chosen['conditions'][condition]
                if not Path(cell['image']).is_file() or not Path(cell['c0_image']).is_file():
                    raise ValueError('Selected saved image missing')
                for owner in (ALPHA, BETA):
                    reference = b['conditions'][condition]['calls'][owner]
                    candidate = e['conditions'][condition]['calls'][owner]
                    for key in ('method','revision','detector_config_id','binding','binding_mode','owners_tested','side_information'):
                        if candidate.get(key)!=reference.get(key):
                            raise ValueError('E1/E2 detector configuration mismatch: '+key)
            row = copy.deepcopy(chosen)
            row.update(method=METHOD, config='E3', selection_provenance=dict(branch=branch,
                deciding_quality=b['conditions']['clean']['quality_source'], selected_run=str(parent/'run.json'),
                selected_rows=str(parent/'rows.jsonl'), selected_row_index=parent_rows.index(chosen),
                selected_commit=read_json(parent/'run.json')['commit'],
                selected_image=chosen['conditions']['clean']['image'], inherited_full_calls=9, new_full_calls=0))
            # Per-source times belong to the parents, never newly timed E3 embedding.
            row['timing_scope'] = 'inherited parent timings; no newly measured E3 writer time'
            rows.append(row)
        summary = summarize(rows)
        record.update(outcome='completed', summary=summary,
            branch_counts={b:sum(r['selection_provenance']['branch']==b for r in rows) for b in ('retain','contract_once')})
    except Exception:
        record.update(outcome='failed', error=traceback.format_exc(), summary=dict(stage_a_pass=False))
        raise
    finally:
        (out/'rows.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in rows), encoding='utf-8')
        record.update(duration_seconds=time.monotonic()-STARTED, budget_overrun=time.monotonic()-STARTED>CAP)
        passed = bool(record['outcome']=='completed' and record['summary'].get('screen_pass') and not record['budget_overrun'])
        record['summary']['stage_a_pass'] = passed
        record['qualification'] = 'stage_a_pass' if passed else 'ineligible'
        write(out/'summary.json', record['summary'])
        write(out/'run.json', record)
        record['duration_seconds'] = time.monotonic()-STARTED
        if record['duration_seconds']>CAP:
            record.update(budget_overrun=True, qualification='ineligible')
            record['summary']['stage_a_pass'] = False
        write(out/'summary.json', record['summary'])
        write(out/'run.json', record)
        print(json.dumps(dict(outcome=record['outcome'], summary=record['summary'])), flush=True)


if __name__=='__main__':
    main()
