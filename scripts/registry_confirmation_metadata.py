"""Build held-out reservations from metadata; never open an image or raw asset.

Default replay uses retained HTTP directory listings. --refresh-listings fetches
only HTML directory listings from the original Tears of Steel footage server.
No image, EXR, annotation, descriptor, score, or outcome file is read.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
ADMITTED = Path('C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5')
BASE = 'https://media.xiph.org/tearsofsteel/tearsofsteel-footage-exr/'
META_NAME = re.compile(r'(manifest|schedule|selection|external-index|input|receipt|acquisition|sources|near-duplicates|source-pins|m1b-plan|config|^run\.json$)', re.I)
DENY_NAME = re.compile(r'(descriptor|score|metric|result|threshold|outcome|checkpoint|model_index)', re.I)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_meta(path):
    if path.suffix.lower() not in ('.json', '.jsonl', '.csv', '.md', '.txt', '.py'):
        raise ValueError(f'Not metadata: {path}')
    return path.read_bytes()


def pin(path):
    return dict(path=path.as_posix(), sha256=digest(read_meta(path)))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def metadata_files():
    """Inventory metadata, including historical runs, without visiting asset bytes."""
    roots = [ROOT/'research', MAIN/'research', ADMITTED/'research',
             MAIN/'.thesis-build', ROOT/'.thesis-build']
    found = set()
    for root in roots:
        if not root.exists():
            continue
        for directory, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if not any(x in d.lower() for x in
                ('venv', 'wheel', 'site-packages', 'upstream', 'literature', '.git',
                 'registry-confirmation', 'model', 'snapshot', 'node_modules')))
            for name in sorted(files):
                p = Path(directory)/name
                if p.suffix.lower() not in ('.json', '.jsonl', '.csv'):
                    continue
                if META_NAME.search(name) and not DENY_NAME.search(name):
                    found.add(p)
    return sorted(found, key=lambda p: p.as_posix())


def build_index(out):
    split_path = ADMITTED/'data/splits.csv'
    manifest_path = ADMITTED/'data/b4-admission-20260926/source-manifest.csv'
    split = list(csv.DictReader(read_meta(split_path).decode('utf-8-sig').splitlines()))
    receipts = list(csv.DictReader(read_meta(manifest_path).decode('utf-8-sig').splitlines()))
    key = lambda r: tuple(r[k] for k in ('domain', 'release_id', 'source_split', 'source_id'))
    receipt_map = {key(r): r for r in receipts}
    candidates = sorted((r for r in split if r['domain']=='div2k' and r['study_split']=='test'), key=lambda r:r['source_uid'])
    if len(candidates)!=300 or len({r['group_id'] for r in candidates})!=300:
        raise ValueError('Expected all 300 DIV2K test sources and groups')
    uids = {r['source_uid'] for r in candidates}
    hashes = {r['raw_sha256'] for r in candidates}
    groups = {r['group_id'] for r in candidates}
    admitted_exposed = [r for r in split if r['study_split']!='test']
    overlap = [r['source_uid'] for r in admitted_exposed if r['source_uid'] in uids or r['raw_sha256'] in hashes or r['group_id'] in groups]
    if overlap:
        raise ValueError(f'Admitted development/calibration overlap: {overlap}')
    inspected, hits, failures = [], [], []
    def without_exclusions(obj):
        if isinstance(obj,dict):
            return {k:without_exclusions(v) for k,v in obj.items() if not re.search(r'exclu',k,re.I)}
        if isinstance(obj,list):
            return [without_exclusions(v) for v in obj]
        return obj
    for path in metadata_files():
        try:
            raw = read_meta(path)
            text = raw.decode('utf-8-sig')
            role='scientific-use-or-reservation-metadata'
            if 'b3-diffusiondb-integrity' in path.as_posix() or 'cloud-transfer-' in path.as_posix():
                role='admission-or-transport-only-not-scientific-use'
            original=text
            if path.suffix=='.json':
                text=json.dumps(without_exclusions(json.loads(text)))
            if role!='scientific-use-or-reservation-metadata':
                text=''
            # Compare exact UID/hash/group tokens, never dimensions or outcomes.
            tokens = set(re.findall(r'div2k:[A-Za-z0-9:_-]+|(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])', text))
            matches = dict(source_uids=sorted(tokens & uids), raw_sha256=sorted(tokens & hashes), group_ids=sorted(tokens & groups))
            original_tokens=set(re.findall(r'div2k:[A-Za-z0-9:_-]+|(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])', original))
            inspected.append(dict(path=path.as_posix(), sha256=digest(raw),role=role,
                allocation_exclusion_or_transport_match_count=len((original_tokens & (uids|hashes|groups))-(tokens & (uids|hashes|groups))), **matches))
            if any(matches.values()):
                hits.append(inspected[-1])
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            failures.append(dict(path=path.as_posix(), error=str(exc)))
    if hits or failures:
        write(out/'div2k-exposure.json', dict(overlap=hits, unreadable=failures, inspected=inspected))
        raise ValueError('Metadata exposure match or unreadable inventory requires resolution')
    rows=[]
    for rank, r in enumerate(candidates):
        m=receipt_map[key(r)]
        if m['raw_sha256']!=r['raw_sha256'] or r['primary_group_representative'].lower()!='true':
            raise ValueError('Receipt mismatch or non-primary source')
        raw_path=MAIN/'data/raw'/m['relative_path']
        rows.append(dict(index=rank, **{k:r[k] for k in ('source_uid','source_id','group_id','domain','release_id','source_split','study_split','raw_sha256')},
            primary_group_representative=True, raw_path=raw_path.as_posix(), raw_relative_path=m['relative_path'],
            raw_path_exists=raw_path.is_file(), raw_size_bytes=int(m['raw_size_bytes']),
            license_reference=m['license_reference'], rights_status=m['rights_status'], use_limitations=m['use_limitations']))
    if not all(r['raw_path_exists'] for r in rows):
        raise ValueError('Missing recorded raw path (existence only; bytes untouched)')
    inputs=[pin(split_path), pin(manifest_path)]
    write(out/'div2k-heldout-index.json', dict(schema='registry-confirmation-heldout-index-v1', status='metadata-only; pixels locked',
        rule='All admitted DIV2K test primary representatives; ascending source_uid; no outcome-dependent selection',
        input_pins=inputs, source_count=300, group_count=300, sources=rows))
    write(out/'div2k-exposure.json', dict(schema='registry-confirmation-exposure-metadata-v1', input_pins=inputs,
        admitted_non_test_rows=len(admitted_exposed), admitted_non_test_overlap=overlap,
        metadata_file_count=len(inspected), overlap=hits, unreadable=failures, inspected=inspected,
        scope='Known recorded development/calibration and historical run metadata in MAIN, journal and admitted worktrees. Exact UID/raw SHA/group token exclusion; raw paths existence only.',
        limitations=['Historical ingestion/canonicalization is disclosed, not a never-decoded claim.',
            'Cannot certify undocumented human or off-repository exposure.',
            'Admitted test partition itself is allocation metadata, not scientific exposure; intentionally excluded from exposure scan.',
            'Numeric IDs without domain cannot establish DIV2K identity; full UID and recorded raw hashes are the definitive joins.']))
    return len(inspected)


def fetch_listing(url):
    if not url.startswith(BASE) or not url.endswith('/'):
        raise ValueError('Only directory metadata GETs are allowed')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                if 'text/html' not in response.headers.get('Content-Type',''):
                    raise ValueError('Directory listing is not HTML')
                return response.read().decode('utf-8')
        except Exception:
            if attempt==2:
                raise


def reserve_shots(out, refresh, reserve_count):
    docs=ROOT/'research/journal-upgrade-20261009'
    previous=[docs/'registry-near-duplicate-selection.json', docs/'round3-near-duplicate-selection.json']
    prev=[json.loads(read_meta(p)) for p in previous]
    used={r['shot'].rstrip('/') for p in prev for r in p['selected']}
    prior_last=prev[-1]['selected'][-1]['shot'].rstrip('/')
    cache_path=out/'tears-of-steel-shots-listings.json'
    cache=json.loads(cache_path.read_text('utf-8')) if cache_path.exists() and not refresh else {'root_html':fetch_listing(BASE), 'shot_html':{}}
    listing=cache['root_html']
    shots=list(dict.fromkeys(re.findall(r'href="(\d{2}_[^"/]+/)"', listing)))
    last=shots.index(prior_last+'/')
    inspected=[]; eligible=[]
    def inspect(shot):
        url=BASE+shot+'linear_hd/'
        if shot not in cache['shot_html']:
            try:
                cache['shot_html'][shot]=fetch_listing(url)
            except Exception as exc:
                cache['shot_html'][shot]={'metadata_unavailable':str(exc)}
        html=cache['shot_html'][shot]
        if isinstance(html,dict):
            return dict(shot=shot.rstrip('/'),listing_rank=shots.index(shot),metadata_url=url,
                        eligible=False,status='metadata unavailable',**html)
        files=sorted(set(re.findall(r'href="([^"/]+\.exr)"', html)))
        numbered={int(re.search(r'(\d+)\.exr$', name).group(1)):name for name in files}
        first=min(numbered) if numbered else None
        valid=first is not None and len(files)>=289 and all(first+o in numbered for o in (0,72,144,288))
        row=dict(shot=shot.rstrip('/'), listing_rank=shots.index(shot), metadata_url=url, metadata_sha256=digest(html.encode()), frame_count=len(files), eligible=valid)
        if valid:
            row['frames']=[dict(offset=o, frame_index=first+o, filename=numbered[first+o],url=url+numbered[first+o],raw_sha256=None) for o in (0,72,144,288)]
            row['pairs']=[dict(pair_id=f'tos-{shot.rstrip("/")}-o{o:03d}',frame_offsets=[0,o]) for o in (72,144,288)]
        return row
    pending=[s for s in shots[last+1:] if s.rstrip('/') not in used]
    # Fixed batches preserve listing order regardless of concurrent HTTP completion.
    for start in range(0,len(pending),8):
        with ThreadPoolExecutor(max_workers=8) as pool:
            batch=list(pool.map(inspect,pending[start:start+8]))
        inspected.extend(batch)
        write(cache_path,cache)
        eligible.extend(r for r in batch if r['eligible'])
        if len(eligible)>=20+reserve_count:
            break
    write(cache_path,cache)
    if len(eligible)<20:
        raise ValueError('Insufficient metadata-eligible shots for selected20')
    write(out/'tears-of-steel-shots-index.json',dict(schema='registry-confirmation-shot-reservation-v1',status='metadata-only; no frames fetched',
        rule='Strictly after final round3 shot in upstream listing order, >=289 frames, exact earliest+0/72/144/288; first20 eligible; next eligible shots replace whole duplicate shots only during approved preflight',
        after_round3_shot=prior_last, source_root=BASE, source_index_sha256=digest(listing.encode()),
        previous_selection_pins=[pin(p) for p in previous], source_selection_code_pins=[pin(ROOT/'scripts/registry_round3_selection.py'),pin(ROOT/'scripts/registry_near_duplicate_selection.py')],
        license=prev[0]['license'],license_url=prev[0]['license_url'],license_receipt_sha256=prev[0]['license_receipt_sha256'],attribution=prev[0]['attribution'],
        selected=eligible[:20],ordered_replacement_reserve=eligible[20:20+reserve_count],inspected=inspected,
        selected_shots=20,selected_pairs=60,selected_unique_frames=80,
        requested_maximum_reserve_shots=reserve_count,available_reserve_shots=len(eligible[20:20+reserve_count]),
        preflight='Only after exact-manifest approval: download, hash and canonicalize; compare every frame against every recorded development frame canonical hash, replace entire duplicate shot using ordered reserve, retain failures and replacements in journal.',
        limitations=['Same film as development; distinct shots are not independent scene families.','Frame digests and canonical duplicate exclusion remain pending approved preflight.','Reserve exhaustion requires stop, never a performance-based replacement.']))
    return len(eligible[20:20+reserve_count])


def development_frame_exposure(out):
    """Retain known footage digest identities for the future approved preflight."""
    files=sorted((MAIN/'.thesis-build/assets').glob('*/near-duplicates.json'))
    frames=[]
    for path in files:
        obj=json.loads(read_meta(path))
        if obj.get('data_split')!='development-reserved':
            raise ValueError(f'Unexpected footage inventory split: {path}')
        for pair in obj['pairs']:
            for frame in pair['frames']:
                if not frame['url'].startswith(BASE):
                    raise ValueError('Unexpected development footage URL')
                frames.append(dict(shot=pair['shot'],pair_id=pair['pair_id'],url=frame['url'],
                    **{k:frame[k] for k in ('raw_sha256','canonical_png_sha256','rgb8_sha256','canonical_path')}))
    write(out/'development-frame-exposure-index.json',dict(schema='registry-development-frame-digest-exposure-v1',
        input_pins=[pin(p) for p in files],record_count=len(frames),unique_urls=len({r['url'] for r in frames}),
        unique_rgb8_sha256=len({r['rgb8_sha256'] for r in frames}),frames=frames,
        scope='All acquired Tears of Steel development frame receipts found under MAIN .thesis-build/assets/*/near-duplicates.json; no frame bytes read.',
        preflight='Compare all selected new frames against this complete recorded footage digest set after the user approves the exact manifest. Retain the prior receipt inventories as inputs.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'research/registry-confirmation')
    parser.add_argument('--refresh-listings',action='store_true')
    parser.add_argument('--reserve-count',type=int,default=20)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    n=build_index(args.out)
    development_frame_exposure(args.out)
    reserve=reserve_shots(args.out,args.refresh_listings,args.reserve_count)
    print(json.dumps(dict(div2k_sources=300,exposure_metadata_files=n,shots=20,pairs=60,reserve_shots=reserve,heldout_bytes_opened=0)))


if __name__=='__main__':
    main()
