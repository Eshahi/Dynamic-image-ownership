"""Fixed development common-message eligibility and conditional T3 comparison."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
PROTOCOL = ROOT / 'research/journal-upgrade-20261009/e3-wam-common-task-protocol.md'
INPUT = MAIN / '.thesis-build/dev-runs/20261013-1636-fresh-e3-simplification/run.json'
IDS = (30, 72, 73, 89, 127, 165)
TARGETS = ('bac09534', '0ec0942e', 'bdd49438', '99c4b43c', 'efd08760', '9a5ca71c')
ALPHA = 'qim-pilot-owner-alpha'
GPU_CAP, RAM_CAP = 9 * 1024**3, 10 * 1024**3


def hex_bits(value):
    if len(value) != 8 or not 0 <= int(value, 16) < 2**32:
        raise ValueError('Expected eight hexadecimal digits')
    return [(int(value, 16) >> shift) & 1 for shift in range(31, -1, -1)]


def bits_hex(bits):
    if len(bits) != 32 or any(b not in (0, 1, False, True) for b in bits):
        raise ValueError('Expected 32 binary values')
    return f'{sum(int(b) << (31-i) for i, b in enumerate(bits)):08x}'


def evaluate(readout, target):
    """Only this evaluator accepts a target; no reader accepts it."""
    word = readout['decoded_hex'] if readout['readable'] else None
    distance = (int(word, 16) ^ int(target, 16)).bit_count() if word is not None else None
    return dict(Q=distance == 0, bit_errors=distance,
                bit_accuracy=None if distance is None else 1-distance/32,
                zero_filled_bit_accuracy=0 if distance is None else 1-distance/32)


def wam_predictions(predictions, native_decoder):
    """Target-free native decode, independently checked on the SAME prediction tensor."""
    import torch
    if predictions.shape[0:2] != (1, 33) or not bool(torch.isfinite(predictions).all()):
        raise ValueError('Invalid WAM native predictions')
    mask = predictions[:, :1].sigmoid()
    positive = int((mask > .5).sum().item())
    decoded = native_decoder(predictions[:, 1:], mask)[0].tolist() if positive else None
    # Independent transcription of the pinned semihard decision; no sigmoid on bits.
    selected = mask[0, 0] > .5
    reference = (predictions[0, 1:, selected].mean(dim=-1, dtype=torch.float64) > .5).tolist() if positive else None
    parity = decoded == reference
    if not parity:
        raise ValueError('Native WAM semihard parity failed')
    return dict(readable=bool(positive), decoded_hex=bits_hex(decoded) if decoded is not None else None,
                native=dict(mask_positive_pixels=positive, mask_pixels=mask.numel(),
                    mask_fraction=positive/mask.numel(), mask_mean=float(mask.mean().item()),
                    decoded_bits=decoded, parity=parity))


def read_wam(adapter, rgb):
    with adapter.torch.inference_mode():
        return wam_predictions(adapter.model.detect(adapter.tensor(rgb))['preds'], adapter.decode_message)


def read_e3(ev, rgb):
    from journal_bch_readout import detect_rgb
    features, latent = ev.features(rgb, 7), ev.reader.latent(rgb)
    call = detect_rgb(rgb, latent, ALPHA, ev.profile, features,
                      binding='soft', binding_mode='combined', roster_size=1)
    readable = bool(call['semantic']['read'])
    return dict(readable=readable, decoded_hex=call['semantic']['decoded_code'] if readable else None,
                native=call)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temp.replace(path)


def summarize(record):
    rows = record['rows']
    groups = {}
    for key in sorted({(r['method'], r['family'], r.get('strength', 'clean')) for r in rows}, key=str):
        group = [r for r in rows if (r['method'], r['family'], r.get('strength', 'clean')) == key]
        good = [r for r in group if r['status'] == 'ok']
        groups['/'.join(map(str, key))] = dict(planned=len(group), completed=len(good),
            statuses={s: sum(r['status'] == s for r in group) for s in sorted({r['status'] for r in group})},
            readable=sum(r['readout']['readable'] for r in good),
            exact=sum(r['scores']['assigned']['Q'] for r in good),
            strict_quality=sum(r['strict_quality'] for r in good),
            exact_and_quality=sum(r['strict_quality'] and r['scores']['assigned']['Q'] for r in good),
            wrong_complement=sum(r['scores']['complement']['Q'] for r in good),
            cyclic_q=sum(r['scores']['cyclic']['Q'] for r in good),
            own_q=sum(r['scores']['own_q']['Q'] for r in good),
            zero_filled_bit_accuracy_mean=sum(r['scores']['assigned']['zero_filled_bit_accuracy'] for r in good)/len(group),
            source_majorities=sum(sum(r['status'] == 'ok' and r['scores']['assigned']['Q']
                for r in group if r['source_id'] == sid) >= 2 for sid in IDS) if record['phase'] == 't3' else None)
    if record['phase'] == 'clean':
        positive = [r for r in rows if r['family'] != 'C0']
        negative = [r for r in rows if r['family'] in ('q', 'C0')]
        passed = (len(rows) == 36 and len(record['images']) == 30 and
            all(r['status'] == 'ok' for r in rows) and record.get('interface_checks') is True and
            all(r['scores']['assigned']['Q'] and r['strict_quality'] for r in positive) and
            all(not r['scores']['complement']['Q'] and not r['scores']['cyclic']['Q'] and
                (r['family'] != 'C0' or not r['scores']['own_q']['Q']) for r in negative) and
            all(r.get('retained_parity') is True for r in rows if r['method'] == 'E3' and r['family'] == 'q'))
    else:
        passed = None
    return dict(groups=groups, eligibility_pass=passed, planned_calls=len(rows),
                completed_calls=sum(r['status'] == 'ok' for r in rows), images=len(record['images']))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase', choices=('clean', 't3'), required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--clean-run', type=Path)
    args = p.parse_args()
    started = time.monotonic()
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    from journal_wam_probe import ASSET, REVISION, message
    source_record = json.loads(INPUT.read_text())
    sources = sorted(source_record['sources'], key=lambda s: s['source_id'])[:6]
    if tuple(s['source_id'] for s in sources) != IDS or tuple(s['payload']['q'] for s in sources) != TARGETS:
        raise ValueError('Frozen six-source schedule disagrees')
    rows = []
    for source in sources:
        sid = source['source_id']
        if args.phase == 'clean':
            for method, family in [('E3', 'q'), ('E3', 'C0'), ('WAM', 'q'), ('WAM', 'C0'), ('WAM', 'complement'), ('WAM', 'hash')]:
                rows.append(dict(source_id=sid, method=method, family=family, status='not_started'))
        else:
            for strength in (.1, .2):
                for seed in (9, 10, 11):
                    for method, family in [('E3', 'q'), ('WAM', 'q'), ('E3', 'C0'), ('WAM', 'C0')]:
                        rows.append(dict(source_id=sid, method=method, family=family, strength=strength,
                                         seed=seed, status='not_started'))
    record = dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=sys.argv, phase=args.phase, protocol=str(PROTOCOL), protocol_sha256=sha(PROTOCOL),
        data_split='previously consulted reserved development', seeds=[0] if args.phase == 'clean' else [9, 10, 11],
        started_at_utc=datetime.now(timezone.utc).isoformat(), duration_seconds=0., outcome='running',
        config=dict(wam_revision=REVISION, checkpoint=str(ASSET/'wam_mit.pth'), native_scaling_w=2.,
            float_precision='float32', execution_seed=0, cap_seconds=900, gpu_cap_bytes=GPU_CAP,
            ram_cap_bytes=RAM_CAP, min_available_ram_bytes=3*1024**3, cpu_threads=4,
            human_admissibility='missing', clean_quality=dict(psnr_gt=35, ssim_gt=.9, lpips_lt=.1)),
        sources=[], rows=rows, images=[dict(source_id=sid, family=family, method=method, status='not_started')
            for sid in IDS for family, method in [('q','E3'),('C0','shared'),('q','WAM'),('complement','WAM'),('hash','WAM')]]
            if args.phase == 'clean' else [], usd=0)
    torch = None

    def save():
        record['duration_seconds'] = time.monotonic()-started
        record['summary'] = summarize(record)
        write(out/'run.json', record)

    def budget():
        from fresh_e3_simplification import memory
        rss, peak, available = memory()
        allocated = int(torch.cuda.max_memory_allocated()) if torch is not None and torch.cuda.is_initialized() else 0
        record['peak_ram_bytes'] = max(record.get('peak_ram_bytes', 0), rss, peak)
        record['peak_gpu_bytes'] = max(record.get('peak_gpu_bytes', 0), allocated)
        if time.monotonic()-started >= 900 or rss > RAM_CAP or allocated > GPU_CAP or available < 3*1024**3:
            raise RuntimeError('Inclusive time/resource cap reached; remaining rows retained')

    save()
    try:
        budget()
        sys.path[:0] = [str(MAIN/'.thesis-build/journal-wam-deps'), str(ASSET/'source')]
        import numpy as np
        import torch
        from PIL import Image
        import three_threat_models as models
        from journal_vae_probe import Evaluator
        from journal_wam_probe import Adapter
        from journal_bch_analysis import endpoint, strict_quality
        models.block_network()
        random.seed(0); np.random.seed(0); torch.manual_seed(0); torch.set_num_threads(4)
        free, total = torch.cuda.mem_get_info()
        if free < GPU_CAP: raise RuntimeError('Less than 9 GiB free GPU')
        torch.cuda.set_per_process_memory_fraction(GPU_CAP/total)
        torch.cuda.reset_peak_memory_stats()
        record['config']['checkpoint_sha256'] = sha(ASSET/'wam_mit.pth')
        if record['config']['checkpoint_sha256'] != '90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2':
            raise ValueError('Pinned WAM checkpoint mismatch')
        for value in TARGETS + ('00000000', 'ffffffff', '80000001'):
            assert bits_hex(hex_bits(value)) == value
        for s in sources:
            if sha(s['canonical_path']) != s['sha256']: raise ValueError('Canonical identity mismatch')
            record['sources'].append(dict(source_id=s['source_id'], q=s['payload']['q'],
                canonical=s['canonical_path'], canonical_sha256=s['sha256'], full_image=s['full_image'],
                full_sha256=sha(s['full_image']), hash_control=bits_hex(message(s['source_id']))))
        record['message_diagnostics'] = dict(bit_ones=[sum(hex_bits(q)[i] for q in TARGETS) for i in range(32)],
            pair_distances=[dict(a=IDS[i], b=IDS[j], distance=(int(TARGETS[i],16)^int(TARGETS[j],16)).bit_count())
                for i in range(6) for j in range(i+1,6)],
            control_collisions=[s['source_id'] for s in record['sources'] if s['hash_control'] in
                (s['q'], f"{int(s['q'],16)^0xffffffff:08x}")])
        save()  # Fixed targets/distribution recorded before scientific scoring.
        budget(); tick = time.monotonic(); ev = Evaluator(); budget()
        adapter = Adapter(ASSET/'source', ASSET/'wam_mit.pth', 'cuda'); budget()
        record['model_load_seconds'] = time.monotonic()-tick
        record['config']['e3_profile'] = ev.profile
        record['environment'] = dict(torch=torch.__version__, numpy=np.__version__, gpu=torch.cuda.get_device_name(0),
                                     lpips_device=str(next(ev.lpips.parameters()).device))
        empty = torch.zeros((1,33,2,2))
        def never_called(*_): raise AssertionError('Empty mask invoked decoder')
        assert wam_predictions(empty, never_called)['decoded_hex'] is None
        fixed = dict(readable=True, decoded_hex=TARGETS[0])
        before = dict(fixed)
        assert evaluate(fixed, TARGETS[0])['Q'] and not evaluate(fixed, TARGETS[1])['Q'] and fixed == before
        record['interface_checks'] = True

        def load(path):
            with Image.open(path) as image:
                if image.mode != 'RGB' or image.size != (512,512): raise ValueError('RGB8 512 required')
                return np.asarray(image, np.uint8).copy()

        def delivered(rgb, name):
            path = out/'images'/f'{name}.png'; Image.fromarray(rgb).save(path)
            return path, load(path)

        def score(row, source, rgb, canonical, path, marking_input=None):
            budget(); tick = time.monotonic()
            rd = read_e3(ev, rgb) if row['method'] == 'E3' else read_wam(adapter, rgb)
            torch.cuda.synchronize()
            row['read_seconds'] = time.monotonic()-tick
            row['readout'] = rd
            own = source['payload']['q']; complement = f'{int(own,16)^0xffffffff:08x}'
            assigned = complement if row['family'] == 'complement' else bits_hex(message(source['source_id'])) if row['family'] == 'hash' else own
            row['scores'] = {key: evaluate(rd, value) for key, value in dict(assigned=assigned, own_q=own,
                complement=complement, cyclic=TARGETS[(IDS.index(source['source_id'])+1)%6]).items()}
            row['assigned_hex'] = assigned; row['image'] = str(path)
            budget(); row['quality_source'] = ev.metrics(canonical, rgb)
            row['strict_quality'] = strict_quality(row['quality_source'])
            if marking_input is not None: row['quality_marking_input'] = ev.metrics(marking_input, rgb)
            if row['method'] == 'E3': row['native_endpoints'] = endpoint(rd['native'], source['payload'])
            if args.phase == 'clean' and row['method'] == 'E3' and row['family'] == 'q':
                retained = source['clean']['full']
                old = retained['calls'][ALPHA]['semantic']
                row['retained_parity'] = (rd['readable'] == old['read'] and rd['native']['semantic']['decoded_code'] == old['decoded_code']
                    and row['scores']['assigned']['Q'] == retained['endpoints'][ALPHA]['Q']
                    and row['strict_quality'] == retained['strict_quality'])
                if not row['retained_parity']: raise RuntimeError('Retained E3 clean classification disagrees')
            row['status'] = 'ok'; save(); budget()
            print(json.dumps({k: row[k] for k in ('source_id','method','family','status')}), flush=True)

        if args.phase == 'clean':
            for source in sources:
                sid = source['source_id']; canonical = load(source['canonical_path'])
                for family, method in [('q','E3'), ('C0','shared'), ('q','WAM'), ('complement','WAM'), ('hash','WAM')]:
                    budget(); path = source['full_image'] if method == 'E3' else source['canonical_path']
                    tick = time.monotonic()
                    if method == 'WAM':
                        q = source['payload']['q']
                        target = f'{int(q,16)^0xffffffff:08x}' if family == 'complement' else bits_hex(message(sid)) if family == 'hash' else q
                        rgb = adapter.embed(canonical, hex_bits(target), 2.)
                        torch.cuda.synchronize(); embed_seconds = time.monotonic()-tick
                        path, rgb = delivered(rgb, f'{sid}-WAM-{family}')
                    else: rgb = load(path); embed_seconds = None
                    entry = next(i for i in record['images'] if (i['source_id'],i['family'],i['method']) == (sid,family,method))
                    entry.update(image=str(path), sha256=sha(path), status='ok', embed_seconds=embed_seconds)
                    save()
                    for row in rows:
                        if row['source_id'] == sid and row['family'] == family and (row['method'] == method or method == 'shared'):
                            score(row, source, rgb, canonical, path)
        else:
            raise NotImplementedError('Conditional T3 invocation must be committed after clean PASS')
        record['outcome'] = 'completed'; save()
    except Exception:
        record['outcome'] = 'failed'; record['error'] = traceback.format_exc()
        print(record['error'], flush=True)
        for row in rows:
            if row['status'] == 'not_started': row['status'] = 'unattempted_after_failure'
        for entry in record['images']:
            if entry['status'] == 'not_started': entry['status'] = 'unattempted_after_failure'
        save()
        return 1
    finally:
        save()
    print(json.dumps(record['summary']), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
