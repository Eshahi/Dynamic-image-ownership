"""Read retained JSONL timings only. No image access or experimental imports."""
import collections
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOURNAL = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
latest = {}
lines = 0
with JOURNAL.open(encoding='utf-8') as stream:
    for line in stream:
        lines += 1
        row = json.loads(line)
        latest[row['id']] = row

def summary(values):
    values = sorted(values)
    return dict(n=len(values), mean=statistics.mean(values), median=statistics.median(values),
                p90=values[int(.9*(len(values)-1))], total_hours=sum(values)/3600)

generation = collections.defaultdict(list)
detection = collections.defaultdict(list)
metric = []
statuses = collections.Counter()
for row in latest.values():
    statuses[row['status']] += 1
    key = row['channel'] + ':' + (row['arm'] if row['channel']=='clean' else str(row['strength']))
    if 'generation_seconds' in row:
        generation[key].append(row['generation_seconds'])
    for method, seconds in row.get('detection_seconds',{}).items():
        detection[(method, row['control'])].append(seconds)
    if 'metrics_seconds' in row:
        metric.append(row['metrics_seconds'])
result = dict(source=str(JOURNAL), raw_lines=lines, unique_ids=len(latest), statuses=dict(statuses),
              generation={k:summary(v) for k,v in sorted(generation.items())},
              detection_batches={':'.join(k):summary(v) for k,v in sorted(detection.items())},
              metrics=summary(metric))

# Counts specify prospective schedules; timings do not imply equal-work derivative calls.
core = [('R0',.1),('R0',.2),('R0',.4),('R1',.1),('R1',.2),('R1',.4),('R3',.2)]
def native_hours(n,cells):
    return n*5*3*sum(result['generation'][f'{c}:{s}']['mean'] for c,s in cells)/3600
def assessment_hours(n,settings):
    # Per setting/source: four positive batches + one C0 batch per each method.
    per = sum(result['detection_batches'][m+':C1']['mean']+result['detection_batches'][m+':C0']['mean']
              for m in ['f5-r2','v5-r3','wam','vine-r'])
    return n*settings*(per+5*result['metrics']['mean'])/3600
result['forecast'] = dict(
    phase_b_core_native_generation_hours=native_hours(200,core),
    phase_a_sixcell_native_generation_hours=native_hours(60,core[:6]),
    phase_b_clean_embedding_hours=200*sum(result['generation']['clean:'+a]['mean'] for a in ['unmarked','f5-r2','v5-r3','wam','vine-r'])/3600,
    phase_b_core_assessment_hours=assessment_hours(200,22),
    phase_b_attack_and_firstpass_assessment_hours=assessment_hours(200,9),
    phase_a_native_assessment_hours=assessment_hours(60,18),
    per_source_setting_assessment_seconds=assessment_hours(1,1)*3600,
)
result['prospective_unit_counts'] = dict(
    controlling_protocol='07-final-experiment.md and analysis/mechanism-server-spec.md',
    phase_a_main_law_jvp=1080,
    phase_a_additional_mode_encoder_jvp=720,
    phase_a_additional_differential_full_chain_jvp=540,
    phase_a_all_full_chain_jvp=1620,
    phase_a_additional_stage_primal_outputs=1620,
    phase_a_preprocess_outputs_per_unique_path=60,
    phase_a_optional_flux_grid_marked_outputs=2160,
    phase_a_optional_flux_selected_c0_outputs=180,
    phase_a_optional_flux_codec_outputs=300,
    phase_b_core_outputs=31000,
    phase_b_core_detector_batches=49600,
    phase_b_core_native_law_jvp=4200,
    phase_b_optional_flux_native_outputs=3000,
    phase_b_optional_flux_native_detector_batches=4800,
    phase_b_optional_flux_law_jvp=600,
    phase_b_optional_flux_codec_outputs=1000,
    phase_b_optional_flux_codec_detector_batches=1600,
    phase_b_with_flux_outputs=35000,
    phase_b_with_flux_detector_batches=56000,
    phase_b_with_flux_native_law_jvp=4800,
    codec_only_law_jvp=0,
    note='720 encoder and 540 differential JVPs are distinct additional work; do not subtract 72 law tangents. All unknown paths require separate server-pilot time/memory accounting.',
)
(ROOT/'cost-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
