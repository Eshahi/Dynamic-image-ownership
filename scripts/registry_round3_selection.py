"""Round3 metadata-only shot selection, using the existing source and decoder."""
from pathlib import Path
import json
import re
import hashlib
from registry_near_duplicate_selection import BASE, DOCS, fetch

def main():
    prior = json.loads((DOCS/'registry-near-duplicate-selection.json').read_text())
    used = {r['shot'] for r in prior['selected']}
    raw = fetch(BASE)
    # Preserve upstream directory listing order, as explicitly required by brief.
    shots = list(dict.fromkeys(re.findall(r'href="(\d{2}_[^"/]+/)"', raw.decode())))
    selected, inspected = [], []
    for shot in shots:
        if shot.rstrip('/') in used:
            continue
        url = BASE + shot + 'linear_hd/'
        try:
            listing = fetch(url)
        except Exception as exc:
            inspected.append(dict(shot=shot, status='metadata unavailable', error=str(exc)))
            continue
        files = sorted(set(re.findall(r'href="([^"/]+\.exr)"', listing.decode())))
        numbered = {int(re.search(r'(\d+)\.exr$', name).group(1)): name for name in files}
        first = min(numbered) if numbered else None
        eligible = len(files) >= 289 and all(first + o in numbered for o in (0,72,144,288)) if first is not None else False
        inspected.append(dict(shot=shot, frames=len(files), eligible=eligible, metadata_sha256=hashlib.sha256(listing).hexdigest()))
        if not eligible:
            continue
        for offset in (72,144,288):
            frames = [dict(frame_index=first+o, filename=numbered[first+o], url=url+numbered[first+o], raw_sha256=None) for o in (0,offset)]
            selected.append(dict(shot=shot.rstrip('/'), pair_id=f'tos-{shot.rstrip("/")}-o{offset:03d}', split='evaluation', frames=frames, separation_frames=offset, available_frame_count=len(files), metadata_url=url))
        print('selected',shot,flush=True)
        if len(selected) == 60:
            break
    out = {k:prior[k] for k in ('source_root','license','license_url','license_receipt_sha256','attribution')}
    out.update(schema='round3-fixed-look-alike-selection-v1', selected=selected, inspected=inspected, source_index_sha256=hashlib.sha256(raw).hexdigest(), selection_rule='First20 eligible unused shots in listing order, >=289 frames and exact offsets 72/144/288; all evaluation; no image outcomes consulted')
    (DOCS/'round3-near-duplicate-selection.json').write_text(json.dumps(out,indent=2)+'\n')
    if len(selected) != 60:
        raise ValueError('Fewer than20 eligible shots')

if __name__ == '__main__':
    main()
