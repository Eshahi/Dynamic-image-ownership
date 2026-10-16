"""Select original live-action shot/frame pairs by metadata only; no pixels."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import re
import urllib.request

BASE = 'https://media.xiph.org/tearsofsteel/tearsofsteel-footage-exr/'
DOCS = Path(__file__).resolve().parents[1] / 'research/journal-upgrade-20261009'


def fetch(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise


def shot_metadata(shot):
    url = BASE + shot + 'linear_hd/'
    try:
        raw = fetch(url)
    except Exception as exc:
        return dict(shot=shot, status='unavailable metadata', error=str(exc))
    text = raw.decode()
    files = sorted(set(re.findall(r'href="([^"/]+\.exr)"', text)))
    numbered = {int(re.search(r'(\d+)\.exr$', name).group(1)): name for name in files}
    if not numbered:
        return dict(shot=shot, status='no numbered EXR frames')
    first = min(numbered)
    if first + 72 not in numbered:
        return dict(shot=shot, status='no exact three-second second frame', frames=len(files))
    frames = []
    for number in (first, first + 72):
        name = numbered[number]
        row = next(r for r in text.split('<tr>') if f'href="{name}"' in r)
        size = re.search(r'<td align="right">\s*([\d.]+[KMG]?)\s*</td>', row.split('</a>')[-1]).group(1)
        frames.append(dict(frame_index=number, filename=name, url=url + name,
                           listing_rounded_size=size, raw_sha256=None))
    return dict(shot=shot.rstrip('/'), status='eligible', metadata_url=url,
                metadata_sha256=hashlib.sha256(raw).hexdigest(), available_frame_count=len(files),
                separation_frames=72, separation_seconds=3.0, frames=frames)


def main():
    licence = fetch(BASE + 'README.txt')
    if b'24 frames per second' not in licence or b'Attribution 3.0' not in licence:
        raise ValueError('upstream fps/licence statement changed')
    receipt = DOCS / 'registry-near-duplicate-source-license.txt'
    receipt.write_bytes(licence)
    raw = fetch(BASE)
    shots = sorted(set(re.findall(r'href="(\d{2}_[^"/]+/)"', raw.decode())))
    selected, inspected = [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        # Inspect fixed sorted metadata batches; select only the first20 eligible.
        for start in range(0, len(shots), 20):
            rows = list(pool.map(shot_metadata, shots[start:start+20]))
            for row in rows:
                inspected.append(row)
                if row['status'] == 'eligible' and len(selected) < 20:
                    row['pair_id'] = 'tos-' + row['shot']
                    row['split'] = 'calibration' if len(selected) < 7 else 'evaluation'
                    selected.append(row)
                if len(selected) == 20:
                    break
            if len(selected) == 20:
                break
    if len(selected) != 20:
        raise ValueError('fewer than20 eligible shots')
    out = dict(schema='registry-real-near-duplicate-selection-v1', prepared_date='2026-10-16',
        status='metadata-only; no source frames downloaded or decoded',
        source='Tears of Steel original live-action camera footage; linear_hd OpenEXR derivatives',
        source_root=BASE, source_index_sha256=hashlib.sha256(raw).hexdigest(),
        license='CC BY 3.0', license_url='https://creativecommons.org/licenses/by/3.0/',
        original_license_receipt_url=BASE+'README.txt',
        license_receipt_path=str(receipt.relative_to(DOCS.parents[1])),
        license_receipt_sha256=hashlib.sha256(licence).hexdigest(),
        attribution='(CC) Blender Foundation | mango.blender.org',
        retained_rights='Logos/trademarks excluded; actors retain portrait and privacy rights.',
        supporting_primary_page='https://mango.blender.org/category/filming/',
        fps=24, fps_source='Original footage README, not a re-encoded movie assumption',
        selection_rule='Ascending ASCII original numbered shot directory; require linear_hd EXR earliest frame and exact frame+72. First20 eligible. First7 calibration, remaining13 evaluation. No pixels, features or outcomes used. No similarity or aesthetic exclusion.',
        independence_limit='Shots from one production may repeat scenes/actors and are not independent scene samples. Same film scene families must be disclosed; distinct shot IDs do not imply independent clusters.',
        identity_definition='Two separately captured video frames are distinct published instances even with the same scene/object.',
        decoding=dict(PIL='installed12.3.0; no native EXR reader', imageio='installed; EXR backend not established',
                      OpenEXR=False, cv2=False,
                      route='Installed ffmpeg9.0.1 full build advertises native OpenEXR decoder. No installer needed; real-frame decode not yet tested.',
                      color='linear_hd is scene-linear: freeze a common linear-to-sRGB conversion before first descriptor use; do not silently treat linear floats as gamma-encoded RGB.'),
        selected=selected, inspected_shots=inspected, source_frames_downloaded=0,
        pending='HEAD exact content lengths and raw SHA256 before decode; actual EXR backend check and fixed color conversion before descriptor computation.')
    target = DOCS / 'registry-near-duplicate-selection.json'
    with target.open('x', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(selected=[r['shot'] for r in selected], pairs=len(selected), frames=40)))


if __name__ == '__main__':
    main()
