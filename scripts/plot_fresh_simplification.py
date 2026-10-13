"""Plot descriptive construction cost from the completed fresh Stage A summary."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--summary', type=Path, required=True)
p.add_argument('--output', type=Path, required=True, help='Output stem for PNG and SVG')
a = p.parse_args()
r = json.loads(a.summary.read_text(encoding='utf-8-sig'))
assert r['outcome'] == 'completed' and len(r['source_rows']) == 24
rows = r['source_rows']
full = [x['timing']['full_supplier_writer_seconds'] for x in rows]
lean = [x['timing']['lean_stage_sum_estimate_seconds'] for x in rows]
fig, ax = plt.subplots(figsize=(8.2, 8.4), layout='constrained')
for i, (f, l) in enumerate(zip(full, lean)):
    ax.plot([l, f], [i, i], color='#b6bcc5', lw=1.5, zorder=1)
ax.scatter(full, range(24), label='Full E3: measured', color='#294f78', s=34, zorder=2)
ax.scatter(lean, range(24), label='Lean: stage-sum estimate', color='#c4652c', s=34, zorder=3)
ax.set_yticks(range(24), [str(x['source_id']) for x in rows])
ax.invert_yaxis()
ax.set_xlim(0, max(full)*1.06)
ax.set_xlabel('Supplier-through-final-image construction cost (seconds)')
ax.set_ylabel('Reserved development source ID')
ax.set_title('Fresh simplification: clean quality and exact payloads 24/24 in both arms\n'
             'Median saving 18.57%; fixed advancement target 25% not met', loc='left', fontsize=12, pad=16)
ax.legend(loc='lower right', frameon=False)
ax.grid(axis='x', color='#e4e7ec', lw=.8)
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)
fig.supxlabel('N = 24. Shared supplier/initializer computation; lean was not timed as a separate end-to-end run.\n'
              'No Stage B attacks. Setup, warmup and evaluation costs are excluded from these construction boundaries.', fontsize=8)
a.output.parent.mkdir(parents=True, exist_ok=True)
for suffix in ('.png', '.svg'):
    fig.savefig(a.output.with_suffix(suffix), dpi=160, facecolor='white')
plt.close(fig)
