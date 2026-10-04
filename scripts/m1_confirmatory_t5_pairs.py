"""Pure bounded T5 scheduling arithmetic; no files, annotations or models are loaded.

Only an authorized future worker may supply reserved-source observations.
Current tests use generated metadata and integer hashes exclusively.
"""
from __future__ import annotations
import hashlib
from itertools import combinations

VERSION = 'm1-confirmatory-t5-pairs-v1'
TAG = b'm1-coco512-t5-v1'


def category_signature(annotations):
    """COCO operational signature: unique noncrowd category IDs, no semantics inferred."""
    result = set()
    for annotation in annotations:
        crowd = annotation['iscrowd']
        category = annotation['category_id']
        if type(crowd) is not int or crowd not in (0, 1):
            raise ValueError('Invalid crowd flag')
        if type(category) is not int or category <= 0:
            raise ValueError('Invalid category ID')
        if crowd == 0:
            result.add(category)
    return tuple(sorted(result))


def pair_rank(left, right):
    ordered = sorted((left.encode('utf-8'), right.encode('utf-8')))
    if ordered[0] == ordered[1]:
        raise ValueError('Identical source UIDs')
    framed = TAG + b'\x00' + b''.join(len(uid).to_bytes(4, 'big') + uid for uid in ordered)
    return hashlib.sha256(framed).hexdigest(), tuple(ordered)


def schedule(observations, frozen_uids, limit=30):
    """Enumerate every fixed-cohort pair, then hash-rank and greedily select disjoint groups.

    An observation is uid/group_id/categories/phash/error only. Categories and
    phash are source observations; detector scores and marked-image values have
    no interface here. Missing sources remain in the pair ledger.
    """
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError('Bounded pair limit must be1..30')
    if len(frozen_uids) != len(set(frozen_uids)) or not all(type(u) is str and u for u in frozen_uids):
        raise ValueError('Frozen UIDs must be unique nonempty strings')
    rows = {}
    for value in observations:
        if set(value) != {'uid', 'group_id', 'categories', 'phash', 'error'}:
            raise ValueError('Unexpected observation fields')
        uid = value['uid']
        if uid not in frozen_uids or uid in rows:
            raise ValueError('Extra or duplicate source observation')
        if type(value['group_id']) is not str or not value['group_id']:
            raise ValueError('Missing frozen group identity')
        if value['error'] is None:
            cats = value['categories']
            if not isinstance(cats, (list, tuple)) or any(type(c) is not int or c <= 0 for c in cats) or list(cats) != sorted(set(cats)):
                raise ValueError('Categories must be sorted unique positive IDs')
            if type(value['phash']) is not int or not 0 <= value['phash'] < 2**32:
                raise ValueError('Expected32-bit source pHash')
        elif type(value['error']) is not str or not value['error']:
            raise ValueError('Missing observation reason')
        rows[uid] = value
    ledger = []
    eligible = []
    for left, right in combinations(sorted(frozen_uids, key=lambda u: u.encode('utf-8')), 2):
        a, b = rows.get(left), rows.get(right)
        item = dict(left=left, right=right, eligible=False, selected=False, phash_distance=None)
        if a is None or b is None or a['error'] is not None or b['error'] is not None:
            item['reason'] = 'missing_source_observation'
        elif a['group_id'] == b['group_id']:
            item['reason'] = 'same_frozen_group'
        elif not a['categories'] or not b['categories']:
            item['reason'] = 'empty_category_signature'
        elif tuple(a['categories']) != tuple(b['categories']):
            item['reason'] = 'different_category_signature'
        else:
            item['phash_distance'] = (a['phash'] ^ b['phash']).bit_count()
            if item['phash_distance'] < 8:
                item['reason'] = 'source_phash_distance_below8'
            else:
                item.update(eligible=True, reason='eligible', rank_sha256=pair_rank(left, right)[0])
                eligible.append(item)
        ledger.append(item)
    used = set()
    selected = []
    for item in sorted(eligible, key=lambda x: pair_rank(x['left'], x['right'])):
        groups = {rows[item['left']]['group_id'], rows[item['right']]['group_id']}
        if len(selected) == limit:
            item['reason'] = 'bounded_limit_reached'
        elif used.intersection(groups):
            item['reason'] = 'group_already_selected'
        else:
            item.update(selected=True, reason='selected')
            selected.append(dict(item))
            used.update(groups)
    return dict(schema_version=VERSION, planned_sources=len(frozen_uids),
                observed_sources=len(rows), valid_sources=sum(r['error'] is None for r in rows.values()),
                enumerated_pairs=len(ledger), eligible_pairs=len(eligible), requested_pairs=limit,
                selected_pairs=len(selected), shortfall=limit-len(selected),
                pairs=selected, ledger=ledger, human_semantic_verdict=None,
                caveat='Operational category/pHash screen; no human semantic equivalence or detector acceptance implied')
