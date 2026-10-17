"""Conditional registry source acquisition/canonicalization; no feature extraction.

Run with the scientific Python after a complete chosen-method screen pass. All
raw files, including failed/duplicate objects, stay in the new output directory.
Canonical exclusion roots are read as bytes/hashes only, never decoded.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'research/journal-upgrade-20261009'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def immutable_json(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f'Existing receipt differs; preserve it: {path}')
    else:
        with path.open('xb') as f:
            f.write(raw)


def exr_rgb(raw_path, ffmpeg):
    import numpy as np
    from PIL import Image
    # Original selected metadata declares this fixed geometry. Decoding does not
    # need ffprobe or an EXR Python dependency; ffmpeg's native decoder is used.
    command = [ffmpeg, '-nostdin', '-v', 'error', '-threads', '1', '-i', str(raw_path),
               '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gbrpf32le', 'pipe:1']
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    expected = 3 * 1012 * 1920
    values = np.frombuffer(result.stdout, dtype='<f4')
    if values.size != expected or not np.isfinite(values).all():
        raise ValueError('Expected finite1920x1012 GBR float EXR decode; no geometry substitution')
    gbr = values.reshape(3, 1012, 1920)
    rgb = np.moveaxis(gbr[[2, 0, 1]], 0, -1).astype(np.float64)
    clipped_low, clipped_high = int((rgb < 0).sum()), int((rgb > 1).sum())
    linear = np.clip(rgb, 0., 1.)
    srgb = np.where(linear <= .0031308, 12.92 * linear, 1.055 * linear ** (1. / 2.4) - .055)
    native = np.floor(srgb * 255. + .5).astype(np.uint8)
    resized = np.asarray(Image.fromarray(native).resize((512, 512), Image.Resampling.BICUBIC)).copy()
    receipt = dict(schema='registry-original-footage-rgb512-v1', native_shape=[1012, 1920, 3],
        decoded_layout='ffmpeg nativeEXR gbrpf32le, reorder GBR toRGB',
        conversion='float64; cliplinear[0,1]; x<=0.0031308:12.92x else1.055*x**(1/2.4)-0.055; floor255*sRGB+0.5 toRGB8',
        resize='Pillow BICUBIC from1920x1012 to512x512, same stretch geometry asCOCO canonicalization',
        clipped_low_components=clipped_low, clipped_high_components=clipped_high,
        native_rgb8_sha256=sha(native.tobytes()), rgb8_sha256=sha(resized.tobytes()), command=command)
    return resized, receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--round3', action='store_true', help='40 evaluation sources, 60 prescribed pairs; remove EXRs after hashed canonical receipt')
    p.add_argument('--screen-dir', type=Path, required=True)
    p.add_argument('--chosen-method', choices=('e3-s1', 'f5-r2'), required=True)
    p.add_argument('--sources', type=Path, default=DOCS/'registry-fresh-development-selection.json')
    p.add_argument('--near-duplicates', type=Path, default=DOCS/'registry-near-duplicate-selection.json')
    p.add_argument('--output-dir', type=Path, required=True, help='New assets/receipt directory; compatible interrupted acquisition can resume')
    p.add_argument('--canonical-exclusion-root', type=Path, action='append', required=True,
                   help='Existing admitted/held-out/M2/prior-development canonicalPNG root; repeat to cover all families. Hashes only, never decode.')
    p.add_argument('--ffmpeg', default=shutil.which('ffmpeg'))
    p.add_argument('--max-download-bytes', type=int, default=2_000_000_000,
                   help='This acquisition cap; parent must separately verify global30GB headroom')
    a = p.parse_args()
    screen_path = a.screen_dir/'run.json'
    screen = read(screen_path)
    descriptor = screen.get('selected_descriptor')
    if (screen.get('outcome') != 'screen_pass_hypothesis' or
        screen.get('config', {}).get('chosen_method') != a.chosen_method or
        descriptor not in ('D1', 'D2') or screen.get('descriptors', {}).get(descriptor, {}).get('decision') != 'pass'):
        raise ValueError('Acquire only after a complete chosen-method registry screen pass')
    sources, near = read(a.sources), read(a.near_duplicates)
    if len(sources['selected']) != (40 if a.round3 else 60) or len(near['selected']) != (60 if a.round3 else 20):
        raise ValueError('Frozen60 sources and20 pairs required')
    ids = [r['source_id'] for r in sources['selected']]
    if ids != sorted(set(ids)) or min(ids) <= 790:
        raise ValueError('Source ID ordering differs from frozen rule')
    if [r['split'] for r in sources['selected']] != (['evaluation']*40 if a.round3 else ['calibration']*20+['evaluation']*40):
        raise ValueError('Source split differs')
    if [r['split'] for r in near['selected']] != (['evaluation']*60 if a.round3 else ['calibration']*7+['evaluation']*13):
        raise ValueError('Pair split differs')
    if not a.ffmpeg:
        raise ValueError('Existing ffmpeg nativeEXR decoder required; do not install automatically')
    out = a.output_dir.resolve()
    for root in a.canonical_exclusion_root:
        root = root.resolve()
        if not root.is_dir() or root == out or out.is_relative_to(root):
            raise ValueError('Exclusion roots must exist and exclude the new output directory')
    hashes, png_count = set(sources['raw_sha256_exclusions']), 0
    inventory = []
    previous = read(out/'acquisition-config.json') if (out/'acquisition-config.json').exists() else None
    # A running development job can add PNGs under these roots. Resume the
    # frozen pre-acquisition inventory, checking its bytes, rather than silently
    # changing the exclusion evidence or rejecting a compatible interruption.
    recorded = previous['canonical_exclusion_inventory'] if previous else None
    recorded_hashes = {row['path']: row['sha256'] for row in recorded} if recorded else {}
    roots = [root.resolve() for root in a.canonical_exclusion_root]
    if recorded and any(not any(Path(row['path']).is_relative_to(root) for root in roots) for row in recorded):
        raise ValueError('Resume roots do not cover the original exclusion inventory')
    for root in roots:
        paths = ([Path(row['path']) for row in recorded if Path(row['path']).is_relative_to(root)]
                 if recorded is not None else sorted(root.rglob('*.png')))
        if not paths:
            raise ValueError(f'Canonical exclusion root has noPNG: {root}')
        for path in paths:
            value = sha(path.read_bytes())
            if recorded is not None:
                expected = recorded_hashes[str(path)]
                if value != expected:
                    raise ValueError(f'Original exclusion bytes changed: {path}')
            hashes.add(value)
            inventory.append(dict(path=str(path), sha256=value))
            png_count += 1
    base_exclusions = hashes.copy()
    config = dict(schema='registry-fresh-acquire-config-v1', chosen_method=a.chosen_method,
        screen_sha256=sha(screen_path.read_bytes()), sources_sha256=sha(a.sources.read_bytes()),
        near_duplicates_sha256=sha(a.near_duplicates.read_bytes()),
        canonical_exclusion_inventory=inventory, canonical_exclusion_PNG_count=png_count,
        ffmpeg=str(Path(a.ffmpeg).resolve()), max_download_bytes=a.max_download_bytes,
        side_information='acquisition only; no feature extraction or registry lookup')
    out.mkdir(parents=True, exist_ok=True)
    immutable_json(out/'acquisition-config.json', config)
    (out/'raw').mkdir(exist_ok=True)
    (out/'canonical').mkdir(exist_ok=True)
    consumed = sum(x.stat().st_size for x in (out/'raw').iterdir() if x.is_file())
    started = time.monotonic()
    log = out/'acquisition.jsonl'

    def emit(row):
        with log.open('a', encoding='utf-8') as f:
            f.write(json.dumps(row, allow_nan=False)+'\n')

    prepared = {}
    urls = {}
    if a.round3 and log.exists():
        for line in log.read_text(encoding='utf-8').splitlines():
            event = json.loads(line)
            if event.get('kind') == 'prepared':
                prepared[event['label']] = event['receipt']
                urls[event['receipt']['url']] = event['receipt']

    def acquire(row, label, is_exr=False):
        nonlocal consumed
        if a.round3 and label in prepared:
            receipt = prepared[label]
            if receipt['url'] != row['url'] or sha(Path(receipt['canonical_path']).read_bytes()) != receipt['canonical_png_sha256']:
                raise ValueError('Resume receipt mismatch')
            return receipt
        if a.round3 and is_exr and row['url'] in urls:
            prior = urls[row['url']]
            dest = out/'canonical'/f'{label}-rgb512.png'
            if not dest.exists():
                shutil.copyfile(prior['canonical_path'], dest)
            receipt = dict(row, **prior)
            receipt['canonical_path'] = str(dest)
            receipt['shared_source_frame'] = prior['canonical_path']
            emit(dict(kind='prepared', label=label, receipt=receipt))
            prepared[label] = receipt
            return receipt
        raw_path = out/'raw'/f'{label}-{row["filename"]}'
        if not raw_path.exists():
            for attempt in range(3):
                partial = raw_path.with_name(raw_path.name+f'.partial-{time.time_ns()}')
                try:
                    with urllib.request.urlopen(row['url'], timeout=60) as response, partial.open('xb') as f:
                        while True:
                            chunk = response.read(1_048_576)
                            if not chunk:
                                break
                            if consumed+len(chunk) > a.max_download_bytes:
                                raise RuntimeError('Acquisition byte cap reached; retain partial object')
                            f.write(chunk)
                            consumed += len(chunk)
                    partial.rename(raw_path)
                    break
                except Exception as exc:
                    emit(dict(kind='download_failure', label=label, attempt=attempt+1, partial=str(partial), error=str(exc)))
                    if attempt == 2 or 'byte cap' in str(exc):
                        raise
        raw = raw_path.read_bytes()
        raw_hash = sha(raw)
        if raw_hash in hashes:
            raise ValueError(f'RawSHA overlap before decode: {label}; retained, no automatic substitution')
        if row.get('size_bytes') is not None and len(raw) != row['size_bytes']:
            raise ValueError('Declared raw size mismatch; retain object')
        # Only after raw identity checks may a decoder see the image.
        if is_exr:
            rgb, canonicalization = exr_rgb(raw_path, a.ffmpeg)
        else:
            from m1b_canonical_source import canonicalize
            rgb, canonicalization = canonicalize(raw, raw_hash)
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(rgb).save(buf, format='PNG')
        png = buf.getvalue()
        png_hash, pixel_hash = sha(png), sha(rgb.tobytes())
        if png_hash in hashes or pixel_hash in hashes:
            raise ValueError(f'CanonicalPNG/pixelSHA overlap before reservation: {label}; no automatic substitution')
        path = out/'canonical'/f'{label}-rgb512.png'
        if path.exists():
            if path.read_bytes() != png:
                raise ValueError('Existing canonical differs; refuse overwrite')
        else:
            with path.open('xb') as f:
                f.write(png)
        hashes.update((raw_hash, png_hash, pixel_hash))
        receipt = dict(row, raw_path=str(raw_path), raw_sha256=raw_hash, size_bytes=len(raw),
            canonical_path=str(path), sha256=png_hash, canonical_png_sha256=png_hash,
            rgb8_sha256=pixel_hash, canonicalization=canonicalization,
            raw_overlap=False, canonical_overlap=False, data_split='development-reserved', development_reserved=True)
        emit(dict(kind='prepared', label=label, receipt=receipt))
        if a.round3:
            prepared[label] = receipt
            urls[row['url']] = receipt
            if is_exr:
                raw_path.unlink()
        print(f'prepared {label}: {len(raw)}bytes', flush=True)
        return receipt

    try:
        acquired = [acquire(row, f'coco-{row["source_id"]}') for row in sources['selected']]
        pairs = []
        for row in near['selected']:
            frames = [acquire(dict(frame, license=near['license'], license_url=near['license_url'],
                                   attribution=near['attribution'], split=row['split']),
                              row['pair_id']+f'-{i}', True) for i, frame in enumerate(row['frames'])]
            pairs.append(dict(row, frames=frames, left_path=frames[0]['canonical_path'], right_path=frames[1]['canonical_path']))
        common = dict(config_sha256=sha((out/'acquisition-config.json').read_bytes()), data_split='development-reserved')
        immutable_json(out/'sources.json', dict(schema='registry-fresh-acquired-v1', **common, sources=acquired))
        immutable_json(out/'near-duplicates.json', dict(schema='registry-near-duplicates-acquired-v1', **common,
            license=near['license'], license_receipt_sha256=near['license_receipt_sha256'], pairs=pairs))
        emit(dict(kind='complete', consumed_download_bytes=consumed, elapsed_seconds=time.monotonic()-started,
                  initial_exclusion_hash_count=len(base_exclusions)))
    except Exception as exc:
        emit(dict(kind='failed', error=str(exc), elapsed_seconds=time.monotonic()-started))
        raise


if __name__ == '__main__':
    main()
