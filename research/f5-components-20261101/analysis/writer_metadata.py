"""Summarize saved clean F5 reports; never executes the writer or loads pixels."""
import csv
import hashlib
import json
from pathlib import Path
import runpy
import statistics
import subprocess
import sys
import time

start = time.monotonic()
api = runpy.run_path(str(Path(__file__).with_name('account_saved_development.py')))
rows, inputs = api['load']('stage2')
out = api['RD'] / 'results/wp1-writer-metadata'
if out.exists():
    raise FileExistsError(out)
kept = []
for line, row in rows.values():
    if row.get('arm') != 'f5-r2' or row.get('channel') != 'clean' or row.get('status') != 'ok':
        continue
    report = row['embedding_report']
    kept.append({'source': row['source_id'], 'line': line,
                 **{key: report[key] for key in ('rgb_psnr_db', 'margin_median', 'margin_min', 'negative_chips', 'target_margin', 'steps', 'refine_rounds', 'psnr_target_db')}})
assert len(kept) == 60 and len({r['source'] for r in kept}) == 60
stats = {key: api['stat']([r[key] for r in kept]) for key in ('rgb_psnr_db', 'margin_median', 'margin_min', 'negative_chips')}
stats['median_margin_below_target_sources'] = sum(r['margin_median'] < r['target_margin'] for r in kept)
stats['negative_chip_sources'] = sum(r['negative_chips'] > 0 for r in kept)
stats['nominal_not_measured_tier_MSE_rgb8'] = {str(p): 255**2 * 10**(-p/10) for p in (47, 52, 58)}
stats['interpretation'] = 'Final post-fragile margins, not convergence traces or isolated stage residuals. Neither measured distortion shares nor recoverable-source forecasts follow.'
out.mkdir(parents=True)
with (out/'sources.csv').open('w', encoding='utf-8', newline='') as handle:
    w = csv.DictWriter(handle,fieldnames=list(kept[0])); w.writeheader(); w.writerows(sorted(kept,key=lambda r:r['source']))
(out/'summary.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
meta = {'label':'MEASURED aggregation of saved writer metadata; no new writing', 'input':inputs,
        'command':[sys.executable,'-I',str(Path(__file__).resolve())],
        'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=api['ROOT'],text=True).strip(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256':hashlib.sha256(Path(__file__).with_name('account_saved_development.py').read_bytes()).hexdigest(),
        'phase_b_journals':'off','seconds':time.monotonic()-start,
        'outputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}}
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(out),'seconds':meta['seconds'],'below_target':stats['median_margin_below_target_sources'],'with_negative_chips':stats['negative_chip_sources']}))
