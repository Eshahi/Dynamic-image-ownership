"""Prepare a metadata-only draft schedule; never open image/annotation paths."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import unicodedata

from a4_protocol_reference import owner_and_seed

SPLIT_SHA256 = '60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f'
VERSION = 'm1-coco512-metadata-schedule-v1'


def uid_bytes(uid):
    if not isinstance(uid, str) or not uid or unicodedata.normalize('NFC', uid) != uid:
        raise ValueError('Nonempty NFC source UID required')
    value = uid.encode('utf-8')
    if len(value) >= 2**32:
        raise ValueError('UID too long')
    return value


def rank(tag, uid):
    value = uid_bytes(uid)
    return hashlib.sha256(tag.encode('ascii') + b'\0' + len(value).to_bytes(4, 'big') + value).digest(), value


def schedule(rows):
    """Use metadata flags only; eligibility acceptance remains explicitly pending."""
    seen = set()
    candidates = []
    for row in rows:
        uid = row['source_uid']
        uid_bytes(uid)
        if uid in seen:
            raise ValueError('Duplicate source UID')
        seen.add(uid)
        if row['domain'] != 'ms-coco' or row['study_split'] != 'test':
            continue
        if row['primary_group_representative'] not in ('true', 'false'):
            raise ValueError('Invalid representative flag')
        if row['primary_group_representative'] != 'true':
            continue
        if not row['group_id']:
            raise ValueError('Missing group')
        candidates.append(row)
    if len({r['group_id'] for r in candidates}) != len(candidates):
        raise ValueError('Multiple primary representatives in a group')
    if len(candidates) < 300:
        raise ValueError('Fewer than 300 metadata representatives; no replacement allowed')
    selected = sorted(candidates, key=lambda r: rank('m1-coco512-confirm-v1', r['source_uid']))[:300]
    clean = []
    for row in selected:
        owner, wrong, seed = owner_and_seed(row['source_uid'])
        clean.append(dict(source_uid=row['source_uid'], group_id=row['group_id'],
                          owner=owner, wrong_owner=wrong, seed_uint64_decimal=str(seed),
                          seed_uint64_hex=f'{seed:016x}'))
    t3 = sorted(clean, key=lambda r: rank('m1-coco512-t3-v1', r['source_uid']))[:30]
    t4 = sorted(clean, key=lambda r: rank('m1-coco512-t4-v1', r['source_uid']))[:60]
    pairs = [dict(pair_index=i, donor_uid=t4[i]['source_uid'], recipient_uid=t4[i+30]['source_uid']) for i in range(30)]
    return dict(schema_version=VERSION, status='draft_metadata_only_not_authorized',
                source_contract_accepted=False, scientific_run_authorized=False,
                candidate='UNRESOLVED', images_or_annotations_opened=False,
                n_metadata_candidates=len(candidates), clean=clean,
                t3_source_uids=[r['source_uid'] for r in t3], t4_pairs=pairs,
                t5=dict(status='post-approval-only', design='bounded disjoint30 pairs',
                        annotation_signature='identical nonempty noncrowd COCO category sets',
                        minimum_source_phash_hamming=8, maximum_pairs=30,
                        selection_tag='m1-coco512-t5-v1', no_replacement=True),
                caveat='Metadata groups are operational leakage screens, not certified population independence. This schedule grants no data access or scientific acceptance.')


def prepare(source, destination):
    # This is the only input file read. Do not follow any paths in its cells.
    raw = Path(source).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SPLIT_SHA256:
        raise ValueError('Pinned split metadata hash mismatch')
    result = schedule(list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))))
    result['split_metadata'] = dict(path=str(Path(source).resolve()), sha256=digest)
    result['builder_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with Path(destination).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split-metadata', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    prepare(args.split_metadata, args.output)
