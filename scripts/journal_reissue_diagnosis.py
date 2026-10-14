"""Development-only residual diagnosis of all six RC1 pairs; no model calls.

Compare retained canonical, marked, first-PGD and final images. This is a
post-hoc mechanism diagnosis, never a replacement for RC1's frozen endpoints.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from PIL import Image


def main():
    started = time.monotonic()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--stage-a', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    run = json.loads(a.receipt.read_text())
    prior = {r['source_id']: r for r in json.loads(a.stage_a.read_text())['sources']}
    rows = []
    def load(path):
        with Image.open(path) as im:
            return np.asarray(im, dtype=np.float64)
    def stats(delta, old):
        norm = float(np.linalg.norm(delta))
        oldnorm = float(np.linalg.norm(old))
        return dict(mse=float(np.square(delta).mean()),
                    cosine_with_original_mark=float(np.sum(delta*old)/(norm*oldnorm)) if norm*oldnorm else None,
                    chroma_residual_mse=float(np.square(delta-delta.mean(axis=2, keepdims=True)).mean()))
    for cell in run['cells']:
        sid = cell['recipient']; target = run['targets'][str(sid)]
        canonical = load(target['canonical_path']); marked = load(target['full_image'])
        shared = load(cell['shared_image']); final = load(cell['image'])
        old = marked-canonical
        rows.append(dict(recipient=sid, cell=cell['cell'],
            original_quality=prior[sid]['clean']['full']['quality_source'],
            final_quality=cell['quality_canonical'],
            original_mark=stats(old, old), first_pgd_increment=stats(shared-marked, old),
            branch_increment=stats(final-shared, old), total_increment=stats(final-marked, old),
            final_residual=stats(final-canonical, old),
            first_restore=cell['first_restore'], second_restore=cell['second_restore']))
    result = dict(commit=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        command=__import__('sys').argv, config=dict(all_rc1_pairs=True, no_models=True),
        seeds=[], data_split='consulted development', outcome='completed',
        interpretation='Post-hoc saved-pixel diagnosis; branch includes PGD50 and both restorations, so not a causal isolation.',
        rows=rows, duration_seconds=time.monotonic()-started)
    (a.output_dir/'run.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for r in rows:
        if r['cell']=='RR':
            print(r['recipient'], 'LPIPS', round(r['original_quality']['lpips'],4), '->', round(r['final_quality']['lpips'],4),
                  'MSE old/first/branch/total', *[round(r[k]['mse'],5) for k in ('original_mark','first_pgd_increment','branch_increment','final_residual')],
                  'increment cosine', round(r['total_increment']['cosine_with_original_mark'],4),
                  'restore amplitudes', round(r['first_restore']['amplitude'],4), round(r['second_restore']['amplitude'],4))


if __name__=='__main__':
    main()
