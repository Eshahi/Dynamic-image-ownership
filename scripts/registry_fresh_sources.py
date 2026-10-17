"""Metadata-only conditional Step 2b reservation; no network/image decoding."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'research/journal-upgrade-20261009'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--round3', action='store_true')
    args = parser.parse_args()
    prior_path = DOCS / 'fresh-development-selection.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    ids, flickr, hashes = set(), set(), set(prior['raw_sha256_exclusions'])
    inventories = []

    def inspect(value):
        if isinstance(value, dict):
            # These are source identity inventories, never image annotations.
            for key, item in value.items():
                if key in ('source_id', 'coco_id') and str(item).isdigit() and value.get('domain', 'ms-coco') == 'ms-coco':
                    ids.add(int(item))
                if key in ('source_ids', 'fixed_twelve_ids') and isinstance(item, list):
                    ids.update(int(x) for x in item if str(x).isdigit())
                if 'sha256' in key and isinstance(item, str) and re.fullmatch('[0-9a-f]{64}', item):
                    hashes.add(item)
                if key == 'flickr_photo_id' and str(item).isdigit():
                    flickr.add(str(item))
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
        elif isinstance(value, str):
            for match in re.finditer(r'(?:ms-coco:coco-2017:(?:train2017|val2017):|(?:train2017|val2017)/)(\d+)', value):
                ids.add(int(match.group(1)))
            match = re.search(r'/([0-9]+)_[^/]+\.(?:jpg|png)', value)
            if match and ('flickr' in value):
                flickr.add(match.group(1))

    paths = [Path(x['path']) for x in prior['exclusion_inventories']]
    paths += [DOCS / 'fresh-development-inputs.json', prior_path]
    if args.round3:
        paths += [DOCS/'registry-fresh-development-selection.json', Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/registry-fresh-20261016/sources.json')]
    for path in paths:
        if path.suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as f:
                data = list(csv.DictReader(f))
        else:
            data = json.loads(path.read_text(encoding='utf-8-sig'))
        inspect(data)
        inventories.append(dict(path=str(path), sha256=digest(path), purpose='identity/hash exclusion only'))
    metadata = Path(prior['source_metadata']['path'])
    raw = metadata.read_bytes()
    if hashlib.sha256(raw).hexdigest() != prior['source_metadata']['sha256']:
        raise ValueError('source metadata changed')
    text = raw.decode('utf-8')
    start = re.search(r'"images"\s*:\s*', text).end()
    images, _ = json.JSONDecoder().raw_decode(text, start)
    lower_bound = max(r['source_id'] for r in json.loads((DOCS/'registry-fresh-development-selection.json').read_text())['selected']) if args.round3 else 790
    count = 40 if args.round3 else 60
    selected = []
    for image in sorted(images, key=lambda x: x['id']):
        source_id = image['id']
        hook = image.get('flickr_url', '')
        photo = re.search(r'/([0-9]+)_[^/]+\.', hook)
        if source_id <= lower_bound or source_id in ids or image.get('license') != 4:
            continue
        if min(image['width'], image['height']) < 256 or not photo or photo.group(1) in flickr:
            continue
        url = image.get('coco_url', '')
        if not url.startswith('http://images.cocodataset.org/train2017/'):
            continue
        selected.append(dict(source_id=source_id, source_uid=f'ms-coco:coco-2017:train2017:{source_id}',
            filename=image['file_name'], url=url.replace('http://images.cocodataset.org/', 'https://s3.amazonaws.com/images.cocodataset.org/'),
            original_coco_url=url, license_id=4, license='CC BY 2.0',
            license_url='https://creativecommons.org/licenses/by/2.0/',
            flickr_attribution_hook=hook, flickr_photo_id=photo.group(1),
            width=image['width'], height=image['height'], raw_sha256=None,
            size_bytes=None, development_reserved=True,
            split='evaluation' if args.round3 else ('calibration' if len(selected) < 20 else 'evaluation'),
            data_split='development-reserved', canonical_path=None))
        flickr.add(photo.group(1))
        if len(selected) == count:
            break
    if len(selected) != count:
        raise ValueError('fewer than sixty eligible metadata identities')
    output = dict(schema='registry-fresh-development-selection-metadata-v1', prepared_date='2026-10-16',
        status='conditional Step2b metadata-only; no source downloads or scientific access',
        original_rule_path=prior['selection_rule_path'], prior_selection_sha256=digest(prior_path),
        source_metadata=prior['source_metadata'],
        selection_rule='First 60 eligible ascending train2017 IDs strictly >790; original licence/dimension/URL/Flickr rule unchanged; prior identity, Flickr and recorded-hash exclusions retained. First20 calibration; last40 evaluation.',
        exclusion_inventories=inventories, excluded_identity_count=len(ids),
        raw_sha256_exclusions=sorted(hashes), recorded_hash_exclusions_count=len(hashes),
        raw_hash_check_pending=True,
        pending_before_decode='Compare acquired raw SHA256 with every recorded exclusion before decode. Retain exact duplicates as excluded and advance to the next eligible ascending ID by the same rule. No outcome-based replacements.',
        selected=selected, images_downloaded=0, image_bodies_opened=0,
        metadata_fields_parsed='images only; captions/categories/outcomes not parsed')
    if args.round3:
        output.update(prepared_date='2026-10-17', status='round3 metadata-only', selection_rule=f'Next {count} eligible ascending train2017 IDs strictly >{lower_bound}; unchanged original rule; all evaluation.')
    target = DOCS / ('round3-development-selection.json' if args.round3 else 'registry-fresh-development-selection.json')
    if target.exists() and json.loads(target.read_text())['status'] != output['status']:
        raise ValueError('refuse to overwrite an acquired/scientifically consulted inventory')
    with target.open('w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(path=str(target), selected_ids=[x['source_id'] for x in selected], excluded_ids=len(ids), hashes=len(hashes))))


if __name__ == '__main__':
    main()
